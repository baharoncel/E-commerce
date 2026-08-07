import os
import sys
import django

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Product, ProductVariant, ProductReview, Category

print("Final site-wide deduplication: Ensuring 100% unique image for every product on the site...")

all_products = Product.objects.all().order_by('id')
seen_images = {}
deleted_count = 0

# Image remappings for specific items to make them unique
remap_rules = {
    'Minimalist Çelik Su Yolu Kadın Bileklik': 'products/womens_jewelry_bracelet.jpg',
    'Zirkon Taşlı Lüks Baget Kadın Altın Yüzük': 'products/womens_jewelry_ring.jpg',
    'Pırlanta Işıltılı Damla Sallantılı Kadın Küpe': 'products/womens_jewelry_earrings.jpg',
    'Altın Kaplama Deniz Kabuğu Kadın Halhal & Broş': 'products/womens_jewelry_anklet.jpg',
    'İncili ve Kristal Taşlı Lüks Gelin/Özel Gün Tacı': 'products/hair_accessory_pearl_comb_real.jpg',
    '%100 İpek Desenli Baş Örtüsü & Bandana': 'products/head_accessory_bandana.png',
    'Zarf Model Fermuarlı Kadın Deri Cüzdan': 'products/accessory_wallet_leather.png',
    'Bebekler İçin Hijyenik İzotonik Serum Fizyolojik 20\'li Ampul': 'products/baby_saline_ampoules.png',
    'Bebekler İçin %100 BPA İçermeyen Silikon Parmak Diş Fırçası': 'products/baby_finger_toothbrush.png',
    'Yenidoğan Güvenli Bebek Tırnak Makası & Yumuşak Tarak-Fırça Seti': 'products/baby_grooming_kit.png',
    'Yumuşak Silikon Uçlu Hijyenik Manuel Bebek Burun Aspiratörü': 'products/baby_nasal_dental_kit.png',
    'Organik Papatya & Badem Yağı İçeren Rahatlatıcı Bebek Masaj Yağı 200ml': 'products/baby_oil.jpg',
    'Yoğun Nemlendirici Bebek Yüz & Vücut Losyonu 200ml': 'products/baby_lotion.jpg',
    'Hassas Ciltler İçin Çinko Oksit Özlü Doğal Bebek Pişik Önleyici Krem 100ml': 'products/baby_cream.jpg',
}

for p in all_products:
    if p.title in remap_rules:
        p.image = remap_rules[p.title]
        p.save()

# De-duplicate any remaining exact duplicates
for p in list(Product.objects.all().order_by('-id')):
    if not p.image:
        continue
    img_name = p.image.name
    if img_name in seen_images:
        print(f"Deleting duplicate product ID {p.id}: {p.title} (Image: {img_name})")
        ProductVariant.objects.filter(product=p).delete()
        ProductReview.objects.filter(product=p).delete()
        p.delete()
        deleted_count += 1
    else:
        seen_images[img_name] = p.id

print(f"\nFinal Site-wide Deduplication Complete!")
print(f"Removed {deleted_count} duplicate items.")
print(f"Total remaining products on site: {Product.objects.count()} (All images 100% UNIQUE!)")
