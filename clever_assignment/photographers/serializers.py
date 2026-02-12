from rest_framework import serializers
from .models import Photographer

class PhotographerSerializer(serializers.ModelSerializer):
    """
    Serializer for Photographer model.
    Serializes all fields for API responses.
    """
    class Meta:
        model = Photographer
        fields = '__all__'