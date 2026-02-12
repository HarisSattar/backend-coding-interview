from rest_framework import serializers
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles creation and email normalization.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        """
        Create a new user instance.
        """
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    
    def validate_email(self, value):
        """
        Normalize email input.
        """
        return value.strip().lower()
