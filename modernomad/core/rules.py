from . import models
import rules


@rules.predicate
def location_is_visible(user, location):
    return any([
        location.visibility == models.LOCATION_PUBLIC,
        location.visibility == models.LOCATION_LINK
    ])


@rules.predicate
def user_belongs_to_location(user, location):
    return user in location.get_members()


location_is_visible = location_is_visible | user_belongs_to_location
rules.add_perm('location.can_view', location_is_visible)
