from django.test import TestCase
from django.test import SimpleTestCase
from decimal import Decimal

from simulacao.calculadora_financeira import simular_consorcio, simular_aluguel_investimento

class CalculadoraFinanceiraTests(SimpleTestCase):
	def test_simular_consorcio_basic(self):
		resultado = simular_consorcio(Decimal('300000'), 120, 1.5, 2.0, fgts_saldo=10000)
		# função retorna floats em chaves conhecidas
		self.assertIn('parcela_fixa', resultado)
		self.assertIn('total_custo', resultado)
		self.assertEqual(resultado['valor_lance_fgts'], 10000.0)
		self.assertGreater(resultado['parcela_fixa'], 0.0)

	def test_simular_aluguel_investimento_basic(self):
		resultado = simular_aluguel_investimento(
			valor_imovel_total=300000,
			entrada_total=60000,
			taxa_investimento=5.0,
			aluguel_inicial=1500,
			taxa_inflacao=3.0,
			prazo_meses=12,
			recursos_proprios_iniciais=0.0,
			opcao_pagamento_aluguel='investimento',
			fgts_saldo=0.0,
			rendimento_fgts=3.0,
			fgts_mensal_percent=8.0,
			aporte_13=1000,
			renda_familiar_bruta=5000,
			valorizacao_imovel=2.0,
			taxa_anual_financiamento=7.0
		)
		self.assertIn('acumulado_final', resultado)
		self.assertIn('total_gasto_aluguel', resultado)
		self.assertGreaterEqual(resultado['acumulado_final'], 0.0)
		self.assertGreater(resultado['total_gasto_aluguel'], 0.0)

	def test_comparar_cenarios_e_formatar_economia_present(self):
		from simulacao.calculadora_financeira import comparar_cenarios_e_formatar

		dados_form = {
			'valor_imovel': '300000',
			'entrada': '60000',
			'valor_despesas': '0',
			'prazo_anos': '30',
			'taxa_anual': '7.0',
			'seguro_mensal': '0',
			'taxa_admin_mensal': '0',
			'fgts_saldo': '10000',
			'incorporar_despesas': 'off',
			'usar_fgts_financiamento': 'on',
			'tipo_amortizacao_fgts': 'reduzir_prazo',
			'mes_uso_fgts_financiamento': '12',

			'taxa_adm': '1.5',
			'fundo_reserva': '2.0',
			'valor_imovel_total': '300000',
			'entrada_total': '60000',
			'taxa_investimento': '5.0',
			'aluguel_inicial': '1500',
			'taxa_inflacao': '3.0',
			'recursos_proprios_iniciais': '0.0',
			'opcao_pagamento_aluguel': 'investimento',
			'rendimento_fgts': '3.0',
			'fgts_mensal_percent': '8.0',
			'aporte_13': '1000',
			'renda_familiar_bruta': '5000',
			'valorizacao_imovel': '2.0'
		}

		resumo = comparar_cenarios_e_formatar(dados_form)
		# Deve conter entradas para Price/SAC e cada uma deve trazer 'economia'
		metodos = [r['metodo'] for r in resumo]
		self.assertTrue(any('Price' in m or 'SAC' in m for m in metodos))
		# Pelo menos uma entrada de financiamento deve ter chave 'economia'
		found = False
		for r in resumo:
			if r.get('metodo') in ('Tabela Price', 'Tabela SAC') and 'economia' in r:
				found = True
		self.assertTrue(found)
