from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from clever_assignment.users.models import User

class UserRegistrationTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.url = '/api/v1/users/register/'

	def test_register_success(self):
		resp = self.client.post(self.url, {'email': 'new@example.com', 'password': 'testpass123'})
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		self.assertTrue(User.objects.filter(email='new@example.com').exists())

	def test_register_duplicate_email(self):
		User.objects.create_user(email='dup@example.com', password='testpass123')
		resp = self.client.post(self.url, {'email': 'dup@example.com', 'password': 'testpass123'})
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

	def test_register_missing_email(self):
		resp = self.client.post(self.url, {'password': 'testpass123'})
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

	def test_register_missing_password(self):
		resp = self.client.post(self.url, {'email': 'nopass@example.com'})
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

	def test_register_normalizes_email(self):
		resp = self.client.post(self.url, {'email': '  Test@Example.COM  ', 'password': 'testpass123'})
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		self.assertTrue(User.objects.filter(email='test@example.com').exists())

	def test_password_is_hashed(self):
		self.client.post(self.url, {'email': 'hash@example.com', 'password': 'testpass123'})
		user = User.objects.get(email='hash@example.com')
		self.assertNotEqual(user.password, 'testpass123')
		self.assertTrue(user.check_password('testpass123'))

class AuthTokenTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User.objects.create_user(email='auth@example.com', password='testpass123')

	def test_login_success(self):
		resp = self.client.post('/api/v1/auth/login/', {'email': 'auth@example.com', 'password': 'testpass123'})
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertIn('access', resp.data)
		self.assertIn('refresh', resp.data)

	def test_login_wrong_password(self):
		resp = self.client.post('/api/v1/auth/login/', {'email': 'auth@example.com', 'password': 'wrong'})
		self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_login_nonexistent_user(self):
		resp = self.client.post('/api/v1/auth/login/', {'email': 'none@example.com', 'password': 'testpass123'})
		self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_token_refresh(self):
		login = self.client.post('/api/v1/auth/login/', {'email': 'auth@example.com', 'password': 'testpass123'})
		refresh_token = login.data['refresh']
		resp = self.client.post('/api/v1/auth/refresh/', {'refresh': refresh_token})
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertIn('access', resp.data)

	def test_token_refresh_invalid(self):
		resp = self.client.post('/api/v1/auth/refresh/', {'refresh': 'invalidtoken'})
		self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
