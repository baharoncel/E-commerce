import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Product, Category, ProductVariant, OrderItem, SubOrder, Order, ReturnRequest, ProductReview

def cleanup():
    # Target products with mismatched images: 6670, 6671, 6672, 6673
    mismatched_ids = [6670, 6671, 6672, 6673]
    
    # Also clean up placeholder products in Taçlar and Tokalar & Lastikler that use generic dummy images (necklace.png, ring.png, earrings.png, etc.)
    dummy_products = Product.objects.filter(
        category__name__in=['Taçlar', 'Tokalar & Lastikler', 'Şal & Atkı', 'Kemer', 'Şapka & Bere']
    ).exclude(id__in=[6674, 6675, 6676, 6677, 6678])

    all_to_remove = Product.objects.filter(id__in=mismatched_ids) | dummy_products

    count = all_to_remove.count()
    print(f"Found {count} products to clean up.")

    for p in all_to_remove:
        # Delete dependencies if any
        ProductVariant.objects.filter(product=p).delete()
        ProductReview.objects.filter(product=p).delete()
        print(f"Deleting Product ID: {p.id} - {p.title} (Image: {p.image})")
        p.delete()

    print("Cleanup completed successfully!")

if __name__ == '__main__':
    cleanup()
