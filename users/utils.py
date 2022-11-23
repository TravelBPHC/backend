from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
import jwt


def get_user(request):

    token = str(request.headers['Authorization'].split(" ")[1])
    decoded = jwt.decode(
        token, key=settings.SECRET_KEY, algorithms=["HS256"])
    user_id = decoded['id']
    user = get_object_or_404(User, id=user_id)
    return user
