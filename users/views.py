from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import status
from decouple import config
from .utils import get_user
from .serializers import CustomUserSerializer, UserSerializer
from google.auth.transport import requests as google_requests
import requests
from google.oauth2 import id_token
from random import randint
from .permissions import IsLoggedIn
from decouple import config
import google.auth.transport.requests
import jwt


class AuthenticateView(APIView):

    def post(self, request):

        code = request.data.get('code', None)

        if code is not None:

            data = {
                'code': code,
                'client_id': config('CLIENT_ID'),
                'client_secret': config('CLIENT_SECRET'),
                'redirect_uri': 'postmessage',
                'grant_type': 'authorization_code'
            }
            res = requests.post(
                'https://oauth2.googleapis.com/token', data=data)
            token = res.json()['id_token']

            info = id_token.verify_oauth2_token(
                token, google_requests.Request(), config('CLIENT_ID'))

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

                token = jwt.encode(payload={"id": user.id},
                                   key=settings.SECRET_KEY, algorithm="HS256")
                request.session['token'] = str(token)
                response.data = {
                    "created": f"User with the email ID {email} created",
                    "token": str(token)
                }
                response.status = status.HTTP_201_CREATED

                return response

            else:
                user = qs[0]
                token = jwt.encode(payload={"id": user.id},
                                   key=settings.SECRET_KEY, algorithm="HS256")
                request.session['token'] = str(token)
                response.data = {
                    "success": f"User with email ID {email} logged in successfully",
                    "token": str(token)
                }
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


class AllUsersView(ListAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
