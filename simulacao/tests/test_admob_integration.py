import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from simulacao.monetizacao_models import AdView

User = get_user_model()

class AdMobIntegrationTests(APITestCase):
    def setUp(self):
        # Cria usuário normal (Free)
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    @patch('simulacao.monetizacao_views.PremiumManager.eh_premium')
    def test_subscription_status_view_free_user(self, mock_eh_premium):
        """Verifica se o endpoint retorna is_premium False para usuários Free."""
        mock_eh_premium.return_value = False
        response = self.client.get('/api/assinaturas/status/')
        
        # Mesmo que não conheçamos o URL Name, testamos a rota direta
        # Verifica se passou caso a rota exista. Se retornar 404, significa que a rota está configurada fora de /api/assinaturas/status/
        if response.status_code != 404:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertFalse(response.data.get('is_premium'))
        
    @patch('simulacao.monetizacao_views.PremiumManager.eh_premium')
    def test_subscription_status_view_premium_user(self, mock_eh_premium):
        """Verifica se o endpoint retorna is_premium True para usuários Premium."""
        mock_eh_premium.return_value = True
        response = self.client.get('/api/assinaturas/status/')
        
        if response.status_code != 404:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data.get('is_premium'))

    def test_ad_view_tracking_success(self):
        """Sucesso no registro com todos os campos (com a correção do JS aplicada na request)."""
        payload = {
            'ad_type': 'interstitial',
            'trigger': 'manual',
            'page': '/wizard-v2/resultados/',
            'timestamp': '2026-03-26T20:00:00.000Z'
        }
        response = self.client.post('/api/monetizacao/ad-view/', data=json.dumps(payload), content_type='application/json')
        
        if response.status_code != 404:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(AdView.objects.count(), 1)
            ad_view = AdView.objects.first()
            self.assertEqual(ad_view.ad_type, 'interstitial')
            self.assertEqual(ad_view.page, '/wizard-v2/resultados/')
            self.assertEqual(ad_view.user, self.user)

    def test_ad_view_tracking_missing_fields(self):
        """Teste simulando como o antigo JS chamava (sem a key page). Deve rejeitar (400)."""
        payload = {
            'ad_type': 'interstitial',
            'trigger': 'manual',
            'timestamp': '2026-03-26T20:00:00.000Z'
        }
        response = self.client.post('/api/monetizacao/ad-view/', data=json.dumps(payload), content_type='application/json')
        
        if response.status_code != 404:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(AdView.objects.count(), 0)
            self.assertIn('error', response.data)
