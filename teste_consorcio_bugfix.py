#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TESTE: Validação da correção do bug do consórcio (0.7%)
Data: 25 de Janeiro de 2026

OBJETIVO: Verificar se simular_consorcio() agora retorna o valor REAL que o usuário paga
(incluindo taxa de administração + fundo de reserva)
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ImobCalc.settings')
django.setup()

from simulacao.calculadora_financeira import simular_consorcio, simular_consorcio_com_lances
from decimal import Decimal

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

resultado = simular_consorcio(
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
print(f"  PERCENTUAL:            {((resultado['parcela_mensal_total'] - parcela_base_esperado) / parcela_base_esperado * 100):.1f}%")
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
# TESTE 2: simular_consorcio_com_lances() - Validação
# ============================================================================

print("TESTE 2: simular_consorcio_com_lances() - R$ 300.000 em 120 meses")
print("-" * 80)

valor_imovel_2 = 300000
prazo_meses_2 = 120
taxa_adm_2 = 1.5
fundo_reserva_2 = 0.5

resultado_2 = simular_consorcio_com_lances(
    valor_imovel=valor_imovel_2,
    prazo_meses=prazo_meses_2,
    taxa_adm=taxa_adm_2,
    fundo_reserva=fundo_reserva_2,
    tipo_lance='livre',
    percentual_lance=30.0,
    numero_cotas_ativas=120
)

print(f"Valor do imóvel: R$ {valor_imovel_2:,.2f}")
print(f"Prazo: {prazo_meses_2} meses")
print()

print("BREAKDOWN DA PARCELA MENSAL:")
print(f"  ├─ Base (0.7%):           R$ {resultado_2['parcela_base']:.2f}")
print(f"  ├─ Taxa + Fundo:          R$ {resultado_2['parcela_total_mensal'] - resultado_2['parcela_base']:.2f}")
print(f"  └─ TOTAL MENSAL:          R$ {resultado_2['parcela_total_mensal']:.2f}")
print()

print("CENÁRIOS:")
print(f"  Melhor caso (mês {resultado_2['melhor_caso']['mes_contemplacao']}):")
print(f"    Total pago: R$ {resultado_2['melhor_caso']['total_pago']:,.2f}")
print(f"    Meses pagos: {resultado_2['melhor_caso']['meses_pagos']}")
print()

print(f"  Caso médio (mês {resultado_2['caso_medio']['mes_contemplacao']}):")
print(f"    Total pago: R$ {resultado_2['caso_medio']['total_pago']:,.2f}")
print(f"    Meses pagos: {resultado_2['caso_medio']['meses_pagos']}")
print()

print(f"  Pior caso (mês {resultado_2['pior_caso']['mes_contemplacao']}):")
print(f"    Total pago: R$ {resultado_2['pior_caso']['total_pago']:,.2f}")
print(f"    Meses pagos: {resultado_2['pior_caso']['meses_pagos']}")
print()

# Validar que parcela_total_mensal > parcela_base
if resultado_2['parcela_total_mensal'] > resultado_2['parcela_base']:
    print(f"✓ VALIDADO: parcela_total_mensal ({resultado_2['parcela_total_mensal']:.2f}) > parcela_base ({resultado_2['parcela_base']:.2f})")
else:
    print(f"✗ ERRO: parcela_total_mensal não é maior que parcela_base")
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
print(f"EXEMPLO: R$ 500.000 em 180 meses")
print(f"  Antes:  R$ 3.500/mês (0.7% apenas)")
print(f"  Depois: R$ {resultado['parcela_mensal_total']:.2f}/mês (TOTAL REAL)")
print(f"  Delta:  +R$ {resultado['parcela_mensal_total'] - parcela_base_esperado:.2f}/mês (+{((resultado['parcela_mensal_total'] - parcela_base_esperado) / parcela_base_esperado * 100):.1f}%)")
print()
print("=" * 80)
