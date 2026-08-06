from decimal import Decimal
from django.test import TestCase, override_settings
from django.core import mail
from marketplace.models import CustomUser, SellerProfile, Category, Product, ProductVariant, Order, SubOrder, Notification
from marketplace.services.payment_service import PaymentGatewayFactory, SimulatorMarketplaceGateway, IyzicoMarketplaceGateway, PayTRMarketplaceGateway
from marketplace.services.notification_service import NotificationService

class PaymentAndNotificationTestCase(TestCase):
    def setUp(self):
        # Müşteri
        self.customer = CustomUser.objects.create_user(
            username="customer_pay_test",
            email="customer_pay@test.com",
            password="password123",
            role="CUSTOMER"
        )

        # Satıcı
        self.seller_user = CustomUser.objects.create_user(
            username="seller_pay_test",
            email="seller_pay@test.com",
            password="password123",
            role="SELLER"
        )
        self.seller_profile = SellerProfile.objects.create(
            user=self.seller_user,
            store_name="Ödeme Mağazası",
            iban="TR999999999999999999999999",
            commission_rate=Decimal("10.00")
        )

        self.category = Category.objects.create(name="Elektronik Test")
        self.product = Product.objects.create(
            seller=self.seller_profile,
            category=self.category,
            title="Kablosuz Kulaklık",
            base_price=Decimal("500.00")
        )
        self.variant = ProductVariant.objects.create(
            product=self.product, color="Siyah", stock=20, sku="HEADPHONE-BLK"
        )

    def test_payment_gateway_factory(self):
        sim_gw = PaymentGatewayFactory.get_gateway('simulator')
        self.assertIsInstance(sim_gw, SimulatorMarketplaceGateway)

        iyzi_gw = PaymentGatewayFactory.get_gateway('iyzico')
        self.assertIsInstance(iyzi_gw, IyzicoMarketplaceGateway)

        paytr_gw = PaymentGatewayFactory.get_gateway('paytr')
        self.assertIsInstance(paytr_gw, PayTRMarketplaceGateway)

    def test_simulator_payment_success(self):
        cart_items = [{
            'product': self.product,
            'variant': self.variant,
            'quantity': 2,
            'price': Decimal("500.00"),
            'total_price': Decimal("1000.00")
        }]

        gateway = SimulatorMarketplaceGateway()
        res = gateway.process_payment(
            customer=self.customer,
            cart_items=cart_items,
            card_number="1111222233334444",
            card_holder_name="Ahmet Yılmaz"
        )

        self.assertEqual(res['status'], "SUCCESS")
        self.assertTrue(res['payment_id'].startswith("SIM-PAY-"))
        self.assertEqual(res['total_paid'], Decimal("1000.00"))
        self.assertEqual(res['platform_total_commission'], Decimal("100.00")) # %10 of 1000

    def test_simulator_payment_invalid_card(self):
        gateway = SimulatorMarketplaceGateway()
        res = gateway.process_payment(
            customer=self.customer,
            cart_items=[],
            card_number="1234",
            card_holder_name="Ahmet Yılmaz"
        )
        self.assertEqual(res['status'], "FAILED")

    def test_notification_order_confirmation(self):
        order = Order.objects.create(
            customer=self.customer,
            total_amount=Decimal("1000.00"),
            payment_status="PAID",
            payment_id="TEST-PAY-123"
        )

        sub_order = SubOrder.objects.create(
            parent_order=order,
            seller=self.seller_profile,
            subtotal=Decimal("1000.00"),
            commission_fee=Decimal("100.00"),
            seller_payout=Decimal("900.00")
        )

        NotificationService.send_order_confirmation(order)
        NotificationService.send_seller_new_order_alert(sub_order)

        # Müşteriye notification kaydı düşmeli
        self.assertTrue(Notification.objects.filter(user=self.customer, title="Siparişiniz Alındı").exists())

        # Satıcıya notification kaydı düşmeli
        self.assertTrue(Notification.objects.filter(user=self.seller_user, title="Yeni Satış Bildirimi").exists())
