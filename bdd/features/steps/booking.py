from core.models import *
from robber import expect
import datetime
from datetime import timedelta
import time
import os.path
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))


def visit_path(context, path):
    context.browser.visit(context.config.server_url + path)


@given(u'a new site visitor is looking at options to stay at "{location_name}"')
def impl(context, location_name):
    location = Location.objects.get(name=location_name)
    visit_path(context, '/locations/' + location.slug + '/stay/')


@when(u'they want to stay {days_in_future:d} days from now for {nights:d} nights')
def impl(context, days_in_future, nights):
    # JKS: note, this will break when we push the new booking code.
    today = datetime.datetime.today()
    arrive = today + timedelta(days=days_in_future)
    depart = arrive + timedelta(days=nights)

    context.browser.fill('arrive', arrive.strftime("%m/%d/%Y"))
    context.browser.fill('depart', depart.strftime("%m/%d/%Y"))
    context.browser.find_by_tag('body').click()
    time.sleep(3)


@then(u'ensure they are offered {room_count:d} rooms')
def impl(context, room_count):
    rooms = context.browser.find_by_css('.room-card')
    expect(len(rooms)).to.eq(room_count)


@when(u'they ask to book a bed in "{room_name}"')
def impl(context, room_name):
    for room_link in context.browser.find_by_css('.room-card a.room-link'):
        heading = room_link.find_by_css('h3')
        title = heading.html
        if title.startswith(room_name):
            room_link.click()
            break

    time.sleep(1)

    form = context.browser.find_by_css('.booking-request-form')
    print(form.html)
    context.browser.fill("purpose", "I want to have a great stay")
    context.browser.find_by_id('submit-booking-request').first.click()


@when(u'they create a valid profile')
def impl(context):
    avatar_filename = os.path.normpath(SITE_ROOT + '/../../data/avatars/craig.jpg')
    context.browser.attach_file('image', avatar_filename)
    context.browser.fill("bio", "I am just really great")
    context.browser.fill("projects", "saving the world")
    context.browser.fill("sharing", "I'd like to learn to knit")
    context.browser.fill("discussion", "I'm interested in talking about narwhals")
    context.browser.fill("first_name", "Bilbo")
    context.browser.fill("last_name", "Baggins")
    context.browser.fill("referral", "Jessy Kate")
    context.browser.find_by_name('city').type("San Francisco, USA")
    context.browser.fill("email", "bilbo@baggins.com")
    context.browser.fill("password1", "theonering")
    context.browser.fill("password2", "theonering")

    time.sleep(1)

    context.browser.execute_script("$('input[name=city]').prop('disabled', false)")
    context.browser.find_by_id('profilesubmit').first.click()

    time.sleep(1)

    context.current_user = User.objects.get(email="bilbo@baggins.com")

    assert context.browser.is_text_present("Thank you! Your booking has been submitted")


@then(u'the house admins get an email about a new pending booking')
def impl(context):
    # time.sleep(30)
    assert False


@then(u'they should have a pending booking')
def impl(context):
    assert context.current_user
    visit_path(context, '/people/' + context.current_user.username)
    context.browser.find_link_by_text('Bookings').click()
    table_rows = context.browser.find_by_css('#booking-list-table tr')
    expect(len(table_rows)).to.eq(1)


@then(u'they should be asked to create a profile')
def impl(context):
    assert context.browser.is_text_present("Please make a profile to complete your booking request")
