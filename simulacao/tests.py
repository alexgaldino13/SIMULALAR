from django.test import TestCase
from django.test import SimpleTestCase
from decimal import Decimal

from simulacao.calculadora_financeira import (
	simular_consorcio, 
	simular_aluguel_investimento,
	calcular_iof,
	calcular_despesas_imovel,
	adicionar_despesas_ao_financiamento
)

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

# ==============================================================================
# TESTES: CÁLCULO DE IOF (Imposto sobre Operações Financeiras)
# ==============================================================================

class CalcularIOFTests(SimpleTestCase):
	"""Testes para função calcular_iof()"""
	
	def test_calcular_iof_basico_com_prazo_meses(self):
		"""Testa cálculo básico de IOF com prazo em meses"""
		resultado = calcular_iof(valor_financiado=300000, prazo_meses=360)
		
		# Validações básicas
		self.assertIn('iof_taxa_diaria', resultado)
		self.assertIn('iof_taxa_fixa', resultado)
		self.assertIn('iof_total', resultado)
		self.assertIn('valor_total_com_iof', resultado)
		
		# IOF deve ser positivo
		self.assertGreater(resultado['iof_total'], 0.0)
		
		# Valor total deve ser maior que valor financiado
		self.assertGreater(resultado['valor_total_com_iof'], 300000.0)
	
	def test_calcular_iof_com_prazo_dias(self):
		"""Testa cálculo com prazo em dias explícito"""
		resultado = calcular_iof(valor_financiado=300000, prazo_dias=365)
		
		# IOF diária com 365 dias (máximo)
		# 300000 × 0,038% × 365 = 41,700.00
		expected_iof_diaria = 300000 * 0.000038 * 365
		self.assertAlmostEqual(resultado['iof_taxa_diaria'], expected_iof_diaria, places=0)
		
		# IOF fixa: 300000 × 0,38% = 1,140.00
		expected_iof_fixa = 300000 * 0.0038
		self.assertAlmostEqual(resultado['iof_taxa_fixa'], expected_iof_fixa, places=0)
	
	def test_calcular_iof_dias_limitados_365(self):
		"""Valida que dias são limitados a 365 (máximo legal)"""
		resultado_1000_dias = calcular_iof(valor_financiado=300000, prazo_dias=1000)
		resultado_365_dias = calcular_iof(valor_financiado=300000, prazo_dias=365)
		
		# Ambos devem ter 365 dias registrados
		self.assertEqual(resultado_1000_dias['dias_operacao'], 365)
		self.assertEqual(resultado_365_dias['dias_operacao'], 365)
		
		# IOF diária deve ser igual em ambos
		self.assertAlmostEqual(
			resultado_1000_dias['iof_taxa_diaria'],
			resultado_365_dias['iof_taxa_diaria'],
			places=2
		)
	
	def test_calcular_iof_sem_aplicar(self):
		"""Testa quando IOF não é aplicado (aplicar_iof=False)"""
		resultado = calcular_iof(
			valor_financiado=300000,
			prazo_meses=360,
			aplicar_iof=False
		)
		
		# Todas as componentes de IOF devem ser zero
		self.assertEqual(resultado['iof_taxa_diaria'], 0.0)
		self.assertEqual(resultado['iof_taxa_fixa'], 0.0)
		self.assertEqual(resultado['iof_total'], 0.0)
		
		# Valor total deve ser igual ao valor financiado
		self.assertEqual(resultado['valor_total_com_iof'], 300000.0)
		
		# Aplicar IOF deve ser False
		self.assertFalse(resultado['aplicar_iof'])
	
	def test_calcular_iof_valor_pequeno(self):
		"""Testa IOF com valores pequenos"""
		resultado = calcular_iof(valor_financiado=100000, prazo_meses=180)
		
		# IOF diária: 100000 × 0,038% × 365 = 13,900.00
		expected_diaria = 100000 * 0.000038 * 365
		self.assertAlmostEqual(resultado['iof_taxa_diaria'], expected_diaria, places=0)
		
		# IOF fixa: 100000 × 0,38% = 380.00
		expected_fixa = 100000 * 0.0038
		self.assertAlmostEqual(resultado['iof_taxa_fixa'], expected_fixa, places=0)
	
	def test_calcular_iof_composicao_total(self):
		"""Valida que IOF total = IOF diária + IOF fixa"""
		resultado = calcular_iof(valor_financiado=500000, prazo_meses=240)
		
		iof_esperado = resultado['iof_taxa_diaria'] + resultado['iof_taxa_fixa']
		self.assertAlmostEqual(resultado['iof_total'], iof_esperado, places=2)
	
	def test_calcular_iof_percentual_sobre_valor(self):
		"""Valida o percentual de IOF em relação ao valor financiado"""
		resultado = calcular_iof(valor_financiado=300000, prazo_meses=360)
		
		# Percentual = (IOF_total / valor_financiado) × 100
		percentual_esperado = (resultado['iof_total'] / 300000) * 100
		self.assertAlmostEqual(
			resultado['percentual_iof_total'],
			percentual_esperado,
			places=2
		)
	
	def test_calcular_iof_erro_prazo_nao_fornecido(self):
		"""Valida que erro é lançado quando prazo não é fornecido"""
		with self.assertRaises(ValueError):
			calcular_iof(valor_financiado=300000)
	
	def test_calcular_iof_exemplo_real_itau(self):
		"""Testa com dados reais do contrato Itaú validado"""
		# Contrato Itaú: R$ 327.650,72 financiado por 360 meses
		valor = 327650.72
		prazo = 360
		
		resultado = calcular_iof(
			valor_financiado=valor,
			prazo_meses=prazo,
			taxa_iof_diaria=0.000038,  # 0,038% ao dia
			taxa_iof_fixa=0.0038       # 0,38% fixo
		)
		
		# IOF diária esperada: 327.650,72 × 0,000038 × 365 ≈ 4.551,33
		expected_diaria = valor * 0.000038 * 365
		# IOF fixa esperada: 327.650,72 × 0,0038 ≈ 1.249,07
		expected_fixa = valor * 0.0038
		# Total: ~5.800,40
		expected_total = expected_diaria + expected_fixa
		
		self.assertAlmostEqual(resultado['iof_taxa_diaria'], expected_diaria, places=0)
		self.assertAlmostEqual(resultado['iof_taxa_fixa'], expected_fixa, places=0)
		self.assertAlmostEqual(resultado['iof_total'], expected_total, places=0)
		
		# Valor total com IOF
		expected_com_iof = valor + expected_total
		self.assertAlmostEqual(resultado['valor_total_com_iof'], expected_com_iof, places=2)
	
	def test_calcular_iof_retorno_estrutura(self):
		"""Valida que todas as chaves esperadas estão presentes no retorno"""
		resultado = calcular_iof(valor_financiado=300000, prazo_meses=360)
		
		chaves_esperadas = [
			'valor_financiado',
			'dias_operacao',
			'iof_taxa_diaria',
			'iof_taxa_fixa',
			'iof_total',
			'percentual_iof_total',
			'valor_total_com_iof',
			'aplicar_iof',
			'taxa_iof_diaria_percent',
			'taxa_iof_fixa_percent'
		]
		
		for chave in chaves_esperadas:
			self.assertIn(chave, resultado, f"Chave '{chave}' não encontrada no resultado")
	
	def test_calcular_iof_conversao_meses_para_dias(self):
		"""Valida conversão correta de meses para dias (30 dias/mês)"""
		resultado = calcular_iof(valor_financiado=100000, prazo_meses=12)
		
		# 12 meses = 360 dias, mas limitado a 365, então 360 dias
		self.assertEqual(resultado['dias_operacao'], 360)
	
	def test_calcular_iof_tipos_numericos(self):
		"""Valida que retorno contém floats, não Decimal"""
		resultado = calcular_iof(valor_financiado=300000, prazo_meses=360)
		
		# Chaves numéricas devem ser float
		self.assertIsInstance(resultado['iof_total'], float)
		self.assertIsInstance(resultado['valor_total_com_iof'], float)
		self.assertIsInstance(resultado['percentual_iof_total'], float)

# ==============================================================================
# TESTES: CÁLCULO DE DESPESAS DO IMÓVEL (IPTU, CONDOMÍNIO, SEGURO)
# ==============================================================================

class CalcularDespesasImovelTests(SimpleTestCase):
	"""Testes para função calcular_despesas_imovel()"""
	
	def test_calcular_despesas_basico(self):
		"""Testa cálculo básico de despesas do imóvel"""
		resultado = calcular_despesas_imovel(
			valor_imovel=500000,
			aliquota_iptu=0.012,
			valor_condominio_mensal=800,
			percentual_seguro=0.004,
			prazo_meses=360
		)
		
		# Validações básicas
		self.assertIn('iptu_mensal', resultado)
		self.assertIn('condominio_mensal', resultado)
		self.assertIn('seguro_mensal', resultado)
		self.assertIn('total_mensal', resultado)
		self.assertIn('despesa_periodo', resultado)
		
		# Valores devem ser positivos
		self.assertGreater(resultado['total_mensal'], 0.0)
		self.assertGreater(resultado['despesa_periodo'], 0.0)
	
	def test_calcular_iptu_mensal(self):
		"""Valida cálculo correto de IPTU mensal"""
		resultado = calcular_despesas_imovel(
			valor_imovel=600000,
			aliquota_iptu=0.012,  # 1.2% ao ano
			valor_condominio_mensal=0,
			percentual_seguro=0,
			prazo_meses=360
		)
		
		# IPTU anual: 600000 × 0.012 = 7200
		# IPTU mensal: 7200 / 12 = 600
		expected_iptu_mensal = 600000 * 0.012 / 12
		self.assertAlmostEqual(resultado['iptu_mensal'], expected_iptu_mensal, places=2)
		
		# IPTU anual esperado
		expected_iptu_anual = 600000 * 0.012
		self.assertAlmostEqual(resultado['iptu_anual'], expected_iptu_anual, places=2)
	
	def test_calcular_condominio_mensal(self):
		"""Valida cálculo de condomínio mensal"""
		resultado = calcular_despesas_imovel(
			valor_imovel=500000,
			aliquota_iptu=0,
			valor_condominio_mensal=950,
			percentual_seguro=0,
			prazo_meses=360
		)
		
		# Condomínio deve ser exatamente o valor fornecido
		self.assertAlmostEqual(resultado['condominio_mensal'], 950.0, places=2)
		
		# Total anual = condomínio × 12
		expected_total_anual = 950 * 12
		self.assertAlmostEqual(resultado['total_anual'], expected_total_anual, places=2)
	
	def test_calcular_seguro_predial(self):
		"""Valida cálculo correto de seguro predial"""
		resultado = calcular_despesas_imovel(
			valor_imovel=500000,
			aliquota_iptu=0,
			valor_condominio_mensal=0,
			percentual_seguro=0.004,  # 0.4% ao ano
			prazo_meses=360
		)
		
		# Seguro anual: 500000 × 0.004 = 2000
		# Seguro mensal: 2000 / 12 ≈ 166.67
		expected_seguro_mensal = 500000 * 0.004 / 12
		self.assertAlmostEqual(resultado['seguro_mensal'], expected_seguro_mensal, places=2)
		
		# Seguro anual
		expected_seguro_anual = 500000 * 0.004
		self.assertAlmostEqual(resultado['seguro_anual'], expected_seguro_anual, places=2)
	
	def test_calcular_despesas_totais_30anos(self):
		"""Valida cálculo de despesas acumuladas no período"""
		resultado = calcular_despesas_imovel(
			valor_imovel=500000,
			aliquota_iptu=0.012,
			valor_condominio_mensal=800,
			percentual_seguro=0.004,
			prazo_meses=360
		)
		
		# Despesa período = total_mensal × 360
		expected_despesa_periodo = resultado['total_mensal'] * 360
		self.assertAlmostEqual(resultado['despesa_periodo'], expected_despesa_periodo, places=0)
	
	def test_calcular_despesas_sem_componentes(self):
		"""Valida que todas as despesas podem ser desabilitadas"""
		resultado = calcular_despesas_imovel(
			valor_imovel=500000,
			aliquota_iptu=0.012,
			valor_condominio_mensal=800,
			percentual_seguro=0.004,
			prazo_meses=360,
			incluir_iptu=False,
			incluir_condominio=False,
			incluir_seguro=False
		)
		
		# Se desabilitar tudo, despesas devem ser zero
		self.assertEqual(resultado['iptu_mensal'], 0.0)
		self.assertEqual(resultado['condominio_mensal'], 0.0)
		self.assertEqual(resultado['seguro_mensal'], 0.0)
		self.assertEqual(resultado['total_mensal'], 0.0)
		self.assertEqual(resultado['despesa_periodo'], 0.0)
	
	def test_calcular_percentual_sobre_imovel(self):
		"""Valida cálculo de despesas como % do valor do imóvel"""
		resultado = calcular_despesas_imovel(
			valor_imovel=500000,
			aliquota_iptu=0.012,
			valor_condominio_mensal=1000,
			percentual_seguro=0.004,
			prazo_meses=360
		)
		
		# Percentual = (despesa_periodo / valor_imovel) × 100
		expected_percentual = (resultado['despesa_periodo'] / 500000) * 100
		self.assertAlmostEqual(resultado['percentual_sobre_imovel'], expected_percentual, places=2)
	
	def test_calcular_despesas_exemplo_real(self):
		"""Testa com valores realistas de imóvel brasileiro"""
		# Apartamento de R$ 400.000 em São Paulo
		# IPTU: 1.2% a.a., Condomínio: R$ 700/mês, Seguro: 0.4% a.a.
		resultado = calcular_despesas_imovel(
			valor_imovel=400000,
			aliquota_iptu=0.012,
			valor_condominio_mensal=700,
			percentual_seguro=0.004,
			prazo_meses=360
		)
		
		# Expectativas realistas
		# IPTU mensal: 400000 × 1.2% / 12 = 400
		self.assertAlmostEqual(resultado['iptu_mensal'], 400.0, places=0)
		
		# Condomínio: 700 (fixo)
		self.assertEqual(resultado['condominio_mensal'], 700.0)
		
		# Seguro mensal: 400000 × 0.4% / 12 ≈ 133.33
		self.assertAlmostEqual(resultado['seguro_mensal'], 133.33, places=1)
		
		# Total mensal deve ser ~1233
		expected_total = 400 + 700 + 133.33
		self.assertAlmostEqual(resultado['total_mensal'], expected_total, places=0)
	
	def test_calcular_despesas_retorno_estrutura(self):
		"""Valida que todas as chaves esperadas estão presentes"""
		resultado = calcular_despesas_imovel(
			valor_imovel=500000,
			aliquota_iptu=0.012,
			valor_condominio_mensal=800,
			percentual_seguro=0.004
		)
		
		chaves_esperadas = [
			'valor_imovel',
			'iptu_mensal',
			'iptu_anual',
			'condominio_mensal',
			'seguro_mensal',
			'seguro_anual',
			'total_mensal',
			'total_anual',
			'despesa_periodo',
			'percentual_sobre_imovel',
			'aliquota_iptu_percent',
			'percentual_seguro_percent',
			'incluir_iptu',
			'incluir_condominio',
			'incluir_seguro'
		]
		
		for chave in chaves_esperadas:
			self.assertIn(chave, resultado, f"Chave '{chave}' não encontrada")
	
	def test_calcular_despesas_tipos_numericos(self):
		"""Valida que retorno contém floats, não Decimal"""
		resultado = calcular_despesas_imovel(
			valor_imovel=500000,
			aliquota_iptu=0.012,
			valor_condominio_mensal=800,
			percentual_seguro=0.004
		)
		
		# Chaves numéricas devem ser float
		self.assertIsInstance(resultado['iptu_mensal'], float)
		self.assertIsInstance(resultado['total_mensal'], float)
		self.assertIsInstance(resultado['despesa_periodo'], float)

# ==============================================================================
# TESTES: INTEGRAÇÃO DE DESPESAS AO FINANCIAMENTO
# ==============================================================================

class AdicionarDespesasAoFinanciamentoTests(SimpleTestCase):
	"""Testes para função adicionar_despesas_ao_financiamento()"""
	
	def test_adicionar_despesas_ao_financiamento(self):
		"""Testa integração de despesas ao resultado de financiamento"""
		from simulacao.calculadora_financeira import calcular_price_sac
		
		# Financiamento base
		resultado_financiamento = calcular_price_sac(
			metodo='price',
			valor_principal=300000,
			taxa_anual=7.0,
			prazo_meses=360
		)
		
		# Despesas
		despesas_imovel = calcular_despesas_imovel(
			valor_imovel=400000,
			aliquota_iptu=0.012,
			valor_condominio_mensal=700,
			percentual_seguro=0.004,
			prazo_meses=360
		)
		
		# Integrar
		resultado_com_despesas = adicionar_despesas_ao_financiamento(
			resultado_financiamento,
			despesas_imovel
		)
		
		# Validações
		self.assertIn('tabela_com_despesas', resultado_com_despesas)
		self.assertIn('parcela_inicial_com_despesas', resultado_com_despesas)
		self.assertIn('despesa_mensal_total', resultado_com_despesas)
		self.assertIn('total_custo_real', resultado_com_despesas)
		
		# Parcela com despesas deve ser maior que parcela original
		self.assertGreater(
			resultado_com_despesas['parcela_inicial_com_despesas'],
			resultado_financiamento['parcela_inicial']
		)
		
		# Tabela com despesas deve ter mesmo tamanho
		self.assertEqual(
			len(resultado_com_despesas['tabela_com_despesas']),
			len(resultado_financiamento['tabela'])
		)
	
	def test_despesas_adicionadas_por_mes(self):
		"""Valida que despesas são adicionadas corretamente em cada mês"""
		from simulacao.calculadora_financeira import calcular_price_sac
		
		resultado_financiamento = calcular_price_sac(
			metodo='sac',
			valor_principal=200000,
			taxa_anual=6.0,
			prazo_meses=60
		)
		
		despesas_imovel = calcular_despesas_imovel(
			valor_imovel=300000,
			aliquota_iptu=0.012,
			valor_condominio_mensal=500,
			percentual_seguro=0.004,
			prazo_meses=60
		)
		
		resultado_com_despesas = adicionar_despesas_ao_financiamento(
			resultado_financiamento,
			despesas_imovel
		)
		
		# Verificar primeira linha da tabela
		tabela_com = resultado_com_despesas['tabela_com_despesas']
		original = resultado_financiamento['tabela']
		
		if tabela_com and original:
			parcela_com_despesa = tabela_com[0]['parcela_com_despesa']
			parcela_original = original[0]['parcela']
			despesa_mensal = despesas_imovel['total_mensal']
			
			# parcela_com_despesa = parcela_original + despesa_mensal
			expected = parcela_original + despesa_mensal
			self.assertAlmostEqual(parcela_com_despesa, expected, places=1)

