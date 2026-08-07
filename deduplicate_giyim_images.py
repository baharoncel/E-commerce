import os
import sys
import django

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Category, Product, ProductVariant, ProductReview

print("Deduplicating images in Giyim & Moda categories...")

# Get all Giyim & Moda categories
giyim_cats = list(Category.objects.filter(name__icontains='giyim')) + list(Category.objects.filter(parent__name__icontains='giyim')) + list(Category.objects.filter(name__in=['Tişört', 'Gömlek', 'Bluz', 'Pantolon', 'Jean (Kot)', 'Etek', 'Elbise', 'Ceket', 'Hırka & Kazak', 'Tulum', 'Şort', 'Eşofman & Tayt', 'Mont & Ceket', 'Hırka & Yelek', 'Gömlek & Tişört', 'Elbise & Tulum', 'Pijama & Kombin Setleri']))

products = Product.objects.filter(category__in=giyim_cats)

seen_images = {}
deleted_count = 0

for p in products:
    if not p.image:
        continue
    img_name = p.image.name
    
    if img_name in seen_images:
        print(f"Deleting duplicate product ID {p.id}: '{p.title}' (Image: {img_name})")
        ProductVariant.objects.filter(product=p).delete()
        ProductReview.objects.filter(product=p).delete()
        p.delete()
        deleted_count += 1
    else:
        seen_images[img_name] = p.id

print(f"\nSuccessfully deduplicated Giyim & Moda images!")
print(f"Removed {deleted_count} duplicate products.")
print(f"Remaining unique products in Giyim & Moda: {len(seen_images)}")
