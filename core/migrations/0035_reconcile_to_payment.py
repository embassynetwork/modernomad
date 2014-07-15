# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

	def forwards(self, orm):
		db.rename_table('core_reconcile', 'core_payment')

		# Removing unique constraint on 'Payment', fields ['reservation']
		db.delete_unique(u'core_payment', ['reservation_id'])

		# Adding model 'Fee'
		db.create_table(u'core_fee', (
			(u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
			('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
			('percentage', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
			('paid_by_house', self.gf('django.db.models.fields.BooleanField')(default=False)),
		))
		db.send_create_signal(u'core', ['Fee'])

		# Adding model 'FeeCollection'
		db.create_table(u'core_feecollection', (
			(u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
			('collected_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
			('fee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Fee'])),
			('applies_to', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Payment'])),
			('amount', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
		))
		db.send_create_signal(u'core', ['FeeCollection'])

		# Adding model 'FeeDistribution'
		db.create_table(u'core_feedistribution', (
			(u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
			('distributed_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
			('distributed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
			('payment_method', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
			('amount', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
			('note', self.gf('django.db.models.fields.CharField')(max_length=200)),
		))
		db.send_create_signal(u'core', ['FeeDistribution'])

		# Adding M2M table for field collected_fees on 'FeeDistribution'
		m2m_table_name = db.shorten_name(u'core_feedistribution_collected_fees')
		db.create_table(m2m_table_name, (
			('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
			('feedistribution', models.ForeignKey(orm[u'core.feedistribution'], null=False)),
			('feecollection', models.ForeignKey(orm[u'core.feecollection'], null=False))
		))
		db.create_unique(m2m_table_name, ['feedistribution_id', 'feecollection_id'])

		# Adding model 'LocationFee'
		db.create_table(u'core_locationfee', (
			(u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
			('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Location'])),
			('fee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Fee'])),
		))
		db.send_create_signal(u'core', ['LocationFee'])

		# Changing field 'Payment.payment_date'
		db.alter_column(u'core_payment', 'payment_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2014, 7, 14, 0, 0)))

		# Changing field 'Payment.reservation'
		db.alter_column(u'core_payment', 'reservation_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Reservation']))

		# Adding field 'Reservation.rate'
		db.add_column(u'core_reservation', 'rate',
					  self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
					  keep_default=False)

	def backwards(self, orm):
		raise RuntimeError("Cannot reverse this migration.")

	models = {
		u'auth.group': {
			'Meta': {'object_name': 'Group'},
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
			'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
		},
		u'auth.permission': {
			'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
			'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
			'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
		},
		u'auth.user': {
			'Meta': {'ordering': "['username']", 'object_name': 'User'},
			'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
			'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
			'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
			'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
			'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
			'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
			'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
			'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
			'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
			'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
			'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
		},
		u'contenttypes.contenttype': {
			'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
			'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
			'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
		},
		u'core.emailtemplate': {
			'Meta': {'object_name': 'EmailTemplate'},
			'body': ('django.db.models.fields.TextField', [], {}),
			'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
			'shared': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
			'subject': ('django.db.models.fields.CharField', [], {'max_length': '200'})
		},
		u'core.fee': {
			'Meta': {'object_name': 'Fee'},
			'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'paid_by_house': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
			'percentage': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
		},
		u'core.feecollection': {
			'Meta': {'object_name': 'FeeCollection'},
			'amount': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
			'applies_to': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Payment']"}),
			'collected_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
			'fee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Fee']"}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
		},
		u'core.feedistribution': {
			'Meta': {'object_name': 'FeeDistribution'},
			'amount': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
			'collected_fees': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.FeeCollection']", 'symmetrical': 'False'}),
			'distributed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
			'distributed_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'note': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
			'payment_method': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
		},
		u'core.location': {
			'Meta': {'object_name': 'Location'},
			'about_page': ('django.db.models.fields.TextField', [], {}),
			'address': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
			'bank_account_number': ('django.db.models.fields.IntegerField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
			'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
			'email_subject_prefix': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
			'front_page_participate': ('django.db.models.fields.TextField', [], {}),
			'front_page_stay': ('django.db.models.fields.TextField', [], {}),
			'house_access_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
			'house_admins': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'house_admin'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
			'latitude': ('django.db.models.fields.FloatField', [], {}),
			'longitude': ('django.db.models.fields.FloatField', [], {}),
			'max_reservation_days': ('django.db.models.fields.IntegerField', [], {'default': '14'}),
			'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
			'name_on_account': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
			'residents': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'residences'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
			'routing_number': ('django.db.models.fields.IntegerField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
			'short_description': ('django.db.models.fields.TextField', [], {}),
			'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60'}),
			'ssid': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
			'ssid_password': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
			'stay_page': ('django.db.models.fields.TextField', [], {}),
			'tax_rate': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
			'taxes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
			'timezone': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
			'welcome_email_days_ahead': ('django.db.models.fields.IntegerField', [], {'default': '2'})
		},
		u'core.locationfee': {
			'Meta': {'object_name': 'LocationFee'},
			'fee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Fee']"}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Location']"})
		},
		u'core.payment': {
			'Meta': {'object_name': 'Payment'},
			'automatic_invoice': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'paid_amount': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'payment_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
			'payment_method': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
			'payment_service': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
			'rate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'reservation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Reservation']"}),
			'status': ('django.db.models.fields.CharField', [], {'default': "'unpaid'", 'max_length': '200'}),
			'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
		},
		u'core.reservation': {
			'Meta': {'object_name': 'Reservation'},
			'arrival_time': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
			'arrive': ('django.db.models.fields.DateField', [], {}),
			'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
			'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
			'depart': ('django.db.models.fields.DateField', [], {}),
			'guest_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
			'hosted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'last_msg': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
			'location': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reservations'", 'null': 'True', 'to': u"orm['core.Location']"}),
			'purpose': ('django.db.models.fields.TextField', [], {}),
			'rate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'room': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Room']", 'null': 'True'}),
			'status': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '200', 'blank': 'True'}),
			'tags': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
			'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
			'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reservations'", 'to': u"orm['auth.User']"})
		},
		u'core.room': {
			'Meta': {'object_name': 'Room'},
			'beds': ('django.db.models.fields.IntegerField', [], {}),
			'cancellation_policy': ('django.db.models.fields.CharField', [], {'default': "'24 hours'", 'max_length': '400'}),
			'default_rate': ('django.db.models.fields.IntegerField', [], {}),
			'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
			'location': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rooms'", 'null': 'True', 'to': u"orm['core.Location']"}),
			'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
			'primary_use': ('django.db.models.fields.CharField', [], {'default': "'private'", 'max_length': '200'}),
			'shared': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
		},
		u'core.userprofile': {
			'Meta': {'object_name': 'UserProfile'},
			'bio': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
			'city': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
			'customer_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
			'discussion': ('django.db.models.fields.TextField', [], {}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
			'image_thumb': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
			'links': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
			'projects': ('django.db.models.fields.TextField', [], {}),
			'referral': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
			'sharing': ('django.db.models.fields.TextField', [], {}),
			'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
			'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
		}
	}

	complete_apps = ['core']