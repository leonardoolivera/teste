from rest_framework.test import APITestCase

from apps.core.models import Campus, Institution, LibraryBranch
from apps.users.models import User


class CatalogApiTests(APITestCase):
    def setUp(self):
        self.institution = Institution.objects.create(name='IFMS', code='IFMS')
        self.campus = Campus.objects.create(institution=self.institution, name='Campus CG', code='CG')
        self.branch = LibraryBranch.objects.create(campus=self.campus, name='Biblioteca Central', code='BC')
        self.operator = User.objects.create_user(
            email='bibliotecario@ifms.edu.br',
            password='teste123',
            role='librarian',
            library_branch=self.branch,
        )

    def test_catalog_list_is_public(self):
        response = self.client.get('/api/v1/catalog/records/')

        self.assertEqual(response.status_code, 200)

    def test_catalog_write_requires_authenticated_operator(self):
        response = self.client.post(
            '/api/v1/catalog/records/',
            {'title': 'Arquitetura Limpa', 'isbn': '1234567890'},
            format='json',
        )

        self.assertEqual(response.status_code, 401)

    def test_authenticated_operator_can_create_record_and_copy(self):
        self.client.force_authenticate(user=self.operator)

        record_response = self.client.post(
            '/api/v1/catalog/records/',
            {'title': 'Arquitetura Limpa', 'isbn': '1234567890'},
            format='json',
        )
        self.assertEqual(record_response.status_code, 201)

        copy_response = self.client.post(
            '/api/v1/catalog/copies/',
            {
                'bibliographic_record': record_response.json()['id'],
                'library_branch': str(self.branch.id),
                'asset_code': 'PAT-100',
                'barcode': 'BAR-100',
                'status': 'available',
            },
            format='json',
        )
        self.assertEqual(copy_response.status_code, 201)
        self.assertEqual(copy_response.json()['asset_code'], 'PAT-100')
