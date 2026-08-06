import os
import sys
from decimal import Decimal

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Category, Product, SellerProfile, ProductVariant

def apply():
    items = [
        {
            "title": "İnci ve Kristal Yaprak Detaylı Saç Tarak Tokası",
            "filename": "photo_1_pearl_comb_studio.png",
            "price": Decimal("289.90"),
            "desc": "Özel gün, söz, nişan ve gelin kullanımı için tasarlanmış zarif incili saç tarağı tokası."
        },
        {
            "title": "3'lü %100 İpek Saten Lüks Scrunchie Saç Lastiği Seti",
            "filename": "photo_2_satin_scrunchies_studio.png",
            "price": Decimal("149.90"),
            "desc": "Saçı kırmayan ve iz bırakmayan yumuşacık ipek saten 3'lü renkli saç Lastik tokası seti."
        },
        {
            "title": "Minimalist Altın Metal Topuz Saç Çubuğu",
            "filename": "photo_3_gold_hairpin_studio.png",
            "price": Decimal("169.00"),
            "desc": "Modern ve zarif tasarımıyla pratik topuz yapmayı sağlayan paslanmaz altın metal saç çubuğu."
        },
        {
            "title": "4'lü Kristal Taşlı Lüks Yan Saç Klipsi Seti",
            "filename": "photo_4_crystal_clips_studio.png",
            "price": Decimal("199.90"),
            "desc": "Parıltılı zirkon taşlar ve geometrik desenli premium 4'lü tel saç klipsi seti."
        },
        {
            "title": "Krem Organze Tül Fiyonklu Romantik Saç Klipsi",
            "filename": "photo_5_organza_bow_studio.png",
            "price": Decimal("179.50"),
            "desc": "Hafif organze tül kumaştan büyük boy romantik Fransız stil fiyonk saç tokası."
        }
    ]

    seller = SellerProfile.objects.first()
    hair_cat, _ = Category.objects.get_or_create(id=433, defaults={"name": "Saç Aksesuarları", "slug": "sac-aksesuarlari"})

    # Clean existing in 433
    existing = Product.objects.filter(category=hair_cat)
    for p in existing:
        ProductVariant.objects.filter(product=p).delete()
        p.delete()

    for item in items:
        product = Product.objects.create(
            title=item["title"],
            description=item["desc"],
            base_price=item["price"],
            category=hair_cat,
            seller=seller,
            image=f"products/{item['filename']}",
            average_rating=Decimal("4.9"),
            review_count=35
        )
        ProductVariant.objects.create(
            product=product,
            sku=f"HAIR-STUDIO-{product.id}",
            stock=50,
            price=item["price"]
        )
        print(f"Created Product ID: {product.id} - {product.title}")

    print("All 5 products updated with 100% hair-accessory studio photos!")

if __name__ == '__main__':
    apply()
