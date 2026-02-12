from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from clever_assignment.photographers.models import Photographer

class PhotographerListTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.url = '/api/v1/photographers/'
		self.p1 = Photographer.objects.create(name='Alice Adams', url='https://example.com/alice')
		self.p2 = Photographer.objects.create(name='Bob Brown', url='https://example.com/bob')
		self.p3 = Photographer.objects.create(name='Charlie Clark', url='https://example.com/charlie')

	def test_list_photographers(self):
		resp = self.client.get(self.url)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertEqual(resp.data['count'], 3)

	def test_search_by_name(self):
		resp = self.client.get(f'{self.url}?search=Alice')
		self.assertEqual(resp.data['count'], 1)
		self.assertEqual(resp.data['results'][0]['name'], 'Alice Adams')

	def test_search_no_results(self):
		resp = self.client.get(f'{self.url}?search=Zzzzzz')
		self.assertEqual(resp.data['count'], 0)

	def test_ordering_by_name(self):
		resp = self.client.get(f'{self.url}?ordering=name')
		names = [r['name'] for r in resp.data['results']]
		self.assertEqual(names, ['Alice Adams', 'Bob Brown', 'Charlie Clark'])

	def test_ordering_by_name_desc(self):
		resp = self.client.get(f'{self.url}?ordering=-name')
		names = [r['name'] for r in resp.data['results']]
		self.assertEqual(names, ['Charlie Clark', 'Bob Brown', 'Alice Adams'])

	def test_pagination(self):
		for i in range(25):
			Photographer.objects.create(name=f'Photographer {i}', url=f'https://example.com/p{i}')
		resp = self.client.get(self.url)
		self.assertEqual(resp.data['count'], 28)
		self.assertEqual(len(resp.data['results']), 20)
		self.assertIsNotNone(resp.data['next'])
