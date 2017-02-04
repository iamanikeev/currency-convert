import urllib.request
import datetime
from rest_framework import viewsets
from rest_framework.parsers import JSONParser
from currency.serializers import CurrencySerializer, RatesSerializer
from currency.models import Currency, Rate, CURRENCY_CHOICES

EXCHANGE_RATES_API = 'https://openexchangerates.org/api/latest.json'
APP_ID = '0073e9ef358945e0a473163268c74586'


# Create your views here.
class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        # If this is the first time API is called, create rates from openexchange data. If
        if len(serializer.data) == 0:
            self.build_currency_rates()
        elif self.is_outdated(serializer.data[0]):  # Grab first currency, cus they are all updates at once
            Currency.objects.all().delete()
            self.build_currency_rates()

        return super(CurrencyViewSet, self).list(request, *args, **kwargs)

    @staticmethod
    def get_rates_from_openexchange():
        with urllib.request.urlopen('{}?app_id={}'.format(EXCHANGE_RATES_API, APP_ID)) as response:
            response_parsed = JSONParser().parse(response)
            rates_filtered = {}
            # Get rate for all currencies that we support, except USD, because it is always a base one
            for code in (v[0] for v in CURRENCY_CHOICES[1:]):
                if code in response_parsed['rates']:
                    rates_filtered[code] = response_parsed['rates'][code]
                else:
                    raise KeyError("Invalid currency code was specified in currency.models.CURRENCY_CHOICES: {}"
                                   .format(code))
        return rates_filtered

    def build_currency_rates(self):
        rates = self.get_rates_from_openexchange()
        now = int(datetime.datetime.now().timestamp())
        # Add base (USD) currency
        usd = Currency(base='USD', created_timestamp=now)
        usd.save()

        for code, rate_to_usd in rates.items():
            # Add corresponding rates for USD
            Rate(base=usd, code=code, rate=rate_to_usd).save()

            # Add each of allowed currencies and populate its rates
            curr = Currency(base=code, created_timestamp=now)
            curr.save()
            Rate(base=curr, code='USD', rate=1 / rate_to_usd).save()
            for curr_code, rate_to_curr in (_ for _ in rates.items() if _[0] != code):  # Oh boy, this seems ugly...
                Rate(base=curr, code=curr_code, rate=1 / rate_to_usd * rate_to_curr).save()

    @staticmethod
    def is_outdated(currency_info):
        created_datetime = [v for k, v in currency_info.items() if k == 'created_timestamp'][0]
        return int(datetime.datetime.now().timestamp()) - created_datetime > 60 * 60 * 24


class RateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RatesSerializer
    queryset = Rate.objects.all()
