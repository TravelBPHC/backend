from django.urls import path
from .views import PastTripsView, UpcomingTripsView, TripCreateView, TripDetailView

urlpatterns = [
    path('past', PastTripsView.as_view(), name='past_trips'),
    path('upcoming', UpcomingTripsView.as_view(), name='upcoming_trips'),

    path('create-trip', TripCreateView.as_view(), name='create_trip'),
    path('trip/<int:id>', TripDetailView.as_view(), name='trip_detail'),
]
