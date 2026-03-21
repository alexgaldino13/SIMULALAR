from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal

class WizardIntegrationTest(TestCase):
    """Testes de integração do wizard completo"""
    
    def setUp(self):
        self.client = Client()
        self.wizard_url = reverse('wizard_v2')
    
    def test_wizard_flow_complete(self):
        """Testa o fluxo completo do wizard do início ao fim"""
        
        # Step 1: Perfil do usuário
        response = self.client.post(self.wizard_url, {
            'wizard_v2-current_step': '0',
            '0-idade': '30',
            '0-renda_mensal': '5000',
            '0-tem_fgts': 'sim',
            '0-valor_fgts': '20000',
        })
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Características do imóvel
        response = self.client.post(self.wizard_url, {
            'wizard_v2-current_step': '1',
            '1-valor_imovel': '300000',
            '1-valor_entrada': '60000',
            '1-cidade': 'São Paulo',
            '1-tipo_imovel': 'apartamento',
        })
        self.assertEqual(response.status_code, 200)
        
        # Step 3: Condições de financiamento
        response = self.client.post(self.wizard_url, {
            'wizard_v2-current_step': '2',
            '2-prazo_anos': '20',
            '2-sistema_amortizacao': 'SAC',
            '2-taxa_juros': '9.5',
        })
        self.assertEqual(response.status_code, 200)
        
        # Step 4: Custos adicionais
        response = self.client.post(self.wizard_url, {
            'wizard_v2-current_step': '3',
            '3-itbi': '2',
            '3-registro': '1500',
            '3-avaliacao': '800',
        })
        self.assertEqual(response.status_code, 200)
        
        # Verificar se chegou ao resultado final
        self.assertContains(response, 'Resultado da Simulação')
    
    def test_wizard_validation_errors(self):
        """Testa validações de campos obrigatórios"""
        
        # Tentar enviar step 1 sem dados
        response = self.client.post(self.wizard_url, {
            'wizard_v2-current_step': '0',
        })
        
        # Deve retornar erros de validação
        self.assertFormError(response, 'form', 'idade', 'Este campo é obrigatório.')
    
    def test_wizard_back_navigation(self):
        """Testa navegação para trás no wizard"""
        
        # Avançar para step 2
        self.client.post(self.wizard_url, {
            'wizard_v2-current_step': '0',
            '0-idade': '30',
            '0-renda_mensal': '5000',
        })
        
        # Voltar para step 1
        response = self.client.post(self.wizard_url, {
            'wizard_v2-current_step': '1',
            'wizard_goto_step': '0',
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Perfil do Usuário')
    
    def test_wizard_session_persistence(self):
        """Testa se os dados são mantidos na sessão"""
        
        # Enviar dados do step 1
        self.client.post(self.wizard_url, {
            'wizard_v2-current_step': '0',
            '0-idade': '35',
            '0-renda_mensal': '8000',
        })
        
        # Voltar e verificar se dados foram mantidos
        response = self.client.get(self.wizard_url)
        self.assertContains(response, '35')  # Idade deve estar preenchida


class WizardCalculationTest(TestCase):
    """Testes de cálculos do wizard"""
    
    def test_sac_calculation(self):
        """Testa cálculo SAC"""
        client = Client()
        
        response = client.post(reverse('wizard_v2'), {
            'wizard_v2-current_step': '0',
            '0-idade': '30',
            '0-renda_mensal': '5000',
            '0-tem_fgts': 'nao',
            '0-valor_fgts': '0',
        })
        
        response = client.post(reverse('wizard_v2'), {
            'wizard_v2-current_step': '1',
            '1-valor_imovel': '200000',
            '1-valor_entrada': '40000',
            '1-cidade': 'São Paulo',
            '1-tipo_imovel': 'apartamento',
        })
        
        response = client.post(reverse('wizard_v2'), {
            'wizard_v2-current_step': '2',
            '2-prazo_anos': '15',
            '2-sistema_amortizacao': 'SAC',
            '2-taxa_juros': '10',
        })
        
        # Verificar se o cálculo foi realizado
        self.assertContains(response, 'Parcela Inicial')
        self.assertContains(response, 'Parcela Final')
    
    def test_price_calculation(self):
        """Testa cálculo PRICE"""
        client = Client()
        
        # Similar ao teste SAC, mas com sistema PRICE
        # ... (implementar fluxo completo)
        pass


class WizardUITest(TestCase):
    """Testes de interface do wizard"""
    
    def test_progress_bar(self):
        """Testa se a barra de progresso é exibida"""
        client = Client()
        response = client.get(reverse('wizard_v2'))
        
        self.assertContains(response, 'progress-bar')
        self.assertContains(response, 'Step 1')
    
    def test_responsive_classes(self):
        """Testa se classes responsivas estão presentes"""
        client = Client()
        response = client.get(reverse('wizard_v2'))
        
        self.assertContains(response, 'wizard-container')
        self.assertContains(response, 'wizard-responsive')
