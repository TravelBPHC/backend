from django.urls import path
from . import trip_views

urlpatterns = [
    path('past', trip_views.PastTripsView.as_view(), name='past_trips'),
    path('upcoming', trip_views.UpcomingTripsView.as_view(),
         name='upcoming_trips'),
    path('create', trip_views.TripCreateView.as_view(), name='create_trip'),
    path('<int:id>', trip_views.TripDetailView.as_view(), name='trip_detail'),
    path('update/<int:pk>',
         trip_views.TripUpdateView.as_view(), name='trip_update'),
    path('remove-passengers/<int:pk>',
         trip_views.RemovePassengersView.as_view(), name='remove_passengers'),
    path('all-active',
         trip_views.AllPostsView.as_view(), name='all_active'),
    path('done',
         trip_views.TripDoneView.as_view(), name='trip_done'),
    path('delete/<int:pk>',
         trip_views.DeleteTripView.as_view(), name='trip_delete')
]
