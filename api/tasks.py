from api.models import Trip
from celery import shared_task
from django.db import transaction


@shared_task(bind=True)
def trip_expired(self, trip_id):
    with transaction.atomic():
        trip = Trip.objects.get(id=trip_id)
        trip.status = "Past"
        trip.save()
        return f"Marked trip #[{trip_id}] as a past trip"
