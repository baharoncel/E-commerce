"""
PazarAsistan AI Shopping Chatbot Service
"""
from marketplace.models import Product

def ask_shopping_assistant(user_query, user=None):
    """
    Processes natural language queries from customers and returns 
    smart Turkish responses with recommended product cards.
    """
    query = user_query.strip().lower()
    
    if "sipariş" in query or "kargo" in query:
        return {
            "reply": "Siparişlerinizin güncel kargo durumunu Hesabım > Siparişlerim sayfasından canlı takip edebilirsiniz. Yardımcı olabileceğim başka bir ürün arayışınız var mı?",
            "products": []
        }
    
    if "beden" in query or "kalıp" in query:
        return {
            "reply": "Kıyafetlerimizde standart tam beden kullanılmaktadır. Kararsız kalırsanız bir beden büyük tercih etmenizi öneririz. 14 gün ücretsiz iade garantimiz mevcuttur!",
            "products": []
        }
    
    if "indirim" in query or "fırsat" in query or "kampanya" in query:
        discounted = Product.objects.filter(discount_percent__gt=0)[:3]
        return {
            "reply": "İşte sizin için seçtiğim günün özel indirimli Flaş Fırsat ürünleri:",
            "products": [{"id": p.id, "title": p.title, "price": str(p.base_price), "image_url": p.image_url} for p in discounted]
        }

    # Default product keyword search matching
    words = query.split()
    matched = Product.objects.none()
    for w in words:
        if len(w) > 2:
            matched = matched | Product.objects.filter(title__icontains=w)
    
    products_list = matched.distinct()[:3]
    if products_list.exists():
        return {
            "reply": f"Aramanıza en uygun {products_list.count()} harika ürünü buldum:",
            "products": [{"id": p.id, "title": p.title, "price": str(p.base_price), "image_url": p.image_url} for p in products_list]
        }

    # General Fallback
    top_products = Product.objects.all()[:3]
    return {
        "reply": "Size yardımcı olmaktan mutluluk duyarım! Sitemizdeki en popüler ve çok satan öne çıkan ürünlerimize göz atabilirsiniz:",
        "products": [{"id": p.id, "title": p.title, "price": str(p.base_price), "image_url": p.image_url} for p in top_products]
    }
