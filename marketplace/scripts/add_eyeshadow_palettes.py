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

def add_eyeshadow_palettes():
    brain_dir = r"C:\Users\Bahar\.gemini\antigravity-ide\brain\54dc9cd8-2d3f-44f1-a2d9-408fd3f691fd"
    media_products_dir = r"c:\Users\Bahar\Desktop\E-commerce\media\products"
    os.makedirs(media_products_dir, exist_ok=True)

    eyeshadow_cat = Category.objects.get(id=451)
    seller = SellerProfile.objects.first()
    customer_user = CustomUser.objects.filter(role='CUSTOMER').first() or CustomUser.objects.first()

    # 1. Clean up old dummy products in Far Paleti category
    old_products = Product.objects.filter(category=eyeshadow_cat)
    count = old_products.count()
    for p in old_products:
        ProductVariant.objects.filter(product=p).delete()
        ProductReview.objects.filter(product=p).delete()
        p.delete()
    print(f"Cleaned up {count} old dummy products in Far Paleti category.")

    items = [
        {
            "src": os.path.join(brain_dir, "media__1785940144052.png"),
            "filename": "eyeshadow_rose_blossom_8color.png",
            "title": "Rose Cosmetic Blossom 8'li Nude & Işıltılı Far Paleti",
            "description": "Rose ve nude tonlarının eşsiz uyumunu sunan 8 renkli kompakt göz farı paleti. Yüksek pigmentasyon, kolay dağılan ipeksi formül ve tozutmayan yapısıyla hem günlük hem de şık gece makyajları için idealdir.",
            "price": Decimal("289.90"),
            "variants": [
                {"color": "Rose Nude", "stock": 45},
                {"color": "Warm Earth", "stock": 30}
            ],
            "reviews": [
                {"rating": 5, "comment": "Renk tonları harika, hiç tozutma yapmıyor. Gün boyu kalıcı!"},
                {"rating": 5, "comment": "Çantada taşımak için çok pratik ve renklerin pigmeti harika."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785940156858.png"),
            "filename": "eyeshadow_pink_berry_15color.png",
            "title": "Professional Pink & Berry 15 Renkli Göz Farı Paleti",
            "description": "Pembe, mürdüm, ışıltılı şampanya ve nude tonlarından oluşan 15 renkli profesyonel far paleti. Yoğun renk verimliliği, ışıltılı ve mat seçenekleri bir arada sunar.",
            "price": Decimal("349.90"),
            "variants": [
                {"color": "Berry Glam 15", "stock": 60},
                {"color": "Sunset Pink 15", "stock": 25}
            ],
            "reviews": [
                {"rating": 5, "comment": "Mat ve simli renkler bir harika. Mürdüm tonları göz rengini çok güzel ortaya çıkarıyor."},
                {"rating": 4, "comment": "Kalıcılığı çok yüksek, fiyatına göre muazzam bir palet."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785940173895.png"),
            "filename": "eyeshadow_revolution_45color.png",
            "title": "Revolution Maxi Reloaded 45 Renkli Mega Far Paleti",
            "description": "Canlı sarı, turuncu, pembe, mor ve nude tonları bir arada sunan 45 renkli mega boy göz farı paleti. Profesyonel makyaj artistleri ve makyaj severler için sınırsız kombinasyon imkanı.",
            "price": Decimal("599.90"),
            "variants": [
                {"color": "Maxi Reloaded 45", "stock": 20}
            ],
            "reviews": [
                {"rating": 5, "comment": "İçinde yok yok! Her renk kombinasyonuna uygun far var, aşık oldum."},
                {"rating": 5, "comment": "Paketlemesi sağlam ulaştı, renk skalası inanılmaz geniş."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785940193601.png"),
            "filename": "eyeshadow_flormar_sunset_10color.png",
            "title": "Flormar Sunset 10 Renkli Kremsi Doku Göz Farı Paleti",
            "description": "Gün batımı sıcak tonlarından esinlenen, 10 farklı krem ve sıcak toprak tonu barındıran fırçalı göz farı paleti. Özel yumuşak kremsi dokusu ile göz kapağına pürüzsüzce oturur.",
            "price": Decimal("249.90"),
            "variants": [
                {"color": "Sunset Nude 10", "stock": 50}
            ],
            "reviews": [
                {"rating": 5, "comment": "İçindeki fırça çok kullanışlı. Kremsi yapısı sayesinde hemen dağılıyor."},
                {"rating": 4, "comment": "Günlük makyajın vazgeçilmezi oldu."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785940215422.png"),
            "filename": "eyeshadow_naked_style_12color.png",
            "title": "Naked Rose Gold 12'li Aynalı & Fırçalı Göz Farı Paleti",
            "description": "Metalik rose gold ambalajı, entegre aynası ve çift taraflı profesyonel fırçasıyla 12 renkli sıcak toprak ve ışıltılı far paleti. İpeksi dokusu ile gün boyu bozulmayan makyaj deneyimi.",
            "price": Decimal("489.90"),
            "variants": [
                {"color": "Rose Gold Heat 12", "stock": 35}
            ],
            "reviews": [
                {"rating": 5, "comment": "Ambalajı çok lüks duruyor. Fırçası da kaliteli, gölgelendirme için mükemmel."},
                {"rating": 5, "comment": "Arkadaşıma hediye almıştım, çok beğendi. Kesinlikle tavsiye ederim."}
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
            category=eyeshadow_cat,
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
                sku=f"FAR-{product.id}-{idx+1}"
            )

        customers = list(CustomUser.objects.all()[:5])
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
        print(f"Added product: {product.title} (Price: ₺{product.base_price})")

    print(f"Successfully added {added_count} real eyeshadow palettes to Far Paleti category.")

if __name__ == "__main__":
    add_eyeshadow_palettes()
