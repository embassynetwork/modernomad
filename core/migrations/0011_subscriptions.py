# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0010_auto_20151015_2140'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('price', models.DecimalField(max_digits=9, decimal_places=2)),
                ('description', models.CharField(max_length=256, null=True, blank=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='+', default=1, to=settings.AUTH_USER_MODEL)),
                ('location', models.ForeignKey(to='core.Location')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('note', models.TextField(null=True, blank=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('subscription', models.ForeignKey(related_name='communitysubscription_notes', to='core.Subscription')),
            ],
        ),
        migrations.RemoveField(
            model_name='communitysubscription',
            name='bills',
        ),
        migrations.RemoveField(
            model_name='communitysubscription',
            name='location',
        ),
        migrations.RemoveField(
            model_name='communitysubscription',
            name='user',
        ),
        migrations.RemoveField(
            model_name='roomsubscription',
            name='bills',
        ),
        migrations.RemoveField(
            model_name='roomsubscription',
            name='location',
        ),
        migrations.RemoveField(
            model_name='roomsubscription',
            name='user',
        ),
        migrations.AlterField(
            model_name='room',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.DeleteModel(
            name='CommunitySubscription',
        ),
        migrations.DeleteModel(
            name='RoomSubscription',
        ),
        migrations.AddField(
            model_name='subscriptionbill',
            name='subscription',
            field=models.ForeignKey(related_name='bills', to='core.Subscription', null=True),
        ),
    ]
