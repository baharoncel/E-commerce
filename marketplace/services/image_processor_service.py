import os
import io
import base64
from PIL import Image, ImageFilter
from django.conf import settings

class ImageProcessorService:
    """
    Ürün görsellerinden:
    1. Responsive varyasyonlar (300w, 600w, 1200w WebP)
    2. Blur-Up (LQIP) Base64 Data URI (16x16 ultra küçük bulanık resim)
    3. Baskın Renk ve Renk Paleti Çıkarımı (Color Extraction)
    işlemlerini gerçekleştirir.
    """

    @staticmethod
    def process_product_image(product):
        """
        Ürün resmi yüklendiğinde responsive görseller, LQIP ve renk paleti üretir.
        """
        if not product.image or not hasattr(product.image, 'path'):
            return False

        try:
            image_path = product.image.path
            if not os.path.exists(image_path):
                return False

            with Image.open(image_path) as img:
                img = img.convert("RGB")

                # 1. LQIP (Blur-Up) Base64 Üretimi
                lqip_base64 = ImageProcessorService.generate_lqip(img)
                product.lqip_base64 = lqip_base64

                # 2. Baskın Renk Çıkarımı (Dominant Color Extraction)
                dominant_color, palette = ImageProcessorService.extract_colors(img)
                product.dominant_color = dominant_color
                product.color_palette = palette

                # 3. Responsive WebP Varyasyonları (300w, 600w, 1200w)
                responsive_dict = ImageProcessorService.generate_responsive_variants(img, product)
                product.responsive_images = responsive_dict

                product.save(update_fields=['lqip_base64', 'dominant_color', 'color_palette', 'responsive_images'])
                return True
        except Exception as e:
            print(f"[ImageProcessorService Error] {e}")
            return False

    @staticmethod
    def generate_lqip(img: Image.Image) -> str:
        """16x16 piksellik bulanıklaştırılmış base64 data URI üretir."""
        lqip = img.resize((16, 16), Image.Resampling.BILINEAR)
        lqip = lqip.filter(ImageFilter.GaussianBlur(radius=1.5))
        buffer = io.BytesIO()
        lqip.save(buffer, format="JPEG", quality=40)
        encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded}"

    @staticmethod
    def extract_colors(img: Image.Image, num_colors: int = 5):
        """
        Görseldeki en baskın renkleri ve HEX kodlarını çıkarır.
        """
        small_img = img.resize((100, 100))
        # Quantize ile baskın renk kümeleme
        quantized = small_img.quantize(colors=num_colors, method=Image.Quantize.FASTOCTREE)
        palette = quantized.getpalette()[:num_colors * 3]

        colors = []
        for i in range(0, len(palette), 3):
            r, g, b = palette[i], palette[i+1], palette[i+2]
            hex_code = f"#{r:02x}{g:02x}{b:02x}"
            colors.append(hex_code)

        dominant_color = colors[0] if colors else "#333333"
        return dominant_color, colors

    @staticmethod
    def generate_responsive_variants(img: Image.Image, product) -> dict:
        """
        300w, 600w, 1200w boyutlarında WebP görselleri üretir.
        """
        target_widths = [300, 600, 1200]
        responsive_map = {}

        rel_dir = os.path.join("products", "responsive")
        abs_dir = os.path.join(settings.MEDIA_ROOT, rel_dir)
        os.makedirs(abs_dir, exist_ok=True)

        orig_w, orig_h = img.size

        for w in target_widths:
            if orig_w > w:
                h = int(orig_h * (w / orig_w))
                resized = img.resize((w, h), Image.Resampling.LANCZOS)
            else:
                resized = img

            filename = f"prod_{product.id if product.id else 'temp'}_{w}w.webp"
            abs_path = os.path.join(abs_dir, filename)
            resized.save(abs_path, format="WEBP", quality=80)

            url = f"{settings.MEDIA_URL}products/responsive/{filename}"
            responsive_map[str(w)] = url

        return responsive_map
