import os
import time
import urllib
import sys
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):
	#help = "Set all users to given email, password and customer ID"
	#args = "[email_address] [password] [customer_id]"
	requires_system_checks = True

	def handle(self, *labels, **options):
		#if not labels or len(labels) < 1: raise CommandError('Args: <email_address> <password> <customer_id>')

		print "Checking %d users..." % User.objects.all().count()
		
		nonalpha = []
		dup_emails = []
		for u in User.objects.filter(is_active=True):
			if not u.username.replace("_", "").isalnum():
				nonalpha.append(u)
				print "%s: not alphanumeric" % u.username
				print "    UserID: %d" % u.id
				print "    Last Login: %s" % u.last_login
		
			if u.email not in dup_emails:
				others_with_email = User.objects.filter(email=u.email, is_active=True)
				if others_with_email.count() > 1:
					dup_emails.append(u.email)
					print "%s: Duplicate email" % u.email
					for o in others_with_email:
						print "    %s/%d: %s" % (o.username, o.id, o.last_login)
		
		print "%d alphanumeric problems" % len(nonalpha)
		print "%d duplicate email problems" % len(dup_emails)