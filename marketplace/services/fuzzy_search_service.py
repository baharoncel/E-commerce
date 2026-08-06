import re
from difflib import SequenceMatcher
from django.db.models import Q
from marketplace.models import Product

class FuzzySearchService:
    """
    Tam Metin & Yazım Hatalarına Toleranslı (Fuzzy) Arama Engine.
    Kullanıcının girdiği kelimeleri analiz eder, Türkçe karakter değişimlerini
    ve harf hatalarını ("çeket" -> "ceket") Levenshtein benzerliği ile eşleştirir.
    """

    # Türkçe yaygın yazım düzeltmeleri sözlüğü
    COMMON_TYPO_MAP = {
        'çeket': 'ceket',
        'pantolon': 'pantolon',
        'tişört': 't-shirt',
        'tşört': 't-shirt',
        'ayakkabı': 'ayakkabı',
        'ayakkabi': 'ayakkabı',
        'gömlek': 'gömlek',
        'gomlek': 'gömlek',
        'elbişe': 'elbise',
        'saat': 'saat',
        'çanta': 'çanta',
        'canta': 'çanta',
    }

    @classmethod
    def search(cls, query: str, queryset=None, threshold: float = 0.6):
        """
        Gelişmiş arama gerçekleştirir.
        """
        if queryset is None:
            queryset = Product.objects.all()

        if not query or not query.strip():
            return queryset

        raw_query = query.strip().lower()
        words = raw_query.split()

        # 1. Sözlük Tabanlı Yazım Düzeltmesi (Fuzzy Spelling Correction)
        corrected_words = []
        for word in words:
            corrected = cls.COMMON_TYPO_MAP.get(word)
            if not corrected:
                # En yakın kelime benzerliği bulma
                best_match = word
                best_ratio = 0.0
                for dict_word, target in cls.COMMON_TYPO_MAP.items():
                    ratio = SequenceMatcher(None, word, dict_word).ratio()
                    if ratio > best_ratio and ratio >= threshold:
                        best_ratio = ratio
                        best_match = target
                corrected_words.append(best_match)
            else:
                corrected_words.append(corrected)

        search_query_str = " ".join(corrected_words)

        # 2. Çok Alanlı Ağırlıklı Arama (Title, Description, Category, Seller, Dominant Color)
        q_objects = Q()
        for w in set(words + corrected_words):
            q_objects |= Q(title__icontains=w)
            q_objects |= Q(description__icontains=w)
            q_objects |= Q(category__name__icontains=w)
            q_objects |= Q(seller__store_name__icontains=w)
            q_objects |= Q(dominant_color__icontains=w)

        results = queryset.filter(q_objects).distinct()

        # 3. Sonuçları Benzerlik Skoruna Göre Sıralama (Relevance Scoring)
        def calc_score(product):
            score = 0.0
            p_title = product.title.lower()
            if raw_query in p_title or search_query_str in p_title:
                score += 10.0
            for w in corrected_words:
                if w in p_title:
                    score += 5.0
                if product.category and w in product.category.name.lower():
                    score += 3.0
                if w in product.description.lower():
                    score += 1.0
            return score

        sorted_results = sorted(results, key=calc_score, reverse=True)
        return sorted_results
