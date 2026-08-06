from decimal import Decimal
from django.test import TestCase
from marketplace.models import (
    CustomUser, SellerProfile, Category, Product, ProductVariant,
    Order, SubOrder, OrderItem, ReturnRequest, Wallet, WalletTransaction,
    InventoryLog, SearchQueryLog
)
from marketplace.services.return_service import ReturnService
from marketplace.services.wallet_service import WalletService
from marketplace.services.seller_performance_service import SellerPerformanceService
from marketplace.services.inventory_service import InventoryService
from marketplace.services.search_analytics_service import SearchAnalyticsService


class NewModulesTestCase(TestCase):
    def setUp(self):
        # Müşteri ve Satıcı Kullanıcıları
        self.customer = CustomUser.objects.create_user(
            username='test_customer', email='cust@test.com', password='password123', role='CUSTOMER'
        )
        self.seller_user = CustomUser.objects.create_user(
            username='test_seller', email='seller@test.com', password='password123', role='SELLER'
        )
        self.seller_profile = SellerProfile.objects.create(
            user=self.seller_user, store_name='TestTekno', iban='TR1234567890'
        )
        self.category = Category.objects.create(name='Elektronik')

        # Ürün ve Varyasyon
        self.product = Product.objects.create(
            seller=self.seller_profile, category=self.category, title='Akıllı Saat', base_price=Decimal('1000.00')
        )
        self.variation = ProductVariant.objects.create(
            product=self.product, color='Siyah', size='Std', stock=10, sku='SW-001'
        )

        # Sipariş & Alt Sipariş
        self.order = Order.objects.create(
            customer=self.customer, total_amount=Decimal('1000.00'), payment_status='PAID'
        )
        self.sub_order = SubOrder.objects.create(
            parent_order=self.order, seller=self.seller_profile, status='DELIVERED',
            subtotal=Decimal('1000.00'), commission_fee=Decimal('100.00'), seller_payout=Decimal('900.00')
        )
        self.order_item = OrderItem.objects.create(
            sub_order=self.sub_order, product=self.product, variant=self.variation, quantity=1, price=Decimal('1000.00')
        )

    def test_return_service_flow(self):
        """İade talebi oluşturma, onaylama ve cüzdana aktarım akışı testi."""
        ret_req = ReturnService.create_return_request(
            sub_order=self.sub_order, customer=self.customer, reason='Beğenmedim'
        )
        self.assertEqual(ret_req.status, 'PENDING')
        self.assertEqual(ret_req.refund_amount, Decimal('1000.00'))

        # İadeyi onaylama
        approved = ReturnService.approve_return_request(ret_req)
        self.assertEqual(approved.status, 'APPROVED')
        self.assertTrue(approved.return_shipping_code.startswith('RMA-'))

        # İadeyi tamamlama (Cüzdana para yatırma)
        completed = ReturnService.complete_return_request(approved)
        self.assertEqual(completed.status, 'COMPLETED')

        # Cüzdan Bakiyesi Kontrolü
        wallet = Wallet.objects.get(user=self.customer)
        self.assertEqual(wallet.balance, Decimal('1000.00'))

    def test_wallet_service_operations(self):
        """Cüzdan para yükleme ve harcama testi."""
        wallet = WalletService.get_or_create_wallet(self.customer)
        self.assertEqual(wallet.balance, Decimal('0.00'))

        # Para ekleme
        WalletService.add_funds(self.customer, Decimal('500.00'), 'Hediye Bakiye')
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal('500.00'))

        # Ödeme yapma
        success = WalletService.pay_with_wallet(self.customer, Decimal('200.00'), 'Ürün Satın Alma')
        self.assertTrue(success)
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal('300.00'))

        # Yetersiz bakiye testi
        fail = WalletService.pay_with_wallet(self.customer, Decimal('500.00'), 'Fazla Ödeme')
        self.assertFalse(fail)
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal('300.00'))

    def test_inventory_service_and_alerts(self):
        """Stok güncelleme, log tutma ve kritik stok uyarısı testi."""
        log = InventoryService.update_stock(self.variation, -6, 'Sipariş Satışı')
        self.assertEqual(self.variation.stock, 4)
        self.assertEqual(log.previous_stock, 10)
        self.assertEqual(log.new_stock, 4)

        # Kritik stok uyarısı oluşmuş mu? (Stok <= 5 olduğu için notification yazılmalı)
        low_stock_items = InventoryService.get_low_stock_items(self.seller_profile)
        self.assertIn(self.variation, low_stock_items)

    def test_seller_performance_service(self):
        """Satıcı metrik ve rozet hesaplama testi."""
        metrics = SellerPerformanceService.calculate_seller_metrics(self.seller_profile)
        self.assertEqual(metrics['seller_name'], 'TestTekno')
        self.assertEqual(metrics['total_orders'], 1)
        self.assertEqual(metrics['completed_orders'], 1)

    def test_search_analytics_service(self):
        """Arama loglama, trend kelimeler ve otomatik tamamlama testi."""
        SearchAnalyticsService.log_search_query('Akıllı Saat')
        SearchAnalyticsService.log_search_query('Akıllı Saat')
        SearchAnalyticsService.log_search_query('Kulaklık')

        trending = SearchAnalyticsService.get_trending_searches()
        self.assertEqual(trending[0].query, 'akıllı saat')
        self.assertEqual(trending[0].count, 2)

        suggestions = SearchAnalyticsService.get_autocomplete_suggestions('Akıllı')
        self.assertTrue(len(suggestions) > 0)
        self.assertEqual(suggestions[0]['title'], 'Akıllı Saat')
