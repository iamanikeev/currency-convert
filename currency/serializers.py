from rest_framework import serializers
from currency.models import Currency, CURRENCY_CHOICES, Rate, ConverterResponse


class RatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = ('base', 'code', 'rate')


class CurrencySerializer(serializers.ModelSerializer):

    rates = RatesSerializer(many=True)
    base = serializers.HyperlinkedRelatedField(view_name='currency-detail', read_only=True)

    class Meta:
        model = Currency
        fields = ('created_timestamp', 'base', 'rates')


class ConverterResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConverterResponse
        fields = ('base', 'target', 'amount', 'result')
