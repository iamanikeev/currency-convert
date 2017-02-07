from decimal import Decimal, InvalidOperation
from django.http import Http404
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.generics import RetrieveAPIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from api.serializers import CurrencySerializer, RatesSerializer, ConverterResponseSerializer
from api.models import Currency, ConverterResponse, Rate
from api.util import update_queryset


class CurrencyViewSet(ReadOnlyModelViewSet):
    """
    Get currencies list and detailed information on particular currency
    """
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()

    def get_queryset(self):
        """
        Make sure that data exists and is not outdated
        :return:
        """
        queryset = super().get_queryset()
        return update_queryset(queryset)


class RateViewSet(ReadOnlyModelViewSet):
    """
    Get rates list and detailed information on particular rate
    """
    serializer_class = RatesSerializer
    queryset = Rate.objects.all()


class ConvertCurrency(RetrieveAPIView):
    """
    Convert specified amount of given currency into target currency according to rates
    """
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()
    lookup_url_kwarg = 'base'

    def get_queryset(self):
        """
        Make sure that data exists and is not outdated
        :return:
        """
        queryset = super().get_queryset()
        return update_queryset(queryset)

    def get(self, request, *args, **kwargs):
        try:
            base = kwargs['base']
            target = kwargs['target']
            amount = kwargs['amount']
        except KeyError as ke:
            return Response(status=HTTP_400_BAD_REQUEST, exception="Required argument is missing: {}".format(ke))

        if base == target:
            return Response(status=HTTP_400_BAD_REQUEST, exception="Same currency is given as source and target")

        try:
            amount = Decimal(amount)
        except InvalidOperation:
            return Response(status=HTTP_400_BAD_REQUEST, exception="Amount must be float or integer")

        try:
            for rate in self.get_serializer(self.get_object()).data['rates']:
                if rate['code'] == target:
                    result = Decimal(rate['rate']) * amount
                    serializer = ConverterResponseSerializer(
                        ConverterResponse(base=base, target=target, amount=amount, result=result))
                    return Response(serializer.data, status=HTTP_200_OK)
        except Http404:
            return Response(status=HTTP_400_BAD_REQUEST,
                            exception="Could not find corresponding currency rate. Please check 'base' parameter")
        return Response(status=HTTP_400_BAD_REQUEST,
                        exception="Could not find corresponding currency rate. Please check 'target' parameter")
