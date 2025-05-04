# applications/resturant/serializers/auth.py
from rest_framework import serializers
from applications.resturant.serializers.core import UserSerializer
class AuthRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    
    
    
class AuthResponseSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    user = UserSerializer(required=True)
    email = serializers.EmailField(required=True)