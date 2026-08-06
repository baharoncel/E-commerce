import uuid
from decimal import Decimal
from marketplace.models import SellerProfile

class IyzicoMarketplaceSimulator:
    """
    Iyzico Pazar Yeri (Sub-Merchant/Alt Üye İşyeri) API simülasyon sınıfı.
    Tek bir ödeme alıp, arka planda parayı komisyon oranlarına göre 
    platform cüzdanı ve satıcıların IBAN hesapları arasında paylaştırır.
    """

    @staticmethod
    def process_payment(customer, cart_items, card_number, card_holder_name):
        """
        Gelen sepet elemanlarını (cart_items) ve kart bilgilerini alarak
        pazar yeri mantığında ödemeyi simüle eder.
        
        cart_items formatı:
        [
            {
                'product': Product nesnesi,
                'variant': ProductVariant nesnesi (opsiyonel),
                'quantity': int,
                'price': Decimal
            },
            ...
        ]
        """
        # Kart numarası basit doğrulama (16 haneli olmalı)
        clean_card = "".join(card_number.split())
        if len(clean_card) != 16 or not clean_card.isdigit():
            return {
                "status": "FAILED",
                "error_message": "Geçersiz Kart Numarası! Kart numarası 16 haneli olmalıdır.",
                "payment_id": None,
                "breakdown": [],
                "platform_total_commission": Decimal("0.00"),
            }

        payment_id = f"IYZI-PAY-{uuid.uuid4().hex[:12].upper()}"
        breakdown = []
        platform_total_commission = Decimal("0.00")
        total_paid = Decimal("0.00")

        # Sepet elemanlarını satıcılara göre grupla
        seller_baskets = {}
        for item in cart_items:
            product = item['product']
            seller = product.seller
            quantity = item['quantity']
            price = Decimal(str(item['price']))
            item_total = price * quantity
            total_paid += item_total

            if seller.id not in seller_baskets:
                seller_baskets[seller.id] = {
                    "seller": seller,
                    "items": [],
                    "subtotal": Decimal("0.00")
                }
            
            seller_baskets[seller.id]["items"].append(item)
            seller_baskets[seller.id]["subtotal"] += item_total

        # Her satıcı için komisyon ve hak ediş tutarını hesapla
        for seller_id, basket in seller_baskets.items():
            seller = basket["seller"]
            subtotal = basket["subtotal"]
            
            # Satıcının komisyon oranını çek (%10 -> 0.10)
            commission_percent = Decimal(str(seller.commission_rate))
            commission_fee = (subtotal * commission_percent / Decimal("100.00")).quantize(Decimal("0.01"))
            seller_payout = (subtotal - commission_fee).quantize(Decimal("0.01"))

            platform_total_commission += commission_fee

            breakdown.append({
                "seller_id": seller.id,
                "store_name": seller.store_name,
                "iban": seller.iban,
                "commission_rate": commission_percent,
                "subtotal": subtotal,
                "commission_fee": commission_fee,
                "seller_payout": seller_payout,
            })

        return {
            "status": "SUCCESS",
            "payment_id": payment_id,
            "total_paid": total_paid,
            "breakdown": breakdown,
            "platform_total_commission": platform_total_commission,
        }

    @staticmethod
    def generate_webhook_signature(payload: str, secret_key: str = "pazaryeri_webhook_secret_key_2026") -> str:
        """
        Webhook isteği için HMAC-SHA256 imzası üretir.
        """
        import hmac
        import hashlib
        return hmac.new(
            secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    def verify_webhook_signature(payload: str, signature: str, secret_key: str = "pazaryeri_webhook_secret_key_2026") -> bool:
        """
        Gelen Webhook bildiriminin imzasını doğrular (HMAC-SHA256).
        """
        import hmac
        expected_sig = IyzicoMarketplaceSimulator.generate_webhook_signature(payload, secret_key)
        return hmac.compare_digest(expected_sig, signature)

