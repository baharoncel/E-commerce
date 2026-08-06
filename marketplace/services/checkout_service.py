from decimal import Decimal
from typing import Dict, Any
from django.db import transaction
from marketplace.models import Order, SubOrder, OrderItem, CustomUser, ProductVariant
from marketplace.payment_gateway import IyzicoMarketplaceSimulator
from marketplace.services.cart_service import CartService
from marketplace.services.background_job_service import BackgroundJobService
from marketplace.services.reward_service import RewardService

class CheckoutService:
    """
    Sipariş Oluşturma ve Ödeme Tamamlama Servisi (Checkout Service Layer).
    Veritabanı işlemleri (atomic transaction), stok güncelleme, pazar yeri komisyon
    dağıtımı ve ödeme entegrasyonunu yönetir.
    """

    @classmethod
    def process_checkout(cls, user: CustomUser, session_cart: Dict[str, Any], payment_data: Dict[str, Any], coupon_code: str = None, points_used: int = 0) -> Dict[str, Any]:
        """
        Siparişi doğrular, veritabanına kaydeder ve ödemeyi gerçekleştirir.
        """
        cart_summary = CartService.get_cart_details(session_cart, coupon_code, points_used)

        if not cart_summary['items']:
            return {"success": False, "message": "Sepetiniz boş!"}

        card_number = payment_data.get('card_number', '')
        card_holder = payment_data.get('card_holder_name', '')

        # 1. Ödeme Ağ Geçidi Simülasyonu
        payment_result = IyzicoMarketplaceSimulator.process_payment(
            customer=user,
            cart_items=cart_summary['items'],
            card_number=card_number,
            card_holder_name=card_holder
        )

        if payment_result.get('status') != 'SUCCESS':
            return {"success": False, "message": payment_result.get('error_message', 'Ödeme başarısız!')}

        # 2. Veritabanı İşlemleri (Atomic Transaction)
        try:
            with transaction.atomic():
                # Ana Sipariş (Order)
                order = Order.objects.create(
                    customer=user,
                    total_amount=cart_summary['final_total'],
                    payment_status='PAID',
                    payment_id=payment_result.get('payment_id')
                )

                # Satıcılara Göre Gruplama ve SubOrder Oluşturma
                seller_breakdowns = {b['seller_id']: b for b in payment_result['breakdown']}
                seller_items = {}

                for item in cart_summary['items']:
                    seller_id = item['product'].seller.id
                    if seller_id not in seller_items:
                        seller_items[seller_id] = []
                    seller_items[seller_id].append(item)

                for seller_id, items in seller_items.items():
                    breakdown = seller_breakdowns.get(seller_id, {})
                    suborder = SubOrder.objects.create(
                        parent_order=order,
                        seller=items[0]['product'].seller,
                        status='PROCESSING',
                        subtotal=breakdown.get('subtotal', Decimal("0.00")),
                        commission_fee=breakdown.get('commission_fee', Decimal("0.00")),
                        seller_payout=breakdown.get('seller_payout', Decimal("0.00"))
                    )

                    for item in items:
                        OrderItem.objects.create(
                            sub_order=suborder,
                            product=item['product'],
                            variant=item['variant'],
                            quantity=item['quantity'],
                            price=item['discounted_unit_price']
                        )

                        # Stok Düşümü
                        if item['variant']:
                            item['variant'].stock = max(0, item['variant'].stock - item['quantity'])
                            item['variant'].save(update_fields=['stock'])

                # Harcanan puanları düş ve yeni puanı ekle
                if points_used > 0:
                    RewardService.redeem_points_for_checkout(user, points_used)
                RewardService.earn_points_for_order(order)

                # Asenkron E-posta Gönderimi
                BackgroundJobService.send_async_email(
                    subject=f"Siparişiniz Alındı #{order.id}",
                    message=f"Sayın {user.username}, #{order.id} numaralı siparişiniz başarıyla alındı. Toplam: {cart_summary['final_total']} TL",
                    recipient_list=[user.email]
                )

                return {
                    "success": True,
                    "order_id": order.id,
                    "total_paid": cart_summary['final_total'],
                    "payment_id": payment_result.get('payment_id')
                }
        except Exception as e:
            return {"success": False, "message": f"Sipariş oluşturulurken hata oluştu: {str(e)}"}
