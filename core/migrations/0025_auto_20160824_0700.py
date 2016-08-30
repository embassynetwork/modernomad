# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_auto_20160816_0702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='availability',
            name='resource',
            field=models.ForeignKey(related_name='availabilities', to='core.Resource'),
        ),
        migrations.AlterUniqueTogether(
            name='availability',
            unique_together=set([('start_date', 'resource')]),
        ),
    ]
