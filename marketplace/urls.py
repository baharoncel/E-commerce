from django.urls import path
from marketplace import views, api_views

urlpatterns = [
    # Storefront (Müşteri Mağaza)
    path('', views.store_index, name='store_index'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/review/', views.product_detail, name='submit_review'),
    
    # Cart (Sepet)
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/apply-coupon/', views.apply_coupon, name='apply_coupon'),
    
    # Checkout & Payment (Ödeme ve Sipariş)
    path('checkout/', views.checkout_view, name='checkout_view'),
    path('checkout/success/', views.checkout_success_view, name='checkout_success'),
    path('payment/webhook/', views.payment_webhook_view, name='payment_webhook'),
    
    # Membership (Üyelik)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Expanded Client Features (Hesabım, Favori, İade, Mesajlaşma, Adresler)
    path('account/', views.account_view, name='account'),
    path('account/address/add/', views.add_user_address_view, name='add_user_address'),
    path('account/address/<int:address_id>/delete/', views.delete_user_address_view, name='delete_user_address'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('favorites/toggle/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('returns/request/<int:order_item_id>/', views.request_return_view, name='request_return'),
    path('messages/send/', views.send_chat_message, name='send_chat_message'),
    path('messages/poll/<int:contact_id>/', views.poll_chat_messages, name='poll_chat_messages'),
    
    # Seller Dashboard (Satıcı Paneli)
    path('seller/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/add-product/', views.seller_add_product, name='seller_add_product'),
    path('seller/coupons/create/', views.seller_create_coupon, name='seller_create_coupon'),
    path('seller/order/<int:suborder_id>/update-status/', views.update_suborder_status, name='update_suborder_status'),
    path('seller/returns/<int:return_id>/handle/', views.seller_handle_return, name='seller_handle_return'),
    path('seller/review/<int:review_id>/handle/', views.seller_handle_review, name='seller_handle_review'),
    
    # REST API & JWT Endpoints & Interactive Docs
    path('api/docs/', views.api_docs_view, name='api_docs'),
    path('api/auth/register/', api_views.api_register_view, name='api_register'),
    path('api/auth/login/', api_views.api_login_view, name='api_login'),
    path('api/auth/token/refresh/', api_views.api_refresh_token_view, name='api_refresh_token'),
    path('api/auth/profile/', api_views.api_profile_view, name='api_profile'),
    path('api/notifications/register-device/', api_views.api_register_device_token, name='api_register_device_token'),
    path('api/notifications/poll/', views.poll_user_notifications, name='poll_user_notifications'),
    path('api/notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('api/spin-wheel/', views.spin_wheel_api, name='spin_wheel_api'),
    path('cart/apply-points/', views.apply_points_cart, name='apply_points_cart'),
    path('seller/export-orders-csv/', views.seller_export_orders_csv, name='seller_export_orders_csv'),
    path('admin-dashboard/export-platform-csv/', views.admin_export_platform_csv, name='admin_export_platform_csv'),
    path('order/<int:order_id>/invoice/', views.generate_order_invoice, name='generate_order_invoice'),
    path('order/<int:order_id>/invoice/pdf/', views.generate_order_pdf_invoice, name='generate_order_pdf_invoice'),
    path('compare/', views.compare_products_view, name='compare_products'),
    path('api/reviews/<int:review_id>/helpful/', views.toggle_review_helpful, name='toggle_review_helpful'),
    path('api/chat/poll/', views.poll_widget_chat_messages, name='poll_widget_chat_messages'),
    path('api/chat/send/', views.send_chat_message_api, name='send_chat_message_api'),
    path('api/categories/', api_views.api_categories_view, name='api_categories'),
    path('api/products/', api_views.api_products_view, name='api_products'),
    path('api/products/<int:product_id>/', api_views.api_product_detail_view, name='api_product_detail'),
    path('api/cart/checkout/', api_views.api_cart_checkout, name='api_cart_checkout'),
    path('api/favorites/toggle/', api_views.api_toggle_favorite, name='api_toggle_favorite'),
    path('api/orders/', api_views.api_customer_orders_view, name='api_customer_orders'),
    path('api/seller/dashboard/', api_views.api_seller_dashboard_view, name='api_seller_dashboard'),
    path('api/analytics/seller/', api_views.api_seller_analytics_view, name='api_seller_analytics'),
    path('api/analytics/superadmin/', api_views.api_superadmin_analytics_view, name='api_superadmin_analytics'),

    
    # Currency Selector & Autocomplete Search API
    path('set-currency/', views.set_currency, name='set_currency'),
    path('api/search-autocomplete/', views.search_autocomplete, name='search_autocomplete'),
    
    # Superadmin Dashboard (Platform Yönetici Paneli)
    path('admin-dashboard/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('admin-dashboard/seller/<int:seller_id>/toggle-approval/', views.admin_toggle_seller_approval, name='admin_toggle_seller_approval'),
    path('admin-dashboard/seller/<int:seller_id>/update-commission/', views.admin_update_commission_rate, name='admin_update_commission_rate'),
    path('admin-dashboard/category/create/', views.admin_create_category, name='admin_create_category'),
    path('admin-dashboard/category/<int:category_id>/delete/', views.admin_delete_category, name='admin_delete_category'),
    path('admin-dashboard/coupon/create/', views.admin_create_platform_coupon, name='admin_create_platform_coupon'),

    # Second-Hand Marketplace & Bidding (Dolap / Sahibinden İlan ve Teklif)
    path('second-hand/', views.second_hand_list_view, name='second_hand_list'),
    path('second-hand/create/', views.second_hand_create_view, name='second_hand_create'),
    path('offers/', views.my_offers_view, name='my_offers'),
    path('offers/submit/', views.submit_offer_view, name='submit_offer'),
    path('offers/<int:offer_id>/respond/', views.respond_offer_view, name='respond_offer'),

    # OAuth2, SMS OTP Login & Shipping Barcode Services
    path('auth/send-otp/', views.send_phone_otp_view, name='send_phone_otp'),
    path('auth/verify-otp/', views.verify_phone_otp_view, name='verify_phone_otp'),
    path('auth/google-login/', views.google_oauth2_login_view, name='google_oauth2_login'),
    path('shipping/track/<int:suborder_id>/', views.track_shipping_view, name='track_shipping'),
    path('seller/suborder/<int:suborder_id>/shipping-label/', views.generate_shipping_label_view, name='generate_shipping_label'),

    # Enterprise AI Content Generator & B2B Wholesale Pricing
    path('api/ai/generate-description/', views.api_generate_ai_description_view, name='api_generate_ai_description'),
    path('api/b2b/wholesale-pricing/', views.api_b2b_wholesale_pricing_view, name='api_b2b_wholesale_pricing'),

    # Payout Statement PDF & CSV Bulk Import
    path('seller/payout-statement/pdf/', views.generate_seller_payout_pdf, name='generate_seller_payout_pdf'),
    path('seller/bulk-import/', views.seller_bulk_import_products, name='seller_bulk_import_products'),
    path('seller/download-template/', views.seller_download_import_template, name='seller_download_import_template'),

    # New Enterprise API Endpoints (RMA, Wallet, Autocomplete, Seller Performance Badges, AI Assistant, Cargo, Outfit)
    path('api/v2/search-autocomplete/', api_views.api_search_autocomplete_view, name='api_v2_search_autocomplete'),
    path('api/wallet/', api_views.api_user_wallet_view, name='api_user_wallet'),
    path('api/returns/create/', api_views.api_create_return_request_view, name='api_create_return_request'),
    path('api/seller/<int:seller_id>/performance/', api_views.api_seller_performance_view, name='api_seller_performance'),
    path('api/ai-assistant/', api_views.api_ai_assistant_view, name='api_ai_assistant'),
    path('api/cargo-tracking/<int:order_id>/', api_views.api_cargo_tracking_view, name='api_cargo_tracking'),
    path('api/outfit/add-to-cart/', api_views.api_add_outfit_to_cart_view, name='api_add_outfit_to_cart'),
]




