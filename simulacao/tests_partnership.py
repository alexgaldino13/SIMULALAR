# simulacao/tests_partnership.py
"""
Testes para o Sistema de Parcerias
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import json

from .partnership_models import Partnership, Lead
from .conversion_tracking import ConversionEvent, LeadAlert

User = get_user_model()


class PartnershipModelTest(TestCase):
    """Testes para o model Partnership."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        
        self.parceiro = Partnership.objects.create(
            nome='Consórcio Teste',
            cnpj='12.345.678/0001-90',
            tipo='CONSORCIO',
            status='ATIVO',
            email_contato='contato@consorcio.com',
            telefone='11999999999',
            valor_por_lead=Decimal('50.00'),
            comissao_conversao=Decimal('2.5'),
            valor_minimo_imovel=Decimal('200000.00'),
            valor_maximo_imovel=Decimal('500000.00'),
            estados_atendidos=['SP', 'RJ', 'MG'],
            criado_por=self.user
        )
    
    def test_criacao_parceiro(self):
        """Testa criação de parceiro."""
        self.assertEqual(self.parceiro.nome, 'Consórcio Teste')
        self.assertEqual(self.parceiro.tipo, 'CONSORCIO')
        self.assertEqual(self.parceiro.status, 'ATIVO')
        self.assertIsNotNone(self.parceiro.api_key)
    
    def test_pode_receber_lead_valor_valido(self):
        """Testa se parceiro pode receber lead com valor válido."""
        pode = self.parceiro.pode_receber_lead(
            valor_imovel=Decimal('300000.00'),
            estado='SP'
        )
        self.assertTrue(pode)
    
    def test_pode_receber_lead_valor_baixo(self):
        """Testa se parceiro rejeita lead com valor muito baixo."""
        pode = self.parceiro.pode_receber_lead(
            valor_imovel=Decimal('100000.00'),
            estado='SP'
        )
        self.assertFalse(pode)
    
    def test_pode_receber_lead_valor_alto(self):
        """Testa se parceiro rejeita lead com valor muito alto."""
        pode = self.parceiro.pode_receber_lead(
            valor_imovel=Decimal('600000.00'),
            estado='SP'
        )
        self.assertFalse(pode)
    
    def test_pode_receber_lead_estado_invalido(self):
        """Testa se parceiro rejeita lead de estado não atendido."""
        pode = self.parceiro.pode_receber_lead(
            valor_imovel=Decimal('300000.00'),
            estado='BA'
        )
        self.assertFalse(pode)
    
    def test_pode_receber_lead_parceiro_inativo(self):
        """Testa se parceiro inativo não pode receber leads."""
        self.parceiro.status = 'INATIVO'
        self.parceiro.save()
        
        pode = self.parceiro.pode_receber_lead(
            valor_imovel=Decimal('300000.00'),
            estado='SP'
        )
        self.assertFalse(pode)
    
    def test_atualizar_estatisticas(self):
        """Testa atualização de estatísticas do parceiro."""
        # Cria alguns leads
        for i in range(5):
            Lead.objects.create(
                usuario=self.user,
                parceiro=self.parceiro,
                nome_completo=f'Lead {i}',
                email=f'lead{i}@test.com',
                telefone='11999999999',
                valor_imovel=Decimal('300000.00'),
                status='CONVERTIDO' if i < 2 else 'NOVO'
            )
        
        self.parceiro.atualizar_estatisticas()
        
        self.assertEqual(self.parceiro.total_leads_recebidos, 5)
        self.assertEqual(self.parceiro.total_leads_convertidos, 2)
        self.assertEqual(self.parceiro.taxa_conversao, 40.0)


class LeadModelTest(TestCase):
    """Testes para o model Lead."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='testpass123'
        )
        
        self.parceiro = Partnership.objects.create(
            nome='Corretora Teste',
            cnpj='98.765.432/0001-10',
            tipo='CORRETORA',
            status='ATIVO',
            email_contato='contato@corretora.com',
            telefone='11888888888',
            comissao_conversao=Decimal('3.0'),
            criado_por=self.user
        )
        
        self.lead = Lead.objects.create(
            usuario=self.user,
            parceiro=self.parceiro,
            nome_completo='João Silva',
            email='joao@test.com',
            telefone='11777777777',
            valor_imovel=Decimal('350000.00'),
            valor_entrada=Decimal('70000.00'),
            cidade_interesse='São Paulo',
            estado_interesse='SP',
            renda_mensal=Decimal('8000.00')
        )
    
    def test_criacao_lead(self):
        """Testa criação de lead."""
        self.assertEqual(self.lead.nome_completo, 'João Silva')
        self.assertEqual(self.lead.status, 'NOVO')
        self.assertEqual(self.lead.parceiro, self.parceiro)
    
    def test_marcar_como_enviado(self):
        """Testa marcação de lead como enviado."""
        self.assertIsNone(self.lead.enviado_em)
        
        self.lead.marcar_como_enviado()
        
        self.assertEqual(self.lead.status, 'ENVIADO')
        self.assertIsNotNone(self.lead.enviado_em)
    
    def test_marcar_como_convertido(self):
        """Testa marcação de lead como convertido."""
        valor_negocio = Decimal('350000.00')
        
        self.lead.marcar_como_convertido(valor_negocio)
        
        self.assertEqual(self.lead.status, 'CONVERTIDO')
        self.assertEqual(self.lead.valor_negocio, valor_negocio)
        self.assertIsNotNone(self.lead.convertido_em)
        
        # Verifica cálculo de comissão (3% de 350.000 = 10.500)
        self.assertEqual(self.lead.comissao_gerada, Decimal('10500.00'))
    
    def test_tempo_ate_conversao(self):
        """Testa cálculo de tempo até conversão."""
        # Lead recém criado não tem tempo de conversão
        self.assertIsNone(self.lead.tempo_ate_conversao())
        
        # Marca como convertido
        self.lead.marcar_como_convertido(Decimal('350000.00'))
        
        # Deve ter tempo de conversão (0 dias pois foi imediato)
        tempo = self.lead.tempo_ate_conversao()
        self.assertIsNotNone(tempo)
        self.assertEqual(tempo, 0)


class PartnershipAPITest(TestCase):
    """Testes para a API de Parcerias."""
    
    def setUp(self):
        self.client = Client()
        
        self.user = User.objects.create_user(
            username='parceiro',
            email='parceiro@test.com',
            password='testpass123'
        )
        
        self.parceiro = Partnership.objects.create(
            nome='Banco Teste',
            cnpj='11.222.333/0001-44',
            tipo='BANCO',
            status='ATIVO',
            email_contato='contato@banco.com',
            telefone='11666666666',
            criado_por=self.user
        )
        
        # Cria alguns leads
        for i in range(3):
            Lead.objects.create(
                usuario=self.user,
                parceiro=self.parceiro,
                nome_completo=f'Lead API {i}',
                email=f'leadapi{i}@test.com',
                telefone='11555555555',
                valor_imovel=Decimal('400000.00'),
                status='NOVO'
            )
    
    def test_health_check(self):
        """Testa endpoint de health check."""
        response = self.client.get('/api/v1/partnerships/health/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'ok')
    
    def test_listar_leads_sem_autenticacao(self):
        """Testa listagem de leads sem autenticação."""
        response = self.client.get('/api/v1/partnerships/leads/')
        
        # Deve retornar 401 Unauthorized
        self.assertEqual(response.status_code, 401)
    
    def test_listar_leads_com_autenticacao(self):
        """Testa listagem de leads com autenticação."""
        response = self.client.get(
            '/api/v1/partnerships/leads/',
            HTTP_AUTHORIZATION=f'Api-Key {self.parceiro.api_key}'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 3)
    
    def test_atualizar_status_lead(self):
        """Testa atualização de status de lead."""
        lead = Lead.objects.filter(parceiro=self.parceiro).first()
        
        response = self.client.post(
            f'/api/v1/partnerships/leads/{lead.id}/update_status/',
            data=json.dumps({'status': 'QUALIFICADO'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Api-Key {self.parceiro.api_key}'
        )
        
        self.assertEqual(response.status_code, 200)
        
        lead.refresh_from_db()
        self.assertEqual(lead.status, 'QUALIFICADO')


class ConversionTrackingTest(TestCase):
    """Testes para o sistema de tracking de conversão."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='tracker',
            email='tracker@test.com',
            password='testpass123'
        )
        
        self.parceiro = Partnership.objects.create(
            nome='Construtora Teste',
            cnpj='55.666.777/0001-88',
            tipo='CONSTRUTORA',
            status='ATIVO',
            email_contato='contato@construtora.com',
            telefone='11444444444',
            criado_por=self.user
        )
        
        self.lead = Lead.objects.create(
            usuario=self.user,
            parceiro=self.parceiro,
            nome_completo='Maria Santos',
            email='maria@test.com',
            telefone='11333333333',
            valor_imovel=Decimal('450000.00')
        )
    
    def test_registrar_evento(self):
        """Testa registro de evento de conversão."""
        evento = ConversionEvent.registrar_evento(
            lead=self.lead,
            tipo_evento='PRIMEIRO_CONTATO',
            descricao='Contato realizado por telefone',
            usuario=self.user
        )
        
        self.assertIsNotNone(evento)
        self.assertEqual(evento.tipo_evento, 'PRIMEIRO_CONTATO')
        self.assertEqual(evento.lead, self.lead)
        self.assertEqual(evento.parceiro, self.parceiro)
    
    def test_criar_alerta_lead_parado(self):
        """Testa criação de alerta para lead parado."""
        alerta = LeadAlert.objects.create(
            lead=self.lead,
            parceiro=self.parceiro,
            tipo_alerta='LEAD_PARADO',
            prioridade='ALTA',
            mensagem='Lead sem atividade há 5 dias',
            dias_sem_atividade=5
        )
        
        self.assertEqual(alerta.status, 'ATIVO')
        self.assertEqual(alerta.prioridade, 'ALTA')
        self.assertFalse(alerta.notificacao_enviada)
    
    def test_marcar_alerta_como_resolvido(self):
        """Testa marcação de alerta como resolvido."""
        alerta = LeadAlert.objects.create(
            lead=self.lead,
            parceiro=self.parceiro,
            tipo_alerta='SEM_CONTATO',
            prioridade='URGENTE',
            mensagem='Lead sem contato inicial'
        )
        
        alerta.marcar_como_resolvido(
            usuario=self.user,
            observacoes='Contato realizado com sucesso'
        )
        
        self.assertEqual(alerta.status, 'RESOLVIDO')
        self.assertEqual(alerta.resolvido_por, self.user)
        self.assertIsNotNone(alerta.resolvido_em)


class PartnershipReportsTest(TestCase):
    """Testes para o sistema de relatórios."""
    
    def setUp(self):
        from .partnership_reports import PartnershipReportGenerator
        
        self.user = User.objects.create_user(
            username='reporter',
            email='reporter@test.com',
            password='testpass123'
        )
        
        self.parceiro = Partnership.objects.create(
            nome='Parceiro Relatório',
            cnpj='99.888.777/0001-66',
            tipo='CONSORCIO',
            status='ATIVO',
            email_contato='contato@relatorio.com',
            telefone='11222222222',
            valor_por_lead=Decimal('30.00'),
            comissao_conversao=Decimal('2.0'),
            criado_por=self.user
        )
        
        # Cria leads variados
        for i in range(10):
            status = 'CONVERTIDO' if i < 3 else ('PERDIDO' if i < 5 else 'NOVO')
            lead = Lead.objects.create(
                usuario=self.user,
                parceiro=self.parceiro,
                nome_completo=f'Lead Report {i}',
                email=f'report{i}@test.com',
                telefone='11111111111',
                valor_imovel=Decimal('300000.00'),
                status=status
            )
            
            if status == 'CONVERTIDO':
                lead.valor_negocio = Decimal('300000.00')
                lead.comissao_gerada = Decimal('6000.00')
                lead.convertido_em = timezone.now()
                lead.save()
        
        self.generator = PartnershipReportGenerator(parceiro=self.parceiro)
    
    def test_metricas_gerais(self):
        """Testa geração de métricas gerais."""
        metricas = self.generator.get_metricas_gerais()
        
        self.assertEqual(metricas['total_leads'], 10)
        self.assertEqual(metricas['leads_convertidos'], 3)
        self.assertEqual(metricas['leads_perdidos'], 2)
        self.assertEqual(metricas['taxa_conversao'], 30.0)
    
    def test_funil_conversao(self):
        """Testa geração de funil de conversão."""
        funil = self.generator.get_funil_conversao()
        
        self.assertEqual(funil['total_leads'], 10)
        self.assertEqual(funil['convertidos'], 3)
        self.assertIn('taxa_conversao_final', funil)
    
    def test_roi_parceiro(self):
        """Testa cálculo de ROI."""
        roi = self.generator.get_roi_parceiro()
        
        self.assertIsNotNone(roi)
        self.assertIn('custo_total', roi)
        self.assertIn('receita_total', roi)
        self.assertIn('roi_percentual', roi)
        
        # Custo: 10 leads * R$ 30 = R$ 300
        self.assertEqual(roi['custo_total'], 300.0)
        
        # Receita: 3 conversões * R$ 6.000 = R$ 18.000
        self.assertEqual(roi['receita_total'], 18000.0)
    
    def test_exportar_csv(self):
        """Testa exportação em CSV."""
        csv_content = self.generator.exportar_csv()
        
        self.assertIsNotNone(csv_content)
        self.assertIn('Nome', csv_content)
        self.assertIn('Email', csv_content)
        self.assertIn('Lead Report', csv_content)
    
    def test_gerar_relatorio_completo(self):
        """Testa geração de relatório completo."""
        relatorio = self.generator.gerar_relatorio_completo()
        
        self.assertIn('periodo', relatorio)
        self.assertIn('metricas_gerais', relatorio)
        self.assertIn('funil_conversao', relatorio)
        self.assertIn('roi', relatorio)
        self.assertIn('evolucao_mensal', relatorio)
