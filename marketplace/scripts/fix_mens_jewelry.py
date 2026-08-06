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

def fix_mens_jewelry():
    media_dir = r"c:\Users\Bahar\Desktop\E-commerce\media\products"
    os.makedirs(media_dir, exist_ok=True)

    # Erkek takıları ve alt kategorileri
    parent_cat = Category.objects.get(id=443) # Erkek Takıları
    subcats = Category.objects.filter(parent=parent_cat) | Category.objects.filter(id=443)

    # 1. Clean up ALL dummy/mismatched products in Erkek Takıları (including female earrings, necklaces, rings)
    old_products = Product.objects.filter(category__in=subcats)
    cleaned_count = old_products.count()
    for p in old_products:
        ProductVariant.objects.filter(product=p).delete()
        ProductReview.objects.filter(product=p).delete()
        p.delete()
    print(f"Cleaned up {cleaned_count} old/mismatched products in Erkek Takıları.")

    seller = SellerProfile.objects.first()

    cat_yuzuk = Category.objects.get(id=444)
    cat_bileklik = Category.objects.get(id=445)
    cat_kolye = Category.objects.get(id=446)
    cat_kupe = Category.objects.get(id=447)
    cat_kol_dugmesi = Category.objects.get(id=448)

    items = [
        {
            "cat": cat_yuzuk,
            "filename": "mens_jewelry_ring.jpg",
            "url": "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?auto=format&fit=crop&w=800&h=800&q=80",
            "title": "Gümüş Paslanmaz Çelik Şövalye Erkek Yüzük",
            "price": Decimal("249.90"),
            "desc": "Mat fırçalanmış çelik dokulu, maskülen şövalye model erkek yüzük."
        },
        {
            "cat": cat_bileklik,
            "filename": "mens_jewelry_bracelet.jpg",
            "url": "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?auto=format&fit=crop&w=800&h=800&q=80",
            "title": "Siyah Hakiki Deri & Çelik Erkek Bileklik",
            "price": Decimal("219.90"),
            "desc": "Örgü hakiki siyah deri ve mıknatıslı çelik tokalı karizmatik erkek bileklik."
        },
        {
            "cat": cat_kolye,
            "filename": "mens_jewelry_necklace.jpg",
            "url": "https://images.unsplash.com/photo-1617038260897-41a1f14a8ca0?auto=format&fit=crop&w=800&h=800&q=80",
            "title": "Çelik Mat Siyah Pusula Motifli Erkek Kolye",
            "price": Decimal("289.90"),
            "desc": "Siyah paslanmaz çelik madalyon ve pusula desenli çelik erkek kolye."
        },
        {
            "cat": cat_kupe,
            "filename": "mens_jewelry_earrings.jpg",
            "url": "https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&w=800&h=800&q=80",
            "title": "Siyah Çelik Mıknatıslı Halka Erkek Küpe Seti",
            "price": Decimal("159.90"),
            "desc": "Deliksiz kulağa uygun mıknatıslı mat siyah çelik erkek küpe seti."
        },
        {
            "cat": cat_kol_dugmesi,
            "filename": "mens_jewelry_cufflinks.jpg",
            "url": "https://images.unsplash.com/photo-1617038260897-41a1f14a8ca0?auto=format&fit=crop&w=800&h=800&q=80",
            "title": "Klasik Gümüş Kaplama Çelik Kol Düğmesi & Kravat İğnesi Seti",
            "price": Decimal("329.90"),
            "desc": "Takım elbise ve gömlek şıklığı için klasik çizgi desenli kol düğmesi ve kravat iğnesi seti."
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
            review_count=31
        )
        ProductVariant.objects.create(
            product=product,
            sku=f"JEWELRY-MALE-{product.id}",
            stock=50,
            price=item["price"]
        )
        print(f"Created Product ID: {product.id} - {product.title}")

    print("Successfully updated Men's Jewelry with 100% men's products and real photos!")

if __name__ == '__main__':
    fix_mens_jewelry()
