from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'pfp', 'phone']

    def get_name(self, obj):
        return obj.user.first_name

    def get_email(self, obj):
        return obj.user.email
