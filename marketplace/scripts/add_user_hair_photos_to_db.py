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

def add_user_photos():
    brain_dir = r"C:\Users\Bahar\.gemini\antigravity-ide\brain\3043092d-4f68-4858-be6d-1d00232fb4dc"
    media_dir = r"c:\Users\Bahar\Desktop\E-commerce\media\products"
    os.makedirs(media_dir, exist_ok=True)

    items = [
        {
            "src": os.path.join(brain_dir, "media__1785771976580.png"),
            "dst_name": "user_hair_starfish_chain.png",
            "title": "Deniz Yıldızı ve İnci Detaylı Plaj Saç Zinciri",
            "desc": "Örgülü ve açık saçlar için tasarlanmış deniz yıldızları ve inci taneleriyle bezenmiş zarif saç zinciri aksesuarı.",
            "price": Decimal("249.90")
        },
        {
            "src": os.path.join(brain_dir, "media__1785771996656.png"),
            "dst_name": "user_hair_silver_leaf_comb.png",
            "title": "Gelin Kristal Taşlı Yaprak Motifli Lüks Yan Saç Tokası",
            "desc": "Özel gün, nişan ve gelin kullanımı için ışıltılı zirkon kristal yaprak desenli gösterişli yan saç tarağı tokası.",
            "price": Decimal("399.90")
        },
        {
            "src": os.path.join(brain_dir, "media__1785772027033.png"),
            "dst_name": "user_hair_boho_forehead_chain.png",
            "title": "Bohem Kristal Taşlı Alınlık & Saç Zinciri Taç",
            "desc": "Alın ve saç etrafını saran sarkıt kristal taşlı otantik bohem gelin ve davet saç zinciri taç.",
            "price": Decimal("349.90")
        },
        {
            "src": os.path.join(brain_dir, "media__1785772054117.png"),
            "dst_name": "user_hair_gold_leaf_branch.png",
            "title": "Altın Yaprak ve İnci Motifli Yan Saç Tarağı & Tokası",
            "desc": "Altın sarısı dallar, yapraklar ve inci detaylı romantik yan saç aksesuarı tokası.",
            "price": Decimal("279.90")
        }
    ]

    seller = SellerProfile.objects.first()
    hair_cat, _ = Category.objects.get_or_create(id=433, defaults={"name": "Saç Aksesuarları", "slug": "sac-aksesuarlari"})

    # Clean previous products in Category 433
    existing = Product.objects.filter(category=hair_cat)
    for p in existing:
        ProductVariant.objects.filter(product=p).delete()
        p.delete()

    for item in items:
        dst_path = os.path.join(media_dir, item["dst_name"])
        if os.path.exists(item["src"]):
            shutil.copy2(item["src"], dst_path)
            print(f"Copied user photo to {dst_path}")
        else:
            print(f"Source photo not found: {item['src']}")

        product = Product.objects.create(
            title=item["title"],
            description=item["desc"],
            base_price=item["price"],
            category=hair_cat,
            seller=seller,
            image=f"products/{item['dst_name']}",
            average_rating=Decimal("5.0"),
            review_count=42
        )
        ProductVariant.objects.create(
            product=product,
            sku=f"HAIR-USER-{product.id}",
            stock=50,
            price=item["price"]
        )
        print(f"Created Product ID: {product.id} - {product.title}")

    print("Successfully added all 4 user uploaded hair accessory products!")

if __name__ == '__main__':
    add_user_photos()
