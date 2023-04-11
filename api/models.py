import json
from datetime import datetime as dt
from django.db import models
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

User = settings.AUTH_USER_MODEL


class Trip(models.Model):

    source = models.CharField(max_length=255, null=False, blank=False)
    destination = models.CharField(max_length=255, null=False, blank=False)
    departure_date = models.DateField()
    departure_time = models.TimeField()
    creator = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='created_trips')
    status = models.CharField(
        max_length=50, null=False, blank=False, default="Upcoming", help_text='Upcoming or Past')
    details = models.TextField(null=True, blank=True)
    vendor = models.CharField(max_length=255, null=False, blank=False)
    car_name = models.CharField(max_length=255, null=True, blank=True)
    seats = models.IntegerField(default=0)
    price = models.IntegerField(default=None, blank=True, null=True)
    vacancies = models.IntegerField(default=0)
    waiting_time = models.CharField(max_length=50)

    def __str__(self):
        return f'Trip from {self.source} to {self.destination} on {self.departure_date}'

    def save(self, *args, **kwargs):
        ''''
        Send a message via a websocket to the client whenever a Trip object has
        been modified
        '''

        reqs = [
            {
                "requestor_email": req.sender.email,
                "status": req.status
            }
            for req in self.requests.all()
        ]

        self.departure_date = dt.strptime(
            str(self.departure_date), '%Y-%m-%d').date()
        self.departure_time = dt.strptime(
            str(self.departure_time), '%H:%M:%S').time()

        if (self._state.adding == True):
            super(Trip, self).save(*args, **kwargs)

            channel_layer = get_channel_layer()

            message = {
                "id": self.id,
                "source": self.source,
                "destination": self.destination,
                "departure_date": self.departure_date.isoformat(),
                "departure_time": self.departure_time.isoformat(),
                "creator": self.creator.email,
                "status": self.status,
                "details": self.details,
                "vendor": self.vendor,
                "car_name": self.car_name,
                "seats": self.seats,
                "price": self.price,
                "vacancies": self.vacancies,
                "waiting_time": self.waiting_time,
                "requests": reqs,
                "updated": False
            }
            async_to_sync(channel_layer.group_send)(
                'base_group', {
                    'type': 'trip_created',
                    'value': json.dumps({'message': message})
                }
            )
        else:
            super(Trip, self).save(*args, **kwargs)

            channel_layer = get_channel_layer()

            message = {
                "id": self.id,
                "source": self.source,
                "destination": self.destination,
                "departure_date": self.departure_date.isoformat(),
                "departure_time": self.departure_time.isoformat(),
                "creator": self.creator.email,
                "status": self.status,
                "details": self.details,
                "vendor": self.vendor,
                "car_name": self.car_name,
                "seats": self.seats,
                "price": self.price,
                "vacancies": self.vacancies,
                "waiting_time": self.waiting_time,
                "requests": reqs,
                "updated": True
            }
            async_to_sync(channel_layer.group_send)(
                'base_group', {
                    'type': 'trip_created',
                    'value': json.dumps({'message': message})
                }
            )

    class Meta:
        ordering = ['departure_date']


class Request(models.Model):

    post_link = models.URLField(max_length=255, blank=True, null=True)
    source = models.CharField(max_length=255, null=False, blank=False)
    destination = models.CharField(max_length=255, null=False, blank=False)
    departure_date = models.DateField()
    departure_time = models.TimeField()
    status = models.CharField(
        max_length=50, null=False, blank=False, help_text='Unconfirmed, Accepted or Rejected')
    sender = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='sent_requests', null=True)
    receiver = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='received_requests', null=True)
    for_trip = models.ForeignKey(
        Trip, on_delete=models.CASCADE, related_name='requests', blank=True,  null=True)

    def __str__(self):
        return f"Request for the post: {str(self.for_trip)}"

    def save(self, *args, **kwargs):
        ''''
        Send a message via a websocket to the client whenever a Request object has
        been created/modified
        '''
        super(Request, self).save(*args, **kwargs)
        channel_layer = get_channel_layer()
        message = {
            "id": self.id,
            "post_link": self.post_link,
            "source": self.source,
            "destination": self.destination,
            "departure_date": self.departure_date.isoformat(),
            "departure_time": self.departure_time.isoformat(),
            "status": self.status,
            "sender": self.sender.email,
            "receiver": self.receiver.email if self.receiver else None,
        }
        async_to_sync(channel_layer.group_send)(
            'base_group', {
                'type': 'request_created_or_modified',
                'value': json.dumps({'message': message})
            }
        )
