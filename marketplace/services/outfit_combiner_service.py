"""
AI Outfit Combiner Service ("Bu Ürünle Harika Gider" & Complete the Look Engine)
"""
from marketplace.models import Product, Category

def get_outfit_recommendations(product_id, limit=3):
    """
    Given a target product, automatically selects complementary products 
    from matching style categories to form a complete outfit.
    """
    try:
        target_product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return []

    target_category = target_product.category
    category_name = target_category.name.lower() if target_category else ""

    # Complementary category logic
    complementary_terms = []
    if "tişört" in category_name or "gömlek" in category_name or "bluz" in category_name:
        complementary_terms = ["pantolon", "jean", "etek", "ceket", "ayakkabı", "çanta"]
    elif "pantolon" in category_name or "jean" in category_name or "etek" in category_name:
        complementary_terms = ["tişört", "gömlek", "bluz", "ceket", "ayakkabı", "çanta"]
    elif "elbise" in category_name:
        complementary_terms = ["ceket", "ayakkabı", "çanta", "saat", "gözlük", "parfüm"]
    else:
        complementary_terms = ["tişört", "pantolon", "ayakkabı", "çanta"]

    matched_products = []
    for term in complementary_terms:
        if len(matched_products) >= limit:
            break
        matching = Product.objects.filter(
            title__icontains=term
        ).exclude(id=product_id).first()
        if matching and matching not in matched_products:
            matched_products.append(matching)

    # Fallback to other products in catalog if limit not reached
    if len(matched_products) < limit:
        extra = Product.objects.exclude(id=product_id).exclude(id__in=[p.id for p in matched_products])[:limit - len(matched_products)]
        matched_products.extend(list(extra))

    return matched_products
