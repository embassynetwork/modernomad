# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0031_auto_20160921_0314'),
    ]

    operations = [
        migrations.CreateModel(
            name='Use',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default=b'pending', max_length=200, blank=True, choices=[(b'pending', b'Pending'), (b'approved', b'Approved'), (b'confirmed', b'Confirmed'), (b'house declined', b'House Declined'), (b'user declined', b'User Declined'), (b'canceled', b'Canceled')])),
                ('arrive', models.DateField(verbose_name=b'Arrival Date')),
                ('depart', models.DateField(verbose_name=b'Departure Date')),
                ('arrival_time', models.CharField(help_text=b'Optional, if known', max_length=200, null=True, blank=True)),
                ('purpose', models.TextField(verbose_name=b'Tell us a bit about the reason for your trip/stay')),
                ('last_msg', models.DateTimeField(null=True, blank=True)),
                ('location', models.ForeignKey(related_name='uses', to='core.Location', null=True)),
                ('resource', models.ForeignKey(to='core.Resource', null=True)),
                ('user', models.ForeignKey(related_name='uses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='booking',
            name='use',
            field=models.OneToOneField(related_name='booking', null=True, to='core.Use'),
        ),
    ]
