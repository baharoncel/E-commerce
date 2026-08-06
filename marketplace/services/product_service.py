from decimal import Decimal
from django.db import models
from django.db.models import Q, QuerySet, F
from marketplace.models import Product
from marketplace.services.product_filter_dto import ProductFilterDto



class ProductService:
    def get_products(self, filter_dto: ProductFilterDto) -> QuerySet[Product]:
        queryset = Product.objects.select_related('seller', 'category').prefetch_related('variants')

        if filter_dto.search_term:
            from marketplace.services.fuzzy_search_service import FuzzySearchService
            queryset = FuzzySearchService.search(filter_dto.search_term, queryset)
            if not isinstance(queryset, QuerySet):
                p_ids = [p.id for p in queryset]
                queryset = Product.objects.filter(id__in=p_ids).select_related('seller', 'category').prefetch_related('variants')

        if filter_dto.category_ids:
            from marketplace.models import Category
            expanded_category_ids = set(filter_dto.category_ids)
            sub_cats = Category.objects.filter(Q(id__in=filter_dto.category_ids) | Q(parent_id__in=filter_dto.category_ids))
            for sc in sub_cats:
                expanded_category_ids.add(sc.id)
                for ssc in sc.subcategories.all():
                    expanded_category_ids.add(ssc.id)
            queryset = queryset.filter(category_id__in=expanded_category_ids)


        if filter_dto.min_price is not None:
            queryset = queryset.filter(base_price__gte=filter_dto.min_price)

        if filter_dto.max_price is not None:
            queryset = queryset.filter(base_price__lte=filter_dto.max_price)

        if filter_dto.seller_id:
            queryset = queryset.filter(seller_id=filter_dto.seller_id)

        if filter_dto.min_rating is not None:
            queryset = queryset.filter(average_rating__gte=filter_dto.min_rating)

        if filter_dto.colors:
            queryset = queryset.filter(variants__color__in=filter_dto.colors)

        if filter_dto.sizes:
            queryset = queryset.filter(
                Q(variants__size__in=filter_dto.sizes) | Q(variants__size_number__in=[int(s) for s in filter_dto.sizes if s.isdigit()])
            )

        if filter_dto.in_stock_only:
            queryset = queryset.filter(variants__stock__gt=0)

        if filter_dto.discounted_only:
            queryset = queryset.filter(variants__price__isnull=False, variants__price__lt=models.F('base_price'))

        queryset = queryset.distinct()

        sort_by = filter_dto.sort_by or 'newest'
        if sort_by == 'price_asc':
            queryset = queryset.order_by('base_price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-base_price')
        elif sort_by == 'rating_desc':
            queryset = queryset.order_by('-average_rating')
        elif sort_by == 'popularity':
            queryset = queryset.order_by('-review_count', '-average_rating')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    @staticmethod
    def calculate_b2b_wholesale_price(base_unit_price, quantity):
        """
        Toptan B2B alımlarında kademeli indirim hesaplar:
        1-9 adet: %0 (Standart)
        10-49 adet: %15 İndirim
        50+ adet: %30 İndirim
        """
        qty = int(quantity)
        price = Decimal(str(base_unit_price))

        if qty >= 50:
            discount_percent = Decimal("30.00")
        elif qty >= 10:
            discount_percent = Decimal("15.00")
        else:
            discount_percent = Decimal("0.00")

        factor = Decimal("1.00") - (discount_percent / Decimal("100.00"))
        discounted_unit_price = round(price * factor, 2)
        total_price = round(discounted_unit_price * qty, 2)

        return {
            'quantity': qty,
            'original_unit_price': price,
            'discount_percent': discount_percent,
            'discounted_unit_price': discounted_unit_price,
            'total_price': total_price
        }


