from marketplace.models import ProductVariant, InventoryLog, Notification

class InventoryService:
    """
    Stok hareket takibi ve Kritik Stok Uyarı Servisi.
    """

    LOW_STOCK_THRESHOLD = 5

    @staticmethod
    def update_stock(variation, change_amount, reason):
        """
        Stok miktarını günceller, InventoryLog kaydeder ve gerekirse kritik stok uyarısı verir.
        """
        previous_stock = variation.stock
        new_stock = previous_stock + change_amount

        if new_stock < 0:
            raise ValueError(f"Yetersiz stok! Mevcut: {previous_stock}, İstenen Değişim: {change_amount}")

        variation.stock = new_stock
        variation.save()

        # Log Oluştur
        log = InventoryLog.objects.create(
            variation=variation,
            change_amount=change_amount,
            previous_stock=previous_stock,
            new_stock=new_stock,
            reason=reason
        )

        # Kritik Stok Kontrolü
        if new_stock <= InventoryService.LOW_STOCK_THRESHOLD:
            seller_user = variation.product.seller.user
            Notification.objects.create(
                user=seller_user,
                title="⚠️ Kritik Stok Uyarısı!",
                message=f"'{variation.product.title}' ({variation.color}/{variation.size}) stok miktarı {new_stock} adede düştü!"
            )

        return log

    @staticmethod
    def get_low_stock_items(seller_profile):
        """
        Satıcının kritik stok seviyesine düşmüş varyasyonlarını döndürür.
        """
        return ProductVariant.objects.filter(
            product__seller=seller_profile,
            stock__lte=InventoryService.LOW_STOCK_THRESHOLD
        )

