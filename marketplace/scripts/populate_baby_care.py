import os
import sys
import django

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Product, ProductVariant, Category, SellerProfile

seller = SellerProfile.objects.first()

# Categories
cat_cocuk_bebek, _ = Category.objects.get_or_create(name='Çocuk & Bebek')
cat_banyo, _ = Category.objects.get_or_create(name='Temizleme & Banyo', defaults={'parent': cat_cocuk_bebek})
if not cat_banyo.parent:
    cat_banyo.parent = cat_cocuk_bebek
    cat_banyo.save()

cat_sampuan, _ = Category.objects.get_or_create(name='Bebek Şampuanı', defaults={'parent': cat_banyo})
cat_losyon, _ = Category.objects.get_or_create(name='Bebek Losyonu', defaults={'parent': cat_banyo})
cat_yag, _ = Category.objects.get_or_create(name='Bebek Masaj Yağı', defaults={'parent': cat_banyo})
cat_krem, _ = Category.objects.get_or_create(name='Pişik Kremi', defaults={'parent': cat_banyo})
cat_sabun, _ = Category.objects.get_or_create(name='Bebek Sabunu', defaults={'parent': cat_banyo})

baby_care_list = [
    {
        'title': 'Doğal Organik Göz Yakmayan Bebek Şampuanı (500ml)',
        'desc': 'Göz yakmayan saf formülü, organik papatya ve aynısefa özleriyle bebeğinizin saç ve cildini tahriş etmeden nazikçe temizleyen şampuan.',
        'price': 185.00,
        'img': 'products/baby_shampoo.jpg',
        'cat': cat_sampuan,
        'colors': ['500 ml', '300 ml'],
        'sizes': []
    },
    {
        'title': 'Hassas Ciltler İçin Bebek Nemlendirici Vücut Losyonu (250ml)',
        'desc': 'Tatlı badem yağı ve aloe vera içeren, banyo sonrası bebeğinizin cildini 24 saat nemli tutan hipoalerjenik vücut losyonu.',
        'price': 160.00,
        'img': 'products/baby_lotion.jpg',
        'cat': cat_losyon,
        'colors': ['250 ml', '150 ml'],
        'sizes': []
    },
    {
        'title': 'Rahatlatıcı Organik Bebek Masaj Yağı (200ml)',
        'desc': '%100 doğal lavanta ve papatya yağlı, banyo sonrası masaj esnasında bebeğinizi rahatlatıp gaz sancılarını dindiren masaj yağı.',
        'price': 195.00,
        'img': 'products/baby_oil.jpg',
        'cat': cat_yag,
        'colors': ['200 ml'],
        'sizes': []
    },
    {
        'title': 'Yoğun Koruyucu Çinko Oksitli Pişik Kremi (100ml)',
        'desc': '%20 Çinko Oksit ve provitamin B5 içeren, pişik oluşumunu engelleyen ve tahriş olmuş cildi anında rahatlatan bariyer pişirme kremi.',
        'price': 140.00,
        'img': 'products/baby_cream.jpg',
        'cat': cat_krem,
        'colors': ['100 ml', '75 ml'],
        'sizes': []
    },
    {
        'title': 'Zeytinyağlı Doğal Nemlendirici Bebek Sabunu (100g)',
        'desc': '%100 sızma zeytinyağından elde yapılmış, koruyucu ve sentetik koku içermeyen doğal bebek vücut ve el sabunu.',
        'price': 85.00,
        'img': 'products/baby_soap.jpg',
        'cat': cat_sabun,
        'colors': ['100g'],
        'sizes': []
    }
]

print("Adding 5 unique baby care products to Çocuk & Bebek > Temizleme & Banyo...")

for item in baby_care_list:
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

    p.variants.all().delete()
    for color in item['colors']:
        ProductVariant.objects.create(
            product=p,
            color=color,
            size='',
            stock=40,
            sku=f"CARE-{p.id}-{color}"
        )

print("5 BABY CARE PRODUCTS POPULATED PERFECTLY!")
