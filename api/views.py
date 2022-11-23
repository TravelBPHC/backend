from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.utils import get_user
from .serializers import TripSerializer, RequestSerializer
from users.permissions import IsLoggedIn
from .models import Trip, Request


class PastTripsView(ListAPIView):

    permission_classes = [IsLoggedIn]

    def get(self, request):

        user = get_user(request)
        serializer = TripSerializer(user.customuser.past_trips, many=True)
        return Response(serializer.data)


class UpcomingTripsView(ListAPIView):

    permission_classes = [IsLoggedIn]

    def get(self, request):

        user = get_user(request)
        serializer = TripSerializer(user.customuser.upcoming_trips, many=True)
        return Response(serializer.data)


class TripCreateView(CreateAPIView):

    permission_classes = [IsLoggedIn]

    def post(self, request):

        user = get_user(request)

        source, destination, departure_date, departure_time = request.data.get('source'), request.data.get(
            'destination'), request.data.get('departure_date'), request.data.get('departure_time')
        waiting_time, vendor, seats, details = request.data.get(
            'waiting_time'), request.data.get('vendor'), request.data.get('seats'), request.data.get('details')

        trip = Trip.objects.create(source=source, destination=destination, departure_date=departure_date,
                                   departure_time=departure_time, waiting_time=waiting_time, vendor=vendor, seats=seats, details=details, creator=user, status="Unconfirmed")

        trip.save()

        return Response(data={'success': f'Trip from {source} to {destination} on {departure_date} created'}, status=status.HTTP_201_CREATED)


class TripDetailView(RetrieveAPIView):

    permission_classes = [IsLoggedIn]

    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    lookup_field = 'id'
