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

def add_skincare_products():
    brain_dir = r"C:\Users\Bahar\.gemini\antigravity-ide\brain\54dc9cd8-2d3f-44f1-a2d9-408fd3f691fd"
    media_products_dir = r"c:\Users\Bahar\Desktop\E-commerce\media\products"
    os.makedirs(media_products_dir, exist_ok=True)

    skincare_cat = Category.objects.get(id=452)
    seller = SellerProfile.objects.first()
    customers = list(CustomUser.objects.all()[:10])

    # 1. Clean up old dummy products in Cilt Bakım Ürünleri category
    old_products = Product.objects.filter(category=skincare_cat)
    count = old_products.count()
    for p in old_products:
        ProductVariant.objects.filter(product=p).delete()
        ProductReview.objects.filter(product=p).delete()
        p.delete()
    print(f"Cleaned up {count} old dummy products in Cilt Bakım Ürünleri category.")

    items = [
        {
            "src": os.path.join(brain_dir, "media__1785941348114.png"),
            "filename": "skincare_dermocosmetic_set.png",
            "title": "Yüz Bakımı Dermokozmetik Komple Bakım Seti",
            "description": "Bioderma, Avène, The Purest Solutions ve Nuxe ikonik ürünlerinden oluşan 7'li dermokozmetik yüz bakım seti. Yüz temizleme yağı, güneş koruyucu, nemlendirici krem ve besleyici yüz yağı ile cildinize eksiksiz bakım sağlar.",
            "price": Decimal("849.90"),
            "variants": [
                {"color": "Hassas Ciltler Seti", "stock": 40},
                {"color": "Karma & Yağlı Ciltler Seti", "stock": 25}
            ],
            "reviews": [
                {"rating": 5, "comment": "Tüm dermokozmetik favorilerim tek bir palette/sette toplanmış. Harika!"},
                {"rating": 5, "comment": "Bioderma yağ temizleyici ve The Purest serum harika uyum sağladı."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785941425490.png"),
            "filename": "skincare_purest_serum_set.png",
            "title": "The Purest Solutions Yoğun Nem & Leke Karşıtı Serum Seti",
            "description": "AHA/BHA peeling serumu, Niacinamide tonik ve Hyaluronic Acid nem serumundan oluşan 6 parçalı yoğun cilt bakım kompleksi. Gözenekleri temizler, cilt tonunu eşitler ve 24 saat nem sunar.",
            "price": Decimal("499.90"),
            "variants": [
                {"color": "Leke & Gözenek Karşıtı", "stock": 50},
                {"color": "Yoğun Nem & Onarım", "stock": 35}
            ],
            "reviews": [
                {"rating": 5, "comment": "Kırmızı peeling serumu ilk kullanımdan itibaren etkisini gösterdi. Çok memnun kaldım."},
                {"rating": 4, "comment": "Cildim ışıl ışıl oldu, gözeneklerim bariz küçüldü."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785941440888.png"),
            "filename": "skincare_prima_organic_set.png",
            "title": "Prima Botanical Organik Cilt Yenileyici Gece & Gündüz Seti",
            "description": "Doğal bitkisel özler, retinol alternatifleri ve C vitamini içeren lüks 7 parçalı organik cilt bakım seti. Temizleyici sabun, gündüz nemlendiricisi, gece balamı ve göz çevresi serumu barındırır.",
            "price": Decimal("679.90"),
            "variants": [
                {"color": "Botanical Glow", "stock": 30}
            ],
            "reviews": [
                {"rating": 5, "comment": "Dokusu ve kokusu inanılmaz dinlendirici. Gece kremi cildimi bebek gibi yaptı."},
                {"rating": 5, "comment": "Doğal içerikli olması büyük avantaj. Hassas cildime çok iyi geldi."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785941462892.png"),
            "filename": "skincare_caudalie_sun_set.png",
            "title": "Caudalie Paris SPF 50+ Yüksek Korumalı Güneş Bakım Seti",
            "description": "Fransız Caudalie markasının leke karşıtı ve anti-aging etkili SPF 50+ güneş koruyucu yüz kremi, vücut spreyi, koruyucu stick ve güneş sonrası nemlendirici yağından oluşan 5'li lüks koruma serisi.",
            "price": Decimal("789.90"),
            "variants": [
                {"color": "Invisible Shield 50+", "stock": 45}
            ],
            "reviews": [
                {"rating": 5, "comment": "Güneş kremi hiç beyazlık bırakmıyor, koruması mükemmel. Yazın vazgeçilmezi!"},
                {"rating": 5, "comment": "Sprey formu çok pratik, kokusu harika."}
            ]
        },
        {
            "src": os.path.join(brain_dir, "media__1785941493292.png"),
            "filename": "skincare_yves_rocher_pure_menthe.png",
            "title": "Yves Rocher Pure Menthe Arındırıcı & Gözenek Sıkılaştırıcı Set",
            "description": "Organik nane özlü yüz yıkama jeli, matlaştırıcı tonik, siyah nokta karşıtı peeling ve matlaştırıcı nemlendirici kremden oluşan 4'lü arındırıcı yüz bakım serisi.",
            "price": Decimal("429.90"),
            "variants": [
                {"color": "Pure Menthe Organic", "stock": 55}
            ],
            "reviews": [
                {"rating": 5, "comment": "Nane ferahlığı harika! Yağlanmayı anında kontrol altına alıyor."},
                {"rating": 4, "comment": "Yüz yıkama jeli gözenekleri derinlemesine temizliyor, tavsiye ederim."}
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
            category=skincare_cat,
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
                sku=f"SKIN-{product.id}-{idx+1}"
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
        print(f"Added skincare product: {product.title} (Price: ₺{product.base_price})")

    print(f"Successfully added {added_count} real skincare products to Cilt Bakım Ürünleri category.")

if __name__ == "__main__":
    add_skincare_products()
