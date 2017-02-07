from datetime import datetime
from decimal import Decimal
import requests
from api.models import CURRENCY_CHOICES, Currency, Rate

EXCHANGE_RATES_API = 'https://openexchangerates.org/api/latest.json'
APP_ID = '0073e9ef358945e0a473163268c74586'
UPDATE_INTERVAL = 60 * 60 * 24


def get_rates_from_openexchange():
    response = requests.get(EXCHANGE_RATES_API, params={'app_id': APP_ID}).json()
    rates_filtered = {}
    # Get rate for all currencies that we support, except USD, because it is always a base one
    for code in (v[0] for v in CURRENCY_CHOICES[1:]):
        if code in response['rates']:
            rates_filtered[code] = response['rates'][code]
        else:
            raise KeyError("Invalid currency code was specified in api.models.CURRENCY_CHOICES: {}"
                           .format(code))
    return rates_filtered


def build_currency_rates(queryset):
    rates = get_rates_from_openexchange()
    now = int(datetime.now().timestamp())
    # Add base (USD) api
    usd = Currency(base='USD', created_timestamp=now)
    usd.save()

    for code, rate_to_usd in rates.items():
        rate_to_usd = Decimal(rate_to_usd)
        # Add corresponding rates for USD
        Rate(base=usd, code=code, rate=rate_to_usd).save()

        # Add each of allowed currencies and populate its rates
        curr = Currency(base=code, created_timestamp=now)
        curr.save()
        Rate(base=curr, code='USD', rate=Decimal(1) / rate_to_usd).save()
        for curr_code, rate_to_curr in (_ for _ in rates.items() if _[0] != code):
            Rate(base=curr, code=curr_code, rate=Decimal(1) / rate_to_usd * Decimal(rate_to_curr)).save()
    return queryset.all()


def is_outdated(queryset):
    created_datetime = queryset[0].created_timestamp  # Grab first api, cus they are all updates at once
    return int(datetime.now().timestamp()) - created_datetime > UPDATE_INTERVAL


def update_queryset(queryset):
    if len(queryset) == 0:
        queryset = build_currency_rates(queryset)
    elif is_outdated(queryset):
        Currency.objects.all().delete()
        queryset = build_currency_rates(queryset)
    return queryset
