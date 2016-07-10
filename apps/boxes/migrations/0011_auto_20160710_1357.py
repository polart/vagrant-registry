# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-10 13:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boxes', '0010_auto_20160710_1348'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='boxprovider',
            name='description',
        ),
        migrations.AddField(
            model_name='box',
            name='short_description',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='boxversion',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='box',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='box',
            name='name',
            field=models.CharField(max_length=30),
        ),
    ]
