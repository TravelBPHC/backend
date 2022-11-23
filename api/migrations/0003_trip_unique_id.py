# Generated by Django 3.2.6 on 2022-11-23 15:15

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_trip_vendor'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='unique_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
