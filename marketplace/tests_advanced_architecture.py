import json
import os
import io
from PIL import Image
from decimal import Decimal
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from marketplace.models import CustomUser, SellerProfile, Category, Product, Order, SubOrder
from marketplace.services.image_processor_service import ImageProcessorService
from marketplace.services.fuzzy_search_service import FuzzySearchService
from marketplace.services.background_job_service import BackgroundJobService
from marketplace.payment_gateway import IyzicoMarketplaceSimulator


class AdvancedArchitectureTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username="testuser", password="password123", email="user@test.com")
        self.seller_user = CustomUser.objects.create_user(username="selleruser", password="password123", role="SELLER")
        self.seller = SellerProfile.objects.create(user=self.seller_user, store_name="ModaDunyasi", iban="TR123456")
        self.category = Category.objects.create(name="Giyim & Moda")

        # Test görseli oluştur
        file_obj = io.BytesIO()
        img = Image.new('RGB', (800, 800), color=(230, 57, 70))
        img.save(file_obj, 'JPEG')
        file_obj.seek(0)
        uploaded_image = SimpleUploadedFile("test_product.jpg", file_obj.read(), content_type="image/jpeg")

        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            title="Deri Ceket Siyah",
            description="Lüks hakiki deri ceket erkek mont",
            base_price=Decimal("1500.00"),
            image=uploaded_image
        )

    def test_image_processor_lqip_and_colors(self):
        """1. LQIP, Responsive Resimler ve Renk Çıkarımı Testi"""
        success = ImageProcessorService.process_product_image(self.product)
        self.assertTrue(success)

        self.product.refresh_from_db()
        self.assertIsNotNone(self.product.lqip_base64)
        self.assertTrue(self.product.lqip_base64.startswith("data:image/jpeg;base64,"))
        self.assertIsNotNone(self.product.dominant_color)
        self.assertTrue(self.product.dominant_color.startswith("#"))
        self.assertIn("300", self.product.responsive_images)

    def test_fuzzy_search_service(self):
        """2. Fuzzy Full-Text Arama Engine (Yazım Hatalı Arama) Testi"""
        # Kullanıcı "çeket" (yazım hatalı) yazdığında "Ceket" ürününü bulmalı
        results = FuzzySearchService.search("çeket")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0].id, self.product.id)

    def test_background_job_service(self):
        """3. Asenkron Arka Plan Görev Yöneticisi Testi"""
        ImageProcessorService.process_product_image(self.product)
        self.product.refresh_from_db()
        self.assertIsNotNone(self.product.dominant_color)

    def test_payment_webhook_hmac_verification(self):
        """4. Sanal POS Webhook HMAC İmza ve Otomatik Sipariş Güncelleme Testi"""
        order = Order.objects.create(customer=self.user, total_amount=Decimal("1500.00"))
        suborder = SubOrder.objects.create(
            parent_order=order, 
            seller=self.seller, 
            status="PENDING",
            subtotal=Decimal("1500.00"),
            commission_fee=Decimal("150.00"),
            seller_payout=Decimal("1350.00")
        )

        payload_dict = {
            "order_id": order.id,
            "event_type": "PAYMENT_SUCCESS",
            "payment_id": "IYZI-PAY-TEST123"
        }
        payload_str = json.dumps(payload_dict)
        signature = IyzicoMarketplaceSimulator.generate_webhook_signature(payload_str)

        response = self.client.post(
            reverse('payment_webhook'),
            data=payload_str,
            content_type="application/json",
            HTTP_X_SIGNATURE=signature
        )

        self.assertEqual(response.status_code, 200)
        suborder.refresh_from_db()
        self.assertEqual(suborder.status, "PROCESSING")

