from datetime import timedelta
from decimal import Decimal
from django.db import models
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from marketplace.models import SubOrder, OrderItem, Product, ProductVariant, SellerProfile


class AnalyticsService:
    def get_seller_analytics(self, seller_profile: SellerProfile, days: int = 30) -> dict:
        """
        Satıcının belirli bir gün aralığındaki satış, ciro, komisyon,
        sipariş durumları ve en çok satan ürün metriklerini döner.
        """
        now = timezone.now()
        start_date = now - timedelta(days=days)

        # Ödemesi başarılı olan alt siparişler
        paid_sub_orders = SubOrder.objects.filter(
            seller=seller_profile,
            created_at__gte=start_date,
            parent_order__payment_status='PAID'
        )

        # Toplam Finansal Metrikler
        totals = paid_sub_orders.aggregate(
            gross_revenue=Sum('subtotal'),
            total_commission=Sum('commission_fee'),
            total_payout=Sum('seller_payout'),
            total_orders=Count('id')
        )

        gross_revenue = totals['gross_revenue'] or Decimal('0.00')
        total_commission = totals['total_commission'] or Decimal('0.00')
        total_payout = totals['total_payout'] or Decimal('0.00')
        total_orders = totals['total_orders'] or 0

        # Ortalama Sipariş Tutarı (AOV)
        aov = (gross_revenue / Decimal(total_orders)) if total_orders > 0 else Decimal('0.00')

        # Toplam Satılan Ürün Adedi
        total_items_sold = OrderItem.objects.filter(
            sub_order__in=paid_sub_orders
        ).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0

        # Sipariş Durumu Dağılımı (Tüm alt siparişler için)
        all_sub_orders = SubOrder.objects.filter(
            seller=seller_profile,
            created_at__gte=start_date
        )
        status_counts_raw = all_sub_orders.values('status').annotate(count=Count('id'))
        status_breakdown = {item['status']: item['count'] for item in status_counts_raw}

        # Günlük Satış Trendi (Tarih bazlı)
        daily_trend_qs = paid_sub_orders.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            daily_gross=Sum('subtotal'),
            daily_commission=Sum('commission_fee'),
            daily_payout=Sum('seller_payout'),
            daily_count=Count('id')
        ).order_by('date')

        daily_trend = [
            {
                'date': item['date'].strftime('%Y-%m-%d'),
                'gross_revenue': float(item['daily_gross'] or 0),
                'commission_fee': float(item['daily_commission'] or 0),
                'seller_payout': float(item['daily_payout'] or 0),
                'order_count': item['daily_count']
            }
            for item in daily_trend_qs
        ]

        # En Çok Satan Top 5 Ürün
        top_products_qs = OrderItem.objects.filter(
            sub_order__in=paid_sub_orders
        ).values('product__id', 'product__title').annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('price'))
        ).order_by('-total_sold')[:5]

        top_products = [
            {
                'product_id': item['product__id'],
                'title': item['product__title'],
                'total_sold': item['total_sold'],
                'total_revenue': float(item['total_revenue'] or 0)
            }
            for item in top_products_qs
        ]

        # Düşük Stok Alarmları (Stoku 5 ve altı olan ürünler)
        low_stock_products = self.get_low_stock_alerts(seller_profile, threshold=5)

        return {
            'seller_id': seller_profile.id,
            'store_name': seller_profile.store_name,
            'days': days,
            'gross_revenue': float(gross_revenue),
            'total_commission': float(total_commission),
            'total_payout': float(total_payout),
            'total_orders': total_orders,
            'total_items_sold': total_items_sold,
            'average_order_value': float(round(aov, 2)),
            'status_breakdown': status_breakdown,
            'daily_trend': daily_trend,
            'top_products': top_products,
            'low_stock_alerts': low_stock_products
        }

    def get_superadmin_analytics(self, days: int = 30) -> dict:
        """
        Platform genelinde GMV, toplam komisyon geliri, aktif satıcılar,
        ve en çok ciro yapan mağazaların analizi.
        """
        now = timezone.now()
        start_date = now - timedelta(days=days)

        paid_sub_orders = SubOrder.objects.filter(
            created_at__gte=start_date,
            parent_order__payment_status='PAID'
        )

        totals = paid_sub_orders.aggregate(
            gmv=Sum('subtotal'),
            platform_commission=Sum('commission_fee'),
            total_orders=Count('id')
        )

        gmv = totals['gmv'] or Decimal('0.00')
        platform_commission = totals['platform_commission'] or Decimal('0.00')
        total_orders = totals['total_orders'] or 0

        # Aktif Satıcı Sayısı
        active_sellers_count = paid_sub_orders.values('seller').distinct().count()

        # En Çok Ciro Yapan Satıcılar (Top 5)
        top_sellers_qs = paid_sub_orders.values('seller__id', 'seller__store_name').annotate(
            total_gmv=Sum('subtotal'),
            commission_generated=Sum('commission_fee'),
            order_count=Count('id')
        ).order_by('-total_gmv')[:5]

        top_sellers = [
            {
                'seller_id': item['seller__id'],
                'store_name': item['seller__store_name'],
                'total_gmv': float(item['total_gmv'] or 0),
                'commission_generated': float(item['commission_generated'] or 0),
                'order_count': item['order_count']
            }
            for item in top_sellers_qs
        ]

        # Günlük Platform Trendi
        daily_trend_qs = paid_sub_orders.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            daily_gmv=Sum('subtotal'),
            daily_commission=Sum('commission_fee'),
            daily_count=Count('id')
        ).order_by('date')

        daily_trend = [
            {
                'date': item['date'].strftime('%Y-%m-%d'),
                'gmv': float(item['daily_gmv'] or 0),
                'commission': float(item['daily_commission'] or 0),
                'order_count': item['daily_count']
            }
            for item in daily_trend_qs
        ]

        return {
            'days': days,
            'gmv': float(gmv),
            'platform_commission': float(platform_commission),
            'total_orders': total_orders,
            'active_sellers_count': active_sellers_count,
            'top_sellers': top_sellers,
            'daily_trend': daily_trend
        }

    def get_low_stock_alerts(self, seller_profile: SellerProfile, threshold: int = 5) -> list:
        """
        Satıcının stoğu belirlenen eşik değerin altında kalan ürün/varyasyonlarını listeler.
        """
        low_stock_list = []
        products = Product.objects.filter(seller=seller_profile).prefetch_related('variants')

        for product in products:
            variants = product.variants.all()
            if variants.exists():
                for v in variants:
                    if v.stock <= threshold:
                        low_stock_list.append({
                            'product_id': product.id,
                            'product_title': product.title,
                            'variant_id': v.id,
                            'variant_name': str(v),
                            'stock': v.stock
                        })

        return low_stock_list

