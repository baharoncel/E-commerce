import os
import sys
import shutil
from decimal import Decimal
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Category, Product, SellerProfile, ProductVariant, ProductReview

def create_studio_background(width=800, height=800):
    img = Image.new('RGBA', (width, height), (250, 250, 252, 255))
    draw = ImageDraw.Draw(img)
    # Subtle studio vignette / radial gradient
    for r in range(width, 0, -10):
        alpha = int(15 * (1 - r / width))
        draw.ellipse([width//2 - r, height//2 - r, width//2 + r, height//2 + r], outline=None, fill=(235, 237, 242, alpha))
    return img

def add_shadow(img, bbox, blur_radius=25, offset=(0, 20)):
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    x0, y0, x1, y1 = bbox
    sdraw.ellipse([x0 + offset[0], y0 + offset[1], x1 + offset[0], y1 + offset[1]], fill=(0, 0, 0, 40))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
    return Image.alpha_composite(shadow, img)

def generate_pearl_comb():
    base = create_studio_background()
    # Draw soft shadow underneath
    shadow = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.ellipse([220, 520, 580, 600], fill=(0, 0, 0, 35))
    shadow = shadow.filter(ImageFilter.GaussianBlur(30))
    base = Image.alpha_composite(base, shadow)

    draw = ImageDraw.Draw(base)
    # Draw metal comb teeth (gold/silver)
    for i in range(12):
        x = 280 + i * 22
        draw.rounded_rectangle([x, 400, x + 8, 540], radius=4, fill=(212, 175, 55, 255), outline=(180, 140, 30, 255))

    # Comb base bar
    draw.rounded_rectangle([260, 380, 540, 410], radius=8, fill=(230, 195, 75, 255), outline=(190, 150, 40, 255))

    # Pearls cluster
    pearl_centers = [
        (280, 350, 22), (320, 330, 28), (370, 310, 35), (430, 320, 30), (480, 340, 26), (520, 360, 20),
        (300, 370, 18), (350, 350, 24), (400, 340, 26), (450, 350, 22), (500, 370, 18),
        (370, 275, 20), (420, 285, 18)
    ]
    for cx, cy, pr in pearl_centers:
        # Pearl body (shimmer gradient)
        draw.ellipse([cx - pr, cy - pr, cx + pr, cy + pr], fill=(245, 245, 240, 255), outline=(210, 210, 200, 255), width=1)
        # Highlight
        draw.ellipse([cx - pr//2, cy - pr//2, cx - pr//4, cy - pr//4], fill=(255, 255, 255, 230))

    # Crystal leaves branches
    leaf_coords = [(330, 300), (360, 280), (410, 270), (450, 290), (470, 310)]
    for lx, ly in leaf_coords:
        draw.polygon([(lx, ly-15), (lx+15, ly), (lx, ly+15), (lx-15, ly)], fill=(220, 235, 245, 220), outline=(180, 200, 220, 255))

    return base

def generate_satin_scrunchies():
    base = create_studio_background()
    shadow = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.ellipse([180, 560, 620, 640], fill=(0, 0, 0, 30))
    shadow = shadow.filter(ImageFilter.GaussianBlur(35))
    base = Image.alpha_composite(base, shadow)

    draw = ImageDraw.Draw(base)

    # Scrunchie 1: Soft Pink / Rose Satin (Left)
    c1 = (245, 180, 195)
    draw.ellipse([180, 260, 420, 500], fill=c1, outline=(220, 150, 170), width=3)
    draw.ellipse([250, 330, 350, 430], fill=(250, 250, 252, 255), outline=(220, 150, 170), width=2)
    # Folds
    for a in range(0, 360, 30):
        import math
        rad = math.radians(a)
        x1 = 300 + int(70 * math.cos(rad))
        y1 = 380 + int(70 * math.sin(rad))
        x2 = 300 + int(115 * math.cos(rad))
        y2 = 380 + int(115 * math.sin(rad))
        draw.line([x1, y1, x2, y2], fill=(255, 210, 225, 200), width=4)

    # Scrunchie 2: Champagne Gold Satin (Center Stacked)
    c2 = (235, 205, 145)
    draw.ellipse([320, 200, 580, 460], fill=c2, outline=(205, 175, 115), width=3)
    draw.ellipse([390, 270, 510, 390], fill=(250, 250, 252, 255), outline=(205, 175, 115), width=2)
    for a in range(0, 360, 30):
        import math
        rad = math.radians(a)
        x1 = 450 + int(60 * math.cos(rad))
        y1 = 330 + int(60 * math.sin(rad))
        x2 = 450 + int(120 * math.cos(rad))
        y2 = 330 + int(120 * math.sin(rad))
        draw.line([x1, y1, x2, y2], fill=(255, 230, 180, 200), width=4)

    # Scrunchie 3: Emerald Sage Green (Bottom Center)
    c3 = (150, 185, 165)
    draw.ellipse([250, 380, 520, 620], fill=c3, outline=(120, 155, 135), width=3)
    draw.ellipse([320, 440, 450, 560], fill=(250, 250, 252, 255), outline=(120, 155, 135), width=2)

    return base

def generate_metal_hairpin():
    base = create_studio_background()
    shadow = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.ellipse([200, 580, 600, 640], fill=(0, 0, 0, 30))
    shadow = shadow.filter(ImageFilter.GaussianBlur(25))
    base = Image.alpha_composite(base, shadow)

    draw = ImageDraw.Draw(base)
    # Long Gold Hair Stick / Pin
    draw.polygon([(240, 580), (250, 590), (560, 220), (545, 210)], fill=(225, 185, 65, 255), outline=(180, 140, 30, 255))
    # Top Decorative Circle Loop
    draw.ellipse([510, 160, 630, 280], fill=None, outline=(225, 185, 65, 255), width=12)
    # Inner Pearl accent
    draw.ellipse([550, 200, 590, 240], fill=(245, 245, 240, 255), outline=(210, 210, 200, 255), width=1)
    draw.ellipse([558, 208, 568, 218], fill=(255, 255, 255, 230))

    return base

def generate_crystal_pins():
    base = create_studio_background()
    shadow = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.ellipse([200, 550, 600, 620], fill=(0, 0, 0, 25))
    shadow = shadow.filter(ImageFilter.GaussianBlur(25))
    base = Image.alpha_composite(base, shadow)

    draw = ImageDraw.Draw(base)

    # 4 Parallel Bobby Pins with Crystal tops
    ys = [240, 330, 420, 510]
    for idx, y in enumerate(ys):
        # Metal Pin body
        draw.rounded_rectangle([220, y, 540, y + 14], radius=7, fill=(210, 170, 50, 255), outline=(170, 130, 30, 255))
        # Decorative crystal row on top
        for cx in range(240, 520, 30):
            if idx == 0:
                # Round crystals
                draw.ellipse([cx, y - 6, cx + 18, y + 20], fill=(230, 245, 255, 255), outline=(180, 210, 230, 255), width=1)
            elif idx == 1:
                # Star shape crystals
                draw.rectangle([cx + 2, y - 4, cx + 16, y + 18], fill=(255, 240, 220, 255), outline=(220, 190, 150, 255))
            elif idx == 2:
                # Pearl dots
                draw.ellipse([cx + 2, y - 4, cx + 16, y + 18], fill=(245, 245, 240, 255), outline=(200, 200, 190, 255))
            else:
                # Rectangle baguette crystals
                draw.rounded_rectangle([cx, y - 5, cx + 22, y + 19], radius=3, fill=(220, 240, 250, 255), outline=(160, 190, 210, 255))

    return base

def generate_organza_bow():
    base = create_studio_background()
    shadow = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.ellipse([180, 550, 620, 630], fill=(0, 0, 0, 30))
    shadow = shadow.filter(ImageFilter.GaussianBlur(30))
    base = Image.alpha_composite(base, shadow)

    draw = ImageDraw.Draw(base)

    # Large Romantic Organza Cream Bow
    bow_color = (252, 246, 238, 230) # semi-translucent cream organza
    border_color = (230, 215, 195, 255)

    # Left Loop
    draw.polygon([(400, 360), (200, 240), (160, 360), (220, 480)], fill=bow_color, outline=border_color)
    # Right Loop
    draw.polygon([(400, 360), (600, 240), (640, 360), (580, 480)], fill=bow_color, outline=border_color)

    # Ribbon Tails hanging down
    draw.polygon([(370, 380), (260, 580), (320, 600), (390, 420)], fill=bow_color, outline=border_color)
    draw.polygon([(430, 380), (540, 580), (480, 600), (410, 420)], fill=bow_color, outline=border_color)

    # Center Knot
    draw.rounded_rectangle([360, 320, 440, 400], radius=15, fill=(245, 235, 220, 255), outline=(210, 195, 175, 255), width=2)
    # Pearl accent in knot
    draw.ellipse([385, 345, 415, 375], fill=(255, 255, 250, 255), outline=(220, 210, 195, 255))

    return base

def main():
    media_dir = r"c:\Users\Bahar\Desktop\E-commerce\media\products"
    os.makedirs(media_dir, exist_ok=True)

    generators = [
        ("hair_accessory_pearl_comb.png", generate_pearl_comb, "İnci ve Kristal Yaprak Detaylı Saç Tarak Tokası", "Özel gün, söz, nişan ve gelin kullanımı için tasarlanmış zarif incili saç tarağı tokası.", Decimal("289.90")),
        ("hair_accessory_satin_scrunchies.png", generate_satin_scrunchies, "3'lü %100 İpek Saten Lüks Scrunchie Saç Lastiği Seti", "Saçı kırmayan ve iz bırakmayan yumuşacık ipek saten 3'lü renkli saç Lastik tokası seti.", Decimal("149.90")),
        ("hair_accessory_metal_hairpin.png", generate_metal_hairpin, "Minimalist Altın Metal Topuz Saç Çubuğu", "Modern ve zarif tasarımıyla pratik topuz yapmayı sağlayan paslanmaz altın metal saç çubuğu.", Decimal("169.00")),
        ("hair_accessory_crystal_pins.png", generate_crystal_pins, "4'lü Kristal Taşlı Lüks Yan Saç Klipsi Seti", "Parıltılı zirkon taşlar ve geometrik desenli premium 4'lü tel saç klipsi seti.", Decimal("199.90")),
        ("hair_accessory_organza_bow.png", generate_organza_bow, "Krem Organze Tül Fiyonklu Romantik Saç Klipsi", "Hafif organze tül kumaştan büyük boy romantik Fransız stil fiyonk saç tokası.", Decimal("179.50")),
    ]

    seller = SellerProfile.objects.first()
    hair_cat, _ = Category.objects.get_or_create(id=433, defaults={"name": "Saç Aksesuarları", "slug": "sac-aksesuarlari"})

    # Clean existing in Category 433
    existing = Product.objects.filter(category=hair_cat)
    for p in existing:
        ProductVariant.objects.filter(product=p).delete()
        p.delete()

    for filename, gen_fn, title, desc, price in generators:
        img_path = os.path.join(media_dir, filename)
        img = gen_fn()
        img.save(img_path, format="PNG")
        print(f"Generated image: {img_path}")

        product = Product.objects.create(
            title=title,
            description=desc,
            base_price=price,
            category=hair_cat,
            seller=seller,
            image=f"products/{filename}",
            average_rating=Decimal("4.9"),
            review_count=18
        )
        ProductVariant.objects.create(
            product=product,
            sku=f"HAIR-{product.id}-DEF",
            stock=45,
            price=price
        )
        print(f"Created Product ID: {product.id} - {title}")

    print("All 5 hair accessory products generated and saved successfully!")

if __name__ == '__main__':
    main()
