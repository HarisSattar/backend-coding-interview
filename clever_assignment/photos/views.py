from rest_framework import viewsets, permissions
from .models import Photo
from .serializers import PhotoSerializer
from .permissions import IsOwnerOrAdmin

class PhotoViewSet(viewsets.ModelViewSet):
	"""
	API endpoint for managing photos.
	Supports CRUD, filtering, searching, and ordering.
	"""
	queryset = Photo.objects.all()
	serializer_class = PhotoSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]
	filterset_fields = ['photographer', 'avg_color', 'owner']
	search_fields = ['alt', 'photographer__name']
	ordering_fields = ['created_at', 'width', 'height']
	ordering = ['created_at']

	def perform_create(self, serializer):
		"""
		Set owner field to current user when creating a photo.
		"""
		serializer.save(owner=self.request.user)
