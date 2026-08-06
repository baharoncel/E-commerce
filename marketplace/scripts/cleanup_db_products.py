import os
import sys
import django

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Product, ProductVariant, Category, FlashSale, OrderItem
from django.utils import timezone
import datetime

cat_giyim, _ = Category.objects.get_or_create(name='Giyim & Moda')
cat_aksesuar, _ = Category.objects.get_or_create(name='Saat & Aksesuar')
cat_ayakkabi, _ = Category.objects.get_or_create(name='Ayakkabı')

fashion_pool = [
    {
        'title': 'Zarif İpek Kırmızı Gece Elbisesi',
        'desc': 'Özel davetler ve mezuniyet organizasyonları için tasarlanmış, dökümlü ve zarafeti ön plana çıkaran %100 saf ipek kırmızı gece elbisesi.',
        'price': 1950.00,
        'img': 'products/dress.jpg',
        'cat': cat_giyim,
        'colors': ['Kırmızı', 'Bordo', 'Siyah']
    },
    {
        'title': 'İtalyan Stil Hakiki Deri Ceket',
        'desc': 'Hakiki kuzu derisinden üretilmiş, rüzgara dayanıklı, içi saten astarlı ve modern kesim premium deri ceket.',
        'price': 2890.00,
        'img': 'products/jacket.jpg',
        'cat': cat_giyim,
        'colors': ['Siyah', 'Kahverengi']
    },
    {
        'title': 'Lüks Erkek Kronometre Kol Saati',
        'desc': 'Paslanmaz çelik kasa, çizilmez safir kristal cam ve hakiki deri kordonlu, 50m su geçirmez lüks otomatik kronometre kol saati.',
        'price': 1450.00,
        'img': 'products/watch.jpg',
        'cat': cat_aksesuar,
        'colors': ['Altın', 'Gümüş', 'Siyah']
    },
    {
        'title': 'Minimalist Deri Beyaz Sneaker Ayakkabı',
        'desc': 'Günlük kullanım için ultra hafif ortopedik tabanlı, %100 hakiki deri minimalist beyaz sneaker ayakkabı.',
        'price': 980.00,
        'img': 'products/sneakers.jpg',
        'cat': cat_ayakkabi,
        'colors': ['Beyaz', 'Siyah']
    },
    {
        'title': 'Tasarım Deri Omuz ve El Çantası',
        'desc': 'Çok gözlü iç tasarımı, altın detaylı fermuarları ve ayarlanabilir askısıyla şıklığı tamamlayan özel tasarım deri el çantası.',
        'price': 1250.00,
        'img': 'products/handbag.jpg',
        'cat': cat_aksesuar,
        'colors': ['Taba', 'Siyah', 'Krem']
    }
]

# Update ALL products in DB to cleanly match the fashion pool
all_prods = Product.objects.all()
print(f"Harmonizing all {all_prods.count()} products in database...")

for i, p in enumerate(all_prods):
    item = fashion_pool[i % len(fashion_pool)]
    p.title = item['title']
    p.description = item['desc']
    p.base_price = item['price']
    p.image = item['img']
    p.category = item['cat']
    p.save()

    # Update variants colors cleanly
    for v in p.variants.all():
        v.color = item['colors'][0]
        v.save()

print("ALL PRODUCTS IN DATABASE HARMONIZED 100% PERFECTLY!")
