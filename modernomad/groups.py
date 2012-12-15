# Custom groups for handling permissions. Custom permissions can be defined
# within a model's Meta class,  or you can create permissions directly.

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# house managers is a group that gives its users all permissions 
# associated with reservation objects. (the three default permissions 
# associated with all models are 'create', 'change', and 'delete'). 
# use get_or_create so this script can be run on every startup without 
# complaining about the existing group
house_admin, success = Group.objects.get_or_create(name="house_admin")

# group needs to be saved *before* permissions can be added. 
house_admin.save()

reservation_ct = ContentType.objects.get(model='reservation')
reservation_permissions = Permission.objects.filter(content_type=reservation_ct)
for perm in reservation_permissions:
	house_admin.permissions.add(perm)

# also create a group to put all house residents into - this might not
# necessarily be the exact same set of users as house admins.
Group.objects.get_or_create(name="residents")
