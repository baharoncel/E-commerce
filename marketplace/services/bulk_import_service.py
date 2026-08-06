import csv
import io
from decimal import Decimal
from marketplace.models import Product, Category, ProductVariant

class BulkImportService:
    """
    Satıcıların CSV/Excel dosyası ile toplu ürün yüklemesini yöneten servis.
    """

    CSV_HEADER = ['title', 'category_id', 'base_price', 'stock', 'description', 'image_url', 'sku']

    @classmethod
    def generate_sample_csv_template(cls):
        """
        Satıcıların doldurması için hazır CSV örnek şablonu içeriği üretir.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(cls.CSV_HEADER)
        writer.writerow(['Örnek Deri Ceket', '1', '1250.00', '15', '1. sınıf hakiki deri ceket.', 'products/jacket.jpg', 'SKU-JKT-001'])
        writer.writerow(['Örnek Kablosuz Kulaklık', '2', '850.00', '30', 'Bluetooth 5.0 gürültü engelleyici.', 'products/headphone.jpg', 'SKU-HP-002'])
        return output.getvalue()

    @classmethod
    def import_products_from_csv(cls, seller_profile, csv_file_stream):
        """
        CSV dosya yayınını okur, ürünleri doğrular ve toplu halde veritabanına kaydeder.
        """
        try:
            decoded_file = csv_file_stream.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(decoded_file))
        except Exception as e:
            return False, f"CSV dosyası okunamadı: {str(e)}", 0

        created_count = 0
        errors = []

        for row_idx, row in enumerate(reader, start=2):
            title = row.get('title', '').strip()
            category_id = row.get('category_id', '').strip()
            base_price = row.get('base_price', '').strip()
            stock = row.get('stock', '10').strip()
            description = row.get('description', '').strip()
            image_url = row.get('image_url', '').strip()
            sku = row.get('sku', f"SKU-{seller_profile.id}-{row_idx}").strip()

            if not title or not base_price:
                errors.append(f"Satır {row_idx}: Ürün başlığı veya fiyatı boş.")
                continue

            try:
                price_val = Decimal(base_price)
                stock_val = int(stock)
            except Exception:
                errors.append(f"Satır {row_idx}: Geçersiz fiyat veya stok adedi.")
                continue

            category = None
            if category_id and category_id.isdigit():
                category = Category.objects.filter(id=int(category_id)).first()

            product = Product.objects.create(
                seller=seller_profile,
                category=category,
                title=title,
                base_price=price_val,
                description=description,
                image=image_url if image_url else None
            )

            ProductVariant.objects.create(
                product=product,
                price=price_val,
                stock=stock_val,
                sku=sku
            )

            created_count += 1

        msg = f"{created_count} adet ürün başarıyla aktarıldı."
        if errors:
            msg += f" (Hatalar: {'; '.join(errors[:3])})"

        return True, msg, created_count
