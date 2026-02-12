from rest_framework import serializers
from .models import Photo
from clever_assignment.photographers.models import Photographer

class PhotoSerializer(serializers.ModelSerializer):
    """
    Serializer for Photo model.
    Handles validation and serialization for API requests and responses.
    """
    photographer = serializers.PrimaryKeyRelatedField(queryset=Photographer.objects.all(), required=False)
    photographer_name = serializers.CharField(source='photographer.name', read_only=True)
    photographer_url = serializers.URLField(source='photographer.url', read_only=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    new_photographer_name = serializers.CharField(write_only=True, required=False)
    new_photographer_url = serializers.URLField(write_only=True, required=False)

    class Meta:
        model = Photo
        fields = [
            'id', 'width', 'height', 'url', 'photographer', 'avg_color',
            'src_original', 'src_large2x', 'src_large', 'src_medium', 'src_small',
            'src_portrait', 'src_landscape', 'src_tiny', 'alt', 'owner',
            'photographer_name', 'photographer_url',
            'new_photographer_name', 'new_photographer_url',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validate input data for photo creation and update.
        """
        has_photographer = 'photographer' in data
        has_new = data.get('new_photographer_name') and data.get('new_photographer_url')

        if self.instance is None and not has_photographer and not has_new:
            raise serializers.ValidationError(
                'Provide either "photographer" (existing UUID) or both "new_photographer_name" and "new_photographer_url".'
            )
        return data

    def update(self, instance, validated_data):
        """
        Update photo instance, handling new photographer creation if needed.
        """
        validated_data.pop('photographer', None)
        new_name = validated_data.pop('new_photographer_name', None)
        new_url = validated_data.pop('new_photographer_url', None)

        if new_name and new_url:
            photographer, _ = Photographer.objects.get_or_create(
                name=new_name, url=new_url,
            )
            instance.photographer = photographer

        return super().update(instance, validated_data)

    def create(self, validated_data):
        new_name = validated_data.pop('new_photographer_name', None)
        new_url = validated_data.pop('new_photographer_url', None)

        if new_name and new_url and 'photographer' not in validated_data:
            photographer, _ = Photographer.objects.get_or_create(
                name=new_name, url=new_url,
            )
            validated_data['photographer'] = photographer

        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user
        return super().create(validated_data)
