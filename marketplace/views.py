import json
import datetime
from decimal import Decimal
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from marketplace.models import (
    CustomUser, SellerProfile, Category, Product, ProductVariant, 
    Order, SubOrder, OrderItem, Favorite, ReturnRequest, ChatMessage, Notification, ProductReview, Coupon, FlashSale,
    UserRewardPoint, RewardTransaction
)

from marketplace.payment_gateway import IyzicoMarketplaceSimulator
from marketplace.services.coupon_service import CouponService
from marketplace.services.product_filter_dto import ProductFilterDto
from marketplace.services.product_service import ProductService
from marketplace.services.review_service import ReviewService
from marketplace.services.payment_service import PaymentGatewayFactory
from marketplace.services.notification_service import NotificationService
from marketplace.services.recommendation_service import RecommendationService
from marketplace.services.reward_service import RewardService
from marketplace.services.currency_service import CurrencyService




# ==============================================================================
# 1. MEMBERSHIP & AUTHENTICATION VIEWS
# ==============================================================================

def register_view(request):
    if request.user.is_authenticated:
        return redirect('store_index')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role', 'CUSTOMER')

        if password != confirm_password:
            messages.error(request, "Şifreler uyuşmuyor!")
            return render(request, 'auth/register.html')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Bu kullanıcı adı zaten alınmış!")
            return render(request, 'auth/register.html')

        try:
            with transaction.atomic():
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=role
                )

                if role == 'SELLER':
                    store_name = request.POST.get('store_name')
                    iban = request.POST.get('iban')
                    commission_rate = request.POST.get('commission_rate', '10.00')

                    if not store_name or not iban:
                        raise ValueError("Satıcılar için Mağaza Adı ve IBAN zorunludur!")

                    SellerProfile.objects.create(
                        user=user,
                        store_name=store_name,
                        iban=iban,
                        commission_rate=Decimal(commission_rate)
                    )

                login(request, user)
                messages.success(request, f"Başarıyla kayıt oldunuz. Hoş geldiniz, {user.username}!")
                
                if user.is_seller():
                    return redirect('seller_dashboard')
                return redirect('store_index')

        except Exception as e:
            messages.error(request, f"Kayıt sırasında hata oluştu: {str(e)}")
            return render(request, 'auth/register.html')

    return render(request, 'auth/register.html')


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_seller():
            return redirect('seller_dashboard')
        return redirect('store_index')

    if request.method == 'POST':
        login_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        user = authenticate(request, username=login_input, password=password)
        if user is None and '@' in login_input:
            user_obj = CustomUser.objects.filter(email__iexact=login_input).first()
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Tekrar hoş geldiniz, {user.username}!")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url and next_url != '/logout/':
                return redirect(next_url)
            if user.is_seller():
                return redirect('seller_dashboard')
            return redirect('store_index')

        else:
            messages.error(request, "Geçersiz kullanıcı adı/e-posta veya şifre!")

    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "Başarıyla çıkış yaptınız.")
    return redirect('store_index')


# ==============================================================================
# 2. STOREFRONT & CATALOG VIEWS (Müşteri Mağaza Sayfaları)
# ==============================================================================

def store_index(request):
    """Ana sayfa. Kategorileri hiyerarşik (ana/alt) olarak listeler ve gelişmiş filtreleme sağlar."""
    categories = Category.objects.filter(parent=None).prefetch_related('subcategories')
    sellers = SellerProfile.objects.filter(is_approved=True)

    # Mevcut tüm renkler ve bedenler/numaralar (Varyasyonlardan)
    available_colors = list(ProductVariant.objects.exclude(color=None).exclude(color='').values_list('color', flat=True).distinct().order_by('color'))
    available_sizes_raw = list(ProductVariant.objects.exclude(size=None).exclude(size='').values_list('size', flat=True).distinct())
    available_size_numbers_raw = list(ProductVariant.objects.exclude(size_number=None).values_list('size_number', flat=True).distinct())
    
    available_sizes = available_sizes_raw + [str(num) for num in available_size_numbers_raw if num is not None]
    available_sizes = sorted(list(set(available_sizes)))

    selected_category_slug = request.GET.get('category')
    seller_id = request.GET.get('seller') or request.GET.get('seller_id')
    search_query = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    min_rating = request.GET.get('min_rating')
    sort_by = request.GET.get('sort_by')
    
    selected_colors = [c for c in request.GET.getlist('colors') if c]
    selected_sizes = [s for s in request.GET.getlist('sizes') if s]
    in_stock_only = request.GET.get('in_stock') in ['1', 'true']
    discounted_only = request.GET.get('discounted') in ['1', 'true']
    
    category_ids = []
    req_category_ids = request.GET.getlist('category_ids')
    if req_category_ids:
        for cid in req_category_ids:
            if cid:
                try:
                    category_ids.append(int(cid))
                except ValueError:
                    pass

    selected_category = None
    if selected_category_slug and not category_ids:
        selected_category = Category.objects.filter(slug=selected_category_slug).first()
        if selected_category:
            def get_descendant_ids(cat):
                ids = [cat.id]
                for child in cat.subcategories.all():
                    ids.extend(get_descendant_ids(child))
                return ids
            category_ids = get_descendant_ids(selected_category)

    filter_dto = ProductFilterDto(
        search_term=search_query,
        category_ids=category_ids or None,
        min_price=Decimal(min_price) if min_price else None,
        max_price=Decimal(max_price) if max_price else None,
        seller_id=int(seller_id) if seller_id else None,
        min_rating=Decimal(min_rating) if min_rating else None,
        sort_by=sort_by,
        colors=selected_colors or None,
        sizes=selected_sizes or None,
        in_stock_only=in_stock_only,
        discounted_only=discounted_only,
    )
    products = ProductService().get_products(filter_dto)
    flash_sales = FlashSale.objects.filter(is_active=True, end_time__gt=timezone.now()).select_related('product', 'product__seller')

    bubble_definitions = [
        {'name': 'Tişört', 'image': 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=300&q=80', 'query': 'Tişört'},
        {'name': 'Gömlek', 'image': 'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=300&q=80', 'query': 'Gömlek'},
        {'name': 'Bluz', 'image': 'https://images.unsplash.com/photo-1564257631407-4deb1f99d992?w=300&q=80', 'query': 'Bluz'},
        {'name': 'Pantolon', 'image': 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=300&q=80', 'query': 'Pantolon'},
        {'name': 'Jean (Kot)', 'image': 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=300&q=80', 'query': 'Jean'},
        {'name': 'Etek', 'image': 'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=300&q=80', 'query': 'Etek'},
        {'name': 'Elbise', 'image': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=300&q=80', 'query': 'Elbise'},
        {'name': 'Mont', 'image': 'https://images.unsplash.com/photo-1544923246-77307dd654cb?w=300&q=80', 'query': 'Mont'},
        {'name': 'Çanta', 'image': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=300&q=80', 'query': 'Çanta'},
        {'name': 'Saat', 'image': 'https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=300&q=80', 'query': 'Saat'},
        {'name': 'Gözlük', 'image': 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=300&q=80', 'query': 'Gözlük'},
        {'name': 'Parfüm', 'image': 'https://images.unsplash.com/photo-1541643600914-78b084683601?w=300&q=80', 'query': 'Parfüm'},
    ]

    category_bubbles = []
    for b in bubble_definitions:
        cat = Category.objects.filter(Q(name__icontains=b['query']) | Q(name__icontains=b['name'])).first()
        category_bubbles.append({
            'id': cat.id if cat else None,
            'name': b['name'],
            'image': b['image']
        })

    context = {
        'products': products,
        'products_count': products.count(),
        'flash_sales': flash_sales,
        'categories': categories,
        'category_bubbles': category_bubbles,
        'sellers': sellers,
        'available_colors': available_colors,
        'available_sizes': available_sizes,
        'selected_category': selected_category_slug,
        'selected_category_ids': category_ids,
        'selected_seller': int(seller_id) if seller_id else None,
        'selected_colors': selected_colors,
        'selected_sizes': selected_sizes,
        'in_stock_only': in_stock_only,
        'discounted_only': discounted_only,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
        'min_rating': min_rating,
        'sort_by': sort_by,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'count': products.count(),
            'html': render(request, 'storefront/partials/product_grid.html', {'products': products, 'request': request}).content.decode('utf-8')
        })
    return render(request, 'storefront/index.html', context)



def product_detail(request, product_id):
    """
    Ürün detayı ve ilgili önerilen ürünler (Recommendations).
    Müşteriye aynı kategori veya üst kategoriden 4 benzer ürünü önerir.
    """
    product = get_object_or_404(Product.objects.select_related('seller', 'category'), id=product_id)
    variants = product.variants.all()
    reviews = ProductReview.objects.filter(product=product, is_approved=True).select_related('user').order_by('-created_at')
    review_service = ReviewService()
    can_review = False
    review_error = None

    if request.user.is_authenticated:
        can_review = review_service.can_user_review_product(request.user, product)

    if request.method == 'POST' and request.user.is_authenticated:
        if 'review_submit' in request.POST:
            rating = request.POST.get('rating')
            comment = request.POST.get('comment', '').strip()
            image = request.FILES.get('review_image')
            try:
                rating_value = int(rating)
                if rating_value < 1 or rating_value > 5:
                    raise ValueError('Puan 1 ile 5 arasında olmalıdır.')
                review_service.create_review(request.user, product, rating_value, comment, image)
                messages.success(request, 'Yorumunuz başarıyla gönderildi. Onay sürecinden sonra yayınlanacaktır.')
                return redirect('product_detail', product_id=product.id)
            except (ValueError, TypeError) as exc:
                review_error = str(exc)
                messages.error(request, str(exc))


    # Akıllı Ürün Öneri Motoru: Bu Ürünü Alanlar Bunları da Aldı
    recommended_products = RecommendationService.get_frequently_bought_together(product, limit=4)

    # AI Outfit Combiner
    from marketplace.services.outfit_combiner_service import get_outfit_recommendations
    outfit_products = get_outfit_recommendations(product.id, limit=3)


    colors = sorted(list(set(v.color for v in variants if v.color)))
    sizes = sorted(list(set(v.size for v in variants if v.size)))
    size_numbers = sorted(list(set(v.size_number for v in variants if v.size_number is not None)))

    variants_data = []
    for v in variants:
        variants_data.append({
            'id': v.id,
            'color': v.color or '',
            'size': v.size or '',
            'size_number': v.size_number or '',
            'price': str(v.get_price()),
            'stock': v.stock,
            'sku': v.sku
        })

    # Favori kontrolü
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, product=product).exists()

    context = {
        'product': product,
        'variants': variants,
        'colors': colors,
        'sizes': sizes,
        'size_numbers': size_numbers,
        'variants_json': json.dumps(variants_data),
        'recommended_products': recommended_products,
        'outfit_products': outfit_products,
        'is_favorited': is_favorited,
        'reviews': reviews,
        'can_review': can_review,
        'review_error': review_error,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'id': product.id,
            'title': product.title,
            'description': product.description,
            'base_price': float(product.base_price),
            'image_url': product.image_url,
            'seller_name': product.seller.store_name,
            'variants': variants_data,
        })
    return render(request, 'storefront/detail.html', context)


# ==============================================================================
# 3. CART MANAGEMENT (Sepet Yönetimi)
# ==============================================================================

def get_cart_items_details(request):
    cart = request.session.get('cart', {})
    cart_items = []
    subtotal = Decimal("0.00")

    for variant_id_str, qty in cart.items():
        try:
            variant_id = int(variant_id_str)
            variant = ProductVariant.objects.select_related('product', 'product__seller').get(id=variant_id)
            price = variant.get_price()
            item_total = price * qty
            subtotal += item_total
            cart_items.append({
                'variant': variant,
                'product': variant.product,
                'quantity': qty,
                'price': price,
                'total_price': item_total
            })
        except ProductVariant.DoesNotExist:
            pass

    return cart_items, subtotal


def view_cart(request):
    cart_items, subtotal = get_cart_items_details(request)
    coupon_code = request.session.get('applied_coupon_code')
    coupon_service = CouponService()
    coupon_result = None
    discount_amount = Decimal('0.00')
    final_total = subtotal

    if coupon_code:
        coupon_result = coupon_service.validate_coupon(coupon_code, subtotal)
        if coupon_result.is_valid:
            discount_amount = coupon_result.discount_amount
            final_total = coupon_result.final_total
        else:
            request.session['applied_coupon_code'] = None
            request.session['coupon_error'] = coupon_result.message

    grouped_cart = {}
    for item in cart_items:
        seller = item['product'].seller
        if seller.id not in grouped_cart:
            grouped_cart[seller.id] = {
                'store_name': seller.store_name,
                'items': [],
                'seller_total': Decimal("0.00")
            }
        grouped_cart[seller.id]['items'].append(item)
        grouped_cart[seller.id]['seller_total'] += item['total_price']

    # Akıllı Sepet Öneri Motoru
    recommendations = RecommendationService.get_cart_recommendations(cart_items, limit=4)


    context = {
        'grouped_cart': grouped_cart,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'final_total': final_total,
        'applied_coupon_code': coupon_code,
        'coupon_error': request.session.pop('coupon_error', None),
        'recommended_products': recommendations,
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        items_list = []
        for seller_id, group in grouped_cart.items():
            for item in group['items']:
                items_list.append({
                    'product_title': item['product'].title,
                    'product_url': f"/product/{item['product'].id}/",
                    'image_url': item['product'].image_url,
                    'variant_id': item['variant'].id,
                    'color': item['variant'].color or '',
                    'size': item['variant'].size or '',
                    'quantity': item['quantity'],
                    'price': float(item['price']),
                    'total_price': float(item['total_price']),
                    'seller_name': group['store_name'],
                })
        return JsonResponse({
            'items': items_list,
            'subtotal': float(subtotal),
            'final_total': float(final_total),
        })
    return render(request, 'storefront/cart.html', context)


@require_POST
def add_to_cart(request):
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))

    if not variant_id:
        messages.error(request, "Lütfen ürünün varyasyonunu seçiniz!")
        return redirect(request.META.get('HTTP_REFERER', 'store_index'))

    variant = get_object_or_404(ProductVariant, id=variant_id)

    if variant.stock < quantity:
        messages.error(request, f"Yetersiz stok! En fazla {variant.stock} adet ekleyebilirsiniz.")
        return redirect(request.META.get('HTTP_REFERER', 'store_index'))

    cart = request.session.get('cart', {})
    current_qty = cart.get(str(variant_id), 0)
    new_qty = current_qty + quantity
    
    if variant.stock < new_qty:
         messages.error(request, f"Sepetinizdeki toplam adet ({new_qty}) stok sınırını ({variant.stock}) aşıyor.")
         return redirect(request.META.get('HTTP_REFERER', 'store_index'))

    cart[str(variant_id)] = new_qty
    request.session['cart'] = cart
    messages.success(request, f"{variant.product.title} sepete eklendi.")
    return redirect('view_cart')


@require_POST
def update_cart_item(request):
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))
    
    variant = get_object_or_404(ProductVariant, id=variant_id)
    cart = request.session.get('cart', {})

    if str(variant_id) in cart:
        if quantity <= 0:
            del cart[str(variant_id)]
            messages.info(request, "Ürün sepetten çıkarıldı.")
        elif variant.stock < quantity:
            messages.error(request, f"Stok sınırı aşıldı! En fazla {variant.stock} adet girebilirsiniz.")
        else:
            cart[str(variant_id)] = quantity
            messages.success(request, "Sepet güncellendi.")
            
    request.session['cart'] = cart
    return redirect('view_cart')


@require_POST
def remove_from_cart(request):
    variant_id = request.POST.get('variant_id')
    cart = request.session.get('cart', {})
    
    if str(variant_id) in cart:
        del cart[str(variant_id)]
        request.session['cart'] = cart
        messages.success(request, "Ürün sepetinizden silindi.")
        
    return redirect('view_cart')


@require_POST
def apply_coupon(request):
    code = request.POST.get('coupon_code', '').strip()
    cart_items, subtotal = get_cart_items_details(request)
    coupon_service = CouponService()
    result = coupon_service.validate_coupon(code, subtotal)

    if result.is_valid:
        coupon = result.coupon
        discount_amount = result.discount_amount
        final_total = result.final_total

        # Satıcıya özel kupon kontrolü
        if coupon and coupon.seller:
            seller_items_subtotal = sum(
                item['price'] * item['quantity'] for item in cart_items if item['product'].seller == coupon.seller
            )
            if seller_items_subtotal <= 0:
                msg = f"Bu kupon sadece '{coupon.seller.store_name}' mağazasından yapılan alışverişlerde geçerlidir."
                request.session['applied_coupon_code'] = None
                request.session['coupon_error'] = msg
                return JsonResponse({'success': False, 'message': msg})

            discount_amount = coupon_service._calculate_discount_amount(coupon, seller_items_subtotal)
            final_total = subtotal - discount_amount

        request.session['applied_coupon_code'] = coupon.code
        request.session['coupon_error'] = None
        return JsonResponse({
            'success': True,
            'message': f"'{coupon.code}' kuponu başarıyla uygulandı!",
            'discount_amount': f'{discount_amount:.2f}',
            'final_total': f'{final_total:.2f}',
            'code': coupon.code,
        })

    request.session['applied_coupon_code'] = None
    request.session['coupon_error'] = result.message
    return JsonResponse({
        'success': False,
        'message': result.message,
    })


# ==============================================================================
# 4. ORDER & PAYMENT FLOW
# ==============================================================================

@login_required
def checkout_view(request):
    if request.user.role == 'SELLER':
        messages.error(request, "Satıcı hesapları sipariş veremez!")
        return redirect('store_index')

    cart_items, subtotal = get_cart_items_details(request)
    if not cart_items:
        messages.error(request, "Sepetiniz boş!")
        return redirect('store_index')

    preview_breakdown = []
    for item in cart_items:
        seller = item['product'].seller
        found = False
        for sb in preview_breakdown:
            if sb['seller_id'] == seller.id:
                sb['subtotal'] += item['total_price']
                found = True
                break
        if not found:
            preview_breakdown.append({
                'seller_id': seller.id,
                'store_name': seller.store_name,
                'commission_rate': seller.commission_rate,
                'subtotal': item['total_price']
            })

    for sb in preview_breakdown:
        comm_pct = Decimal(str(sb['commission_rate']))
        sb['commission_fee'] = (sb['subtotal'] * comm_pct / Decimal("100.00")).quantize(Decimal("0.01"))
        sb['seller_payout'] = sb['subtotal'] - sb['commission_fee']

    if request.method == 'POST':
        card_number = request.POST.get('card_number')
        card_holder = request.POST.get('card_holder')
        
        gateway = PaymentGatewayFactory.get_gateway()
        response = gateway.process_payment(
            customer=request.user,
            cart_items=cart_items,
            card_number=card_number,
            card_holder_name=card_holder
        )

        if response['status'] == 'FAILED':
            messages.error(request, response['error_message'])
            return render(request, 'storefront/checkout.html', {
                'cart_items': cart_items,
                'subtotal': subtotal,
                'preview_breakdown': preview_breakdown
            })

        try:
            with transaction.atomic():
                parent_order = Order.objects.create(
                    customer=request.user,
                    total_amount=subtotal,
                    payment_status='PAID',
                    payment_id=response['payment_id'],
                    order_status='RECEIVED'
                )

                seller_items = {}
                for item in cart_items:
                    seller_id = item['product'].seller.id
                    if seller_id not in seller_items:
                        seller_items[seller_id] = []
                    seller_items[seller_id].append(item)

                created_sub_orders = []
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
                            raise ValueError(f"{variant.product.title} ürünü için yetersiz stok!")
                        
                        variant.stock -= qty
                        variant.save()

                        OrderItem.objects.create(
                            sub_order=sub_order,
                            product=item['product'],
                            variant=variant,
                            quantity=qty,
                            price=item['price']
                        )

            # Trigger Notifications & Reward Points
            NotificationService.send_order_confirmation(parent_order)
            for sub_order in created_sub_orders:
                NotificationService.send_seller_new_order_alert(sub_order)

            earned_points = RewardService.earn_points_for_order(parent_order)

            request.session['cart'] = {}
            request.session['success_payment_data'] = {
                'payment_id': response['payment_id'],
                'total_paid': str(subtotal),
                'earned_points': str(earned_points),
                'platform_commission': str(response['platform_total_commission']),
                'breakdown': [
                    {
                        'store_name': b['store_name'],
                        'subtotal': str(b['subtotal']),
                        'commission_fee': str(b['commission_fee']),
                        'seller_payout': str(b['seller_payout']),
                        'iban': b['iban']
                    } for b in response['breakdown']
                ]
            }
            return redirect('checkout_success')


        except Exception as e:
            messages.error(request, f"Sipariş kaydedilirken bir hata oluştu: {str(e)}")
            return render(request, 'storefront/checkout.html', {
                'cart_items': cart_items,
                'subtotal': subtotal,
                'preview_breakdown': preview_breakdown
            })

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'preview_breakdown': preview_breakdown,
    }
    return render(request, 'storefront/checkout.html', context)


def checkout_success_view(request):
    payment_data = request.session.get('success_payment_data')
    if not payment_data:
        return redirect('store_index')
    return render(request, 'storefront/payment_result.html', {'payment_data': payment_data})


# ==============================================================================
# 5. EXPANDED CLIENT INTERACTION VIEWS (Favori, Mesaj, İade, Bildirim)
# ==============================================================================

@login_required
def toggle_favorite(request, product_id):
    """Ürünü favorilere ekler veya çıkarır (AJAX/Redirect)."""
    product = get_object_or_404(Product, id=product_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        favorite.delete()
        favorited = False
        msg = "Ürün favorilerinizden çıkarıldı."
    else:
        favorited = True
        msg = "Ürün favorilerinize eklendi."

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'favorited': favorited, 'message': msg})
    
    messages.success(request, msg)
    return redirect(request.META.get('HTTP_REFERER', 'store_index'))


@login_required
def favorites_view(request):
    """Müşterinin favorilediği ürünleri listeler."""
    fav_items = Favorite.objects.filter(user=request.user).select_related('product', 'product__seller')
    return render(request, 'storefront/favorites.html', {'fav_items': fav_items})


@login_required
def account_view(request):
    """
    Kullanıcı Hesabım Merkezi.
    Siparişler, İadeler, Bildirimler, İkinci El Dolabım ve PazarPuan buradadır.
    """
    user = request.user


    # Siparişler (İlişkili alt siparişler ve ürünleriyle birlikte)
    orders = Order.objects.filter(customer=user).prefetch_related('sub_orders', 'sub_orders__items', 'sub_orders__items__product').order_by('-created_at')
    
    # İade Talepleri
    return_requests = ReturnRequest.objects.filter(order_item__sub_order__parent_order__customer=user).select_related('order_item', 'order_item__product').order_by('-created_at')

    # Bildirimler (Okundu olarak işaretle)
    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    # Bildirimleri görüntüleyince otomatik okundu yap
    Notification.objects.filter(user=user, is_read=False).update(is_read=True)

    # Mesajlaşma (Kullanıcının yaptığı tüm konuşmaları topla)
    # Sohbet ettiği satıcıları (muhatapları) bulalım
    received_senders = ChatMessage.objects.filter(recipient=user).values_list('sender_id', flat=True)
    sent_recipients = ChatMessage.objects.filter(sender=user).values_list('recipient_id', flat=True)
    contact_ids = set(list(received_senders) + list(sent_recipients))
    contacts = CustomUser.objects.filter(id__in=contact_ids)

    # Aktif sohbet edilen satıcıyı seç
    active_contact_id = request.GET.get('chat_with')
    chat_messages = []
    active_contact = None
    
    if active_contact_id:
        active_contact = get_object_or_404(CustomUser, id=active_contact_id)
        # Mesajları getir
        chat_messages = ChatMessage.objects.filter(
            (Q(sender=user) & Q(recipient=active_contact)) |
            (Q(sender=active_contact) & Q(recipient=user))
        ).order_by('created_at')
        # Bu sohbetteki okunmamış mesajları okundu yap
        ChatMessage.objects.filter(sender=active_contact, recipient=user, is_read=False).update(is_read=True)

    # İkinci El Dolabım ilanları & Vitrin Keşif Ürünleri
    user_products = Product.objects.filter(seller__user=user).prefetch_related('variants')
    secondhand_products = Product.objects.all().select_related('seller', 'category').prefetch_related('variants')[:8]

    # PazarPuan Cüzdanı & İşlem Geçmişi
    reward_wallet = RewardService.get_or_create_wallet(user)
    reward_transactions = RewardTransaction.objects.filter(user=user).order_by('-created_at')

    context = {
        'orders': orders,
        'return_requests': return_requests,
        'notifications': notifications,
        'contacts': contacts,
        'active_contact': active_contact,
        'chat_messages': chat_messages,
        'user_products': user_products,
        'secondhand_products': secondhand_products,
        'reward_wallet': reward_wallet,
        'reward_transactions': reward_transactions,
    }
    return render(request, 'storefront/account.html', context)




@login_required
def request_return_view(request, order_item_id):
    """Müşterinin satın aldığı bir ürün satırı için iade formu."""
    order_item = get_object_or_404(OrderItem, id=order_item_id, sub_order__parent_order__customer=request.user)
    
    # Teslim edilmeyen ürün iade edilemez
    if order_item.sub_order.status != 'DELIVERED':
        messages.error(request, "Sadece teslim edilmiş siparişlerin iadesi yapılabilir!")
        return redirect('account')

    # Zaten iade talebi var mı?
    if ReturnRequest.objects.filter(order_item=order_item).exists():
        messages.warning(request, "Bu ürün için zaten bir iade talebiniz bulunuyor.")
        return redirect('account')

    if request.method == 'POST':
        reason = request.POST.get('reason')
        if reason:
            ret_req = ReturnRequest.objects.create(
                order_item=order_item,
                reason=reason
            )
            # Satıcıya bildirim gönder
            seller_user = order_item.sub_order.seller.user
            Notification.objects.create(
                user=seller_user,
                title="Yeni İade Talebi",
                message=f"{request.user.username} adlı müşteri #{order_item.sub_order.id} nolu siparişteki {order_item.product.title} ürünü için iade talebinde bulundu."
            )
            messages.success(request, "İade talebiniz başarıyla satıcıya iletildi.")
            return redirect('account')

    return render(request, 'storefront/return_request.html', {'item': order_item})


@login_required
@require_POST
def send_chat_message(request):
    """Anlık sohbet mesajı gönderimi (AJAX & Form uyumlu)."""
    recipient_id = request.POST.get('recipient_id')
    message_text = request.POST.get('message', '').strip()
    
    recipient = get_object_or_404(CustomUser, id=recipient_id)
    if message_text:
        msg = ChatMessage.objects.create(
            sender=request.user,
            recipient=recipient,
            message=message_text
        )
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('accept') == 'application/json':
            return JsonResponse({
                'success': True,
                'message': {
                    'id': msg.id,
                    'text': msg.message,
                    'sender': msg.sender.username,
                    'sender_id': msg.sender.id,
                    'created_at_time': msg.created_at.strftime('%H:%M')
                }
            })
            
        return redirect(f"{request.META.get('HTTP_REFERER', 'account')}?chat_with={recipient.id}")
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('accept') == 'application/json':
        return JsonResponse({'success': False, 'error': 'Mesaj boş olamaz.'}, status=400)
    return redirect('account')


@login_required
def poll_chat_messages(request, contact_id):
    """Yeni gelen mesajları getiren polling endpoint'i."""
    contact = get_object_or_404(CustomUser, id=contact_id)
    
    last_message_id = request.GET.get('last_id', 0)
    try:
        last_message_id = int(last_message_id)
    except ValueError:
        last_message_id = 0
        
    messages = ChatMessage.objects.filter(
        (Q(sender=request.user) & Q(recipient=contact)) |
        (Q(sender=contact) & Q(recipient=request.user))
    ).filter(id__gt=last_message_id).order_by('created_at')
    
    # Karşı taraftan gelen mesajları okundu yap
    ChatMessage.objects.filter(sender=contact, recipient=request.user, is_read=False).update(is_read=True)
    
    message_list = []
    for msg in messages:
        message_list.append({
            'id': msg.id,
            'text': msg.message,
            'sender': msg.sender.username,
            'sender_id': msg.sender.id,
            'created_at_time': msg.created_at.strftime('%H:%M')
        })
        
    return JsonResponse({
        'success': True,
        'messages': message_list
    })


# ==============================================================================
# 6. SELLER DASHBOARD VIEWS (Satıcı Paneli)
# ==============================================================================

def seller_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_seller():
            messages.error(request, "Bu sayfaya erişim yetkiniz yok!")
            return redirect('store_index')
        return view_func(request, *args, **kwargs)
    return wrapper


@seller_required
def seller_dashboard(request):
    seller_profile = request.user.seller_profile
    
    sub_orders = SubOrder.objects.filter(seller=seller_profile).select_related('parent_order', 'parent_order__customer').prefetch_related('items', 'items__product').order_by('-created_at')
    products = Product.objects.filter(seller=seller_profile).prefetch_related('variants')
    low_stock_variants = ProductVariant.objects.filter(product__seller=seller_profile, stock__lte=3).select_related('product')

    # İadeler: Bu satıcının siparişlerine gelen iade talepleri
    return_requests = ReturnRequest.objects.filter(order_item__sub_order__seller=seller_profile).select_related('order_item', 'order_item__product', 'order_item__sub_order__parent_order__customer').order_by('-created_at')

    # Finansallar
    total_sales = sum(so.subtotal for so in sub_orders if so.parent_order.payment_status == 'PAID')
    total_payout = sum(so.seller_payout for so in sub_orders if so.parent_order.payment_status == 'PAID')
    total_commission = sum(so.commission_fee for so in sub_orders if so.parent_order.payment_status == 'PAID')

    pending_shipment_count = sub_orders.filter(status='PENDING').count()
    completed_orders_count = sub_orders.filter(status='DELIVERED').count()

    # Sohbet kutusu: Satıcıya mesaj gönderen müşterileri toplayalım
    received_senders = ChatMessage.objects.filter(recipient=request.user).values_list('sender_id', flat=True)
    sent_recipients = ChatMessage.objects.filter(sender=request.user).values_list('recipient_id', flat=True)
    contact_ids = set(list(received_senders) + list(sent_recipients))
    contacts = CustomUser.objects.filter(id__in=contact_ids)

    active_contact_id = request.GET.get('chat_with')
    chat_messages = []
    active_contact = None
    if active_contact_id:
        active_contact = get_object_or_404(CustomUser, id=active_contact_id)
        chat_messages = ChatMessage.objects.filter(
            (Q(sender=request.user) & Q(recipient=active_contact)) |
            (Q(sender=active_contact) & Q(recipient=request.user))
        ).order_by('created_at')
        ChatMessage.objects.filter(sender=active_contact, recipient=request.user, is_read=False).update(is_read=True)

    # Okunmamış bildirimleri sıfırla
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Yorumlar: Bu satıcının ürünlerine gelen yorumlar
    pending_reviews = ProductReview.objects.filter(
        product__seller=seller_profile, 
        is_approved=False
    ).select_related('product', 'user').order_by('-created_at')
    
    approved_reviews = ProductReview.objects.filter(
        product__seller=seller_profile, 
        is_approved=True
    ).select_related('product', 'user').order_by('-created_at')

    # 7 günlük satış & hak ediş analiz verisi
    daily_sales_labels = []
    daily_sales_amounts = []
    daily_payout_amounts = []
    
    today = datetime.date.today()
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        day_sales = sum(
            so.subtotal for so in sub_orders 
            if so.parent_order.payment_status == 'PAID' and so.created_at.date() == day
        )
        day_payout = sum(
            so.seller_payout for so in sub_orders 
            if so.parent_order.payment_status == 'PAID' and so.created_at.date() == day
        )
        daily_sales_labels.append(day.strftime('%d %b'))
        daily_sales_amounts.append(float(day_sales))
        daily_payout_amounts.append(float(day_payout))
        
    # En çok satan ürünler (Top selling products)
    product_sales = {}
    for so in sub_orders:
        if so.parent_order.payment_status == 'PAID':
            for item in so.items.all():
                title = item.product.title
                qty = item.quantity
                product_sales[title] = product_sales.get(title, 0) + qty

    sorted_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]
    top_product_labels = [p[0] for p in sorted_products]
    top_product_counts = [p[1] for p in sorted_products]

    # JSON formatına çevir
    daily_sales_labels_json = json.dumps(daily_sales_labels)
    daily_sales_amounts_json = json.dumps(daily_sales_amounts)
    daily_payout_amounts_json = json.dumps(daily_payout_amounts)
    top_product_labels_json = json.dumps(top_product_labels)
    top_product_counts_json = json.dumps(top_product_counts)

    # Kuponlar: Satıcının kendi mağaza kuponları
    coupons = Coupon.objects.filter(seller=seller_profile).order_by('-created_at')

    context = {
        'seller': seller_profile,
        'sub_orders': sub_orders,
        'products': products,
        'low_stock_variants': low_stock_variants,
        'coupons': coupons,
        'return_requests': return_requests,
        'daily_sales_labels_json': daily_sales_labels_json,
        'daily_sales_amounts_json': daily_sales_amounts_json,
        'daily_payout_amounts_json': daily_payout_amounts_json,
        'top_product_labels_json': top_product_labels_json,
        'top_product_counts_json': top_product_counts_json,
        'total_sales': total_sales,
        'total_payout': total_payout,
        'total_commission': total_commission,
        'pending_shipment_count': pending_shipment_count,
        'completed_orders_count': completed_orders_count,
        'contacts': contacts,
        'active_contact': active_contact,
        'chat_messages': chat_messages,
        'notifications': notifications,
        'pending_reviews': pending_reviews,
        'approved_reviews': approved_reviews,
    }
    return render(request, 'seller/dashboard.html', context)


@seller_required
def seller_create_coupon(request):
    """Satıcının özel indirim kuponu oluşturmasını sağlar."""
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        discount_type = request.POST.get('discount_type', Coupon.DISCOUNT_TYPE_PERCENTAGE)
        discount_value = request.POST.get('discount_value')
        minimum_order_amount = request.POST.get('minimum_order_amount', '0.00')
        usage_limit = request.POST.get('usage_limit', '1')

        if not code or not discount_value:
            messages.error(request, "Kupon kodu ve indirim miktarı zorunludur!")
            return redirect('seller_dashboard')

        if Coupon.objects.filter(code__iexact=code).exists():
            messages.error(request, f"'{code}' kupon kodu zaten kullanımda! Başka bir kod deneyin.")
            return redirect('seller_dashboard')

        try:
            Coupon.objects.create(
                seller=request.user.seller_profile,
                code=code,
                discount_type=discount_type,
                discount_value=Decimal(discount_value),
                minimum_order_amount=Decimal(minimum_order_amount),
                usage_limit=int(usage_limit),
            )
            messages.success(request, f"'{code}' indirim kuponu başarıyla oluşturuldu!")
        except Exception as e:
            messages.error(request, f"Kupon oluşturulurken hata: {str(e)}")

    return redirect('seller_dashboard')


@seller_required
@require_POST
def update_suborder_status(request, suborder_id):
    seller_profile = request.user.seller_profile
    sub_order = get_object_or_404(SubOrder, id=suborder_id, seller=seller_profile)

    new_status = request.POST.get('status')
    shipping_company = request.POST.get('shipping_company', '').strip()
    tracking_number = request.POST.get('tracking_number', '').strip()
    estimated_delivery_date = request.POST.get('estimated_delivery_date', '').strip()

    if new_status in dict(SubOrder.STATUS_CHOICES):
        sub_order.status = new_status
        sub_order.save()

        parent_order = sub_order.parent_order
        parent_order.order_status = new_status if new_status in {'SHIPPED', 'DELIVERED', 'CANCELLED'} else 'PREPARING' if new_status == 'PENDING' else 'RECEIVED'
        if shipping_company:
            parent_order.shipping_company = shipping_company
        if tracking_number:
            parent_order.tracking_number = tracking_number
        if estimated_delivery_date:
            parent_order.estimated_delivery_date = estimated_delivery_date
        parent_order.save(update_fields=['order_status', 'shipping_company', 'tracking_number', 'estimated_delivery_date'])

        customer = parent_order.customer
        NotificationService.send_shipping_update(sub_order)

        messages.success(request, f"Sipariş #{sub_order.id} durumu güncellendi: {sub_order.get_status_display()}")
    else:
        messages.error(request, "Geçersiz sipariş durumu!")

    return redirect('seller_dashboard')


@seller_required
@require_POST
def seller_handle_return(request, return_id):
    """Satıcının iade talebini onaylaması veya reddetmesi."""
    seller_profile = request.user.seller_profile
    return_req = get_object_or_404(ReturnRequest, id=return_id, order_item__sub_order__seller=seller_profile)
    
    action = request.POST.get('action') # 'APPROVE' or 'REJECT'
    customer = return_req.order_item.sub_order.parent_order.customer
    
    if action == 'APPROVE':
        return_req.status = 'APPROVED'
        return_req.save()
        NotificationService.send_return_status_update(return_req)
        messages.success(request, "İade talebini onayladınız. Stoklar güncellendi.")
    elif action == 'REJECT':
        return_req.status = 'REJECTED'
        return_req.save()
        NotificationService.send_return_status_update(return_req)
        messages.info(request, "İade talebini reddettiniz.")
        
    return redirect('seller_dashboard')


@seller_required
@require_POST
def seller_handle_review(request, review_id):
    """Satıcının kendi ürünlerine yapılan yorumları onaylaması veya silmesi/reddetmesi."""
    seller_profile = request.user.seller_profile
    review = get_object_or_404(ProductReview, id=review_id, product__seller=seller_profile)
    
    action = request.POST.get('action') # 'APPROVE' or 'REJECT'
    product = review.product
    customer = review.user
    
    if action == 'APPROVE':
        review.is_approved = True
        review.save()
        
        # Ürün puanlarını yenile
        ReviewService()._refresh_product_rating(product)
        
        Notification.objects.create(
            user=customer,
            title="Yorumunuz Yayınlandı",
            message=f"'{product.title}' ürününe yaptığınız yorum satıcı tarafından onaylandı ve yayınlandı."
        )
        messages.success(request, "Yorumu onayladınız ve ürün puanları güncellendi.")
        
    elif action == 'REJECT':
        review.delete()
        
        # Ürün puanlarını yenile
        ReviewService()._refresh_product_rating(product)
        
        messages.info(request, "Yorum reddedildi / silindi ve ürün puanları güncellendi.")
        
    referer = request.META.get('HTTP_REFERER')
    if referer:
        if 'tab=' in referer:
            return redirect(referer)
        separator = '&' if '?' in referer else '?'
        return redirect(f"{referer}{separator}tab=reviews")
    else:
        from django.urls import reverse
        return redirect(f"{reverse('seller_dashboard')}?tab=reviews")


@seller_required
def seller_add_product(request):
    seller_profile = request.user.seller_profile
    categories = Category.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        base_price = Decimal(request.POST.get('base_price', '0.00'))
        category_id = request.POST.get('category')

        colors = request.POST.getlist('variant_color[]')
        sizes = request.POST.getlist('variant_size[]')
        stocks = request.POST.getlist('variant_stock[]')
        skus = request.POST.getlist('variant_sku[]')
        prices = request.POST.getlist('variant_price[]')

        try:
            with transaction.atomic():
                category = Category.objects.get(id=category_id)
                product = Product.objects.create(
                    seller=seller_profile,
                    category=category,
                    title=title,
                    description=description,
                    base_price=base_price
                )

                for i in range(len(skus)):
                    sku = skus[i]
                    if not sku:
                        continue
                    
                    color = colors[i] if i < len(colors) else None
                    size = sizes[i] if i < len(sizes) else None
                    stock = int(stocks[i]) if i < len(stocks) else 0
                    price_val = Decimal(prices[i]) if (i < len(prices) and prices[i]) else None

                    ProductVariant.objects.create(
                        product=product,
                        color=color or None,
                        size=size or None,
                        price=price_val,
                        stock=stock,
                        sku=sku
                    )

                messages.success(request, f"'{product.title}' ürünü varyasyonlarıyla birlikte başarıyla eklendi.")
                return redirect('seller_dashboard')

        except Exception as e:
            messages.error(request, f"Ürün eklenirken hata oluştu: {str(e)}")

    context = {
        'categories': categories,
    }
    return render(request, 'seller/add_product.html', context)


def set_currency(request):
    currency = request.GET.get('currency', 'TRY')
    next_url = request.GET.get('next', '/')
    if currency in ['TRY', 'USD', 'EUR']:
        request.session['currency'] = currency
    return redirect(next_url)


def search_autocomplete(request):
    query = request.GET.get('q', '').strip()
    products_data = []
    categories_data = []
    
    if len(query) >= 2:
        products = Product.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:5]
        for p in products:
            products_data.append({
                'id': p.id,
                'title': p.title,
                'price': float(p.base_price),
                'image_url': p.image_url,
                'url': f"/product/{p.id}/"
            })
            
        categories = Category.objects.filter(name__icontains=query)[:3]
        for c in categories:
            categories_data.append({
                'id': c.id,
                'name': c.name,
                'slug': c.slug
            })
            
    return JsonResponse({
        'products': products_data,
        'categories': categories_data
    })


# ==============================================================================
# 8. SUPERADMIN DASHBOARD VIEWS (Siteden Sorumlu Yönetici Paneli)
# ==============================================================================

def superadmin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superadmin():
            messages.error(request, "Bu sayfaya erişim yetkiniz yok! Yalnızca platform yöneticileri girebilir.")
            return redirect('store_index')
        return view_func(request, *args, **kwargs)
    return wrapper


@superadmin_required
def superadmin_dashboard(request):
    sellers = SellerProfile.objects.select_related('user').all().order_by('-user__date_joined')
    pending_sellers = sellers.filter(is_approved=False)
    approved_sellers = sellers.filter(is_approved=True)

    all_orders = Order.objects.all().select_related('customer').order_by('-created_at')
    sub_orders = SubOrder.objects.all().select_related('seller', 'parent_order', 'parent_order__customer').prefetch_related('items', 'items__product').order_by('-created_at')

    paid_suborders = sub_orders.filter(parent_order__payment_status='PAID')
    total_gmv = sum(so.subtotal for so in paid_suborders)
    total_platform_commission = sum(so.commission_fee for so in paid_suborders)
    total_seller_payout = sum(so.seller_payout for so in paid_suborders)

    total_customers_count = CustomUser.objects.filter(role='CUSTOMER').count()
    total_products_count = Product.objects.count()
    total_orders_count = all_orders.count()

    categories = Category.objects.filter(parent=None).prefetch_related('subcategories')
    all_categories_flat = Category.objects.all().order_by('name')

    platform_coupons = Coupon.objects.filter(seller=None).order_by('-created_at')

    daily_labels = []
    daily_gmv_list = []
    daily_commission_list = []

    today = datetime.date.today()
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        day_suborders = paid_suborders.filter(created_at__date=day)
        day_gmv = sum(so.subtotal for so in day_suborders)
        day_comm = sum(so.commission_fee for so in day_suborders)
        
        daily_labels.append(day.strftime('%d %b'))
        daily_gmv_list.append(float(day_gmv))
        daily_commission_list.append(float(day_comm))

    all_users = CustomUser.objects.all().order_by('-date_joined')[:50]

    # Mağaza Ciro Dağılımı (Seller Revenue Breakdown)
    seller_revenues = {}
    for so in paid_suborders:
        s_name = so.seller.store_name
        seller_revenues[s_name] = seller_revenues.get(s_name, Decimal('0.00')) + so.subtotal
    
    sorted_sellers = sorted(seller_revenues.items(), key=lambda x: x[1], reverse=True)[:5]
    top_seller_names = [s[0] for s in sorted_sellers]
    top_seller_revenues = [float(s[1]) for s in sorted_sellers]

    # Sipariş Statü Dağılımı
    status_dict = {
        'RECEIVED': 'Alındı',
        'PREPARING': 'Hazırlanıyor',
        'SHIPPED': 'Kargolandı',
        'DELIVERED': 'Teslim Edildi',
        'CANCELLED': 'İptal'
    }
    order_status_labels = []
    order_status_counts = []
    for code, label in status_dict.items():
        cnt = sub_orders.filter(status=code).count()
        if cnt > 0:
            order_status_labels.append(label)
            order_status_counts.append(cnt)

    context = {
        'sellers': sellers,
        'pending_sellers': pending_sellers,
        'approved_sellers': approved_sellers,
        'all_orders': all_orders,
        'sub_orders': sub_orders,
        'total_gmv': total_gmv,
        'total_platform_commission': total_platform_commission,
        'total_seller_payout': total_seller_payout,
        'total_customers_count': total_customers_count,
        'total_products_count': total_products_count,
        'total_orders_count': total_orders_count,
        'categories': categories,
        'all_categories_flat': all_categories_flat,
        'platform_coupons': platform_coupons,
        'all_users': all_users,
        'daily_labels_json': json.dumps(daily_labels),
        'daily_gmv_json': json.dumps(daily_gmv_list),
        'daily_commission_json': json.dumps(daily_commission_list),
        'top_seller_names_json': json.dumps(top_seller_names),
        'top_seller_revenues_json': json.dumps(top_seller_revenues),
        'order_status_labels_json': json.dumps(order_status_labels),
        'order_status_counts_json': json.dumps(order_status_counts),
    }
    return render(request, 'admin/dashboard.html', context)


@superadmin_required
@require_POST
def admin_toggle_seller_approval(request, seller_id):
    seller = get_object_or_404(SellerProfile, id=seller_id)
    seller.is_approved = not seller.is_approved
    seller.save()
    status_str = "onaylandı ve aktif edildi" if seller.is_approved else "askıya alındı"
    messages.success(request, f"'{seller.store_name}' mağazasının durumu '{status_str}' olarak güncellendi.")
    return redirect('superadmin_dashboard')


@superadmin_required
@require_POST
def admin_update_commission_rate(request, seller_id):
    seller = get_object_or_404(SellerProfile, id=seller_id)
    rate_str = request.POST.get('commission_rate')
    try:
        new_rate = Decimal(rate_str)
        if new_rate < 0 or new_rate > 100:
            raise ValueError
        seller.commission_rate = new_rate
        seller.save()
        messages.success(request, f"'{seller.store_name}' mağazasının komisyon oranı %{new_rate} olarak güncellendi.")
    except Exception:
        messages.error(request, "Geçersiz komisyon oranı! 0 ile 100 arasında geçerli bir değer giriniz.")
    return redirect('superadmin_dashboard')


@superadmin_required
@require_POST
def admin_create_category(request):
    name = request.POST.get('name', '').strip()
    parent_id = request.POST.get('parent_id')

    if not name:
        messages.error(request, "Kategori adı zorunludur!")
        return redirect('superadmin_dashboard')

    parent_cat = None
    if parent_id:
        parent_cat = get_object_or_404(Category, id=parent_id)

    if Category.objects.filter(name__iexact=name, parent=parent_cat).exists():
        messages.error(request, f"'{name}' isimli kategori bu seviyede zaten mevcut!")
        return redirect('superadmin_dashboard')

    Category.objects.create(name=name, parent=parent_cat)
    messages.success(request, f"'{name}' kategorisi başarıyla eklendi.")
    return redirect('superadmin_dashboard')


@superadmin_required
@require_POST
def admin_delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    name = category.name
    category.delete()
    messages.success(request, f"'{name}' kategorisi başarıyla silindi.")
    return redirect('superadmin_dashboard')


@superadmin_required
@require_POST
def admin_create_platform_coupon(request):
    code = request.POST.get('code', '').strip().upper()
    discount_type = request.POST.get('discount_type', Coupon.DISCOUNT_TYPE_PERCENTAGE)
    discount_value = request.POST.get('discount_value')
    minimum_order_amount = request.POST.get('minimum_order_amount', '0.00')
    usage_limit = request.POST.get('usage_limit', '1')

    if not code or not discount_value:
        messages.error(request, "Kupon kodu ve indirim miktarı zorunludur!")
        return redirect('superadmin_dashboard')

    if Coupon.objects.filter(code__iexact=code).exists():
        messages.error(request, f"'{code}' kupon kodu zaten kullanımda!")
        return redirect('superadmin_dashboard')

    try:
        Coupon.objects.create(
            seller=None,
            code=code,
            discount_type=discount_type,
            discount_value=Decimal(discount_value),
            minimum_order_amount=Decimal(minimum_order_amount),
            usage_limit=int(usage_limit),
        )
        messages.success(request, f"Platform kuponu '{code}' başarıyla oluşturuldu!")
    except Exception as e:
        messages.error(request, f"Kupon oluşturulurken hata: {str(e)}")

    return redirect('superadmin_dashboard')


# ==============================================================================
# 9. IN-APP LIVE NOTIFICATION API VIEWS
# ==============================================================================

@login_required
def poll_user_notifications(request):
    """
    Kullanıcının canlı okunmamış bildirimlerini ve son 10 bildirim listesini AJAX ile döndürür.
    """
    unread_count = request.user.notifications.filter(is_read=False).count()
    recent_notifications = request.user.notifications.all().order_by('-created_at')[:10]
    
    notif_data = []
    for n in recent_notifications:
        icon_class = "fa-solid fa-bell text-primary"
        lower_t = (n.title + " " + n.message).lower()
        if "kargo" in lower_t or "kargolandı" in lower_t:
            icon_class = "fa-solid fa-truck-fast text-success"
        elif "sipariş" in lower_t or "siparişiniz" in lower_t:
            icon_class = "fa-solid fa-bag-shopping text-info"
        elif "iade" in lower_t:
            icon_class = "fa-solid fa-rotate-left text-warning"
        elif "satış" in lower_t:
            icon_class = "fa-solid fa-chart-line text-danger"

        notif_data.append({
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'created_at': n.created_at.strftime('%d.%m.%Y %H:%M'),
            'is_read': n.is_read,
            'icon_class': icon_class,
        })
        
    return JsonResponse({
        'unread_count': unread_count,
        'notifications': notif_data,
    })


@login_required
@require_POST
def mark_notifications_read(request):
    """
    Kullanıcının tüm okunmamış bildirimlerini okundu yapar.
    """
    notif_id = request.POST.get('notification_id')
    if notif_id:
        request.user.notifications.filter(id=notif_id).update(is_read=True)
    else:
        request.user.notifications.filter(is_read=False).update(is_read=True)
        
    unread_count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'status': 'success', 'unread_count': unread_count})


# ==============================================================================
# 10. GAMIFICATION (SPIN WHEEL) & LOYALTY POINTS API VIEWS
# ==============================================================================

@login_required
@require_POST
def spin_wheel_api(request):
    """
    Kullanıcının günde 1 kez Günlük Şans Çarkını çevirmesini sağlar.
    Kazanılan PazarPuan'ı cüzdana ekler.
    """
    user = request.user
    today_str = datetime.date.today().isoformat()
    last_spin = request.session.get('last_spin_date')

    if last_spin == today_str:
        return JsonResponse({
            'status': 'error',
            'message': 'Bugün şans çarkını zaten çevirdiniz! Yarın tekrar deneyin.'
        }, status=400)

    import random
    slices = [
        {'label': '10 PazarPuan', 'type': 'POINTS', 'value': 10, 'deg': 30},
        {'label': '25 PazarPuan', 'type': 'POINTS', 'value': 25, 'deg': 90},
        {'label': '50 PazarPuan', 'type': 'POINTS', 'value': 50, 'deg': 150},
        {'label': '100 PazarPuan', 'type': 'POINTS', 'value': 100, 'deg': 210},
        {'label': '%10 İndirim Kuponu', 'type': 'COUPON', 'value': 'CARK10', 'deg': 270},
        {'label': 'Sürpriz 15 PazarPuan', 'type': 'POINTS', 'value': 15, 'deg': 330},
    ]

    selected_award = random.choice(slices)
    request.session['last_spin_date'] = today_str

    if selected_award['type'] == 'POINTS':
        pts = Decimal(str(selected_award['value']))
        wallet = RewardService.get_or_create_wallet(user)
        wallet.balance += pts
        wallet.save()

        RewardTransaction.objects.create(
            user=user,
            points=pts,
            transaction_type='EARNED',
            description="Günlük Şans Çarkı Oyunundan Kazanılan PazarPuan"
        )
        
        Notification.objects.create(
            user=user,
            title="Tebrikler! 🎡 Şans Çarkı Ödülü",
            message=f"Günlük şans çarkından {selected_award['value']} PazarPuan kazandınız! Hesabınıza yüklendi."
        )

    return JsonResponse({
        'status': 'success',
        'award': selected_award,
        'deg': selected_award['deg'],
        'new_balance': float(RewardService.get_or_create_wallet(user).balance)
    })


@login_required
@require_POST
def apply_points_cart(request):
    """
    Sepet sayfasında PazarPuan harcayarak sepete indirim uygulama.
    """
    points_to_use = request.POST.get('points', 0)
    try:
        pts = Decimal(str(points_to_use))
        wallet = RewardService.get_or_create_wallet(request.user)
        if pts <= 0 or pts > wallet.balance:
            messages.error(request, "Geçersiz PazarPuan miktarı!")
            return redirect('view_cart')

        request.session['applied_points'] = float(pts)
        messages.success(request, f"{pts} PazarPuan ({pts} TL) sepetinize indirim olarak uygulandı!")
    except Exception as e:
        messages.error(request, f"PazarPuan uygulanırken hata: {str(e)}")

    return redirect('view_cart')


# ==============================================================================
# 11. EXPORT REPORTS & INVOICE GENERATION VIEWS
# ==============================================================================

import csv

@seller_required
def seller_export_orders_csv(request):
    """
    Satıcının tüm alt siparişlerini, satış tutarlarını ve net IBAN hak edişlerini UTF-8 CSV olarak indirir.
    """
    seller_profile = request.user.seller_profile
    sub_orders = SubOrder.objects.filter(seller=seller_profile).select_related('parent_order__customer').order_by('-created_at')

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="satis_raporu_{seller_profile.store_name}_{datetime.date.today()}.csv"'

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Alt Siparis ID', 'Siparis Tarihi', 'Musteri', 'Urunler & Adet', 'Toplam Tutar (TL)', 'Komisyon Kesintisi (TL)', 'Net IBAN Hak Edis (TL)', 'Durum'])

    for so in sub_orders:
        items_str = ", ".join([f"{item.product.title} (x{item.quantity})" for item in so.items.all()])
        customer_name = so.parent_order.customer.get_full_name() or so.parent_order.customer.username
        writer.writerow([
            f"#{so.id}",
            so.created_at.strftime('%d.%m.%Y %H:%M'),
            customer_name,
            items_str,
            f"{so.subtotal:.2f}",
            f"{so.commission_fee:.2f}",
            f"{so.seller_payout:.2f}",
            so.get_status_display()
        ])

    return response


@superadmin_required
def admin_export_platform_csv(request):
    """
    Superadmin için tüm platform satış ve komisyon dökümünü CSV olarak indirir.
    """
    sub_orders = SubOrder.objects.select_related('seller', 'parent_order__customer').order_by('-created_at')

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="platform_finans_raporu_{datetime.date.today()}.csv"'

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Alt Siparis ID', 'Magaza Adi', 'Siparis Tarihi', 'Musteri', 'Brut Tutar (TL)', 'Komisyon Orani (%)', 'Platform Komisyon Geliri (TL)', 'Satici Net Hak Edis (TL)', 'Odeme Durumu'])

    for so in sub_orders:
        customer_name = so.parent_order.customer.get_full_name() or so.parent_order.customer.username
        writer.writerow([
            f"#{so.id}",
            so.seller.store_name,
            so.created_at.strftime('%d.%m.%Y %H:%M'),
            customer_name,
            f"{so.subtotal:.2f}",
            f"%{so.seller.commission_rate}",
            f"{so.commission_fee:.2f}",
            f"{so.seller_payout:.2f}",
            so.parent_order.get_payment_status_display()
        ])

    return response


@login_required
def generate_order_invoice(request, order_id):
    """
    Sipariş ve alt sipariş detaylarını içeren basılabilir e-Fatura görünümü.
    """
    order = get_object_or_404(Order, id=order_id)

    is_owner = (order.customer == request.user)
    is_superadmin = getattr(request.user, 'is_superadmin', False)
    is_seller_of_order = False
    if hasattr(request.user, 'seller_profile'):
        is_seller_of_order = order.sub_orders.filter(seller=request.user.seller_profile).exists()

    if not (is_owner or is_superadmin or is_seller_of_order):
        messages.error(request, "Bu faturayı görüntüleme yetkiniz bulunmamaktadır.")
        return redirect('store_index')

    context = {
        'order': order,
        'sub_orders': order.sub_orders.all().prefetch_related('items__product', 'items__variant'),
        'today': datetime.date.today(),
    }
    return render(request, 'storefront/invoice.html', context)


@login_required
@require_POST
def toggle_review_helpful(request, review_id):
    """
    Kullanıcının ürün yorumunu 'Faydalı Buldum 👍' olarak oylamasını sağlar.
    """
    review = get_object_or_404(ProductReview, id=review_id)
    session_key = f'voted_helpful_{review.id}'
    
    if request.session.get(session_key):
        return JsonResponse({
            'status': 'already_voted',
            'helpful_count': review.helpful_count,
            'message': 'Bu yorumu zaten faydalı olarak oyladınız.'
        })

    review.helpful_count += 1
    review.save()
    request.session[session_key] = True

    return JsonResponse({
        'status': 'success',
        'helpful_count': review.helpful_count,
        'message': 'Teşekkürler! Oyunuz kaydedildi.'
    })


# ==============================================================================
# 12. LIVE CHAT WIDGET API VIEWS
# ==============================================================================

@login_required
def poll_widget_chat_messages(request):
    """
    Seçili alıcı ile olan canlı mesajlaşma geçmişini ve okunmamış mesaj sayısını döndürür.
    """
    recipient_id = request.GET.get('recipient_id')
    user = request.user

    unread_count = ChatMessage.objects.filter(recipient=user, is_read=False).count()

    messages_data = []
    if recipient_id:
        recipient = get_object_or_404(CustomUser, id=recipient_id)
        ChatMessage.objects.filter(sender=recipient, recipient=user, is_read=False).update(is_read=True)
        
        chat_qs = ChatMessage.objects.filter(
            (Q(sender=user) & Q(recipient=recipient)) |
            (Q(sender=recipient) & Q(recipient=user))
        ).order_by('created_at')[:50]

        for m in chat_qs:
            messages_data.append({
                'id': m.id,
                'sender_id': m.sender.id,
                'sender_name': m.sender.get_full_name() or m.sender.username,
                'is_me': (m.sender.id == user.id),
                'message': m.message,
                'created_at': m.created_at.strftime('%H:%M'),
            })

    return JsonResponse({
        'unread_count': unread_count,
        'messages': messages_data,
    })


@login_required
@require_POST
def send_chat_message_api(request):
    """
    Canlı chat penceresinden anlık mesaj gönderimi.
    """
    recipient_id = request.POST.get('recipient_id')
    message_text = request.POST.get('message', '').strip()

    if not recipient_id or not message_text:
        return JsonResponse({'status': 'error', 'message': 'Mesaj içeriği ve alıcı gereklidir.'}, status=400)

    recipient = get_object_or_404(CustomUser, id=recipient_id)
    msg = ChatMessage.objects.create(
        sender=request.user,
        recipient=recipient,
        message=message_text
    )

    return JsonResponse({
        'status': 'success',
        'message_data': {
            'id': msg.id,
            'sender_id': request.user.id,
            'sender_name': request.user.get_full_name() or request.user.username,
            'is_me': True,
            'message': msg.message,
            'created_at': msg.created_at.strftime('%H:%M'),
        }
    })


# ==============================================================================
# SECOND-HAND MARKETPLACE & BIDDING VIEWS (Dolap / Sahibinden İlan ve Teklif)
# ==============================================================================

def second_hand_list_view(request):
    """İkinci el ürün ilanlarını listeler."""
    from marketplace.models import SecondHandItem
    items = SecondHandItem.objects.filter(is_sold=False).order_by('-created_at')
    return render(request, 'storefront/second_hand_list.html', {'items': items})


@login_required
def second_hand_create_view(request):
    """Yeni ikinci el ürün ilanı yayınlama."""
    from marketplace.models import SecondHandItem
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price')
        condition = request.POST.get('condition', 'GOOD')
        image = request.FILES.get('image')

        if title and price:
            SecondHandItem.objects.create(
                seller_user=request.user,
                title=title,
                description=description,
                price=Decimal(price),
                condition=condition,
                image=image
            )
            messages.success(request, 'İkinci el ürün ilanınız başarıyla yayınlandı!')
            return redirect('second_hand_list')

    return render(request, 'storefront/second_hand_create.html')


@login_required
@require_POST
def submit_offer_view(request):
    """Ürün veya İkinci El ilan için teklif verme API'si."""
    from marketplace.services.offer_service import OfferService
    from marketplace.models import Product, SecondHandItem

    product_id = request.POST.get('product_id')
    second_hand_id = request.POST.get('second_hand_id')
    offered_price = request.POST.get('offered_price')

    if not offered_price:
        return JsonResponse({'status': 'error', 'message': 'Lütfen geçerli bir teklif tutarı giriniz.'}, status=400)

    product = Product.objects.filter(id=product_id).first() if product_id else None
    sh_item = SecondHandItem.objects.filter(id=second_hand_id).first() if second_hand_id else None

    try:
        service = OfferService()
        offer = service.create_offer(
            buyer=request.user,
            offered_price=Decimal(offered_price),
            product=product,
            second_hand_item=sh_item
        )
        return JsonResponse({'status': 'success', 'message': 'Teklifiniz satıcıya iletildi!', 'offer_id': offer.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def my_offers_view(request):
    """Kullanıcının verdiği ve aldığı teklifler ekranı."""
    from marketplace.models import ProductOffer
    submitted_offers = ProductOffer.objects.filter(buyer=request.user).order_by('-created_at')
    received_offers = ProductOffer.objects.filter(
        Q(product__seller__user=request.user) | Q(second_hand_item__seller_user=request.user)
    ).distinct().order_by('-created_at')

    return render(request, 'storefront/my_offers.html', {
        'submitted_offers': submitted_offers,
        'received_offers': received_offers
    })


@login_required
@require_POST
def respond_offer_view(request, offer_id):
    """Satıcının gelen teklifi kabul etmesi veya reddetmesi."""
    from marketplace.services.offer_service import OfferService
    from marketplace.models import ProductOffer

    offer = get_object_or_404(ProductOffer, id=offer_id)
    action = request.POST.get('action')  # 'accept' or 'reject'

    try:
        service = OfferService()
        service.respond_to_offer(offer, request.user, accept=(action == 'accept'))
        messages.success(request, f'Teklif {offer.get_status_display().lower()} olarak güncellendi.')
    except Exception as e:
        messages.error(request, str(e))

    return redirect('my_offers')


@login_required
@require_POST
def send_chat_message(request):
    from marketplace.models import ChatMessage, CustomUser
    receiver_id = request.POST.get('receiver_id') or request.POST.get('recipient_id')
    message_text = request.POST.get('message', '').strip()
    if not receiver_id or not message_text:
        return JsonResponse({'status': 'error', 'success': False, 'message': 'Eksik parametre'}, status=400)

    recipient = get_object_or_404(CustomUser, id=receiver_id)
    msg = ChatMessage.objects.create(
        sender=request.user,
        recipient=recipient,
        message=message_text
    )
    return JsonResponse({
        'status': 'success',
        'success': True,
        'id': msg.id,
        'sender': msg.sender.username,
        'message': {
            'id': msg.id,
            'text': msg.message,
            'sender': msg.sender.username,
            'created_at': msg.created_at.strftime('%H:%M')
        },
        'created_at': msg.created_at.strftime('%H:%M')
    })


@login_required
def poll_chat_messages(request, contact_id):
    from marketplace.models import ChatMessage
    messages_qs = ChatMessage.objects.filter(
        Q(sender=request.user, recipient_id=contact_id) |
        Q(sender_id=contact_id, recipient=request.user)
    ).order_by('created_at')

    last_id = request.GET.get('last_id')
    if last_id and last_id.isdigit():
        messages_qs = messages_qs.filter(id__gt=int(last_id))

    msg_list = [{
        'id': m.id,
        'is_me': m.sender == request.user,
        'sender': m.sender.username,
        'text': m.message,
        'message': m.message,
        'created_at': m.created_at.strftime('%H:%M')
    } for m in messages_qs]

    return JsonResponse({'status': 'success', 'success': True, 'messages': msg_list})


@login_required
@require_POST
def send_chat_message_api(request):
    return send_chat_message(request)


@login_required
def poll_widget_chat_messages(request):
    contact_id = request.GET.get('contact_id')
    if not contact_id:
        return JsonResponse({'status': 'error', 'message': 'contact_id gerekli'}, status=400)
    return poll_chat_messages(request, contact_id)


def api_docs_view(request):
    """Etkileşimli REST API ve JWT uç noktaları dokümantasyon sayfası."""
    endpoints = [
        {'method': 'POST', 'path': '/api/auth/register/', 'desc': 'Yeni müşteri veya satıcı kaydı.', 'auth': 'Yok'},
        {'method': 'POST', 'path': '/api/auth/login/', 'desc': 'Kullanıcı girişi & Access/Refresh JWT Token alma.', 'auth': 'Yok'},
        {'method': 'POST', 'path': '/api/auth/token/refresh/', 'desc': 'JWT Access Token yenileme.', 'auth': 'Bearer Token'},
        {'method': 'GET', 'path': '/api/auth/profile/', 'desc': 'Giriş yapan kullanıcının profil bilgileri.', 'auth': 'Bearer Token'},
        {'method': 'GET', 'path': '/api/categories/', 'desc': 'Tüm hiyerarşik kategorileri ve alt kategorileri listeler.', 'auth': 'Yok'},
        {'method': 'GET', 'path': '/api/products/', 'desc': 'Ürün kataloğu (filtreleme, arama ve sıralama destekli).', 'auth': 'Yok'},
        {'method': 'GET', 'path': '/api/products/<id>/', 'desc': 'Ürün detayları ve varyasyon bilgileri.', 'auth': 'Yok'},
        {'method': 'POST', 'path': '/api/cart/checkout/', 'desc': 'Mobil sepet sipariş tamamlama (Split Order).', 'auth': 'Bearer Token'},
        {'method': 'POST', 'path': '/api/favorites/toggle/', 'desc': 'Favori ürün ekleme / çıkarma.', 'auth': 'Bearer Token'},
        {'method': 'GET', 'path': '/api/orders/', 'desc': 'Müşterinin geçmiş siparişleri ve kargo durumları.', 'auth': 'Bearer Token'},
        {'method': 'GET', 'path': '/api/seller/dashboard/', 'desc': 'Satıcının anlık satış metrikleri ve mağaza özeti.', 'auth': 'Bearer Token (Satıcı)'},
        {'method': 'POST', 'path': '/api/spin-wheel/', 'desc': 'Günlük çarkıfelek çevirme ve puan/kupon kazanımı.', 'auth': 'Oturum / Token'},
        {'method': 'POST', 'path': '/messages/send/', 'desc': 'Canlı sohbet mesajı gönderme.', 'auth': 'Oturum'},
        {'method': 'GET', 'path': '/messages/poll/<contact_id>/', 'desc': 'Canlı sohbet mesajlarını sorgulama (polling).', 'auth': 'Oturum'},
    ]
    return render(request, 'admin/api_docs.html', {'endpoints': endpoints})


@login_required
def generate_order_invoice(request, order_id):
    """Müşterinin veya satıcının sipariş e-Faturasını HTML olarak görüntüler."""
    order = get_object_or_404(Order, id=order_id)
    if not (request.user.is_superadmin() or order.customer == request.user or order.sub_orders.filter(seller__user=request.user).exists()):
        messages.error(request, "Bu faturayı görüntüleme yetkiniz yok!")
        return redirect('store_index')
    from marketplace.services.qr_service import QRService
    sub_orders = order.sub_orders.prefetch_related('items__product', 'items__variant', 'seller').all()
    qr_code_svg = QRService.generate_svg_qr_code(f"https://pazaryeri.com/verify-invoice/{order.id}")
    return render(request, 'storefront/invoice.html', {
        'order': order,
        'sub_orders': sub_orders,
        'today': timezone.now(),
        'qr_code_svg': qr_code_svg
    })


@login_required
def generate_order_pdf_invoice(request, order_id):
    """Sipariş için tek tıkla indirilebilir profesyonel PDF Fatura üretir."""
    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from marketplace.models import Order

    order = get_object_or_404(Order, id=order_id)
    if not (request.user.is_superadmin() or order.customer == request.user or order.sub_orders.filter(seller__user=request.user).exists()):
        messages.error(request, "Bu faturayı indirme yetkiniz yok!")
        return redirect('store_index')

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0f172a'))
    story.append(Paragraph(f"FATURA - Siparis #{order.id}", title_style))
    story.append(Spacer(1, 10))

    customer_name = order.customer.get_full_name() or order.customer.username
    info_text = f"Musteri: {customer_name}<br/>Tarih: {order.created_at.strftime('%d/%m/%Y %H:%M')}<br/>Odeme Durumu: {order.get_payment_status_display()}"
    story.append(Paragraph(info_text, styles['Normal']))
    story.append(Spacer(1, 15))

    data = [["Urun", "Satici", "Adet", "Birim Fiyat", "Toplam"]]
    for sub in order.sub_orders.all():
        for item in sub.items.all():
            data.append([
                item.product.title[:30],
                sub.seller.store_name[:20],
                str(item.quantity),
                f"{item.price} TL",
                f"{item.get_total_item_price()} TL"
            ])
    data.append(["", "", "", "Genel Toplam:", f"{order.total_amount} TL"])

    t = Table(data, colWidths=[180, 120, 40, 80, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
    ]))
    story.append(t)

    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="fatura-siparis-{order.id}.pdf"'
    return response


def compare_products_view(request):
    """2 veya 3 ürünü yan yana fiyat ve teknik özellik bakımından karşılaştırır."""
    p_ids = request.GET.getlist('id')
    products = Product.objects.filter(id__in=p_ids)[:3]
    return render(request, 'storefront/compare.html', {'products': products})


@login_required
@require_POST
def add_user_address_view(request):
    from marketplace.models import UserAddress
    title = request.POST.get('title', '').strip()
    full_name = request.POST.get('full_name', '').strip()
    phone = request.POST.get('phone', '').strip()
    city = request.POST.get('city', '').strip()
    district = request.POST.get('district', '').strip()
    address_text = request.POST.get('address_text', '').strip()

    if title and full_name and city and address_text:
        UserAddress.objects.create(
            user=request.user,
            title=title,
            full_name=full_name,
            phone=phone,
            city=city,
            district=district,
            address_text=address_text,
            is_default=not request.user.addresses.exists()
        )
        messages.success(request, f"'{title}' adresi adres defterinize eklendi.")
    else:
        messages.error(request, "Lütfen gerekli adres alanlarını doldurunuz.")
    return redirect('account')


@login_required
@require_POST
def delete_user_address_view(request, address_id):
    from marketplace.models import UserAddress
    addr = get_object_or_404(UserAddress, id=address_id, user=request.user)
    addr.delete()
    messages.success(request, "Adresiniz silindi.")
    return redirect('account')


@require_POST
def send_phone_otp_view(request):
    """Kullanıcı telefon numarasına SMS OTP kodu üretir ve gönderir."""
    from marketplace.services.otp_service import OTPService
    phone = request.POST.get('phone', '').strip()
    if not phone:
        return JsonResponse({'status': 'error', 'message': 'Lütfen geçerli bir telefon numarası giriniz.'})

    otp_code, clean_phone = OTPService.generate_otp(phone)
    return JsonResponse({
        'status': 'success',
        'message': f'+90{clean_phone} numarasına 6 haneli doğrulama kodu gönderildi (Simülasyon Kodu: {otp_code} veya 123456).'
    })


@require_POST
def verify_phone_otp_view(request):
    """Kullanıcının girdiği OTP kodunu doğrular ve oturum açar."""
    from marketplace.services.otp_service import OTPService
    phone = request.POST.get('phone', '').strip()
    otp_code = request.POST.get('otp_code', '').strip()

    success, msg, user = OTPService.verify_otp_and_login(phone, otp_code)
    if success and user:
        login(request, user)
        return JsonResponse({'status': 'success', 'message': msg, 'redirect_url': '/'})
    return JsonResponse({'status': 'error', 'message': msg})


@require_POST
def google_oauth2_login_view(request):
    """Google OAuth2 ile tek tıkla hızlı oturum açma."""
    from marketplace.services.social_auth_service import SocialAuthService
    email = request.POST.get('email', 'demo_google_user@gmail.com').strip()
    name = request.POST.get('name', 'Google Kullanıcısı').strip()

    user, msg = SocialAuthService.authenticate_google_user(email, name, 'google-sub-123456')
    if user:
        login(request, user)
        messages.success(request, f"🎉 {msg}")
        return JsonResponse({'status': 'success', 'message': msg, 'redirect_url': '/'})
    return JsonResponse({'status': 'error', 'message': msg})


def track_shipping_view(request, suborder_id):
    """Satıcı veya müşteri için canlı Yurtiçi/Aras kargo takip durumunu getirir."""
    from marketplace.models import SubOrder
    from marketplace.services.shipping_service import ShippingService

    sub_order = get_object_or_404(SubOrder, id=suborder_id)
    tracking_no = sub_order.parent_order.tracking_number or f"YK-{sub_order.id}987654"
    company_code = 'YURTICI' if 'Yurtiçi' in (sub_order.parent_order.shipping_company or 'Yurtiçi') else 'ARAS'

    cargo_info = ShippingService.get_live_cargo_tracking(tracking_no, company_code)
    return JsonResponse({'status': 'success', 'cargo_info': cargo_info})


@login_required
def generate_shipping_label_view(request, suborder_id):
    """Satıcı için yazdırılabilir standart Code128 barkodlu kargo etiketi şablonu."""
    from marketplace.models import SubOrder
    from marketplace.services.shipping_service import ShippingService

    sub_order = get_object_or_404(SubOrder, id=suborder_id)
    if not (request.user.is_superadmin() or sub_order.seller.user == request.user):
        messages.error(request, "Bu kargo etiketini görüntüleme yetkiniz yok!")
        return redirect('store_index')

    tracking_no = sub_order.parent_order.tracking_number or f"YK-{sub_order.id}987654"
    barcode_svg = ShippingService.generate_code128_svg_barcode(tracking_no)

    return render(request, 'seller/shipping_label.html', {
        'sub_order': sub_order,
        'tracking_no': tracking_no,
        'barcode_svg': barcode_svg,
        'today': timezone.now()
    })


@require_POST
def api_generate_ai_description_view(request):
    """Satıcı ürün eklerken AI ile otomatik SEO açıklaması ve etiket üretir."""
    from marketplace.services.ai_content_service import AIContentService
    title = request.POST.get('title', '').strip()
    category_name = request.POST.get('category_name', 'Genel').strip()

    if not title:
        return JsonResponse({'status': 'error', 'message': 'Ürün başlığı boş olamaz.'})

    res = AIContentService.generate_product_description(title, category_name)
    return JsonResponse({'status': 'success', 'data': res})


def api_b2b_wholesale_pricing_view(request):
    """Toptan B2B alımlarda dinamik kademeli fiyat hesaplaması yapar."""
    from marketplace.services.product_service import ProductService
    price = request.GET.get('price', '100.00')
    quantity = request.GET.get('quantity', '1')

    data = ProductService.calculate_b2b_wholesale_price(price, quantity)
    return JsonResponse({'status': 'success', 'b2b_data': data})


@login_required
def generate_seller_payout_pdf(request):
    """Satıcı için resmi banka komisyon düşülmüş hakediş dekontu PDF üretir."""
    if not request.user.is_seller():
        messages.error(request, "Bu dekontu indirme yetkiniz yok!")
        return redirect('store_index')

    from io import BytesIO
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    seller = request.user.seller_profile
    sub_orders = seller.sub_orders.select_related('parent_order').all()

    total_gross = sum(s.subtotal for s in sub_orders) if sub_orders.exists() else Decimal("0.00")
    total_commission = sum(s.commission_fee for s in sub_orders) if sub_orders.exists() else Decimal("0.00")
    net_payout = total_gross - total_commission

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0f172a'))
    story.append(Paragraph(f"HAKEDİŞ VE KOMİSYON DEKONTU - {seller.store_name}", title_style))
    story.append(Spacer(1, 10))

    info_text = f"<b>Magaza:</b> {seller.store_name}<br/><b>IBAN:</b> {seller.iban}<br/><b>Komisyon Orani:</b> %{seller.commission_rate}<br/><b>Tarih:</b> {timezone.now().strftime('%d/%m/%Y %H:%M')}"
    story.append(Paragraph(info_text, styles['Normal']))
    story.append(Spacer(1, 15))

    data = [
        ["Finansal Metrik", "Tutar (TL)"],
        ["Toplam Brut Satis Tutari", f"{total_gross:,.2f} TL"],
        ["Platform Komisyon Kesintisi", f"-{total_commission:,.2f} TL"],
        ["Saticiya Aktarilacak Net Hakedis", f"{net_payout:,.2f} TL"]
    ]

    t = Table(data, colWidths=[300, 200])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#6366f1')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor('#10b981')),
    ]))
    story.append(t)
    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="hakedis-dekontu-{seller.store_name}.pdf"'
    return response


@login_required
@require_POST
def seller_bulk_import_products(request):
    """Satıcının yüklediği CSV dosyası ile toplu ürün kaydı yapar."""
    if not request.user.is_seller():
        messages.error(request, "Bu işlem için satıcı yetkiniz yok!")
        return redirect('store_index')

    csv_file = request.FILES.get('csv_file')
    if not csv_file:
        messages.error(request, "Lütfen bir CSV dosyası seçiniz.")
        return redirect('seller_dashboard')

    from marketplace.services.bulk_import_service import BulkImportService
    success, msg, count = BulkImportService.import_products_from_csv(request.user.seller_profile, csv_file)

    if success and count > 0:
        messages.success(request, f"🎉 {msg}")
    else:
        messages.error(request, f"⚠️ {msg}")

    return redirect('seller_dashboard')


@login_required
def seller_download_import_template(request):
    """Satıcılar için örnek CSV toplu ürün yükleme şablonu indirir."""
    from django.http import HttpResponse
    from marketplace.services.bulk_import_service import BulkImportService

    csv_content = BulkImportService.generate_sample_csv_template()
    response = HttpResponse(csv_content, content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="ornek_toplu_urun_sablonu.csv"'
    return response


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def payment_webhook_view(request):
    """
    Sanal Pos / Ödeme Ağ Geçidi Webhook Uç Noktası.
    Banka veya ödeme altyapısından gelen asenkron bildirimleri 
    HMAC-SHA256 imzası ile doğrulayıp sipariş durumunu otomatik günceller.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Yalnızca POST istekleri kabul edilir.'}, status=405)

    signature = request.headers.get('X-Signature') or request.META.get('HTTP_X_SIGNATURE')
    raw_body = request.body.decode('utf-8')

    if signature and not IyzicoMarketplaceSimulator.verify_webhook_signature(raw_body, signature):
        return JsonResponse({'status': 'error', 'message': 'Geçersiz Webhook İmza (HMAC Verification Failed)!'}, status=400)

    try:
        data = json.loads(raw_body)
        order_id = data.get('order_id')
        event_type = data.get('event_type')  # PAYMENT_SUCCESS, PAYMENT_FAILED
        payment_id = data.get('payment_id')

        if order_id:
            order = Order.objects.filter(id=order_id).first()
            if order:
                if event_type == 'PAYMENT_SUCCESS':
                    order.sub_orders.update(status='PROCESSING')
                    # Asenkron Bildirim Gönder
                    from marketplace.services.background_job_service import BackgroundJobService
                    BackgroundJobService.send_async_email(
                        subject=f"Siparişiniz Alındı #{order.id}",
                        message=f"Sayın {order.customer.username}, #{order.id} numaralı siparişinizin ödemesi alındı.",
                        recipient_list=[order.customer.email]
                    )
                elif event_type == 'PAYMENT_FAILED':
                    order.sub_orders.update(status='CANCELLED')

                return JsonResponse({'status': 'success', 'order_id': order.id, 'event': event_type})

        return JsonResponse({'status': 'received', 'message': 'Webhook işlendi.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
















