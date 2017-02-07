from django.db import models

CURRENCY_CHOICES = (
    ("USD", "United States Dollar"),
    ("CZK", "Czech Republic Koruna"),
    ("PLN", "Polish Zloty"),
    ("EUR", "Euro"),
)


class Currency(models.Model):
    created_timestamp = models.PositiveIntegerField()
    base = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default=CURRENCY_CHOICES[0][0], primary_key=True)


class Rate(models.Model):
    base = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='rates')
    code = models.CharField(max_length=3, choices=CURRENCY_CHOICES, blank=False)
    rate = models.DecimalField(blank=False, decimal_places=12, max_digits=16)


class ConverterResponse(models.Model):

    base = models.CharField(max_length=3, choices=CURRENCY_CHOICES, blank=False)
    target = models.CharField(max_length=3, choices=CURRENCY_CHOICES, blank=False)
    amount = models.DecimalField(blank=False, decimal_places=12, max_digits=16)
    result = models.DecimalField(blank=False, decimal_places=12, max_digits=16)

    class Meta:
        managed = False
