# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-11 15:52
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tysk', '0004_auto_20170710_2136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='main',
            name='date',
            field=models.DateField(default=datetime.date(2017, 8, 11), verbose_name='дата вимірювання'),
        ),
        migrations.AlterField(
            model_name='main',
            name='time',
            field=models.TimeField(default=datetime.time(18, 52, 59, 685296), verbose_name='час вимірювання'),
        ),
    ]
