# Tests for the core app, including management commands and API endpoints.

from django.core.management import call_command
from django.test import TestCase
from io import StringIO
from clever_assignment.photos.models import Photo
from clever_assignment.photographers.models import Photographer
import os
from django.urls import reverse
from rest_framework.test import APITestCase

class HealthCheckApiTest(APITestCase):
    """
    Test the /api/v1/health/ endpoint to ensure it returns a 200 OK and the expected response.
    """
    def test_healthcheck_returns_ok(self):
        url = reverse('health-check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

class ImportPhotosCommandTest(TestCase):
    """
    Test the import_photos management command to ensure photos and photographers are imported from CSV.
    """
    def setUp(self):
        # Create a temporary CSV file for import
        self.csv_content = (
            'id,width,height,url,photographer,photographer_url,photographer_id,avg_color,src.original,src.large2x,src.large,src.medium,src.small,src.portrait,src.landscape,src.tiny,alt\n'
            '1,100,200,http://photo/1,Test Photographer,http://photographer/1,1,#123,http://src/o.jpg,http://src/l2x.jpg,http://src/l.jpg,http://src/m.jpg,http://src/s.jpg,http://src/p.jpg,http://src/ls.jpg,http://src/t.jpg,Test alt\n'
        )
        with open('photos.csv', 'w', encoding='utf-8') as f:
            f.write(self.csv_content)

    def tearDown(self):
        # Remove the temporary CSV file after the test
        if os.path.exists('photos.csv'):
            os.remove('photos.csv')

    def test_import_photos_command(self):
        """
        Run the import_photos command and check that one photo and one photographer are created.
        """
        out = StringIO()
        call_command('import_photos', stdout=out)
        self.assertIn('Imported', out.getvalue())
        self.assertEqual(Photo.objects.count(), 1)
        self.assertEqual(Photographer.objects.count(), 1)
        photo = Photo.objects.first()
        photographer = Photographer.objects.first()
        self.assertEqual(photo.photographer, photographer)
        self.assertEqual(photo.alt, 'Test alt')
        self.assertEqual(photographer.name, 'Test Photographer')
