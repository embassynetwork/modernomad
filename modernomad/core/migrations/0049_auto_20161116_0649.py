# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0048_auto_20161115_1052'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('symbol', models.CharField(max_length=5)),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='type',
            field=models.CharField(default=b'standard', max_length=32, choices=[(b'system', b'System'), (b'standard', b'Standard')]),
        ),
        migrations.AddField(
            model_name='transaction',
            name='reason',
            field=models.CharField(default='test', max_length=200),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='account',
            name='currency',
        ),
    ]
