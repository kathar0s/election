# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-04 16:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('election', '0009_survey_unique_str'),
    ]

    operations = [
        migrations.CreateModel(
            name='Office',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=40, verbose_name='이름')),
                ('aliases', models.CharField(default='', help_text='콤마로 구분', max_length=250, verbose_name='별칭')),
            ],
            options={
                'verbose_name': '여론조사 의뢰기관',
                'verbose_name_plural': '여론조사 의뢰기관 목록',
            },
        ),
        migrations.RemoveField(
            model_name='survey',
            name='unique_str',
        ),
    ]
