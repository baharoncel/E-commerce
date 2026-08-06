import os
import sys
import django

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Product, ProductVariant, Category, SellerProfile, FlashSale
from django.utils import timezone
import datetime

seller = SellerProfile.objects.first()

# 1. Ensure Top-level and Sub Categories Exist
cat_giyim, _ = Category.objects.get_or_create(name='Giyim & Moda')
cat_aksesuar, _ = Category.objects.get_or_create(name='Saat & Aksesuar')
cat_ayakkabi, _ = Category.objects.get_or_create(name='Ayakkabı')
cat_elektronik, _ = Category.objects.get_or_create(name='Elektronik & Teknoloji')
cat_kozmetik, _ = Category.objects.get_or_create(name='Kozmetik & Kişisel Bakım')

# Complete catalog with unique fashion, electronics, cosmetics, accessories
catalog = [
    # GİYİM & MODA
    {
        'title': 'Zarif İpek Kırmızı Gece Elbisesi',
        'desc': 'Özel davetler ve mezuniyet organizasyonları için tasarlanmış, dökümlü ve zarafeti ön plana çıkaran %100 saf ipek kırmızı gece elbisesi.',
        'price': 1950.00,
        'img': 'products/dress.jpg',
        'cat': cat_giyim,
        'colors': ['Kırmızı', 'Bordo', 'Siyah'],
        'sizes': ['S (36)', 'M (38)', 'L (40)']
    },
    {
        'title': 'İtalyan Stil Hakiki Deri Ceket',
        'desc': 'Hakiki kuzu derisinden üretilmiş, rüzgara dayanıklı, içi saten astarlı ve modern kesim premium deri ceket.',
        'price': 2890.00,
        'img': 'products/jacket.jpg',
        'cat': cat_giyim,
        'colors': ['Siyah', 'Kahverengi'],
        'sizes': ['M', 'L', 'XL']
    },

    # SAAT & AKSESUAR
    {
        'title': 'Lüks Erkek Kronometre Kol Saati',
        'desc': 'Paslanmaz çelik kasa, çizilmez safir kristal cam ve hakiki deri kordonlu, 50m su geçirmez lüks otomatik kronometre kol saati.',
        'price': 1450.00,
        'img': 'products/watch.jpg',
        'cat': cat_aksesuar,
        'colors': ['Altın', 'Gümüş', 'Siyah'],
        'sizes': []
    },
    {
        'title': 'Tasarım Deri Omuz ve El Çantası',
        'desc': 'Çok gözlü iç tasarımı, altın detaylı fermuarları ve ayarlanabilir askısıyla şıklığı tamamlayan özel tasarım deri el çantası.',
        'price': 1250.00,
        'img': 'products/handbag.jpg',
        'cat': cat_aksesuar,
        'colors': ['Taba', 'Siyah', 'Krem'],
        'sizes': []
    },
    {
        'title': 'Klasik Aviator Güneş Gözlüğü',
        'desc': 'UV400 korumalı, polarize polarize camlı ve hafif altın kaplama metal çerçeveli unisex aviator güneş gözlüğü.',
        'price': 680.00,
        'img': 'products/sunglasses.jpg',
        'cat': cat_aksesuar,
        'colors': ['Altın-Siyah', 'Gümüş-Mavi', 'Siyah-Siyah'],
        'sizes': []
    },

    # AYAKKABI
    {
        'title': 'Minimalist Deri Beyaz Sneaker Ayakkabı',
        'desc': 'Günlük kullanım için ultra hafif ortopedik tabanlı, %100 hakiki deri minimalist beyaz sneaker ayakkabı.',
        'price': 980.00,
        'img': 'products/sneakers.jpg',
        'cat': cat_ayakkabi,
        'colors': ['Beyaz', 'Siyah'],
        'sizes': ['40', '41', '42', '43']
    },

    # ELEKTRONİK & TEKNOLOJİ
    {
        'title': 'Gürültü Önleyici Aktif Kablosuz Kulaklık (ANC)',
        'desc': '40 saate varan pil ömrü, yüksek çözünürlüklü Hi-Fi ses sürücüleri ve aktif gürültü engelleme (ANC) özellikli Bluetooth kulaklık.',
        'price': 2150.00,
        'img': 'products/headphones.jpg',
        'cat': cat_elektronik,
        'colors': ['Mat Siyah', 'Gümüş Gri'],
        'sizes': []
    },
    {
        'title': 'Akıllı Spor Saat (Smartwatch OLED)',
        'desc': 'Kalp ritmi, nabız ve kanda oksijen ölçümü yapan, su geçirmez, GPS destekli ve uzun ömürlü bataryalı akıllı saat.',
        'price': 1850.00,
        'img': 'products/smartwatch.jpg',
        'cat': cat_elektronik,
        'colors': ['Siyah Spor', 'Silikon Turuncu'],
        'sizes': []
    },

    # KOZMETİK & KİŞİSEL BAKIM
    {
        'title': 'Niş Odunsu ve Çiçeksi Özel Parfüm (100ml)',
        'desc': 'Kalıcı ve büyüleyici nota geçişlerine sahip, oryantal ve odunsu dokunuşlu lüks esanslı niş parfüm.',
        'price': 1650.00,
        'img': 'products/perfume.jpg',
        'cat': cat_kozmetik,
        'colors': ['100 ml'],
        'sizes': []
    }
]

print("Populating all categories with diverse products...")

# Update first N existing products, create new ones if needed
prods = list(Product.objects.all())

for i, item in enumerate(catalog):
    if i < len(prods):
        p = prods[i]
        p.title = item['title']
        p.description = item['desc']
        p.base_price = item['price']
        p.image = item['img']
        p.category = item['cat']
        if seller:
            p.seller = seller
        p.save()
    else:
        p = Product.objects.create(
            seller=seller,
            category=item['cat'],
            title=item['title'],
            description=item['desc'],
            base_price=item['price'],
            image=item['img']
        )

    # Ensure variants
    existing_variants = list(p.variants.all())
    idx = 0
    for color in item['colors']:
        for size in (item['sizes'] or ['']):
            is_num = size.isdigit()
            size_str = '' if is_num else size
            size_num = int(size) if is_num else None

            if idx < len(existing_variants):
                v = existing_variants[idx]
                v.color = color
                v.size = size_str
                v.size_number = size_num
                v.stock = 30
                v.save()
            else:
                ProductVariant.objects.create(
                    product=p,
                    color=color,
                    size=size_str,
                    size_number=size_num,
                    stock=30,
                    sku=f"{p.id}-{color}-{size}"
                )
            idx += 1

print("ALL CATEGORIES POPULATED WITH DIVERSE PRODUCTS SUCCESSFULLY!")
