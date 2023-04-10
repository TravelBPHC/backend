from django.urls import path
from . import request_views

urlpatterns = [
    path('all-sent', request_views.SentRequestsView.as_view(),
         name='sent_requests'),
    path('all-received', request_views.ReceivedRequestsView.as_view(),
         name='received_requests'),
    path('new', request_views.RequestReceivedView.as_view(),
         name='new_request_received'),
    path('mailaccept', request_views.AcceptFromMail.as_view(),
         name='accept_request_from_mail'),
    path('mailreject', request_views.RejectFromMail.as_view(),
         name='reject_request_from_mail'),
    path('reject', request_views.RejectRequestView.as_view(),
         name='reject_request'),
    path('accept', request_views.AcceptRequestView.as_view(),
         name='accpet_request'),
]
