from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.utils import get_user
from .serializers import TripSerializer
from users.permissions import IsLoggedIn
from .models import Trip
from django.contrib.auth.models import User


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
        data = request.data

        source, destination, departure_date, departure_time = data.get('source'), data.get(
            'destination'), data.get('departure_date'), data.get('departure_time')
        waiting_time, vendor, seats, details = data.get(
            'waiting_time'), data.get('vendor'), data.get('seats'), data.get('details')

        trip = Trip.objects.create(source=source, destination=destination, departure_date=departure_date,
                                   departure_time=departure_time, waiting_time=waiting_time, vendor=vendor, seats=seats, details=details, creator=user, status="Unconfirmed")

        trip.users_confirmed.add(user.customuser)
        confirmed_passengers = data.get('passengers').split(',')
        for passenger_email in confirmed_passengers:
            temp = User.objects.get(email=passenger_email)
            trip.users_confirmed.add(temp.customuser)

        trip.save()

        return Response(data={'success': f'Trip from {source} to {destination} on {departure_date} created'}, status=status.HTTP_201_CREATED)


class TripUpdateView(APIView):

    permission_classes = [IsLoggedIn]

    def patch(self, request, pk):

        user = get_user(request)
        trip = Trip.objects.get(pk=pk)

        if user.id == trip.creator.id:
            serializer = TripSerializer(trip, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(data={"error": "wrong parameters"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data={"error": "only the creator of a trip can edit it"}, status=status.HTTP_403_FORBIDDEN)


class RemovePassengersView(APIView):

    permission_classes = [IsLoggedIn]

    def post(self, request, pk):

        user = get_user(request)
        trip = Trip.objects.get(pk=pk)

        if user.id == trip.creator.id:
            passengers_to_remove = request.data.get('passengers').split(',')

            for passenger_email in passengers_to_remove:
                if passenger_email == user.email:
                    continue
                temp = User.objects.get(email=passenger_email)
                trip.users_confirmed.remove(temp.customuser)

            trip.save()
            return Response(data={"success": "specified passenger(s) removed"}, status=status.HTTP_200_OK)
        else:
            return Response(data={"error": "only the creator of a trip can edit it"}, status=status.HTTP_403_FORBIDDEN)


class TripDetailView(RetrieveAPIView):

    permission_classes = [IsLoggedIn]

    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    lookup_field = 'id'
