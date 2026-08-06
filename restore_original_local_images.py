import os
import sys
import django

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Product

print("Restoring exact local media image paths for all products...")

# Mapping keywords to exact local media product filenames
local_images_map = {
    'saç': 'products/shampoo.png',
    'şampuan': 'products/shampoo.png',
    'elidor': 'products/shampoo.png',
    'schwarzkopf': 'products/shampoo.png',
    'pantene': 'products/shampoo.png',
    'urban': 'products/shampoo.png',

    'çinko': 'products/toothpaste.png',
    'ağız': 'products/toothpaste.png',
    'diş': 'products/toothpaste.png',
    'macun': 'products/toothpaste.png',

    'cilt': 'products/skincare.png',
    'krem': 'products/skincare.png',
    'güneş': 'products/skincare_caudalie_sun_set.png',
    'serum': 'products/skincare_purest_serum_set.png',
    'caudalie': 'products/skincare_caudalie_sun_set.png',
    'yves': 'products/skincare_yves_rocher_pure_menthe.png',

    'parfüm': 'products/perfume.png',
    'deodorant': 'products/perfume.png',
    'loris': 'products/perfume.png',
    'chanel': 'products/perfume.png',
    'bleu': 'products/perfume.png',
    'rabanne': 'products/perfume.png',

    'ceket': 'products/coat_black_puffer.png',
    'deri': 'products/coat_black_puffer.png',
    'elbise': 'products/dress_emerald_satin.png',
    'etek': 'products/skirt_leopard.png',
    'tişört': 'products/tshirt_blue_plain.png',
    'gömlek': 'products/shirt_white_close_real.png',
    'bluz': 'products/blouse_turquoise.png',
    'pantolon': 'products/pants_black_jean_v2.png',
    'jean': 'products/jean_mom_fit_light.png',
    'kot': 'products/jean_mom_fit_light.png',

    'saat': 'products/accessory_watch_gold.png',
    'çanta': 'products/bag_shoulder_beige_set.png',
    'gözlük': 'products/accessory_sunglasses_aviator.png',
    'laptop': 'products/test_product.jpg',
    'probook': 'products/test_product.jpg',
    'kulaklık': 'products/headphones.jpg',

    'bileklik': 'products/timsah_logolu_celik_baklali_erkek_bileklik.png',
    'kolye': 'products/necklace.png',
    'bebek': 'products/baby_body.png',
}

count = 0
for p in Product.objects.all():
    title_lower = p.title.lower()
    matched = False
    for kw, img_path in local_images_map.items():
        if kw in title_lower:
            p.image = img_path
            p.save()
            matched = True
            count += 1
            break
    if not matched:
        if p.category:
            cat_name = p.category.name.lower()
            if 'kozmetik' in cat_name or 'bakım' in cat_name:
                p.image = 'products/skincare.png'
            elif 'giyim' in cat_name or 'moda' in cat_name:
                p.image = 'products/tshirt_blue_plain.png'
            elif 'elektronik' in cat_name:
                p.image = 'products/headphones.jpg'
            elif 'aksesuar' in cat_name or 'saat' in cat_name:
                p.image = 'products/accessory_watch_gold.png'
            else:
                p.image = 'products/tshirt_blue_plain.png'
        else:
            p.image = 'products/tshirt_blue_plain.png'
        p.save()
        count += 1

print(f"Restored exact local media image paths for {count} products!")
