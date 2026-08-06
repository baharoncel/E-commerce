import os
import sys
import urllib.request
from decimal import Decimal

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Category, Product, SellerProfile, ProductVariant, ProductReview

def fix_jewelry():
    media_dir = r"c:\Users\Bahar\Desktop\E-commerce\media\products"
    os.makedirs(media_dir, exist_ok=True)

    # Kadın takıları ve alt kategorileri
    parent_cat = Category.objects.get(id=437) # Kadın Takıları
    subcats = Category.objects.filter(parent=parent_cat) | Category.objects.filter(id=437)

    # 1. Clean up ALL dummy/mismatched products in Kadın Takıları (including cufflinks & men rings)
    old_products = Product.objects.filter(category__in=subcats)
    for p in old_products:
        ProductVariant.objects.filter(product=p).delete()
        ProductReview.objects.filter(product=p).delete()
        p.delete()
    print(f"Cleaned up {old_products.count()} old/mismatched products in Kadın Takıları.")

    seller = SellerProfile.objects.first()

    cat_kolye = Category.objects.get(id=438)
    cat_yuzuk = Category.objects.get(id=439)
    cat_kupe = Category.objects.get(id=440)
    cat_bileklik = Category.objects.get(id=441)
    cat_halhal = Category.objects.get(id=442)

    items = [
        {
            "cat": cat_kolye,
            "filename": "womens_jewelry_necklace.jpg",
            "url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&h=800&q=80",
            "title": "Zarif İncili Altın Zincir Kadın Kolye",
            "price": Decimal("349.90"),
            "desc": "Zarafet dolu doğal inci ucu ve ince altın kaplama zincirli kadın kolye."
        },
        {
            "cat": cat_yuzuk,
            "filename": "womens_jewelry_ring.jpg",
            "url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=800&h=800&q=80",
            "title": "Zirkon Taşlı Lüks Baget Kadın Altın Yüzük",
            "price": Decimal("499.90"),
            "desc": "Parıltılı baget kesim zirkon taşlı altın kaplama zarif kadın yüzük."
        },
        {
            "cat": cat_kupe,
            "filename": "womens_jewelry_earrings.jpg",
            "url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=800&h=800&q=80",
            "title": "Pırlanta Işıltılı Damla Sallantılı Kadın Küpe",
            "price": Decimal("299.90"),
            "desc": "Özel davetler ve günlük şıklık için damla kesim pırlanta efektli sallantılı kadın küpe."
        },
        {
            "cat": cat_bileklik,
            "filename": "womens_jewelry_bracelet.jpg",
            "url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=800&h=800&q=80",
            "title": "Minimalist Çelik Su Yolu Kadın Bileklik",
            "price": Decimal("279.90"),
            "desc": "Işıltılı zirkon taş sırası ve paslanmaz çelik zinciri ile modern kadın bileklik."
        },
        {
            "cat": cat_halhal,
            "filename": "womens_jewelry_anklet.jpg",
            "url": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=800&h=800&q=80",
            "title": "Altın Kaplama Deniz Kabuğu Kadın Halhal & Broş",
            "price": Decimal("189.90"),
            "desc": "Yaz aylarında zarif görünüm sunan deniz kabuğu ve sallantılı inci detaylı kadın halhal."
        }
    ]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for item in items:
        file_path = os.path.join(media_dir, item["filename"])
        try:
            req = urllib.request.Request(item["url"], headers=headers)
            with urllib.request.urlopen(req) as resp, open(file_path, 'wb') as out_file:
                out_file.write(resp.read())
            print(f"Downloaded photo: {item['filename']}")
        except Exception as e:
            print(f"Failed to download {item['filename']}: {e}")

        product = Product.objects.create(
            title=item["title"],
            description=item["desc"],
            base_price=item["price"],
            category=item["cat"],
            seller=seller,
            image=f"products/{item['filename']}",
            average_rating=Decimal("4.9"),
            review_count=28
        )
        ProductVariant.objects.create(
            product=product,
            sku=f"JEWELRY-FEMALE-{product.id}",
            stock=50,
            price=item["price"]
        )
        print(f"Created Product ID: {product.id} - {product.title}")

    print("Successfully updated Women's Jewelry with 100% women's products and real photos!")

if __name__ == '__main__':
    fix_jewelry()
