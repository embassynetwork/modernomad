# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gather', '0005_auto_20150530_1623'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='private',
        ),
        migrations.AddField(
            model_name='event',
            name='visibility',
            field=models.CharField(default=b'public', help_text=b'Community events are visible only to community members. Private events are visible to those who have the link.', max_length=200, choices=[(b'public', b'Public'), (b'private', b'Private'), (b'community', b'Community')]),
        ),
    ]
