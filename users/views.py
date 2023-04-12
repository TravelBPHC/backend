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

        try:

            data = {
                'code': code,
                'client_id': config('CLIENT_ID'),
                'client_secret': config('CLIENT_SECRET'),
                'redirect_uri': 'postmessage',
                'grant_type': 'authorization_code'
            }
            res = requests.post(
                'https://oauth2.googleapis.com/token', data=data)
            token, access_token, refresh_token, expires_in = res.json()['id_token'], res.json()['access_token'], res.json()[
                'refresh_token'], res.json()['expires_in']

            info = id_token.verify_oauth2_token(
                token, google_requests.Request(), config('CLIENT_ID'), clock_skew_in_seconds=1)

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
                    "token": str(token),
                    "g_access_token": str(access_token),
                    "g_refresh_token": str(refresh_token),
                    "expires_in": str(expires_in)
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
                    "token": str(token),
                    "g_access_token": str(access_token),
                    "g_refresh_token": str(refresh_token),
                    "expires_in": str(expires_in)
                }
                response.status = status.HTTP_200_OK
                return response

        except Exception as e:
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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


class AddSubscription(APIView):

    permission_classes = [IsLoggedIn]

    def post(self, request):
        try:
            payload = request.data
            print(type(payload))
            print(payload['keys'].get(
                'p256dh'))
            print(payload['keys'].get('auth'))
            p256dh_key, auth_key, endpoint = payload['keys'].get(
                'p256dh'), payload['keys'].get('auth'), payload.get('endpoint', None)
            print(payload.get('endpoint', None))
            base_user = get_user(request)
            user = base_user.customuser
            user.p256dh_key, user.auth_key, user.endpoint, user.get_notifs = p256dh_key, auth_key, endpoint, True
            user.save()
            return Response({"success": f"registered the user with the email ID: {user.user.email} to the mailing list"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class RemoveSubscription(APIView):

    permission_classes = [IsLoggedIn]

    def post(self, request):
        try:
            base_user = get_user(request)
            user = base_user.customuser
            user.p256dh_key, user.auth_key, user.endpoint, user.get_notifs = None, None, None, False
            user.save()
            return Response({"success": f"unregistered the user with the email ID: {user.email} from the mailing list"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
