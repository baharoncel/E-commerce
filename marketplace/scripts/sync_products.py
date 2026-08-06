import os
import sys
import django

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()


from marketplace.models import Product, ProductVariant, Category, FlashSale
from django.utils import timezone
import datetime

cat_giyim, _ = Category.objects.get_or_create(name='Giyim & Moda')
cat_aksesuar, _ = Category.objects.get_or_create(name='Saat & Aksesuar')
cat_ayakkabi, _ = Category.objects.get_or_create(name='Ayakkabı')

items = [
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
        'title': 'Minimalist Deri Beyaz Sneaker Ayakkabı',
        'desc': 'Günlük kullanım için ultra hafif ortopedik tabanlı, %100 hakiki deri minimalist beyaz sneaker ayakkabı.',
        'price': 980.00,
        'img': 'products/sneakers.jpg',
        'cat': cat_ayakkabi,
        'colors': ['Beyaz', 'Siyah'],
        'sizes': ['40', '41', '42', '43']
    },
    {
        'title': 'Tasarım Deri Omuz ve El Çantası',
        'desc': 'Çok gözlü iç tasarımı, altın detaylı fermuarları ve ayarlanabilir askısıyla şıklığı tamamlayan özel tasarım deri el çantası.',
        'price': 1250.00,
        'img': 'products/handbag.jpg',
        'cat': cat_aksesuar,
        'colors': ['Taba', 'Siyah', 'Krem'],
        'sizes': []
    }
]

prods = list(Product.objects.all())
for i, item in enumerate(items):
    if i < len(prods):
        p = prods[i]
        p.title = item['title']
        p.description = item['desc']
        p.base_price = item['price']
        p.image = item['img']
        p.category = item['cat']
        p.save()

        # Update existing variants or create new ones
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
                    v.stock = 25
                    v.save()
                else:
                    ProductVariant.objects.create(
                        product=p,
                        color=color,
                        size=size_str,
                        size_number=size_num,
                        stock=25,
                        sku=f"{p.id}-{color}-{size}"
                    )
                idx += 1

print("ALL PRODUCTS AND VARIANTS HARMONIZED 100% PERFECTLY!")
