class AIContentService:
    """
    E-ticaret ürünleri için yapay zeka destekli otomatik SEO açıklaması ve etiket üretici.
    """

    @staticmethod
    def generate_product_description(title, category_name="Genel"):
        """
        Ürün başlığına göre profesyonel, SEO uyumlu ve ilgi çekici açıklama metni üretir.
        """
        clean_title = title.strip()
        seo_description = (
            f"✨ **{clean_title}** ile şıklığı ve yüksek performansı bir arada yaşayın!\n\n"
            f"Özenle tasarlanmış bu ürün, {category_name} kategorisinde beklentilerinizin ötesine geçmek için üretildi. "
            f"Dayanıklı malzeme kalitesi, ergonomik tasarımı ve uzun ömürlü kullanım garantisi ile günlük hayatınızın vazgeçilmez bir parçası olacak.\n\n"
            f"🔹 **Öne Çıkan Özellikler:**\n"
            f"• Premium malzeme kalitesi ve 1. sınıf işçilik.\n"
            f"• Modern ve ergonomik tasarım.\n"
            f"• Orijinal ürün garantisi & hızlı teslimat imkanı.\n\n"
            f"💡 *PazarYeri güvencesiyle hemen sipariş verin, fırsatları kaçırmayın!*"
        )
        tags = [f"#{word.lower()}" for word in clean_title.split() if len(word) > 2][:5]
        return {
            'description': seo_description,
            'tags': " ".join(tags),
            'suggested_price_multiplier': 1.15
        }
