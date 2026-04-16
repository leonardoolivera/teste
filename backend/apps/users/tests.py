from rest_framework.test import APITestCase

from apps.core.models import Campus, Institution, LibraryBranch
from apps.users.models import User


class UsersApiTests(APITestCase):
    def setUp(self):
        self.institution = Institution.objects.create(name='IFMS', code='IFMS')
        self.campus = Campus.objects.create(institution=self.institution, name='Campus CG', code='CG')
        self.branch = LibraryBranch.objects.create(campus=self.campus, name='Biblioteca Central', code='BC')
        self.operator = User.objects.create_user(
            email='operador@ifms.edu.br',
            password='teste123',
            role='librarian',
            library_branch=self.branch,
        )
        self.manager = User.objects.create_user(
            email='gestor@ifms.edu.br',
            password='teste123',
            role='manager',
            library_branch=self.branch,
        )

    def test_patron_create_requires_authenticated_operator(self):
        response = self.client.post(
            '/api/v1/users/patrons/',
            {
                'library_branch': str(self.branch.id),
                'registration_code': '2026001',
                'full_name': 'Maria Souza',
                'email': 'maria@ifms.edu.br',
                'category': 'student',
                'status': 'active',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 401)

    def test_authenticated_operator_can_create_patron(self):
        self.client.force_authenticate(user=self.operator)
        response = self.client.post(
            '/api/v1/users/patrons/',
            {
                'library_branch': str(self.branch.id),
                'registration_code': '2026001',
                'full_name': 'Maria Souza',
                'email': 'maria@ifms.edu.br',
                'category': 'student',
                'status': 'active',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['registration_code'], '2026001')

    def test_operator_management_requires_manager_or_admin(self):
        self.client.force_authenticate(user=self.operator)
        response = self.client.get('/api/v1/users/operators/')
        self.assertEqual(response.status_code, 403)

        self.client.force_authenticate(user=self.manager)
        manager_response = self.client.get('/api/v1/users/operators/')
        self.assertEqual(manager_response.status_code, 200)

    def test_login_returns_token_and_me_returns_user(self):
        login_response = self.client.post(
            '/api/v1/users/auth/login/',
            {'email': 'operador@ifms.edu.br', 'password': 'teste123'},
            format='json',
        )

        self.assertEqual(login_response.status_code, 200)
        token = login_response.json()['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        me_response = self.client.get('/api/v1/users/auth/me/')

        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.json()['email'], 'operador@ifms.edu.br')
