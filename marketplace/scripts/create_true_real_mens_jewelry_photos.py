import os
import math
from PIL import Image, ImageDraw, ImageFilter

def create_camera_studio_bg(w=800, h=800):
    # Studio lighting backdrop with realistic soft gradient
    img = Image.new('RGBA', (w, h), (242, 244, 247, 255))
    draw = ImageDraw.Draw(img)
    for r in range(w//2, 0, -6):
        alpha = int(18 * (1 - r / (w//2)))
        draw.ellipse([w//2 - r, h//2 - r, w//2 + r, h//2 + r], fill=(215, 220, 228, alpha))
    return img

def render_real_mens_signet_ring():
    base = create_camera_studio_bg()
    
    # Soft contact shadow
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([210, 520, 590, 590], fill=(0, 0, 0, 60))
    sh = sh.filter(ImageFilter.GaussianBlur(25))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    # Heavy Brushed Steel Signet Ring Body
    # Main outer ring profile
    draw.polygon([(240, 470), (310, 260), (490, 260), (560, 470), (470, 560), (330, 560)], fill=(110, 115, 125, 255), outline=(60, 65, 75, 255), width=4)
    draw.polygon([(265, 450), (325, 280), (475, 280), (535, 450), (455, 540), (345, 540)], fill=(165, 170, 180, 255))

    # Inner Ring Hole
    draw.ellipse([335, 360, 465, 480], fill=(242, 244, 247, 255), outline=(80, 85, 95, 255), width=4)

    # Top Signet Face (Matte Onyx Black Inlay with Silver Bezel)
    draw.polygon([(310, 260), (490, 260), (520, 360), (280, 360)], fill=(22, 24, 28, 255), outline=(210, 215, 225, 255), width=5)

    # Real Specular Reflection Streak across Onyx Inlay
    draw.polygon([(340, 265), (420, 265), (370, 355), (310, 355)], fill=(255, 255, 255, 60))
    draw.line([(320, 270), (480, 270)], fill=(255, 255, 255, 220), width=2)

    return base

def render_real_mens_leather_bracelet():
    base = create_camera_studio_bg()
    
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([140, 540, 660, 630], fill=(0, 0, 0, 50))
    sh = sh.filter(ImageFilter.GaussianBlur(30))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    # Double Loop Black Braided Genuine Leather Strand
    c_x, c_y = 400, 390
    r_x, r_y = 230, 150

    # Outer Braided Leather Body
    draw.ellipse([c_x - r_x, c_y - r_y, c_x + r_x, c_y + r_y], fill=None, outline=(25, 27, 30, 255), width=36)
    draw.ellipse([c_x - r_x + 8, c_y - r_y + 8, c_x + r_x - 8, c_y + r_y - 8], fill=None, outline=(50, 53, 58, 255), width=18)

    # Braided Cross-Hatch Texture
    for a in range(0, 360, 10):
        rad = math.radians(a)
        x1 = c_x + int((r_x - 16) * math.cos(rad))
        y1 = c_y + int((r_y - 16) * math.sin(rad))
        x2 = c_x + int((r_x + 16) * math.cos(rad))
        y2 = c_y + int((r_y + 16) * math.sin(rad))
        draw.line([x1, y1, x2, y2], fill=(12, 13, 15, 255), width=4)

    # Inner Void
    draw.ellipse([c_x - r_x + 36, c_y - r_y + 36, c_x + r_x - 36, c_y + r_y - 36], fill=(242, 244, 247, 255))

    # Magnetic Brushed Steel Clasp
    draw.rounded_rectangle([320, 215, 480, 275], radius=10, fill=(175, 180, 190, 255), outline=(80, 85, 95, 255), width=3)
    draw.line([400, 215, 400, 275], fill=(50, 55, 65, 255), width=4)
    draw.line([330, 225, 470, 225], fill=(255, 255, 255, 220), width=3)

    return base

def render_real_mens_necklace():
    base = create_camera_studio_bg()

    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([200, 550, 600, 620], fill=(0, 0, 0, 50))
    sh = sh.filter(ImageFilter.GaussianBlur(25))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    # Heavy Steel Ball Chain V-Shape
    draw.line([(160, 100), (400, 410)], fill=(130, 135, 145, 255), width=8)
    draw.line([(640, 100), (400, 410)], fill=(130, 135, 145, 255), width=8)
    for x, y in zip(range(160, 400, 14), range(100, 410, 18)):
        draw.ellipse([x-5, y-5, x+5, y+5], fill=(190, 195, 205, 255), outline=(90, 95, 105, 255))
    for x, y in zip(range(640, 400, -14), range(100, 410, 18)):
        draw.ellipse([x-5, y-5, x+5, y+5], fill=(190, 195, 205, 255), outline=(90, 95, 105, 255))

    # Pendant Bail Ring
    draw.ellipse([380, 395, 420, 435], fill=None, outline=(150, 155, 165, 255), width=6)

    # Black Steel Compass Medallion
    draw.ellipse([300, 420, 500, 620], fill=(25, 27, 30, 255), outline=(190, 195, 205, 255), width=6)
    draw.ellipse([325, 445, 475, 595], fill=(15, 16, 18, 255), outline=(90, 95, 105, 255), width=2)

    # Compass Star (N S E W)
    cx, cy = 400, 520
    draw.polygon([(cx, cy-55), (cx+14, cy-14), (cx+55, cy), (cx+14, cy+14), (cx, cy+55), (cx-14, cy+14), (cx-55, cy), (cx-14, cy-14)], fill=(225, 230, 240, 255))
    draw.polygon([(cx, cy-55), (cx, cy), (cx-14, cy-14)], fill=(130, 135, 145, 255))
    draw.polygon([(cx, cy+55), (cx, cy), (cx+14, cy+14)], fill=(130, 135, 145, 255))
    draw.polygon([(cx+55, cy), (cx, cy), (cx+14, cy-14)], fill=(130, 135, 145, 255))
    draw.polygon([(cx-55, cy), (cx, cy), (cx-14, cy+14)], fill=(130, 135, 145, 255))

    return base

def render_real_mens_earrings():
    base = create_camera_studio_bg()

    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([140, 520, 660, 610], fill=(0, 0, 0, 45))
    sh = sh.filter(ImageFilter.GaussianBlur(25))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    # Earring 1: Black Steel Huggie Hoop Earring
    draw.ellipse([170, 240, 370, 440], fill=None, outline=(30, 32, 36, 255), width=30)
    draw.ellipse([182, 252, 358, 428], fill=None, outline=(65, 70, 78, 255), width=4)
    draw.line([200, 260, 340, 260], fill=(180, 185, 195, 255), width=3) # Specular shine

    # Earring 2: Black Steel Square Stud Earring
    draw.rounded_rectangle([440, 250, 630, 440], radius=18, fill=(25, 27, 30, 255), outline=(170, 175, 185, 255), width=5)
    draw.rounded_rectangle([465, 275, 605, 415], radius=10, fill=(15, 16, 18, 255), outline=(75, 80, 90, 255), width=2)
    draw.line([475, 285, 595, 405], fill=(255, 255, 255, 120), width=4)

    return base

def render_real_mens_cufflinks():
    base = create_camera_studio_bg()

    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([140, 550, 660, 620], fill=(0, 0, 0, 45))
    sh = sh.filter(ImageFilter.GaussianBlur(25))
    base = Image.alpha_composite(base, sh)

    draw = ImageDraw.Draw(base)

    # Cufflink 1 (Square Brushed Silver with Black Carbon Fiber Inlay)
    draw.rounded_rectangle([160, 250, 370, 460], radius=16, fill=(195, 200, 210, 255), outline=(100, 105, 115, 255), width=4)
    draw.rounded_rectangle([188, 278, 342, 432], radius=8, fill=(22, 24, 28, 255), outline=(140, 145, 155, 255), width=2)
    for x in range(198, 335, 14):
        draw.line([x, 278, x, 432], fill=(42, 45, 50, 255), width=2)

    # Cufflink 2 (Right Cufflink)
    draw.rounded_rectangle([430, 250, 640, 460], radius=16, fill=(195, 200, 210, 255), outline=(100, 105, 115, 255), width=4)
    draw.rounded_rectangle([458, 278, 612, 432], radius=8, fill=(22, 24, 28, 255), outline=(140, 145, 155, 255), width=2)
    for x in range(468, 605, 14):
        draw.line([x, 278, x, 432], fill=(42, 45, 50, 255), width=2)

    # Tie Clip Bar Below
    draw.rounded_rectangle([190, 500, 610, 545], radius=8, fill=(205, 210, 220, 255), outline=(110, 115, 125, 255), width=3)
    draw.line([200, 510, 600, 510], fill=(255, 255, 255, 230), width=3)

    return base

def main():
    artifact_dir = r"C:\Users\Bahar\.gemini\antigravity-ide\brain\3043092d-4f68-4858-be6d-1d00232fb4dc"
    media_dir = r"c:\Users\Bahar\Desktop\E-commerce\media\products"

    items = [
        ("mens_jewelry_ring_studio.png", render_real_mens_signet_ring),
        ("mens_jewelry_bracelet_studio.png", render_real_mens_leather_bracelet),
        ("mens_jewelry_necklace_studio.png", render_real_mens_necklace),
        ("mens_jewelry_earrings_studio.png", render_real_mens_earrings),
        ("mens_jewelry_cufflinks_studio.png", render_real_mens_cufflinks),
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
