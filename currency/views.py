import urllib.request
import datetime

from rest_framework import viewsets, generics, status, response
from rest_framework.parsers import JSONParser
from currency.serializers import CurrencySerializer, RatesSerializer, ConverterResponseSerializer
from currency.models import Currency, ConverterResponse, Rate, CURRENCY_CHOICES

EXCHANGE_RATES_API = 'https://openexchangerates.org/api/latest.json'
UPDATE_INTERVAL = 60 * 60 * 24
APP_ID = '0073e9ef358945e0a473163268c74586'


# Create your views here.
# TODO: add some exception handling
class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()

    def get_queryset(self):
        """
        If this is the first time API is called, create rates from openexchange data.
        If data is outdated, perform update
        """
        queryset = super().get_queryset()
        if len(queryset) == 0:
            queryset = self.build_currency_rates(queryset)
        elif self.is_outdated(queryset):
            Currency.objects.all().delete()
            queryset = self.build_currency_rates(queryset)

        return queryset

    def build_currency_rates(self, queryset):
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
        return queryset.all()

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

    @staticmethod
    def is_outdated(queryset):
        created_datetime = queryset[0].created_timestamp  # Grab first currency, cus they are all updates at once
        return int(datetime.datetime.now().timestamp()) - created_datetime > UPDATE_INTERVAL


class RateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RatesSerializer
    queryset = Rate.objects.all()


class ConvertCurrency(generics.RetrieveAPIView):
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()
    lookup_url_kwarg = 'base'

    # def get_queryset(self):
    #     base = self.kwargs['base']
    #     return Currency.objects.filter(base=base)

    def get(self, request, *args, **kwargs):
        base = kwargs['base']
        target = kwargs['target']
        amount = kwargs['amount']
        for rate in self.get_serializer(self.get_object()).data['rates']:
            if rate['code'] == target:
                print(rate['rate'])
                result = rate['rate'] * float(amount)
                serializer = ConverterResponseSerializer(
                    ConverterResponse(base=base, target=target, amount=amount, result=result))
                return response.Response(serializer.data, status=status.HTTP_200_OK)
