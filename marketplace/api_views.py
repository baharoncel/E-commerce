import json
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import authenticate
from django.db import transaction
from marketplace.models import (
    CustomUser, SellerProfile, Category, Product, ProductVariant,
    Order, SubOrder, OrderItem, Favorite, Notification, PushDeviceToken, ProductReview
)
from marketplace.jwt_helper import generate_jwt_token, decode_jwt_token, generate_refresh_token, refresh_access_token
from marketplace.services.payment_service import PaymentGatewayFactory
from marketplace.services.notification_service import NotificationService


def jwt_required(view_func):
    """
    Decorator for views that requires a valid JWT token in Authorization header.
    """
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authorization header missing or invalid format. Use Bearer <token>.'}, status=401)
        
        token = auth_header.split(' ')[1]
        payload = decode_jwt_token(token)
        if not payload:
            return JsonResponse({'error': 'Token is invalid or expired.'}, status=401)
        
        try:
            request.user = CustomUser.objects.get(id=payload['user_id'])
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=401)
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@csrf_exempt
@require_POST
def api_register_view(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'CUSTOMER')
        
        if not username or not email or not password:
            return JsonResponse({'error': 'username, email, password are required.'}, status=400)
            
        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists.'}, status=400)
            
        with transaction.atomic():
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role
            )
            
            if role == 'SELLER':
                store_name = data.get('store_name')
                iban = data.get('iban')
                commission_rate = data.get('commission_rate', '10.0')
                if not store_name or not iban:
                    raise ValueError('store_name and iban are required for sellers.')
                    
                SellerProfile.objects.create(
                    user=user,
                    store_name=store_name,
                    iban=iban,
                    commission_rate=Decimal(commission_rate)
                )
                
        token = generate_jwt_token(user)
        refresh_token = generate_refresh_token(user)
        return JsonResponse({
            'message': 'User registered successfully.',
            'token': token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_POST
def api_login_view(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'username and password are required.'}, status=400)
            
        user = authenticate(username=username, password=password)
        if user is not None:
            token = generate_jwt_token(user)
            refresh_token = generate_refresh_token(user)
            return JsonResponse({
                'message': 'Login successful.',
                'token': token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                }
            })
        else:
            return JsonResponse({'error': 'Invalid username or password.'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_POST
def api_refresh_token_view(request):
    try:
        data = json.loads(request.body)
        refresh_token = data.get('refresh_token')
        if not refresh_token:
            return JsonResponse({'error': 'refresh_token is required.'}, status=400)
            
        new_token = refresh_access_token(refresh_token)
        if not new_token:
            return JsonResponse({'error': 'Invalid or expired refresh token.'}, status=401)
            
        return JsonResponse({'token': new_token})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_GET
@jwt_required
def api_profile_view(request):
    user = request.user
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role
    }
    if user.role == 'SELLER' and hasattr(user, 'seller_profile'):
        profile = user.seller_profile
        user_data['store_name'] = profile.store_name
        user_data['iban'] = profile.iban
        user_data['commission_rate'] = float(profile.commission_rate)
        user_data['is_approved'] = profile.is_approved
        
    return JsonResponse({'user': user_data})

@csrf_exempt
@require_GET
def api_products_view(request):
    products = Product.objects.all().select_related('seller', 'category')
    data = []
    for p in products:
        data.append({
            'id': p.id,
            'title': p.title,
            'price': float(p.base_price),
            'image': p.image_url if p.image else '',
            'seller': p.seller.store_name,
            'category': p.category.name
        })
    return JsonResponse({'products': data})

@csrf_exempt
@require_POST
@jwt_required
def api_cart_checkout(request):
    """
    Handles checkout via API using a list of cart items passed in the request body.
    Supports dynamic split-ordering logic based on different sellers.
    """
    try:
        if request.user.role == 'SELLER':
            return JsonResponse({'error': 'Seller accounts cannot place orders.'}, status=403)
            
        data = json.loads(request.body)
        items = data.get('items', [])
        card_number = data.get('card_number')
        card_holder = data.get('card_holder')
        
        if not items:
            return JsonResponse({'error': 'Cart is empty.'}, status=400)
        if not card_number or not card_holder:
            return JsonResponse({'error': 'Payment credentials are required.'}, status=400)
            
        # Resolve cart items details from variants
        cart_items = []
        subtotal = Decimal("0.00")
        
        for item in items:
            variant_id = item.get('variant_id')
            quantity = int(item.get('quantity', 1))
            variant = ProductVariant.objects.select_related('product', 'product__seller').get(id=variant_id)
            
            unit_price = variant.get_price()
            total_price = unit_price * quantity
            subtotal += total_price
            
            cart_items.append({
                'variant': variant,
                'product': variant.product,
                'quantity': quantity,
                'price': unit_price,
                'total_price': total_price
            })
            
        gateway = PaymentGatewayFactory.get_gateway()
        response = gateway.process_payment(
            customer=request.user,
            cart_items=cart_items,
            card_number=card_number,
            card_holder_name=card_holder
        )
        
        if response['status'] == 'FAILED':
            return JsonResponse({'error': response['error_message']}, status=400)
            
        created_sub_orders = []
        with transaction.atomic():
            parent_order = Order.objects.create(
                customer=request.user,
                total_amount=subtotal,
                payment_status='PAID',
                payment_id=response['payment_id']
            )
            
            seller_items = {}
            for item in cart_items:
                seller_id = item['product'].seller.id
                if seller_id not in seller_items:
                    seller_items[seller_id] = []
                seller_items[seller_id].append(item)
                
            for breakdown_item in response['breakdown']:
                seller_id = breakdown_item['seller_id']
                seller = SellerProfile.objects.get(id=seller_id)
                
                sub_order = SubOrder.objects.create(
                    parent_order=parent_order,
                    seller=seller,
                    subtotal=breakdown_item['subtotal'],
                    commission_fee=breakdown_item['commission_fee'],
                    seller_payout=breakdown_item['seller_payout']
                )
                created_sub_orders.append(sub_order)
                
                for item in seller_items[seller_id]:
                    variant = item['variant']
                    qty = item['quantity']
                    
                    if variant.stock < qty:
                        raise ValueError(f"{variant.product.title} has insufficient stock.")
                        
                    variant.stock -= qty
                    variant.save()
                    
                    OrderItem.objects.create(
                        sub_order=sub_order,
                        product=item['product'],
                        variant=variant,
                        quantity=qty,
                        price=item['price']
                    )

        # Trigger Notifications
        NotificationService.send_order_confirmation(parent_order)
        for sub_order in created_sub_orders:
            NotificationService.send_seller_new_order_alert(sub_order)

        return JsonResponse({
            'message': 'Order processed successfully.',
            'order_id': parent_order.id,
            'payment_id': response['payment_id'],
            'total_amount': float(subtotal)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_POST
@jwt_required
def api_toggle_favorite(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        product = Product.objects.get(id=product_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
        if not created:
            favorite.delete()
            return JsonResponse({'favorited': False, 'message': 'Product removed from favorites.'})
        return JsonResponse({'favorited': True, 'message': 'Product added to favorites.'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_POST
@jwt_required
def api_register_device_token(request):
    """Mobil uygulama Cihaz Push Notification Token (FCM / APNS) kaydı."""
    try:
        data = json.loads(request.body)
        token = data.get('token')
        device_type = data.get('device_type', 'ANDROID').upper()

        if not token:
            return JsonResponse({'error': 'Device push token is required.'}, status=400)

        push_token, created = PushDeviceToken.objects.get_or_create(
            token=token,
            defaults={'user': request.user, 'device_type': device_type}
        )
        if not created and push_token.user != request.user:
            push_token.user = request.user
            push_token.device_type = device_type
            push_token.save()

        return JsonResponse({'message': 'Push device token registered successfully.', 'device_type': device_type})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_GET
def api_categories_view(request):
    """Mobil uygulamalar için hiyerarşik kategori ağacı API uç noktası."""
    main_categories = Category.objects.filter(parent=None).prefetch_related('subcategories')
    data = []
    for cat in main_categories:
        subcats = [{'id': sub.id, 'name': sub.name, 'slug': sub.slug} for sub in cat.subcategories.all()]
        data.append({
            'id': cat.id,
            'name': cat.name,
            'slug': cat.slug,
            'subcategories': subcats
        })
    return JsonResponse({'categories': data})


@csrf_exempt
@require_GET
def api_product_detail_view(request, product_id):
    """Mobil uygulamalar için detaylı ürün ve renk/beden varyasyon API'si."""
    try:
        product = Product.objects.select_related('seller', 'category').prefetch_related('variants', 'reviews').get(id=product_id)
        variants = []
        for v in product.variants.all():
            variants.append({
                'id': v.id,
                'color': v.color or '',
                'size': v.size or (str(v.size_number) if v.size_number else ''),
                'price': float(v.get_price()),
                'stock': v.stock,
                'sku': v.sku
            })

        reviews = []
        for r in product.reviews.filter(is_approved=True):
            reviews.append({
                'id': r.id,
                'user': r.user.username,
                'rating': r.rating,
                'comment': r.comment,
                'created_at': r.created_at.strftime('%Y-%m-%d %H:%M')
            })

        return JsonResponse({
            'id': product.id,
            'title': product.title,
            'description': product.description,
            'base_price': float(product.base_price),
            'image_url': product.image_url,
            'average_rating': float(product.average_rating),
            'review_count': product.review_count,
            'seller': {
                'id': product.seller.id,
                'store_name': product.seller.store_name
            },
            'category': {
                'id': product.category.id if product.category else None,
                'name': product.category.name if product.category else ''
            },
            'variants': variants,
            'reviews': reviews
        })
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found.'}, status=404)


@csrf_exempt
@require_GET
@jwt_required
def api_customer_orders_view(request):
    """Müşterinin geçmiş siparişleri ve canlı kargo takip bilgileri API'si."""
    orders = Order.objects.filter(customer=request.user).prefetch_related('sub_orders', 'sub_orders__items', 'sub_orders__seller').order_by('-created_at')
    orders_data = []
    for order in orders:
        sub_orders_data = []
        for sub in order.sub_orders.all():
            items_data = []
            for item in sub.items.all():
                items_data.append({
                    'id': item.id,
                    'product_title': item.product.title,
                    'quantity': item.quantity,
                    'price': float(item.price),
                    'total_price': float(item.get_total_item_price())
                })
            sub_orders_data.append({
                'id': sub.id,
                'seller_store': sub.seller.store_name,
                'subtotal': float(sub.subtotal),
                'status': sub.status,
                'status_display': sub.get_status_display(),
                'items': items_data
            })

        orders_data.append({
            'id': order.id,
            'total_amount': float(order.total_amount),
            'payment_status': order.payment_status,
            'order_status': order.order_status,
            'order_status_display': order.get_order_status_display(),
            'tracking_number': order.tracking_number or '',
            'shipping_company': order.shipping_company or '',
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
            'sub_orders': sub_orders_data
        })
    return JsonResponse({'orders': orders_data})


@csrf_exempt
@require_GET
@jwt_required
def api_seller_dashboard_view(request):
    """Mobil satıcı uygulaması için ciro, stok ve sipariş metrikleri API'si."""
    if not request.user.is_seller():
        return JsonResponse({'error': 'Access denied. Seller account required.'}, status=403)

    seller = request.user.seller_profile
    sub_orders = SubOrder.objects.filter(seller=seller).select_related('parent_order')

    total_sales = sum(so.subtotal for so in sub_orders if so.parent_order.payment_status == 'PAID')
    total_payout = sum(so.seller_payout for so in sub_orders if so.parent_order.payment_status == 'PAID')
    total_commission = sum(so.commission_fee for so in sub_orders if so.parent_order.payment_status == 'PAID')
    pending_orders_count = sub_orders.filter(status='PENDING').count()

    products_count = Product.objects.filter(seller=seller).count()

    return JsonResponse({
        'store_name': seller.store_name,
        'commission_rate': float(seller.commission_rate),
        'is_approved': seller.is_approved,
        'metrics': {
            'total_sales': float(total_sales),
            'total_payout': float(total_payout),
            'total_commission': float(total_commission),
            'pending_orders_count': pending_orders_count,
            'products_count': products_count
        }
    })


@csrf_exempt
@require_GET
@jwt_required
def api_seller_analytics_view(request):
    """Gelişmiş Satıcı Analitik API'si (Analitik Servisi Entegrasyonu)."""
    if not request.user.is_seller():
        return JsonResponse({'error': 'Access denied. Seller account required.'}, status=403)

    days_str = request.GET.get('days', '30')
    try:
        days = int(days_str)
    except ValueError:
        days = 30

    from marketplace.services.analytics_service import AnalyticsService
    service = AnalyticsService()
    analytics_data = service.get_seller_analytics(request.user.seller_profile, days=days)

    return JsonResponse({'status': 'success', 'data': analytics_data})


@csrf_exempt
@require_GET
@jwt_required
def api_superadmin_analytics_view(request):
    """Platform SuperAdmin Analitik API'si (Analitik Servisi Entegrasyonu)."""
    if not request.user.is_superadmin():
        return JsonResponse({'error': 'Access denied. SuperAdmin privileges required.'}, status=403)

    days_str = request.GET.get('days', '30')
    try:
        days = int(days_str)
    except ValueError:
        days = 30

    from marketplace.services.analytics_service import AnalyticsService
    service = AnalyticsService()
    analytics_data = service.get_superadmin_analytics(days=days)

    return JsonResponse({'status': 'success', 'data': analytics_data})


# ==============================================================================
# NEW MODULE API ENDPOINTS (RMA, WALLET, SEARCH AUTOCOMPLETE, SELLER BADGES)
# ==============================================================================

@csrf_exempt
@require_GET
def api_search_autocomplete_view(request):
    """Canlı Arama Otomatik Tamamlama & Trend Arama API'si."""
    query = request.GET.get('q', '').strip()
    from marketplace.services.search_analytics_service import SearchAnalyticsService
    
    if query:
        SearchAnalyticsService.log_search_query(query)
        suggestions = SearchAnalyticsService.get_autocomplete_suggestions(query)
        return JsonResponse({'query': query, 'suggestions': suggestions})
    else:
        trending = list(SearchAnalyticsService.get_trending_searches().values('query', 'count'))
        return JsonResponse({'trending_searches': trending})


@csrf_exempt
@require_GET
@jwt_required
def api_user_wallet_view(request):
    """Kullanıcı Cüzdan Bakiyesi ve İşlem Geçmişi API'si."""
    from marketplace.services.wallet_service import WalletService
    wallet = WalletService.get_or_create_wallet(request.user)
    transactions = WalletService.get_transaction_history(request.user)
    
    tx_list = [
        {
            'id': tx.id,
            'amount': float(tx.amount),
            'type': tx.transaction_type,
            'description': tx.description,
            'created_at': tx.created_at.strftime('%Y-%m-%d %H:%M')
        }
        for tx in transactions
    ]
    return JsonResponse({
        'balance': float(wallet.balance),
        'transactions': tx_list
    })


@csrf_exempt
@require_POST
@jwt_required
def api_create_return_request_view(request):
    """Müşteri İade Talebi Oluşturma API'si."""
    try:
        data = json.loads(request.body)
        sub_order_id = data.get('sub_order_id')
        reason = data.get('reason')

        if not sub_order_id or not reason:
            return JsonResponse({'error': 'sub_order_id ve reason zorunludur.'}, status=400)

        sub_order = SubOrder.objects.get(id=sub_order_id)
        from marketplace.services.return_service import ReturnService
        ret_req = ReturnService.create_return_request(sub_order, request.user, reason)

        return JsonResponse({
            'message': 'İade talebiniz başarıyla oluşturuldu.',
            'return_request_id': ret_req.id,
            'status': ret_req.status,
            'refund_amount': float(ret_req.refund_amount)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_GET
def api_seller_performance_view(request, seller_id):
    """Satıcı Performansı & Başarı Rozetleri API'si."""
    try:
        seller_profile = SellerProfile.objects.get(id=seller_id)
        from marketplace.services.seller_performance_service import SellerPerformanceService
        metrics = SellerPerformanceService.calculate_seller_metrics(seller_profile)
        return JsonResponse(metrics)
    except SellerProfile.DoesNotExist:
        return JsonResponse({'error': 'Satıcı bulunamadı.'}, status=404)


@csrf_exempt
@require_POST
def api_ai_assistant_view(request):
    """PazarAsistan AI Chatbot Akıllı Yanıt API'si."""
    try:
        data = json.loads(request.body)
        query = data.get('query', '')
        from marketplace.services.ai_shopping_assistant_service import ask_shopping_assistant
        res = ask_shopping_assistant(query, request.user if request.user.is_authenticated else None)
        return JsonResponse(res)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_GET
def api_cargo_tracking_view(request, order_id):
    """Canlı Kargo Takip Çizelgesi API'si."""
    try:
        order = Order.objects.get(id=order_id)
        from marketplace.services.cargo_tracking_service import get_order_tracking_timeline
        data = get_order_tracking_timeline(order)
        return JsonResponse(data)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Sipariş bulunamadı.'}, status=404)


@csrf_exempt
@require_POST
def api_add_outfit_to_cart_view(request):
    """Tüm AI Kombin Ürünlerini Tek Tıkla Sepete Ekleme API'si."""
    try:
        data = json.loads(request.body)
        product_ids = data.get('product_ids', [])
        cart, _ = Cart.objects.get_or_create(user=request.user if request.user.is_authenticated else None)
        
        added_count = 0
        for pid in product_ids:
            try:
                prod = Product.objects.get(id=pid)
                var = prod.variants.first()
                if var:
                    item, created = CartItem.objects.get_or_create(cart=cart, variant=var)
                    if not created:
                        item.quantity += 1
                        item.save()
                    added_count += 1
            except Product.DoesNotExist:
                continue

        return JsonResponse({'status': 'success', 'message': f'{added_count} kombin ürünü sepetinize eklendi!', 'cart_count': cart.total_items()})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
