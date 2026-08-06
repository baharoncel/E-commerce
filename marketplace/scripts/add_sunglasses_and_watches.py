import os
import sys
import shutil
from decimal import Decimal

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Category, Product, SellerProfile, ProductVariant, ProductReview

def update_items():
    brain_dir = r"C:\Users\Bahar\.gemini\antigravity-ide\brain\3043092d-4f68-4858-be6d-1d00232fb4dc"
    media_products_dir = r"c:\Users\Bahar\Desktop\E-commerce\media\products"
    os.makedirs(media_products_dir, exist_ok=True)

    sunglasses_cat, _ = Category.objects.get_or_create(id=431, defaults={"name": "Güneş Gözlüğü", "slug": "gunes-gozlugu"})
    watch_cat, _ = Category.objects.get_or_create(id=432, defaults={"name": "Saat", "slug": "saat"})

    seller = SellerProfile.objects.first()

    # 1. Clean up old dummy products in Güneş Gözlüğü and Saat
    old_products = Product.objects.filter(category__in=[sunglasses_cat, watch_cat])
    for p in old_products:
        ProductVariant.objects.filter(product=p).delete()
        ProductReview.objects.filter(product=p).delete()
        p.delete()
    print(f"Cleaned up {old_products.count()} old products in Güneş Gözlüğü & Saat.")

    sunglasses_items = [
        {
            "src": os.path.join(brain_dir, "sunglasses_black_wayfarer_1785752027197.png"),
            "filename": "accessory_sunglasses_wayfarer_real.png",
            "title": "Polarize Siyah Kemik Çerçeve Güneş Gözlüğü",
            "description": "Mat siyah kemik çerçeve, %100 UV400 korumalı polarize siyah camlı ikonik tasarım güneş gözlüğü.",
            "price": Decimal("349.90"),
            "category": sunglasses_cat
        },
        {
            "src": os.path.join(brain_dir, "sunglasses_gold_aviator_1785752042585.png"),
            "filename": "accessory_sunglasses_aviator_real.png",
            "title": "Klasik Altın Çerçeveli Damla Havacı Gözlüğü",
            "description": "İnce paslanmaz altın kaplama metal çerçeve ve koyu haki koruyucu camlı efsane havacı güneş gözlüğü.",
            "price": Decimal("429.00"),
            "category": sunglasses_cat
        },
        {
            "src": os.path.join(brain_dir, "sunglasses_cat_eye_brown_1785752063087.png"),
            "filename": "accessory_sunglasses_cateye_real.png",
            "title": "Retro Kahverengi Cat-Eye Kadın Güneş Gözlüğü",
            "description": "Kaplumbağa desenli kahverengi vintage çerçeve, şık çekik kedi gözü tasarımlı kadın güneş gözlüğü.",
            "price": Decimal("299.90"),
            "category": sunglasses_cat
        },
        {
            "src": os.path.join(brain_dir, "sunglasses_sport_mirror_1785752086244.png"),
            "filename": "accessory_sunglasses_sport_real.png",
            "title": "Aynalı Cam Aerodinamik Spor Güneş Gözlüğü",
            "description": "Gümüş reflektörlü aynalı tek parça cam, outdoor ve bisiklet kullanımı için hafif ergonomik spor gözlük.",
            "price": Decimal("389.50"),
            "category": sunglasses_cat
        }
    ]

    watch_items = [
        {
            "src": os.path.join(brain_dir, "watch_silver_steel_1785752104590.png"),
            "filename": "accessory_watch_silver_steel_real.png",
            "title": "Paslanmaz Çelik Kordon Lüks Erkek Kol Saati",
            "description": "Gümüş rengi paslanmaz çelik kordon, mavi kadranlı kronometreli ve takvimli lüks erkek saati.",
            "price": Decimal("1299.00"),
            "category": watch_cat
        },
        {
            "src": os.path.join(brain_dir, "watch_brown_leather_1785752127122.png"),
            "filename": "accessory_watch_brown_leather_real.png",
            "title": "Hakiki Kahverengi Deri Kordon Klasik Erkek Saat",
            "description": "Taba hakiki deri kordon, minimalist beyaz kadran ve gümüş çelik kasa klasik tasarım kol saati.",
            "price": Decimal("899.90"),
            "category": watch_cat
        },
        {
            "src": os.path.join(brain_dir, "watch_rose_gold_women_1785752155802.png"),
            "filename": "accessory_watch_rose_gold_real.png",
            "title": "Rose Gold İnce Hasır Çelik Kadın Kol Saati",
            "description": "Pembe altın kaplama zarif hasır çelik kordon, kristal taş detaylı şık kadın saat.",
            "price": Decimal("749.90"),
            "category": watch_cat
        },
        {
            "src": os.path.join(brain_dir, "watch_black_smartwatch_1785752177395.png"),
            "filename": "accessory_watch_smartwatch_real.png",
            "title": "Dokunmatik Ekran Siyah Akıllı Spor Saat",
            "description": "AMOLED dokunmatik ekran, nabız/adım takibi, su geçirmez siyah silikon kordonlu akıllı saat.",
            "price": Decimal("1099.00"),
            "category": watch_cat
        }
    ]

    all_items = sunglasses_items + watch_items

    for item in all_items:
        dst_path = os.path.join(media_products_dir, item["filename"])
        if os.path.exists(item["src"]):
            shutil.copy2(item["src"], dst_path)
            print(f"Copied {item['filename']}")

        p = Product.objects.create(
            title=item["title"],
            description=item["description"],
            base_price=item["price"],
            category=item["category"],
            seller=seller,
            image=f"products/{item['filename']}",
            average_rating=Decimal("4.9"),
            review_count=15
        )
        ProductVariant.objects.create(
            product=p,
            sku=f"ACC-{p.id}-DEF",
            stock=40,
            price=item["price"]
        )
        print(f"Created Product ID: {p.id} - {p.title}")

    print("All 8 products created successfully!")

if __name__ == '__main__':
    update_items()
