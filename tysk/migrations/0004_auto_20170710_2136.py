# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-10 18:36
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tysk', '0003_auto_20170710_1113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='main',
            name='time',
            field=models.TimeField(default=datetime.time(21, 36, 17, 34648), verbose_name='час вимірювання'),
        ),
    ]
