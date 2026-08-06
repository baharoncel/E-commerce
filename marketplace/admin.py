from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from marketplace.models import CustomUser, SellerProfile, Category, Product, ProductVariant, Order, SubOrder, OrderItem

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Platform Rolü', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Platform Rolü', {'fields': ('role',)}),
    )

class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'user', 'commission_rate', 'iban', 'is_approved']
    list_filter = ['is_approved']
    search_fields = ['store_name', 'user__username', 'iban']

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'category', 'base_price', 'created_at']
    list_filter = ['category', 'seller']
    search_fields = ['title', 'description']
    inlines = [ProductVariantInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class SubOrderInline(admin.TabularInline):
    model = SubOrder
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'total_amount', 'payment_status', 'payment_id', 'created_at']
    list_filter = ['payment_status', 'created_at']
    search_fields = ['customer__username', 'payment_id']
    inlines = [SubOrderInline]

class SubOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'parent_order', 'seller', 'subtotal', 'commission_fee', 'seller_payout', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'seller']
    search_fields = ['parent_order__id', 'seller__store_name']
    inlines = [OrderItemInline]

# Admin sitesine kaydet
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SellerProfile, SellerProfileAdmin)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariant)
admin.site.register(Order, OrderAdmin)
admin.site.register(SubOrder, SubOrderAdmin)
admin.site.register(OrderItem)
