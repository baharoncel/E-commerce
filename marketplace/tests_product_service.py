from decimal import Decimal
from django.test import TestCase
from marketplace.models import Category, Product, SellerProfile, CustomUser
from marketplace.services.product_filter_dto import ProductFilterDto
from marketplace.services.product_service import ProductService


class ProductServiceTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='seller1', password='testpass123')
        self.seller = SellerProfile.objects.create(user=self.user, store_name='Test Store', iban='TR123', commission_rate=10)
        self.category = Category.objects.create(name='Giyim', slug='giyim')
        self.other_category = Category.objects.create(name='Elektronik', slug='elektronik')

        self.product_one = Product.objects.create(
            seller=self.seller,
            category=self.category,
            title='Yazlık Tişört',
            description='Beyaz tişört',
            base_price=Decimal('120.00'),
        )
        self.product_two = Product.objects.create(
            seller=self.seller,
            category=self.other_category,
            title='Akıllı Saat',
            description='Yüksek kalite',
            base_price=Decimal('300.00'),
        )

    def test_filters_products_in_database_query(self):
        filter_dto = ProductFilterDto(
            search_term='tişört',
            category_ids=[self.category.id],
            min_price=Decimal('100.00'),
            max_price=Decimal('150.00'),
            sort_by='price_asc',
        )

        products = ProductService().get_products(filter_dto)

        self.assertEqual(list(products), [self.product_one])
