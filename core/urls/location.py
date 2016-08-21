from django.conf.urls import patterns, include, url

per_location_patterns = [
	url(r'^$', 'core.views.unsorted.location', name='location_home'),
	url(r'^stay/$', 'core.views.unsorted.ReservationSubmit', name='location_stay'),
	url(r'^community/$', 'core.views.unsorted.community', name='location_community'),
	url(r'^team/$', 'core.views.unsorted.team', name='location_team'),
	url(r'^guests/$', 'core.views.unsorted.guests', name='location_guests'),
	url(r'^occupancy/$', 'core.views.unsorted.occupancy', name='location_occupancy'),
	url(r'^occupancy/room/(?P<room_id>\d+)/(?P<year>\d+)/$', 'core.views.unsorted.room_occupancy', name='room_occupancy'),
	url(r'^calendar/$', 'core.views.unsorted.calendar', name='location_calendar'),
	url(r'^thanks/$', 'core.views.unsorted.thanks', name='location_thanks'),
	url(r'^today/$', 'core.views.unsorted.today', name='location_today'),

	url(r'^edit/settings/$', 'core.views.unsorted.LocationEditSettings', name='location_edit_settings'),
	url(r'^edit/users/$', 'core.views.unsorted.LocationEditUsers', name='location_edit_users'),
	url(r'^edit/content/$', 'core.views.unsorted.LocationEditContent', name='location_edit_content'),
	url(r'^edit/emails/$', 'core.views.unsorted.LocationEditEmails', name='location_edit_emails'),
	url(r'^edit/pages/$', 'core.views.unsorted.LocationEditPages', name='location_edit_pages'),
	url(r'^edit/rooms/(?P<room_id>\d+)/$', 'core.views.unsorted.LocationEditRoom', name='location_edit_room'),
    url(r'^edit/rooms/new$', 'core.views.unsorted.LocationNewRoom', name='location_new_room'),
	url(r'^edit/rooms/$', 'core.views.unsorted.LocationManageRooms', name='location_manage_rooms'),

	url(r'^email/current$', 'core.emails.current', name='location_email_current'),
	url(r'^email/stay$', 'core.emails.stay', name='location_email_stay'),
	url(r'^email/residents$', 'core.emails.residents', name='location_email_residents'),
	url(r'^email/test80085$', 'core.emails.test80085', name='location_email_test'),
	url(r'^email/unsubscribe$', 'core.emails.unsubscribe', name='location_email_unsubscribe'),
	url(r'^email/announce$', 'core.emails.announce', name='location_email_announce'),

	# internal views
	url(r'^rooms_availabile_on_dates/$', 'core.views.unsorted.RoomsAvailableOnDates', name='rooms_available_on_dates'),

	url(r'^reservation/', include('core.urls.reservations')),
	url(r'^manage/', include('core.urls.manage')),
	url(r'^room/', include('core.urls.room')),

	url(r'^events/', include('gather.urls')),
]

urlpatterns = patterns('core.views.unsorted',
	url(r'^$', 'location_list', name='location_list'),
	url(r'^(?P<location_slug>\w+)/', include(per_location_patterns)),
)
