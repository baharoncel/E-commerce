from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

# ==============================================================================
# 1. USER & ROLE MANAGEMENT (ASP.NET Core Identity Karşılığı)
# ==============================================================================

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('SUPERADMIN', 'Super Admin (Site Sahibi)'),
        ('SELLER', 'Seller (Satıcı Mağaza)'),
        ('CUSTOMER', 'Customer (Müşteri)'),
    )
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='CUSTOMER',
        help_text="Kullanıcının platformdaki yetki rolü."
    )

    def is_superadmin(self):
        return self.role == 'SUPERADMIN' or self.is_superuser

    def is_seller(self):
        return self.role == 'SELLER'

    def is_customer(self):
        return self.role == 'CUSTOMER'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class SellerProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='seller_profile',
        help_text="Her profil bir CustomUser'a bağlıdır."
    )
    store_name = models.CharField(max_length=150, unique=True, verbose_name="Mağaza Adı")
    iban = models.CharField(max_length=34, verbose_name="IBAN Numarası (Simülasyon için)")
    commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=10.00, 
        verbose_name="Komisyon Oranı (%)",
        help_text="Platformun bu satıcının satışlarından alacağı komisyon yüzdesi."
    )
    is_approved = models.BooleanField(default=True, verbose_name="Onay Durumu")

    def __str__(self):
        return self.store_name


# ==============================================================================
# 2. CATALOG & HIERARCHICAL RELATIONSHIPS (Entity Framework Core Alt Kategoriler)
# ==============================================================================

class Category(models.Model):
    """
    Ürün kategorileri. parent alanı sayesinde alt kategorileri (subcategories) destekler.
    Örn: Takılar (parent=None) -> Yüzük (parent=Takılar)
    """
    name = models.CharField(max_length=100, verbose_name="Kategori Adı")
    slug = models.SlugField(max_length=120, blank=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='subcategories',
        verbose_name="Üst Kategori"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            if self.parent:
                self.slug = slugify(f"{self.parent.name}-{self.name}")
            else:
                self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ('name', 'parent')

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Product(models.Model):
    seller = models.ForeignKey(
        SellerProfile, 
        on_delete=models.CASCADE, 
        related_name='products',
        verbose_name="Satıcı (Mağaza)"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='products',
        verbose_name="Kategori"
    )
    title = models.CharField(max_length=200, verbose_name="Ürün Başlığı")
    description = models.TextField(verbose_name="Ürün Açıklaması", blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Taban Fiyat")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Ürün Görseli")
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'), verbose_name='Ortalama Puan')
    review_count = models.PositiveIntegerField(default=0, verbose_name='Toplam Yorum Sayısı')
    
    # Görsel İşleme, LQIP, Responsive ve Renk Çıkarımı Alanları
    dominant_color = models.CharField(max_length=30, blank=True, null=True, verbose_name="Baskın Renk Code")
    color_palette = models.JSONField(default=list, blank=True, verbose_name="Baskın Renk Paleti")
    lqip_base64 = models.TextField(blank=True, null=True, verbose_name="Blur-Up (LQIP) Base64")
    responsive_images = models.JSONField(default=dict, blank=True, verbose_name="Responsive Görsel Varyantları")
    
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def image_url(self):
        if self.image:
            if self.image.name.startswith('http://') or self.image.name.startswith('https://'):
                return self.image.name
            return self.image.url
        return ''

    def get_srcset(self):
        if self.responsive_images:
            return ", ".join([f"{url} {width}w" for width, url in self.responsive_images.items()])
        return ""

    def __str__(self):
        return f"{self.title} - {self.seller.store_name}"


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='Ürün')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='product_reviews', verbose_name='Kullanıcı')
    rating = models.PositiveSmallIntegerField(verbose_name='Puan', default=5)
    comment = models.TextField(blank=True, verbose_name='Yorum')
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False, verbose_name='Satıcı Onaylı')
    image = models.ImageField(upload_to='reviews/', blank=True, null=True, verbose_name='Yorum Görseli')
    helpful_count = models.PositiveIntegerField(default=0, verbose_name='Faydalı Bulma Sayısı')

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f'{self.user.username} - {self.product.title} ({self.rating}/5)'

    @property
    def is_verified_buyer(self):
        from marketplace.models import OrderItem
        return OrderItem.objects.filter(
            product=self.product,
            sub_order__parent_order__customer=self.user,
            sub_order__status='DELIVERED'
        ).exists()


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='variants',
        verbose_name="Ürün"
    )
    color = models.CharField(max_length=50, blank=True, null=True, verbose_name="Renk")
    size = models.CharField(max_length=20, blank=True, null=True, verbose_name="Beden")
    size_number = models.IntegerField(blank=True, null=True, verbose_name="Numara")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        verbose_name="Varyasyon Fiyatı",
        help_text="Boş bırakılırsa ürünün taban fiyatı geçerli olur."
    )
    stock = models.IntegerField(default=0, verbose_name="Stok Adedi")
    sku = models.CharField(max_length=100, unique=True, verbose_name="Stok Kodu (SKU)")

    def get_price(self):
        return self.price if self.price is not None else self.product.base_price

    def __str__(self):
        variant_desc = []
        if self.color: variant_desc.append(f"Renk: {self.color}")
        if self.size: variant_desc.append(f"Beden: {self.size}")
        if self.size_number: variant_desc.append(f"No: {self.size_number}")
        
        desc = ", ".join(variant_desc) if variant_desc else "Standart"
        return f"{self.product.title} ({desc}) - Stok: {self.stock}"


# ==============================================================================
# 3. BASKET & SPLIT ORDER MANAGEMENT (Sipariş Yönetimi)
# ==============================================================================

class Order(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Ödeme Bekleniyor'),
        ('PAID', 'Ödendi'),
        ('FAILED', 'Ödeme Başarısız'),
    )
    ORDER_STATUS_CHOICES = (
        ('RECEIVED', 'Alındı'),
        ('PREPARING', 'Hazırlanıyor'),
        ('SHIPPED', 'Kargoya Verildi'),
        ('DELIVERED', 'Teslim Edildi'),
        ('CANCELLED', 'İptal'),
    )
    customer = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='orders',
        verbose_name="Müşteri"
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Toplam Tutar")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING', verbose_name="Ödeme Durumu")
    payment_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ödeme Gateway ID")
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='RECEIVED', verbose_name="Sipariş Durumu")
    tracking_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Kargo Takip Numarası")
    shipping_company = models.CharField(max_length=100, blank=True, null=True, verbose_name="Kargo Firması")
    estimated_delivery_date = models.DateField(blank=True, null=True, verbose_name="Tahmini Teslimat Tarihi")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ana Sipariş #{self.id} - {self.customer.username} - {self.total_amount} TL"


class SubOrder(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Hazırlanıyor'),
        ('SHIPPED', 'Kargoya Verildi'),
        ('DELIVERED', 'Teslim Edildi'),
        ('CANCELLED', 'İptal Edildi'),
    )
    parent_order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='sub_orders',
        verbose_name="Ana Sipariş"
    )
    seller = models.ForeignKey(
        SellerProfile, 
        on_delete=models.CASCADE, 
        related_name='sub_orders',
        verbose_name="Satıcı"
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Satıcı Ara Toplam")
    commission_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Platform Komisyon Kesintisi"
    )
    seller_payout = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Satıcıya Net Hak Ediş"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Sipariş Durumu")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alt Sipariş #{self.id} (Ana Sipariş #{self.parent_order.id}) - Satıcı: {self.seller.store_name}"


class OrderItem(models.Model):
    sub_order = models.ForeignKey(
        SubOrder, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name="Alt Sipariş"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.PROTECT, 
        verbose_name="Ürün"
    )
    variant = models.ForeignKey(
        ProductVariant, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        verbose_name="Ürün Varyasyonu"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Adet")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Birim Satış Fiyatı")

    def get_total_item_price(self):
        return self.price * self.quantity

    def __str__(self):
        variant_desc = f" ({self.variant})" if self.variant else ""
        return f"{self.product.title}{variant_desc} x {self.quantity}"


# ==============================================================================
# 4. CUSTOMER INTERACTION FEATURES (Müşteri Etkileşim Tabloları)
# ==============================================================================

class Coupon(models.Model):
    DISCOUNT_TYPE_PERCENTAGE = 'PERCENTAGE'
    DISCOUNT_TYPE_FIXED_AMOUNT = 'FIXED_AMOUNT'
    DISCOUNT_TYPE_CHOICES = (
        (DISCOUNT_TYPE_PERCENTAGE, 'Yüzdelik'),
        (DISCOUNT_TYPE_FIXED_AMOUNT, 'Sabit Tutar'),
    )

    seller = models.ForeignKey('SellerProfile', on_delete=models.CASCADE, null=True, blank=True, related_name='coupons', verbose_name='Satıcı Mağaza')
    code = models.CharField(max_length=50, unique=True, verbose_name='Kupon Kodu')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default=DISCOUNT_TYPE_PERCENTAGE, verbose_name='İndirim Tipi')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='İndirim Değeri')
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='Minimum Sepet Tutarı')
    usage_limit = models.PositiveIntegerField(default=1, verbose_name='Kullanım Limiti')
    used_count = models.PositiveIntegerField(default=0, verbose_name='Kullanım Sayısı')
    expiration_date = models.DateTimeField(blank=True, null=True, verbose_name='Son Kullanma Tarihi')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code


class Favorite(models.Model):
    """Müşterinin favorilediği ürünleri tutar."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"


class ReturnRequest(models.Model):
    """Sipariş satırına özel veya alt siparişe özel iade taleplerini yönetir."""
    STATUS_CHOICES = (
        ('PENDING', 'Onay Bekliyor'),
        ('APPROVED', 'Onaylandı (İade Alındı)'),
        ('REJECTED', 'İade Reddedildi'),
        ('COMPLETED', 'Tamamlandı (Ücret İade Edildi)'),
    )
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='return_requests', null=True, blank=True)
    sub_order = models.ForeignKey(SubOrder, on_delete=models.CASCADE, related_name='return_requests', null=True, blank=True, verbose_name="Alt Sipariş")
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='customer_return_requests', null=True, blank=True, verbose_name="Müşteri")
    reason = models.TextField(verbose_name="İade Talebi Nedeni")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Durum")
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="İade Edilecek Tutar")
    return_shipping_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="İade Kargo Kodu")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Eğer bu bir güncelleme ise ve durum APPROVED olarak değişiyorsa stokları otomatik geri ekle
        if self.id:
            old_self = ReturnRequest.objects.get(id=self.id)
            if old_self.status != 'APPROVED' and self.status == 'APPROVED':
                variant = self.order_item.variant if self.order_item else None
                if variant:
                    variant.stock += self.order_item.quantity
                    variant.save()
        super().save(*args, **kwargs)

    def __str__(self):
        target = f"Sipariş Satırı #{self.order_item.id}" if self.order_item else (f"Alt Sipariş #{self.sub_order.id}" if self.sub_order else "İade")
        return f"İade Talebi #{self.id} - {target} - Durum: {self.get_status_display()}"



class ChatMessage(models.Model):
    """Müşteri ile satıcı arasındaki mesajlaşmayı yönetir."""
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField(verbose_name="Mesaj")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mesaj: {self.sender.username} -> {self.recipient.username} ({self.created_at.strftime('%d/%m %H:%M')})"


class Notification(models.Model):
    """Kullanıcılara giden sistem bildirimlerini tutar (sipariş durumu güncellemesi, iade onayı vb.)."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200, verbose_name="Başlık")
    message = models.TextField(verbose_name="Açıklama")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bildirim: {self.user.username} - {self.title}"


class PushDeviceToken(models.Model):
    """Mobil cihaz Push Notification token'larını (FCM / APNS) tutar."""
    DEVICE_TYPE_CHOICES = (
        ('ANDROID', 'Android Device'),
        ('IOS', 'iOS Apple Device'),
        ('WEB', 'Web Browser'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='push_tokens')
    token = models.CharField(max_length=255, unique=True, verbose_name="FCM / APNS Push Token")
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE_CHOICES, default='ANDROID')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"PushToken: {self.user.username} ({self.device_type})"


class FlashSale(models.Model):
    """Geri sayımlı Fırsat Ürünleri (Flash Sale Kampanyaları) modeli."""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='flash_sale')
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=20.00, verbose_name="Flaş İndirim Oranı (%)")
    end_time = models.DateTimeField(verbose_name="Kampanya Bitiş Zamanı")
    is_active = models.BooleanField(default=True, verbose_name="Kampanya Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True)

    def get_flash_price(self):
        """Flaş indirimli ürün fiyatını hesaplar."""
        factor = Decimal("1.00") - (self.discount_percent / Decimal("100.00"))
        return round(self.product.base_price * factor, 2)

    def is_valid(self):
        from django.utils import timezone
        return self.is_active and self.end_time > timezone.now()

    def __str__(self):
        return f"Flaş İndirim: {self.product.title} (%{self.discount_percent})"


class UserRewardPoint(models.Model):
    """Müşteri PazarPuan bakiyesi (1 PazarPuan = 1 TL İndirim)."""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='reward_points')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name="PazarPuan Bakiyesi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PazarPuan: {self.user.username} ({self.balance} Puan)"


class RewardTransaction(models.Model):
    """PazarPuan kazanım ve harcama işlem geçmişi."""
    TRANSACTION_TYPES = (
        ('EARNED', 'Kazanılan Puan'),
        ('SPENT', 'Harcanan Puan'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reward_transactions')
    points = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Puan Miktarı")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default='EARNED')
    description = models.CharField(max_length=255, verbose_name="Açıklama")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_transaction_type_display()}: {self.points} Puan"


# ==============================================================================
# 5. SECOND-HAND MARKETPLACE & BIDDING MODULE (Dolap / Sahibinden İlan ve Teklif)
# ==============================================================================

class SecondHandItem(models.Model):
    CONDITION_CHOICES = (
        ('NEW_LIKE', 'Sıfır Gibi (Etiketli)'),
        ('GOOD', 'Az Kullanılmış (Temiz)'),
        ('FAIR', 'Kullanılmış (Makul)'),
    )
    seller_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='second_hand_items', verbose_name="Satıcı Kullanıcı")
    title = models.CharField(max_length=200, verbose_name="İlan Başlığı")
    description = models.TextField(verbose_name="İlan Açıklaması")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Satış Fiyatı")
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='GOOD', verbose_name="Ürün Durumu")
    image = models.ImageField(upload_to='second_hand/', blank=True, null=True, verbose_name="İlan Görseli")
    is_sold = models.BooleanField(default=False, verbose_name="Satıldı mı?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[İkinci El] {self.title} - {self.price} TL ({self.seller_user.username})"


class ProductOffer(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Yanıt Bekliyor'),
        ('ACCEPTED', 'Kabul Edildi'),
        ('REJECTED', 'Reddedildi'),
        ('CANCELLED', 'İptal Edildi'),
    )
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='submitted_offers', verbose_name="Teklif Veren Alıcı")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='offers', verbose_name="Sıfır Ürün")
    second_hand_item = models.ForeignKey(SecondHandItem, on_delete=models.CASCADE, null=True, blank=True, related_name='offers', verbose_name="İkinci El İlan")
    offered_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Teklif Edilen Fiyat")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Teklif Durumu")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        target = self.product.title if self.product else (self.second_hand_item.title if self.second_hand_item else "Ürün")
        return f"Teklif: {self.buyer.username} -> {target} ({self.offered_price} TL) [{self.get_status_display()}]"


class UserAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(max_length=50, verbose_name="Adres Başlığı (Ev, İş vb.)")
    full_name = models.CharField(max_length=100, verbose_name="Ad Soyad")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    city = models.CharField(max_length=50, verbose_name="İl")
    district = models.CharField(max_length=50, verbose_name="İlçe")
    address_text = models.TextField(verbose_name="Açık Adres")
    is_default = models.BooleanField(default=False, verbose_name="Varsayılan Adres mi?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.full_name} ({self.city}/{self.district})"


# ==============================================================================
# 6. RETURN MANAGEMENT, USER WALLET, INVENTORY AUDIT & SEARCH ANALYTICS
# ==============================================================================

class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='wallet', verbose_name="Kullanıcı")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Cüzdan Bakiyesi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def deposit(self, amount, description="Bakiye Yükleme"):
        if amount > 0:
            self.balance += Decimal(str(amount))
            self.save()
            WalletTransaction.objects.create(
                wallet=self,
                amount=Decimal(str(amount)),
                transaction_type='CREDIT',
                description=description
            )
            return True
        return False

    def withdraw(self, amount, description="Harcama"):
        amount_dec = Decimal(str(amount))
        if 0 < amount_dec <= self.balance:
            self.balance -= amount_dec
            self.save()
            WalletTransaction.objects.create(
                wallet=self,
                amount=amount_dec,
                transaction_type='DEBIT',
                description=description
            )
            return True
        return False

    def __str__(self):
        return f"{self.user.username} Cüzdanı ({self.balance} TL)"


class WalletTransaction(models.Model):
    TYPE_CHOICES = (
        ('CREDIT', 'Para Girişi (Kredi)'),
        ('DEBIT', 'Para Çıkışı (Harcama)'),
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Tutar")
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="İşlem Tipi")
    description = models.CharField(max_length=255, verbose_name="Açıklama")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_transaction_type_display()}] {self.amount} TL - {self.description}"


class InventoryLog(models.Model):
    variation = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='inventory_logs', verbose_name="Ürün Varyasyonu")
    change_amount = models.IntegerField(verbose_name="Değişim Miktarı (+ / -)")
    previous_stock = models.IntegerField(verbose_name="Önceki Stok")
    new_stock = models.IntegerField(verbose_name="Yeni Stok")
    reason = models.CharField(max_length=200, verbose_name="Değişim Nedeni")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.variation.product.title} ({self.variation.color}/{self.variation.size}): {self.change_amount} -> Yeni Stok: {self.new_stock}"



class SearchQueryLog(models.Model):
    query = models.CharField(max_length=150, unique=True, verbose_name="Arama Kelimesi")
    count = models.PositiveIntegerField(default=1, verbose_name="Aranma Sayısı")
    last_searched_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-count', '-last_searched_at']

    def __str__(self):
        return f"{self.query} ({self.count} kez arandı)"


class UserLoyalty(models.Model):
    TIER_CHOICES = (
        ('BRONZE', 'Bronz Üye'),
        ('SILVER', 'Gümüş Üye'),
        ('GOLD', 'Altın Üye'),
        ('PLATINUM', 'Platin VIP Üye'),
    )
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='loyalty')
    points = models.PositiveIntegerField(default=0, verbose_name="PazarPuan")
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Toplam Harcama")
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='BRONZE', verbose_name="Üyelik Seviyesi")
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_tier(self):
        if self.points >= 5000:
            self.tier = 'PLATINUM'
        elif self.points >= 2000:
            self.tier = 'GOLD'
        elif self.points >= 500:
            self.tier = 'SILVER'
        else:
            self.tier = 'BRONZE'
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.get_tier_display()} ({self.points} Puan)"











