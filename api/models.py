from django.db import models
from django.conf import settings

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
    seats = models.IntegerField(default=0)
    vacancies = models.IntegerField(default=0)
    waiting_time = models.CharField(max_length=50)

    def __str__(self):
        return f'Trip from {self.source} to {self.destination} on {self.departure_date}'

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
        User, on_delete=models.DO_NOTHING, related_name='sent_requests')
    receiver = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='received_requests')

    def __str__(self):
        return f"Request for the post: {self.post_link}"
