from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from django.utils import timezone
from marketplace.models import Coupon


@dataclass
class CouponValidationResult:
    is_valid: bool
    message: str
    discount_amount: Decimal = Decimal('0.00')
    final_total: Decimal = Decimal('0.00')
    coupon: Coupon | None = None


class ICouponService:
    def validate_coupon(self, code: str, subtotal: Decimal) -> CouponValidationResult:
        raise NotImplementedError


class CouponService(ICouponService):
    def validate_coupon(self, code: str, subtotal: Decimal) -> CouponValidationResult:
        if not code:
            return CouponValidationResult(False, 'Kupon kodu girilmedi.')

        try:
            coupon = Coupon.objects.get(code__iexact=code)
        except Coupon.DoesNotExist:
            return CouponValidationResult(False, 'Geçersiz kupon kodu.')

        now = timezone.now()
        if coupon.expiration_date and coupon.expiration_date < now:
            return CouponValidationResult(False, 'Kupon süresi dolmuştur.')

        if coupon.usage_limit is not None and coupon.used_count >= coupon.usage_limit:
            return CouponValidationResult(False, 'Kupon kullanım limiti dolmuştur.')

        if subtotal < coupon.minimum_order_amount:
            return CouponValidationResult(False, f'Minimum sepet tutarı {coupon.minimum_order_amount} TL olmalıdır.')

        discount_amount = self._calculate_discount_amount(coupon, subtotal)
        final_total = subtotal - discount_amount
        return CouponValidationResult(
            True,
            'Kupon başarıyla uygulandı.',
            discount_amount=discount_amount,
            final_total=final_total,
            coupon=coupon,
        )

    def _calculate_discount_amount(self, coupon: Coupon, subtotal: Decimal) -> Decimal:
        if coupon.discount_type == Coupon.DISCOUNT_TYPE_PERCENTAGE:
            discount = subtotal * (coupon.discount_value / Decimal('100'))
        else:
            discount = coupon.discount_value
            if discount > subtotal:
                discount = subtotal
        return discount.quantize(Decimal('0.01'))
