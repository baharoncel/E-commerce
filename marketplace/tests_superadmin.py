from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from marketplace.models import CustomUser, SellerProfile, Category, Coupon

class SuperadminDashboardTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Superadmin Kullanıcı
        self.superadmin = CustomUser.objects.create_user(
            username="superadmin_test",
            email="admin@test.com",
            password="adminpassword123",
            role="SUPERADMIN"
        )

        # Müşteri Kullanıcı
        self.customer = CustomUser.objects.create_user(
            username="customer_test",
            email="customer@test.com",
            password="customerpassword123",
            role="CUSTOMER"
        )

        # Satıcı Kullanıcı & Profili
        self.seller_user = CustomUser.objects.create_user(
            username="seller_test",
            email="seller@test.com",
            password="sellerpassword123",
            role="SELLER"
        )
        self.seller_profile = SellerProfile.objects.create(
            user=self.seller_user,
            store_name="Test Mağaza",
            iban="TR123456789012345678901234",
            commission_rate=Decimal("10.00"),
            is_approved=False
        )

        # Kategori
        self.category = Category.objects.create(name="Elektronik")

    def test_superadmin_dashboard_access_denied_for_customer(self):
        self.client.login(username="customer_test", password="customerpassword123")
        response = self.client.get(reverse('superadmin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('store_index'))

    def test_superadmin_dashboard_access_allowed_for_superadmin(self):
        self.client.login(username="superadmin_test", password="adminpassword123")
        response = self.client.get(reverse('superadmin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/dashboard.html')

    def test_admin_toggle_seller_approval(self):
        self.client.login(username="superadmin_test", password="adminpassword123")
        self.assertFalse(self.seller_profile.is_approved)

        # Toggle approval to True
        response = self.client.post(reverse('admin_toggle_seller_approval', args=[self.seller_profile.id]))
        self.assertEqual(response.status_code, 302)
        self.seller_profile.refresh_from_db()
        self.assertTrue(self.seller_profile.is_approved)

        # Toggle approval back to False
        self.client.post(reverse('admin_toggle_seller_approval', args=[self.seller_profile.id]))
        self.seller_profile.refresh_from_db()
        self.assertFalse(self.seller_profile.is_approved)

    def test_admin_update_commission_rate(self):
        self.client.login(username="superadmin_test", password="adminpassword123")
        response = self.client.post(
            reverse('admin_update_commission_rate', args=[self.seller_profile.id]),
            {'commission_rate': '15.50'}
        )
        self.assertEqual(response.status_code, 302)
        self.seller_profile.refresh_from_db()
        self.assertEqual(self.seller_profile.commission_rate, Decimal('15.50'))

    def test_admin_create_and_delete_category(self):
        self.client.login(username="superadmin_test", password="adminpassword123")
        
        # Create Category
        response = self.client.post(reverse('admin_create_category'), {
            'name': 'Akıllı Telefon',
            'parent_id': self.category.id
        })
        self.assertEqual(response.status_code, 302)
        subcat = Category.objects.get(name='Akıllı Telefon')
        self.assertEqual(subcat.parent, self.category)

        # Delete Category
        response = self.client.post(reverse('admin_delete_category', args=[subcat.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Category.objects.filter(id=subcat.id).exists())

    def test_admin_create_platform_coupon(self):
        self.client.login(username="superadmin_test", password="adminpassword123")
        response = self.client.post(reverse('admin_create_platform_coupon'), {
            'code': 'SUPER20',
            'discount_type': 'PERCENTAGE',
            'discount_value': '20.00',
            'minimum_order_amount': '100.00',
            'usage_limit': '50'
        })
        self.assertEqual(response.status_code, 302)
        coupon = Coupon.objects.get(code='SUPER20')
        self.assertIsNone(coupon.seller)
        self.assertEqual(coupon.discount_value, Decimal('20.00'))
