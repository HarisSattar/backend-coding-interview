from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from clever_assignment.users.models import User
from clever_assignment.photographers.models import Photographer
from clever_assignment.photos.models import Photo

def make_photo_data(photographer, **overrides):
	data = {
		'width': 1920, 'height': 1080,
		'url': 'https://example.com/photo.jpg',
		'photographer': str(photographer.id),
		'avg_color': '#123456',
		'src_original': 'https://example.com/o.jpg',
		'src_large2x': 'https://example.com/l2x.jpg',
		'src_large': 'https://example.com/l.jpg',
		'src_medium': 'https://example.com/m.jpg',
		'src_small': 'https://example.com/s.jpg',
		'src_portrait': 'https://example.com/p.jpg',
		'src_landscape': 'https://example.com/ls.jpg',
		'src_tiny': 'https://example.com/t.jpg',
		'alt': 'A test photo',
	}
	data.update(overrides)
	return data

class PhotoListTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.photographer = Photographer.objects.create(name='Jane', url='https://example.com/jane')

	def test_list_photos_unauthenticated(self):
		Photo.objects.create(**{k: v for k, v in make_photo_data(self.photographer).items() if k != 'photographer'}, photographer=self.photographer)
		resp = self.client.get('/api/v1/photos/')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertEqual(resp.data['count'], 1)
		self.assertEqual(len(resp.data['results']), 1)

	def test_list_photos_pagination(self):
		for i in range(25):
			Photo.objects.create(
				width=100, height=100,
				url=f'https://example.com/photo{i}.jpg',
				photographer=self.photographer,
				avg_color='#000000',
				src_original=f'https://example.com/o{i}.jpg',
				src_large2x=f'https://example.com/l2x{i}.jpg',
				src_large=f'https://example.com/l{i}.jpg',
				src_medium=f'https://example.com/m{i}.jpg',
				src_small=f'https://example.com/s{i}.jpg',
				src_portrait=f'https://example.com/p{i}.jpg',
				src_landscape=f'https://example.com/ls{i}.jpg',
				src_tiny=f'https://example.com/t{i}.jpg',
				alt=f'Photo {i}',
			)
		resp = self.client.get('/api/v1/photos/')
		self.assertEqual(resp.data['count'], 25)
		self.assertEqual(len(resp.data['results']), 20)
		self.assertIsNotNone(resp.data['next'])

		resp2 = self.client.get('/api/v1/photos/?page=2')
		self.assertEqual(len(resp2.data['results']), 5)
		self.assertIsNone(resp2.data['next'])

class PhotoCRUDTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User.objects.create_user(email='owner@example.com', password='testpass123')
		self.photographer = Photographer.objects.create(name='Jane', url='https://example.com/jane')
		self._auth(self.user)

	def _auth(self, user):
		resp = self.client.post('/api/v1/auth/login/', {'email': user.email, 'password': 'testpass123'})
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {resp.data["access"]}')

	def test_create_photo(self):
		resp = self.client.post('/api/v1/photos/', make_photo_data(self.photographer), format='json')
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		self.assertEqual(str(resp.data['owner']), str(self.user.id))

	def test_create_photo_unauthenticated(self):
		self.client.credentials()
		resp = self.client.post('/api/v1/photos/', make_photo_data(self.photographer), format='json')
		self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_retrieve_photo(self):
		photo = Photo.objects.create(
			**{k: v for k, v in make_photo_data(self.photographer).items() if k != 'photographer'},
			photographer=self.photographer, owner=self.user,
		)
		resp = self.client.get(f'/api/v1/photos/{photo.id}/')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertEqual(resp.data['id'], str(photo.id))

	def test_update_own_photo(self):
		photo = Photo.objects.create(
			**{k: v for k, v in make_photo_data(self.photographer).items() if k != 'photographer'},
			photographer=self.photographer, owner=self.user,
		)
		resp = self.client.patch(f'/api/v1/photos/{photo.id}/', {'alt': 'Updated alt'}, format='json')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertEqual(resp.data['alt'], 'Updated alt')

	def test_update_cannot_change_photographer(self):
		other_photographer = Photographer.objects.create(name='Other', url='https://example.com/other')
		photo = Photo.objects.create(
			**{k: v for k, v in make_photo_data(self.photographer).items() if k != 'photographer'},
			photographer=self.photographer, owner=self.user,
		)
		resp = self.client.patch(
			f'/api/v1/photos/{photo.id}/',
			{'photographer': str(other_photographer.id)},
			format='json',
		)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		photo.refresh_from_db()
		self.assertEqual(photo.photographer_id, self.photographer.id)

	def test_update_photographer_via_new_fields(self):
		photo = Photo.objects.create(
			**{k: v for k, v in make_photo_data(self.photographer).items() if k != 'photographer'},
			photographer=self.photographer, owner=self.user,
		)
		resp = self.client.patch(
			f'/api/v1/photos/{photo.id}/',
			{'new_photographer_name': 'Corrected Name', 'new_photographer_url': 'https://example.com/corrected'},
			format='json',
		)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertEqual(resp.data['photographer_name'], 'Corrected Name')
		photo.refresh_from_db()
		self.assertEqual(photo.photographer.name, 'Corrected Name')

	def test_create_with_existing_photographer(self):
		resp = self.client.post('/api/v1/photos/', make_photo_data(self.photographer), format='json')
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		self.assertEqual(resp.data['photographer'], self.photographer.id)

	def test_create_with_new_photographer(self):
		data = make_photo_data(self.photographer)
		del data['photographer']
		data['new_photographer_name'] = 'New Artist'
		data['new_photographer_url'] = 'https://example.com/newartist'
		resp = self.client.post('/api/v1/photos/', data, format='json')
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		self.assertTrue(Photographer.objects.filter(name='New Artist').exists())
		self.assertEqual(resp.data['photographer_name'], 'New Artist')

	def test_create_with_new_photographer_deduplicates(self):
		data = make_photo_data(self.photographer)
		del data['photographer']
		data['new_photographer_name'] = 'Jane'
		data['new_photographer_url'] = 'https://example.com/jane'
		self.client.post('/api/v1/photos/', data, format='json')
		data['url'] = 'https://example.com/photo2.jpg'
		self.client.post('/api/v1/photos/', data, format='json')
		self.assertEqual(Photographer.objects.filter(name='Jane', url='https://example.com/jane').count(), 1)

	def test_create_without_photographer_fails(self):
		data = make_photo_data(self.photographer)
		del data['photographer']
		resp = self.client.post('/api/v1/photos/', data, format='json')
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

	def test_delete_own_photo(self):
		photo = Photo.objects.create(
			**{k: v for k, v in make_photo_data(self.photographer).items() if k != 'photographer'},
			photographer=self.photographer, owner=self.user,
		)
		resp = self.client.delete(f'/api/v1/photos/{photo.id}/')
		self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(Photo.objects.filter(id=photo.id).exists())

class PhotoPermissionTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.owner = User.objects.create_user(email='owner@example.com', password='testpass123')
		self.other = User.objects.create_user(email='other@example.com', password='testpass123')
		self.admin = User.objects.create_superuser(email='admin@example.com', password='testpass123')
		self.photographer = Photographer.objects.create(name='Jane', url='https://example.com/jane')
		self.photo = Photo.objects.create(
			width=100, height=100,
			url='https://example.com/photo.jpg',
			photographer=self.photographer, owner=self.owner,
			avg_color='#000000',
			src_original='https://example.com/o.jpg',
			src_large2x='https://example.com/l2x.jpg',
			src_large='https://example.com/l.jpg',
			src_medium='https://example.com/m.jpg',
			src_small='https://example.com/s.jpg',
			src_portrait='https://example.com/p.jpg',
			src_landscape='https://example.com/ls.jpg',
			src_tiny='https://example.com/t.jpg',
			alt='Test',
		)

	def _auth(self, user):
		resp = self.client.post('/api/v1/auth/login/', {'email': user.email, 'password': 'testpass123'})
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {resp.data["access"]}')

	def test_other_user_cannot_update(self):
		self._auth(self.other)
		resp = self.client.patch(f'/api/v1/photos/{self.photo.id}/', {'alt': 'Hacked'}, format='json')
		self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

	def test_other_user_cannot_delete(self):
		self._auth(self.other)
		resp = self.client.delete(f'/api/v1/photos/{self.photo.id}/')
		self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

	def test_admin_can_update_any_photo(self):
		self._auth(self.admin)
		resp = self.client.patch(f'/api/v1/photos/{self.photo.id}/', {'alt': 'Admin edit'}, format='json')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertEqual(resp.data['alt'], 'Admin edit')

	def test_admin_can_delete_any_photo(self):
		self._auth(self.admin)
		resp = self.client.delete(f'/api/v1/photos/{self.photo.id}/')
		self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

	def test_unauthenticated_can_read(self):
		self.client.credentials()
		resp = self.client.get(f'/api/v1/photos/{self.photo.id}/')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)

	def test_unowned_photo_only_admin_can_modify(self):
		unowned = Photo.objects.create(
			width=100, height=100,
			url='https://example.com/unowned.jpg',
			photographer=self.photographer, owner=None,
			avg_color='#000000',
			src_original='https://example.com/o.jpg',
			src_large2x='https://example.com/l2x.jpg',
			src_large='https://example.com/l.jpg',
			src_medium='https://example.com/m.jpg',
			src_small='https://example.com/s.jpg',
			src_portrait='https://example.com/p.jpg',
			src_landscape='https://example.com/ls.jpg',
			src_tiny='https://example.com/t.jpg',
			alt='Unowned',
		)
		self._auth(self.owner)
		resp = self.client.patch(f'/api/v1/photos/{unowned.id}/', {'alt': 'Nope'}, format='json')
		self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

		self._auth(self.admin)
		resp = self.client.patch(f'/api/v1/photos/{unowned.id}/', {'alt': 'Admin'}, format='json')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)

class PhotoFilterTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User.objects.create_user(email='filter@example.com', password='testpass123')
		self.photographer1 = Photographer.objects.create(name='Alice', url='https://example.com/alice')
		self.photographer2 = Photographer.objects.create(name='Bob', url='https://example.com/bob')
		base = {
			'width': 100, 'height': 100,
			'avg_color': '#111111',
			'src_original': 'https://example.com/o.jpg',
			'src_large2x': 'https://example.com/l2x.jpg',
			'src_large': 'https://example.com/l.jpg',
			'src_medium': 'https://example.com/m.jpg',
			'src_small': 'https://example.com/s.jpg',
			'src_portrait': 'https://example.com/p.jpg',
			'src_landscape': 'https://example.com/ls.jpg',
			'src_tiny': 'https://example.com/t.jpg',
		}
		self.photo1 = Photo.objects.create(
			**base, url='https://example.com/1.jpg',
			photographer=self.photographer1, owner=self.user,
			alt='Sunset at the beach',
		)
		self.photo2 = Photo.objects.create(
			**{**base, 'avg_color': '#222222', 'width': 3000},
			url='https://example.com/2.jpg',
			photographer=self.photographer2, owner=None,
			alt='Mountain landscape',
		)

	def test_filter_by_photographer(self):
		resp = self.client.get(f'/api/v1/photos/?photographer={self.photographer1.id}')
		self.assertEqual(resp.data['count'], 1)
		self.assertEqual(resp.data['results'][0]['id'], str(self.photo1.id))

	def test_filter_by_avg_color(self):
		resp = self.client.get('/api/v1/photos/?avg_color=%23222222')
		self.assertEqual(resp.data['count'], 1)
		self.assertEqual(resp.data['results'][0]['id'], str(self.photo2.id))

	def test_search_by_alt(self):
		resp = self.client.get('/api/v1/photos/?search=sunset')
		self.assertEqual(resp.data['count'], 1)
		self.assertEqual(resp.data['results'][0]['id'], str(self.photo1.id))

	def test_search_by_photographer_name(self):
		resp = self.client.get('/api/v1/photos/?search=Bob')
		self.assertEqual(resp.data['count'], 1)
		self.assertEqual(resp.data['results'][0]['id'], str(self.photo2.id))

	def test_ordering_by_width(self):
		resp = self.client.get('/api/v1/photos/?ordering=-width')
		self.assertEqual(resp.data['results'][0]['id'], str(self.photo2.id))

	def test_ordering_by_created_at(self):
		resp = self.client.get('/api/v1/photos/?ordering=created_at')
		ids = [r['id'] for r in resp.data['results']]
		self.assertEqual(ids, [str(self.photo1.id), str(self.photo2.id)])
