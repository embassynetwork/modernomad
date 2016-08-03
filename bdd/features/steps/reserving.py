from core.models import *
import datetime
from datetime import timedelta
import time

@given(u'a new site visitor is looking at options to stay at "{location_name}"')
def impl(context, location_name):
    location = Location.objects.get(name = location_name)
    context.browser.visit(context.config.server_url + '/locations/' + location.slug + '/stay')

@when(u'they want to say {days_in_future:d} days from now for {nights:d} nights')
def impl(context, days_in_future, nights):
    # JKS: note, this will break when we push the new reservation code.
    today = datetime.datetime.today()
    arrive = today + timedelta(days=days_in_future)
    depart = arrive + timedelta(days=nights)

    context.browser.fill('arrive', arrive.strftime("%m/%d/%Y"))
    context.browser.fill('depart', depart.strftime("%m/%d/%Y"))
    context.browser.find_by_tag('body').click()
    time.sleep(10)

@then(u'ensure they are offered "Swanky Hostel" and "Love Nest" rooms')
def impl(context):
    assert False

@when(u'they ask to book a bed in "Swanky Hostel"')
def impl(context):
    assert False

@then(u'the house admins get an email about a new pending reservation')
def impl(context):
    assert False

@then(u'they should have a pending reservation')
def impl(context):
    assert False

@then(u'they should be asked to create a profile')
def impl(context):
    assert False

@when(u'they create a valid profile')
def impl(context):
    assert False
