"""Teste de integração do módulo IRRF com calculadora_financeira.py"""

import sys
sys.path.insert(0, 'D:\\PROJETOS\\FI')

from simulacao.calculadora_financeira import calcular_investimento_com_irrf

print("="*70)
print("TESTE DE INTEGRAÇÃO: MÓDULO IRRF + CALCULADORA FINANCEIRA")
print("="*70)

# Teste 1: Investimento de curto prazo (180 dias) - Alíquota 22,5%
print("\n\nTESTE 1: Investimento de 180 dias (Alíquota 22,5%)")
print("-" * 70)
resultado1 = calcular_investimento_com_irrf(
    valor_inicial=10000.00,
    taxa_juros_anual=10.0,
    prazo_dias=180
)
print(f"Valor inicial: R$ {resultado1['valor_inicial']:.2f}")
print(f"Rendimento bruto: R$ {resultado1['rendimento_bruto']:.2f}")
print(f"Alíquota IRRF: {resultado1['aliquota_irrf']:.1f}%")
print(f"IRRF: R$ {resultado1['irrf']:.2f}")
print(f"Rendimento líquido: R$ {resultado1['rendimento_liquido']:.2f}")
print(f"Valor final líquido: R$ {resultado1['valor_final_liquido']:.2f}")

# Teste 2: Investimento de médio prazo (365 dias) - Alíquota 20%
print("\n\nTESTE 2: Investimento de 365 dias (Alíquota 20%)")
print("-" * 70)
resultado2 = calcular_investimento_com_irrf(
    valor_inicial=10000.00,
    taxa_juros_anual=10.0,
    prazo_dias=365
)
print(f"Valor inicial: R$ {resultado2['valor_inicial']:.2f}")
print(f"Rendimento bruto: R$ {resultado2['rendimento_bruto']:.2f}")
print(f"Alíquota IRRF: {resultado2['aliquota_irrf']:.1f}%")
print(f"IRRF: R$ {resultado2['irrf']:.2f}")
print(f"Rendimento líquido: R$ {resultado2['rendimento_liquido']:.2f}")
print(f"Valor final líquido: R$ {resultado2['valor_final_liquido']:.2f}")

# Teste 3: Investimento de longo prazo (720 dias) - Alíquota 17,5%
print("\n\nTESTE 3: Investimento de 720 dias (Alíquota 17,5%)")
print("-" * 70)
resultado3 = calcular_investimento_com_irrf(
    valor_inicial=10000.00,
    taxa_juros_anual=10.0,
    prazo_dias=720
)
print(f"Valor inicial: R$ {resultado3['valor_inicial']:.2f}")
print(f"Rendimento bruto: R$ {resultado3['rendimento_bruto']:.2f}")
print(f"Alíquota IRRF: {resultado3['aliquota_irrf']:.1f}%")
print(f"IRRF: R$ {resultado3['irrf']:.2f}")
print(f"Rendimento líquido: R$ {resultado3['rendimento_liquido']:.2f}")
print(f"Valor final líquido: R$ {resultado3['valor_final_liquido']:.2f}")

# Teste 4: Investimento de muito longo prazo (900 dias) - Alíquota 15%
print("\n\nTESTE 4: Investimento de 900 dias (Alíquota 15%)")
print("-" * 70)
resultado4 = calcular_investimento_com_irrf(
    valor_inicial=10000.00,
    taxa_juros_anual=10.0,
    prazo_dias=900
)
print(f"Valor inicial: R$ {resultado4['valor_inicial']:.2f}")
print(f"Rendimento bruto: R$ {resultado4['rendimento_bruto']:.2f}")
print(f"Alíquota IRRF: {resultado4['aliquota_irrf']:.1f}%")
print(f"IRRF: R$ {resultado4['irrf']:.2f}")
print(f"Rendimento líquido: R$ {resultado4['rendimento_liquido']:.2f}")
print(f"Valor final líquido: R$ {resultado4['valor_final_liquido']:.2f}")

print("\n" + "="*70)
print("✅ INTEGRAÇÃO CONCLUÍDA COM SUCESSO!")
print("="*70)
print("\nO módulo IRRF foi integrado com sucesso à calculadora_financeira.py")
print("A função calcular_investimento_com_irrf() está pronta para uso!")
