import json
import os
from decimal import Decimal
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse

from marketplace.models import CustomUser, SellerProfile, Category, Product, ProductVariant, Order, SubOrder
from marketplace.services.data_masking_service import DataMaskingService
from marketplace.services.cart_service import CartService
from marketplace.services.checkout_service import CheckoutService
from marketplace.utils.api_response import ApiResponse
from marketplace.middleware.exception_middleware import CentralizedExceptionMiddleware


class EnterpriseArchitectureTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.rf = RequestFactory()

        self.user = CustomUser.objects.create_user(username="testuser_ent", password="password123", email="bahar.user@example.com")
        self.seller_user = CustomUser.objects.create_user(username="seller_ent", password="password123", role="SELLER")
        self.seller = SellerProfile.objects.create(user=self.seller_user, store_name="EnterpriseStore", iban="TR987654321")
        self.category = Category.objects.create(name="Elektronik")

        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            title="Kablosuz Kulaklık",
            base_price=Decimal("500.00")
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            color="Siyah",
            stock=100,
            price=Decimal("500.00")
        )

    def test_data_masking_service(self):
        """1. Veri Maskeleme (PII Security) Servis Testi"""
        self.assertEqual(DataMaskingService.mask_phone("05559876543"), "+90 555 *** ** 43")
        self.assertEqual(DataMaskingService.mask_credit_card("4543600012345678"), "4543 **** **** 5678")
        self.assertEqual(DataMaskingService.mask_email("bahar.user@example.com"), "b********r@example.com")
        
        masked_dict = DataMaskingService.mask_dict({
            'username': 'bahar',
            'password': 'secret_password_123',
            'phone': '05559876543',
            'card_number': '4543600012345678'
        })
        self.assertEqual(masked_dict['password'], "********")
        self.assertEqual(masked_dict['phone'], "+90 555 *** ** 43")

    def test_cart_service_and_b2b_wholesale(self):
        """2. CartService ve B2B İndirim Hesaplama Testi"""
        # 10 adet ürün eklendiğinde B2B %15 indirim uygulanmalı
        session_cart = {
            f"v_{self.variant.id}": {
                'product_id': self.product.id,
                'variant_id': self.variant.id,
                'quantity': 10,
                'price': '500.00'
            }
        }
        summary = CartService.get_cart_details(session_cart)
        self.assertEqual(summary['item_count'], 10)
        self.assertEqual(summary['raw_subtotal'], Decimal("5000.00"))
        # %15 indirim = 750 TL indirim
        self.assertEqual(summary['wholesale_discount'], Decimal("750.00"))
        self.assertEqual(summary['final_total'], Decimal("4250.00"))

    def test_checkout_service_atomic_processing(self):
        """3. CheckoutService Sipariş ve Stok Düşme Testi"""
        session_cart = {
            f"v_{self.variant.id}": {
                'product_id': self.product.id,
                'variant_id': self.variant.id,
                'quantity': 2,
                'price': '500.00'
            }
        }
        payment_data = {
            'card_number': '4543600012345678',
            'card_holder_name': 'Bahar User'
        }

        result = CheckoutService.process_checkout(self.user, session_cart, payment_data)
        self.assertTrue(result['success'])
        
        # Stok düşümü kontrolü (100 - 2 = 98)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 98)

    def test_api_response_envelope(self):
        """4. RESTful API Standart Yanıt Zarfı Testi"""
        res = ApiResponse.success(data={'id': 1}, message="Tamamlandı")
        data = json.loads(res.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], "Tamamlandı")
        self.assertIn('timestamp', data)

    def test_centralized_exception_middleware(self):
        """5. Merkezi Hata Yönetimi & Loglama Middleware Testi"""
        middleware = CentralizedExceptionMiddleware(lambda req: 1/0)
        request = self.rf.get('/api/test-error/')
        response = middleware.process_exception(request, ValueError("Test Hatasi"))
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error_code'], 500)
        
        # Log dosyasının oluştuğunu ve yazıldığını kontrol et
        log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'pazaryeri.log')
        self.assertTrue(os.path.exists(log_file))
