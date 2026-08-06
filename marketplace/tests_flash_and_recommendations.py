from decimal import Decimal
import datetime
from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse
from marketplace.models import CustomUser, SellerProfile, Category, Product, ProductVariant, Order, SubOrder, OrderItem, FlashSale
from marketplace.services.recommendation_service import RecommendationService

class FlashSaleAndRecommendationTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Users & Sellers
        self.seller_user = CustomUser.objects.create_user(
            username="flash_seller", email="flash_seller@test.com", password="password123", role="SELLER"
        )
        self.seller_profile = SellerProfile.objects.create(
            user=self.seller_user, store_name="Fırsat Mağazası", iban="TR000011112222333344445555"
        )

        self.category = Category.objects.create(name="Elektronik Fırsat")

        # Products
        self.product1 = Product.objects.create(
            seller=self.seller_profile, category=self.category, title="Flaş Kulaklık", base_price=Decimal("1000.00")
        )
        self.variant1 = ProductVariant.objects.create(product=self.product1, color="Siyah", stock=10, sku="FLASH-1")

        self.product2 = Product.objects.create(
            seller=self.seller_profile, category=self.category, title="Tamamlayıcı Kılıf", base_price=Decimal("200.00")
        )
        self.variant2 = ProductVariant.objects.create(product=self.product2, color="Şeffaf", stock=20, sku="FLASH-2")

        # Create FlashSale Campaign (30% Discount for 24 Hours)
        self.flash_sale = FlashSale.objects.create(
            product=self.product1,
            discount_percent=Decimal("30.00"),
            end_time=timezone.now() + datetime.timedelta(hours=24),
            is_active=True
        )

    def test_flash_sale_price_calculation(self):
        self.assertTrue(self.flash_sale.is_valid())
        # 1000 TL with 30% discount should be 700 TL
        self.assertEqual(self.flash_sale.get_flash_price(), Decimal("700.00"))

    def test_flash_sale_expiration(self):
        expired_sale = FlashSale.objects.create(
            product=self.product2,
            discount_percent=Decimal("50.00"),
            end_time=timezone.now() - datetime.timedelta(hours=1),
            is_active=True
        )
        self.assertFalse(expired_sale.is_valid())

    def test_recommendation_service_co_occurrence(self):
        # Create customer & past order where product1 and product2 were bought together
        customer = CustomUser.objects.create_user(username="rec_user", email="rec@test.com", password="password123", role="CUSTOMER")
        order = Order.objects.create(customer=customer, total_amount=Decimal("1200.00"), payment_status="PAID")
        sub_order = SubOrder.objects.create(parent_order=order, seller=self.seller_profile, subtotal=Decimal("1200.00"), commission_fee=Decimal("120.00"), seller_payout=Decimal("1080.00"))

        OrderItem.objects.create(sub_order=sub_order, product=self.product1, variant=self.variant1, quantity=1, price=Decimal("1000.00"))
        OrderItem.objects.create(sub_order=sub_order, product=self.product2, variant=self.variant2, quantity=1, price=Decimal("200.00"))

        # Test frequently bought together recommendation for product1
        recs = RecommendationService.get_frequently_bought_together(self.product1, limit=4)
        self.assertIn(self.product2, recs)
