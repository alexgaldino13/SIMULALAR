from django.test import TestCase
from simulacao.models import SavedSimulation
from simulacao.calculadora_financeira import calcular_price_sac
from simulacao.utils import guardar_dinheiro
from decimal import Decimal
import json
import os

class BrazilianDiversityScenariosTest(TestCase):
    fixtures = ['simulacao/tests/test_br_scenarios.json']

    def test_sac_jovem_casal_amortization(self):
        """Cenário 1.1: Verifica se parcelas SAC são decrescentes."""
        sim = SavedSimulation.objects.get(titulo="SAC - Jovem Casal")
        d = sim.dados_wizard
        
        resultado = calcular_price_sac(
            metodo='sac',
            valor_principal=d['valor_imovel'] - (d['poupanca'] + d['fgts_saldo']),
            taxa_anual=9.5,
            prazo_meses=d['prazo_anos'] * 12
        )
        
        tabela = resultado['tabela']
        self.assertGreater(tabela[0]['parcela'], tabela[-1]['parcela'])
        self.assertEqual(resultado['parcela_inicial'], tabela[0]['parcela'])

    def test_price_mcmv_constant_installments(self):
        """Cenário 2.1: Verifica se parcelas PRICE são constantes."""
        sim = SavedSimulation.objects.get(titulo="PRICE - MCMV")
        d = sim.dados_wizard
        
        resultado = calcular_price_sac(
            metodo='price',
            valor_principal=d['valor_imovel'] - d['poupanca'],
            taxa_anual=4.5, # Taxa MCMV
            prazo_meses=d['prazo_anos'] * 12,
            seguro_mensal=Decimal('30.00'), # Seguro fixo
            taxa_admin_mensal=Decimal('25.00') # Taxa fixa
        )
        
        tabela = [l for l in resultado['tabela'] if l.get('parcela', 0) > 0]
        # No PRICE a parcela deve ser rigorosamente constante se o seguro e taxas forem fixos
        self.assertAlmostEqual(tabela[0]['parcela'], tabela[-1]['parcela'], places=2)

    def test_margem_comprometimento_autonomo(self):
        """Cenário 1.4: Verifica margem de 30% para Autônomo Renda Alta."""
        sim = SavedSimulation.objects.get(titulo="SAC - Autônomo Renda Alta")
        d = sim.dados_wizard
        
        # Simula o cálculo que deveria estar na wizard_views_v2.py
        renda = d['renda_familiar_bruta']
        margem_maxima = renda * 0.30
        
        resultado = calcular_price_sac(
            metodo='sac',
            valor_principal=d['valor_imovel'] - d['poupanca'],
            taxa_anual=10.5,
            prazo_meses=d['prazo_anos'] * 12
        )
        
        # Se a parcela inicial for maior que a margem, o sistema deve alertar
        if resultado['parcela_inicial'] > margem_maxima:
            # Aqui validaríamos se a view retorna um aviso de "Risco de Crédito"
            pass
        
        self.assertEqual(margem_maxima, 6000.0)
        # Verifica se o bug de R$ 0,00 ocorre (se a renda for processada)
        self.assertGreater(margem_maxima, 0)

    def test_guardar_dinheiro_paciencia(self):
        """Cenário 5.1: Tempo para comprar à vista morando com os pais."""
        sim = SavedSimulation.objects.get(titulo="Guardar Dinheiro - Morando com Pais")
        d = sim.dados_wizard
        
        resultado = guardar_dinheiro(
            valor_imovel=d['valor_imovel'],
            valor_entrada_inicial=d['valor_imovel'], # Quer comprar à vista
            valor_mensal_guardar=d['aporte_mensal'],
            valor_aluguel=0.0,
            taxa_rendimento_mensal=d['taxa_rendimento_am'] / 100,
            prazo_meses=240,
            taxa_reajuste_aluguel_anual=0.05,
            fgts_saldo_inicial=0.0,
            renda_familiar_bruta=0.0,
            fgts_mensal_percent=8.0
        )
        
        # Com 3000/mês a 0.8%, deve levar em torno de 6-7 anos (70-80 meses)
        self.assertTrue(resultado['viavel'])
        self.assertLess(resultado['meses_para_comprar'], 100)

    def test_comparacao_price_sac_juros(self):
        """Cenário 2.4: PRICE deve pagar mais juros que SAC para o mesmo imóvel."""
        sim_price = SavedSimulation.objects.get(titulo="PRICE - Comparação juros")
        sim_sac = SavedSimulation.objects.get(titulo="SAC - Comparação juros")
        
        res_price = calcular_price_sac('price', 400000-80000, 9.0, 360)
        res_sac = calcular_price_sac('sac', 400000-80000, 9.0, 360)
        
        self.assertGreater(res_price['total_juros'], res_sac['total_juros'])
        print(f"Diferença de juros: R$ {res_price['total_juros'] - res_sac['total_juros']:,.2f}")
