#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste simples do módulo IRRF
"""

from decimal import Decimal
from simulacao import irrf

print("=" * 70)
print("TESTE DO MÓDULO IRRF - Cálculo de Imposto de Renda sobre Investimentos")
print("=" * 70)

# Teste 1: 180 dias (22,5%)
print("\n" + "-" * 70)
print("TESTE 1: Aplicação de 180 dias (alíquota de 22,5%)")
print("-" * 70)
rendimento = 1000
dias = 180
resultado = irrf.calcular_irrf(rendimento, dias)
print(f"Rendimento bruto: R$ {rendimento:,.2f}")
print(f"Prazo: {dias} dias")
print(f"Alíquota: {resultado['aliquota_percentual']}%")
print(f"IRRF: R$ {float(resultado['irrf']):,.2f}")
print(f"Rendimento líquido: R$ {float(resultado['valor_liquido']):,.2f}")

# Teste 2: 360 dias (20%)
print("\n" + "-" * 70)
print("TESTE 2: Aplicação de 360 dias (alíquota de 20%)")
print("-" * 70)
rendimento = 1000
dias = 360
resultado = irrf.calcular_irrf(rendimento, dias)
print(f"Rendimento bruto: R$ {rendimento:,.2f}")
print(f"Prazo: {dias} dias")
print(f"Alíquota: {resultado['aliquota_percentual']}%")
print(f"IRRF: R$ {float(resultado['irrf']):,.2f}")
print(f"Rendimento líquido: R$ {float(resultado['valor_liquido']):,.2f}")

# Teste 3: 720 dias (17,5%)
print("\n" + "-" * 70)
print("TESTE 3: Aplicação de 720 dias (alíquota de 17,5%)")
print("-" * 70)
rendimento = 1000
dias = 720
resultado = irrf.calcular_irrf(rendimento, dias)
print(f"Rendimento bruto: R$ {rendimento:,.2f}")
print(f"Prazo: {dias} dias")
print(f"Alíquota: {resultado['aliquota_percentual']}%")
print(f"IRRF: R$ {float(resultado['irrf']):,.2f}")
print(f"Rendimento líquido: R$ {float(resultado['valor_liquido']):,.2f}")

# Teste 4: 900 dias (15%)
print("\n" + "-" * 70)
print("TESTE 4: Aplicação de 900 dias (alíquota de 15%)")
print("-" * 70)
rendimento = 1000
dias = 900
resultado = irrf.calcular_irrf(rendimento, dias)
print(f"Rendimento bruto: R$ {rendimento:,.2f}")
print(f"Prazo: {dias} dias")
print(f"Alíquota: {resultado['aliquota_percentual']}%")
print(f"IRRF: R$ {float(resultado['irrf']):,.2f}")
print(f"Rendimento líquido: R$ {float(resultado['valor_liquido']):,.2f}")

# Teste 5: Cálculo completo com rendimento
print("\n" + "-" * 70)
print("TESTE 5: Cálculo completo de investimento com IRRF")
print("-" * 70)
valor_inicial = 10000
taxa_juros = 0.01  # 1% ao mês
dias = 365
resultado_completo = irrf.calcular_rendimento_com_irrf(valor_inicial, taxa_juros, dias)
print(f"Valor inicial: R$ {valor_inicial:,.2f}")
print(f"Taxa de juros: {taxa_juros * 100}% ao mês")
print(f"Prazo: {dias} dias")
print(f"Rendimento bruto: R$ {float(resultado_completo['rendimento_bruto']):,.2f}")
print(f"IRRF ({resultado_completo['aliquota_percentual']}%): R$ {float(resultado_completo['irrf']):,.2f}")
print(f"Rendimento líquido: R$ {float(resultado_completo['rendimento_liquido']):,.2f}")
print(f"Valor final líquido: R$ {float(resultado_completo['valor_final_liquido']):,.2f}")

print("\n" + "=" * 70)
print("✓ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
print("=" * 70)
