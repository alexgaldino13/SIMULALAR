# simulacao/tests/test_simulation_history_api.py
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from simulacao.models import SavedSimulation, UserProfile

User = get_user_model()

class SimulationHistoryAPITestCase(APITestCase):
    """
    Testes para as APIs de histórico de simulação e dashboard.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='history_tester',
            email='tester@imobcalc.com',
            password='password123',
            first_name='Tester'
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Dados fake de simulação
        self.fake_wizard_data = {
            "perfil_objetivos": {"perfil": "comprador_morar", "prioridade": "equilibrio"},
            "trabalho_renda": {"renda_familiar_bruta": 10000, "tipo_contrato": "clt"},
            "financas_atuais": {"saldo_dinheiro_guardado": 50000},
            "imovel_desejado": {"valor_imovel_desejado": 300000, "prazo_desejado_anos": 30}
        }
        self.fake_results = {
            "valor_imovel": 300000,
            "analise": {"texto_principal": "Cenário ideal encontrado"},
            "resultados": {
                "sac": {"metodo": "SAC", "parcela_inicial": 2500, "total_custo": 550000},
                "price": {"metodo": "PRICE", "parcela_inicial": 2200, "total_custo": 580000}
            }
        }

    def test_save_simulation_success(self):
        """
        Testa o salvamento de uma nova simulação.
        """
        url = reverse('api_simulation_save')
        data = {
            'titulo': 'Meu Novo Apartamento',
            'dados_wizard': self.fake_wizard_data,
            'resultados': self.fake_results
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SavedSimulation.objects.filter(user=self.user).count(), 1)
        self.assertEqual(SavedSimulation.objects.first().titulo, 'Meu Novo Apartamento')

    def test_save_simulation_missing_data(self):
        """
        Testa erro ao tentar salvar sem dados obrigatórios.
        """
        url = reverse('api_simulation_save')
        data = {'titulo': 'Incompleta'} # Faltam dados_wizard e resultados
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_get_dashboard_data(self):
        """
        Testa a recuperação de dados do dashboard, incluindo perfil e simulações recentes.
        """
        # Cria 3 simulações prévias
        for i in range(3):
            SavedSimulation.objects.create(
                user=self.user,
                titulo=f'Simulação {i}',
                dados_wizard=self.fake_wizard_data,
                resultados=self.fake_results
            )

        url = reverse('api_dashboard')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('profile', response.data)
        self.assertIn('recent_simulations', response.data)
        self.assertEqual(len(response.data['recent_simulations']), 3)
        self.assertEqual(response.data['total_simulations'], 3)
        self.assertEqual(response.data['profile']['first_name'], 'Tester')

    def test_delete_simulation_success(self):
        """
        Testa a exclusão de uma simulação própria.
        """
        sim = SavedSimulation.objects.create(
            user=self.user,
            titulo='Excluir',
            dados_wizard=self.fake_wizard_data,
            resultados=self.fake_results
        )
        url = reverse('api_simulation_delete', kwargs={'pk': sim.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SavedSimulation.objects.count(), 0)
    def test_get_all_simulations(self):
        """
        Testa a recuperação da lista completa de simulações.
        """
        # Cria 10 simulações
        for i in range(10):
            SavedSimulation.objects.create(
                user=self.user,
                titulo=f'Sim {i}',
                dados_wizard=self.fake_wizard_data,
                resultados=self.fake_results
            )

        url = reverse('api_simulation_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('simulations', response.data)
        self.assertEqual(len(response.data['simulations']), 10)

    def test_delete_simulation_unauthorized(self):
        """
        Testa que um usuário não pode excluir a simulação de outro.
        """
        other_user = User.objects.create_user(username='other', email='other@test.com', password='pwd')
        sim_other = SavedSimulation.objects.create(
            user=other_user,
            titulo='Sim Outro',
            dados_wizard=self.fake_wizard_data,
            resultados=self.fake_results
        )
        
        url = reverse('api_simulation_delete', kwargs={'pk': sim_other.id})
        response = self.client.delete(url)
        
        # Como o history_tester está logado, ele deve receber 404 ao tentar acessar sim_other
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(SavedSimulation.objects.count(), 1)
