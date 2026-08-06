import urllib.request
import json
from decimal import Decimal
from django.core.cache import cache

class CurrencyService:
    """
    Canlı Döviz Kuru ve Para Birimi Dönüştürücü Servisi.
    Desteklenen Birimler: TRY (₺), USD ($), EUR (€).
    """
    FALLBACK_RATES = {
        'TRY': Decimal("1.00"),
        'USD': Decimal("0.031"), # $1 = 32.25 TL
        'EUR': Decimal("0.028"), # €1 = 35.70 TL
    }

    SYMBOLS = {
        'TRY': '₺',
        'USD': '$',
        'EUR': '€',
    }

    @classmethod
    def get_live_rates(cls):
        """
        Canlı döviz kurlarını getirir ve 1 saat boyunca önbelleğe alır.
        Hata durumunda varsayılan sabit kurlara (FALLBACK_RATES) güvenli düşüş yapar.
        """
        rates = cache.get('live_currency_rates')
        if rates:
            return rates

        try:
            req = urllib.request.Request(
                "https://api.exchangerate-api.com/v4/latest/TRY",
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode())
                api_rates = data.get('rates', {})
                rates = {
                    'TRY': Decimal("1.00"),
                    'USD': Decimal(str(round(api_rates.get('USD', 0.031), 4))),
                    'EUR': Decimal(str(round(api_rates.get('EUR', 0.028), 4))),
                }
                cache.set('live_currency_rates', rates, 3600)
                return rates
        except Exception:
            return cls.FALLBACK_RATES

    @classmethod
    def convert_price(cls, amount_in_try, target_currency='TRY'):
        """
        TL cinsinden verilen fiyatı hedef para birimine dönüştürür.
        """
        if not amount_in_try:
            return f"0.00 {cls.SYMBOLS.get(target_currency, '₺')}"

        amount = Decimal(str(amount_in_try))
        rates = cls.get_live_rates()
        rate = rates.get(target_currency, Decimal("1.00"))
        symbol = cls.SYMBOLS.get(target_currency, '₺')

        converted = round(amount * rate, 2)
        if target_currency == 'TRY':
            return f"{converted:,.2f} {symbol}"
        else:
            return f"{symbol}{converted:,.2f}"

