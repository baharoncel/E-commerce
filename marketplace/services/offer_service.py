from decimal import Decimal
from typing import Optional
from marketplace.models import CustomUser, Product, SecondHandItem, ProductOffer
from marketplace.services.notification_service import NotificationService


class OfferService:
    def create_offer(
        self,
        buyer: CustomUser,
        offered_price: Decimal,
        product: Optional[Product] = None,
        second_hand_item: Optional[SecondHandItem] = None
    ) -> ProductOffer:
        """
        Ürün veya İkinci El ilan için fiyat teklifi oluşturur.
        """
        if not product and not second_hand_item:
            raise ValueError("Teklif vermek için bir ürün veya ikinci el ilan belirtilmelidir.")

        offer = ProductOffer.objects.create(
            buyer=buyer,
            product=product,
            second_hand_item=second_hand_item,
            offered_price=offered_price,
            status='PENDING'
        )

        # Bildirim Gönderimi
        notification_service = NotificationService()
        target_name = product.title if product else second_hand_item.title
        seller_user = product.seller.user if product else second_hand_item.seller_user

        notification_service.create_notification(
            user=seller_user,
            title="Yeni Fiyat Teklifi!",
            message=f"{buyer.username} kullanıcısı '{target_name}' ürününüz için {offered_price} TL teklif verdi."
        )

        return offer

    def respond_to_offer(self, offer: ProductOffer, seller_user: CustomUser, accept: bool) -> ProductOffer:
        """
        Satıcının gelen teklifi kabul etmesi veya reddetmesi.
        """
        item_seller = offer.product.seller.user if offer.product else offer.second_hand_item.seller_user
        if item_seller != seller_user:
            raise PermissionError("Bu teklife yalnızca ilan/ürün sahibi yanıt verebilir.")

        offer.status = 'ACCEPTED' if accept else 'REJECTED'
        offer.save()

        notification_service = NotificationService()
        status_text = "kabul edildi!" if accept else "reddedildi."
        target_name = offer.product.title if offer.product else offer.second_hand_item.title

        notification_service.create_notification(
            user=offer.buyer,
            title=f"Teklifiniz {status_text}",
            message=f"'{target_name}' ürünü için verdiğiniz {offer.offered_price} TL teklif satıcı tarafından {status_text}"
        )

        return offer
