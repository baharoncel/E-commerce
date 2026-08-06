import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from marketplace.models import (
    SellerProfile, Category, Product, ProductVariant,
    Order, SubOrder, OrderItem, Coupon, ProductReview
)

User = get_user_model()

class Command(BaseCommand):
    help = "Sisteme staj ve geliştirme için eksiksiz test verileri (Kullanıcılar, Kategoriler, Ürünler, Siparişler, Kuponlar) yükler."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 Veritabanı test verileri oluşturuluyor..."))

        # 1. KULLANICILAR
        # Superadmin
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@marketplace.com", "role": "SUPERADMIN", "is_staff": True, "is_superuser": True}
        )
        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(self.style.SUCCESS("  [+] Superadmin oluşturuldu: admin / admin123"))

        # Satıcı 1
        seller_user1, _ = User.objects.get_or_create(
            username="tech_seller",
            defaults={"email": "tech@marketplace.com", "role": "SELLER"}
        )
        seller_user1.set_password("seller123")
        seller_user1.save()

        seller_profile1, _ = SellerProfile.objects.get_or_create(
            user=seller_user1,
            defaults={
                "store_name": "TeknoDiyarı Mağazası",
                "iban": "TR990006200000000123456789",
                "commission_rate": Decimal("10.00"),
                "is_approved": True
            }
        )

        # Satıcı 2
        seller_user2, _ = User.objects.get_or_create(
            username="fashion_seller",
            defaults={"email": "fashion@marketplace.com", "role": "SELLER"}
        )
        seller_user2.set_password("seller123")
        seller_user2.save()

        seller_profile2, _ = SellerProfile.objects.get_or_create(
            user=seller_user2,
            defaults={
                "store_name": "Stil & Moda Mağazası",
                "iban": "TR990006200000000987654321",
                "commission_rate": Decimal("12.50"),
                "is_approved": True
            }
        )
        self.stdout.write(self.style.SUCCESS("  [+] Satıcı profilleri oluşturuldu: tech_seller, fashion_seller (şifre: seller123)"))

        # Müşteriler
        customer1, _ = User.objects.get_or_create(
            username="ahmet_yilmaz",
            defaults={"email": "ahmet@gmail.com", "role": "CUSTOMER", "first_name": "Ahmet", "last_name": "Yılmaz"}
        )
        customer1.set_password("customer123")
        customer1.save()

        customer2, _ = User.objects.get_or_create(
            username="ayse_kaya",
            defaults={"email": "ayse@gmail.com", "role": "CUSTOMER", "first_name": "Ayşe", "last_name": "Kaya"}
        )
        customer2.set_password("customer123")
        customer2.save()
        self.stdout.write(self.style.SUCCESS("  [+] Test müşterileri oluşturuldu: ahmet_yilmaz, ayse_kaya (şifre: customer123)"))

        # 2. KATEGORİLER (Tam Ağaç)
        cat_giyim, _ = Category.objects.get_or_create(name="Giyim & Moda")
        cat_kadin, _ = Category.objects.get_or_create(name="Kadın Giyim", parent=cat_giyim)
        cat_erkek, _ = Category.objects.get_or_create(name="Erkek Giyim", parent=cat_giyim)
        cat_tshirt, _ = Category.objects.get_or_create(name="Tişört", parent=cat_giyim)
        cat_gomlek, _ = Category.objects.get_or_create(name="Gömlek", parent=cat_giyim)
        cat_bluz, _ = Category.objects.get_or_create(name="Bluz", parent=cat_giyim)
        cat_pantolon, _ = Category.objects.get_or_create(name="Pantolon", parent=cat_giyim)
        cat_jean, _ = Category.objects.get_or_create(name="Jean (Kot)", parent=cat_giyim)
        cat_etek, _ = Category.objects.get_or_create(name="Etek", parent=cat_giyim)
        cat_elbise, _ = Category.objects.get_or_create(name="Elbise", parent=cat_giyim)

        cat_cocuk, _ = Category.objects.get_or_create(name="Çocuk & Bebek")
        cat_bebek_giyim, _ = Category.objects.get_or_create(name="Bebek Giyim", parent=cat_cocuk)
        cat_bebek_ayakkabi, _ = Category.objects.get_or_create(name="Bebek Ayakkabı", parent=cat_cocuk)

        cat_ayakkabi, _ = Category.objects.get_or_create(name="Ayakkabı")
        cat_sneaker, _ = Category.objects.get_or_create(name="Sneaker", parent=cat_ayakkabi)

        cat_aksesuar, _ = Category.objects.get_or_create(name="Aksesuar & Saat")
        cat_saat, _ = Category.objects.get_or_create(name="Saat", parent=cat_aksesuar)
        cat_canta, _ = Category.objects.get_or_create(name="Çanta", parent=cat_aksesuar)
        cat_gozluk, _ = Category.objects.get_or_create(name="Güneş Gözlüğü", parent=cat_aksesuar)

        cat_taki, _ = Category.objects.get_or_create(name="Takılar")
        cat_erkek_taki, _ = Category.objects.get_or_create(name="Erkek Takı", parent=cat_taki)
        cat_kadin_taki, _ = Category.objects.get_or_create(name="Kadın Takı", parent=cat_taki)

        cat_kozmetik, _ = Category.objects.get_or_create(name="Kozmetik & Makyaj")
        cat_parfum, _ = Category.objects.get_or_create(name="Parfüm", parent=cat_kozmetik)
        cat_cilt, _ = Category.objects.get_or_create(name="Cilt Bakımı", parent=cat_kozmetik)
        cat_sac, _ = Category.objects.get_or_create(name="Saç Bakımı", parent=cat_kozmetik)

        cat_elek, _ = Category.objects.get_or_create(name="Elektronik")
        cat_phone, _ = Category.objects.get_or_create(name="Akıllı Telefonlar", parent=cat_elek)
        cat_laptop, _ = Category.objects.get_or_create(name="Dizüstü Bilgisayarlar", parent=cat_elek)

        self.stdout.write(self.style.SUCCESS("  [+] Tüm ana ve alt kategoriler eksiksiz oluşturuldu."))

        # 3. ÜRÜNLER & VARYASYONLAR
        # Ürün 1 - Laptop
        p1, p1_created = Product.objects.get_or_create(
            title="ProBook Ultra 15'' Laptop M3 16GB RAM",
            defaults={
                "seller": seller_profile1,
                "category": cat_laptop,
                "description": "Yüksek performanslı işlemci, 16GB RAM ve 512GB SSD ile iş ve günlük kullanım için mükemmel notebook.",
                "base_price": Decimal("34999.00"),
                "image": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800",
                "average_rating": Decimal("4.80"),
                "review_count": 2
            }
        )
        if p1_created:
            ProductVariant.objects.create(product=p1, color="Uzay Grisi", size="15 Inç", price=Decimal("34999.00"), stock=15, sku="LAP-M3-GRAY")

        # Ürün 2 - Tişört
        p_tshirt, _ = Product.objects.get_or_create(
            title="Baskılı Premium Pamuk Erkek Tişört",
            defaults={
                "seller": seller_profile2,
                "category": cat_tshirt,
                "description": "%100 pamuklu, nefes alabilir kumaş ve modern baskılı tişört.",
                "base_price": Decimal("299.00"),
                "image": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800",
                "average_rating": Decimal("4.90"),
                "review_count": 5
            }
        )
        ProductVariant.objects.get_or_create(product=p_tshirt, color="Mavi", size="M", defaults={"price": Decimal("299.00"), "stock": 20, "sku": "TSH-BLU-M"})

        # Ürün 3 - Gömlek
        p_gomlek, _ = Product.objects.get_or_create(
            title="Keten Slim Fit Beyaz Kadın Gömlek",
            defaults={
                "seller": seller_profile2,
                "category": cat_gomlek,
                "description": "Doğal keten kumaş, serin tutan şık kesim beyaz gömlek.",
                "base_price": Decimal("450.00"),
                "image": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=800",
                "average_rating": Decimal("4.70"),
                "review_count": 3
            }
        )
        ProductVariant.objects.get_or_create(product=p_gomlek, color="Beyaz", size="S", defaults={"price": Decimal("450.00"), "stock": 15, "sku": "GML-WHT-S"})

        # Ürün 4 - Parfüm
        p_parfum, _ = Product.objects.get_or_create(
            title="Loris K-120 Frequence Lüks Parfüm",
            defaults={
                "seller": seller_profile2,
                "category": cat_parfum,
                "description": "Kalıcı ve büyüleyici esans, gün boyu taze kokusuyla dikkat çeken lüks parfüm.",
                "base_price": Decimal("349.00"),
                "image": "https://images.unsplash.com/photo-1541643600914-78b084683601?w=800",
                "average_rating": Decimal("4.95"),
                "review_count": 8
            }
        )
        ProductVariant.objects.get_or_create(product=p_parfum, color="Altın", defaults={"price": Decimal("349.00"), "stock": 50, "sku": "PRF-LORIS-120"})
            ProductVariant.objects.create(product=p1, color="Gümüş", size="15 Inç", price=Decimal("35999.00"), stock=8, sku="LAP-M3-SILVER")

        # Ürün 2 - Kulaklık
        p2, p2_created = Product.objects.get_or_create(
            title="Kablosuz Gürültü Engelleyici Kulaklık Pro",
            defaults={
                "seller": seller_profile1,
                "category": cat_elek,
                "description": "Aktif gürültü engelleme (ANC), 30 saat pil ömrü ve kristal netliğinde ses kalitesi.",
                "base_price": Decimal("2499.00"),
                "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800",
                "average_rating": Decimal("4.50"),
                "review_count": 1
            }
        )
        if p2_created:
            ProductVariant.objects.create(product=p2, color="Siyah", price=Decimal("2499.00"), stock=25, sku="HEAD-BLK-01")
            ProductVariant.objects.create(product=p2, color="Beyaz", price=Decimal("2499.00"), stock=20, sku="HEAD-WHT-01")

        # Ürün 3 - Deri Ceket
        p3, p3_created = Product.objects.get_or_create(
            title="Hakiki Deri Slim Fit Erkek Ceket",
            defaults={
                "seller": seller_profile2,
                "category": cat_erkek,
                "description": "%100 hakiki kuzu derisinden üretilmiş, şık ve modern slim fit kesim ceket.",
                "base_price": Decimal("3899.00"),
                "image": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800",
                "average_rating": Decimal("5.00"),
                "review_count": 1
            }
        )
        if p3_created:
            ProductVariant.objects.create(product=p3, color="Siyah", size="M", price=Decimal("3899.00"), stock=10, sku="JKT-BLK-M")
            ProductVariant.objects.create(product=p3, color="Kahverengi", size="L", price=Decimal("3999.00"), stock=5, sku="JKT-BRN-L")

        self.stdout.write(self.style.SUCCESS("  [+] Ürünler ve stok varyasyonları oluşturuldu."))

        # 4. KUPONLAR
        Coupon.objects.get_or_create(
            code="HOSGELDIN10",
            defaults={
                "discount_type": Coupon.DISCOUNT_TYPE_PERCENTAGE,
                "discount_value": Decimal("10.00"),
                "minimum_order_amount": Decimal("500.00"),
                "expiration_date": timezone.now() + timezone.timedelta(days=90)
            }
        )
        Coupon.objects.get_or_create(
            code="TEKNO200",
            defaults={
                "seller": seller_profile1,
                "discount_type": Coupon.DISCOUNT_TYPE_FIXED_AMOUNT,
                "discount_value": Decimal("200.00"),
                "minimum_order_amount": Decimal("2000.00"),
                "expiration_date": timezone.now() + timezone.timedelta(days=60)
            }
        )
        self.stdout.write(self.style.SUCCESS("  [+] Platform ve Satıcı İndirim Kuponları yüklendi."))

        # 5. MÜŞTERİ YORUMLARI
        ProductReview.objects.get_or_create(
            product=p1,
            user=customer1,
            defaults={
                "rating": 5,
                "comment": "Ürün harika! Performansı süper, paketleme çok özenliydi.",
                "is_approved": True,
                "helpful_count": 4
            }
        )
        ProductReview.objects.get_or_create(
            product=p2,
            user=customer2,
            defaults={
                "rating": 4,
                "comment": "Ses kalitesi güzel, şarjı uzun gidiyor ama biraz kulağı sıkabiliyor.",
                "is_approved": True,
                "helpful_count": 2
            }
        )

        # 6. DEMO SİPARİŞ & BÖLÜMLENMİŞ ALT SİPARİŞLER (Split Orders)
        if not Order.objects.filter(customer=customer1).exists():
            order = Order.objects.create(
                customer=customer1,
                total_amount=Decimal("37498.00"),
                payment_status="PAID",
                payment_id="PAY-99887766",
                order_status="PREPARING",
                shipping_company="Yurtiçi Kargo",
                tracking_number="YK-88239100"
            )

            # SubOrder 1 (TeknoDiyarı)
            sub1 = SubOrder.objects.create(
                parent_order=order,
                seller=seller_profile1,
                subtotal=Decimal("37498.00"),
                commission_fee=Decimal("3749.80"),
                seller_payout=Decimal("33748.20"),
                status="PENDING"
            )
            v1 = p1.variants.first()
            OrderItem.objects.create(
                sub_order=sub1,
                product=p1,
                variant=v1,
                quantity=1,
                price=v1.get_price()
            )
            v2 = p2.variants.first()
            OrderItem.objects.create(
                sub_order=sub1,
                product=p2,
                variant=v2,
                quantity=1,
                price=v2.get_price()
            )

            self.stdout.write(self.style.SUCCESS("  [+] Demo sipariş ve alt siparişler (Split Order) oluşturuldu."))

        self.stdout.write(self.style.SUCCESS("""
========================================================================
🎉 TEST VERİLERİ BAŞARIYLA OLUŞTURULDU!
------------------------------------------------------------------------
Giriş Bilgileri:
1. Superadmin (Yönetici Paneli): admin / admin123
2. Satıcı (TeknoDiyarı):         tech_seller / seller123
3. Satıcı (Stil & Moda):         fashion_seller / seller123
4. Müşteri:                      ahmet_yilmaz / customer123
5. Müşteri:                      ayse_kaya / customer123
========================================================================
"""))
