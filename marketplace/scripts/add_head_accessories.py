import os
import sys
import shutil
from decimal import Decimal

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Category, Product, SellerProfile, ProductVariant

def add_accessories():
    brain_dir = r"C:\Users\Bahar\.gemini\antigravity-ide\brain\3043092d-4f68-4858-be6d-1d00232fb4dc"
    media_products_dir = r"c:\Users\Bahar\Desktop\E-commerce\media\products"
    os.makedirs(media_products_dir, exist_ok=True)

    items = [
        {
            "src": os.path.join(brain_dir, "head_accessory_tiara_1785751163223.png"),
            "filename": "head_accessory_tiara.png",
            "title": "İncili ve Kristal Taşlı Lüks Gelin/Özel Gün Tacı",
            "description": "Zarif inciler ve birinci sınıf parlak kristal taşlarla bezenmiş, özel günler ve davetler için tasarlanmış lüks kadın taç aksesuarı.",
            "price": Decimal("499.90"),
            "category_name": "Baş Aksesuarları"
        },
        {
            "src": os.path.join(brain_dir, "head_accessory_hairband_1785751173752.png"),
            "filename": "head_accessory_hairband.png",
            "title": "Siyah Kadife Fiyonklu Şık Kadın Saç Bandı",
            "description": "Yumuşak kadife dokusu ve şık fiyonk detayı ile günlük kullanım ve davetler için baş aksesuarı taç.",
            "price": Decimal("249.90"),
            "category_name": "Baş Aksesuarları"
        },
        {
            "src": os.path.join(brain_dir, "head_accessory_bandana_1785751183399.png"),
            "filename": "head_accessory_bandana.png",
            "title": "%100 İpek Desenli Baş Örtüsü & Bandana",
            "description": "Canlı desenleri ve saf ipek kumaşı ile saç ve baş aksesuarı olarak kullanılabilen premium tasarım bandana.",
            "price": Decimal("389.00"),
            "category_name": "Baş Aksesuarları"
        },
        {
            "src": os.path.join(brain_dir, "head_accessory_clip_1785751193517.png"),
            "filename": "head_accessory_clip.png",
            "title": "Sedef Görünümlü Lüks Mandal Saç Tokası",
            "description": "Güçlü kavrama mekanizması ve sedef dokulu zarif görünümü ile modern saç aksesuarı tokası.",
            "price": Decimal("179.90"),
            "category_name": "Baş Aksesuarları"
        },
        {
            "src": os.path.join(brain_dir, "head_accessory_beanie_1785751203771.png"),
            "filename": "head_accessory_beanie.png",
            "title": "Yün Dokulu Soft Bej Kışlık Saç & Baş Bandı",
            "description": "Kış aylarında kulakları ve başı sıcak tutan yumuşacık örgü kışlık baş aksesuarı.",
            "price": Decimal("219.50"),
            "category_name": "Baş Aksesuarları"
        }
    ]

    seller = SellerProfile.objects.first()
    if not seller:
        print("No seller found!")
        return

    # Get or create category 426 "Baş Aksesuarları"
    cat, created = Category.objects.get_or_create(
        name="Baş Aksesuarları",
        defaults={"slug": "bas-aksesuarlari"}
    )

    created_products = []
    for item in items:
        dst_path = os.path.join(media_products_dir, item["filename"])
        if os.path.exists(item["src"]):
            shutil.copy2(item["src"], dst_path)
            print(f"Copied image to {dst_path}")
        else:
            print(f"Source file not found: {item['src']}")

        rel_image_path = f"products/{item['filename']}"

        product, p_created = Product.objects.update_or_create(
            title=item["title"],
            defaults={
                "description": item["description"],
                "base_price": item["price"],
                "category": cat,
                "seller": seller,
                "image": rel_image_path,
                "average_rating": Decimal("4.8"),
                "review_count": 12
            }
        )
        # Create a default variant if none exists
        if not product.variants.exists():
            ProductVariant.objects.create(
                product=product,
                sku=f"HEAD-ACC-{product.id}-DEF",
                stock=50,
                price=item["price"]
            )

        created_products.append(product)
        print(f"{'Created' if p_created else 'Updated'} Product ID: {product.id} - {product.title}")

    print("Successfully added 5 head accessory products!")

if __name__ == '__main__':
    add_accessories()
