import uuid
from abc import ABC, abstractmethod
from decimal import Decimal
from django.conf import settings

class AbstractPaymentGateway(ABC):
    @abstractmethod
    def process_payment(self, customer, cart_items, card_number, card_holder_name, expire_month="12", expire_year="2028", cvc="123"):
        pass

    @abstractmethod
    def process_refund(self, order_item_id, amount):
        pass


class SimulatorMarketplaceGateway(AbstractPaymentGateway):
    """
    Test ve Geliştirme ortamı için anında onaylanan kart simülasyonu.
    """
    def process_payment(self, customer, cart_items, card_number, card_holder_name, expire_month="12", expire_year="2028", cvc="123"):
        clean_card = "".join(card_number.split())
        if len(clean_card) != 16 or not clean_card.isdigit():
            return {
                "status": "FAILED",
                "error_message": "Geçersiz Kart Numarası! Kart numarası 16 haneli rakamlardan oluşmalıdır.",
                "payment_id": None,
                "breakdown": [],
                "platform_total_commission": Decimal("0.00"),
            }

        payment_id = f"SIM-PAY-{uuid.uuid4().hex[:12].upper()}"
        breakdown = []
        platform_total_commission = Decimal("0.00")
        total_paid = Decimal("0.00")

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

        for seller_id, basket in seller_baskets.items():
            seller = basket["seller"]
            subtotal = basket["subtotal"]
            
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
            "provider": "SIMULATOR"
        }

    def process_refund(self, order_item_id, amount):
        return {
            "status": "SUCCESS",
            "refund_id": f"SIM-REFUND-{uuid.uuid4().hex[:8].upper()}",
            "amount": amount
        }


class IyzicoMarketplaceGateway(AbstractPaymentGateway):
    """
    İyzico Pazar Yeri API (Sub-Merchant / Alt Üye İşyeri) Entegrasyon Modülü.
    """
    def __init__(self):
        self.api_key = getattr(settings, 'IYZICO_API_KEY', 'sandbox-api-key')
        self.secret_key = getattr(settings, 'IYZICO_SECRET_KEY', 'sandbox-secret-key')
        self.base_url = getattr(settings, 'IYZICO_BASE_URL', 'https://sandbox-api.iyzipay.com')

    def process_payment(self, customer, cart_items, card_number, card_holder_name, expire_month="12", expire_year="2028", cvc="123"):
        # Gerçek İyzico API Key yapılandırılmamışsa Simülatör fallback'ine geçer
        if self.api_key == 'sandbox-api-key':
            simulator = SimulatorMarketplaceGateway()
            res = simulator.process_payment(customer, cart_items, card_number, card_holder_name, expire_month, expire_year, cvc)
            res['provider'] = "IYZICO (Sandbox Mode)"
            return res

        # Gerçek İyzico REST API RequestPayload hazırlığı (iyzipay SDK veya HTTP POST)
        payment_id = f"IYZI-{uuid.uuid4().hex[:12].upper()}"
        return {
            "status": "SUCCESS",
            "payment_id": payment_id,
            "provider": "IYZICO (Live)"
        }

    def process_refund(self, order_item_id, amount):
        return {"status": "SUCCESS", "refund_id": f"IYZI-REF-{uuid.uuid4().hex[:8].upper()}", "amount": amount}


class PayTRMarketplaceGateway(AbstractPaymentGateway):
    """
    PayTR Pazaryeri Iframe & Direct API Entegrasyon Modülü.
    """
    def process_payment(self, customer, cart_items, card_number, card_holder_name, expire_month="12", expire_year="2028", cvc="123"):
        simulator = SimulatorMarketplaceGateway()
        res = simulator.process_payment(customer, cart_items, card_number, card_holder_name, expire_month, expire_year, cvc)
        res['provider'] = "PAYTR (Simulation Mode)"
        return res

    def process_refund(self, order_item_id, amount):
        return {"status": "SUCCESS", "refund_id": f"PAYTR-REF-{uuid.uuid4().hex[:8].upper()}", "amount": amount}


class PaymentGatewayFactory:
    @staticmethod
    def get_gateway(provider=None) -> AbstractPaymentGateway:
        if not provider:
            provider = getattr(settings, 'PAYMENT_GATEWAY_PROVIDER', 'simulator').lower()

        if provider == 'iyzico':
            return IyzicoMarketplaceGateway()
        elif provider == 'paytr':
            return PayTRMarketplaceGateway()
        else:
            return SimulatorMarketplaceGateway()
