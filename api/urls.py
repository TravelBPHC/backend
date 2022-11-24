from django.urls import path
from .views import PastTripsView, UpcomingTripsView, TripCreateView, TripDetailView, TripUpdateView, RemovePassengersView

urlpatterns = [
    path('past', PastTripsView.as_view(), name='past_trips'),
    path('upcoming', UpcomingTripsView.as_view(), name='upcoming_trips'),

    path('create-trip', TripCreateView.as_view(), name='create_trip'),
    path('trip/<int:id>', TripDetailView.as_view(), name='trip_detail'),
    path('trip/update/<int:pk>', TripUpdateView.as_view(), name='trip_update'),
    path('trip/remove-passengers/<int:pk>',
         RemovePassengersView.as_view(), name='remove_passengers'),
]
