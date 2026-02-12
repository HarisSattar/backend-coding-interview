from rest_framework import generics
from .models import Photographer
from .serializers import PhotographerSerializer

class PhotographerListView(generics.ListAPIView):
	"""
	API endpoint to list photographers.
	Supports search and ordering by name and creation date.
	"""
	queryset = Photographer.objects.all()
	serializer_class = PhotographerSerializer
	search_fields = ['name']
	ordering_fields = ['name', 'created_at']
	ordering = ['created_at']