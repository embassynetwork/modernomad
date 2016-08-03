from core.models import *
from robber import expect
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
    time.sleep(1)

@then(u'ensure they are offered {room_count:d} rooms')
def impl(context, room_count):
    # JKS: this will need to be written differently when jessy pushes the rooms-migration and res-workflow branches.
    rooms = context.browser.find_by_css('.room-panel')
    expect(len(rooms)).to.eq(room_count)

@when(u'they ask to book a bed in "{room_name}"')
def impl(context, room_name):
    for room in context.browser.find_by_css('.room-panel h3'):
        if room.html.startswith(room_name):
            room.click();
            print("ROOM!")
            print(room.html)
    context.browser.fill("purpose", "I want to have a great stay")
    context.browser.find_by_id('submit-reservation').first.click()

@then(u'the house admins get an email about a new pending reservation')
def impl(context):
    time.sleep(30)
    assert False

@then(u'they should have a pending reservation')
def impl(context):
    time.sleep(30)
    assert False

@then(u'they should be asked to create a profile')
def impl(context):
    time.sleep(30)
    assert False

@when(u'they create a valid profile')
def impl(context):
    time.sleep(30)
    assert False
