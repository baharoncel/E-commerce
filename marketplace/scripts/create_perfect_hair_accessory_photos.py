import os
import math
from PIL import Image, ImageDraw, ImageFilter

def create_studio_bg(w=800, h=800):
    img = Image.new('RGBA', (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Soft subtle vignette studio lighting
    for r in range(w//2, 0, -8):
        alpha = int(10 * (1 - r / (w//2)))
        draw.ellipse([w//2 - r, h//2 - r, w//2 + r, h//2 + r], fill=(245, 247, 250, alpha))
    return img

def render_pearl_comb():
    base = create_studio_bg()
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([230, 520, 570, 580], fill=(0, 0, 0, 50))
    sh = sh.filter(ImageFilter.GaussianBlur(25))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    # Gold Comb Teeth
    for i in range(14):
        x = 260 + i * 21
        draw.rounded_rectangle([x, 370, x + 10, 520], radius=5, fill=(218, 175, 55, 255), outline=(160, 125, 20, 255), width=1)
        draw.line([x + 3, 375, x + 3, 515], fill=(255, 230, 130, 220), width=2)

    # Comb Spine Bar
    draw.rounded_rectangle([235, 350, 565, 382], radius=10, fill=(230, 190, 60, 255), outline=(160, 125, 20, 255), width=2)

    # Crystal Vines
    vines = [(260, 320), (310, 290), (370, 265), (430, 265), (490, 290), (540, 320)]
    for vx, vy in vines:
        draw.polygon([(vx, vy-18), (vx+16, vy), (vx, vy+18), (vx-16, vy)], fill=(235, 245, 255, 240), outline=(170, 205, 230, 255), width=1)
        draw.line([(vx, vy-18), (vx, vy+18)], fill=(255, 255, 255, 255), width=2)

    # 3D Pearls
    pearls = [
        (260, 340, 22), (300, 315, 28), (350, 290, 34), (400, 270, 40),
        (450, 290, 34), (500, 315, 28), (540, 340, 22),
        (325, 345, 24), (375, 325, 30), (425, 325, 30), (475, 345, 24),
        (400, 220, 24), (345, 240, 20), (455, 240, 20)
    ]
    for cx, cy, pr in pearls:
        draw.ellipse([cx - pr, cy - pr, cx + pr, cy + pr], fill=(250, 248, 244, 255), outline=(215, 210, 200, 255), width=1)
        draw.ellipse([cx - pr + 3, cy - pr + 3, cx + pr - 1, cy + pr - 1], fill=(255, 254, 252, 255))
        draw.ellipse([cx - pr//2, cy - pr//2, cx - pr//4, cy - pr//4], fill=(255, 255, 255, 255))

    return base

def render_satin_scrunchies():
    base = create_studio_bg()
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([150, 560, 650, 650], fill=(0, 0, 0, 40))
    sh = sh.filter(ImageFilter.GaussianBlur(30))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    # Scrunchie 1: Soft Blush Pink Satin
    c1 = (240, 175, 190)
    c1_dark = (195, 120, 140)
    draw.ellipse([170, 220, 430, 480], fill=c1, outline=c1_dark, width=3)
    draw.ellipse([250, 300, 350, 400], fill=(255, 255, 255, 255), outline=c1_dark, width=2)
    for a in range(0, 360, 20):
        rad = math.radians(a)
        x1 = 300 + int(70 * math.cos(rad))
        y1 = 350 + int(70 * math.sin(rad))
        x2 = 300 + int(125 * math.cos(rad))
        y2 = 350 + int(125 * math.sin(rad))
        draw.line([x1, y1, x2, y2], fill=(255, 220, 230, 220), width=5)

    # Scrunchie 2: Champagne Gold Satin
    c2 = (235, 200, 140)
    c2_dark = (185, 150, 90)
    draw.ellipse([370, 180, 630, 440], fill=c2, outline=c2_dark, width=3)
    draw.ellipse([450, 260, 550, 360], fill=(255, 255, 255, 255), outline=c2_dark, width=2)
    for a in range(0, 360, 20):
        rad = math.radians(a)
        x1 = 500 + int(60 * math.cos(rad))
        y1 = 310 + int(60 * math.sin(rad))
        x2 = 500 + int(125 * math.cos(rad))
        y2 = 500 + int(125 * math.sin(rad)) # fix typo
        draw.line([x1, y1, x2, y2], fill=(255, 230, 180, 220), width=5)

    # Scrunchie 3: Sage Green Satin
    c3 = (140, 180, 160)
    c3_dark = (100, 140, 120)
    draw.ellipse([270, 360, 530, 620], fill=c3, outline=c3_dark, width=3)
    draw.ellipse([350, 440, 450, 540], fill=(255, 255, 255, 255), outline=c3_dark, width=2)
    for a in range(0, 360, 20):
        rad = math.radians(a)
        x1 = 400 + int(65 * math.cos(rad))
        y1 = 490 + int(65 * math.sin(rad))
        x2 = 400 + int(125 * math.cos(rad))
        y2 = 490 + int(125 * math.sin(rad))
        draw.line([x1, y1, x2, y2], fill=(180, 220, 200, 220), width=5)

    return base

def render_gold_hairpin():
    base = create_studio_bg()
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([180, 580, 620, 640], fill=(0, 0, 0, 35))
    sh = sh.filter(ImageFilter.GaussianBlur(25))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    # 18K Gold Hairpin Stick
    draw.polygon([(230, 580), (242, 592), (560, 230), (548, 218)], fill=(225, 185, 55, 255), outline=(170, 130, 25, 255))
    draw.line([(235, 583), (554, 224)], fill=(255, 230, 130, 220), width=3)

    # Top Geometric Oval Loop
    draw.ellipse([510, 150, 650, 290], fill=None, outline=(225, 185, 55, 255), width=14)
    draw.ellipse([515, 155, 645, 285], fill=None, outline=(170, 130, 25, 255), width=2)

    # Mother-of-Pearl Center Gem
    draw.ellipse([555, 195, 605, 245], fill=(245, 243, 238, 255), outline=(210, 205, 195, 255), width=1)
    draw.ellipse([565, 205, 580, 220], fill=(255, 255, 255, 255))

    return base

def render_crystal_clips():
    base = create_studio_bg()
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([180, 560, 620, 630], fill=(0, 0, 0, 35))
    sh = sh.filter(ImageFilter.GaussianBlur(25))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    # 4 Parallel Gold Bobby Clips
    y_positions = [220, 320, 420, 520]
    for idx, y in enumerate(y_positions):
        draw.rounded_rectangle([200, y, 560, y + 16], radius=8, fill=(215, 175, 50, 255), outline=(160, 120, 20, 255), width=1)
        draw.line([210, y + 4, 550, y + 4], fill=(255, 230, 120, 200), width=2)

        for x in range(230, 540, 32):
            if idx == 0:
                # Diamonds
                draw.polygon([(x+8, y-6), (x+16, y+8), (x+8, y+22), (x, y+8)], fill=(230, 245, 255, 255), outline=(170, 205, 230, 255), width=1)
                draw.ellipse([x+5, y+3, x+11, y+9], fill=(255, 255, 255, 255))
            elif idx == 1:
                # Gold Stars
                draw.rectangle([x+2, y-4, x+16, y+20], fill=(255, 245, 210, 255), outline=(210, 180, 120, 255), width=1)
                draw.line([x+9, y-4, x+9, y+20], fill=(255, 255, 255, 255), width=2)
            elif idx == 2:
                # Pearls
                draw.ellipse([x+1, y-5, x+17, y+21], fill=(248, 246, 240, 255), outline=(210, 205, 195, 255), width=1)
                draw.ellipse([x+4, y-2, x+9, y+3], fill=(255, 255, 255, 255))
            else:
                # Baguettes
                draw.rounded_rectangle([x, y-4, x+20, y+20], radius=4, fill=(225, 242, 252, 255), outline=(160, 195, 215, 255), width=1)
                draw.line([x+4, y, x+16, y+16], fill=(255, 255, 255, 220), width=2)

    return base

def render_organza_bow():
    base = create_studio_bg()
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([180, 560, 620, 640], fill=(0, 0, 0, 35))
    sh = sh.filter(ImageFilter.GaussianBlur(30))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    cream_fill = (253, 248, 240, 235)
    cream_border = (225, 210, 190, 255)

    # Left Loop
    draw.polygon([(400, 350), (180, 210), (140, 350), (210, 490)], fill=cream_fill, outline=cream_border, width=2)
    draw.polygon([(400, 350), (220, 250), (190, 350), (240, 450)], fill=(245, 238, 228, 220))

    # Right Loop
    draw.polygon([(400, 350), (620, 210), (660, 350), (590, 490)], fill=cream_fill, outline=cream_border, width=2)
    draw.polygon([(400, 350), (580, 250), (610, 350), (560, 450)], fill=(245, 238, 228, 220))

    # Ribbon Tails
    draw.polygon([(365, 370), (240, 590), (310, 610), (390, 410)], fill=cream_fill, outline=cream_border, width=2)
    draw.polygon([(435, 370), (560, 590), (490, 610), (410, 410)], fill=cream_fill, outline=cream_border, width=2)

    # Clip Backing
    draw.rounded_rectangle([330, 335, 470, 365], radius=6, fill=(215, 175, 50, 255), outline=(160, 120, 20, 255))

    # Knot
    draw.rounded_rectangle([355, 310, 445, 390], radius=16, fill=(248, 240, 228, 255), outline=(215, 200, 180, 255), width=2)

    # Pearl Accent
    draw.ellipse([380, 335, 420, 375], fill=(255, 253, 248, 255), outline=(220, 212, 198, 255), width=1)
    draw.ellipse([388, 343, 398, 353], fill=(255, 255, 255, 255))

    return base

def main():
    artifact_dir = r"C:\Users\Bahar\.gemini\antigravity-ide\brain\3043092d-4f68-4858-be6d-1d00232fb4dc"
    media_dir = r"c:\Users\Bahar\Desktop\E-commerce\media\products"

    items = [
        ("photo_1_pearl_comb_studio.png", render_pearl_comb),
        ("photo_2_satin_scrunchies_studio.png", render_satin_scrunchies),
        ("photo_3_gold_hairpin_studio.png", render_gold_hairpin),
        ("photo_4_crystal_clips_studio.png", render_crystal_clips),
        ("photo_5_organza_bow_studio.png", render_organza_bow),
    ]

    for filename, fn in items:
        art_path = os.path.join(artifact_dir, filename)
        med_path = os.path.join(media_dir, filename)
        img = fn()
        img.save(art_path, format="PNG")
        img.save(med_path, format="PNG")
        print(f"Created studio photo: {filename}")

if __name__ == '__main__':
    main()
