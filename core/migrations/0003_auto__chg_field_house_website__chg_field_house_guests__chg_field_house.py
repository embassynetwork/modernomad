# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'House.website'
        db.alter_column('core_house', 'website', self.gf('django.db.models.fields.URLField')(max_length=200, unique=True, null=True))

        # Changing field 'House.guests'
        db.alter_column('core_house', 'guests', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'House.name'
        db.alter_column('core_house', 'name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True))

        # Changing field 'House.short_term_rooms'
        db.alter_column('core_house', 'short_term_rooms', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'House.summary'
        db.alter_column('core_house', 'summary', self.gf('django.db.models.fields.CharField')(max_length=200, null=True))

        # Changing field 'House.amenities'
        db.alter_column('core_house', 'amenities', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'House.events'
        db.alter_column('core_house', 'events', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'House.long_term_rooms'
        db.alter_column('core_house', 'long_term_rooms', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'House.house_rules'
        db.alter_column('core_house', 'house_rules', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):

        # Changing field 'House.website'
        db.alter_column('core_house', 'website', self.gf('django.db.models.fields.URLField')(default='', max_length=200, unique=True))

        # Changing field 'House.guests'
        db.alter_column('core_house', 'guests', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'House.name'
        db.alter_column('core_house', 'name', self.gf('django.db.models.fields.CharField')(default='', max_length=200))

        # Changing field 'House.short_term_rooms'
        db.alter_column('core_house', 'short_term_rooms', self.gf('django.db.models.fields.IntegerField')(default=None))

        # Changing field 'House.summary'
        db.alter_column('core_house', 'summary', self.gf('django.db.models.fields.CharField')(default='', max_length=200))

        # Changing field 'House.amenities'
        db.alter_column('core_house', 'amenities', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'House.events'
        db.alter_column('core_house', 'events', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'House.long_term_rooms'
        db.alter_column('core_house', 'long_term_rooms', self.gf('django.db.models.fields.IntegerField')(default=None))

        # Changing field 'House.house_rules'
        db.alter_column('core_house', 'house_rules', self.gf('django.db.models.fields.TextField')(default=''))

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
        'core.endorsement': {
            'Meta': {'object_name': 'Endorsement'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'endorsee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'endorser': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.House']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.house': {
            'Meta': {'object_name': 'House'},
            'address': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '400'}),
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'amenities': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'events': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'guests': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'house_rules': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latLong': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'long_term_rooms': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'rooms': ('django.db.models.fields.IntegerField', [], {}),
            'short_term_rooms': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'core.resource': {
            'Meta': {'object_name': 'Resource'},
            'blurb': ('django.db.models.fields.TextField', [], {}),
            'house': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.House']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'resource_type': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'core.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'bio': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'invited_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.UserProfile']", 'null': 'True', 'blank': 'True'}),
            'links': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'upto': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['core']