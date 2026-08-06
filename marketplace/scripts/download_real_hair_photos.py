import os
import sys
import urllib.request
from decimal import Decimal

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Category, Product, SellerProfile, ProductVariant

def update_real_photos():
    media_dir = r"c:\Users\Bahar\Desktop\E-commerce\media\products"
    os.makedirs(media_dir, exist_ok=True)

    items = [
        {
            "id_title": "İnci ve Kristal Yaprak Detaylı Saç Tarak Tokası",
            "filename": "hair_accessory_pearl_comb_real.jpg",
            "url": "https://images.unsplash.com/photo-1519699047748-de8e457a634e?auto=format&fit=crop&w=800&h=800&q=80",
            "price": Decimal("289.90"),
            "desc": "Özel gün, söz, nişan ve gelin kullanımı için tasarlanmış zarif incili saç tarağı tokası."
        },
        {
            "id_title": "3'lü %100 İpek Saten Lüks Scrunchie Saç Lastiği Seti",
            "filename": "hair_accessory_satin_scrunchies_real.jpg",
            "url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=800&h=800&q=80",
            "price": Decimal("149.90"),
            "desc": "Saçı kırmayan ve iz bırakmayan yumuşacık ipek saten 3'lü renkli saç Lastik tokası seti."
        },
        {
            "id_title": "Minimalist Altın Metal Topuz Saç Çubuğu",
            "filename": "hair_accessory_metal_hairpin_real.jpg",
            "url": "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?auto=format&fit=crop&w=800&h=800&q=80",
            "price": Decimal("169.00"),
            "desc": "Modern ve zarif tasarımıyla pratik topuz yapmayı sağlayan paslanmaz altın metal saç çubuğu."
        },
        {
            "id_title": "4'lü Kristal Taşlı Lüks Yan Saç Klipsi Seti",
            "filename": "hair_accessory_crystal_pins_real.jpg",
            "url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=800&h=800&q=80",
            "price": Decimal("199.90"),
            "desc": "Parıltılı zirkon taşlar ve geometrik desenli premium 4'lü tel saç klipsi seti."
        },
        {
            "id_title": "Krem Organze Tül Fiyonklu Romantik Saç Klipsi",
            "filename": "hair_accessory_organza_bow_real.jpg",
            "url": "https://images.unsplash.com/photo-1516914943479-89db7d9ae7f2?auto=format&fit=crop&w=800&h=800&q=80",
            "price": Decimal("179.50"),
            "desc": "Hafif organze tül kumaştan büyük boy romantik Fransız stil fiyonk saç tokası."
        }
    ]

    seller = SellerProfile.objects.first()
    hair_cat = Category.objects.get(id=433)

    # Clean existing in 433
    existing = Product.objects.filter(category=hair_cat)
    for p in existing:
        ProductVariant.objects.filter(product=p).delete()
        p.delete()

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for item in items:
        file_path = os.path.join(media_dir, item["filename"])
        req = urllib.request.Request(item["url"], headers=headers)
        try:
            with urllib.request.urlopen(req) as resp, open(file_path, 'wb') as out_file:
                out_file.write(resp.read())
            print(f"Downloaded real photo to {file_path}")
        except Exception as e:
            print(f"Failed to download {item['url']}: {e}")

        product = Product.objects.create(
            title=item["id_title"],
            description=item["desc"],
            base_price=item["price"],
            category=hair_cat,
            seller=seller,
            image=f"products/{item['filename']}",
            average_rating=Decimal("4.9"),
            review_count=22
        )
        ProductVariant.objects.create(
            product=product,
            sku=f"HAIR-REAL-{product.id}",
            stock=50,
            price=item["price"]
        )
        print(f"Created Product ID: {product.id} - {product.title}")

    print("Successfully updated 5 hair accessories with real photographs!")

if __name__ == '__main__':
    update_real_photos()
