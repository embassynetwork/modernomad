# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'House'
        db.create_table('wc_profiles_house', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=400)),
            ('amenities', self.gf('django.db.models.fields.TextField')()),
            ('house_rules', self.gf('django.db.models.fields.TextField')()),
            ('long_term_rooms', self.gf('django.db.models.fields.IntegerField')()),
            ('short_term_rooms', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('wc_profiles', ['House'])

        # Adding model 'Resource'
        db.create_table('wc_profiles_resource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('house', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wc_profiles.House'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('blurb', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('resource_type', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('wc_profiles', ['Resource'])

        # Adding model 'User'
        db.create_table('wc_profiles_user', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('first', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('last', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('bio', self.gf('django.db.models.fields.TextField')()),
            ('links', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('upto', self.gf('django.db.models.fields.TextField')()),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('invited_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wc_profiles.User'], null=True, blank=True)),
        ))
        db.send_create_signal('wc_profiles', ['User'])

        # Adding model 'Endorsement'
        db.create_table('wc_profiles_endorsement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('endorsee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wc_profiles.User'])),
            ('endorser', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wc_profiles.House'])),
            ('comment', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('wc_profiles', ['Endorsement'])


    def backwards(self, orm):
        # Deleting model 'House'
        db.delete_table('wc_profiles_house')

        # Deleting model 'Resource'
        db.delete_table('wc_profiles_resource')

        # Deleting model 'User'
        db.delete_table('wc_profiles_user')

        # Deleting model 'Endorsement'
        db.delete_table('wc_profiles_endorsement')


    models = {
        'wc_profiles.endorsement': {
            'Meta': {'object_name': 'Endorsement'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'endorsee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wc_profiles.User']"}),
            'endorser': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wc_profiles.House']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'wc_profiles.house': {
            'Meta': {'object_name': 'House'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'amenities': ('django.db.models.fields.TextField', [], {}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {}),
            'house_rules': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_term_rooms': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'short_term_rooms': ('django.db.models.fields.IntegerField', [], {}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'wc_profiles.resource': {
            'Meta': {'object_name': 'Resource'},
            'blurb': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'house': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wc_profiles.House']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'resource_type': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'wc_profiles.user': {
            'Meta': {'object_name': 'User'},
            'bio': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'invited_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wc_profiles.User']", 'null': 'True', 'blank': 'True'}),
            'last': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'links': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'upto': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['wc_profiles']