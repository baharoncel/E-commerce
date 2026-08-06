import os
from decimal import Decimal
from django import template
from django.conf import settings

from marketplace.services.currency_service import CurrencyService

register = template.Library()

@register.filter
def convert_price(value, request):
    """
    Converts a price in TRY (value) to the active session currency (TRY, USD, EUR).
    """
    if value is None:
        return "0.00 ₺"
    
    currency = request.session.get('currency', 'TRY')
    return CurrencyService.convert_price(value, currency)


@register.filter
def sub(value, arg):
    """Subtracts the arg from the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0


@register.simple_tag
def cdn_url(path):
    """
    CDN tabanlı uç nokta teslimat URL'si üretir.
    CDN_BASE_URL tanımlı ise CDN adresini ekler, aksi halde yerel URL döner.
    """
    if not path:
        return ''
    cdn_base = getattr(settings, 'CDN_BASE_URL', os.getenv('CDN_BASE_URL', ''))
    if cdn_base:
        cdn_base = cdn_base.rstrip('/')
        if str(path).startswith('http://') or str(path).startswith('https://'):
            return path
        clean_path = str(path).lstrip('/')
        return f"{cdn_base}/{clean_path}"
    return path


@register.simple_tag
def responsive_srcset(product):
    """
    Product nesnesinin responsive srcset dizgisini döner.
    """
    if hasattr(product, 'get_srcset'):
        return product.get_srcset()
    return ''


@register.simple_tag
def lqip_placeholder(product):
    """
    Blur-Up için base64 placeholder döner.
    """
    if hasattr(product, 'lqip_base64') and product.lqip_base64:
        return product.lqip_base64
    return 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect width="100%" height="100%" fill="%23eeeeee"/></svg>'


@register.filter
def mask_phone(value):
    from marketplace.services.data_masking_service import DataMaskingService
    return DataMaskingService.mask_phone(value)

@register.filter
def mask_card(value):
    from marketplace.services.data_masking_service import DataMaskingService
    return DataMaskingService.mask_credit_card(value)

@register.filter
def mask_email(value):
    from marketplace.services.data_masking_service import DataMaskingService
    return DataMaskingService.mask_email(value)

@register.filter
def mask_address(value):
    from marketplace.services.data_masking_service import DataMaskingService
    return DataMaskingService.mask_address(value)




