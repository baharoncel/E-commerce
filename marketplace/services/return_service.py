import random
from decimal import Decimal
from marketplace.models import ReturnRequest, SubOrder, Wallet

class ReturnService:
    """
    İade ve Değişim Yönetim Servisi (RMA).
    """

    @staticmethod
    def create_return_request(sub_order, customer, reason):
        """
        Müşteri için yeni iade talebi oluşturur.
        """
        if sub_order.parent_order.customer != customer:
            raise ValueError("Bu sipariş sizin hesabınıza ait değil.")

        if sub_order.status not in ['DELIVERED', 'SHIPPED']:
            raise ValueError("Yalnızca kargolanan veya teslim edilen siparişler için iade talebi oluşturulabilir.")

        # Zaten aktif bir iade talebi var mı kontrolü
        existing = ReturnRequest.objects.filter(sub_order=sub_order, status__in=['PENDING', 'APPROVED']).exists()
        if existing:
            raise ValueError("Bu alt sipariş için zaten devam eden bir iade talebi mevcuttur.")

        refund_amount = sub_order.subtotal
        return_request = ReturnRequest.objects.create(
            sub_order=sub_order,
            customer=customer,
            reason=reason,
            refund_amount=refund_amount,
            status='PENDING'
        )
        return return_request

    @staticmethod
    def approve_return_request(return_request):
        """
        Satıcı/Admin iadeyi onaylar ve rastgele iade kargo takip kodu üretir.
        """
        return_request.status = 'APPROVED'
        return_request.return_shipping_code = f"RMA-{random.randint(100000, 999999)}"
        return_request.save()
        return return_request

    @staticmethod
    def complete_return_request(return_request):
        """
        İade kargosu ulaştığında iadeyi tamamlar ve bakiyeyi müşteri cüzdanına aktarır.
        """
        return_request.status = 'COMPLETED'
        return_request.save()

        # Müşterinin alt sipariş durumunu RETURNED yapar
        sub_order = return_request.sub_order
        sub_order.status = 'CANCELLED' # iade edildi
        sub_order.save()

        # Ücret Cüzdana Yatırılır
        wallet, _ = Wallet.objects.get_or_create(user=return_request.customer)
        wallet.deposit(
            amount=return_request.refund_amount,
            description=f"İade Ücret İadesi - Sipariş #{sub_order.parent_order.id}"
        )
        return return_request


    @staticmethod
    def reject_return_request(return_request, reason=""):
        """
        İade talebini reddeder.
        """
        return_request.status = 'REJECTED'
        return_request.save()
        return return_request
