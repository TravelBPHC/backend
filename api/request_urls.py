from django.urls import path
from . import request_views

urlpatterns = [
    path('all-sent', request_views.SentRequestsView.as_view(),
         name='sent_requests'),
    path('all-received', request_views.ReceivedRequestsView.as_view(),
         name='received_requests'),
    path('new', request_views.RequestReceivedView.as_view(),
         name='new_request_received'),
    path('accept', request_views.RequestAcceptView.as_view(),
         name='accept_request'),
    path('reject', request_views.RequestRejectView.as_view(),
         name='reject_request')

]
