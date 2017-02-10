from django.conf.urls import include, url
from core.views.unsorted import *
from core.views.booking import StayComponent 
import core.emails 
import core.views.redirects

per_location_patterns = [
    url(r'^$', location, name='location_home'),
    url(r'^stay/$', StayComponent, name='location_stay'),
    url(r'^stay/room/(?P<room_id>\w+)$', StayComponent, name='room'),
    url(r'^community/$', community, name='location_community'),
    url(r'^team/$', team, name='location_team'),
    url(r'^guests/$', guests, name='location_guests'),
    url(r'^occupancy/$', occupancy, name='location_occupancy'),
    url(r'^occupancy/room/(?P<room_id>\d+)/(?P<year>\d+)/$', room_occupancy, name='room_occupancy'),
    url(r'^calendar/$', calendar, name='location_calendar'),
    url(r'^thanks/$', thanks, name='location_thanks'),
    url(r'^today/$', today, name='location_today'),

    url(r'^edit/settings/$', LocationEditSettings, name='location_edit_settings'),
    url(r'^edit/users/$', LocationEditUsers, name='location_edit_users'),
    url(r'^edit/content/$', LocationEditContent, name='location_edit_content'),
    url(r'^edit/emails/$', LocationEditEmails, name='location_edit_emails'),
    url(r'^edit/pages/$', LocationEditPages, name='location_edit_pages'),
    url(r'^edit/rooms/(?P<room_id>\d+)/$', LocationEditRoom, name='location_edit_room'),
    url(r'^edit/rooms/new$', LocationNewRoom, name='location_new_room'),
    url(r'^edit/rooms/$', LocationManageRooms, name='location_manage_rooms'),

    url(r'^email/current$', core.emails.current, name='location_email_current'),
    url(r'^email/stay$', core.emails.stay, name='location_email_stay'),
    url(r'^email/residents$', core.emails.residents, name='location_email_residents'),
    url(r'^email/test80085$', core.emails.test80085, name='location_email_test'),
    url(r'^email/unsubscribe$', core.emails.unsubscribe, name='location_email_unsubscribe'),
    url(r'^email/announce$', core.emails.announce, name='location_email_announce'),

    # internal views
    url(r'^rooms_availabile_on_dates/$', RoomsAvailableOnDates, name='rooms_available_on_dates'),

    url(r'^booking/', include('core.urls.bookings')),
    url(r'^use/', include('core.urls.uses')),
    url(r'^manage/', include('core.urls.manage')),
    url(r'^room/', include('core.urls.room')),
    url(r'^events/', include('gather.urls')),

    # redirect from old 'reservation' paths
    url(r'^reservation/(?P<rest_of_path>(.+))/$', core.views.redirects.reservation_redirect),

]

urlpatterns = [
    url(r'^(?P<location_slug>\w+)/', include(per_location_patterns)),
]
