import json
from django.conf import settings
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.utils import get_user
from .serializers import RequestSerializer
from users.permissions import IsLoggedIn
from .models import Trip, Request
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.core import mail
from django.core.signing import Signer
from decouple import config
from pywebpush import webpush, WebPushException


class SentRequestsView(ListAPIView):

    permission_classes = [IsLoggedIn]

    def get(self, request):

        user = get_user(request)
        serializer = RequestSerializer(
            user.sent_requests, many=True)
        return Response(serializer.data)


class ReceivedRequestsView(ListAPIView):

    permission_classes = [IsLoggedIn]

    def get(self, request):

        user = get_user(request)
        serializer = RequestSerializer(
            user.received_requests, many=True)
        return Response(serializer.data)


class RequestReceivedView(APIView):

    permission_classes = [IsLoggedIn]

    def post(self, request):

        data = request.data
        post_link, trip_id, requestor_email, creator_email = data.get(
            'trip_link'), data.get('trip_id'), data.get('requestor'), data.get('creator')
        requestor = User.objects.get(email=requestor_email)
        creator = User.objects.get(email=creator_email)
        trip = Trip.objects.get(id=trip_id)
        req = Request.objects.create(post_link=post_link, source=trip.source, destination=trip.destination,
                                     departure_date=trip.departure_date, departure_time=trip.departure_time, status="Unconfirmed", sender=requestor, receiver=creator, for_trip=trip)
        req.save()

        signer = Signer(salt=str(settings.SECRET_KEY))
        signed_email = signer.sign_object({"email": requestor.email})
        html_body = get_template('request_received.html')
        frontend_link = config("FRONTEND_LINK")
        action_link = f"{frontend_link}/request-approval?id={signed_email}&pid={trip_id}&rid={req.id}&plink={post_link}"

        email_context = {
            "receiver": creator,
            "sender": requestor,
            "post_link": str(post_link),
            "source": str(trip.source),
            "destination": str(trip.destination),
            "departure_date": str(trip.departure_date),
            "departure_time": str(trip.departure_time),
            "action_link": str(action_link)
        }

        notification_context = {
            "type": "new request",
            "sender": requestor.first_name,
            "departure_date": str(trip.departure_date),
            "destination": str(trip.destination)
        }

        # sending push notification
        notification_receiver = creator.customuser
        if notification_receiver.get_notifs:
            try:
                webpush(
                    subscription_info={
                        "endpoint": notification_receiver.endpoint,
                        "keys": {
                            "p256dh": notification_receiver.p256dh_key,
                            "auth": notification_receiver.auth_key
                        }},
                    data=json.dumps(notification_context),
                    vapid_private_key=config("VAPID_PRIVATE_KEY"),
                    vapid_claims={
                        "sub": "mailto:bphctravel@gmail.com",
                    },
                    ttl=12 * 60 * 60,
                    verbose=True
                )
                print("Notification sent successfully")
            except WebPushException as e:
                print(
                    f"something went wrong while sending the notification, exception message: {e}")

        # sending email
        body = html_body.render(email_context)
        message = EmailMultiAlternatives(
            subject=f'Travel@BPHC - New request by {requestor.first_name}',
            body=f'Hey {creator.first_name}, {requestor.first_name} has requested to travel along with you on this trip: {post_link}\n\nTo accept or reject, click on this link: {action_link}',
            to=[creator.email],
            from_email=f"TravelBPHC<{settings.EMAIL_HOST_USER}>"
        )

        message.attach_alternative(body, "text/html")
        connection = mail.get_connection()
        connection.send_messages([message])

        return Response(data={"Message": f"Request created, mail and notification sent to {creator.email}"})


class AcceptFromMail(APIView):

    def get(self, request):

        signer = Signer(salt=str(settings.SECRET_KEY))
        signed = request.GET.get('id', None)
        trip_id = request.GET.get('pid', None)
        req_id = request.GET.get('rid', None)
        post_link = request.GET.get('plink', None)
        unsigned = signer.unsign_object(signed)
        email = unsigned['email']
        req = Request.objects.get(id=req_id)

        if req.receiver is not None:

            if signed is not None and trip_id is not None and req_id is not None and post_link is not None:
                requestor = User.objects.get(email=email)
                trip = Trip.objects.get(id=int(trip_id))
                req = Request.objects.get(id=req_id)
                creator = trip.creator

                req.status = "Accepted"
                req.receiver = None
                requestor.customuser.upcoming_trips.add(trip)
                trip.vacancies -= 1

                trip.save()
                req.save()
                requestor.save()

                html_body = get_template('request_accepted.html')

                context = {
                    "receiver": requestor,
                    "sender": creator,
                    "post_link": str(post_link),
                    "source": str(trip.source),
                    "destination": str(trip.destination),
                    "departure_date": str(trip.departure_date),
                    "departure_time": str(trip.departure_time)
                }

                notification_context = {
                    "type": "request accepted",
                    "sender": creator.first_name,
                    "departure_date": str(trip.departure_date),
                    "destination": str(trip.destination)
                }

                # sending push notification
                notification_receiver = requestor.customuser
                if notification_receiver.get_notifs:
                    try:
                        webpush(
                            subscription_info={
                                "endpoint": notification_receiver.endpoint,
                                "keys": {
                                    "p256dh": notification_receiver.p256dh_key,
                                    "auth": notification_receiver.auth_key
                                }},
                            data=json.dumps(notification_context),
                            vapid_private_key=config("VAPID_PRIVATE_KEY"),
                            vapid_claims={
                                "sub": "mailto:bphctravel@gmail.com",
                            },
                            ttl=12 * 60 * 60,
                            verbose=True
                        )
                        print("Notification sent successfully")
                    except WebPushException as e:
                        print(
                            f"something went wrong while sending the notification, exception message: {e}")

                body = html_body.render(context)
                message = EmailMultiAlternatives(
                    subject=f'Request accepted',
                    body=f'Hey {requestor.first_name}, {creator.first_name} has accepted your request to travel along with you on this trip: {post_link}\n',
                    to=[requestor.email],
                    from_email=f"TravelBPHC<{settings.EMAIL_HOST_USER}>"
                )

                message.attach_alternative(body, "text/html")
                connection = mail.get_connection()
                connection.send_messages([message])

                return Response(data={"success": f"Request accepted"}, status=status.HTTP_200_OK)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(data={"error": "already responded to this request"}, status=status.HTTP_400_BAD_REQUEST)


class RejectFromMail(APIView):

    def get(self, request):

        signer = Signer(salt=str(settings.SECRET_KEY))
        signed = request.GET.get('id', None)
        trip_id = request.GET.get('pid', None)
        req_id = request.GET.get('rid', None)
        post_link = request.GET.get('plink', None)
        unsigned = signer.unsign_object(signed)
        email = unsigned['email']
        req = Request.objects.get(id=req_id)

        if req.receiver is not None:

            if signed is not None and trip_id is not None and req_id is not None and post_link is not None:
                requestor = User.objects.get(email=email)
                trip = Trip.objects.get(id=int(trip_id))
                req = Request.objects.get(id=int(req_id))
                creator = trip.creator

                req.status = "Rejected"
                req.receiver = None
                req.save()

                html_body = get_template('request_rejected.html')

                context = {
                    "receiver": requestor,
                    "sender": creator,
                    "post_link": str(post_link),
                    "source": str(trip.source),
                    "destination": str(trip.destination),
                    "departure_date": str(trip.departure_date),
                    "departure_time": str(trip.departure_time)
                }

                body = html_body.render(context)
                message = EmailMultiAlternatives(
                    subject=f'Request rejected',
                    body=f'Hey {requestor.first_name}, {creator.first_name} has rejected your request to travel along with you on this trip: {post_link}\n',
                    to=[requestor.email],
                    from_email=f"TravelBPHC<{settings.EMAIL_HOST_USER}>"
                )

                notification_context = {
                    "type": "request rejected",
                    "sender": creator.first_name,
                    "departure_date": str(trip.departure_date),
                    "destination": str(trip.destination)
                }

                # sending push notification
                notification_receiver = requestor.customuser
                if notification_receiver.get_notifs:
                    try:
                        webpush(
                            subscription_info={
                                "endpoint": notification_receiver.endpoint,
                                "keys": {
                                    "p256dh": notification_receiver.p256dh_key,
                                    "auth": notification_receiver.auth_key
                                }},
                            data=json.dumps(notification_context),
                            vapid_private_key=config("VAPID_PRIVATE_KEY"),
                            vapid_claims={
                                "sub": "mailto:bphctravel@gmail.com",
                            },
                            ttl=12 * 60 * 60,
                            verbose=True
                        )
                        print("Notification sent successfully")
                    except WebPushException as e:
                        print(
                            f"something went wrong while sending the notification, exception message: {e}")

                message.attach_alternative(body, "text/html")
                connection = mail.get_connection()
                connection.send_messages([message])

                return Response(data={"success": f"Request rejected"}, status=status.HTTP_200_OK)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(data={"error": "already responded to this request"}, status=status.HTTP_400_BAD_REQUEST)


class RejectRequestView(APIView):

    def get(self, request):

        email = request.GET.get('id', None)
        trip_id = request.GET.get('pid', None)
        req_id = request.GET.get('rid', None)
        post_link = request.GET.get('plink', None)
        req = Request.objects.get(id=req_id)

        if req.receiver is not None:

            if email is not None and trip_id is not None and req_id is not None and post_link is not None:
                requestor = User.objects.get(email=email)
                print(trip_id, type(trip_id))
                while trip_id == '':
                    pass
                trip = Trip.objects.get(id=int(trip_id))
                req = Request.objects.get(id=int(req_id))
                creator = trip.creator

                req.status = "Rejected"
                req.receiver = None
                req.save()

                html_body = get_template('request_rejected.html')

                context = {
                    "receiver": requestor,
                    "sender": creator,
                    "post_link": str(post_link),
                    "source": str(trip.source),
                    "destination": str(trip.destination),
                    "departure_date": str(trip.departure_date),
                    "departure_time": str(trip.departure_time)
                }

                body = html_body.render(context)
                message = EmailMultiAlternatives(
                    subject=f'Request rejected',
                    body=f'Hey {requestor.first_name}, {creator.first_name} has rejected your request to travel along with you on this trip: {post_link}\n',
                    to=[requestor.email],
                    from_email=f"TravelBPHC<{settings.EMAIL_HOST_USER}>"
                )

                notification_context = {
                    "type": "request rejected",
                    "sender": creator.first_name,
                    "departure_date": str(trip.departure_date),
                    "destination": str(trip.destination)
                }

                # sending push notification
                notification_receiver = requestor.customuser
                if notification_receiver.get_notifs:
                    print('got here')
                    try:
                        webpush(
                            subscription_info={
                                "endpoint": notification_receiver.endpoint,
                                "keys": {
                                    "p256dh": notification_receiver.p256dh_key,
                                    "auth": notification_receiver.auth_key
                                }},
                            data=json.dumps(notification_context),
                            vapid_private_key=config("VAPID_PRIVATE_KEY"),
                            vapid_claims={
                                "sub": "mailto:bphctravel@gmail.com",
                            },
                            ttl=12 * 60 * 60,
                            verbose=True
                        )
                        print("Notification sent successfully")
                    except WebPushException as e:
                        print(
                            f"something went wrong while sending the notification, exception message: {e}")

                message.attach_alternative(body, "text/html")
                connection = mail.get_connection()
                connection.send_messages([message])

                return Response(data={"success": f"Request rejected"}, status=status.HTTP_200_OK)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(data={"error": "already responded to this request"}, status=status.HTTP_400_BAD_REQUEST)


class AcceptRequestView(APIView):

    def get(self, request):

        email = request.GET.get('id', None)
        trip_id = request.GET.get('pid', None)
        req_id = request.GET.get('rid', None)
        post_link = request.GET.get('plink', None)
        req = Request.objects.get(id=req_id)

        if req.receiver is not None:

            if email is not None and trip_id is not None and req_id is not None and post_link is not None:
                requestor = User.objects.get(email=email)
                while trip_id == '':
                    pass
                trip = Trip.objects.get(id=int(trip_id))
                req = Request.objects.get(id=req_id)
                creator = trip.creator

                req.status = "Accepted"
                req.receiver = None
                requestor.customuser.upcoming_trips.add(trip)
                trip.vacancies -= 1

                trip.save()
                req.save()
                requestor.save()

                html_body = get_template('request_accepted.html')

                context = {
                    "receiver": requestor,
                    "sender": creator,
                    "post_link": str(post_link),
                    "source": str(trip.source),
                    "destination": str(trip.destination),
                    "departure_date": str(trip.departure_date),
                    "departure_time": str(trip.departure_time)
                }

                body = html_body.render(context)
                message = EmailMultiAlternatives(
                    subject=f'Request accepted',
                    body=f'Hey {requestor.first_name}, {creator.first_name} has accepted your request to travel along with you on this trip: {post_link}\n',
                    to=[requestor.email],
                    from_email=f"TravelBPHC<{settings.EMAIL_HOST_USER}>"
                )

                notification_context = {
                    "type": "request accepted",
                    "sender": creator.first_name,
                    "departure_date": str(trip.departure_date),
                    "destination": str(trip.destination)
                }

                # sending push notification
                notification_receiver = requestor.customuser
                if notification_receiver.get_notifs:
                    try:
                        webpush(
                            subscription_info={
                                "endpoint": notification_receiver.endpoint,
                                "keys": {
                                    "p256dh": notification_receiver.p256dh_key,
                                    "auth": notification_receiver.auth_key
                                }},
                            data=json.dumps(notification_context),
                            vapid_private_key=config("VAPID_PRIVATE_KEY"),
                            vapid_claims={
                                "sub": "mailto:bphctravel@gmail.com",
                            },
                            ttl=12 * 60 * 60,
                            verbose=True
                        )
                        print("Notification sent successfully")
                    except WebPushException as e:
                        print(
                            f"something went wrong while sending the notification, exception message: {e}")

                message.attach_alternative(body, "text/html")
                connection = mail.get_connection()
                connection.send_messages([message])

                return Response(data={"success": f"Request accepted"}, status=status.HTTP_200_OK)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(data={"error": "already responded to this request"}, status=status.HTTP_400_BAD_REQUEST)
