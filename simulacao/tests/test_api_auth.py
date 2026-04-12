from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

class TokenAuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email='test@example.com'
        )

    def test_obtain_token(self):
        """Testa se é possível obter um token com credenciais válidas"""
        url = '/api-token-auth/'
        data = {
            'username': self.username,
            'password': self.password
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        
    def test_obtain_token_invalid_credentials(self):
        """Testa se falha ao tentar obter token com senha errada"""
        url = '/api-token-auth/'
        data = {
            'username': self.username,
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
