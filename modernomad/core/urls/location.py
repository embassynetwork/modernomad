from django.conf.urls import include, url
import modernomad.core.views.unsorted
from modernomad.core.views import location
import modernomad.core.emails.messages
import modernomad.core.urls.bookings
import modernomad.core.urls.uses
import modernomad.core.urls.manage
import modernomad.core.views.redirects
import gather.urls

per_location_patterns = [
    url(r'^$', location.LocationDetail.as_view(), name='location_detail'),
    url(r'^stay/$', modernomad.core.views.booking.StayView.as_view(), name='location_stay'),
    url(r'^stay/room/(?P<room_id>\w+)$', modernomad.core.views.booking.StayView.as_view(), name='room'),
    url(r'^community/$', modernomad.core.views.unsorted.community, name='location_community'),
    url(r'^team/$', modernomad.core.views.unsorted.team, name='location_team'),
    url(r'^guests/$', modernomad.core.views.unsorted.guests, name='location_guests'),
    url(r'^occupancy/$', modernomad.core.views.unsorted.occupancy, name='location_occupancy'),
    url(r'^occupancy/room/(?P<room_id>\d+)/(?P<year>\d+)/$', modernomad.core.views.unsorted.room_occupancy, name='room_occupancy'),
    url(r'^calendar/$', modernomad.core.views.unsorted.calendar, name='location_calendar'),
    url(r'^thanks/$', modernomad.core.views.unsorted.thanks, name='location_thanks'),
    url(r'^today/$', modernomad.core.views.unsorted.today, name='location_today'),

    url(r'^json/room/$', modernomad.core.views.booking.RoomApiList.as_view(), name='json_room_list'),
    url(r'^json/room/(?P<room_id>\w+)/$', modernomad.core.views.booking.RoomApiDetail.as_view(), name='json_room_detail'),

    url(r'^edit/settings/$', modernomad.core.views.unsorted.LocationEditSettings, name='location_edit_settings'),
    url(r'^edit/users/$', modernomad.core.views.unsorted.LocationEditUsers, name='location_edit_users'),
    url(r'^edit/content/$', modernomad.core.views.unsorted.LocationEditContent, name='location_edit_content'),
    url(r'^edit/emails/$', modernomad.core.views.unsorted.LocationEditEmails, name='location_edit_emails'),
    url(r'^edit/pages/$', modernomad.core.views.unsorted.LocationEditPages, name='location_edit_pages'),
    url(r'^edit/rooms/(?P<room_id>\d+)/$', modernomad.core.views.unsorted.LocationEditRoom, name='location_edit_room'),
    url(r'^edit/rooms/new$', modernomad.core.views.unsorted.LocationNewRoom, name='location_new_room'),
    url(r'^edit/rooms/$', modernomad.core.views.unsorted.LocationManageRooms, name='location_manage_rooms'),

    url(r'^email/current$', modernomad.core.emails.messages.current, name='location_email_current'),
    url(r'^email/stay$', modernomad.core.emails.messages.stay, name='location_email_stay'),
    url(r'^email/residents$', modernomad.core.emails.messages.residents, name='location_email_residents'),
    url(r'^email/test80085$', modernomad.core.emails.messages.test80085, name='location_email_test'),
    url(r'^email/unsubscribe$', modernomad.core.emails.messages.unsubscribe, name='location_email_unsubscribe'),
    url(r'^email/announce$', modernomad.core.emails.messages.announce, name='location_email_announce'),

    # internal views
    url(r'^rooms_availabile_on_dates/$', modernomad.core.views.unsorted.RoomsAvailableOnDates, name='rooms_available_on_dates'),

    url(r'^booking/', include(modernomad.core.urls.bookings)),
    url(r'^use/', include(modernomad.core.urls.uses)),
    url(r'^manage/', include(modernomad.core.urls.manage)),

    url(r'^events/', include(gather.urls)),

    # redirect from old 'reservation' paths
    url(r'^reservation/(?P<rest_of_path>(.+))/$', modernomad.core.views.redirects.reservation_redirect),

]

urlpatterns = [
    url(r'^$', modernomad.core.views.unsorted.location_list, name='location_list'),
    url(r'^(?P<location_slug>[\w-]+)/', include(per_location_patterns)),
]
