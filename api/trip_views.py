from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.utils import get_user
from .serializers import TripSerializer
from users.permissions import IsLoggedIn
from .models import Trip
from django.contrib.auth.models import User
import datetime


class AllPostsView(ListAPIView):

    def get_queryset(self):

        queryset = Trip.objects.filter(status="Upcoming").exclude(vacancies=0)
        fields = ['src', 'dest', 'dt']

        for field in fields:

            globals()[field] = self.request.query_params.get(f'{field}')

            if globals()[field]:

                if field == 'src':
                    queryset = queryset.filter(
                        source__icontains=globals()[field])

                elif field == 'dest':
                    queryset = queryset.filter(
                        destination__icontains=globals()[field])

                elif field == 'dt':
                    dt = globals()[field]
                    date = datetime.datetime.strptime(dt, '%Y-%m-%d').date()

                    queryset = queryset.filter(departure_date=date)

        return queryset

    serializer_class = TripSerializer


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
                                   departure_time=departure_time, waiting_time=waiting_time, vendor=vendor, seats=seats, vacancies=(int(seats) - 1), details=details, creator=user, status="Upcoming")

        trip.users_confirmed.add(user.customuser)
        confirmed_passengers = data.get('passengers').split(',')
        for passenger_email in confirmed_passengers:
            if passenger_email == user.email:
                continue
            temp = User.objects.get(email=passenger_email)
            trip.users_confirmed.add(temp.customuser)
            trip.vacancies -= 1

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
                trip.vacancies += 1

            trip.save()
            return Response(data={"success": "specified passenger(s) removed"}, status=status.HTTP_200_OK)
        else:
            return Response(data={"error": "only the creator of a trip can edit it"}, status=status.HTTP_403_FORBIDDEN)


class TripDetailView(RetrieveAPIView):

    permission_classes = [IsLoggedIn]

    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    lookup_field = 'id'


class TripDoneView(APIView):

    def post(self, request):

        trip_id = request.data.get('trip_id', None)
        trip = Trip.objects.get(id=trip_id)

        trip.status = "Past"
        trip.vacancies = 0
        passengers = trip.users_confirmed.all()
        for passenger in passengers:
            passenger.upcoming_trips.remove(trip)
            passenger.past_trips.add(trip)
            passenger.save()
        trip.save()

        return Response(data={"success": f"Trip no. {trip_id} marked as a past trip"})
