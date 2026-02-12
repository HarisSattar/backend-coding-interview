from django.db import models
from django.conf import settings
import uuid

class Photo(models.Model):
	"""
	Photo model representing a photo entity.
	Stores image metadata, photographer, owner, and timestamps.
	"""
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	width = models.IntegerField()
	height = models.IntegerField()
	url = models.URLField()
	photographer = models.ForeignKey('photographers.Photographer', on_delete=models.RESTRICT)
	avg_color = models.CharField(max_length=20)
	src_original = models.URLField()
	src_large2x = models.URLField()
	src_large = models.URLField()
	src_medium = models.URLField()
	src_small = models.URLField()
	src_portrait = models.URLField()
	src_landscape = models.URLField()
	src_tiny = models.URLField()
	alt = models.TextField()
	owner = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='photos',
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		indexes = [
			models.Index(fields=['created_at']),
			models.Index(fields=['owner']),
			models.Index(fields=['avg_color']),
		]

	def __str__(self):
		"""
		String representation of Photo.
		"""
		return f"Photo {self.id}: {self.alt}"
