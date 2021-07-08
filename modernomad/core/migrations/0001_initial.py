# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-07 21:19
from __future__ import unicode_literals

import modernomad.core.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import imagekit.models.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bank', '0001_initial'),
        ('flatpages', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Backing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateField(default=django.utils.timezone.now)),
                ('end', models.DateField(blank=True, null=True)),
                ('drft_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='bank.Account')),
                ('money_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='bank.Account')),
            ],
        ),
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('generated_on', models.DateTimeField(auto_now=True)),
                ('comment', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BillLineItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('paid_by_house', models.BooleanField(default=True)),
                ('custom', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status_deprecated', models.CharField(blank=True, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('confirmed', 'Confirmed'), ('house declined', 'House Declined'), ('user declined', 'User Declined'), ('canceled', 'Canceled')], default='pending', max_length=200, null=True)),
                ('arrive_deprecated', models.DateField(null=True, verbose_name='Arrival Date')),
                ('depart_deprecated', models.DateField(null=True, verbose_name='Departure Date')),
                ('arrival_time_deprecated', models.CharField(blank=True, help_text='Optional, if known', max_length=200, null=True)),
                ('tags_deprecated', models.CharField(blank=True, help_text='What are 2 or 3 tags that characterize this trip?', max_length=200, null=True)),
                ('purpose_deprecated', models.TextField(null=True, verbose_name='Tell us a bit about the reason for your trip/stay')),
                ('last_msg_deprecated', models.DateTimeField(blank=True, null=True)),
                ('comments', models.TextField(blank=True, null=True, verbose_name='Any additional comments. (Optional)')),
                ('rate', models.DecimalField(blank=True, decimal_places=2, help_text='Uses the default rate unless otherwise specified.', max_digits=9, null=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='CapacityChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateField()),
                ('quantity', models.IntegerField()),
                ('accept_drft', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField(verbose_name='The body of the email')),
                ('subject', models.CharField(max_length=200, verbose_name='Default Subject Line')),
                ('name', models.CharField(max_length=200, verbose_name='Template Name')),
                ('shared', models.BooleanField(default=False)),
                ('context', models.CharField(choices=[('booking', 'Booking'), ('subscription', 'Subscription')], max_length=32)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Fee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=100, verbose_name='Fee Name')),
                ('percentage', models.FloatField(default=0, help_text='For example 5.2% = 0.052')),
                ('paid_by_house', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='HouseAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bank.Account')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.CharField(help_text='Try to make this short and sweet. It will also be used to form several location-specific email addresses in the form of xxx@<your_slug>.mail.embassynetwork.com', max_length=60, unique=True)),
                ('short_description', models.TextField()),
                ('address', models.CharField(max_length=300)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('image', models.ImageField(help_text='Requires an image with proportions 800px wide x 225px high', upload_to=modernomad.core.models.location_img_upload_to)),
                ('profile_image', models.ImageField(blank=True, help_text='A shiny high profile image for the location. Must be 336x344px.', null=True, upload_to=modernomad.core.models.location_img_upload_to)),
                ('stay_page', models.TextField(default='This is the page which has some descriptive text at the top (this text), and then lists the available rooms. HTML is supported.')),
                ('front_page_stay', models.TextField(default='This is the middle of three sections underneath the main landing page text to entice people to stay with you, and then links to the stay page (above). HTML is supported.')),
                ('front_page_participate', models.TextField(default='This is far right of three sections underneath the main landing page text to tell people how to get involved with your community. There is a link to the Events page underneath. HTML is supported. ')),
                ('announcement', models.TextField(blank=True, default='This is far left of three sections underneath the main landing page text to use for announcements and news. HTML is supported.', null=True)),
                ('max_booking_days', models.IntegerField(default=14)),
                ('welcome_email_days_ahead', models.IntegerField(default=2)),
                ('house_access_code', models.CharField(blank=True, max_length=50, null=True)),
                ('ssid', models.CharField(blank=True, max_length=200, null=True)),
                ('ssid_password', models.CharField(blank=True, max_length=200, null=True)),
                ('timezone', models.CharField(help_text='Must be an accurate timezone name, eg. "America/Los_Angeles". Check here for your time zone: http://en.wikipedia.org/wiki/List_of_tz_database_time_zones', max_length=200)),
                ('bank_account_number', models.IntegerField(blank=True, help_text='We use this to transfer money to you!', null=True)),
                ('routing_number', models.IntegerField(blank=True, help_text='We use this to transfer money to you!', null=True)),
                ('bank_name', models.CharField(blank=True, help_text='We use this to transfer money to you!', max_length=200, null=True)),
                ('name_on_account', models.CharField(blank=True, help_text='We use this to transfer money to you!', max_length=200, null=True)),
                ('email_subject_prefix', models.CharField(help_text='Your prefix will be wrapped in square brackets automatically.', max_length=200)),
                ('check_out', models.CharField(help_text='When your guests should be out of their bed/room.', max_length=20)),
                ('check_in', models.CharField(help_text='When your guests can expect their bed to be ready.', max_length=200)),
                ('visibility', models.CharField(choices=[('public', 'Public'), ('members', 'Members Only'), ('link', 'Those with the Link')], default='link', max_length=32)),
                ('house_admins', models.ManyToManyField(related_name='house_admin', to=settings.AUTH_USER_MODEL)),
                ('readonly_admins', models.ManyToManyField(blank=True, help_text='Readonly admins do not show up as part of the community. Useful for eg. external bookkeepers, etc.', related_name='readonly_admin', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LocationEmailTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(choices=[('admin_daily_update', 'Admin Daily Update'), ('guest_daily_update', 'Guest Daily Update'), ('invoice', 'Invoice'), ('receipt', 'Booking Receipt'), ('subscription_receipt', 'Subscription Receipt'), ('newbooking', 'New Booking'), ('pre_arrival_welcome', 'Pre-Arrival Welcome'), ('departure', 'Departure')], max_length=32)),
                ('text_body', models.TextField(verbose_name='The text body of the email')),
                ('html_body', models.TextField(blank=True, null=True, verbose_name='The html body of the email')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Location')),
            ],
        ),
        migrations.CreateModel(
            name='LocationFee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Fee')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Location')),
            ],
        ),
        migrations.CreateModel(
            name='LocationFlatPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flatpage', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='flatpages.FlatPage')),
            ],
        ),
        migrations.CreateModel(
            name='LocationMenu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='A short title for your menu. Note: If there is only one page in the menu, it will be used as a top level nav item, and the menu name will not be used.', max_length=15)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Location')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('payment_service', models.CharField(blank=True, help_text='e.g., Stripe, Paypal, Dwolla, etc. May be empty', max_length=200, null=True)),
                ('payment_method', models.CharField(blank=True, help_text='e.g., Visa, cash, bank transfer', max_length=200, null=True)),
                ('paid_amount', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('transaction_id', models.CharField(blank=True, max_length=200, null=True)),
                ('last4', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('default_rate', models.DecimalField(decimal_places=2, max_digits=9)),
                ('description', models.TextField(blank=True, help_text='Displayed on room detail page only', null=True)),
                ('summary', models.CharField(default='', help_text='Displayed on the search page. Max length 140 chars', max_length=140)),
                ('cancellation_policy', models.CharField(default='24 hours', max_length=400)),
                ('image', imagekit.models.fields.ProcessedImageField(help_text='Should be 500x325px or a 1 to 0.65 ratio. If it is not this size, it will automatically be resized.', upload_to=modernomad.core.models.resource_img_upload_to)),
                ('location', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='resources', to='core.Location')),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=9)),
                ('description', models.CharField(blank=True, max_length=256, null=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Location')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='communitysubscription_notes', to='core.Subscription')),
            ],
        ),
        migrations.CreateModel(
            name='Use',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(blank=True, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('confirmed', 'Confirmed'), ('house declined', 'House Declined'), ('user declined', 'User Declined'), ('canceled', 'Canceled')], default='pending', max_length=200)),
                ('arrive', models.DateField(verbose_name='Arrival Date')),
                ('depart', models.DateField(verbose_name='Departure Date')),
                ('arrival_time', models.CharField(blank=True, help_text='Optional, if known', max_length=200, null=True)),
                ('purpose', models.TextField(verbose_name='Tell us a bit about the reason for your trip/stay')),
                ('last_msg', models.DateTimeField(blank=True, null=True)),
                ('accounted_by', models.CharField(blank=True, choices=[('fiat', 'Fiat'), ('fiatdrft', 'Fiat & DRFT'), ('drft', 'DRFT'), ('backing', 'Backing')], default='fiat', max_length=200)),
                ('location', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='uses', to='core.Location')),
                ('resource', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Resource')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UseNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('booking_deprecated', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='booking_notes', to='core.Booking')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('use', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='use_notes', to='core.Use')),
            ],
        ),
        migrations.CreateModel(
            name='UserNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_notes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('image', imagekit.models.fields.ProcessedImageField(upload_to=modernomad.core.models.profile_img_upload_to)),
                ('bio', models.TextField(blank=True, null=True, verbose_name='About you')),
                ('links', models.TextField(blank=True, help_text='Comma-separated', null=True)),
                ('phone', models.CharField(blank=True, help_text='Optional. Most locations operate primarily by email, but a phone number can be helpful for last minute coordination and the unexpected.', max_length=20, null=True, verbose_name='Phone Number')),
                ('projects', models.TextField(help_text='Describe one or more projects you are currently working on', verbose_name='Current Projects')),
                ('sharing', models.TextField(help_text="Is there anything you'd be interested in learning or sharing during your stay?")),
                ('discussion', models.TextField(help_text="We like discussing thorny issues with each other. What's a question that's been on your mind lately that you don't know the answer to?")),
                ('referral', models.CharField(help_text='How did you hear about us? (Give a name if possible!)', max_length=200)),
                ('city', models.CharField(help_text='In what city are you primarily based?', max_length=200, verbose_name='City')),
                ('customer_id', models.CharField(blank=True, max_length=200, null=True)),
                ('last4', models.IntegerField(blank=True, help_text="Last 4 digits of the user's card on file, if any", null=True)),
                ('primary_accounts', models.ManyToManyField(blank=True, help_text='one for each currency', related_name='primary_for', to='bank.Account')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UseTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bank.Transaction')),
                ('use', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Use')),
            ],
        ),
        migrations.CreateModel(
            name='BookingBill',
            fields=[
                ('bill_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Bill')),
            ],
            bases=('core.bill',),
        ),
        migrations.CreateModel(
            name='SubscriptionBill',
            fields=[
                ('bill_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Bill')),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
                ('subscription', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bills', to='core.Subscription')),
            ],
            options={
                'ordering': ['-period_start'],
            },
            bases=('core.bill',),
        ),
        migrations.AddField(
            model_name='payment',
            name='bill',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='core.Bill'),
        ),
        migrations.AddField(
            model_name='payment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='locationflatpage',
            name='menu',
            field=models.ForeignKey(help_text='Note: If there is only one page in the menu, it will be used as a top level nav item, and the menu name will not be used.', on_delete=django.db.models.deletion.CASCADE, related_name='pages', to='core.LocationMenu'),
        ),
        migrations.AddField(
            model_name='houseaccount',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Location'),
        ),
        migrations.AddField(
            model_name='capacitychange',
            name='resource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='capacity_changes', to='core.Resource'),
        ),
        migrations.AddField(
            model_name='booking',
            name='location_deprecated',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='core.Location'),
        ),
        migrations.AddField(
            model_name='booking',
            name='resource_deprecated',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Resource'),
        ),
        migrations.AddField(
            model_name='booking',
            name='suppressed_fees',
            field=models.ManyToManyField(blank=True, to='core.Fee'),
        ),
        migrations.AddField(
            model_name='booking',
            name='use',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='booking', to='core.Use'),
        ),
        migrations.AddField(
            model_name='booking',
            name='user_deprecated',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='billlineitem',
            name='bill',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='line_items', to='core.Bill'),
        ),
        migrations.AddField(
            model_name='billlineitem',
            name='fee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Fee'),
        ),
        migrations.AddField(
            model_name='backing',
            name='resource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='backings', to='core.Resource'),
        ),
        migrations.AddField(
            model_name='backing',
            name='subscription',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Subscription'),
        ),
        migrations.AddField(
            model_name='backing',
            name='users',
            field=models.ManyToManyField(related_name='backings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='capacitychange',
            unique_together=set([('start_date', 'resource')]),
        ),
        migrations.AddField(
            model_name='booking',
            name='bill',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='booking', to='core.BookingBill'),
        ),
    ]
