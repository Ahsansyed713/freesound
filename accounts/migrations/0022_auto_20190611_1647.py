# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-11 16:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_auto_20190222_1105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailpreferencetype',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]