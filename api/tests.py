import time
from unittest.mock import patch

from decimal import Decimal, getcontext
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from api.models import CURRENCY_CHOICES
from api.views import ConvertCurrency

"""
List of tests:
    1. Rates generation from OE - test that rates for all required currencies are populated
    2. Rates are being updated after specified interval
    3. Conversion - with fake rates models, having integer rates fold to ten, make sure that rates are generated
    correctly (in case of simple rates, result is predictable and observable)
    4. Conversion - test validity by dividing resulting amount on a rate for corresponding currency
    5. Negative scenarios for currency conversion
        - test that 404 is returned for non-existent currencies
        - test that HTTP_400_BAD_REQUEST is returned for incorrectly set parameters
        - non-existent source/target currency
        - amount is mixed with currency specification in route
        - amount is a non-digit
"""


def _get_fake_oe_response():
    return {
        'CZK': 10.0,
        'PLN': 100.0,
        'EUR': 1000.0
    }


class GenerationTests(APITestCase):
    SUPPORTED_CURRENCIES = [v[0] for v in CURRENCY_CHOICES]
    CURRENCY_LIST = reverse('currency-list')
    BASE = 'USD'

    def setUp(self):
        self.SUPPORTED_CURRENCIES.sort()
        getcontext().prec = 11

    def test_oe_rates_generation(self):
        """
        Make sure that database is populated on the first request
        Check that generated rates have all supported bases
        :return:
        """
        response = self.client.get(self.CURRENCY_LIST)
        fetched_currencies = [_['base'] for _ in response.data]  # extract currency code from detail URL
        fetched_currencies.sort()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.SUPPORTED_CURRENCIES), len(response.data))
        self.assertEqual(fetched_currencies, self.SUPPORTED_CURRENCIES)

    @patch('api.util.UPDATE_INTERVAL', new=1)
    def test_rates_update(self):
        """
        Set update interval to one second, and make sure that currency rates update in time
        :return:
        """
        first_timestamp = self.client.get(self.CURRENCY_LIST).data[0]['created_timestamp']
        # Check that currencies have the same timestamp
        self.assertEqual(first_timestamp, self.client.get(self.CURRENCY_LIST).data[0]['created_timestamp'])
        time.sleep(2)
        # Check that timestamp changed after update interval has passed
        self.assertLess(first_timestamp, self.client.get(self.CURRENCY_LIST).data[0]['created_timestamp'])

    @patch('api.util.get_rates_from_openexchange', new=_get_fake_oe_response)
    def test_rates_generation_validity(self):
        """
        Fake response from openexchange and make sure that currency conversion works as expected
        """
        one = Decimal(1)
        self.assertEqual(self._get_decimal_response('CZK', 'USD', 10), one)
        self.assertEqual(self._get_decimal_response('PLN', 'USD', 100), one)
        self.assertEqual(self._get_decimal_response('EUR', 'USD', 1000), one)
        self.assertEqual(self._get_decimal_response('PLN', 'EUR', 10), Decimal(100))

    def test_conversion(self):
        """
        Make sure that conversion result equals rate multiplied by amount
        :return:
        """
        rates = self.client.get(self.CURRENCY_LIST).data
        for rate in rates[0]['rates']:
            self.assertEqual(self._get_decimal_response('USD', rate['code'], 10),
                             Decimal(10) * Decimal(rate['rate']))
            self.assertEqual(self._get_decimal_response(rate['code'], 'USD', 10),
                             Decimal(1) / Decimal(rate['rate']) * Decimal(10))

    def test_exceptions(self):
        """
        Test various ways of incorrect calls to convert API
        :return:
        """
        factory = APIRequestFactory()
        view = ConvertCurrency.as_view()
        amount = 10
        request = factory.get(self._get_currency_convert_url('USD', 'PLN', amount))
        self.assertEqual(view(request, base='USD').status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(view(request, base='USD', target='PLN').exception, "Required argument is missing: 'amount'")
        self.assertEqual(view(request, base='USD', target='USD', amount=amount).exception,
                         "Same currency is given as source and target")
        self.assertEqual(view(request, base='USD', target='EUR', amount='text').exception,
                         "Amount must be float or integer")
        self.assertEqual(view(request, base='DSS', target='USD', amount=amount).exception,
                         "Could not find corresponding currency rate. Please check 'base' parameter")
        self.assertEqual(view(request, base='USD', target='DSS', amount=amount).exception,
                         "Could not find corresponding currency rate. Please check 'target' parameter")

    @staticmethod
    def _get_currency_convert_url(base, target, amount):
        return reverse('currency-convert',
                       kwargs={'base': base, 'target': target, 'amount': amount})

    def _get_decimal_response(self, base, target, amount):
        return Decimal(self.client.get(self._get_currency_convert_url(base, target, amount)).data['result'])
