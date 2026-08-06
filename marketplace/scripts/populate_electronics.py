import os
import sys
import django

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Product, ProductVariant, Category, SellerProfile

seller = SellerProfile.objects.first()

cat_elektronik, _ = Category.objects.get_or_create(name='Elektronik & Teknoloji')
cat_kulaklik, _ = Category.objects.get_or_create(name='Kulaklık & Ses Sistemleri', defaults={'parent': cat_elektronik})
cat_akilli_saat, _ = Category.objects.get_or_create(name='Akıllı Saat & Bileklik', defaults={'parent': cat_elektronik})
cat_aksesuar_elek, _ = Category.objects.get_or_create(name='Bilgisayar Aksesuarları', defaults={'parent': cat_elektronik})

electronics_list = [
    {
        'title': 'Gürültü Önleyici Aktif Kablosuz Kulak Üstü Kulaklık (ANC)',
        'desc': '40 saate varan pil ömrü, yüksek çözünürlüklü Hi-Res ses sürücüleri, Bluetooth 5.3 ve aktif gürültü engelleme (ANC) özellikli kablosuz kulaklık.',
        'price': 2150.00,
        'img': 'products/headphones.jpg',
        'cat': cat_kulaklik,
        'colors': ['Mat Siyah', 'Gümüş Gri', 'Gece Mavisi'],
        'sizes': []
    },
    {
        'title': 'Akıllı Spor Saat (Smartwatch OLED)',
        'desc': '1.43 inç AMOLED dokunmatik ekran, 110+ spor modu, kanda oksijen ve nabız takibi yapan, 50m su geçirmez GPS destekli akıllı saat.',
        'price': 1850.00,
        'img': 'products/smartwatch.jpg',
        'cat': cat_akilli_saat,
        'colors': ['Siyah Spor', 'Silikon Turuncu', 'Titanyum Gri'],
        'sizes': []
    },
    {
        'title': 'Taşınabilir Güçlü Bluetooth Hoparlör (30W)',
        'desc': 'IPX7 %100 su geçirmez gövde, derin bas (Extra Bass) sürücüleri ve 24 saat kesintisiz müzik çalma süreli taşınabilir kablosuz hoparlör.',
        'price': 1290.00,
        'img': 'products/speaker.jpg',
        'cat': cat_kulaklik,
        'colors': ['Gece Mavisi', 'Asker Yeşili', 'Siyah'],
        'sizes': []
    },
    {
        'title': '4K Ultra HD Çift Ekranlı Aksiyon Kamerası',
        'desc': '4K 60fps yüksek çözünürlüklü video kaydı, ön ve arka çift ekran, Wi-Fi aktarımı ve 30m su altı muhafazalı vlogging aksiyon kamerası.',
        'price': 3450.00,
        'img': 'products/camera.jpg',
        'cat': cat_aksesuar_elek,
        'colors': ['Mat Siyah', 'Gümüş'],
        'sizes': []
    },
    {
        'title': 'Ergonomik Kablosuz Dikey Oyuncu Faresi (Mouse)',
        'desc': 'Bilek ağrısını ve yorgunluğu önleyen dikey ergonomik tasarım, RGB aydınlatma, 16.000 DPI sensör ve şarj edilebilir bataryalı dikey mouse.',
        'price': 750.00,
        'img': 'products/mouse.jpg',
        'cat': cat_aksesuar_elek,
        'colors': ['Mat Siyah', 'Beyaz RGB'],
        'sizes': []
    }
]

print("Adding 5 unique electronics products to Elektronik & Teknoloji...")

for item in electronics_list:
    p, created = Product.objects.get_or_create(
        title=item['title'],
        defaults={
            'seller': seller,
            'category': item['cat'],
            'description': item['desc'],
            'base_price': item['price'],
            'image': item['img']
        }
    )
    if not created:
        p.category = item['cat']
        p.description = item['desc']
        p.base_price = item['price']
        p.image = item['img']
        p.save()

    existing_variants = list(p.variants.all())
    for idx, color in enumerate(item['colors']):
        if idx < len(existing_variants):
            v = existing_variants[idx]
            v.color = color
            v.stock = 30
            v.save()
        else:
            ProductVariant.objects.create(
                product=p,
                color=color,
                size='',
                stock=30,
                sku=f"ELEC-{p.id}-{color}"
            )

print("5 ELECTRONICS PRODUCTS POPULATED PERFECTLY!")
