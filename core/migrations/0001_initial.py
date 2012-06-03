# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'House'
        db.create_table('core_house', (
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
        db.send_create_signal('core', ['House'])

        # Adding model 'Resource'
        db.create_table('core_resource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('house', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.House'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('blurb', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('resource_type', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('core', ['Resource'])

        # Adding model 'UserProfile'
        db.create_table('core_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('bio', self.gf('django.db.models.fields.TextField')()),
            ('links', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('upto', self.gf('django.db.models.fields.TextField')()),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('invited_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.UserProfile'], null=True, blank=True)),
        ))
        db.send_create_signal('core', ['UserProfile'])

        # Adding model 'Endorsement'
        db.create_table('core_endorsement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('endorsee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.UserProfile'])),
            ('endorser', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.House'])),
            ('comment', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('core', ['Endorsement'])


    def backwards(self, orm):
        # Deleting model 'House'
        db.delete_table('core_house')

        # Deleting model 'Resource'
        db.delete_table('core_resource')

        # Deleting model 'UserProfile'
        db.delete_table('core_userprofile')

        # Deleting model 'Endorsement'
        db.delete_table('core_endorsement')


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
            'endorsee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.UserProfile']"}),
            'endorser': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.House']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.house': {
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
        'core.resource': {
            'Meta': {'object_name': 'Resource'},
            'blurb': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
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