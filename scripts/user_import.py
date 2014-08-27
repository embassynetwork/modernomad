from django.contrib.auth.models import User, Group
import json

'''
Usage
./manage shell
import user_import
user_import.import_users("farmhouse_users.json", "duplicate_users.json")
user_import.import_profiles("farmhouse_profiles.json")
'''
def import_users(data_file, reject_file, save=False):
	json_file = open(data_file)
	user_data = json.load(json_file)
	json_file.close()

	reject_file = open(reject_file, "w")
	reject_file.write("[")
	
	users = 0
	matches = 0
	for u in user_data:
		users = users + 1
		username = u['fields']['username']
		user = User.objects.filter(username=username).first()
		if user:
			matches = matches + 1
			print "Match (%d) on username %s = %s" % (matches, username, user.get_full_name())
			reject_file.write(json.dumps(u))
		else:
			email = u['fields']['email']
			user = User.objects.filter(email=email).first()
			if user:
				matches = matches + 1
				print "Match (%d) on email %s = %s" % (matches, email, user.get_full_name())
				reject_file.write(json.dumps(u))
			else:
				#{"pk": 100, "model": "auth.user", "fields": {"username": "comabi", "first_name": "Conni", 
				#"last_name": "Biesalski", "is_active": true, "is_superuser": false, "is_staff": false, 
				#"last_login": "2014-07-01T20:32:51.215Z", "groups": [], "user_permissions": [], 
				#"password": "pbkdf2_sha256$10000$vSqyCxVMYKa3$E3weQBNVckvZUmvXh70pYOuK31EExUiAL0SVHoDKdJ4=", 
				#"email": "c.biesalski@gmail.com", "date_joined": "2014-07-01T20:30:41.137Z"}}
				
				new_user = User(username=username, email=email)
				new_user.first_name =  u['fields']['first_name']
				new_user.last_name =  u['fields']['last_name']
				new_user.is_active =  u['fields']['is_active']
				new_user.is_superuser =  u['fields']['is_superuser']
				new_user.is_staff =  u['fields']['is_staff']
				new_user.last_login =  u['fields']['last_login']
				new_user.date_joined =  u['fields']['date_joined']
				new_user.password =  u['fields']['password']
				new_user.save()
				
				for g in u['fields']['groups']:
					group = Group.objects.get(name=g[0])
					new_user.groups.add(group)
				new_user.save()
				
	reject_file.write("]")
	reject_file.close()
	print "Users: %d, Matches: %d" % (users, matches)

def import_profiles(data_file):
	json_file = open(data_file)
	profile_data = json.load(json_file)
	json_file.close()
	
	for p in profile_data:
		#{u'pk': 125, u'model': u'core.userprofile', u'fields': 
		#{u'bio': u"Hello! My husband has a job in SF and he is currently couch surfing and commuting via bike. Myself and our two small children (2yrs and 9mo) are staying with family in Sacramento until we can find somewhere closer. We are looking for a temporary place, such as your offer, so we can be together and focus on our bigger vision of renting a large house with like minded people in the Berkeley/Oakland area long term. One bedroom is wonderful for all of us, I know it sounds like a lot, but we are a close family and it works for us. \r\nThank you for your consideration, please don't hesitate to call/text/email with any questions. \r\nWe are wanting to move ASAP, but we can be flexible. ", 
		#u'updated': u'2014-08-15T19:42:20.413Z', 
		#u'sharing': u'We would love to learn how a successful community house is run-all the ins and outs and how you got started. We would love to share the sweet presence of our beautiful children. We would also like to share music. ', 
		#u'links': u'', 
		#u'city': u'', 
		#u'image': u'avatars/dfc336d1-55c1-4cb1-960e-f868507634fe.png', 
		#u'referral': u'Luke Madera', 
		#u'user': [u'Jackee_Bikes'], 
		#u'image_thumb': u'avatars/dfc336d1-55c1-4cb1-960e-f868507634fe.thumb.png', 
		#u'customer_id': None, 
		#u'discussion': u'Poly question-why spend time, energy, and self on a new relationship when that could be spend on your spouse instead? ', 
		#u'projects': u"Looking for a large house in the Berkeley area to rent with other people! Once that in complete, we would like to participate in the 'food is free' project, make our house into an 'in the grid off the grid', work on our 4 hour work week muse, write songs to sing and preform together, busk around SF electronic music (mostly a looper) for extra cash, teach DJ/electronic music lessons, train dogs, work on building bikes..... I could go on. ;)"}
		username = p['fields']['user'][0]
		user = User.objects.filter(username=username).first()
		if not user:
			print "Username '%s' not found!" % username
		else:
			profile = user.profile
			if not profile.bio: profile.bio = p['fields']['bio']
			if not profile.updated: profile.updated = p['fields']['updated']
			if not profile.sharing: profile.sharing = p['fields']['sharing']
			if not profile.links: profile.links = p['fields']['links']
			if not profile.city: profile.city = p['fields']['city']
			if not profile.image: profile.image = p['fields']['image']
			if not profile.image_thumb: profile.image_thumb = p['fields']['image_thumb']
			if not profile.referral: profile.referral = p['fields']['referral']
			if not profile.discussion: profile.discussion = p['fields']['discussion']
			if not profile.projects: profile.projects = p['fields']['projects']
			profile.save()
