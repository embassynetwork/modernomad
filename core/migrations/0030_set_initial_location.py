# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

	def forwards(self, orm):
		"Write your forwards methods here."
		# Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."

		# this datamigration is run after the schemigration to create the new
		# location model in the database. 
		# first we create a new location object. then we add the new location
		# object as a the foreign key value to the new location field on each
		# of the reservation and room objects
		loc = orm['core.Location'].objects.create(
				name = "Embassy SF",
				slug = 'embassysf',
				short_description = "The flagship location in the Embassy Network to prototyping a new model of Home",
				about_page = "about us goes here",
				address = "399 Webster Street, San Francisco, CA, 94117",
				stay_page = "stay page goes here",
				front_page_stay = "front page stay text",
				front_page_participate = "front page participate text",
				max_reservation_days = 14,
				welcome_email_days_ahead = 2,
				house_access_code = 1,
				stripe_secret_key = "stripesecret",
				stripe_public_key = "stripepublic",
				mailgun_api_key = "mailgunapi",
				mailgun_domain = "example.com",
				email_subject_prefix = "[Embassy SF] ",
				default_from_email = "stay@yourhouse.com",
				)
		loc.save()

		reservations = orm['core.Reservation'].objects.all()
		for r in reservations:
			r.location = loc
			r.save()

		rooms = orm['core.Room'].objects.all()
		for room in rooms:
			room.location = loc
			room.save()

	def backwards(self, orm):
		"Write your backwards methods here."

		# the backwards data migration will remove all references to the location object
		reservations = orm['core.Reservation'].objects.all()
		for r in reservations:
			r.location = None
			r.save()

		rooms = orm['core.Room'].objects.all()
		for room in rooms:
			room.location = None
			room.save()

		# not sure if this is necessary (the previous migration is what
		# actually deletes the location object)
		db.delete_table('core_location')
		location_content_type = ContentType.objects.filter(model='location')
		location_content_type.delete()

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
	symmetrical = True
