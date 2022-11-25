from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from api.models import Trip


class CustomUser(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pfp = models.URLField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=10, null=True, blank=True)
    is_vendor = models.BooleanField(default=False)
    upcoming_trips = models.ManyToManyField(
        Trip, blank=True, related_name='users_confirmed')
    past_trips = models.ManyToManyField(
        Trip, blank=True, related_name='passengers')

    def __str__(self):
        return str(f"{self.user.first_name.capitalize()} - {self.user.email}")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        CustomUser.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.customuser.save()
