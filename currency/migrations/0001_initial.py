# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-04 20:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('created_timestamp', models.PositiveIntegerField()),
                ('base', models.CharField(choices=[('USD', 'United States Dollar'), ('CZK', 'Czech Republic Koruna'), ('PLN', 'Polish Zloty'), ('EUR', 'Euro')], default='USD', max_length=3, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(choices=[('USD', 'United States Dollar'), ('CZK', 'Czech Republic Koruna'), ('PLN', 'Polish Zloty'), ('EUR', 'Euro')], max_length=3)),
                ('rate', models.FloatField()),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rates', to='currency.Currency')),
            ],
        ),
    ]
