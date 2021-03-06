from rest_framework import serializers

from api.models import Currency, Rate, ConverterResponse


class RatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = ('base', 'code', 'rate')


class CurrencySerializer(serializers.ModelSerializer):

    rates = RatesSerializer(many=True)

    class Meta:
        model = Currency
        fields = ('created_timestamp', 'base', 'rates')


class ConverterResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConverterResponse
        fields = ('base', 'target', 'amount', 'result')
