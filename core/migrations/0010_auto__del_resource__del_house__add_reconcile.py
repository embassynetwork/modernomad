# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Resource'
        db.delete_table('core_resource')

        # Deleting model 'House'
        db.delete_table('core_house')

        # Removing M2M table for field admins on 'House'
        db.delete_table('core_house_admins')

        # Adding model 'Reconcile'
        db.create_table('core_reconcile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reservation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Reservation'])),
            ('custom_rate', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('automatic_invoice', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status', self.gf('django.db.models.fields.CharField')(default='unpaid', max_length=200)),
            ('payment_service', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('payment_method', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('paid_amount', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('transaction_id', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('payment_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('room_name', self.gf('django.db.models.fields.CharField')(default='shared', max_length=200)),
        ))
        db.send_create_signal('core', ['Reconcile'])


    def backwards(self, orm):
        # Adding model 'Resource'
        db.create_table('core_resource', (
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('house', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.House'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('resource_type', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('core', ['Resource'])

        # Adding model 'House'
        db.create_table('core_house', (
            ('twitter_handle', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('mission_values', self.gf('django.db.models.fields.TextField')(max_length=2000, null=True, blank=True)),
            ('space_share_description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('contact_ok', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('rooms', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('amenities', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('space_share', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('website', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200, null=True, blank=True)),
            ('picture', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=2000, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=400, unique=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('events', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('latLong', self.gf('django.db.models.fields.CharField')(max_length=100, unique=True)),
            ('contact', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('events_description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('residents', self.gf('django.db.models.fields.IntegerField')()),
            ('pictures_feed', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('guests', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
        ))
        db.send_create_signal('core', ['House'])

        # Adding M2M table for field admins on 'House'
        db.create_table('core_house_admins', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('house', models.ForeignKey(orm['core.house'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('core_house_admins', ['house_id', 'user_id'])

        # Deleting model 'Reconcile'
        db.delete_table('core_reconcile')


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
        'core.reconcile': {
            'Meta': {'object_name': 'Reconcile'},
            'automatic_invoice': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'custom_rate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'paid_amount': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'payment_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'payment_method': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'payment_service': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'reservation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Reservation']"}),
            'room_name': ('django.db.models.fields.CharField', [], {'default': "'shared'", 'max_length': '200'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'unpaid'", 'max_length': '200'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'core.reservation': {
            'Meta': {'object_name': 'Reservation'},
            'accommodation_preference': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'arrival_time': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'arrive': ('django.db.models.fields.DateField', [], {}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'depart': ('django.db.models.fields.DateField', [], {}),
            'guest_emails': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'guest_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'hosted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'purpose': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '200', 'blank': 'True'}),
            'tags': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'core.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'bio': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'discussion': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'default': "'data/avatars/default.jpg'", 'max_length': '100'}),
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