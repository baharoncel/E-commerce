from decimal import Decimal
from typing import Dict, Any, List
from django.db import models
from marketplace.models import Product, ProductVariant, Coupon
from marketplace.services.product_service import ProductService
from marketplace.services.coupon_service import CouponService

class CartService:
    """
    Sepet İş Mantığı Katmanı (Service Layer).
    Sepet tutarlarını, B2B toptan indirimleri, kupon ve sadakat puanlarını
    View katmanından bağımsız olarak hesaplar.
    """

    @classmethod
    def get_cart_details(cls, session_cart: Dict[str, Any], applied_coupon_code: str = None, points_used: int = 0) -> Dict[str, Any]:
        """
        Oturum sepetini (`request.session['cart']`) işler ve detaylı hesaplama özeti döndürür.
        """
        cart_items = []
        raw_subtotal = Decimal("0.00")
        total_wholesale_discount = Decimal("0.00")

        if not session_cart:
            return {
                "items": [],
                "item_count": 0,
                "raw_subtotal": Decimal("0.00"),
                "wholesale_discount": Decimal("0.00"),
                "subtotal_after_wholesale": Decimal("0.00"),
                "coupon_discount": Decimal("0.00"),
                "points_discount": Decimal("0.00"),
                "final_total": Decimal("0.00"),
                "coupon": None,
                "earned_points": 0
            }

        for key, item in session_cart.items():
            variant_id = item.get('variant_id')
            product_id = item.get('product_id')
            quantity = int(item.get('quantity', 1))

            try:
                if variant_id:
                    variant = ProductVariant.objects.select_related('product', 'product__seller').get(id=variant_id)
                    product = variant.product
                else:
                    product = Product.objects.select_related('seller').get(id=product_id)
                    variant = product.variants.first()

                unit_price = Decimal(str(item.get('price', product.base_price)))
                
                # B2B Toptan İndirim Hesaplaması
                b2b_info = ProductService.calculate_b2b_wholesale_price(unit_price, quantity)
                line_total = b2b_info['total_price']
                original_line_total = unit_price * quantity
                line_discount = original_line_total - line_total

                raw_subtotal += original_line_total
                total_wholesale_discount += line_discount

                cart_items.append({
                    'key': key,
                    'product': product,
                    'variant': variant,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'price': b2b_info['discounted_unit_price'],
                    'original_line_total': original_line_total,
                    'discounted_unit_price': b2b_info['discounted_unit_price'],
                    'line_total': line_total,
                    'wholesale_discount_percent': b2b_info['discount_percent']
                })
            except (Product.DoesNotExist, ProductVariant.DoesNotExist):
                continue

        subtotal_after_wholesale = raw_subtotal - total_wholesale_discount

        # Kupon İndirimi
        coupon_discount = Decimal("0.00")
        coupon_obj = None
        if applied_coupon_code:
            coupon = Coupon.objects.filter(code__iexact=applied_coupon_code, is_active=True).first()
            if coupon and coupon.is_valid():
                coupon_discount = CouponService.calculate_discount(coupon, subtotal_after_wholesale)
                coupon_obj = coupon

        subtotal_after_coupon = max(Decimal("0.00"), subtotal_after_wholesale - coupon_discount)

        # Sadakat Puanı İndirimi (10 Puan = 1.00 TL)
        points_discount = Decimal("0.00")
        if points_used > 0:
            points_discount = (Decimal(str(points_used)) / Decimal("10.00")).quantize(Decimal("0.01"))
            points_discount = min(points_discount, subtotal_after_coupon)

        final_total = max(Decimal("0.00"), subtotal_after_coupon - points_discount)
        
        # Kazanılacak Sadakat Puanı (Harcanan 10 TL = 1 Puan)
        earned_points = int(final_total / Decimal("10.00"))

        return {
            "items": cart_items,
            "item_count": sum(i['quantity'] for i in cart_items),
            "raw_subtotal": raw_subtotal,
            "wholesale_discount": total_wholesale_discount,
            "subtotal_after_wholesale": subtotal_after_wholesale,
            "coupon_discount": coupon_discount,
            "points_discount": points_discount,
            "final_total": final_total,
            "coupon": coupon_obj,
            "earned_points": earned_points
        }
