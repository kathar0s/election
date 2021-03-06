# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-02 20:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('election', '0003_auto_20170502_2008'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='icon',
            field=models.ImageField(blank=True, upload_to='', verbose_name='아이콘'),
        ),
    ]
