import os
import sys
import math
from decimal import Decimal
from PIL import Image, ImageDraw, ImageFilter

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Category, Product, SellerProfile, ProductVariant

def create_studio_base(w=800, h=800):
    img = Image.new('RGBA', (w, h), (252, 252, 254, 255))
    draw = ImageDraw.Draw(img)
    # Subtle soft studio radial glow in center
    for r in range(w//2, 0, -10):
        alpha = int(12 * (1 - r / (w//2)))
        draw.ellipse([w//2 - r, h//2 - r, w//2 + r, h//2 + r], fill=(240, 242, 248, alpha))
    return img

def render_pearl_comb():
    base = create_studio_base()
    # Shadow
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([240, 530, 560, 590], fill=(0, 0, 0, 45))
    sh = sh.filter(ImageFilter.GaussianBlur(25))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    # 1. Gold Comb Teeth
    for i in range(14):
        x = 265 + i * 20
        # Gradient gold teeth
        draw.rounded_rectangle([x, 380, x + 9, 530], radius=4, fill=(218, 175, 55, 255), outline=(170, 130, 25, 255), width=1)
        draw.line([x + 3, 385, x + 3, 525], fill=(255, 225, 120, 200), width=2) # Highlight

    # 2. Main Arch Bar
    draw.rounded_rectangle([240, 360, 560, 390], radius=10, fill=(230, 190, 60, 255), outline=(170, 130, 25, 255), width=2)

    # 3. Crystal Leaves & Vines
    vine_pts = [(260, 330), (310, 300), (370, 270), (430, 270), (490, 300), (540, 330)]
    for vx, vy in vine_pts:
        # Silver/Crystal Leaf
        draw.polygon([(vx, vy-18), (vx+16, vy), (vx, vy+18), (vx-16, vy)], fill=(235, 245, 255, 240), outline=(180, 210, 235, 255), width=1)
        draw.line([(vx, vy-18), (vx, vy+18)], fill=(255, 255, 255, 255), width=2)

    # 4. Realistic 3D Pearls
    pearl_data = [
        (260, 350, 20), (300, 330, 26), (350, 300, 32), (400, 280, 38),
        (450, 300, 32), (500, 330, 26), (540, 350, 20),
        (325, 355, 22), (375, 335, 28), (425, 335, 28), (475, 355, 22),
        (400, 230, 22), (350, 250, 18), (450, 250, 18)
    ]
    for cx, cy, pr in pearl_data:
        # Outer soft shade
        draw.ellipse([cx - pr, cy - pr, cx + pr, cy + pr], fill=(248, 246, 242, 255), outline=(215, 210, 200, 255), width=1)
        # 3D Gradient Shading (offset inner circle)
        draw.ellipse([cx - pr + 3, cy - pr + 3, cx + pr - 1, cy + pr - 1], fill=(255, 253, 250, 255))
        # Specular High-Light (Shine)
        draw.ellipse([cx - pr//2, cy - pr//2, cx - pr//4, cy - pr//4], fill=(255, 255, 255, 255))

    return base

def render_satin_scrunchies():
    base = create_studio_base()
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([160, 560, 640, 650], fill=(0, 0, 0, 40))
    sh = sh.filter(ImageFilter.GaussianBlur(30))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    # Scrunchie 1: Dusty Rose Silk Satin (Top Left)
    c1 = (235, 170, 185)
    c1_dark = (195, 120, 140)
    draw.ellipse([180, 220, 440, 480], fill=c1, outline=c1_dark, width=3)
    draw.ellipse([260, 300, 360, 400], fill=(252, 252, 254, 255), outline=c1_dark, width=2)
    # Satin Fold lines
    for angle in range(0, 360, 20):
        rad = math.radians(angle)
        x1 = 310 + int(70 * math.cos(rad))
        y1 = 350 + int(70 * math.sin(rad))
        x2 = 310 + int(125 * math.cos(rad))
        y2 = 350 + int(125 * math.sin(rad))
        draw.line([x1, y1, x2, y2], fill=(255, 215, 228, 220), width=5)

    # Scrunchie 2: Champagne Gold Silk Satin (Top Right)
    c2 = (230, 195, 135)
    c2_dark = (180, 145, 85)
    draw.ellipse([360, 180, 620, 440], fill=c2, outline=c2_dark, width=3)
    draw.ellipse([440, 260, 540, 360], fill=(252, 252, 254, 255), outline=c2_dark, width=2)
    for angle in range(0, 360, 20):
        rad = math.radians(angle)
        x1 = 490 + int(60 * math.cos(rad))
        y1 = 310 + int(60 * math.sin(rad))
        x2 = 490 + int(125 * math.cos(rad))
        y2 = 310 + int(125 * math.sin(rad))
        draw.line([x1, y1, x2, y2], fill=(255, 228, 175, 220), width=5)

    # Scrunchie 3: Emerald Sage Silk Satin (Bottom Center)
    c3 = (135, 175, 155)
    c3_dark = (95, 135, 115)
    draw.ellipse([270, 360, 530, 620], fill=c3, outline=c3_dark, width=3)
    draw.ellipse([350, 440, 450, 540], fill=(252, 252, 254, 255), outline=c3_dark, width=2)
    for angle in range(0, 360, 20):
        rad = math.radians(angle)
        x1 = 400 + int(65 * math.cos(rad))
        y1 = 490 + int(65 * math.sin(rad))
        x2 = 400 + int(125 * math.cos(rad))
        y2 = 490 + int(125 * math.sin(rad))
        draw.line([x1, y1, x2, y2], fill=(175, 215, 195, 220), width=5)

    return base

def render_metal_hairpin():
    base = create_studio_base()
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([180, 580, 620, 640], fill=(0, 0, 0, 35))
    sh = sh.filter(ImageFilter.GaussianBlur(25))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    # 18K Gold Polished Hair Stick (Diagonal)
    draw.polygon([(230, 580), (242, 592), (560, 230), (548, 218)], fill=(225, 185, 55, 255), outline=(170, 130, 25, 255))
    draw.line([(235, 583), (554, 224)], fill=(255, 230, 130, 220), width=3) # Specular highlight line

    # Top Geometric Oval Loop
    draw.ellipse([510, 150, 650, 290], fill=None, outline=(225, 185, 55, 255), width=14)
    draw.ellipse([515, 155, 645, 285], fill=None, outline=(170, 130, 25, 255), width=2)

    # Mother-of-Pearl Center Orb
    draw.ellipse([555, 195, 605, 245], fill=(245, 243, 238, 255), outline=(210, 205, 195, 255), width=1)
    draw.ellipse([565, 205, 580, 220], fill=(255, 255, 255, 255)) # Shine

    return base

def render_crystal_pins():
    base = create_studio_base()
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([180, 560, 620, 630], fill=(0, 0, 0, 35))
    sh = sh.filter(ImageFilter.GaussianBlur(25))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    # 4 Parallel Gold Bobby Clips with Diamonds/Pearls
    y_positions = [220, 320, 420, 520]
    for idx, y in enumerate(y_positions):
        # Clip Body
        draw.rounded_rectangle([200, y, 560, y + 16], radius=8, fill=(215, 175, 50, 255), outline=(160, 120, 20, 255), width=1)
        draw.line([210, y + 4, 550, y + 4], fill=(255, 230, 120, 200), width=2)

        # Embellishments
        for x in range(230, 540, 32):
            if idx == 0:
                # Brilliant-Cut Rhinestones (Diamond shape)
                draw.polygon([(x+8, y-6), (x+16, y+8), (x+8, y+22), (x, y+8)], fill=(230, 245, 255, 255), outline=(170, 205, 230, 255), width=1)
                draw.ellipse([x+5, y+3, x+11, y+9], fill=(255, 255, 255, 255))
            elif idx == 1:
                # Golden Star Clusters
                draw.rectangle([x+2, y-4, x+16, y+20], fill=(255, 245, 210, 255), outline=(210, 180, 120, 255), width=1)
                draw.line([x+9, y-4, x+9, y+20], fill=(255, 255, 255, 255), width=2)
            elif idx == 2:
                # Luminous Pearls
                draw.ellipse([x+1, y-5, x+17, y+21], fill=(248, 246, 240, 255), outline=(210, 205, 195, 255), width=1)
                draw.ellipse([x+4, y-2, x+9, y+3], fill=(255, 255, 255, 255))
            else:
                # Square Baguette Crystals
                draw.rounded_rectangle([x, y-4, x+20, y+20], radius=4, fill=(225, 242, 252, 255), outline=(160, 195, 215, 255), width=1)
                draw.line([x+4, y, x+16, y+16], fill=(255, 255, 255, 220), width=2)

    return base

def render_organza_bow():
    base = create_studio_base()
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([180, 560, 620, 640], fill=(0, 0, 0, 35))
    sh = sh.filter(ImageFilter.GaussianBlur(30))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    # Sheer Translucent Cream Organza Ribbon Bow
    cream_fill = (253, 248, 240, 235)
    cream_border = (225, 210, 190, 255)

    # Outer Left Wing
    draw.polygon([(400, 350), (180, 210), (140, 350), (210, 490)], fill=cream_fill, outline=cream_border, width=2)
    # Inner Left Fold
    draw.polygon([(400, 350), (220, 250), (190, 350), (240, 450)], fill=(245, 238, 228, 220))

    # Outer Right Wing
    draw.polygon([(400, 350), (620, 210), (660, 350), (590, 490)], fill=cream_fill, outline=cream_border, width=2)
    # Inner Right Fold
    draw.polygon([(400, 350), (580, 250), (610, 350), (560, 450)], fill=(245, 238, 228, 220))

    # Hanging Ribbon Tails
    draw.polygon([(365, 370), (240, 590), (310, 610), (390, 410)], fill=cream_fill, outline=cream_border, width=2)
    draw.polygon([(435, 370), (560, 590), (490, 610), (410, 410)], fill=cream_fill, outline=cream_border, width=2)

    # Gold Backing Clip Hint
    draw.rounded_rectangle([330, 335, 470, 365], radius=6, fill=(215, 175, 50, 255), outline=(160, 120, 20, 255))

    # Center Knot
    draw.rounded_rectangle([355, 310, 445, 390], radius=16, fill=(248, 240, 228, 255), outline=(215, 200, 180, 255), width=2)

    # Pearl Accent in Center Knot
    draw.ellipse([380, 335, 420, 375], fill=(255, 253, 248, 255), outline=(220, 212, 198, 255), width=1)
    draw.ellipse([388, 343, 398, 353], fill=(255, 255, 255, 255))

    return base

def main():
    media_dir = r"c:\Users\Bahar\Desktop\E-commerce\media\products"
    os.makedirs(media_dir, exist_ok=True)

    items = [
        ("hair_accessory_pearl_comb_studio.png", render_pearl_comb, "İnci ve Kristal Yaprak Detaylı Saç Tarak Tokası", "Özel gün, söz, nişan ve gelin kullanımı için tasarlanmış zarif incili saç tarağı tokası.", Decimal("289.90")),
        ("hair_accessory_satin_scrunchies_studio.png", render_satin_scrunchies, "3'lü %100 İpek Saten Lüks Scrunchie Saç Lastiği Seti", "Saçı kırmayan ve iz bırakmayan yumuşacık ipek saten 3'lü renkli saç Lastik tokası seti.", Decimal("149.90")),
        ("hair_accessory_metal_hairpin_studio.png", render_metal_hairpin, "Minimalist Altın Metal Topuz Saç Çubuğu", "Modern ve zarif tasarımıyla pratik topuz yapmayı sağlayan paslanmaz altın metal saç çubuğu.", Decimal("169.00")),
        ("hair_accessory_crystal_pins_studio.png", render_crystal_pins, "4'lü Kristal Taşlı Lüks Yan Saç Klipsi Seti", "Parıltılı zirkon taşlar ve geometrik desenli premium 4'lü tel saç klipsi seti.", Decimal("199.90")),
        ("hair_accessory_organza_bow_studio.png", render_organza_bow, "Krem Organze Tül Fiyonklu Romantik Saç Klipsi", "Hafif organze tül kumaştan büyük boy romantik Fransız stil fiyonk saç tokası.", Decimal("179.50")),
    ]

    seller = SellerProfile.objects.first()
    hair_cat = Category.objects.get(id=433)

    # Clean existing in 433
    existing = Product.objects.filter(category=hair_cat)
    for p in existing:
        ProductVariant.objects.filter(product=p).delete()
        p.delete()

    for filename, fn, title, desc, price in items:
        file_path = os.path.join(media_dir, filename)
        img = fn()
        img.save(file_path, format="PNG")
        print(f"Generated studio product image: {file_path}")

        product = Product.objects.create(
            title=title,
            description=desc,
            base_price=price,
            category=hair_cat,
            seller=seller,
            image=f"products/{filename}",
            average_rating=Decimal("4.9"),
            review_count=25
        )
        ProductVariant.objects.create(
            product=product,
            sku=f"HAIR-STUDIO-{product.id}",
            stock=50,
            price=price
        )
        print(f"Created Product ID: {product.id} - {title}")

    print("All 5 pure hair accessory studio products updated successfully!")

if __name__ == '__main__':
    main()
