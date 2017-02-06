from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.generics import RetrieveAPIView
from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response
from api.serializers import CurrencySerializer, RatesSerializer, ConverterResponseSerializer
from api.models import Currency, ConverterResponse, Rate
from api.util import update_queryset


# TODO: add some exception handling
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
        print(kwargs)
        base = kwargs['base']
        target = kwargs['target']
        amount = kwargs['amount']
        for rate in self.get_serializer(self.get_object()).data['rates']:
            if rate['code'] == target:
                result = rate['rate'] * float(amount)
                serializer = ConverterResponseSerializer(
                    ConverterResponse(base=base, target=target, amount=amount, result=result))
                return Response(serializer.data, status=HTTP_200_OK)

