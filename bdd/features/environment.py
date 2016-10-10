from behave import *
from splinter.browser import Browser
from django.core import management


def before_all(context):
    username = os.environ["SAUCE_USERNAME"]
    access_key = os.environ["SAUCE_ACCESS_KEY"]
    hub_url = 'http://%s:%s@ondemand.saucelabs.com:80/wd/hub' % (username, access_key)

    context.browser = Browser(
        driver_name="remote",
        url=hub_url,
        browser='chrome',
        platform="Mac OS X 10.9",
        version="31",
        name="Test of Chrome on Mac")

    # Unless we tell our test runner otherwise, set our default browser to PhantomJS
    # context.browser = Browser('firefox')
    # context.browser = Browser()

    # if context.config.browser:
    #     context.browser = Browser(context.config.browser)
    # else:
    #     context.browser = Browser('phantomjs')
    # context.browser = Browser('phantomjs')

    # When we're running with PhantomJS we need to specify the window size.
    # This is a workaround for an issue where PhantomJS cannot find elements
    # by text - see: https://github.com/angular/protractor/issues/585
    # if context.browser.driver_name == 'PhantomJS':
    #     context.browser.driver.set_window_size(1280, 1024)


def before_scenario(context, scenario):
    # Reset the database before each scenario
    # This means we can create, delete and edit objects within an
    # individual scenerio without these changes affecting our
    # other scenarios
    management.call_command('flush', verbosity=0, interactive=False)

    # At this stage we can (optionally) mock additional data to setup in the database.
    # For example, if we know that all of our tests require a 'SiteConfig' object,
    # we could create it here.


def after_all(context):
    # Quit our browser once we're done!
    # context.browser.quit()
    context.browser = None
