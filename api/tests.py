import time
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from api.models import Currency, CURRENCY_CHOICES, Rate
from api.views import CurrencyViewSet, ConvertCurrency

"""
List of tests:
    1. Rates generation from OE - test that rates for all required currencies are populated
    2. Rates are being updated after specified interval
    3. Conversion - with fake rates models, having integer rates fold to ten, make sure that rates are generated
    correctly (in case of simple rates, result is predictable and observable)
    4. Conversion - test validity by dividing resulting amount on a rate for corresponding currency
    5. Negative scenarios for currency - test that 404 is returned for non-existent currencies
    6. Negative scenarios for conversion - test that ValidationError is returned for incorrectly set parameters
        - non-existent source/target currency
        - amount is mixed with currency specification in route
        - amount is a non-digit
"""


def _get_fake_oe_response():
    rates = {
        'timestamp': 0000000,
        'base': 'USD',
        'rates': {}
    }
    rate = 10
    for curr in CURRENCY_CHOICES[1:]:
        rates[curr] = rate
        rate *= 10
    return rates


class GenerationTests(APITestCase):

    SUPPORTED_CURRENCIES = [v[0] for v in CURRENCY_CHOICES]
    CURRENCY_LIST = reverse('currency-list')
    BASE = 'USD'

    @staticmethod
    def _get_currency_convert_url(base, target, amount):
        return reverse('currency-convert',
                       kwargs={'base': base, 'target': target, 'amount': amount})

    def setUp(self):
        self.SUPPORTED_CURRENCIES.sort()

    def test_oe_rates_generation(self):
        """
        Make sure that database is populated on the first request
        Check that generated rates have all supported bases
        :return:
        """
        print('test 1')
        response = self.client.get(self.CURRENCY_LIST)
        fetched_currencies = [_['base'].split('/')[-2] for _ in response.data]
        fetched_currencies.sort()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.SUPPORTED_CURRENCIES), len(response.data))
        self.assertEqual(fetched_currencies, self.SUPPORTED_CURRENCIES)
        print('test 1 passed')

    @patch('api.util.UPDATE_INTERVAL', new=1)
    def test_rates_update(self):
        print('test 2')
        view = CurrencyViewSet.as_view({'get': 'list'})
        request = APIRequestFactory().get(self.CURRENCY_LIST)
        first_timestamp = view(request).data[0]['created_timestamp']
        # Check that currencies have the same timestamp
        self.assertEqual(first_timestamp, view(request).data[0]['created_timestamp'])
        time.sleep(2)
        # Check that timestamp changed after update interval has passed
        self.assertLess(first_timestamp, view(request).data[0]['created_timestamp'])
        print('test 2 passed')

    @patch('api.util.get_rates_from_openexchange', new=_get_fake_oe_response)
    def test_rates_generation_validity(self):
        print('test 3')
        view = ConvertCurrency.as_view()
        url = self._get_currency_convert_url('USD', 'CZK', 1.0)
        print(url)
        response = self.client.get(url)
        print(response.data)


