# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0010_auto_20151015_2140'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitysubscription',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 2, 17, 19, 16, 812989, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='communitysubscription',
            name='created_by',
            field=models.ForeignKey(related_name='+', default=1, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='communitysubscription',
            name='description',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='communitysubscription',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 2, 17, 19, 18, 324299, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='roomsubscription',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 2, 17, 19, 19, 836101, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='roomsubscription',
            name='created_by',
            field=models.ForeignKey(related_name='+', default=1, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='roomsubscription',
            name='description',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='roomsubscription',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 2, 17, 19, 22, 341548, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='room',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
    ]
