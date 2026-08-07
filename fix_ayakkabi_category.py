import os
import sys
import django
import uuid
from decimal import Decimal

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Category, Product, ProductVariant, SellerProfile, ProductReview

print("Fixing Ayakkabı category with exact real photographic photos...")

# Fetch main Ayakkabı category and subcategories
cat_ayakkabi_main, _ = Category.objects.get_or_create(name='Ayakkabı', defaults={'slug': 'ayakkabi'})

def get_subcat(name, slug=None):
    if not slug:
        slug = name.lower().replace(' ', '-').replace('&', 've').replace('ç', 'c').replace('ğ', 'g').replace('ı', 'i').replace('ö', 'o').replace('ş', 's').replace('ü', 'u')
    cat, _ = Category.objects.get_or_create(name=name, defaults={'parent': cat_ayakkabi_main, 'slug': slug})
    if cat.parent != cat_ayakkabi_main:
        cat.parent = cat_ayakkabi_main
        cat.save()
    return cat

sub_klasik = get_subcat('Klasik Ayakkabı & Kundura')
sub_topuklu = get_subcat('Topuklu Ayakkabı & Babet')
sub_spor = get_subcat('Spor Ayakkabı & Sneaker')
sub_bebek = get_subcat('Bebek Ayakkabısı')

all_ayakkabi_cats = [cat_ayakkabi_main, sub_klasik, sub_topuklu, sub_spor, sub_bebek] + list(Category.objects.filter(name__icontains='ayakkabı')) + list(Category.objects.filter(parent__name__icontains='ayakkabı'))

# Clean up existing products in all Ayakkabı categories
old_products = Product.objects.filter(category__in=all_ayakkabi_cats)
for p in old_products:
    ProductVariant.objects.filter(product=p).delete()
    ProductReview.objects.filter(product=p).delete()
    p.delete()

print(f"Cleaned up {old_products.count()} old products in Ayakkabı categories.")

seller_fashion = SellerProfile.objects.filter(user__username='fashion_seller').first() or SellerProfile.objects.first()

# Real Photographic Shoe Catalog
ayakkabi_items = [
    # KLASİK AYAKKABI & KUNDURA
    {
        'title': 'Hakiki Deri Erkek Siyah Oxford Kundura',
        'desc': '%100 Hakiki dana derisi, kösele tabanlı ve bağcıklı resmi siyah oxford ayakkabı.',
        'price': Decimal('1390.00'),
        'image': 'products/classic_shoes_black_leather_real.jpg',
        'category': sub_klasik,
        'variants': [('Siyah', '40'), ('Siyah', '41'), ('Siyah', '42'), ('Siyah', '43'), ('Siyah', '44')]
    },
    {
        'title': 'Hakiki Deri Taba Tokalı Loafer Ayakkabı',
        'desc': 'El işçiliği taba deri, altın tokalı ve rahat tabanlı şık erkek loafer.',
        'price': Decimal('1290.00'),
        'image': 'products/classic_shoes_brown_loafer_real.jpg',
        'category': sub_klasik,
        'variants': [('Taba', '40'), ('Taba', '41'), ('Taba', '42'), ('Taba', '43')]
    },
    {
        'title': 'Lacivert Süet Çift Tokalı Monk Strap Klasik Ayakkabı',
        'desc': 'İtalyan lacivert süet dokulu, çift tokalı lüks tasarım klasik erkek ayakkabısı.',
        'price': Decimal('1450.00'),
        'image': 'products/classic_shoes_navy_monk_real.jpg',
        'category': sub_klasik,
        'variants': [('Lacivert', '41'), ('Lacivert', '42'), ('Lacivert', '43')]
    },
    {
        'title': 'Siyah Hakiki Deri Premium Kundura',
        'desc': 'Özel işçilik parlak siyah dana derisi, kösele tabanlı lüks erkek kundurası.',
        'price': Decimal('1490.00'),
        'image': 'products/classic_shoes_real_black.jpg',
        'category': sub_klasik,
        'variants': [('Siyah', '41'), ('Siyah', '42'), ('Siyah', '43')]
    },
    {
        'title': 'Kahverengi Deri Klasik Erkek Ayakkabı',
        'desc': 'Derin kahve tonunda el dikişli, klasik tasarım resmi erkek ayakkabısı.',
        'price': Decimal('1350.00'),
        'image': 'products/classic_shoes_real_brown.jpg',
        'category': sub_klasik,
        'variants': [('Kahverengi', '41'), ('Kahverengi', '42'), ('Kahverengi', '43')]
    },

    # TOPUKLU AYAKKABI & BABET
    {
        'title': 'Rugan Kırmızı Topuklu Stiletto Kadın Ayakkabısı',
        'desc': '10 cm ince topuk, parlak kırmızı rugan kaplama ikonik davet stilettosu.',
        'price': Decimal('899.00'),
        'image': 'products/classic_shoes_red_heels_real.jpg',
        'category': sub_topuklu,
        'variants': [('Kırmızı', '36'), ('Kırmızı', '37'), ('Kırmızı', '38'), ('Kırmızı', '39')]
    },
    {
        'title': 'Zarif Bej Taba Deri Klasik Babet Kadın Ayakkabısı',
        'desc': 'Yumuşak taba deri, fiyonk detaylı ve rahat pad tabanlı zamansız babet.',
        'price': Decimal('649.00'),
        'image': 'products/classic_shoes_beige_babet_real.jpg',
        'category': sub_topuklu,
        'variants': [('Bej Taba', '36'), ('Bej Taba', '37'), ('Bej Taba', '38'), ('Bej Taba', '39')]
    },
    {
        'title': 'Kırmızı Süet Şık Topuklu Davet Ayakkabısı',
        'desc': 'İnce topuklu, bordo-kırmızı süet kaplama özel davet ayakkabısı.',
        'price': Decimal('849.00'),
        'image': 'products/classic_shoes_real_red.jpg',
        'category': sub_topuklu,
        'variants': [('Kırmızı', '36'), ('Kırmızı', '37'), ('Kırmızı', '38')]
    },
    {
        'title': 'Taba Hakiki Deri Konforlu Babet Ayakkabı',
        'desc': 'Nefes alan hakiki taba deri kumaş, yumuşak günlük kadın babeti.',
        'price': Decimal('699.00'),
        'image': 'products/classic_shoes_real_tan.jpg',
        'category': sub_topuklu,
        'variants': [('Taba', '36'), ('Taba', '37'), ('Taba', '38')]
    },

    # SPOR AYAKKABI & SNEAKER
    {
        'title': 'Beyaz Deri Günlük Unisex Sneaker Spor Ayakkabı',
        'desc': 'Birinci sınıf deri, ortopedik yürüyüş tabanlı minimalist şık sneaker.',
        'price': Decimal('899.00'),
        'image': 'products/sneakers.jpg',
        'category': sub_spor,
        'variants': [('Beyaz', '38'), ('Beyaz', '40'), ('Beyaz', '42'), ('Beyaz', '44')]
    },

    # BEBEK AYAKKABISI
    {
        'title': 'Taba Deri Cırtcırtlı Ortopedik İlk Adım Bebek Ayakkabısı',
        'desc': 'Kaydırmaz yumuşak taban, bebeğin ayak gelişimini destekleyen hakiki taba deri ilk adım ayakkabısı.',
        'price': Decimal('349.00'),
        'image': 'products/baby_shoes_1.jpg',
        'category': sub_bebek,
        'variants': [('Taba', '18'), ('Taba', '19'), ('Taba', '20'), ('Taba', '21')]
    },
    {
        'title': 'Fiyonk Detaylı Pembe Kız Bebek Babet Ayakkabısı',
        'desc': 'Şirin fiyonklu, yumuşak esnek tabanlı pembe kız bebek babeti.',
        'price': Decimal('299.00'),
        'image': 'products/baby_shoes_2.jpg',
        'category': sub_bebek,
        'variants': [('Pembe', '18'), ('Pembe', '19'), ('Pembe', '20')]
    },
    {
        'title': 'Mavi-Beyaz Esnek Tabanlı Bebek Spor Ayakkabısı',
        'desc': 'Cırtlı bağcıklı, hafif ve nefes alan kumaş mavi bebek spor ayakkabısı.',
        'price': Decimal('329.00'),
        'image': 'products/baby_shoes_3.jpg',
        'category': sub_bebek,
        'variants': [('Mavi', '19'), ('Mavi', '20'), ('Mavi', '21')]
    },
    {
        'title': 'Cırtlı Süet Deri Sıcak Tutan Bebek Botu',
        'desc': 'İçi yumuşak tüylü, cırtcırtlı taba süet deri bebek bot ayakkabısı.',
        'price': Decimal('389.00'),
        'image': 'products/baby_shoes_4.jpg',
        'category': sub_bebek,
        'variants': [('Taba Süet', '19'), ('Taba Süet', '20'), ('Taba Süet', '21')]
    },
    {
        'title': 'Yumuşak Örgü Kumaş Bebek Patik Ayakkabı',
        'desc': 'Evde ve dışarıda giyilebilen yumuşacık örgü kumaş bebek patik ayakkabı.',
        'price': Decimal('249.00'),
        'image': 'products/baby_shoes_5.jpg',
        'category': sub_bebek,
        'variants': [('Bej Örgü', '18'), ('Bej Örgü', '19'), ('Bej Örgü', '20')]
    },
]

created_count = 0

for item in ayakkabi_items:
    product = Product.objects.create(
        title=item['title'],
        description=item['desc'],
        base_price=item['price'],
        image=item['image'],
        category=item['category'],
        seller=seller_fashion
    )
    created_count += 1
    
    for color, size in item['variants']:
        sku_code = f"SKU-SHOE-{product.id}-{uuid.uuid4().hex[:5].upper()}"
        ProductVariant.objects.create(
            product=product,
            color=color,
            size=size,
            price=item['price'],
            stock=25,
            sku=sku_code
        )

print(f"\nSuccessfully populated Ayakkabı category with {created_count} real photographic products!")
