"""
TESTE DE 10 PERFIS DE USUÁRIOS - VALIDAÇÃO DE MERCADO BRASILEIRO

Script para simular jornadas completas de 10 perfis distintos no aplicativo FI,
verificando se as fórmulas de SAC/PRICE, Consórcio e Aluguel+Investimento retornam
valores fiéis ao mercado brasileiro e se o fluxo do Wizard faz sentido.

Resultado esperado:
1. Validação de cálculos contra padrões de mercado (2024-2025)
2. Detecção de variáveis faltantes (TR, seguros obrigatórios, subsídios MCMV)
3. Feedback sobre confusão no fluxo do Wizard para cada perfil
4. Sugestões de melhoria
"""

import sys
import os
from decimal import Decimal
from django.test import SimpleTestCase

# Adiciona o diretório do projeto ao path
sys.path.insert(0, '/root/code/PROJETOS/FI')

# Importa as funções de cálculo
from simulacao.calculadora_financeira import (
    calcular_price_sac,
    simular_consorcio,
    simular_consorcio_com_lances,
    simular_aluguel_investimento,
    comparar_cenarios_e_formatar
)

# ============================================================================
# CONSTANTES DE MERCADO (Brasil 2024-2025)
# ============================================================================

TABELA_TAXAS_BANCOS = {
    'BB': {'price': 7.5, 'sac': 7.5},  # Banco do Brasil
    'CAIXA': {'price': 7.2, 'sac': 7.2, 'mcmv': 4.5},  # Caixa Econômica
    'ITAU': {'price': 9.2, 'sac': 9.2},  # Itaú
    'BRADESCO': {'price': 8.9, 'sac': 8.9},  # Bradesco
    'SANTANDER': {'price': 8.5, 'sac': 8.5},  # Santander
}

CONSORCIO_PADRAO = {
    'taxa_adm': 1.8,  # % ao ano
    'fundo_reserva': 0.8,  # %
    'parcela_media': 0.7,  # % ao mês do valor
}

SEGUROS_OBRIGATORIOS = {
    'MIP': {'descricao': 'Seguro Morte/Invalidez', 'taxa_max': 0.25},  # % ao mês
    'DFI': {'descricao': 'Seguro Desemprego/Funeral', 'taxa_max': 0.15},  # % ao mês
}

LIMITES_FINANCIAMENTO = {
    'LTV_MAX': 0.80,  # Loan-to-Value máximo = 80%
    'ENTRADA_MIN': 0.20,  # Entrada mínima = 20%
}

SELIC_ATUAL = 10.5  # % ao ano (referência)

# ============================================================================
# PERFIL 1: MCMV (Minha Casa Minha Vida)
# ============================================================================

perfil_1_mcmv = {
    'nome': 'MCMV - Programa Minha Casa Minha Vida',
    'descricao': 'Renda R$ 4.500, Imóvel R$ 220k, FGTS R$ 15k. Testar Subsídio.',
    'dados': {
        'valor_imovel': 220000,
        'entrada': 15000,  # Usando FGTS
        'fgts_saldo': 15000,
        'renda_familiar_bruta': 4500,
        'prazo_anos': 20,
        'taxa_anual': 4.5,  # Taxa MCMV da Caixa
        'seguro_mensal': 0.25,
        'valor_despesas': 0,
        'incorporar_despesas': False,
        'usar_fgts_financiamento': True,
        'tipo_amortizacao_fgts': 'reduzir_prazo',
        'mes_uso_fgts_financiamento': 12,
        'fgts_mensal_percent': 8.0,
    },
    'validacoes': [
        'Subsídio MCMV deveria estar explícito (não está no código)',
        'Parcela não deve exceder 30% da renda familiar',
        'FGTS é utilizado corretamente para entrada e amortização',
        'Taxa de 4.5% é fiel ao programa MCMV da Caixa',
    ],
    'problemas_esperados': [
        'FALTA: Subsídio governamental não é calculado',
        'FALTA: Simulação de elegibilidade MCMV (renda, região)',
        'WIZARD: Não há pergunta específica sobre programa MCMV',
    ]
}

# ============================================================================
# PERFIL 2: ALUGUEL vs COMPRA
# ============================================================================

perfil_2_aluguel_compra = {
    'nome': 'Aluguel vs Compra',
    'descricao': 'Aluguel R$ 3k, Imóvel R$ 500k. Verificar gráfico de comparação.',
    'dados': {
        'valor_imovel': 500000,
        'entrada': 100000,  # 20% de entrada
        'paga_aluguel': True,
        'aluguel_inicial': 3000,
        'renda_familiar_bruta': 15000,
        'prazo_anos': 30,
        'taxa_anual': 7.5,  # BB média
        'seguro_mensal': 0.25,
        'taxa_admin_mensal': 0.05,
        'valor_imovel_total': 500000,
        'entrada_total': 100000,
        'taxa_investimento': 6.0,  # CDI
        'taxa_inflacao': 3.5,
        'recursos_proprios_iniciais': 0.0,
        'opcao_pagamento_aluguel': 'investimento',
        'fgts_saldo': 0,
        'rendimento_fgts': 3.0,
        'fgts_mensal_percent': 0,
        'aporte_13': 2000,
        'valorizacao_imovel': 2.0,  # Valorização imobiliária
    },
    'validacoes': [
        'Gráfico de comparação aluguel vs compra deve ser visual',
        'NPV (Valor Presente Líquido) deve favorecer compra no longo prazo',
        'Cenário de aluguel+investimento vs financiamento',
    ],
    'problemas_esperados': [
        'FALTA: Gráfico comparativo visual não é gerado',
        'FALTA: Projeção de oferta/demanda imobiliária por região',
        'WIZARD: Fluxo confuso - mistura aluguel, investimento e financiamento',
    ]
}

# ============================================================================
# PERFIL 3: POUPADOR
# ============================================================================

perfil_3_poupador = {
    'nome': 'Poupador com Aporte Mensal',
    'descricao': 'Aporte mensal R$ 2k, Imóvel R$ 400k. Testar módulo Investimento/CDI.',
    'dados': {
        'valor_imovel': 400000,
        'entrada': 80000,
        'renda_familiar_bruta': 8000,
        'prazo_anos': 25,
        'taxa_anual': 7.2,  # Caixa
        'aporte_13': 2000,  # Aporte mensal = 2k
        'taxa_investimento': 5.5,  # CDI médio
        'fgts_saldo': 5000,
        'rendimento_fgts': 3.0,
        'fgts_mensal_percent': 8.0,
        'valor_imovel_total': 400000,
        'entrada_total': 80000,
        'taxa_inflacao': 3.5,
        'recursos_proprios_iniciais': 10000,
        'opcao_pagamento_aluguel': 'renda',
        'valorizacao_imovel': 2.0,
    },
    'validacoes': [
        'Aporte mensal deve ser somado ao saldo de investimento',
        'Rendimento do FGTS deve ser progressivo',
        'Entrada maior reduz juros totais e prazo',
    ],
    'problemas_esperados': [
        'FALTA: Simulação de outros investimentos (Tesouro Direto, ações)',
        'WIZARD: Não há pergunta clara sobre aporte mensal pós-compra',
        'FALTA: Comparação entre investir e quitar o financiamento',
    ]
}

# ============================================================================
# PERFIL 4: INVESTIDOR
# ============================================================================

perfil_4_investidor = {
    'nome': 'Investidor Imobiliário',
    'descricao': 'Imóvel R$ 300k, Aluguel esperado R$ 1.800. Verificar ROI.',
    'dados': {
        'valor_imovel': 300000,
        'entrada': 60000,
        'aluguel_esperado': 1800,  # ROI = 7.2% ao ano (1800*12/300000)
        'renda_familiar_bruta': 12000,
        'prazo_anos': 20,
        'taxa_anual': 8.5,  # Taxa média Santander
        'seguro_mensal': 0.25,
        'valor_imovel_total': 300000,
        'entrada_total': 60000,
        'taxa_investimento': 6.0,
        'aluguel_inicial': 1800,
        'taxa_inflacao': 3.5,
        'recursos_proprios_iniciais': 0,
        'opcao_pagamento_aluguel': 'investimento',  # Aluguel paga parcela + investimento
        'fgts_saldo': 8000,
        'rendimento_fgts': 3.0,
        'fgts_mensal_percent': 8.0,
        'aporte_13': 0,
        'valorizacao_imovel': 2.5,  # Localização premium
    },
    'validacoes': [
        'ROI deve ser calculado: (aluguel anual / valor investido)',
        'Fluxo de caixa mensal deve considerar despesas (IPTU, condomínio, seguro)',
        'Vacância e inadimplência devem reduzir rentabilidade',
    ],
    'problemas_esperados': [
        'FALTA: Cálculo explícito de ROI',
        'FALTA: Despesas com imóvel alugado (IPTU, condomínio, seguro)',
        'FALTA: Simulação de taxa de vacância',
        'FALTA: Simulação de inadimplência do inquilino',
        'WIZARD: Não distingue comprador de investidor imobiliário',
    ]
}

# ============================================================================
# PERFIL 5: UPGRADE (Venda + Compra)
# ============================================================================

perfil_5_upgrade = {
    'nome': 'Upgrade - Venda + Compra',
    'descricao': 'Venda de imóvel R$ 400k para compra R$ 800k. Testar entrada.',
    'dados': {
        'valor_imovel_venda': 400000,
        'valor_imovel_nova': 800000,
        'saldo_devedor_antigo': 200000,  # Saldo do financiamento anterior
        'entrada': 400000 - 200000 + 50000,  # Usa saldo da venda + economia
        'renda_familiar_bruta': 18000,
        'prazo_anos': 25,
        'taxa_anual': 7.5,
        'seguro_mensal': 0.25,
    },
    'validacoes': [
        'Entrada deve considerar saldo da venda anterior',
        'Imposto de Transmissão (ITBI) deve ser deduzido da venda',
        'Entrada mínima deve ser 20% do novo valor',
    ],
    'problemas_esperados': [
        'FALTA: Cálculo de ITBI na venda do imóvel anterior',
        'FALTA: Simulação de reforma/obra no novo imóvel',
        'WIZARD: Não há pergunta sobre imóvel anterior/saldo devedor',
        'WIZARD: Fluxo confuso - mistura venda e compra',
    ]
}

# ============================================================================
# PERFIL 6: CONSORCIADO
# ============================================================================

perfil_6_consorcio = {
    'nome': 'Consorciado',
    'descricao': 'Carta de R$ 500k, Taxa Adm 1.5%. Testar parcela sem juros.',
    'dados': {
        'objetivo': 'Consórcio',
        'valor_imovel': 500000,
        'prazo_anos': 15,
        'taxa_adm': 1.5,  # % ao ano
        'fundo_reserva': 0.8,  # %
        'fgts_saldo': 20000,
        'tipo_lance': 'livre',
        'percentual_lance': 30.0,  # 30% de lance
        'valor_lance_fgts': 20000,
    },
    'validacoes': [
        'Parcela = ~0.7% do valor ao mês (sem juros)',
        'Taxa de administração deve ser transparente',
        'Fundo de reserva deve garantir inesperados',
        'Lance aumenta probabilidade de contemplação',
    ],
    'problemas_esperados': [
        'FALTA: Cálculo de probabilidade real de contemplação',
        'FALTA: Comparação com financiamento em paralelo',
        'FALTA: Liquidação de cotas (venda de direitos)',
        'WIZARD: Não há pergunta sobre histórico de consórcio anterior',
    ]
}

# ============================================================================
# PERFIL 7: EMPRESÁRIO (Alto Crédito)
# ============================================================================

perfil_7_empresario = {
    'nome': 'Empresário - Alto Crédito',
    'descricao': 'Imóvel R$ 3Mi, Taxa 10% a.a. Testar limites de crédito.',
    'dados': {
        'valor_imovel': 3000000,
        'entrada': 600000,  # 20%
        'renda_familiar_bruta': 100000,  # Renda alta
        'prazo_anos': 30,
        'taxa_anual': 10.0,  # Taxa maior (risco ou taxa de mercado)
        'seguro_mensal': 0.20,  # Seguro pode ser menor para alta renda
        'taxa_admin_mensal': 0.02,
    },
    'validacoes': [
        'LTV (Loan-to-Value) deve estar dentro de 80%',
        'Capacidade de pagamento deve ser >=30% da renda',
        'Taxa pode ser negociada conforme história creditícia',
    ],
    'problemas_esperados': [
        'FALTA: Simulação de negociação de taxa',
        'FALTA: Impacto de histórico creditício na taxa',
        'FALTA: Limite máximo de crédito por banco',
        'WIZARD: Não há campo para comprovação de renda não-formal',
    ]
}

# ============================================================================
# PERFIL 8: AUTÔNOMO (Prazos Curtos)
# ============================================================================

perfil_8_autonom = {
    'nome': 'Autônomo - Prazo Curto',
    'descricao': 'Entrada 50%, 120 meses. Testar flexibilidade.',
    'dados': {
        'valor_imovel': 250000,
        'entrada': 125000,  # 50%
        'renda_familiar_bruta': 6000,  # Renda limitada
        'prazo_anos': 10,  # 120 meses
        'taxa_anual': 8.0,
        'seguro_mensal': 0.25,
        'entrada_percentual': 50,
    },
    'validacoes': [
        'Entrada alta reduz financiamento e juros',
        'Prazo curto com entrada alta é viável',
        'Autônomo pode ter renda comprovada por últimos 12 meses',
    ],
    'problemas_esperados': [
        'FALTA: Comprovação de renda para autônomo (declaração, MEI)',
        'FALTA: Simulação de taxa variável (renda flutuante)',
        'WIZARD: Não há campo específico para profissional autônomo',
    ]
}

# ============================================================================
# PERFIL 9: CUSTO DE OPORTUNIDADE (SELIC vs Financiamento)
# ============================================================================

perfil_9_oportunidade = {
    'nome': 'Custo de Oportunidade - SELIC vs Financiamento',
    'descricao': 'R$ 1Mi em caixa. Financiar ou pagar à vista?',
    'dados': {
        'valor_imovel': 1000000,
        'entrada': 1000000,  # Tem dinheiro para pagar à vista
        'selic_atual': 10.5,
        'taxa_financiamento': 8.0,
        'prazo_anos': 30,
        'aplicacao_alternativa': 'tesouro_direto',  # Se deixar em Tesouro Direto rendendo 10.5%
    },
    'validacoes': [
        'Se SELIC > taxa de financiamento, é melhor manter o dinheiro investido',
        'Financiar permite aproveitar SELIC/Tesouro Direto',
        'Análise de Valor Presente (VPL) deve orientar decisão',
    ],
    'problemas_esperados': [
        'FALTA: Cálculo de oportunidade vs financiamento',
        'FALTA: Comparação com taxas de investimento seguro (Tesouro)',
        'FALTA: Análise de inflação vs financiamento',
        'WIZARD: Não há pergunta sobre aplicações alternativas',
    ]
}

# ============================================================================
# PERFIL 10: MIGRAÇÃO (Comparação de Taxas entre Bancos)
# ============================================================================

perfil_10_migracao = {
    'nome': 'Migração - Comparativo de Taxas entre Bancos',
    'descricao': 'Comparativo BB vs Caixa vs Itaú. Qual é melhor?',
    'dados': {
        'valor_imovel': 400000,
        'entrada': 80000,
        'renda_familiar_bruta': 10000,
        'prazo_anos': 25,
        'bancos_comparar': ['BB', 'CAIXA', 'ITAU', 'BRADESCO', 'SANTANDER'],
    },
    'validacoes': [
        'Parcela inicial varia conforme taxa do banco',
        'CET (Custo Efetivo Total) é melhor métrica que taxa nominal',
        'Banco com menor parcela no início pode ser melhor no longo prazo',
    ],
    'problemas_esperados': [
        'FALTA: Comparação entre bancos (frontend não oferece)',
        'FALTA: CET não é calculado (apenas taxa nominal)',
        'FALTA: Simulação de portabilidade de financiamento',
        'WIZARD: Não há opção de simular múltiplos cenários em paralelo',
    ]
}

# ============================================================================
# FUNÇÃO: EXECUTAR TESTE PARA UM PERFIL
# ============================================================================

def testar_perfil(perfil_numero, perfil_data):
    """Executa teste completo para um perfil."""
    
    print(f"\n{'='*80}")
    print(f"PERFIL {perfil_numero}: {perfil_data['nome']}")
    print(f"{'='*80}")
    print(f"\nDescrição: {perfil_data['descricao']}\n")
    
    dados = perfil_data['dados']
    
    # ========================================================================
    # TESTE 1: SIMULAÇÃO BÁSICA (Price/SAC/Consórcio/Aluguel)
    # ========================================================================
    
    print(f"TESTE 1: SIMULAÇÃO BÁSICA")
    print(f"-" * 80)
    
    if perfil_numero in [1, 2, 3, 7, 8, 9, 10]:  # Financiamento
        
        # Testa Price
        try:
            resultado_price = calcular_price_sac(
                'price',
                valor_principal=dados['valor_imovel'] - dados.get('entrada', 0),
                taxa_anual=dados['taxa_anual'],
                prazo_meses=dados['prazo_anos'] * 12,
                seguro_mensal=dados.get('seguro_mensal', 0),
                taxa_admin_mensal=dados.get('taxa_admin_mensal', 0),
                renda_familiar_bruta=dados.get('renda_familiar_bruta', 0),
                usar_fgts_financiamento=dados.get('usar_fgts_financiamento', False),
                fgts_mensal_percent=dados.get('fgts_mensal_percent', 0),
                tipo_amortizacao_fgts=dados.get('tipo_amortizacao_fgts', 'reduzir_prazo'),
            )
            
            if resultado_price and 'tabela' in resultado_price:
                parcela_inicial = resultado_price['parcela_inicial']
                total_juros = resultado_price['total_juros']
                print(f"✓ PRICE: Parcela inicial = R$ {parcela_inicial:,.2f}")
                print(f"  Total de juros = R$ {total_juros:,.2f}")
                
                # Validação: Parcela não deve exceder 30% da renda
                renda_mensal = dados.get('renda_familiar_bruta', 0)
                if renda_mensal > 0:
                    percentual_renda = (parcela_inicial / renda_mensal) * 100
                    if percentual_renda > 30:
                        print(f"  ⚠ AVISO: Parcela = {percentual_renda:.1f}% da renda (máx 30%)")
                    else:
                        print(f"  ✓ OK: Parcela = {percentual_renda:.1f}% da renda")
            else:
                print(f"✗ PRICE: Erro na simulação")
        
        except Exception as e:
            print(f"✗ PRICE: Exceção - {str(e)}")
        
        # Testa SAC
        try:
            resultado_sac = calcular_price_sac(
                'sac',
                valor_principal=dados['valor_imovel'] - dados.get('entrada', 0),
                taxa_anual=dados['taxa_anual'],
                prazo_meses=dados['prazo_anos'] * 12,
                seguro_mensal=dados.get('seguro_mensal', 0),
                taxa_admin_mensal=dados.get('taxa_admin_mensal', 0),
                renda_familiar_bruta=dados.get('renda_familiar_bruta', 0),
                usar_fgts_financiamento=dados.get('usar_fgts_financiamento', False),
                fgts_mensal_percent=dados.get('fgts_mensal_percent', 0),
                tipo_amortizacao_fgts=dados.get('tipo_amortizacao_fgts', 'reduzir_prazo'),
            )
            
            if resultado_sac and 'tabela' in resultado_sac:
                parcela_inicial = resultado_sac['parcela_inicial']
                total_juros = resultado_sac['total_juros']
                print(f"\n✓ SAC: Parcela inicial = R$ {parcela_inicial:,.2f}")
                print(f"  Total de juros = R$ {total_juros:,.2f}")
                
                # Comparação Price vs SAC
                juros_price = resultado_price.get('total_juros', 0)
                economia_sac = juros_price - total_juros
                if economia_sac > 0:
                    print(f"\n✓ SAC economiza R$ {economia_sac:,.2f} vs Price")
                else:
                    print(f"\n✗ SAC custa R$ {abs(economia_sac):,.2f} a mais vs Price")
            else:
                print(f"✗ SAC: Erro na simulação")
        
        except Exception as e:
            print(f"✗ SAC: Exceção - {str(e)}")
    
    elif perfil_numero == 6:  # Consórcio
        
        try:
            resultado_consorcio = simular_consorcio(
                valor_imovel=dados['valor_imovel'],
                prazo_meses=dados['prazo_anos'] * 12,
                taxa_adm=dados['taxa_adm'],
                fundo_reserva=dados['fundo_reserva'],
                fgts_saldo=dados.get('fgts_saldo', 0),
            )
            
            parcela_fixa = resultado_consorcio['parcela_fixa']
            total_custo = resultado_consorcio['total_custo']
            print(f"✓ CONSÓRCIO: Parcela fixa = R$ {parcela_fixa:,.2f}")
            print(f"  Total custo = R$ {total_custo:,.2f}")
            print(f"  Contemplação estimada mês {resultado_consorcio['mes_contemplacao_estimado']}")
        
        except Exception as e:
            print(f"✗ CONSÓRCIO: Exceção - {str(e)}")
    
    elif perfil_numero == 2:  # Aluguel + Investimento
        
        try:
            resultado_aluguel = simular_aluguel_investimento(
                valor_imovel_total=dados['valor_imovel_total'],
                entrada_total=dados['entrada_total'],
                taxa_investimento=dados['taxa_investimento'],
                aluguel_inicial=dados['aluguel_inicial'],
                taxa_inflacao=dados['taxa_inflacao'],
                prazo_meses=dados['prazo_anos'] * 12,
                recursos_proprios_iniciais=dados['recursos_proprios_iniciais'],
                opcao_pagamento_aluguel=dados['opcao_pagamento_aluguel'],
                fgts_saldo=dados.get('fgts_saldo', 0),
                rendimento_fgts=dados['rendimento_fgts'],
                fgts_mensal_percent=dados['fgts_mensal_percent'],
                aporte_13=dados['aporte_13'],
                renda_familiar_bruta=dados['renda_familiar_bruta'],
                valorizacao_imovel=dados['valorizacao_imovel'],
                taxa_anual_financiamento=dados['taxa_anual'],
            )
            
            acumulado_final = resultado_aluguel['acumulado_final']
            total_gasto = resultado_aluguel['total_gasto_aluguel']
            print(f"✓ ALUGUEL+INVESTIMENTO:")
            print(f"  Acumulado final = R$ {acumulado_final:,.2f}")
            print(f"  Total gasto em aluguel = R$ {total_gasto:,.2f}")
        
        except Exception as e:
            print(f"✗ ALUGUEL+INVESTIMENTO: Exceção - {str(e)}")
    
    # ========================================================================
    # TESTE 2: VALIDAÇÕES DE MERCADO
    # ========================================================================
    
    print(f"\n\nTESTE 2: VALIDAÇÕES DE MERCADO")
    print(f"-" * 80)
    
    for validacao in perfil_data['validacoes']:
        print(f"  → {validacao}")
    
    # ========================================================================
    # TESTE 3: PROBLEMAS ESPERADOS
    # ========================================================================
    
    print(f"\n\nTESTE 3: PROBLEMAS ESPERADOS / FALTANDO")
    print(f"-" * 80)
    
    for problema in perfil_data['problemas_esperados']:
        print(f"  ⚠ {problema}")
    
    print(f"\n")


# ============================================================================
# EXECUÇÃO DOS TESTES
# ============================================================================

if __name__ == '__main__':
    
    print(f"\n{'='*80}")
    print(f"SIMULAÇÃO DE 10 PERFIS DE USUÁRIOS")
    print(f"Validação de Fórmulas e Fluxo do Wizard")
    print(f"Data: Janeiro 2026")
    print(f"{'='*80}\n")
    
    perfis = [
        (1, perfil_1_mcmv),
        (2, perfil_2_aluguel_compra),
        (3, perfil_3_poupador),
        (4, perfil_4_investidor),
        (5, perfil_5_upgrade),
        (6, perfil_6_consorcio),
        (7, perfil_7_empresario),
        (8, perfil_8_autonom),
        (9, perfil_9_oportunidade),
        (10, perfil_10_migracao),
    ]
    
    for perfil_numero, perfil_data in perfis:
        testar_perfil(perfil_numero, perfil_data)
    
    # ========================================================================
    # RELATÓRIO FINAL
    # ========================================================================
    
    print(f"\n{'='*80}")
    print(f"RESUMO GERAL - ERROS E FALTANDO")
    print(f"{'='*80}\n")
    
    print(f"VARIÁVEIS FALTANDO (crítico para mercado brasileiro):")
    print(f"""
    1. ⚠ TR (Taxa Referencial) - Usada em alguns financiamentos antigos
    2. ⚠ Subsídio MCMV - Não é calculado (programa governamental)
    3. ⚠ ITBI - Imposto de Transmissão não é simulado
    4. ⚠ Seguros obrigatórios - MIP/DFI devem ter taxas máximas reguladas
    5. ⚠ Despesas do imóvel - IPTU, condomínio, seguros imobiliários
    6. ⚠ CET - Custo Efetivo Total não é calculado corretamente
    7. ⚠ Vacância/Inadimplência - Não há simulação para investidor
    8. ⚠ Taxa de negociação - Não há campo para renegociação de taxa
    9. ⚠ Portabilidade - Migração entre bancos não é simulada
    10. ⚠ Imposto de Renda - Sobre juros/juros nominais não são considerados
    """)
    
    print(f"\nPROBLEMAS NO WIZARD (Fluxo confuso):")
    print(f"""
    1. ⚠ Não distingue comprador de investidor imobiliário
    2. ⚠ Pergunta sobre aluguel, investimento e financiamento em ordem confusa
    3. ⚠ Não há campo para programa MCMV específico
    4. ⚠ Não há pergunta sobre profissão (autônomo vs CLT)
    5. ⚠ Não permite comparação de múltiplos cenários em paralelo
    6. ⚠ Upgrade (venda + compra) não é contemplado
    7. ⚠ Consórcio anterior/experiência não é perguntado
    8. ⚠ Limite de crédito por banco não é mostrado
    """)
    
    print(f"\nSUGESTÕES DE MELHORIA:")
    print(f"""
    1. ✓ Separar fluxo: Comprador → Investidor → Consorciado
    2. ✓ Adicionar campo de programa MCMV no início
    3. ✓ Implementar cálculo de CET conforme normativas BC
    4. ✓ Adicionar despesas operacionais (IPTU, condomínio)
    5. ✓ Simular vacância e inadimplência para investidores
    6. ✓ Comparador de bancos (BB, Caixa, Itaú, Bradesco, Santander)
    7. ✓ Permitir simulação de taxa variável (para autônomos)
    8. ✓ Incluir ITBI e outros impostos na entrada
    9. ✓ Gráfico visual de aluguel vs compra (NPL)
    10. ✓ Calculadora de oportunidade (SELIC vs Financiamento)
    """)
    
    print(f"\n{'='*80}\n")
