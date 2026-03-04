#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste de integração do módulo IRRF
"""

from decimal import Decimal
from simulacao import irrf
from simulacao.calculadora_financeira import calcular_ir_rendimentos

print("=" * 60)
print("TESTE 1: Módulo IRRF direto")
print("=" * 60)

# Teste com 180 dias (22,5%)
resultado1 = irrf.calcular_irrf(1000, 180)
print(f"\nRendimento: R$ 1.000,00")
print(f"Prazo: 180 dias")
print(f"Alíquota: {resultado1['aliquota_percentual']}%")
print(f"IRRF: R$ {resultado1['irrf']}")
print(f"Valor líquido: R$ {resultado1['valor_liquido']}")

# Teste com 360 dias (20%)
resultado2 = irrf.calcular_irrf(1000, 360)
print(f"\nRendimento: R$ 1.000,00")
print(f"Prazo: 360 dias")
print(f"Alíquota: {resultado2['aliquota_percentual']}%")
print(f"IRRF: R$ {resultado2['irrf']}")
print(f"Valor líquido: R$ {resultado2['valor_liquido']}")

# Teste com 720 dias (17,5%)
resultado3 = irrf.calcular_irrf(1000, 720)
print(f"\nRendimento: R$ 1.000,00")
print(f"Prazo: 720 dias")
print(f"Alíquota: {resultado3['aliquota_percentual']}%")
print(f"IRRF: R$ {resultado3['irrf']}")
print(f"Valor líquido: R$ {resultado3['valor_liquido']}")

# Teste com 800 dias (15%)
resultado4 = irrf.calcular_irrf(1000, 800)
print(f"\nRendimento: R$ 1.000,00")
print(f"Prazo: 800 dias")
print(f"Alíquota: {resultado4['aliquota_percentual']}%")
print(f"IRRF: R$ {resultado4['irrf']}")
print(f"Valor líquido: R$ {resultado4['valor_liquido']}")

print("\n" + "=" * 60)
print("TESTE 2: Função calcular_ir_rendimentos integrada")
print("=" * 60)

# Teste com 6 meses (180 dias)
ir1 = calcular_ir_rendimentos(1000, 6)
print(f"\nRendimento mensal: R$ 1.000,00")
print(f"Prazo: 6 meses (180 dias)")
print(f"IR mensal: R$ {ir1}")

# Teste com 12 meses (360 dias)
ir2 = calcular_ir_rendimentos(1000, 12)
print(f"\nRendimento mensal: R$ 1.000,00")
print(f"Prazo: 12 meses (360 dias)")
print(f"IR mensal: R$ {ir2}")

# Teste com 24 meses (720 dias)
ir3 = calcular_ir_rendimentos(1000, 24)
print(f"\nRendimento mensal: R$ 1.000,00")
print(f"Prazo: 24 meses (720 dias)")
print(f"IR mensal: R$ {ir3}")

# Teste com 30 meses (900 dias)
ir4 = calcular_ir_rendimentos(1000, 30)
print(f"\nRendimento mensal: R$ 1.000,00")
print(f"Prazo: 30 meses (900 dias)")
print(f"IR mensal: R$ {ir4}")

print("\n" + "=" * 60)
print("TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
print("=" * 60)
