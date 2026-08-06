from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from marketplace.models import Coupon
from marketplace.services.coupon_service import CouponService


class CouponServiceTests(TestCase):
    def setUp(self):
        self.service = CouponService()

    def test_percentage_coupon_applies_when_minimum_order_is_met(self):
        coupon = Coupon.objects.create(
            code='SAVE10',
            discount_type=Coupon.DISCOUNT_TYPE_PERCENTAGE,
            discount_value=Decimal('10'),
            minimum_order_amount=Decimal('100.00'),
            usage_limit=5,
            expiration_date=timezone.now() + timezone.timedelta(days=7),
        )

        result = self.service.validate_coupon('SAVE10', Decimal('200.00'))

        self.assertTrue(result.is_valid)
        self.assertEqual(result.discount_amount, Decimal('20.00'))
        self.assertEqual(result.final_total, Decimal('180.00'))
        self.assertEqual(result.coupon, coupon)

    def test_coupon_is_invalid_when_limit_is_reached(self):
        Coupon.objects.create(
            code='USEDUP',
            discount_type=Coupon.DISCOUNT_TYPE_FIXED_AMOUNT,
            discount_value=Decimal('25.00'),
            minimum_order_amount=Decimal('50.00'),
            usage_limit=1,
            used_count=1,
            expiration_date=timezone.now() + timezone.timedelta(days=7),
        )

        result = self.service.validate_coupon('USEDUP', Decimal('80.00'))

        self.assertFalse(result.is_valid)
        self.assertEqual(result.message, 'Kupon kullanım limiti dolmuştur.')
