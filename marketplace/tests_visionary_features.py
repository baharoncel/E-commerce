"""
Unit and Integration Tests for 5 Visionary Enterprise Modules
"""
from django.test import TestCase, Client
from django.urls import reverse
from marketplace.models import CustomUser, Category, Product, ProductVariant, UserLoyalty, Order, SubOrder, SellerProfile
from marketplace.services.outfit_combiner_service import get_outfit_recommendations
from marketplace.services.cargo_tracking_service import get_order_tracking_timeline
from marketplace.services.loyalty_club_service import get_or_create_user_loyalty, add_loyalty_points_for_purchase
from marketplace.services.ai_shopping_assistant_service import ask_shopping_assistant


class VisionaryEnterpriseModulesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username="visionary_customer",
            email="customer@visionary.com",
            password="Password123!",
            role="CUSTOMER"
        )
        self.seller_user = CustomUser.objects.create_user(
            username="visionary_seller",
            email="seller@visionary.com",
            password="Password123!",
            role="SELLER"
        )
        self.seller_profile = SellerProfile.objects.create(
            user=self.seller_user,
            store_name="Visionary Store"
        )
        self.category = Category.objects.create(name="Giyim & Moda", slug="giyim-moda")
        self.product1 = Product.objects.create(
            title="Slim Fit Erkek Tişört",
            description="Harika pamuklu tişört",
            base_price=299.90,
            category=self.category,
            seller=self.seller_profile
        )
        self.product2 = Product.objects.create(
            title="Mavi Jean Pantolon",
            description="Klasik denim jean",
            base_price=599.90,
            category=self.category,
            seller=self.seller_profile
        )
        self.variant1 = ProductVariant.objects.create(
            product=self.product1,
            color="Mavi",
            size="M",
            stock=20
        )

    def test_outfit_combiner_service(self):
        rec_products = get_outfit_recommendations(self.product1.id, limit=2)
        self.assertIsInstance(rec_products, list)
        self.assertTrue(len(rec_products) >= 1)
        self.assertEqual(rec_products[0].id, self.product2.id)

    def test_cargo_tracking_service(self):
        order = Order.objects.create(
            customer=self.user,
            total_amount=899.80,
            order_status="SHIPPED"
        )
        tracking_data = get_order_tracking_timeline(order)
        self.assertEqual(tracking_data["current_status"], "SHIPPED")
        self.assertEqual(tracking_data["current_step_index"], 2)
        self.assertIn("timeline", tracking_data)

    def test_user_loyalty_service(self):
        loyalty = get_or_create_user_loyalty(self.user)
        self.assertEqual(loyalty.points, 0)
        self.assertEqual(loyalty.tier, "BRONZE")

        earned = add_loyalty_points_for_purchase(self.user, 10000.00)
        loyalty.refresh_from_db()
        self.assertTrue(earned > 0)
        self.assertEqual(loyalty.tier, "SILVER")

        loyalty.points = 2500
        loyalty.calculate_tier()
        self.assertEqual(loyalty.tier, "GOLD")

    def test_ai_shopping_assistant_service(self):
        res = ask_shopping_assistant("tişört modelleriniz neler?", self.user)
        self.assertIn("reply", res)
        self.assertIn("products", res)
        self.assertTrue(len(res["products"]) >= 1)

    def test_api_endpoints_integration(self):
        # AI Assistant API
        response = self.client.post(
            reverse("api_ai_assistant"),
            data='{"query": "elbiseler"}',
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("reply", response.json())

        # Cargo Tracking API
        order = Order.objects.create(
            customer=self.user,
            total_amount=500.00,
            order_status="PREPARING"
        )
        response = self.client.get(reverse("api_cargo_tracking", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["current_status"], "PREPARING")

