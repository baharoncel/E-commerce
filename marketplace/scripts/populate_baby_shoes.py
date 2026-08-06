import os
import sys
import django

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Product, ProductVariant, Category, SellerProfile

seller = SellerProfile.objects.first()

# Ensure Category Chain: Çocuk & Bebek -> Bebek Ayakkabısı
cat_cocuk_bebek, _ = Category.objects.get_or_create(name='Çocuk & Bebek')
cat_bebek_ayakkabi, _ = Category.objects.get_or_create(name='Bebek Ayakkabısı', defaults={'parent': cat_cocuk_bebek})
if not cat_bebek_ayakkabi.parent:
    cat_bebek_ayakkabi.parent = cat_cocuk_bebek
    cat_bebek_ayakkabi.save()

baby_shoes_list = [
    {
        'title': 'Hakiki Deri Kahverengi İlk Adım Bebek Ayakkabısı',
        'desc': '%100 nefes alabilir hakiki kuzu derisinden üretilmiş, kaydırmaz esnek yumuşak tabanlı, kemik gelişimini destekleyen ilk adım bebek patiği.',
        'price': 420.00,
        'img': 'products/baby_shoes_1.jpg',
        'colors': ['Taban Kahve', 'Koyu Taba'],
        'sizes': ['18', '19', '20', '21']
    },
    {
        'title': 'Sevimli Pembe Fiyonklu Deri Bebek Babeti',
        'desc': 'Özel gün ve doğum günü konseptlerine uygun, cırt cırtlı bağlamalı, ortopedik pedli ve fiyonk detaylı kız bebek babet ayakkabısı.',
        'price': 390.00,
        'img': 'products/baby_shoes_2.jpg',
        'cat': cat_bebek_ayakkabi,
        'colors': ['Pudra Pembe', 'Şeker Pembe'],
        'sizes': ['18', '19', '20']
    },
    {
        'title': 'Mavi-Beyaz Yumuşak Tabanlı Spor Bebek Ayakkabısı',
        'desc': 'Bebeklerin rahat hareket edebilmesi için havalandırma delikli, hafif sünger tabanlı ve kolay giydirilebilir spor bebek ayakkabısı.',
        'price': 350.00,
        'img': 'products/baby_shoes_3.jpg',
        'colors': ['Mavi-Beyaz', 'Lacivert-Beyaz'],
        'sizes': ['19', '20', '21', '22']
    },
    {
        'title': 'Krem Rengi Örgü Kışlık Bebek Pandufu',
        'desc': 'İçi yumuşacık welsoft peluş kaplı, bileği kavrayan düşmez tasarımlı sıcak tutan kışlık örgü bebek pandufu.',
        'price': 280.00,
        'img': 'products/baby_shoes_4.jpg',
        'colors': ['Krem', 'Bej'],
        'sizes': ['18', '19', '20']
    },
    {
        'title': 'Kırmızı Unisex Cırt Cırtlı İlk Adım Patiği',
        'desc': 'Geniş burun yapısıyla parmak sıkışmasını önleyen, terletmez pamuk astarlı canlı kırmızı unisex ilk adım bebek patiği.',
        'price': 320.00,
        'img': 'products/baby_shoes_5.jpg',
        'colors': ['Canlı Kırmızı', 'Bordo'],
        'sizes': ['18', '19', '20', '21', '22']
    }
]

print("Adding 5 unique baby shoes products to Çocuk & Bebek > Bebek Ayakkabısı...")

for item in baby_shoes_list:
    p, created = Product.objects.get_or_create(
        title=item['title'],
        defaults={
            'seller': seller,
            'category': cat_bebek_ayakkabi,
            'description': item['desc'],
            'base_price': item['price'],
            'image': item['img']
        }
    )
    if not created:
        p.category = cat_bebek_ayakkabi
        p.description = item['desc']
        p.base_price = item['price']
        p.image = item['img']
        p.save()

    # Clear old variants if any, and add new size_number variants
    p.variants.all().delete()
    for color in item['colors']:
        for size in item['sizes']:
            ProductVariant.objects.create(
                product=p,
                color=color,
                size='',
                size_number=int(size),
                stock=25,
                sku=f"BABY-{p.id}-{color}-{size}"
            )

print("5 BABY SHOES PRODUCTS POPULATED PERFECTLY!")
