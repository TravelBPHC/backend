from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('users.urls')),
    path('api/request/', include('api.request_urls')),
    path('api/trip/', include('api.trip_urls')),
]
