# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0018_userprofile_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='readonly_admins',
            field=models.ManyToManyField(help_text=b'Readonly admins do not show up as part of the community. Useful for eg. external bookkeepers, etc.', related_name='readonly_admin', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='phone',
            field=models.CharField(help_text=b'Optional. Most locations operate primarily by email, but a phone number can be helpful for last minute coordination and the unexpected.', max_length=20, null=True, verbose_name=b'Phone Number', blank=True),
        ),
    ]
