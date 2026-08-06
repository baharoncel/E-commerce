from decimal import Decimal
from django.test import TestCase
from marketplace.models import CustomUser, SellerProfile, Category, Product, ProductVariant, Order, SubOrder, OrderItem, ProductReview


class ReviewServiceTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.seller_user = CustomUser.objects.create_user(username='seller', password='password123', role='SELLER')
        self.seller_profile = SellerProfile.objects.create(user=self.seller_user, store_name='Seller Store', iban='TR000000000000000000000000')
        self.customer = CustomUser.objects.create_user(username='customer', password='password123', role='CUSTOMER')
        self.product = Product.objects.create(seller=self.seller_profile, category=self.category, title='Test Product', base_price=Decimal('100.00'))
        self.variant = ProductVariant.objects.create(product=self.product, stock=5, sku='SKU-1')

    def test_customer_can_review_only_after_delivered_purchase(self):
        from marketplace.services.review_service import ReviewService

        service = ReviewService()

        self.assertFalse(service.can_user_review_product(self.customer, self.product))

        order = Order.objects.create(customer=self.customer, total_amount=Decimal('100.00'), payment_status='PAID')
        sub_order = SubOrder.objects.create(
            parent_order=order,
            seller=self.seller_profile,
            subtotal=Decimal('100.00'),
            commission_fee=Decimal('10.00'),
            seller_payout=Decimal('90.00'),
            status='DELIVERED',
        )
        OrderItem.objects.create(sub_order=sub_order, product=self.product, variant=self.variant, quantity=1, price=Decimal('100.00'))

        self.assertTrue(service.can_user_review_product(self.customer, self.product))

        review = service.create_review(self.customer, self.product, 5, 'Great product')
        self.assertEqual(review.rating, 5)
        self.assertEqual(ProductReview.objects.filter(product=self.product, user=self.customer).count(), 1)
