from django.conf.urls import patterns, include, url
import registration.backends.default.urls
from core.views import Registration

import core.forms

# Add the user registration and account management patters from the
# django-registration package, overriding the initial registration
# view to collect our additional user profile information.
user_patterns = patterns('',
    url(r'^register/$', Registration.as_view(form_class = core.forms.UserProfileForm),
        name='registration_register'),
)
user_patterns += registration.backends.default.urls.urlpatterns

user_patterns += patterns('core.views',
    url(r'^$', 'ListUsers', name='user_list'),
    url(r'^daterange/$', 'PeopleDaterangeQuery', name='people_daterange'),
    url(r'^(?P<username>(?!logout)(?!login)(?!register)[\w\d\-\.@+_]+)/$', 'GetUser', name='user_details'),
    url(r'^(?P<username>[\w\d\-\.@+_]+)/edit/$', 'UserEdit', name='user_edit'),
    url(r'^(?P<username>[\w\d\-\.@+_]+)/addcard/$', 'UserAddCard', name='user_add_card'),
    url(r'^(?P<username>[\w\d\-\.@+_]+)/deletecard/$', 'UserDeleteCard', name='user_delete_card'),
)

house_patterns = patterns('core.views',
    url(r'^$', 'ListHouses', name='house_list'),
    url(r'^(?P<house_id>\d+)/$', 'GetHouse', name='house_details'),
)

# urls starting in /reservation get sent here. 
reservation_patterns = patterns('core.views',
	url(r'^create/$', 'ReservationSubmit', name='reservation_submit'),
    url(r'^(?P<reservation_id>\d+)/$', 'ReservationDetail', name='reservation_detail'), 
	url(r'^(?P<reservation_id>\d+)/edit/$', 'ReservationEdit', name='reservation_edit'), 
    url(r'^(?P<reservation_id>\d+)/confirm/$', 'ReservationConfirm', name='reservation_confirm'), 
    url(r'^(?P<reservation_id>\d+)/delete/$', 'ReservationDelete', name='reservation_delete'), 
    url(r'^(?P<reservation_id>\d+)/cancel/$', 'ReservationCancel', name='reservation_cancel'), 

)

# /room patterns
room_patterns = patterns('core.views',
	url(r'availability/$', 'CheckRoomAvailability', name='room_availability'),
)


# custom management (admin) patterns
management_patterns = patterns('core.views', 
	url(r'reservations/$', 'ReservationList', name='reservation_list'),
	url(r'reservation/(?P<reservation_id>\d+)/$', 'ReservationManage', name='reservation_manage'),
    url(r'reservation/(?P<reservation_id>\d+)/action/$', 'ReservationManageUpdate', name='reservation_manage_update'), 
    url(r'reservation/(?P<reservation_id>\d+)/chargecard/$', 'ReservationChargeCard', name='reservation_charge_card'), 
    url(r'reservation/(?P<reservation_id>\d+)/togglecomp/$', 'ReservationToggleComp', name='reservation_toggle_comp'), 
    url(r'reservation/(?P<reservation_id>\d+)/sendmail/$', 'ReservationSendMail', name='reservation_send_mail'), 
)

