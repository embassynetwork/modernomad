# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(default=b'standard', max_length=32, choices=[(b'system', b'System'), (b'standard', b'Standard')])),
                ('admins', models.ManyToManyField(help_text=b'May be blank', related_name='accounts_administered', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('symbol', models.CharField(max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.IntegerField()),
                ('account', models.ForeignKey(related_name='entries', to='bank.Account')),
            ],
        ),
        migrations.CreateModel(
            name='SystemAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('credits', models.OneToOneField(related_name='systemaccount_credit', to='bank.Account')),
                ('currency', models.OneToOneField(to='bank.Currency')),
                ('debits', models.OneToOneField(related_name='systemaccount_debit', to='bank.Account')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reason', models.CharField(max_length=200)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('approver', models.ForeignKey(related_name='approved_transactions', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='entry',
            name='transaction',
            field=models.ForeignKey(to='bank.Transaction'),
        ),
        migrations.AddField(
            model_name='account',
            name='currency',
            field=models.ForeignKey(related_name='accounts', to='bank.Currency'),
        ),
        migrations.AddField(
            model_name='account',
            name='owner',
            field=models.ForeignKey(related_name='accounts_owned', blank=True, to=settings.AUTH_USER_MODEL, help_text=b'May be blank for group accounts', null=True),
        ),
    ]
