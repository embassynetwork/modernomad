# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0033_auto_20160922_0303'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booking',
            old_name='arrival_time',
            new_name='arrival_time_deprecated',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='arrive',
            new_name='arrive_deprecated',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='depart',
            new_name='depart_deprecated',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='last_msg',
            new_name='last_msg_deprecated',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='location',
            new_name='location_deprecated',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='purpose',
            new_name='purpose_deprecated',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='resource',
            new_name='resource_deprecated',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='status',
            new_name='status_deprecated',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='tags',
            new_name='tags_deprecated',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='user',
            new_name='user_deprecated',
        ),
        migrations.AlterField(
            model_name='booking',
            name='use',
            field=models.OneToOneField(related_name='booking', to='core.Use'),
        ),
    ]
