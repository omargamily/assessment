from rest_framework import serializers
from django.contrib.auth import get_user_model
from .services import create_user_with_group

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return create_user_with_group(
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role']
        )