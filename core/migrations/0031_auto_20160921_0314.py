# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_auto_20160921_0309'),
    ]

    operations = [
        migrations.RunSQL("UPDATE core_emailtemplate SET context = 'booking' WHERE context = 'reservation';", elidable=True),
        migrations.RunSQL("UPDATE core_locationemailtemplate SET key = 'newbooking' WHERE key = 'newreservation';", elidable=True)
    ]
