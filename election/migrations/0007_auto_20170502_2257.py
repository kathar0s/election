# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-02 22:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('election', '0006_auto_20170502_2025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agency',
            name='name',
            field=models.CharField(default='', max_length=40, verbose_name='이름'),
        ),
    ]
