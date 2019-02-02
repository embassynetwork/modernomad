# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

''' 
WARNING! since each resource can only have one backing, this DELETES ANY
EXISTING BACKINGS
'''

class Migration(migrations.Migration):

    def do_stuff(apps, schema_editor):
        # move residents from resource.residents.all() to backing. 

        Resource = apps.get_model('core', 'Resource')
        Backing = apps.get_model('core', 'Backing')
        Currency = apps.get_model('bank', 'Currency')
        Account = apps.get_model('bank', 'Account')
        
        # !!! WARNING!!
        Backing.objects.all().delete()
        
        for resource in Resource.objects.all():
            residents_this_room = list(resource.residents.all())
            
            if len(residents_this_room) > 0:
                ma = Account.objects.create(
                        currency=Currency.objects.get(name="USD"), 
                        type="credit", 
                        name="USD Account for %s" % resource.name[:20]
                    )
                ma.owners = residents_this_room
                ma.save()

                da = Account.objects.create(
                        currency=Currency.objects.get(name="DRFT"), 
                        type="credit", 
                        name="DRFT Account for %s" % resource.name[:20]
                    )
                da.owners = residents_this_room
                da.save()
                
                Backing.objects.create(resource=resource, money_account=ma, drft_account=da, accepts_drft=False)

    dependencies = [
        ('core', '0061_usetransaction'),
    ]

    operations = [
        migrations.RunPython(do_stuff, elidable=True),
    ]
