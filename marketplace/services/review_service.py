from django.db.models import Avg
from marketplace.models import ProductReview, SubOrder, OrderItem


class ReviewService:
    def can_user_review_product(self, user, product):
        if not user or not user.is_authenticated:
            return False

        has_delivered_purchase = OrderItem.objects.filter(
            product=product,
            sub_order__parent_order__customer=user,
            sub_order__status='DELIVERED'
        ).exists()

        if not has_delivered_purchase:
            return False

        existing_review = ProductReview.objects.filter(product=product, user=user).exists()
        return not existing_review

    def create_review(self, user, product, rating, comment='', image=None):
        if not self.can_user_review_product(user, product):
            raise ValueError('Bu ürünü yalnızca daha önce teslim edilmiş bir siparişinizle değerlendirebilirsiniz.')

        review = ProductReview.objects.create(
            product=product,
            user=user,
            rating=rating,
            comment=comment,
            is_approved=False,
            image=image
        )
        self._refresh_product_rating(product)
        return review

    def _refresh_product_rating(self, product):
        aggregate = ProductReview.objects.filter(product=product, is_approved=True).aggregate(avg_rating=Avg('rating'))
        avg = aggregate['avg_rating'] or 0
        product.average_rating = round(avg, 2)
        product.review_count = ProductReview.objects.filter(product=product, is_approved=True).count()
        product.save(update_fields=['average_rating', 'review_count'])
