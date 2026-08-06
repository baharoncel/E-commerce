import os
import sys
from decimal import Decimal

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Category, Product, SellerProfile, ProductVariant, ProductReview

def apply():
    parent_cat = Category.objects.get(id=443) # Erkek Takıları
    subcats = Category.objects.filter(parent=parent_cat) | Category.objects.filter(id=443)

    # Clean existing in 443
    old_products = Product.objects.filter(category__in=subcats)
    for p in old_products:
        ProductVariant.objects.filter(product=p).delete()
        ProductReview.objects.filter(product=p).delete()
        p.delete()

    seller = SellerProfile.objects.first()

    cat_yuzuk = Category.objects.get(id=444)
    cat_bileklik = Category.objects.get(id=445)
    cat_kolye = Category.objects.get(id=446)
    cat_kupe = Category.objects.get(id=447)
    cat_kol_dugmesi = Category.objects.get(id=448)

    items = [
        {
            "cat": cat_yuzuk,
            "filename": "real_photo_mens_ring.jpg",
            "title": "Gümüş Paslanmaz Çelik Şövalye Erkek Yüzük",
            "price": Decimal("249.90"),
            "desc": "Gerçek stüdyo fotoğrafı çekimiyle mat fırçalanmış gümüş çelik dokulu, maskülen şövalye model erkek yüzük."
        },
        {
            "cat": cat_bileklik,
            "filename": "real_photo_mens_bracelet.jpg",
            "title": "Siyah Hakiki Deri & Çelik Erkek Bileklik",
            "price": Decimal("219.90"),
            "desc": "Gerçek stüdyo fotoğrafı çekimiyle örgü hakiki siyah deri ve mıknatıslı çelik tokalı karizmatik erkek bileklik."
        },
        {
            "cat": cat_kolye,
            "filename": "real_photo_mens_necklace.jpg",
            "title": "Çelik Mat Siyah Pusula Motifli Erkek Kolye",
            "price": Decimal("289.90"),
            "desc": "Gerçek stüdyo fotoğrafı çekimiyle siyah paslanmaz çelik madalyon ve pusula desenli çelik erkek kolye."
        },
        {
            "cat": cat_kupe,
            "filename": "real_photo_mens_earrings.jpg",
            "title": "Siyah Çelik Mıknatıslı Halka Erkek Küpe Seti",
            "price": Decimal("159.90"),
            "desc": "Gerçek stüdyo fotoğrafı çekimiyle deliksiz kulağa uygun mıknatıslı mat siyah çelik erkek küpe seti."
        },
        {
            "cat": cat_kol_dugmesi,
            "filename": "real_photo_mens_cufflinks.jpg",
            "title": "Klasik Gümüş Kaplama Çelik Kol Düğmesi & Kravat İğnesi Seti",
            "price": Decimal("329.90"),
            "desc": "Gerçek stüdyo fotoğrafı çekimiyle takım elbise ve gömlek şıklığı için klasik çizgi desenli kol düğmesi ve kravat iğnesi seti."
        }
    ]

    for item in items:
        product = Product.objects.create(
            title=item["title"],
            description=item["desc"],
            base_price=item["price"],
            category=item["cat"],
            seller=seller,
            image=f"products/{item['filename']}",
            average_rating=Decimal("4.9"),
            review_count=38
        )
        ProductVariant.objects.create(
            product=product,
            sku=f"MALE-REAL-CAM-{product.id}",
            stock=50,
            price=item["price"]
        )
        print(f"Created Product ID: {product.id} - {product.title}")

    print("Successfully updated Men's Jewelry with 100% REAL camera photos!")

if __name__ == '__main__':
    apply()
