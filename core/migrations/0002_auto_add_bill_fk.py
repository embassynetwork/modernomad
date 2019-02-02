# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

def forward(apps, schema_editor):
    Reservation = apps.get_model("core", "Reservation")
    BillLineItem = apps.get_model("core", "BillLineItem")
    Payment = apps.get_model("core", "Payment")
    Bill = apps.get_model("core", "Bill")

    # make a bill item for each reservation, then update the associated
    # billLineItem and Payment objects to link to the bill instead of the
    # reservation. 
    reservations = Reservation.objects.all()
    for r in reservations:
        bill = Bill.objects.create()
        r.bill = bill
        r.save()
        payments = Payment.objects.filter(reservation =r)
        for p in payments:
            p.bill = bill
            p.user = r.user
            p.save()
        lineitems = BillLineItem.objects.filter(reservation=r)
        for l in lineitems:
            l.bill = bill
            l.save()
        # finally, update the creation date of the bill so that it matches the
        # reservation creation date.
        bill.created_on = r.created
        bill.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('generated_on', models.DateTimeField(auto_now=True)),
                ('comment', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='payment',
            name='automatic_invoice',
        ),
        migrations.AddField(
            model_name='billlineitem',
            name='bill',
            field=models.ForeignKey(related_name='line_items', to='core.Bill', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='payment',
            name='bill',
            field=models.ForeignKey(related_name='payments', to='core.Bill', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='payment',
            name='user',
            field=models.ForeignKey(related_name='payments', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='reservation',
            name='bill',
            field=models.OneToOneField(related_name='reservation', to='core.Bill', null=True),
            preserve_default=True,
        ),
        migrations.RunPython(forward, elidable=True),
        migrations.RemoveField(
            model_name='payment',
            name='reservation',
        ),
        migrations.RemoveField(
            model_name='billlineitem',
            name='reservation',
        ),
    ]
