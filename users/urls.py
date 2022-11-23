from django.urls import path
from .views import AuthenticateView, PhoneView, UserDetailView

urlpatterns = [
    path('auth', AuthenticateView.as_view(), name='authenticate'),
    path('phone', PhoneView.as_view(), name='phone'),
    path('', UserDetailView.as_view(), name='user_detail'),
]
