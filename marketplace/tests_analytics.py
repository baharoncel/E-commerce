from decimal import Decimal
from django.test import TestCase, Client
from marketplace.models import CustomUser, SellerProfile, Category, Product, ProductVariant, Order, SubOrder, OrderItem
from marketplace.services.analytics_service import AnalyticsService
from marketplace.jwt_helper import generate_jwt_token


class AnalyticsServiceTests(TestCase):
    def setUp(self):
        # Kullanıcılar
        self.seller_user = CustomUser.objects.create_user(username='seller_ana', role='SELLER')
        self.seller_profile = SellerProfile.objects.create(
            user=self.seller_user,
            store_name='Analytics Store',
            iban='TR001',
            commission_rate=Decimal('10.00')
        )

        self.customer = CustomUser.objects.create_user(username='customer_ana', role='CUSTOMER')
        self.admin_user = CustomUser.objects.create_user(username='admin_ana', role='SUPERADMIN')

        # Kategori & Ürünler & Varyasyonlar
        self.category = Category.objects.create(name='Teknoloji', slug='teknoloji')
        self.product1 = Product.objects.create(
            seller=self.seller_profile,
            category=self.category,
            title='Kablosuz Kulaklık',
            base_price=Decimal('500.00')
        )
        self.v1 = ProductVariant.objects.create(
            product=self.product1,
            sku='KUL-001',
            stock=3
        )

        self.product2 = Product.objects.create(
            seller=self.seller_profile,
            category=self.category,
            title='Akıllı Saat',
            base_price=Decimal('1000.00')
        )
        self.v2 = ProductVariant.objects.create(
            product=self.product2,
            sku='SAT-001',
            stock=20
        )


        # Siparişler (Sipariş 1: Ödendi)
        self.order1 = Order.objects.create(
            customer=self.customer,
            total_amount=Decimal('1500.00'),
            payment_status='PAID',
            order_status='PREPARING'
        )
        self.sub_order1 = SubOrder.objects.create(
            parent_order=self.order1,
            seller=self.seller_profile,
            subtotal=Decimal('1500.00'),
            commission_fee=Decimal('150.00'),
            seller_payout=Decimal('1350.00'),
            status='PENDING'
        )
        OrderItem.objects.create(
            sub_order=self.sub_order1,
            product=self.product1,
            quantity=1,
            price=Decimal('500.00')
        )
        OrderItem.objects.create(
            sub_order=self.sub_order1,
            product=self.product2,
            quantity=1,
            price=Decimal('1000.00')
        )

        self.service = AnalyticsService()
        self.client = Client()

    def test_seller_analytics_metrics(self):
        analytics = self.service.get_seller_analytics(self.seller_profile, days=30)

        self.assertEqual(analytics['gross_revenue'], 1500.0)
        self.assertEqual(analytics['total_commission'], 150.0)
        self.assertEqual(analytics['total_payout'], 1350.0)
        self.assertEqual(analytics['total_orders'], 1)
        self.assertEqual(analytics['total_items_sold'], 2)
        self.assertEqual(analytics['average_order_value'], 1500.0)
        self.assertEqual(len(analytics['top_products']), 2)

    def test_superadmin_analytics_metrics(self):
        analytics = self.service.get_superadmin_analytics(days=30)

        self.assertEqual(analytics['gmv'], 1500.0)
        self.assertEqual(analytics['platform_commission'], 150.0)
        self.assertEqual(analytics['total_orders'], 1)
        self.assertEqual(analytics['active_sellers_count'], 1)
        self.assertEqual(len(analytics['top_sellers']), 1)
        self.assertEqual(analytics['top_sellers'][0]['store_name'], 'Analytics Store')

    def test_low_stock_alerts(self):
        alerts = self.service.get_low_stock_alerts(self.seller_profile, threshold=5)

        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['product_id'], self.product1.id)
        self.assertEqual(alerts[0]['stock'], 3)

    def test_api_seller_analytics_endpoint(self):
        token = generate_jwt_token(self.seller_user)
        response = self.client.get(
            '/api/analytics/seller/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['status'], 'success')
        self.assertEqual(json_data['data']['gross_revenue'], 1500.0)

    def test_api_superadmin_analytics_endpoint(self):
        token = generate_jwt_token(self.admin_user)
        response = self.client.get(
            '/api/analytics/superadmin/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['status'], 'success')
        self.assertEqual(json_data['data']['gmv'], 1500.0)
