# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Location'
        db.create_table('core_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=60)),
            ('short_description', self.gf('django.db.models.fields.TextField')()),
            ('about_page', self.gf('django.db.models.fields.TextField')()),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('stay_page', self.gf('django.db.models.fields.TextField')()),
            ('front_page_stay', self.gf('django.db.models.fields.TextField')()),
            ('front_page_participate', self.gf('django.db.models.fields.TextField')()),
            ('max_reservation_days', self.gf('django.db.models.fields.IntegerField')(default=14)),
            ('welcome_email_days_ahead', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('house_access_code', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('stripe_secret_key', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('stripe_public_key', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('mailgun_api_key', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('mailgun_domain', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('email_subject_prefix', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('default_from_email', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('core', ['Location'])

        # Adding M2M table for field house_admins on 'Location'
        db.create_table('core_location_house_admins', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('location', models.ForeignKey(orm['core.location'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('core_location_house_admins', ['location_id', 'user_id'])

        # Adding M2M table for field residents on 'Location'
        db.create_table('core_location_residents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('location', models.ForeignKey(orm['core.location'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('core_location_residents', ['location_id', 'user_id'])

        # Adding field 'Reservation.location'
        db.add_column('core_reservation', 'location',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='reservations', null=True, to=orm['core.Location']),
                      keep_default=False)

        # Adding field 'Room.location'
        db.add_column('core_room', 'location',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='rooms', null=True, to=orm['core.Location']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Location'
        db.delete_table('core_location')

        # Removing M2M table for field house_admins on 'Location'
        db.delete_table('core_location_house_admins')

        # Removing M2M table for field residents on 'Location'
        db.delete_table('core_location_residents')

        # Deleting field 'Reservation.location'
        db.delete_column('core_reservation', 'location_id')

        # Deleting field 'Room.location'
        db.delete_column('core_room', 'location_id')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.emailtemplate': {
            'Meta': {'object_name': 'EmailTemplate'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'shared': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'core.location': {
            'Meta': {'object_name': 'Location'},
            'about_page': ('django.db.models.fields.TextField', [], {}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'default_from_email': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'email_subject_prefix': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'front_page_participate': ('django.db.models.fields.TextField', [], {}),
            'front_page_stay': ('django.db.models.fields.TextField', [], {}),
            'house_access_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'house_admins': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'house_admin'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailgun_api_key': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'mailgun_domain': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'max_reservation_days': ('django.db.models.fields.IntegerField', [], {'default': '14'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'residents': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'residences'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'short_description': ('django.db.models.fields.TextField', [], {}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60'}),
            'stay_page': ('django.db.models.fields.TextField', [], {}),
            'stripe_public_key': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'stripe_secret_key': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'welcome_email_days_ahead': ('django.db.models.fields.IntegerField', [], {'default': '2'})
        },
        'core.reconcile': {
            'Meta': {'object_name': 'Reconcile'},
            'automatic_invoice': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'paid_amount': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'payment_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'payment_method': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'payment_service': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'rate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reservation': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Reservation']", 'unique': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'unpaid'", 'max_length': '200'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'core.reservation': {
            'Meta': {'object_name': 'Reservation'},
            'arrival_time': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'arrive': ('django.db.models.fields.DateField', [], {}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'depart': ('django.db.models.fields.DateField', [], {}),
            'guest_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'hosted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_msg': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reservations'", 'null': 'True', 'to': "orm['core.Location']"}),
            'purpose': ('django.db.models.fields.TextField', [], {}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Room']", 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '200', 'blank': 'True'}),
            'tags': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reservations'", 'to': "orm['auth.User']"})
        },
        'core.room': {
            'Meta': {'object_name': 'Room'},
            'beds': ('django.db.models.fields.IntegerField', [], {}),
            'cancellation_policy': ('django.db.models.fields.CharField', [], {'default': "'24 hours'", 'max_length': '400'}),
            'default_rate': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rooms'", 'null': 'True', 'to': "orm['core.Location']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'primary_use': ('django.db.models.fields.CharField', [], {'default': "'private'", 'max_length': '200'}),
            'shared': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'core.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'bio': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'customer_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'discussion': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'image_thumb': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'links': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'projects': ('django.db.models.fields.TextField', [], {}),
            'referral': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sharing': ('django.db.models.fields.TextField', [], {}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['core']