from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/request-created/', consumers.RequestConsumer.as_asgi()),
    path('ws/request-modified/', consumers.RequestConsumer.as_asgi()),
    path('ws/trip-created/', consumers.TripConsumer.as_asgi())
]
