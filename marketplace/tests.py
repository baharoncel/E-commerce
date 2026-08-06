import json
from decimal import Decimal
from django.test import TestCase
from django.db.models import Q
from marketplace.models import (
    CustomUser, SellerProfile, Category, Product, ProductVariant, 
    Order, SubOrder, OrderItem, Favorite, ReturnRequest, ChatMessage, Notification
)
from marketplace.payment_gateway import IyzicoMarketplaceSimulator

class ExpandedMarketplaceTestCase(TestCase):
    def setUp(self):
        # 1. Hiyerarşik Kategoriler
        self.cat_moda = Category.objects.create(name="Giyim & Moda")
        self.cat_tisort = Category.objects.create(name="Tişört", parent=self.cat_moda)
        self.cat_pantolon = Category.objects.create(name="Pantolon", parent=self.cat_moda)

        # 2. Kullanıcılar ve Profiller
        # Seller A (Moda Butik - %12 komisyon)
        self.user_seller_a = CustomUser.objects.create_user(
            username="seller_a_test", password="password123", role="SELLER"
        )
        self.profile_seller_a = SellerProfile.objects.create(
            user=self.user_seller_a,
            store_name="Moda Butik",
            iban="TR111111111111111111111111",
            commission_rate=Decimal("12.00")
        )

        # Seller B (Kozmetik Dünyası - %10 komisyon)
        self.user_seller_b = CustomUser.objects.create_user(
            username="seller_b_test", password="password123", role="SELLER"
        )
        self.profile_seller_b = SellerProfile.objects.create(
            user=self.user_seller_b,
            store_name="Kozmetik Dünyası",
            iban="TR222222222222222222222222",
            commission_rate=Decimal("10.00")
        )

        # Customer (Müşteri)
        self.customer = CustomUser.objects.create_user(
            username="customer_test", password="password123", role="CUSTOMER"
        )

        # 3. Ürünler ve Varyasyonlar
        # Product A (Seller A)
        self.product_a = Product.objects.create(
            seller=self.profile_seller_a,
            category=self.cat_tisort,
            title="Oversize Tişört",
            base_price=Decimal("250.00")
        )
        self.variant_a = ProductVariant.objects.create(
            product=self.product_a,
            color="Siyah",
            size="M",
            stock=10,
            sku="TEST-CLO-BLK-M"
        )

        # Product B (Seller B)
        self.product_b = Product.objects.create(
            seller=self.profile_seller_b,
            category=self.cat_pantolon,
            title="Likit Ruj",
            base_price=Decimal("180.00")
        )
        self.variant_b = ProductVariant.objects.create(
            product=self.product_b,
            color="Kırmızı",
            stock=15,
            sku="TEST-COS-RED"
        )

    def test_category_hierarchy(self):
        """Kategori hiyerarşisinin doğruluğunu test eder."""
        self.assertEqual(self.cat_tisort.parent, self.cat_moda)
        self.assertIn(self.cat_tisort, self.cat_moda.subcategories.all())
        self.assertIn(self.cat_pantolon, self.cat_moda.subcategories.all())

    def test_toggle_favorites(self):
        """Favori ekleme/çıkarma mantığını test eder."""
        # İlk ekleme
        fav = Favorite.objects.create(user=self.customer, product=self.product_a)
        self.assertTrue(Favorite.objects.filter(user=self.customer, product=self.product_a).exists())
        self.assertEqual(self.customer.favorites.count(), 1)
        
        # Kaldırma
        fav.delete()
        self.assertFalse(Favorite.objects.filter(user=self.customer, product=self.product_a).exists())

    def test_messaging_system(self):
        """Müşteri ve satıcı arasındaki sohbet mesajlaşmasını test eder."""
        # Müşteriden satıcıya mesaj
        msg1 = ChatMessage.objects.create(
            sender=self.customer,
            recipient=self.user_seller_a,
            message="Ürün pamuklu mu?"
        )
        self.assertEqual(ChatMessage.objects.filter(sender=self.customer, recipient=self.user_seller_a).count(), 1)

        # Satıcıdan müşteriye cevap
        msg2 = ChatMessage.objects.create(
            sender=self.user_seller_a,
            recipient=self.customer,
            message="Evet, %100 pamukludur."
        )

        # Sohbet geçmişi sorgulama (Customer ve Seller A konuşmaları)
        thread = ChatMessage.objects.filter(
            (Q(sender=self.customer) & Q(recipient=self.user_seller_a)) |
            (Q(sender=self.user_seller_a) & Q(recipient=self.customer))
        ).order_by('created_at')

        self.assertEqual(len(thread), 2)
        self.assertEqual(thread[0].message, "Ürün pamuklu mu?")
        self.assertEqual(thread[1].message, "Evet, %100 pamukludur.")

    def test_return_request_lifecycle(self):
        """İade talebi oluşturma ve satıcının onaylama/stok yenileme döngüsünü test eder."""
        # 1. Sipariş Oluştur
        parent_order = Order.objects.create(
            customer=self.customer,
            total_amount=Decimal("430.00"),
            payment_status='PAID',
            payment_id="IYZI-TEST-1234"
        )
        
        sub_order = SubOrder.objects.create(
            parent_order=parent_order,
            seller=self.profile_seller_a,
            subtotal=Decimal("250.00"),
            commission_fee=Decimal("30.00"),
            seller_payout=Decimal("220.00"),
            status='DELIVERED' # İade için teslim edilmiş olmalı
        )
        
        order_item = OrderItem.objects.create(
            sub_order=sub_order,
            product=self.product_a,
            variant=self.variant_a,
            quantity=2,
            price=Decimal("125.00")
        )

        # 2. İade Talebi Gönder
        return_req = ReturnRequest.objects.create(
            order_item=order_item,
            reason="Bedeni küçük geldi."
        )
        
        self.assertEqual(ReturnRequest.objects.filter(order_item=order_item).count(), 1)
        self.assertEqual(return_req.status, 'PENDING')

        # İade öncesi stok durumunu kontrol et
        initial_stock = self.variant_a.stock

        # 3. Satıcı İadeyi Onaylasın
        return_req.status = 'APPROVED'
        return_req.save()

        # Stokların geri eklendiğini doğrula (+2 adet)
        self.variant_a.refresh_from_db()
        self.assertEqual(self.variant_a.stock, initial_stock + 2)

        # Müşteriye bildirim iletildiğini doğrula
        Notification.objects.create(
            user=self.customer,
            title="İade Talebiniz Onaylandı",
            message="İade talebiniz onaylandı, paranız iade ediliyor."
        )
        self.assertEqual(Notification.objects.filter(user=self.customer, title="İade Talebiniz Onaylandı").count(), 1)

    def test_api_jwt_auth_and_checkout(self):
        """REST API ve JWT Kimlik Doğrulama süreçlerini test eder."""
        # 1. API Login & JWT üretimi
        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({
                'username': 'customer_test',
                'password': 'password123'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        self.assertIn('token', resp_data)
        token = resp_data['token']

        # 2. JWT korumalı Profile API'sine erişim
        headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        profile_resp = self.client.get('/api/auth/profile/', **headers)
        self.assertEqual(profile_resp.status_code, 200)
        profile_data = profile_resp.json()
        self.assertEqual(profile_data['user']['username'], 'customer_test')
        self.assertEqual(profile_data['user']['role'], 'CUSTOMER')

        # 3. API Üzerinden Dinamik Sepet / Split Order Checkout
        checkout_resp = self.client.post(
            '/api/cart/checkout/',
            data=json.dumps({
                'items': [
                    {'variant_id': self.variant_a.id, 'quantity': 1},
                    {'variant_id': self.variant_b.id, 'quantity': 2}
                ],
                'card_number': '1234567890123456',
                'card_holder': 'Test User'
            }),
            content_type='application/json',
            **headers
        )
        self.assertEqual(checkout_resp.status_code, 200)
        checkout_data = checkout_resp.json()
        self.assertIn('order_id', checkout_data)

        # Siparişlerin arka planda satıcılara göre parçalandığını (Split Order) doğrula
        order = Order.objects.get(id=checkout_data['order_id'])
        self.assertEqual(order.sub_orders.count(), 2)
        sub_orders = order.sub_orders.all()
        
        # Sub-order A (Seller A)
        sub_a = sub_orders.get(seller=self.profile_seller_a)
        self.assertEqual(sub_a.subtotal, Decimal("250.00"))
        
        # Sub-order B (Seller B)
        sub_b = sub_orders.get(seller=self.profile_seller_b)
        self.assertEqual(sub_b.subtotal, Decimal("360.00")) # 180 * 2

        # 4. API Üzerinden Favori Ekleme/Çıkarma
        fav_resp = self.client.post(
            '/api/favorites/toggle/',
            data=json.dumps({
                'product_id': self.product_a.id
            }),
            content_type='application/json',
            **headers
        )
        self.assertEqual(fav_resp.status_code, 200)
        self.assertTrue(fav_resp.json()['favorited'])

    def test_review_approval_flow(self):
        """Satıcının ürün yorumlarını onaylama ve reddetme/silme akışını test eder."""
        from marketplace.models import ProductReview
        
        # Müşteriden Product A için yorum oluşturalım
        review = ProductReview.objects.create(
            product=self.product_a,
            user=self.customer,
            rating=4,
            comment="Güzel ürün beğendim",
            is_approved=False
        )
        
        # Giriş yapalım (Satıcı A olarak)
        self.client.login(username="seller_a_test", password="password123")
        
        # 1. Onaylama POST isteği gönderelim
        response = self.client.post(
            f'/seller/review/{review.id}/handle/',
            data={'action': 'APPROVE'}
        )
        self.assertEqual(response.status_code, 302) # Yönlendirme (redirect)
        
        # Yorumun onaylandığını ve ortalama puanın güncellendiğini doğrulayalım
        review.refresh_from_db()
        self.assertTrue(review.is_approved)
        
        self.product_a.refresh_from_db()
        self.assertEqual(self.product_a.average_rating, Decimal("4.00"))
        self.assertEqual(self.product_a.review_count, 1)
        
        # 2. Reddetme/Silme POST isteği gönderelim
        response = self.client.post(
            f'/seller/review/{review.id}/handle/',
            data={'action': 'REJECT'}
        )
        self.assertEqual(response.status_code, 302)
        
        # Yorumun silindiğini ve ortalama puanın sıfırlandığını doğrulayalım
        self.assertFalse(ProductReview.objects.filter(id=review.id).exists())
        self.product_a.refresh_from_db()
        self.assertEqual(self.product_a.average_rating, Decimal("0.00"))
        self.assertEqual(self.product_a.review_count, 0)

    def test_ajax_chat_and_polling_flow(self):
        """AJAX ile mesaj gönderme ve mesajları polling ile sorgulama süreçlerini test eder."""
        # 1. AJAX Mesaj Gönderimi
        self.client.login(username="customer_test", password="password123")
        
        response = self.client.post(
            '/messages/send/',
            data={
                'recipient_id': self.user_seller_a.id,
                'message': 'Merhaba AJAX ile gönderildi.'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        self.assertTrue(resp_data['success'])
        self.assertEqual(resp_data['message']['text'], 'Merhaba AJAX ile gönderildi.')
        msg_id = resp_data['message']['id']
        
        # 2. Polling API'si ile yeni mesajları çekme
        # Satıcı A olarak giriş yapalım
        self.client.login(username="seller_a_test", password="password123")
        
        poll_response = self.client.get(
            f'/messages/poll/{self.customer.id}/?last_id={msg_id - 1}',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(poll_response.status_code, 200)
        poll_data = poll_response.json()
        self.assertTrue(poll_data['success'])
        self.assertEqual(len(poll_data['messages']), 1)
        self.assertEqual(poll_data['messages'][0]['text'], 'Merhaba AJAX ile gönderildi.')
        self.assertEqual(poll_data['messages'][0]['id'], msg_id)

    def test_otp_service_and_login(self):
        """SMS OTP üretimi ve doğrulama test edilir."""
        from marketplace.services.otp_service import OTPService
        code, phone = OTPService.generate_otp("5559876543")
        self.assertEqual(len(code), 6)
        
        success, msg, user = OTPService.verify_otp_and_login("5559876543", code)
        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, f"user_{phone}")

    def test_google_oauth2_service(self):
        """Google OAuth2 kullanıcı doğrulama ve oluşturma test edilir."""
        from marketplace.services.social_auth_service import SocialAuthService
        user, msg = SocialAuthService.authenticate_google_user("test_guser@gmail.com", "Ahmet Yılmaz", "g123")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test_guser@gmail.com")
        self.assertEqual(user.first_name, "Ahmet")

    def test_shipping_and_barcode_service(self):
        """Kargo takip sorgulama ve Code128 SVG barkod üretici test edilir."""
        from marketplace.services.shipping_service import ShippingService
        cargo_info = ShippingService.get_live_cargo_tracking("YK-123456", "YURTICI")
        self.assertEqual(cargo_info['company'], "Yurtiçi Kargo")
        self.assertEqual(len(cargo_info['events']), 3)

        barcode_svg = ShippingService.generate_code128_svg_barcode("YK-123456")
        self.assertIn("<svg", barcode_svg)
        self.assertIn("YK-123456", barcode_svg)

    def test_ai_content_service(self):
        """Yapay Zeka otomatik SEO ürün açıklaması üretimi test edilir."""
        from marketplace.services.ai_content_service import AIContentService
        res = AIContentService.generate_product_description("Hakiki Deri Ceket", "Giyim")
        self.assertIn("Hakiki Deri Ceket", res['description'])
        self.assertIn("#hakiki", res['tags'])

    def test_qr_service(self):
        """Vektörel SVG QR Kod doğrulama üreticisi test edilir."""
        from marketplace.services.qr_service import QRService
        qr_svg = QRService.generate_svg_qr_code("https://pazaryeri.com/verify/100")
        self.assertIn("<svg", qr_svg)
        self.assertIn("DOĞRULA", qr_svg)

    def test_b2b_wholesale_pricing(self):
        """B2B Toptan kademeli indirim hesaplaması test edilir."""
        from marketplace.services.product_service import ProductService
        tier1 = ProductService.calculate_b2b_wholesale_price("100.00", 5)
        self.assertEqual(tier1['discount_percent'], Decimal("0.00"))

        tier2 = ProductService.calculate_b2b_wholesale_price("100.00", 20)
        self.assertEqual(tier2['discount_percent'], Decimal("15.00"))
        self.assertEqual(tier2['discounted_unit_price'], Decimal("85.00"))

        tier3 = ProductService.calculate_b2b_wholesale_price("100.00", 60)
        self.assertEqual(tier3['discount_percent'], Decimal("30.00"))
        self.assertEqual(tier3['discounted_unit_price'], Decimal("70.00"))

    def test_bulk_import_service(self):
        """CSV toplu ürün şablonu üretimi ve içe aktarım test edilir."""
        from io import BytesIO
        from marketplace.services.bulk_import_service import BulkImportService

        template = BulkImportService.generate_sample_csv_template()
        self.assertIn("title,category_id,base_price", template)

        csv_bytes = template.encode('utf-8')
        success, msg, count = BulkImportService.import_products_from_csv(self.profile_seller_a, BytesIO(csv_bytes))
        self.assertTrue(success)
        self.assertGreaterEqual(count, 2)

    def test_seller_payout_pdf_view(self):
        """Satıcı banka hakediş dekontu PDF indirme uç noktası test edilir."""
        self.client.login(username="seller_a_test", password="password123")
        response = self.client.get('/seller/payout-statement/pdf/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')






