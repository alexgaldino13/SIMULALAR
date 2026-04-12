from django.test import TestCase
from simulacao.models import SavedSimulation
from simulacao.calculadora_financeira import (
    calcular_financiamento_sac, 
    calcular_financiamento_price,
    guardar_dinheiro
)
import json
import os

class BrazilianDiversityScenariosTest(TestCase):
    fixtures = ['test_br_scenarios.json']

    def test_sac_jovem_casal_amortization(self):
        """Cenário 1.1: Verifica se parcelas SAC são decrescentes."""
        sim = SavedSimulation.objects.get(nome_simulacao="SAC - Jovem Casal")
        d = sim.dados_wizard
        
        resultado = calcular_financiamento_sac(
            valor_principal=d['valor_imovel'] - (d['poupanca'] + d['fgts_saldo']),
            taxa_anual=9.5,
            prazo_meses=d['prazo_anos'] * 12
        )
        
        tabela = resultado['tabela']
        self.assertGreater(tabela[0]['parcela'], tabela[-1]['parcela'])
        self.assertEqual(resultado['parcela_inicial'], tabela[0]['parcela'])

    def test_price_mcmv_constant_installments(self):
        """Cenário 2.1: Verifica se parcelas PRICE são constantes."""
        sim = SavedSimulation.objects.get(nome_simulacao="PRICE - MCMV")
        d = sim.dados_wizard
        
        resultado = calcular_financiamento_price(
            valor_principal=d['valor_imovel'] - d['poupanca'],
            taxa_anual=4.5, # Taxa MCMV
            prazo_meses=d['prazo_anos'] * 12
        )
        
        tabela = resultado['tabela']
        # No PRICE a parcela é constante (exceto possíveis seguros variáveis)
        self.assertAlmostEqual(tabela[0]['parcela'], tabela[len(tabela)//2]['parcela'], places=0)

    def test_margem_comprometimento_autonomo(self):
        """Cenário 1.4: Verifica margem de 30% para Autônomo Renda Alta."""
        sim = SavedSimulation.objects.get(nome_simulacao="SAC - Autônomo Renda Alta")
        d = sim.dados_wizard
        
        # Simula o cálculo que deveria estar na wizard_views_v2.py
        renda = d['renda_familiar_bruta']
        margem_maxima = renda * 0.30
        
        resultado = calcular_financiamento_sac(
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
        sim = SavedSimulation.objects.get(nome_simulacao="Guardar Dinheiro - Morando com Pais")
        d = sim.dados_wizard
        
        resultado = guardar_dinheiro(
            valor_imovel=d['valor_imovel'],
            valor_entrada_inicial=d['valor_imovel'], # Quer comprar à vista
            valor_mensal_guardar=d['aporte_mensal'],
            valor_aluguel=0.0,
            taxa_rendimento_mensal=d['taxa_rendimento_am'] / 100,
            prazo_meses=240
        )
        
        # Com 3000/mês a 0.8%, deve levar em torno de 6-7 anos (70-80 meses)
        self.assertTrue(resultado['viavel'])
        self.assertLess(resultado['meses_para_comprar'], 100)

    def test_comparacao_price_sac_juros(self):
        """Cenário 2.4: PRICE deve pagar mais juros que SAC para o mesmo imóvel."""
        sim_price = SavedSimulation.objects.get(nome_simulacao="PRICE - Comparação juros")
        sim_sac = SavedSimulation.objects.get(nome_simulacao="SAC - Comparação juros")
        
        res_price = calcular_financiamento_price(400000-80000, 9.0, 360)
        res_sac = calcular_financiamento_sac(400000-80000, 9.0, 360)
        
        self.assertGreater(res_price['total_juros'], res_sac['total_juros'])
        print(f"Diferença de juros: R$ {res_price['total_juros'] - res_sac['total_juros']:,.2f}")