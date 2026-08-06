import os
import sys
import shutil
from decimal import Decimal

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Category, Product, SellerProfile, ProductVariant, ProductReview, CustomUser

def add_oralcare_products():
    brain_dir = r"C:\Users\Bahar\.gemini\antigravity-ide\brain\54dc9cd8-2d3f-44f1-a2d9-408fd3f691fd"
    media_products_dir = r"c:\Users\Bahar\Desktop\E-commerce\media\products"
    os.makedirs(media_products_dir, exist_ok=True)

    oralcare_cat = Category.objects.get(id=456)
    seller = SellerProfile.objects.first()
    customers = list(CustomUser.objects.all()[:10])

    # 1. Clean up old dummy products in Ağız Bakım Ürünleri category
    old_products = Product.objects.filter(category=oralcare_cat)
    count = old_products.count()
    for p in old_products:
        ProductVariant.objects.filter(product=p).delete()
        ProductReview.objects.filter(product=p).delete()
        p.delete()
    print(f"Cleaned up {count} old dummy products in Ağız Bakım Ürünleri category.")

    items = [
        {
            "src": os.path.join(brain_dir, "media__1785943327533.png"),
            "filename": "oralcare_listerine_coolmint.png",
            "title": "Listerine Cool Mint Nane Aromalı Ağız Bakım Suyu (500 ml)",
            "description": "Diş fırçalamanın ulaşamadığı alanlarda plak oluşumunu %70'e kadar azaltan, ferah nane aromalı 24 saat korumalı antiseptik ağız çalkalama suyu.",
            "price": Decimal("149.90"),
            "variants": [
                {"color": "Cool Mint 500ml", "stock": 80}
            ],
            "reviews": [
                {"rating": 5, "comment": "Yıllardır kullandığım tek ağız çalkalama suyu. Ağızda harika bir ferahlık bırakıyor."},
                {"rating": 5, "comment": "Diş etlerime çok iyi geldi, plak oluşumunu engelliyor."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785943342314.png"),
            "filename": "oralcare_bamboo_tongue_set.png",
            "title": "Ekolojik Bambu Diş Fırçası & Paslanmaz Çelik Dil Sıyırıcı Ağız Hijyen Seti",
            "description": "Çevre dostu, %100 doğada çözünür bambu diş fırçaları ve hijyenik paslanmaz çelik dil temizleyicilerden oluşan 10 parçalı ekolojik ağız bakım kompleksi.",
            "price": Decimal("199.90"),
            "variants": [
                {"color": "Eco Bamboo Set", "stock": 45}
            ],
            "reviews": [
                {"rating": 5, "comment": "Dil temizleyici inanılmaz etkili, sabahları ağız kokusunu sıfırlıyor. Bambu fırçalar da çok yumuşak."},
                {"rating": 4, "comment": "Plastik kullanmak istemeyenler için harika bir alternatif."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785943358294.png"),
            "filename": "oralcare_alujain_miswak_set.png",
            "title": "Alujain Organik Ağız Bakım Macunu, Hindistan Cevizi Yağı & Bakır Dil Temizleyici Set",
            "description": "Geleneksel koruyuculu misvak kılıfı, %100 doğal hindistan cevizi yağı macunu ve saf bakır dil sıyırıcı içeren lüks organik ağız bakım seti.",
            "price": Decimal("329.90"),
            "variants": [
                {"color": "Organik Bakır Set", "stock": 35}
            ],
            "reviews": [
                {"rating": 5, "comment": "Bakır dil sıyırıcı ve organik macun harika. Diş beyazlatmada da etkisini gördüm."},
                {"rating": 5, "comment": "Misvak kılıfı taşıma için çok hijyenik."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785943371397.png"),
            "filename": "oralcare_biolaturca_natural.png",
            "title": "Biolaturca %100 Doğal Beyazlatıcı Diş Macunu & Bambu Fırça Seti",
            "description": "Florür, SLS ve yapay tatlandırıcı içermeyen %100 doğal beyazlatıcı diş macunu ve siyah aktif karbon kıllı bambu diş fırçası ikilisi.",
            "price": Decimal("179.90"),
            "variants": [
                {"color": "Natural White Set", "stock": 50}
            ],
            "reviews": [
                {"rating": 5, "comment": "Kimyasalsız olması içimi çok rahatlatıyor. Diş lekelerini çok güzel temizliyor."},
                {"rating": 4, "comment": "Tadı yumuşak ve ferahlatıcı."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785943389553.png"),
            "filename": "oralcare_dentasave_zinc.png",
            "title": "DentaSave Özel Çinko Formüllü Ağız Kokusu Karşıtı Çalkalama Suyu (300 ml)",
            "description": "Kötü kokuya neden olan VSK bileşiklerini nötralize eden özel çinko aktifli, ağız kokusu ve günlük bakım için geliştirilmiş çalkalama suyu.",
            "price": Decimal("139.90"),
            "variants": [
                {"color": "Çinko Formül 300ml", "stock": 60}
            ],
            "reviews": [
                {"rating": 5, "comment": "Diş hekimimin tavsiyesi üzerine aldım, ağız kokusu sorununu kökten çözdü."},
                {"rating": 5, "comment": "Alkol içermediği için ağzı yakmıyor, koruması mükemmel."}
            ]
        }
    ]

    added_count = 0
    for item in items:
        dest_path = os.path.join(media_products_dir, item["filename"])
        if os.path.exists(item["src"]):
            shutil.copy(item["src"], dest_path)
            relative_image_path = f"products/{item['filename']}"
        else:
            print(f"Warning: Source image {item['src']} not found!")
            relative_image_path = f"products/{item['filename']}"

        product = Product.objects.create(
            seller=seller,
            category=oralcare_cat,
            title=item["title"],
            description=item["description"],
            base_price=item["price"],
            image=relative_image_path,
            average_rating=Decimal("4.9"),
            review_count=len(item["reviews"])
        )

        for idx, var in enumerate(item["variants"]):
            ProductVariant.objects.create(
                product=product,
                color=var["color"],
                stock=var["stock"],
                sku=f"ORAL-{product.id}-{idx+1}"
            )

        for rev_idx, rev in enumerate(item["reviews"]):
            rev_user = customers[rev_idx % len(customers)]
            ProductReview.objects.get_or_create(
                product=product,
                user=rev_user,
                defaults={
                    "rating": rev["rating"],
                    "comment": rev["comment"],
                    "is_approved": True
                }
            )

        added_count += 1
        print(f"Added oralcare product: {product.title} (Price: ₺{product.base_price})")

    print(f"Successfully added {added_count} real oralcare products to Ağız Bakım Ürünleri category.")

if __name__ == "__main__":
    add_oralcare_products()
