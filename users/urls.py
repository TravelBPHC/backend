from django.urls import path
from .views import AuthenticateView, PhoneView, UserDetailView, AllUsersView, AddSubscription, RemoveSubscription

urlpatterns = [
    path('auth', AuthenticateView.as_view(), name='authenticate'),
    path('phone', PhoneView.as_view(), name='phone'),
    path('all', AllUsersView.as_view(), name='all_users'),
    path('subscribe', AddSubscription.as_view(), name='subscribe_notifs'),
    path('unsubscribe', RemoveSubscription.as_view(), name='unsubscribe_notifs'),
    path('', UserDetailView.as_view(), name='user_detail'),
]
