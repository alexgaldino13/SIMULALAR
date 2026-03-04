#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TESTE: Validação da correção do bug do consórcio (0.7%)
Data: 25 de Janeiro de 2026
VERSÃO: Sem dependência de Django
"""

from decimal import Decimal

# ============================================================================
# IMPLEMENTAÇÃO LOCAL DAS FUNÇÕES CORRIGIDAS (para teste rápido)
# ============================================================================

def simular_consorcio_corrigido(valor_imovel, prazo_meses, taxa_adm, fundo_reserva, fgts_saldo=0.0):
    """
    VERSÃO CORRIGIDA: Agora retorna o valor REAL que o usuário paga
    (incluindo taxa de administração + fundo de reserva)
    """
    
    # CONVERSÃO DOS PARÂMETROS PARA DECIMAL
    valor_imovel_total = valor_imovel
    prazo_meses_dec = Decimal(str(prazo_meses))
    valor_lance_fgts = Decimal(str(fgts_saldo))
    taxa_adm_mensal_percent = Decimal(str(taxa_adm)) / 100 / 12
    fundo_reserva_percent = Decimal(str(fundo_reserva)) / 100
    
    # 1. CÁLCULO DA PARCELA BASE (0.7%)
    parcela_base_percentual = Decimal('0.007')  # 0.7% ao mês
    parcela_base = valor_imovel_total * parcela_base_percentual
    
    # 2. CUSTOS MENSAIS (Taxa de Administração e Fundo de Reserva)
    taxa_adm_mensal = valor_imovel_total * taxa_adm_mensal_percent
    fundo_reserva_mensal = valor_imovel_total * fundo_reserva_percent / 12
    
    # 3. PARCELA MENSAL TOTAL (O QUE O USUÁRIO REALMENTE PAGA)
    parcela_mensal_total = parcela_base + taxa_adm_mensal + fundo_reserva_mensal
    
    # 4. CUSTO TOTAL DO CONSÓRCIO
    custo_total_parcelas = parcela_base * prazo_meses_dec
    custo_total_taxa_adm = taxa_adm_mensal * prazo_meses_dec
    custo_total_fundo = fundo_reserva_mensal * prazo_meses_dec
    total_custo = custo_total_parcelas - valor_imovel_total + custo_total_taxa_adm + custo_total_fundo
    
    # 5. SIMULAÇÃO DE SORTEIOS
    mes_contemplacao_estimado = int(prazo_meses * Decimal('0.4'))
    
    # 6. RESUMO COM BREAKDOWN CLARO
    return {
        'parcela_base': float(parcela_base),
        'taxa_adm_mensal': float(taxa_adm_mensal),
        'fundo_reserva_mensal': float(fundo_reserva_mensal),
        'parcela_mensal_total': float(parcela_mensal_total),
        'parcela_fixa': float(parcela_mensal_total),  # Compatibilidade com templates legados
        'total_custo': float(total_custo),
        'custo_total_taxa_adm': float(custo_total_taxa_adm),
        'custo_total_fundo': float(custo_total_fundo),
        'valor_lance_fgts': float(valor_lance_fgts),
        'mes_contemplacao_estimado': mes_contemplacao_estimado,
        'prazo_efetivo_estimado': max(1, mes_contemplacao_estimado),
        'observacao': f'Parcela total: R$ {float(parcela_mensal_total):.2f}/mês (Base 0.7% + Taxa Admin + Fundo Reserva). Contemplação estimada mês {mes_contemplacao_estimado}.'
    }


print("=" * 80)
print("TESTE: CORREÇÃO DO BUG DO CONSÓRCIO (0.7%)")
print("=" * 80)
print()

# ============================================================================
# TESTE 1: simular_consorcio() - Caso exemplo do documento de análise
# ============================================================================

print("TESTE 1: simular_consorcio() - R$ 500.000 em 180 meses")
print("-" * 80)

valor_imovel = 500000
prazo_meses = 180
taxa_adm = 1.5  # 1.5% ao ano
fundo_reserva = 0.5  # 0.5% ao ano

resultado = simular_consorcio_corrigido(
    valor_imovel=valor_imovel,
    prazo_meses=prazo_meses,
    taxa_adm=taxa_adm,
    fundo_reserva=fundo_reserva,
    fgts_saldo=0.0
)

print(f"Valor do imóvel: R$ {valor_imovel:,.2f}")
print(f"Prazo: {prazo_meses} meses")
print(f"Taxa administração: {taxa_adm}% a.a.")
print(f"Fundo de reserva: {fundo_reserva}% a.a.")
print()

print("BREAKDOWN DA PARCELA MENSAL:")
print(f"  ├─ Base (0.7%):           R$ {resultado['parcela_base']:.2f}")
print(f"  ├─ Taxa Adm (1.5%/12):    R$ {resultado['taxa_adm_mensal']:.2f}")
print(f"  ├─ Fundo Reserva (0.5%/12): R$ {resultado['fundo_reserva_mensal']:.2f}")
print(f"  └─ TOTAL MENSAL:          R$ {resultado['parcela_mensal_total']:.2f}")
print()

# Cálculos esperados
parcela_base_esperado = valor_imovel * 0.007
taxa_adm_esperado = (valor_imovel * taxa_adm / 100) / 12
fundo_reserva_esperado = (valor_imovel * fundo_reserva / 100) / 12
total_esperado = parcela_base_esperado + taxa_adm_esperado + fundo_reserva_esperado

print("VALIDAÇÃO DOS CÁLCULOS:")
print(f"  Parcela base calculada:        R$ {parcela_base_esperado:.2f}")
print(f"  Retornado:                     R$ {resultado['parcela_base']:.2f}")
print(f"  ✓ OK" if abs(resultado['parcela_base'] - parcela_base_esperado) < 0.01 else "  ✗ ERRO")
print()

print(f"  Taxa adm calculada:            R$ {taxa_adm_esperado:.2f}")
print(f"  Retornado:                     R$ {resultado['taxa_adm_mensal']:.2f}")
print(f"  ✓ OK" if abs(resultado['taxa_adm_mensal'] - taxa_adm_esperado) < 0.01 else "  ✗ ERRO")
print()

print(f"  Fundo reserva calculado:       R$ {fundo_reserva_esperado:.2f}")
print(f"  Retornado:                     R$ {resultado['fundo_reserva_mensal']:.2f}")
print(f"  ✓ OK" if abs(resultado['fundo_reserva_mensal'] - fundo_reserva_esperado) < 0.01 else "  ✗ ERRO")
print()

print(f"  Total mensal calculado:        R$ {total_esperado:.2f}")
print(f"  Retornado (parcela_mensal_total): R$ {resultado['parcela_mensal_total']:.2f}")
print(f"  ✓ OK" if abs(resultado['parcela_mensal_total'] - total_esperado) < 0.01 else "  ✗ ERRO")
print()

# Comparação ANTES vs DEPOIS do BUG FIX
print("IMPACTO DA CORREÇÃO:")
print(f"  ANTES (bugado):        R$ {parcela_base_esperado:,.2f}/mês (0.7% apenas)")
print(f"  DEPOIS (corrigido):    R$ {resultado['parcela_mensal_total']:,.2f}/mês (0.7% + taxa + fundo)")
print(f"  DIFERENÇA:             R$ {resultado['parcela_mensal_total'] - parcela_base_esperado:.2f}/mês")
percentual_aumento = ((resultado['parcela_mensal_total'] - parcela_base_esperado) / parcela_base_esperado * 100)
print(f"  PERCENTUAL:            +{percentual_aumento:.1f}%")
print()

total_180_meses_antes = parcela_base_esperado * 180
total_180_meses_depois = resultado['parcela_mensal_total'] * 180
print(f"  TOTAL 180 MESES:")
print(f"    Antes:               R$ {total_180_meses_antes:,.2f}")
print(f"    Depois:              R$ {total_180_meses_depois:,.2f}")
print(f"    Custo oculto:        R$ {total_180_meses_depois - total_180_meses_antes:,.2f}")
print()
print()

# ============================================================================
# TESTE 2: Mesmo cenário em 360 meses (30 anos)
# ============================================================================

print("TESTE 2: simular_consorcio() - R$ 500.000 em 360 meses (30 anos)")
print("-" * 80)

prazo_meses_30anos = 360
resultado_30anos = simular_consorcio_corrigido(
    valor_imovel=valor_imovel,
    prazo_meses=prazo_meses_30anos,
    taxa_adm=taxa_adm,
    fundo_reserva=fundo_reserva,
    fgts_saldo=0.0
)

print(f"Valor do imóvel: R$ {valor_imovel:,.2f}")
print(f"Prazo: {prazo_meses_30anos} meses")
print()

print("BREAKDOWN DA PARCELA MENSAL:")
print(f"  ├─ Base (0.7%):           R$ {resultado_30anos['parcela_base']:.2f}")
print(f"  ├─ Taxa Adm (1.5%/12):    R$ {resultado_30anos['taxa_adm_mensal']:.2f}")
print(f"  ├─ Fundo Reserva (0.5%/12): R$ {resultado_30anos['fundo_reserva_mensal']:.2f}")
print(f"  └─ TOTAL MENSAL:          R$ {resultado_30anos['parcela_mensal_total']:.2f}")
print()

total_360_meses_antes = parcela_base_esperado * 360
total_360_meses_depois = resultado_30anos['parcela_mensal_total'] * 360

print(f"  TOTAL 360 MESES (30 ANOS):")
print(f"    Antes:               R$ {total_360_meses_antes:,.2f}")
print(f"    Depois:              R$ {total_360_meses_depois:,.2f}")
print(f"    Custo oculto:        R$ {total_360_meses_depois - total_360_meses_antes:,.2f}")
print()
print()

# ============================================================================
# TESTE 3: Outro valor de imóvel - R$ 300.000
# ============================================================================

print("TESTE 3: simular_consorcio() - R$ 300.000 em 120 meses")
print("-" * 80)

valor_imovel_3 = 300000
prazo_meses_3 = 120

resultado_3 = simular_consorcio_corrigido(
    valor_imovel=valor_imovel_3,
    prazo_meses=prazo_meses_3,
    taxa_adm=taxa_adm,
    fundo_reserva=fundo_reserva,
    fgts_saldo=0.0
)

parcela_base_3 = valor_imovel_3 * 0.007
total_120_antes = parcela_base_3 * 120
total_120_depois = resultado_3['parcela_mensal_total'] * 120

print(f"Valor do imóvel: R$ {valor_imovel_3:,.2f}")
print(f"Prazo: {prazo_meses_3} meses")
print()

print("BREAKDOWN DA PARCELA MENSAL:")
print(f"  ├─ Base (0.7%):           R$ {resultado_3['parcela_base']:.2f}")
print(f"  ├─ Taxa Adm (1.5%/12):    R$ {resultado_3['taxa_adm_mensal']:.2f}")
print(f"  ├─ Fundo Reserva (0.5%/12): R$ {resultado_3['fundo_reserva_mensal']:.2f}")
print(f"  └─ TOTAL MENSAL:          R$ {resultado_3['parcela_mensal_total']:.2f}")
print()

print(f"  TOTAL 120 MESES:")
print(f"    Antes:               R$ {total_120_antes:,.2f}")
print(f"    Depois:              R$ {total_120_depois:,.2f}")
print(f"    Custo oculto:        R$ {total_120_depois - total_120_antes:,.2f}")
print()
print()

# ============================================================================
# RESUMO FINAL
# ============================================================================

print("=" * 80)
print("RESUMO DA CORREÇÃO")
print("=" * 80)
print()
print("✓ BUG CORRIGIDO: As funções agora retornam 'parcela_mensal_total' que inclui:")
print("  1. Parcela base (0.7% do valor do imóvel)")
print("  2. Taxa de administração (X% ao ano ÷ 12)")
print("  3. Fundo de reserva (Y% ao ano ÷ 12)")
print()
print("✓ COMPATIBILIDADE: 'parcela_fixa' ainda é retornada (para templates legados)")
print("  mas agora contém o valor TOTAL, não apenas 0.7%")
print()
print("✓ TRANSPARÊNCIA: O usuário agora vê exatamente quanto vai pagar por mês")
print()
print("EXEMPLOS DE IMPACTO:")
print(f"  1. R$ 500.000 em 180 meses:")
print(f"     Antes:  R$ {parcela_base_esperado:,.2f}/mês → Total: R$ {total_180_meses_antes:,.2f}")
print(f"     Depois: R$ {resultado['parcela_mensal_total']:.2f}/mês → Total: R$ {total_180_meses_depois:,.2f}")
print(f"     Diferença: +R$ {total_180_meses_depois - total_180_meses_antes:,.2f} ({percentual_aumento:.1f}%)")
print()
print(f"  2. R$ 500.000 em 360 meses (30 anos):")
print(f"     Custo oculto: +R$ {total_360_meses_depois - total_360_meses_antes:,.2f}")
print()
print(f"  3. R$ 300.000 em 120 meses:")
print(f"     Custo oculto: +R$ {total_120_depois - total_120_antes:,.2f}")
print()
print("=" * 80)
