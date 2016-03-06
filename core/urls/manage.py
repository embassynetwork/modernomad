from django.conf.urls import patterns, include, url

# custom management patterns
urlpatterns = patterns('core.views', 
	url(r'^payments/$', 'payments_today', name='location_payments_today'),
	url(r'^payments/(?P<year>\d+)/(?P<month>\d+)$', 'payments', name='location_payments'),
	url(r'^today/$', 'manage_today', name='manage_today'),
	url(r'reservations/$', 'ReservationManageList', name='reservation_manage_list'),
	url(r'reservation/create/$', 'ReservationManageCreate', name='reservation_manage_create'),
	url(r'reservation/(?P<reservation_id>\d+)/$', 'ReservationManage', name='reservation_manage'),
	url(r'reservation/(?P<reservation_id>\d+)/action/$', 'ReservationManageAction', name='reservation_manage_action'), 
	url(r'reservation/(?P<reservation_id>\d+)/togglecomp/$', 'ReservationToggleComp', name='reservation_toggle_comp'), 
	url(r'reservation/(?P<reservation_id>\d+)/sendreceipt/$', 'ReservationSendReceipt', name='reservation_send_receipt'), 
	url(r'reservation/(?P<reservation_id>\d+)/sendwelcome/$', 'ReservationSendWelcomeEmail', name='reservation_send_welcome'), 
	url(r'reservation/(?P<reservation_id>\d+)/sendmail/$', 'ReservationSendMail', name='reservation_send_mail'), 
	url(r'bill/(?P<bill_id>\d+)/charge/$', 'BillCharge', name='bill_charge'), 
	url(r'bill/(?P<bill_id>\d+)/payment/$', 'ManagePayment', name='manage_payment'), 
	url(r'bill/(?P<bill_id>\d+)/addbillitem/$', 'AddBillLineItem', name='add_bill_item'), 
	url(r'bill/(?P<bill_id>\d+)/deletebillitem/$', 'DeleteBillLineItem', name='delete_bill_item'), 
	url(r'bill/(?P<bill_id>\d+)/recalculate/$', 'RecalculateBill', name='recalculate_bill'), 
	url(r'reservation/(?P<reservation_id>\d+)/edit/$', 'ReservationManageEdit', name='reservation_manage_edit'), 
	url(r'^subscriptions/create$', 'SubscriptionManageCreate', name='subscription_manage_create'),
	url(r'^subscriptions/(?P<subscription_id>\d+)/$', 'SubscriptionManageDetail', name='subscription_manage_detail'),
	url(r'^subscriptions/(?P<subscription_id>\d+)/update_end_date/$', 'SubscriptionManageUpdateEndDate', name='subscription_manage_update_end_date'),
	url(r'^subscriptions/(?P<subscription_id>\d+)/generateallbills/$', 'SubscriptionManageGenerateAllBills', name='subscription_manage_all_bills'),
	url(r'^subscriptions/$', 'SubscriptionsManageList', name='subscriptions_manage_list'),
)


