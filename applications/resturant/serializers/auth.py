# applications/resturant/serializers/auth.py
from rest_framework import serializers

from applications.resturant.serializers.core import CustomUserSerializer


class AuthRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class AuthResponseSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    user = CustomUserSerializer(required=True)
    email = serializers.EmailField(required=True)
