from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from marketplace.models import CustomUser, SellerProfile, Category, Product, ProductVariant
from marketplace.services.product_filter_dto import ProductFilterDto
from marketplace.services.product_service import ProductService

class AdvancedFilterTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Satıcı & Kategori
        self.seller_user = CustomUser.objects.create_user(username="seller_filt", role="SELLER")
        self.seller = SellerProfile.objects.create(
            user=self.seller_user, store_name="Filtre Mağazası", iban="TR12345"
        )
        self.category = Category.objects.create(name="Giyim & Aksesuar")

        # Ürün 1: Kırmızı Tişört, M Beden, Stok: 10, Fiyat: 100 TL
        self.product1 = Product.objects.create(
            seller=self.seller, category=self.category, title="Kırmızı Tişört", base_price=Decimal("100.00")
        )
        self.variant1 = ProductVariant.objects.create(
            product=self.product1, color="Kırmızı", size="M", stock=10, sku="TSHIRT-RED-M"
        )

        # Ürün 2: Mavi Jean, L Beden, Stok: 0 (Tükendi), Fiyat: 200 TL (İndirimli 150 TL)
        self.product2 = Product.objects.create(
            seller=self.seller, category=self.category, title="Mavi Jean", base_price=Decimal("200.00")
        )
        self.variant2 = ProductVariant.objects.create(
            product=self.product2, color="Mavi", size="L", price=Decimal("150.00"), stock=0, sku="JEAN-BLUE-L"
        )

        # Ürün 3: Siyah Ceket, XL Beden, Stok: 5, Fiyat: 500 TL
        self.product3 = Product.objects.create(
            seller=self.seller, category=self.category, title="Siyah Ceket", base_price=Decimal("500.00")
        )
        self.variant3 = ProductVariant.objects.create(
            product=self.product3, color="Siyah", size="XL", stock=5, sku="JACKET-BLK-XL"
        )

    def test_filter_by_color(self):
        dto = ProductFilterDto(colors=["Kırmızı"])
        products = ProductService().get_products(dto)
        self.assertIn(self.product1, products)
        self.assertNotIn(self.product2, products)

    def test_filter_by_size(self):
        dto = ProductFilterDto(sizes=["L"])
        products = ProductService().get_products(dto)
        self.assertIn(self.product2, products)
        self.assertNotIn(self.product1, products)

    def test_filter_in_stock_only(self):
        dto = ProductFilterDto(in_stock_only=True)
        products = ProductService().get_products(dto)
        self.assertIn(self.product1, products)
        self.assertIn(self.product3, products)
        self.assertNotIn(self.product2, products)  # product2 has stock 0

    def test_filter_discounted_only(self):
        dto = ProductFilterDto(discounted_only=True)
        products = ProductService().get_products(dto)
        self.assertIn(self.product2, products)
        self.assertNotIn(self.product1, products)

    def test_ajax_store_index_filter_response(self):
        response = self.client.get(reverse('store_index'), {'colors': ['Kırmızı']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn('count', json_data)
        self.assertIn('html', json_data)
        self.assertEqual(json_data['count'], 1)
        self.assertIn("Kırmızı Tişört", json_data['html'])
