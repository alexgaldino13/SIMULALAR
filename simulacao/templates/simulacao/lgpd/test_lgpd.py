from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from simulacao.lgpd_models import ConsentManagement, DataAccessLog, DataDeletionRequest
from simulacao.encryption import encrypt_cpf, decrypt_cpf
import json

User = get_user_model()

class LGPDComplianceTests(TestCase):
    """Testes de conformidade LGPD"""
    
    def setUp(self):
        """Configuração inicial dos testes"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@imobcalc.com',
            password='Test@123456',
            first_name='Test',
            last_name='User'
        )
        self.user.aceitou_termos = True
        self.user.aceitou_privacidade = True
        self.user.save()
    
    def test_consent_required_for_registration(self):
        """Teste: Registro requer consentimento de termos e privacidade"""
        # Tentar registrar sem aceitar termos
        response = self.client.post('/register/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'Test@123456',
            'password2': 'Test@123456',
            'consent_terms': '0',  # Não aceito
            'consent_privacy': '1',
        })
        
        # Deve falhar (assumindo que a view retorna erro ou re-renderiza form com erro)
        # Ajuste conforme a implementação real da view de registro
        self.assertEqual(response.status_code, 200) 
        # Verifica se não criou o usuário
        self.assertFalse(User.objects.filter(username='newuser').exists())
    
    def test_user_can_revoke_consent(self):
        """Teste: Usuário pode revogar consentimento"""
        # Criar consentimento
        consent = ConsentManagement.objects.create(
            user=self.user,
            consent_type='MARKETING',
            granted=True
        )
        
        # Revogar
        self.client.login(username='testuser', password='Test@123456')
        response = self.client.post(f'/revoke-consent/MARKETING/')
        
        # Verificar
        consent.refresh_from_db()
        self.assertFalse(consent.granted)
        self.assertIsNotNone(consent.revoked_at)
    
    def test_data_access_is_logged(self):
        """Teste: Acessos a dados são registrados"""
        # Login
        self.client.login(username='testuser', password='Test@123456')
        
        # Acessar dashboard (que agora tem o decorator @audit_log)
        response = self.client.get('/dashboard/')
        
        # Verificar log
        logs = DataAccessLog.objects.filter(
            user=self.user,
            data_type='DASHBOARD'
        )
        self.assertTrue(logs.exists())
    
    def test_user_can_export_data(self):
        """Teste: Usuário pode exportar seus dados (portabilidade)"""
        # Login
        self.client.login(username='testuser', password='Test@123456')
        
        # Exportar dados
        response = self.client.get('/export-data/')
        
        # Verificar resposta JSON
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('usuario', data)
        self.assertEqual(data['usuario']['email'], 'test@imobcalc.com')
    
    def test_user_can_request_deletion(self):
        """Teste: Usuário pode solicitar exclusão (esquecimento)"""
        # Login
        self.client.login(username='testuser', password='Test@123456')
        
        # Solicitar exclusão
        response = self.client.post('/request-deletion/', {
            'reason': 'Não quero mais usar o serviço'
        })
        
        # Verificar solicitação
        deletion_request = DataDeletionRequest.objects.filter(
            user=self.user,
            status='PENDING'
        )
        self.assertTrue(deletion_request.exists())
    
    def test_sensitive_data_is_encrypted(self):
        """Teste: Dados sensíveis são criptografados"""
        # CPF original
        cpf_original = '123.456.789-00'
        
        # Criptografar
        cpf_encrypted = encrypt_cpf(cpf_original)
        
        # Verificar que está criptografado (não é igual ao original)
        self.assertNotEqual(cpf_encrypted, cpf_original)
        self.assertNotEqual(cpf_encrypted, '12345678900')
        
        # Descriptografar
        cpf_decrypted = decrypt_cpf(cpf_encrypted, formatted=True)
        
        # Verificar que volta ao original
        self.assertEqual(cpf_decrypted, cpf_original)