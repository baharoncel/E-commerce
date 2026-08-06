import json
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from marketplace.models import CustomUser, SellerProfile, Category, Product, ProductVariant, Order, SubOrder, PushDeviceToken

class MobileApiTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Customer User
        self.customer = CustomUser.objects.create_user(
            username="mobile_customer",
            email="mobile_customer@test.com",
            password="mobilepassword123",
            role="CUSTOMER"
        )

        # Seller User
        self.seller_user = CustomUser.objects.create_user(
            username="mobile_seller",
            email="mobile_seller@test.com",
            password="sellerpassword123",
            role="SELLER"
        )
        self.seller_profile = SellerProfile.objects.create(
            user=self.seller_user,
            store_name="Mobil Mağaza",
            iban="TR111122223333444455556666",
            commission_rate=Decimal("12.00")
        )

        self.category = Category.objects.create(name="Mobil Elektronik")
        self.product = Product.objects.create(
            seller=self.seller_profile,
            category=self.category,
            title="Mobil Kulaklık",
            base_price=Decimal("250.00")
        )
        self.variant = ProductVariant.objects.create(
            product=self.product, color="Beyaz", size="Standart", stock=15, sku="MOB-HEADPHONE-WHT"
        )

    def test_mobile_login_returns_access_and_refresh_token(self):
        response = self.client.post(
            reverse('api_login'),
            json.dumps({'username': 'mobile_customer', 'password': 'mobilepassword123'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('token', data)
        self.assertIn('refresh_token', data)

        # Test Refresh Token Endpoint
        refresh_resp = self.client.post(
            reverse('api_refresh_token'),
            json.dumps({'refresh_token': data['refresh_token']}),
            content_type='application/json'
        )
        self.assertEqual(refresh_resp.status_code, 200)
        self.assertIn('token', refresh_resp.json())

    def test_mobile_register_push_device_token(self):
        # Login to get token
        login_resp = self.client.post(
            reverse('api_login'),
            json.dumps({'username': 'mobile_customer', 'password': 'mobilepassword123'}),
            content_type='application/json'
        )
        token = login_resp.json()['token']

        # Register Device Token
        response = self.client.post(
            reverse('api_register_device_token'),
            json.dumps({'token': 'FCM-TEST-TOKEN-999', 'device_type': 'IOS'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(PushDeviceToken.objects.filter(user=self.customer, token='FCM-TEST-TOKEN-999').exists())

    def test_mobile_categories_and_product_detail_api(self):
        # Categories API
        cat_resp = self.client.get(reverse('api_categories'))
        self.assertEqual(cat_resp.status_code, 200)
        self.assertIn('categories', cat_resp.json())

        # Product Detail API
        prod_resp = self.client.get(reverse('api_product_detail', args=[self.product.id]))
        self.assertEqual(prod_resp.status_code, 200)
        data = prod_resp.json()
        self.assertEqual(data['title'], "Mobil Kulaklık")
        self.assertEqual(len(data['variants']), 1)

    def test_mobile_seller_dashboard_api(self):
        # Login as Seller
        login_resp = self.client.post(
            reverse('api_login'),
            json.dumps({'username': 'mobile_seller', 'password': 'sellerpassword123'}),
            content_type='application/json'
        )
        token = login_resp.json()['token']

        dashboard_resp = self.client.get(
            reverse('api_seller_dashboard'),
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        self.assertEqual(dashboard_resp.status_code, 200)
        data = dashboard_resp.json()
        self.assertEqual(data['store_name'], "Mobil Mağaza")
        self.assertIn('metrics', data)
