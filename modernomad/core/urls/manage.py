from django.conf.urls import include, url
from modernomad.core.views.unsorted import *

# custom management patterns
urlpatterns = [
    url(r'^payments/$', payments_today, name='location_payments_today'),
    url(r'^payments/(?P<year>\d+)/(?P<month>\d+)$', payments, name='location_payments'),
    url(r'^today/$', manage_today, name='manage_today'),
    url(r'bookings/$', BookingManageList, name='booking_manage_list'),
    url(r'booking/create/$', BookingManageCreate, name='booking_manage_create'),
    url(r'booking/(?P<booking_id>\d+)/$', BookingManage, name='booking_manage'),
    url(r'booking/(?P<booking_id>\d+)/action/$', BookingManageAction, name='booking_manage_action'),
    url(r'booking/(?P<booking_id>\d+)/paywithdrft/$', BookingManagePayWithDrft, name='booking_manage_pay_drft'),
    url(r'booking/(?P<booking_id>\d+)/togglecomp/$', BookingToggleComp, name='booking_toggle_comp'),
    url(r'booking/(?P<booking_id>\d+)/sendreceipt/$', BookingSendReceipt, name='booking_send_receipt'),
    url(r'booking/(?P<booking_id>\d+)/sendwelcome/$', BookingSendWelcomeEmail, name='booking_send_welcome'),
    url(r'booking/(?P<booking_id>\d+)/sendmail/$', BookingSendMail, name='booking_send_mail'),
    url(r'bill/(?P<bill_id>\d+)/charge/$', BillCharge, name='bill_charge'),
    url(r'bill/(?P<bill_id>\d+)/payment/$', ManagePayment, name='manage_payment'),
    url(r'bill/(?P<bill_id>\d+)/addbillitem/$', AddBillLineItem, name='add_bill_item'),
    url(r'bill/(?P<bill_id>\d+)/deletebillitem/$', DeleteBillLineItem, name='delete_bill_item'),
    url(r'bill/(?P<bill_id>\d+)/recalculate/$', RecalculateBill, name='recalculate_bill'),
    url(r'booking/(?P<booking_id>\d+)/edit/$', BookingManageEdit, name='booking_manage_edit'),
    url(r'^subscription/(?P<subscription_id>\d+)/bill/(?P<bill_id>\d+)/sendreceipt/$', SubscriptionSendReceipt, name='subscription_send_receipt'),
    url(r'^subscriptions/(?P<subscription_id>\d+)/sendmail/$', SubscriptionSendMail, name='subscription_send_mail'),
    url(r'^subscriptions/create$', SubscriptionManageCreate, name='subscription_manage_create'),
    url(r'^subscriptions/(?P<subscription_id>\d+)/$', SubscriptionManageDetail, name='subscription_manage_detail'),
    url(r'^subscriptions/(?P<subscription_id>\d+)/update_end_date/$', SubscriptionManageUpdateEndDate, name='subscription_manage_update_end_date'),
    url(r'^subscriptions/(?P<subscription_id>\d+)/generateallbills/$', SubscriptionManageGenerateAllBills, name='subscription_manage_all_bills'),
    url(r'^subscriptions/$', SubscriptionsManageList, name='subscriptions_manage_list'),
]
