import uuid
from django.db import models

class Photographer(models.Model):
	"""
	Photographer model representing a photographer entity.
	Stores name, profile URL, and timestamps.
	"""
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=255)
	url = models.URLField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		indexes = [
			models.Index(fields=['name']),
			models.Index(fields=['created_at']),
		]

	def __str__(self):
		"""
		String representation of Photographer.
		"""
		return f"{self.name} ({self.id})"
