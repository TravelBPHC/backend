from rest_framework import permissions
from django.conf import settings
from rest_framework.exceptions import APIException
from django.contrib.auth.models import User
from rest_framework import status
import jwt


class IsLoggedIn(permissions.BasePermission):
    message = 'User needs to be logged in'

    def has_permission(self, request, view):
        token = str(request.headers['Authorization'].split(" ")[1])
        if token is None:
            raise NotLoggedIn()
        else:
            decoded = jwt.decode(
                token, key=settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded['id']
            qs = User.objects.filter(id=user_id)
            if (len(qs) == 0):
                raise NotLoggedIn()
            else:
                return True


class NotLoggedIn(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {'error': 'user not logged in'}
