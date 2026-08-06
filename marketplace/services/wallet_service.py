from decimal import Decimal
from marketplace.models import Wallet, WalletTransaction

class WalletService:
    """
    Müşteri Cüzdanı Servisi.
    """

    @staticmethod
    def get_or_create_wallet(user):
        wallet, _ = Wallet.objects.get_or_create(user=user)
        return wallet

    @staticmethod
    def add_funds(user, amount, description="Cüzdana Bakiye Ekleme"):
        wallet = WalletService.get_or_create_wallet(user)
        return wallet.deposit(amount, description)

    @staticmethod
    def pay_with_wallet(user, amount, description="Sipariş Ödemesi"):
        wallet = WalletService.get_or_create_wallet(user)
        return wallet.withdraw(amount, description)

    @staticmethod
    def get_transaction_history(user):
        wallet = WalletService.get_or_create_wallet(user)
        return wallet.transactions.all().order_by('-created_at')
