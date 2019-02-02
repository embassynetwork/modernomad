# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

def forward(apps, schema_editor):
    Reservation = apps.get_model("core", "Reservation")
    Bill = apps.get_model("core", "Bill")
    ReservationBill = apps.get_model("core", "ReservationBill")

    reservations = Reservation.objects.all()
    for r in reservations:
        r.bill = ReservationBill.objects.create(bill_ptr=r.old_bill)
        r.save()
        
class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0002_auto_add_bill_fk'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunitySubscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.DecimalField(max_digits=9, decimal_places=2)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(null=True, blank=True)),
                ('recurring_charge_date', models.IntegerField(default=1, help_text=b'The day of the month that the subscription will be charged. This is an integer value.')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReservationBill',
            fields=[
                ('bill_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.Bill')),
            ],
            options={
            },
            bases=('core.bill',),
        ),
        migrations.CreateModel(
            name='RoomSubscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.DecimalField(max_digits=9, decimal_places=2)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(null=True, blank=True)),
                ('recurring_charge_date', models.IntegerField(default=1, help_text=b'The day of the month that the subscription will be charged. This is an integer value.')),
                ('nights', models.IntegerField(help_text=b'How many nights does this subscription entitle the member to?')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubscriptionBill',
            fields=[
                ('bill_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.Bill')),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
            ],
            options={
            },
            bases=('core.bill',),
        ),
        migrations.AddField(
            model_name='roomsubscription',
            name='bills',
            field=models.ManyToManyField(to='core.SubscriptionBill', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='roomsubscription',
            name='location',
            field=models.ForeignKey(to='core.Location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='roomsubscription',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='communitysubscription',
            name='bills',
            field=models.ManyToManyField(to='core.SubscriptionBill', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='communitysubscription',
            name='location',
            field=models.ForeignKey(to='core.Location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='communitysubscription',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.RenameField(
            model_name='reservation',
            old_name='bill',
            new_name='old_bill',
        ),
        migrations.AlterField(
            model_name='reservation',
            name='old_bill',
            field=models.OneToOneField(related_name='old_related', null=True, to='core.Bill'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='reservation',
            name='bill',
            field=models.OneToOneField(related_name='reservation', null=True, to='core.ReservationBill'),
            preserve_default=True,
        ),
        migrations.RunPython(forward, elidable=True),
        migrations.RemoveField(
            model_name='reservation',
            name='old_bill',
        ),
    ]
