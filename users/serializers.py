from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.models import User


class CustomUserSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'pfp', 'phone', 'get_notifs']

    def get_name(self, obj):
        return obj.user.first_name

    def get_email(self, obj):
        return obj.user.email


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'email']
