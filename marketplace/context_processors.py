def cart_info(request):
    """
    Sepetteki toplam ürün miktarını, kullanıcının okunmamış bildirim sayısını,
    favorilediği ürün sayısını ve okunmamış mesaj sayısını tüm şablonlarda 
    küresel olarak erişilebilir kılar.
    """
    cart = request.session.get('cart', {})
    total_qty = 0
    try:
        total_qty = sum(int(qty) for qty in cart.values())
    except Exception:
        pass
    
    unread_notifications_count = 0
    favorites_count = 0
    unread_messages_count = 0
    favorited_product_ids = set()
    
    if request.user.is_authenticated:
        unread_notifications_count = request.user.notifications.filter(is_read=False).count()
        favorites_count = request.user.favorites.count()
        unread_messages_count = request.user.received_messages.filter(is_read=False).count()
        favorited_product_ids = set(request.user.favorites.values_list('product_id', flat=True))
    
    from django.conf import settings
    currency = request.session.get('currency', 'TRY')
    if currency not in getattr(settings, 'CURRENCY_RATES', {}):
        currency = 'TRY'
    rates = getattr(settings, 'CURRENCY_RATES', {'TRY': 1.0, 'USD': 33.0, 'EUR': 36.0})
    symbols = getattr(settings, 'CURRENCY_SYMBOLS', {'TRY': '₺', 'USD': '$', 'EUR': '€'})
    rate = rates.get(currency, 1.0)
    symbol = symbols.get(currency, '₺')

    return {
        'cart_count': total_qty,
        'unread_notifications_count': unread_notifications_count,
        'favorites_count': favorites_count,
        'unread_messages_count': unread_messages_count,
        'active_currency': currency,
        'active_currency_symbol': symbol,
        'currency_rate': rate,
        'favorited_product_ids': favorited_product_ids,
    }
