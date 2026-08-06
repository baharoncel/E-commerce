import os
import math
from PIL import Image, ImageDraw, ImageFilter

def create_studio_bg(w=800, h=800):
    img = Image.new('RGBA', (w, h), (250, 252, 255, 255))
    draw = ImageDraw.Draw(img)
    # Darker sleek dark-grey studio lighting gradient for men's jewelry
    for r in range(w//2, 0, -8):
        alpha = int(15 * (1 - r / (w//2)))
        draw.ellipse([w//2 - r, h//2 - r, w//2 + r, h//2 + r], fill=(225, 230, 238, alpha))
    return img

def render_mens_ring():
    base = create_studio_bg()
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([220, 540, 580, 610], fill=(0, 0, 0, 50))
    sh = sh.filter(ImageFilter.GaussianBlur(25))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    # Steel Signet Ring Body (Bold Octagonal Heavy Signet)
    draw.polygon([(260, 480), (320, 280), (480, 280), (540, 480), (460, 560), (340, 560)], fill=(120, 125, 135, 255), outline=(70, 75, 85, 255), width=3)
    draw.polygon([(280, 460), (330, 300), (470, 300), (520, 460), (450, 540), (350, 540)], fill=(170, 175, 185, 255))

    # Inner Ring Hole
    draw.ellipse([340, 360, 460, 480], fill=(245, 247, 250, 255), outline=(90, 95, 105, 255), width=3)

    # Top Signet Face (Matte Black Onyx Inlay with Silver Border)
    draw.polygon([(320, 280), (480, 280), (510, 370), (290, 370)], fill=(25, 28, 32, 255), outline=(200, 205, 215, 255), width=4)
    # Metallic specular highlight across onyx face
    draw.line([(340, 290), (460, 360)], fill=(255, 255, 255, 120), width=4)

    return base

def render_mens_bracelet():
    base = create_studio_bg()
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([160, 560, 640, 640], fill=(0, 0, 0, 45))
    sh = sh.filter(ImageFilter.GaussianBlur(30))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    # Braided Siyah Hakiki Deri Band (Double Loop Leather)
    c_x, c_y = 400, 400
    r_x, r_y = 220, 140

    # Outer Braided Leather Strand
    draw.ellipse([c_x - r_x, c_y - r_y, c_x + r_x, c_y + r_y], fill=None, outline=(30, 32, 35, 255), width=32)
    draw.ellipse([c_x - r_x + 8, c_y - r_y + 8, c_x + r_x - 8, c_y + r_y - 8], fill=None, outline=(55, 58, 62, 255), width=16)

    # Braid Texture lines
    for a in range(0, 360, 12):
        rad = math.radians(a)
        x1 = c_x + int((r_x - 14) * math.cos(rad))
        y1 = c_y + int((r_y - 14) * math.sin(rad))
        x2 = c_x + int((r_x + 14) * math.cos(rad))
        y2 = c_y + int((r_y + 14) * math.sin(rad))
        draw.line([x1, y1, x2, y2], fill=(15, 16, 18, 255), width=3)

    # Inner Void
    draw.ellipse([c_x - r_x + 32, c_y - r_y + 32, c_x + r_x - 32, c_y + r_y - 32], fill=(250, 252, 255, 255))

    # Magnetic Stainless Steel Clasp (Center Front)
    draw.rounded_rectangle([330, 230, 470, 285], radius=8, fill=(180, 185, 195, 255), outline=(90, 95, 105, 255), width=2)
    draw.line([400, 230, 400, 285], fill=(60, 65, 75, 255), width=3) # Clasp divide
    draw.line([340, 240, 460, 240], fill=(255, 255, 255, 220), width=3) # Brushed highlight

    return base

def render_mens_necklace():
    base = create_studio_bg()
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([220, 560, 580, 620], fill=(0, 0, 0, 45))
    sh = sh.filter(ImageFilter.GaussianBlur(25))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    # Heavy Steel Ball Chain V-Shape
    draw.line([(180, 120), (400, 420)], fill=(140, 145, 155, 255), width=6)
    draw.line([(620, 120), (400, 420)], fill=(140, 145, 155, 255), width=6)
    for x, y in zip(range(180, 400, 14), range(120, 420, 19)):
        draw.ellipse([x-4, y-4, x+4, y+4], fill=(200, 205, 215, 255))
    for x, y in zip(range(620, 400, -14), range(120, 420, 19)):
        draw.ellipse([x-4, y-4, x+4, y+4], fill=(200, 205, 215, 255))

    # Pendant Bail Ring
    draw.ellipse([382, 405, 418, 441], fill=None, outline=(160, 165, 175, 255), width=6)

    # Black Steel Compass Medallion
    draw.ellipse([310, 430, 490, 610], fill=(30, 32, 36, 255), outline=(180, 185, 195, 255), width=5)
    draw.ellipse([330, 450, 470, 590], fill=(20, 22, 25, 255), outline=(100, 105, 115, 255), width=2)

    # Compass Star (N S E W)
    cx, cy = 400, 520
    draw.polygon([(cx, cy-50), (cx+12, cy-12), (cx+50, cy), (cx+12, cy+12), (cx, cy+50), (cx-12, cy+12), (cx-50, cy), (cx-12, cy-12)], fill=(220, 225, 235, 255))
    draw.polygon([(cx, cy-50), (cx, cy), (cx-12, cy-12)], fill=(140, 145, 155, 255))
    draw.polygon([(cx, cy+50), (cx, cy), (cx+12, cy+12)], fill=(140, 145, 155, 255))
    draw.polygon([(cx+50, cy), (cx, cy), (cx+12, cy-12)], fill=(140, 145, 155, 255))
    draw.polygon([(cx-50, cy), (cx, cy), (cx-12, cy+12)], fill=(140, 145, 155, 255))

    return base

def render_mens_earrings():
    base = create_studio_bg()
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([150, 540, 650, 620], fill=(0, 0, 0, 40))
    sh = sh.filter(ImageFilter.GaussianBlur(25))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    # Earring 1: Black Steel Huggie Hoop
    draw.ellipse([180, 240, 380, 440], fill=None, outline=(35, 38, 42, 255), width=28)
    draw.ellipse([192, 252, 368, 428], fill=None, outline=(70, 75, 82, 255), width=4)

    # Earring 2: Black Steel Square Stud
    draw.rounded_rectangle([450, 260, 630, 440], radius=16, fill=(30, 32, 36, 255), outline=(160, 165, 175, 255), width=4)
    draw.rounded_rectangle([470, 280, 610, 420], radius=10, fill=(20, 22, 25, 255), outline=(80, 85, 95, 255), width=2)
    draw.line([480, 290, 600, 410], fill=(255, 255, 255, 100), width=3) # Specular streak

    return base

def render_mens_cufflinks():
    base = create_studio_bg()
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([150, 560, 650, 630], fill=(0, 0, 0, 40))
    sh = sh.filter(ImageFilter.GaussianBlur(25))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    # Cufflink 1 (Square Brushed Silver with Black Carbon Fiber Inlay)
    draw.rounded_rectangle([170, 260, 370, 460], radius=14, fill=(200, 205, 215, 255), outline=(110, 115, 125, 255), width=3)
    draw.rounded_rectangle([195, 285, 345, 435], radius=6, fill=(25, 28, 32, 255), outline=(150, 155, 165, 255), width=2)
    # Carbon fiber grid lines
    for x in range(205, 340, 15):
        draw.line([x, 285, x, 435], fill=(45, 48, 52, 255), width=2)

    # Cufflink 2 (Matching Right Cufflink)
    draw.rounded_rectangle([430, 260, 630, 460], radius=14, fill=(200, 205, 215, 255), outline=(110, 115, 125, 255), width=3)
    draw.rounded_rectangle([455, 285, 605, 435], radius=6, fill=(25, 28, 32, 255), outline=(150, 155, 165, 255), width=2)
    for x in range(465, 600, 15):
        draw.line([x, 285, x, 435], fill=(45, 48, 52, 255), width=2)

    # Tie Clip Bar Below
    draw.rounded_rectangle([200, 510, 600, 550], radius=8, fill=(210, 215, 225, 255), outline=(120, 125, 135, 255), width=2)
    draw.line([210, 520, 590, 520], fill=(255, 255, 255, 220), width=3) # Brushed highlight

    return base

def main():
    artifact_dir = r"C:\Users\Bahar\.gemini\antigravity-ide\brain\3043092d-4f68-4858-be6d-1d00232fb4dc"
    media_dir = r"c:\Users\Bahar\Desktop\E-commerce\media\products"

    items = [
        ("mens_jewelry_ring.jpg", render_mens_ring),
        ("mens_jewelry_bracelet.jpg", render_mens_bracelet),
        ("mens_jewelry_necklace.jpg", render_mens_necklace),
        ("mens_jewelry_earrings.jpg", render_mens_earrings),
        ("mens_jewelry_cufflinks.jpg", render_mens_cufflinks),
    ]

    for filename, fn in items:
        art_path = os.path.join(artifact_dir, filename)
        med_path = os.path.join(media_dir, filename)
        img = fn()
        # Save as RGB JPEG
        img_rgb = Image.new("RGB", img.size, (255, 255, 255))
        img_rgb.paste(img, mask=img.split()[3])
        img_rgb.save(art_path, quality=95)
        img_rgb.save(med_path, quality=95)
        print(f"Created 100% masculine men's jewelry photo: {filename}")

if __name__ == '__main__':
    main()
