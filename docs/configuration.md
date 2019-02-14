When getting a new instance up and running in a production setting, there are several things to be configured for your particular uses.

The majority of the configuration is around

- settings which are mostly environment variables `settings/common.py` file
- customizing templates
- customizing default emails

## Location Settings

- `MAX_BOOKING_DAYS` sets a limit for the longest a guest can request a
  booking for. This is easily to override in the admin interface, but we have
  found a sane default to be helpful.
- `WELCOME_EMAIL_DAYS_AHEAD` says how many days ahead to send guests their
  welcome email with house details.
- The stripe keys are available in your `stripe.js` account. The payment
  processing in modernomad is closely integrated with stripe and requires you
  to have your own stripe account.
- EMAIL_SUBJECT_PREFIX and DEFAULT_FROM_EMAIL are used when generating emails
  to send to guests from the manage pages and elsewhere on the site. Usually
  DEFAULT_FROM_EMAIL will be the same as your production email setting. The
  EMAIL_SUBJECT_PREFIX is best set to something short and clear, like your
  house name.
- The social media settings are used to share with guests info about how to get
  connected with the house and its activities. They are sent to guests in the
  welcome email so make sure to populate these.

## Stripe in development

If you want to test Stripe payments, you need to set up an account and get some test keys.

First, [create an account](https://dashboard.stripe.com/register). On the left-hand menu, click "Developers", then "API Keys".

**Important:** Make sure the keys start with `pk_test_` and `sk_test_` otherwise you will be charging real credit cards!

Copy and paste these keys into your `local_settings.py` file. If you're using Docker, they go in the `.env` file.

## Local Settings

- When in DEVELOPMENT mode, modernomad will send emails to stdout. In
  PRODUCTION mode, you will need an email account that you can configure to
  send and receive real emails. Configure the email settings for production
  mode with the correct SMTP settings.

## Email Templates
There are two places email templates are stored. The first is in
`templates/emails` and the other is in EmailTemplate models, which are
accessible and customizable via the Django admin interface.

### templates/emails

These are emails that are developed once and generally not changed again, and
that don't necessarily need to be configurable by house admins. Although you
can change any of these templates, the majority are administrative emails seen
by house admins.

- admin_today_notification is a sparse text email that goes out daily
  announcing arrivals and departures.
- invoice is currently unused
- receipt is automatically sent when a user pays for their booking. At a
  minimum, this should be customized for the details of your house name,
  location, and legal information. this is an HTML email so there is a text and
  html version, make sure to change both.
- the newbooking email can easily be left unchanged; it is sent to house
  admins upon receipt of a new booking request.
- The pre_arrival_welcome email is sent to guests before they arrive and
  contains details completely specific to your house. Make sure to customize
  this, and take note of the variables available to the template.

### EmailTemplate objects

Under Django's `/admin` pages, there are also a series of Email Templates that
can be added and customized by authorized users from the browser. These
templates are used to pre-populate a list of options, that house admins can
select from, and customize, when emailing a guest from the `/manage` pages.

These emails should represent the tone and language of your house. You can
define as many or as few as you like. Several email templates are automatically
installed with the software, which you can use as a starting point for your
own.

## Defining Rooms

It is necessary to define the rooms available in your house. These room objects
are used to display availability on the booking request page. Rooms can be
defined in the admin pages under `/admin/core/room/`. Rooms have a name,
optional description, default rate, a primary use (guest or private) and a
cancellation policy (which default to 24 hours but can be overwritten on a
per-room basis).

## Adding House Admins
Any user can be promoted to a resident and/or house admin. Residents are
displayed on the `community` page; House admins receive email notifications of
new booking requests and have permissions to manage those requests on the
website.

A user must have an account before being added to any special group. Once the
user has created an account, go to the admin page for users
(`/admin/auth/user`) and visit their individual user page. Check the `staff
status` box, and select one or both of the `house_admin` and `residents`
groups, then save the user. C'est tout!




