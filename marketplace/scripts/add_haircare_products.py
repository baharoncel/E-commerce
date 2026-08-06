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

def add_haircare_products():
    brain_dir = r"C:\Users\Bahar\.gemini\antigravity-ide\brain\54dc9cd8-2d3f-44f1-a2d9-408fd3f691fd"
    media_products_dir = r"c:\Users\Bahar\Desktop\E-commerce\media\products"
    os.makedirs(media_products_dir, exist_ok=True)

    haircare_cat = Category.objects.get(id=454)
    seller = SellerProfile.objects.first()
    customers = list(CustomUser.objects.all()[:10])

    # 1. Clean up old dummy products in Saç Bakım Ürünleri category
    old_products = Product.objects.filter(category=haircare_cat)
    count = old_products.count()
    for p in old_products:
        ProductVariant.objects.filter(product=p).delete()
        ProductReview.objects.filter(product=p).delete()
        p.delete()
    print(f"Cleaned up {count} old dummy products in Saç Bakım Ürünleri category.")

    items = [
        {
            "src": os.path.join(brain_dir, "media__1785942029854.png"),
            "filename": "haircare_elseve_dream_long.png",
            "title": "L'Oreal Paris Elseve Dream Long Kırık Uç Onarıcı 5'li Bakım Rutini",
            "description": "Uzun ve yıpranmış saçlar için özel geliştirilmiş 5 parçalı komple bakım seti. Kırık uç onarıcı şampuan, saç bakım kremi, durulanmayan Bye-Bye Makas kremi, pürüzsüzleştirici serum ve uzun saç kurtarıcı maske içerir.",
            "price": Decimal("529.90"),
            "variants": [
                {"color": "Dream Long 5'li Rutin", "stock": 50}
            ],
            "reviews": [
                {"rating": 5, "comment": "Saç kestirmekten kurtaran efsane seri! Bye-Bye makas kremi saçlarımı pamuk gibi yaptı."},
                {"rating": 5, "comment": "Kokusu muhteşem, saçlarımı hiç ağırlaştırmadan parlatıyor."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785942046320.png"),
            "filename": "haircare_pantene_miracle_rescue.png",
            "title": "Pantene Miracle Rescue & Pro-V Onarıcı Lüks Saç Bakım Koleksiyonu",
            "description": "Pantene Pro-V formüllü Miracle Rescue serisi lüks bakım seti. Yoğun saç maskesi, bukle belirginleştirici krem, durulanmayan bakım spreyleri ve sülfatsız onarıcı şampuan içerir.",
            "price": Decimal("649.90"),
            "variants": [
                {"color": "Miracle Rescue Gold", "stock": 35}
            ],
            "reviews": [
                {"rating": 5, "comment": "Kuru ve boyalı saçlarımı ilk yıkamada ipek gibi yaptı. Set olarak almak çok daha karlı."},
                {"rating": 4, "comment": "Maskesi aşırı yoğun ve harika nem veriyor."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785942068706.png"),
            "filename": "haircare_urban_care_biotin.png",
            "title": "Urban Care Biotin & Caffeine Dökülme Karşıtı 3'lü Saç Bakım Kompleksi",
            "description": "Biotin ve kafein içerikli saç kökü güçlendirici, dökülme karşıtı ve hızlı uzamaya yardımcı 3'lü uzman saç bakım seti. Şampuan, saç kremi ve saç derisi peeling yağı içerir.",
            "price": Decimal("399.90"),
            "variants": [
                {"color": "Biotin & Caffeine 3'lü Set", "stock": 45}
            ],
            "reviews": [
                {"rating": 5, "comment": "Dökülmem 2 haftada gözle görülür şekilde azaldı. Bebek saçlarım çıkmaya başladı!"},
                {"rating": 5, "comment": "Saç derisini çok güzel ferahlatıyor."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785942087547.png"),
            "filename": "haircare_gliss_deep_repair.png",
            "title": "Schwarzkopf Gliss Serum Deep Repair Sıvı Keratin Saç Maskesi",
            "description": "Canlılığını yitirmiş, yoğun işlem görmüş ve aşırı yıpranmış saçlar için geliştirilmiş amino-protein serum ve sıvılaştırılmış keratin içerikli banyo sonrası bakım maskesi.",
            "price": Decimal("219.90"),
            "variants": [
                {"color": "Deep Repair Mask 300ml", "stock": 60}
            ],
            "reviews": [
                {"rating": 5, "comment": "Yıllardır vazgeçemediğim tek maske. Yıpranmış saçları anında canlandırıyor."},
                {"rating": 5, "comment": "Fiyatı çok uygun, etkisi ise paha biçilemez."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785942104618.png"),
            "filename": "haircare_elidor_repair_spray.png",
            "title": "Elidor Anında Onarıcı Sıvı Saç Kremi Spreyi",
            "description": "İşlem görmüş ve yıpranmış saçlar için özel Superblend formüllü, C vitamini ve hindistan cevizi yağı içeren durulanmayan kolay tarama spreyi.",
            "price": Decimal("169.90"),
            "variants": [
                {"color": "Anında Onarıcı 200ml", "stock": 70}
            ],
            "reviews": [
                {"rating": 5, "comment": "Banyodan sonra sıkıyorum, kıvırcık ve dolaşan saçlarımı şıp diye açıyor."},
                {"rating": 4, "comment": "Kokusu çok güzel ve saçta yağlı his bırakmıyor."}
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
            category=haircare_cat,
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
                sku=f"HAIR-{product.id}-{idx+1}"
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
        print(f"Added haircare product: {product.title} (Price: ₺{product.base_price})")

    print(f"Successfully added {added_count} real haircare products to Saç Bakım Ürünleri category.")

if __name__ == "__main__":
    add_haircare_products()
