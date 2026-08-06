from django.db.models import Count, Q
from marketplace.models import Product, OrderItem, SubOrder

class RecommendationService:
    """
    Akıllı Ürün Öneri Motoru (Recommendation Engine).
    Geçmiş sipariş birlikteliklerini (Co-occurrence Matrix) ve kategori popülerliğini analiz eder.
    """

    @staticmethod
    def get_frequently_bought_together(product, limit=4):
        """
        Target bir ürün için, geçmiş siparişlerde en çok birlikte satın alınan diğer ürünleri getirir.
        ("Bu ürünü alan müşteriler şunları da satın aldı").
        """
        if not product:
            return Product.objects.none()

        # Target ürünün yer aldığı alt sipariş (SubOrder) ID'leri
        sub_order_ids = OrderItem.objects.filter(product=product).values_list('sub_order_id', flat=True)

        if sub_order_ids.exists():
            # Bu alt siparişlerde yer alan DİĞER ürünlerin kimlikleri ve frekansları
            co_bought_product_ids = (
                OrderItem.objects.filter(sub_order_id__in=sub_order_ids)
                .exclude(product=product)
                .values('product_id')
                .annotate(co_count=Count('product_id'))
                .order_by('-co_count')
                .values_list('product_id', flat=True)[:limit]
            )
            recommendations = list(Product.objects.filter(id__in=co_bought_product_ids).select_related('seller', 'category').prefetch_related('variants'))
        else:
            recommendations = []

        # Eğer birlikte satın alınan ürün sayısı limitin altındaysa, aynı kategorideki popüler ürünlerle tamamla
        if len(recommendations) < limit:
            existing_ids = [p.id for p in recommendations] + [product.id]
            category_products = (
                Product.objects.filter(category=product.category)
                .exclude(id__in=existing_ids)
                .select_related('seller', 'category')
                .prefetch_related('variants')[: (limit - len(recommendations))]
            )
            recommendations.extend(list(category_products))

        # Hala eksikse genel ürünlerle doldur
        if len(recommendations) < limit:
            existing_ids = [p.id for p in recommendations] + [product.id]
            fallback_products = (
                Product.objects.exclude(id__in=existing_ids)
                .select_related('seller', 'category')
                .prefetch_related('variants')[: (limit - len(recommendations))]
            )
            recommendations.extend(list(fallback_products))

        return recommendations[:limit]

    @staticmethod
    def get_cart_recommendations(cart_items, limit=4):
        """
        Sepetteki ürünlerle tam uyumlu / birlikte satın alınabilecek önerileri hesaplar.
        """
        if not cart_items:
            return Product.objects.all().select_related('seller', 'category').prefetch_related('variants')[:limit]

        cart_product_ids = [item['product'].id for item in cart_items if 'product' in item]
        sub_order_ids = OrderItem.objects.filter(product_id__in=cart_product_ids).values_list('sub_order_id', flat=True)

        co_product_ids = (
            OrderItem.objects.filter(sub_order_id__in=sub_order_ids)
            .exclude(product_id__in=cart_product_ids)
            .values('product_id')
            .annotate(co_count=Count('product_id'))
            .order_by('-co_count')
            .values_list('product_id', flat=True)[:limit]
        )

        recommendations = list(Product.objects.filter(id__in=co_product_ids).select_related('seller', 'category').prefetch_related('variants'))

        if len(recommendations) < limit:
            existing_ids = [p.id for p in recommendations] + cart_product_ids
            fallback = Product.objects.exclude(id__in=existing_ids).select_related('seller', 'category').prefetch_related('variants')[: (limit - len(recommendations))]
            recommendations.extend(list(fallback))

        return recommendations[:limit]
