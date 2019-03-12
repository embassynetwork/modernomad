# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modernomad.core.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('flatpages', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BillLineItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('amount', models.DecimalField(default=0, max_digits=7, decimal_places=2)),
                ('paid_by_house', models.BooleanField(default=True)),
                ('custom', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('body', models.TextField(verbose_name=b'The body of the email')),
                ('subject', models.CharField(max_length=200, verbose_name=b'Default Subject Line')),
                ('name', models.CharField(max_length=200, verbose_name=b'Template Name')),
                ('shared', models.BooleanField(default=False)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Fee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=100, verbose_name=b'Fee Name')),
                ('percentage', models.FloatField(default=0, help_text=b'For example 5.2% = 0.052')),
                ('paid_by_house', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('slug', models.CharField(help_text=b'Try to make this short and sweet. It will also be used to form several location-specific email addresses in the form of xxx@<your_slug>.mail.embassynetwork.com', unique=True, max_length=60)),
                ('short_description', models.TextField()),
                ('address', models.CharField(max_length=300)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('image', models.ImageField(help_text=b'Requires an image with proportions 1400px wide x 300px high', upload_to=modernomad.core.models.location_img_upload_to)),
                ('stay_page', models.TextField(default=b'This is the page which has some descriptive text at the top (this text), and then lists the available rooms. HTML is supported.')),
                ('front_page_stay', models.TextField(default=b'This is the middle of three sections underneath the main landing page text to entice people to stay with you, and then links to the stay page (above). HTML is supported.')),
                ('front_page_participate', models.TextField(default=b'This is far right of three sections underneath the main landing page text to tell people how to get involved with your community. There is a link to the Events page underneath. HTML is supported. ')),
                ('announcement', models.TextField(default=b'This is far left of three sections underneath the main landing page text to use for announcements and news. HTML is supported.', null=True, blank=True)),
                ('max_reservation_days', models.IntegerField(default=14)),
                ('welcome_email_days_ahead', models.IntegerField(default=2)),
                ('house_access_code', models.CharField(max_length=50, null=True, blank=True)),
                ('ssid', models.CharField(max_length=200, null=True, blank=True)),
                ('ssid_password', models.CharField(max_length=200, null=True, blank=True)),
                ('timezone', models.CharField(help_text=b'Must be an accurate timezone name, eg. "America/Los_Angeles". Check here for your time zone: http://en.wikipedia.org/wiki/List_of_tz_database_time_zones', max_length=200)),
                ('bank_account_number', models.IntegerField(help_text=b'We use this to transfer money to you!', max_length=200, null=True, blank=True)),
                ('routing_number', models.IntegerField(help_text=b'We use this to transfer money to you!', max_length=200, null=True, blank=True)),
                ('bank_name', models.CharField(help_text=b'We use this to transfer money to you!', max_length=200, null=True, blank=True)),
                ('name_on_account', models.CharField(help_text=b'We use this to transfer money to you!', max_length=200, null=True, blank=True)),
                ('email_subject_prefix', models.CharField(help_text=b'Your prefix will be wrapped in square brackets automatically.', max_length=200)),
                ('check_out', models.CharField(help_text=b'When your guests should be out of their bed/room.', max_length=20)),
                ('check_in', models.CharField(help_text=b'When your guests can expect their bed to be ready.', max_length=200)),
                ('public', models.BooleanField(default=False, verbose_name=b'Is this location open to the public?')),
                ('house_admins', models.ManyToManyField(related_name='house_admin', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
                ('residents', models.ManyToManyField(related_name='residences', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LocationEmailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=32, choices=[(b'admin_daily_update', b'Admin Daily Update'), (b'guest_daily_update', b'Guest Daily Update'), (b'invoice', b'Invoice'), (b'receipt', b'Receipt'), (b'newreservation', b'New Reservation'), (b'pre_arrival_welcome', b'Pre-Arrival Welcome')])),
                ('text_body', models.TextField(verbose_name=b'The text body of the email')),
                ('html_body', models.TextField(null=True, verbose_name=b'The html body of the email', blank=True)),
                ('location', models.ForeignKey(to='core.Location')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LocationFee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fee', models.ForeignKey(to='core.Fee')),
                ('location', models.ForeignKey(to='core.Location')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LocationFlatPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('flatpage', models.OneToOneField(to='flatpages.FlatPage')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LocationMenu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'A short title for your menu. Note: If there is only one page in the menu, it will be used as a top level nav item, and the menu name will not be used.', max_length=15)),
                ('location', models.ForeignKey(to='core.Location')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('automatic_invoice', models.BooleanField(default=False, help_text=b'If True, an invoice will be sent to the user automatically at the end of their stay.')),
                ('payment_service', models.CharField(help_text=b'e.g., Stripe, Paypal, Dwolla, etc. May be empty', max_length=200, null=True, blank=True)),
                ('payment_method', models.CharField(help_text=b'e.g., Visa, cash, bank transfer', max_length=200, null=True, blank=True)),
                ('paid_amount', models.DecimalField(default=0, max_digits=7, decimal_places=2)),
                ('transaction_id', models.CharField(max_length=200, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Reservable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(help_text=b'Leave this blank for a guest room or room with open ended reservability.', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default=b'pending', max_length=200, blank=True, choices=[(b'pending', b'Pending'), (b'approved', b'Approved'), (b'confirmed', b'Confirmed'), (b'house declined', b'House Declined'), (b'user declined', b'User Declined'), (b'canceled', b'Canceled')])),
                ('arrive', models.DateField(verbose_name=b'Arrival Date')),
                ('depart', models.DateField(verbose_name=b'Departure Date')),
                ('arrival_time', models.CharField(help_text=b'Optional, if known', max_length=200, null=True, blank=True)),
                ('tags', models.CharField(help_text=b'What are 2 or 3 tags that characterize this trip?', max_length=200, null=True, blank=True)),
                ('purpose', models.TextField(verbose_name=b'Tell us a bit about the reason for your trip/stay')),
                ('comments', models.TextField(null=True, verbose_name=b'Any additional comments. (Optional)', blank=True)),
                ('last_msg', models.DateTimeField(null=True, blank=True)),
                ('rate', models.DecimalField(help_text=b'Uses the default rate unless otherwise specified.', null=True, max_digits=9, decimal_places=2, blank=True)),
                ('uuid', models.UUIDField(max_length=32, unique=True, null=True, editable=False, blank=True)),
                ('location', models.ForeignKey(related_name='reservations', to='core.Location', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReservationNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('note', models.TextField(null=True, blank=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('reservation', models.ForeignKey(related_name='reservation_notes', to='core.Reservation')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('default_rate', models.DecimalField(max_digits=9, decimal_places=2)),
                ('description', models.TextField(null=True, blank=True)),
                ('cancellation_policy', models.CharField(default=b'24 hours', max_length=400)),
                ('shared', models.BooleanField(default=False, verbose_name=b'Is this a hostel/shared accommodation room?')),
                ('beds', models.IntegerField()),
                ('image', models.ImageField(null=True, upload_to=modernomad.core.models.resource_img_upload_to, blank=True)),
                ('location', models.ForeignKey(related_name='rooms', to='core.Location', null=True)),
                ('residents', models.ManyToManyField(help_text=b'This field is optional.', related_name='residents', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('note', models.TextField(null=True, blank=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(related_name='user_notes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(help_text=b'Image should have square dimensions.', upload_to=modernomad.core.models.profile_img_upload_to)),
                ('image_thumb', models.ImageField(null=True, upload_to=b'avatars/%Y/%m/%d/', blank=True)),
                ('bio', models.TextField(null=True, verbose_name=b'About you', blank=True)),
                ('links', models.TextField(help_text=b'Comma-separated', null=True, blank=True)),
                ('projects', models.TextField(help_text=b'Describe one or more projects you are currently working on', verbose_name=b'Current Projects')),
                ('sharing', models.TextField(help_text=b"Is there anything you'd be interested in learning or sharing during your stay?")),
                ('discussion', models.TextField(help_text=b"We like discussing thorny issues with each other. What's a question that's been on your mind lately that you don't know the answer to?")),
                ('referral', models.CharField(max_length=200, verbose_name=b'How did you hear about us? (Give a name if possible!)')),
                ('city', models.CharField(max_length=200, verbose_name=b'In what city are you primarily based?')),
                ('customer_id', models.CharField(max_length=200, null=True, blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='reservation',
            name='room',
            field=models.ForeignKey(to='core.Room', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='reservation',
            name='suppressed_fees',
            field=models.ManyToManyField(to='core.Fee', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='reservation',
            name='user',
            field=models.ForeignKey(related_name='reservations', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='reservable',
            name='room',
            field=models.ForeignKey(related_name='reservables', to='core.Room'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='payment',
            name='reservation',
            field=models.ForeignKey(to='core.Reservation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='locationflatpage',
            name='menu',
            field=models.ForeignKey(related_name='pages', to='core.LocationMenu', help_text=b'Note: If there is only one page in the menu, it will be used as a top level nav item, and the menu name will not be used.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='billlineitem',
            name='fee',
            field=models.ForeignKey(to='core.Fee', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='billlineitem',
            name='reservation',
            field=models.ForeignKey(to='core.Reservation'),
            preserve_default=True,
        ),
    ]
