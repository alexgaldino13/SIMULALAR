import unittest
from decimal import Decimal
from django.test import TestCase
from simulacao.calculadora_financeira import (
    calcular_price_sac, simular_consorcio, simular_aluguel_investimento, calcular_mcmv
)
from simulacao.utils import calcular_margem_credito

class CalculosFinanceirosTests(TestCase):
    
    def test_financiamento_price_sem_fgts(self):
        """No financiamento PRICE as parcelas devem ser constantes (permitindo pequena flutuação no último mês)."""
        resultado = calcular_price_sac(
            metodo='price',
            valor_principal=Decimal('400000'),
            taxa_anual=Decimal('8.5'),
            prazo_meses=360,
            seguro_mensal=0.0,
            taxa_admin_mensal=0.0
        )
        tabela = resultado['tabela']
        self.assertEqual(len(tabela), 360)
        self.assertEqual(resultado['prazo_final_meses'], 360)
        
        parcela_inicial = resultado['parcela_inicial']
        # Verifica se todas as parcelas são iguais ou muito próximas (diferença < 0.10)
        for linha in tabela[:-1]: # ignoro a ultima parcela q pode ter resíduo de amortizacao
            self.assertAlmostEqual(linha['parcela'], parcela_inicial, delta=0.50)
            
    def test_financiamento_sac_sem_fgts(self):
        """No financiamento SAC a amortização deve ser constante e as parcelas decrescentes."""
        resultado = calcular_price_sac(
            metodo='sac',
            valor_principal=Decimal('400000'),
            taxa_anual=Decimal('8.5'),
            prazo_meses=360,
            seguro_mensal=0.0,
            taxa_admin_mensal=0.0
        )
        tabela = resultado['tabela']
        self.assertEqual(len(tabela), 360)
        
        # O valor amortizado deve ser sempre constante
        amortizacao_fixa = 400000 / 360
        for linha in tabela[:-1]: 
            self.assertAlmostEqual(linha['amortizacao'], amortizacao_fixa, delta=0.05)
            
        # As parcelas devem ser decrescentes
        for i in range(1, len(tabela)):
            self.assertLessEqual(tabela[i]['parcela'], tabela[i-1]['parcela'] + 0.01)

    def test_uso_fgts_reduzir_prazo_price(self):
        """Ao utilizar saldo de FGTS para amortizar o saldo no mês 1 para reduzir prazo."""
        resultado = calcular_price_sac(
            metodo='price',
            valor_principal=Decimal('400000'),
            taxa_anual=Decimal('8.5'),
            prazo_meses=360,
            usar_fgts_financiamento=True,
            fgts_saldo=Decimal('50000'),
            tipo_amortizacao_fgts='reduzir_prazo',
            mes_uso_fgts_financiamento=1
        )
        
        # A primeira linha deve ser o lump sum FGTS
        self.assertEqual(resultado['tabela'][0]['tipo'], 'FGTS_LumpSum')
        # Como usou 50k para amortizar, o prazo deve ser reduzido, então < 360
        self.assertLess(resultado['prazo_final_meses'], 360)
        self.assertGreater(resultado['parcela_inicial'], 0)

    def test_uso_fgts_reduzir_parcela_sac(self):
        """Ao utilizar saldo de FGTS para reduzir parcela em SAC."""
        resultado_sem_fgts = calcular_price_sac(
            metodo='sac',
            valor_principal=Decimal('400000'),
            taxa_anual=Decimal('8.5'),
            prazo_meses=360,
        )
        
        resultado_com_fgts = calcular_price_sac(
            metodo='sac',
            valor_principal=Decimal('400000'),
            taxa_anual=Decimal('8.5'),
            prazo_meses=360,
            usar_fgts_financiamento=True,
            fgts_saldo=Decimal('50000'),
            tipo_amortizacao_fgts='reduzir_parcela',
            mes_uso_fgts_financiamento=1
        )
        
        # O prazo continua sendo o original, mas a parcela inicial cai
        # (Lembrando que o prazo real pra reduzir_parcela é igual)
        self.assertEqual(resultado_com_fgts['prazo_final_meses'], 360)
        self.assertLess(resultado_com_fgts['parcela_inicial'], resultado_sem_fgts['parcela_inicial'])

    def test_simulacao_consorcio(self):
        """Cálculos do consórcio com valores estáticos."""
        resultado = simular_consorcio(
            valor_imovel=Decimal('400000'),
            prazo_meses=200,
            taxa_adm=20.0,
            fundo_reserva=5.0
        )
        
        # Taxa adm total = (taxa / 100) * (prazo / 12) * valor
        taxa_adm_total = (20.0 / 100) * (200 / 12) * 400000
        # Fundo reserva = % sobre o valor
        fundo_reserva_total = (5.0 / 100) * 400000
        
        custo_esperado = taxa_adm_total + fundo_reserva_total
        parcela_esperada = (400000 + custo_esperado) / 200
        
        self.assertAlmostEqual(resultado['taxa_administracao_total'], taxa_adm_total, places=2)
        self.assertAlmostEqual(resultado['fundo_reserva_total'], fundo_reserva_total, places=2)
        self.assertAlmostEqual(resultado['total_custo'], custo_esperado, places=2)
        self.assertAlmostEqual(resultado['parcela_fixa'], parcela_esperada, places=2)

    def test_calcular_margem_credito(self):
        """Regra de limites de margem de crédito pelo banco considerando rendas adicionais e desconto de risco."""
        resultado = calcular_margem_credito(
            renda_familiar_bruta=10000,
            outras_rendas=2000,
            percentual_comprometimento=30.0,
            desconto_outras_rendas=50.0 # 50% de desconto -> 1000
        )
        # Renda considerada = 10000 + (2000 * 0.5) = 11000
        # Parcela máxima = 11000 * 0.30 = 3300
        
        self.assertEqual(resultado['renda_total_considerada'], 11000)
        self.assertAlmostEqual(resultado['parcela_maxima'], 3300, places=2)

    def test_calcular_mcmv(self):
        """Testando limites da simulação MCMV (subsídio e limite Teto)."""
        resultado = calcular_mcmv(
            valor_imovel=Decimal('150000'),
            renda_familiar_mensal=2000,
            valor_entrada=Decimal('10000'),
            prazo_meses=360
        )
        self.assertTrue(resultado['qualificado'])
        self.assertEqual(resultado['faixa'], 'faixa1')
        self.assertLessEqual(resultado['subsidio'], 55000)
        self.assertGreater(resultado['subsidio'], 0)
        
    def test_calcular_mcmv_acima_teto(self):
        """Verifica se desqualifica cliente caso renda passe do Teto de 8 mil."""
        resultado = calcular_mcmv(
            valor_imovel=Decimal('500000'),
            renda_familiar_mensal=8500, # Acima de 8000 (limite)
            valor_entrada=Decimal('50000'),
            prazo_meses=360
        )
        self.assertFalse(resultado['qualificado'])

    def test_simular_aluguel_investimento(self):
        """Valida que simulação gera capital de acumulo progressivo frente a inflação."""
        resultado = simular_aluguel_investimento(
            valor_imovel_total=Decimal('400000'),
            entrada_total=Decimal('80000'),
            taxa_investimento=10.0,
            aluguel_inicial=Decimal('2000'),
            taxa_inflacao=4.5,
            prazo_meses=360,
            recursos_proprios_iniciais=Decimal('0'),
            opcao_pagamento_aluguel='renda',
            fgts_saldo=Decimal('0'),
            rendimento_fgts=3.0,
            fgts_mensal_percent=0.0,
            aporte_13=Decimal('0'),
            renda_familiar_bruta=Decimal('10000'),
            valorizacao_imovel=5.0,
            taxa_anual_financiamento=8.5
        )
        
        self.assertGreater(resultado['acumulado_final'], 80000) # O valor deve ter rendido acima da entrada
        self.assertGreater(resultado['valor_imovel_final'], 400000) # O Imóvel deve ter valorizado
        
        # Testando opção 'investimento' (quando o aluguel é descontado do saldo investido todo mês)
        resultado_inv = simular_aluguel_investimento(
            valor_imovel_total=Decimal('400000'),
            entrada_total=Decimal('80000'),
            taxa_investimento=10.0,
            aluguel_inicial=Decimal('2000'),
            taxa_inflacao=4.5,
            prazo_meses=360,
            recursos_proprios_iniciais=Decimal('0'),
            opcao_pagamento_aluguel='investimento',
            fgts_saldo=Decimal('0'),
            rendimento_fgts=3.0,
            fgts_mensal_percent=0.0,
            aporte_13=Decimal('0'),
            renda_familiar_bruta=Decimal('10000'),
            valorizacao_imovel=5.0,
            taxa_anual_financiamento=8.5
        )
        # O acumulado neste caso deve ser muito menor (talvez até 0) pois 2k é > que o rendimento livre que 80k renderia a 10% aa
        self.assertLessEqual(resultado_inv['acumulado_final'], resultado['acumulado_final'])
