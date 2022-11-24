from django.urls import path
from . import trip_views, request_views

urlpatterns = [

    # trip URLs
    path('past', trip_views.PastTripsView.as_view(), name='past_trips'),
    path('upcoming', trip_views.UpcomingTripsView.as_view(), name='upcoming_trips'),
    path('create-trip', trip_views.TripCreateView.as_view(), name='create_trip'),
    path('trip/<int:id>', trip_views.TripDetailView.as_view(), name='trip_detail'),
    path('trip/update/<int:pk>',
         trip_views.TripUpdateView.as_view(), name='trip_update'),
    path('trip/remove-passengers/<int:pk>',
         trip_views.RemovePassengersView.as_view(), name='remove_passengers'),

    # request URLs
    path('request/all-sent', request_views.SentRequestsView.as_view(),
         name='sent_requests'),
    path('request/all-received', request_views.ReceivedRequestsView.as_view(),
         name='received_requests'),
    path('request/new', request_views.RequestReceivedView.as_view(),
         name='new_request_received'),
    path('request/accept', request_views.RequestAcceptView.as_view(),
         name='accept_request'),
    path('request/reject', request_views.RequestRejectView.as_view(),
         name='reject_request')

]
