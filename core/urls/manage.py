from django.conf.urls import patterns, include, url

# custom management (admin) patterns
urlpatterns = patterns('core.views', 
	url(r'reservations/$', 'ReservationManageList', name='reservation_manage_list'),
	url(r'reservation/(?P<reservation_id>\d+)/$', 'ReservationManage', name='reservation_manage'),
    url(r'reservation/(?P<reservation_id>\d+)/action/$', 'ReservationManageUpdate', name='reservation_manage_update'), 
    url(r'reservation/(?P<reservation_id>\d+)/chargecard/$', 'ReservationChargeCard', name='reservation_charge_card'), 
    url(r'reservation/(?P<reservation_id>\d+)/togglecomp/$', 'ReservationToggleComp', name='reservation_toggle_comp'), 
    url(r'reservation/(?P<reservation_id>\d+)/sendreceipt/$', 'ReservationSendReceipt', name='reservation_send_receipt'), 
    url(r'reservation/(?P<reservation_id>\d+)/sendmail/$', 'ReservationSendMail', name='reservation_send_mail'), 
)


