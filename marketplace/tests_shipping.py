from datetime import date
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from marketplace.models import CustomUser, SellerProfile, Category, Product, ProductVariant, Order, SubOrder


class ShippingTrackingTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.seller_user = CustomUser.objects.create_user(username='seller_ship', password='password123', role='SELLER')
        self.seller_profile = SellerProfile.objects.create(user=self.seller_user, store_name='Ship Store', iban='TR000000000000000000000000')
        self.customer = CustomUser.objects.create_user(username='customer_ship', password='password123', role='CUSTOMER')
        self.product = Product.objects.create(seller=self.seller_profile, category=self.category, title='Shipping Product', base_price=Decimal('100.00'))
        self.variant = ProductVariant.objects.create(product=self.product, stock=10, sku='SHIP-1')
        self.order = Order.objects.create(customer=self.customer, total_amount=Decimal('100.00'), payment_status='PAID')
        self.sub_order = SubOrder.objects.create(
            parent_order=self.order,
            seller=self.seller_profile,
            subtotal=Decimal('100.00'),
            commission_fee=Decimal('10.00'),
            seller_payout=Decimal('90.00'),
            status='PENDING',
        )

    def test_seller_can_update_shipping_details_and_parent_order_status(self):
        self.client.force_login(self.seller_user)

        response = self.client.post(
            reverse('update_suborder_status', args=[self.sub_order.id]),
            {
                'status': 'SHIPPED',
                'shipping_company': 'Yurtiçi',
                'tracking_number': 'YT-123456',
                'estimated_delivery_date': '2026-07-20',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.sub_order.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.sub_order.status, 'SHIPPED')
        self.assertEqual(self.order.order_status, 'SHIPPED')
        self.assertEqual(self.order.shipping_company, 'Yurtiçi')
        self.assertEqual(self.order.tracking_number, 'YT-123456')
        self.assertEqual(self.order.estimated_delivery_date, date(2026, 7, 20))
