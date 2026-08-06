from decimal import Decimal
from django.db import transaction
from marketplace.models import UserRewardPoint, RewardTransaction

class RewardService:
    """
    PazarPuan Sadakat ve Ödül Sistemi Servisi.
    1 PazarPuan = 1 TL İndirim değerindedir.
    Sipariş tutarının %2'si otomatik kazanılır.
    """
    REWARD_RATE = Decimal("0.02") # %2

    @staticmethod
    def get_or_create_wallet(user):
        wallet, _ = UserRewardPoint.objects.get_or_create(user=user)
        return wallet

    @classmethod
    def earn_points_for_order(cls, order):
        """
        Tamamlanan siparişte toplam tutarın %2'si kadar PazarPuan kazandırır.
        """
        if not order or not order.customer:
            return Decimal("0.00")

        earned_points = round(order.total_amount * cls.REWARD_RATE, 2)
        if earned_points <= Decimal("0.00"):
            return Decimal("0.00")

        with transaction.atomic():
            wallet = cls.get_or_create_wallet(order.customer)
            wallet.balance += earned_points
            wallet.save()

            RewardTransaction.objects.create(
                user=order.customer,
                points=earned_points,
                transaction_type='EARNED',
                description=f"#{order.id} Nolu Siparişten Kazanılan PazarPuan (%2)"
            )

        return earned_points

    @classmethod
    def redeem_points_for_checkout(cls, user, points_to_use):
        """
        Ödeme aşamasında PazarPuan harcayarak indirim kazanma.
        Returns: Decimal (TL indirim tutarı)
        """
        points_to_use = Decimal(str(points_to_use))
        if points_to_use <= Decimal("0.00"):
            return Decimal("0.00")

        wallet = cls.get_or_create_wallet(user)
        if wallet.balance < points_to_use:
            raise ValueError(f"Yetersiz PazarPuan bakiyesi! Mevcut bakiyeniz: {wallet.balance} PazarPuan")

        with transaction.atomic():
            wallet.balance -= points_to_use
            wallet.save()

            RewardTransaction.objects.create(
                user=user,
                points=points_to_use,
                transaction_type='SPENT',
                description=f"Ödeme Aşamasında Kullanılan PazarPuan İndirimi"
            )

        return points_to_use
