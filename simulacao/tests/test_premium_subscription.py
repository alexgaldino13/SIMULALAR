from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from simulacao.subscription_models import Subscription, SubscriptionPlan
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class PremiumSubscriptionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test_premium', email='test@premium.com', password='testpassword')
        
        self.plan = SubscriptionPlan.objects.create(
            nome='Plano Premium Anual',
            descricao='Plano completo anual',
            preco=150.00,
            duracao='ANUAL',
            dias_duracao=365,
            ativo=True
        )

    def test_redirecionamento_usuario_nao_autenticado(self):
        """Usuário não logado deve ser redirecionado para o login ao acessar rota premium"""
        response = self.client.get(reverse('investidor_imobiliario'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('account_login') if reverse('account_login') else '/login/')) # Ajustar conforme a URL real

    def test_redirecionamento_usuario_free(self):
        """Usuário autenticado, mas Free (sem assinatura), deve ser redirecionado para o dashboard"""
        self.client.login(username='test_premium', password='testpassword')
        
        response = self.client.get(reverse('investidor_imobiliario'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('dashboard')))

    def test_acesso_usuario_premium_ativo(self):
        """Usuário com assinatura Premium ATIVA deve acessar a rota restrita"""
        self.client.login(username='test_premium', password='testpassword')
        
        # Atribuir assinatura
        Subscription.objects.create(
            usuario=self.user,
            plano=self.plan,
            status='ATIVA',
            data_inicio=timezone.now(),
            data_expiracao=timezone.now() + timedelta(days=365),
            valor_pago=150.00
        )
        
        response = self.client.get(reverse('investidor_imobiliario'))
        self.assertEqual(response.status_code, 200)

    def test_redirecionamento_assinatura_expirada(self):
        """Usuário com assinatura expirada deve ser redirecionado"""
        self.client.login(username='test_premium', password='testpassword')
        
        # Assinatura expirada
        Subscription.objects.create(
            usuario=self.user,
            plano=self.plan,
            status='ATIVA',  # Status pode estar ativa mas data expirou (a verificação lida com isso)
            data_inicio=timezone.now() - timedelta(days=400),
            data_expiracao=timezone.now() - timedelta(days=35),
            valor_pago=150.00
        )
        
        response = self.client.get(reverse('investidor_imobiliario'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('dashboard')))
