# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-05 17:39
from __future__ import unicode_literals

import apps.boxes.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('boxes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoxChunkedUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upload_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_completed', models.DateTimeField(blank=True, null=True)),
                ('file', models.FileField(max_length=255, upload_to=apps.boxes.models.chunked_upload_path)),
                ('filename', models.CharField(max_length=255)),
                ('offset', models.BigIntegerField(default=0)),
                ('status', models.CharField(choices=[('S', 'Started'), ('I', 'In progress'), ('C', 'Completed')], default='S', max_length=1)),
                ('name', models.CharField(max_length=255)),
                ('checksum_type', models.CharField(choices=[('md5', 'md5'), ('sha1', 'sha1'), ('sha256', 'sha256')], default='sha256', max_length=10)),
                ('checksum', models.CharField(max_length=128)),
                ('version', models.CharField(max_length=40, validators=[django.core.validators.RegexValidator(message='Invalid version number. It must be of the format X.Y.Z where X, Y, and Z are all positive integers.', regex='^(\\d+)\\.(\\d+)(\\.(\\d+))?$')])),
                ('provider', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='box_uploads', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]