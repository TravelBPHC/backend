import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.exceptions import ImproperlyConfigured


class BaseConsumer(WebsocketConsumer):
    def connect(self, *args, **kwargs):
        try:
            self.group_name = kwargs.get('group_name', None)
            if self.group_name is None:
                raise ImproperlyConfigured('Group name not provided')
            async_to_sync(self.channel_layer.group_add)(
                self.group_name, self.channel_name
            )
            self.accept()
        except ImproperlyConfigured as e:
            self.accept()
            self.send(text_data=str(e))

    def disconnect(self, close_code):
        self.send(
            text_data=f"Disconnected from client with code: { {close_code}}")
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )
        super().disconnect(close_code)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        self.send(text_data=f"Received {message} from client")


class RequestConsumer(BaseConsumer):

    def connect(self, *args, **kwargs):
        kwargs = {"group_name": "request_group"}
        super().connect(*args, **kwargs)

    def request_modified(self, event):
        self.send(text_data=event.get('value'))

    def request_created(self, event):
        self.send(text_data=event.get('value'))


class TripConsumer(BaseConsumer):

    def connect(self, *args, **kwargs):
        kwargs = {"group_name": "trip_group"}
        super().connect(*args, **kwargs)

    def trip_created(self, event):
        self.send(text_data=event.get('value'))
