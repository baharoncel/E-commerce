from django.db.models import F
from marketplace.models import SearchQueryLog, Product

class SearchAnalyticsService:
    """
    Popüler Arama Kelimeleri ve Akıllı Otomatik Tamamlama Servisi.
    """

    @staticmethod
    def log_search_query(query):
        """
        Kullanıcının arama kelimesini kaydeder veya sayacını artırır.
        """
        cleaned_query = query.strip().lower()
        if not cleaned_query or len(cleaned_query) < 2:
            return None

        log, created = SearchQueryLog.objects.get_or_create(query=cleaned_query)
        if not created:
            log.count = F('count') + 1
            log.save()
            log.refresh_from_db()
        return log

    @staticmethod
    def get_trending_searches(limit=5):
        """
        En çok aranan trend kelimeleri döndürür.
        """
        return SearchQueryLog.objects.all().order_by('-count')[:limit]

    @staticmethod
    def get_autocomplete_suggestions(keyword, limit=5):
        """
        Arama çubuğu için canlı otomatik tamamlama önerileri sunar.
        """
        if not keyword or len(keyword) < 2:
            return []

        products = Product.objects.filter(
            title__icontains=keyword
        ).values('id', 'title', 'base_price', 'category__name')[:limit]


        return list(products)
