from django.db.models import Avg, Count
from marketplace.models import SellerProfile, SubOrder, ProductReview

class SellerPerformanceService:
    """
    Satıcı performans ve başarım rozeti hesaplama servisi.
    """

    @staticmethod
    def calculate_seller_metrics(seller_profile):
        """
        Satıcının ortalama puanı, tamamlanan sipariş sayısı ve başarı rozetlerini hesaplar.
        """
        sub_orders = SubOrder.objects.filter(seller=seller_profile)
        total_orders = sub_orders.count()
        completed_orders = sub_orders.filter(status='DELIVERED').count()

        # Ortalama Ürün Puanı
        avg_rating = ProductReview.objects.filter(
            product__seller=seller_profile
        ).aggregate(Avg('rating'))['rating__avg'] or 0.0

        badges = []
        if avg_rating >= 4.5:
            badges.append({
                'key': 'HIGH_RATING',
                'title': '⭐ Yüksek Müşteri Memnuniyeti',
                'description': '4.5+ ortalama müşteri puanı'
            })
        if completed_orders >= 5:
            badges.append({
                'key': 'SUPER_SELLER',
                'title': '🏆 Süper Satıcı',
                'description': 'Başarıyla tamamlanmış 5+ sipariş'
            })
        if total_orders > 0 and (completed_orders / total_orders) >= 0.8:
            badges.append({
                'key': 'FAST_SHIPPER',
                'title': '🚀 Hızlı Gönderi',
                'description': '%80+ yüksek sipariş tamamlama oranı'
            })

        return {
            'seller_name': seller_profile.store_name,
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'avg_rating': round(avg_rating, 2),
            'badges': badges
        }
