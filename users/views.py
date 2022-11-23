import base64
import json
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import status
from .utils import get_user
from .serializers import CustomUserSerializer
from .models import CustomUser
from google.auth.transport import requests
from google.oauth2 import id_token
from random import randint
from .permissions import IsLoggedIn
import jwt


class AuthenticateView(APIView):

    def post(self, request):

        token = request.data.get('credential', None)

        if token is not None:

            info = id_token.verify_oauth2_token(
                token, requests.Request(), '980575440299-7v5ap704i43iao1v61atqs3872f1mifr.apps.googleusercontent.com')

            email, first_name, pfp, last_name = info['email'], info.get(
                'given_name', None), info['picture'], info.get("family_name", "")
            response = Response()

            qs = User.objects.filter(email=email)

            if (len(qs) == 0):
                password = str(
                    hash(email + first_name + str(randint(1, 1000) * randint(1, 1000))))

                user = User.objects.create_user(
                    email=email, password=password, username=email, first_name=first_name, last_name=last_name)

                user.customuser.pfp = pfp
                user.save()

                response.data = {
                    "created": f"User with the email ID {email} created"}
                token = jwt.encode(payload={"id": user.id},
                                   key=settings.SECRET_KEY, algorithm="HS256")
                request.session['token'] = str(token)
                response.status = status.HTTP_201_CREATED

                return response

            else:
                user = qs[0]
                token = jwt.encode(payload={"id": user.id},
                                   key=settings.SECRET_KEY, algorithm="HS256")
                request.session['token'] = str(token)
                response.data = {
                    "success": f"User with email ID {email} logged in successfully"}
                response.status = status.HTTP_200_OK
                return response

        else:
            return Response(data={"error": "auth token not found"}, status=status.HTTP_400_BAD_REQUEST)


class PhoneView(APIView):

    permission_classes = [IsLoggedIn]

    def patch(self, request):

        phone = request.data.get('phone', None)

        if phone is not None:
            user = get_user(request)
            user.customuser.phone = phone
            user.save()
            return Response(data={"success": f"{user.first_name}'s phone number updated to {phone}"})

        else:
            return Response(data={"error": "phone number not found"}, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):

    permission_classes = [IsLoggedIn]

    def get(self, request):
        user = get_user(request)
        serializer = CustomUserSerializer(user.customuser, many=False)
        return Response(serializer.data)
