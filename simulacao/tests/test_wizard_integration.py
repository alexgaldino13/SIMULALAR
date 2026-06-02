from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal

class WizardIntegrationTest(TestCase):
    """Testes de integração do wizard completo"""
    
    def setUp(self):
        self.client = Client()
        # Wizard V2 uses step as part of the URL /wizard-v2/<step>/
        self.wizard_step_url = lambda s: reverse('wizard_v2_step', kwargs={'step': s})
    
    def test_wizard_flow_complete(self):
        """Testa o fluxo completo do wizard do início ao fim"""
        
        # Step 1: Perfil & Objetivos
        response = self.client.post(self.wizard_step_url(1), {
            'perfil_usuario': 'comprador_morar',
            'prioridade_principal': 'pagar_menos',
            'onde_mora_atualmente': 'aluga',
            'idade_comprador': '30',
            'aluguel_atual': '1500',
            'tempo_mora_atualmente': '1_3'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Trabalho')

        # Step 2: Trabalho & Renda
        response = self.client.post(self.wizard_step_url(2), {
            'tipo_contrato': 'clt',
            'renda_familiar_bruta': '8000',
            'outras_rendas': '1000',
            'renda_estavel': 'estavel',
            'quantos_dependentes': '1'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Finanças')

        # Step 3: Finanças Atuais
        response = self.client.post(self.wizard_step_url(3), {
            'saldo_dinheiro_guardado': '60000',
            'saldo_fgts': '20000',
            'valor_imovel_proprio': '0',
            'despesas_mensais_fixas': '2000'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Imóvel Desejado')

        # Step 4: Imóvel Desejado
        response = self.client.post(self.wizard_step_url(4), {
            'valor_imovel_desejado': '400000',
            'prazo_desejado_anos': '30',
            'cidade': 'São Paulo',
            'custas_documentacao_forma': 'financiado'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cenários')

        # Step 5: Cenários
        response = self.client.post(self.wizard_step_url(5), {
            'comparar_financiamento_sac': 'on',
            'comparar_financiamento_price': 'on',
            'usar_fgts': 'on'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        # Deve chegar na página de resultados
        self.assertContains(response, 'Resultados')
    
    def test_wizard_validation_errors(self):
        """Testa validações de campos obrigatórios"""
        
        # Tentar enviar step 1 sem idade
        response = self.client.post(self.wizard_step_url(1), {
            'perfil_usuario': 'comprador_morar',
            'prioridade_principal': 'pagar_menos',
            'onde_mora_atualmente': 'aluga',
            # 'idade_comprador': missing
            'tempo_mora_atualmente': '1_3'
        })
        
        # Deve retornar erros de validação na página
        self.assertContains(response, 'Este campo é obrigatório')
    
    def test_wizard_back_navigation(self):
        """Testa navegação para trás no wizard"""
        
        # Step 1 -> Step 2
        self.client.post(self.wizard_step_url(1), {
            'perfil_usuario': 'comprador_morar',
            'prioridade_principal': 'pagar_menos',
            'onde_mora_atualmente': 'aluga',
            'idade_comprador': '30',
            'aluguel_atual': '1500',
            'tempo_mora_atualmente': '1_3'
        })
        
        # Acessar Step 1 novamente via GET
        response = self.client.get(self.wizard_step_url(1))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Perfil')
        self.assertContains(response, 'value="30"') # Verifica se manteve dado
    
    def test_wizard_session_persistence(self):
        """Testa se os dados são mantidos na sessão"""
        
        # Enviar dados do step 1
        self.client.post(self.wizard_step_url(1), {
            'perfil_usuario': 'comprador_morar',
            'prioridade_principal': 'pagar_menos',
            'onde_mora_atualmente': 'aluga',
            'idade_comprador': '35',
            'aluguel_atual': '2000',
            'tempo_mora_atualmente': '1_3'
        })
        
        # Verificar dados na sessão
        session = self.client.session
        wizard_data = session.get('wizard_v2_data', {})
        self.assertEqual(wizard_data['perfil_objetivos']['idade_comprador'], 35.0)


class WizardCalculationTest(TestCase):
    """Testes de cálculos do wizard"""
    
    def setUp(self):
        self.client = Client()
        self.wizard_step_url = lambda s: reverse('wizard_v2_step', kwargs={'step': s})

    def test_sac_calculation(self):
        """Testa cálculo SAC via Wizard V2"""
        # Preenche os 5 passos
        self.client.post(self.wizard_step_url(1), {'perfil_usuario': 'comprador_morar', 'prioridade_principal': 'pagar_menos', 'onde_mora_atualmente': 'aluga', 'idade_comprador': '30', 'aluguel_atual': '0', 'tempo_mora_atualmente': '1_3'})
        self.client.post(self.wizard_step_url(2), {'tipo_contrato': 'clt', 'renda_familiar_bruta': '10000', 'outras_rendas': '0', 'renda_estavel': 'estavel', 'quantos_dependentes': '0'})
        self.client.post(self.wizard_step_url(3), {'saldo_dinheiro_guardado': '100000', 'saldo_fgts': '0', 'valor_imovel_proprio': '0', 'despesas_mensais_fixas': '0'})
        self.client.post(self.wizard_step_url(4), {'valor_imovel_desejado': '500000', 'prazo_desejado_anos': '30', 'cidade': 'SP', 'custas_documentacao_forma': 'a_vista'})
        response = self.client.post(self.wizard_step_url(5), {'comparar_financiamento_sac': 'on'}, follow=True)
        
        # Verificar se o cálculo foi realizado
        self.assertContains(response, 'Financiamento SAC')
        self.assertContains(response, 'Parcela Inicial')

    def test_price_calculation(self):
        """Testa cálculo PRICE via Wizard V2"""
        # Preenche os 5 passos
        self.client.post(self.wizard_step_url(1), {'perfil_usuario': 'comprador_morar', 'prioridade_principal': 'pagar_menos', 'onde_mora_atualmente': 'aluga', 'idade_comprador': '30', 'aluguel_atual': '0', 'tempo_mora_atualmente': '1_3'})
        self.client.post(self.wizard_step_url(2), {'tipo_contrato': 'clt', 'renda_familiar_bruta': '10000', 'outras_rendas': '0', 'renda_estavel': 'estavel', 'quantos_dependentes': '0'})
        self.client.post(self.wizard_step_url(3), {'saldo_dinheiro_guardado': '100000', 'saldo_fgts': '0', 'valor_imovel_proprio': '0', 'despesas_mensais_fixas': '0'})
        self.client.post(self.wizard_step_url(4), {'valor_imovel_desejado': '500000', 'prazo_desejado_anos': '30', 'cidade': 'SP', 'custas_documentacao_forma': 'a_vista'})
        response = self.client.post(self.wizard_step_url(5), {'comparar_financiamento_price': 'on'}, follow=True)
        
        # Verificar se o cálculo foi realizado
        self.assertContains(response, 'Financiamento PRICE')
        self.assertContains(response, 'Parcela Inicial')


class WizardUITest(TestCase):
    """Testes de interface do wizard"""
    
    def test_progress_bar(self):
        """Testa se a barra de progresso é exibida"""
        client = Client()
        response = client.get(reverse('wizard_v2_step', kwargs={'step': 1}))
        
        self.assertContains(response, 'progress-bar')
        self.assertContains(response, 'Etapa 1')
    
    def test_responsive_classes(self):
        """Testa se classes responsivas estão presentes"""
        client = Client()
        response = client.get(reverse('wizard_v2_step', kwargs={'step': 1}))
        
        self.assertContains(response, 'wizard-container')
