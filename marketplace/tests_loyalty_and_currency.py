from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from marketplace.models import CustomUser, Order, UserRewardPoint, RewardTransaction
from marketplace.services.reward_service import RewardService
from marketplace.services.currency_service import CurrencyService

class LoyaltyAndCurrencyTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = CustomUser.objects.create_user(
            username="loyalty_user", email="loyalty@test.com", password="password123", role="CUSTOMER"
        )

    def test_earn_reward_points_for_order(self):
        # Create an order worth 1000 TL
        order = Order.objects.create(
            customer=self.customer, total_amount=Decimal("1000.00"), payment_status="PAID"
        )
        earned = RewardService.earn_points_for_order(order)
        # %2 of 1000 TL = 20.00 PazarPuan
        self.assertEqual(earned, Decimal("20.00"))

        wallet = RewardService.get_or_create_wallet(self.customer)
        self.assertEqual(wallet.balance, Decimal("20.00"))
        self.assertTrue(RewardTransaction.objects.filter(user=self.customer, points=Decimal("20.00"), transaction_type="EARNED").exists())

    def test_redeem_reward_points(self):
        wallet = RewardService.get_or_create_wallet(self.customer)
        wallet.balance = Decimal("50.00")
        wallet.save()

        discount = RewardService.redeem_points_for_checkout(self.customer, Decimal("30.00"))
        self.assertEqual(discount, Decimal("30.00"))

        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("20.00"))
        self.assertTrue(RewardTransaction.objects.filter(user=self.customer, points=Decimal("30.00"), transaction_type="SPENT").exists())

    def test_currency_conversion(self):
        # 100 TL -> TRY
        try_price = CurrencyService.convert_price(Decimal("100.00"), "TRY")
        self.assertIn("100.00", try_price)

        # 100 TL -> USD
        usd_price = CurrencyService.convert_price(Decimal("100.00"), "USD")
        self.assertTrue(usd_price.startswith("$"))

        # 100 TL -> EUR
        eur_price = CurrencyService.convert_price(Decimal("100.00"), "EUR")
        self.assertTrue(eur_price.startswith("€"))
