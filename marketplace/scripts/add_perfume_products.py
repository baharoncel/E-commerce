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

def add_perfume_products():
    brain_dir = r"C:\Users\Bahar\.gemini\antigravity-ide\brain\54dc9cd8-2d3f-44f1-a2d9-408fd3f691fd"
    media_products_dir = r"c:\Users\Bahar\Desktop\E-commerce\media\products"
    os.makedirs(media_products_dir, exist_ok=True)

    perfume_cat = Category.objects.get(id=455)
    seller = SellerProfile.objects.first()
    customers = list(CustomUser.objects.all()[:10])

    # 1. Clean up old dummy products in Parfüm ve Deodorantlar category
    old_products = Product.objects.filter(category=perfume_cat)
    count = old_products.count()
    for p in old_products:
        ProductVariant.objects.filter(product=p).delete()
        ProductReview.objects.filter(product=p).delete()
        p.delete()
    print(f"Cleaned up {count} old dummy products in Parfüm ve Deodorantlar category.")

    items = [
        {
            "src": os.path.join(brain_dir, "media__1785942536486.png"),
            "filename": "perfume_rabanne_1million_deo.png",
            "title": "Rabanne 1 Million Lüks Erkek Deodorant Spray (150 ml)",
            "description": "Paco Rabanne 1 Million ikonik kokusunun ferahlatıcı erkek deodorant spray versiyonu. Altın rengi şık silindir ambalajı, baharatlı ve tatlı odunsu notaları ile gün boyu kesintisiz tazelik sunar.",
            "price": Decimal("489.90"),
            "variants": [
                {"color": "1 Million Gold 150ml", "stock": 40}
            ],
            "reviews": [
                {"rating": 5, "comment": "Kokusu tıpkı 1 Million parfümü gibi yoğun ve çok kalıcı. Gün boyu ter kokusunu önlüyor."},
                {"rating": 5, "comment": "Tasarımı da kokusu da harika."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785942554368.png"),
            "filename": "perfume_bleu_de_chanel_deo.png",
            "title": "Bleu de Chanel Paris Lüks Erkek Deodorant Spray (150 ml)",
            "description": "Chanel'in zamansız ve karizmatik Bleu de Chanel erkek kokusu. Narenciye, nane ve odunsu akorların birleşimi ile cilde anında ferahlık ve zarafet katar.",
            "price": Decimal("749.90"),
            "variants": [
                {"color": "Bleu De Chanel 150ml", "stock": 30}
            ],
            "reviews": [
                {"rating": 5, "comment": "Aşırı kaliteli bir koku. Parfüm kullanmış gibi hissettiriyor."},
                {"rating": 5, "comment": "Chanel kalitesi kendini her an belli ediyor."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785942607587.png"),
            "filename": "perfume_gabrielle_chanel_deo.png",
            "title": "Gabrielle Chanel Paris Lüks Kadın Deodorant Spray (150 ml)",
            "description": "Yasemin, ylang-ylang, portakal çiçeği ve sümbülteberin mükemmel uyumuyla tasarlanan Gabrielle Chanel kadın deodorant spray. Şık krem & altın ambalajı ile feminen ve büyüleyici bir koku.",
            "price": Decimal("789.90"),
            "variants": [
                {"color": "Gabrielle Gold 150ml", "stock": 25}
            ],
            "reviews": [
                {"rating": 5, "comment": "Çiçeksi ve çok asil bir koku. Yaz kış severek kullanıyorum."},
                {"rating": 5, "comment": "Kalıcılığı bir deodorant için inanılmaz yüksek."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785942675121.png"),
            "filename": "perfume_loris_k120_set.png",
            "title": "Loris K-120 Frequence Kadın Parfüm & Deodorant İkili Set",
            "description": "Çiçek bahçelerinden ilham alan Loris K-120 Frequence Collection 50 ml EDP kadın parfümü ve aynı notalara sahip 150 ml vücut & deodorant spray ikili hediye seti.",
            "price": Decimal("349.90"),
            "variants": [
                {"color": "K-120 Floral Set", "stock": 60}
            ],
            "reviews": [
                {"rating": 5, "comment": "Kutusu ve parfüm-deodorant uyumu çok güzel. Fiyatı da son derece uygun."},
                {"rating": 4, "comment": "Çevremdekiler sürekli hangi parfümü sıktığımı soruyor."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785942695428.png"),
            "filename": "perfume_rbl_black_set.png",
            "title": "Rbl Black Karizmatik Erkek Parfüm & Deo Spray Seti",
            "description": "Siyah cam şişede karizmatik odunsu erkek parfümü ve tamamlayıcı 150 ml Rbl Black Deo Spray ikili avantaj seti. Günlük kullanım için maskülen ve çekici koku seçeneği.",
            "price": Decimal("299.90"),
            "variants": [
                {"color": "Rbl Black Duo", "stock": 50}
            ],
            "reviews": [
                {"rating": 5, "comment": "Erkek arkadaşıma hediye aldım, kokusuna bayıldık. Çok karizmatik bir koku."},
                {"rating": 5, "comment": "Fiyat performans açısından 10/10 bir set."}
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
            category=perfume_cat,
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
                sku=f"PERF-{product.id}-{idx+1}"
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
        print(f"Added perfume product: {product.title} (Price: ₺{product.base_price})")

    print(f"Successfully added {added_count} real perfume products to Parfüm ve Deodorantlar category.")

if __name__ == "__main__":
    add_perfume_products()
