"""
Teste da função guardar_dinheiro()
Simula 3 cenários reais de poupança
"""

import sys
sys.path.insert(0, r'd:\PROJETOS\FI')

from simulacao.calculadora_financeira import guardar_dinheiro
import json

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

print("=" * 80)
print("TESTE: FUNÇÃO guardar_dinheiro()")
print("=" * 80)

# CENÁRIO 1: Cenário Conservador (Poupança Real com 0.5% a.a. = 0.0417% a.m.)
print("\n\n📊 CENÁRIO 1: CONSERVADOR (Poupança Real - 0.5% a.a.)")
print("-" * 80)

resultado_1 = guardar_dinheiro(
    valor_imovel=500000,                          # Imóvel de R$ 500k
    valor_entrada_inicial=100000,                 # 20% = R$ 100k
    valor_mensal_guardar=3000,                    # Poupar R$ 3.000/mês
    valor_aluguel=2500,                           # Aluguel de R$ 2.500/mês
    taxa_rendimento_mensal=0.00417,               # 0.5% a.a. = 0.0417% a.m.
    prazo_meses=360,                              # 30 anos
    taxa_reajuste_aluguel_anual=0.06,             # Reajuste 6% ao ano
    fgts_saldo_inicial=15000,                     # Tem R$ 15k de FGTS
    renda_familiar_bruta=8000,                    # Renda de R$ 8k/mês
    fgts_mensal_percent=8.0                       # 8% da renda = R$ 640/mês
)

print(f"✓ Imóvel: {formatar_moeda(500000)}")
print(f"✓ Entrada necessária: {formatar_moeda(100000)}")
print(f"✓ Poupança mensal: {formatar_moeda(3000)}")
print(f"✓ Aluguel inicial: {formatar_moeda(2500)}")
print(f"\n📈 RESULTADOS:")
print(f"  Conseguiu guardar? {resultado_1['viavel']}")
if resultado_1['viavel']:
    print(f"  ⏰ Tempo para comprar: {resultado_1['tempo_para_comprar_anos']} anos e {resultado_1['tempo_para_comprar_meses']} meses")
    print(f"  💰 Capital final: {formatar_moeda(resultado_1['capital_final'])}")
    print(f"     - Poupança: {formatar_moeda(resultado_1['poupanca_final'])}")
    print(f"     - FGTS: {formatar_moeda(resultado_1['fgts_final'])}")
else:
    print(f"  ❌ Não conseguiu em 30 anos")
    print(f"  💰 Capital final: {formatar_moeda(resultado_1['capital_final'])}")

print(f"  📊 Total gasto com aluguel: {formatar_moeda(resultado_1['total_aluguel_pago'])}")
print(f"  📝 Total guardado: {formatar_moeda(resultado_1['total_guardado'])}")


# CENÁRIO 2: Cenário Agressivo (Aplicação CDI - 10% a.a.)
print("\n\n📊 CENÁRIO 2: AGRESSIVO (CDI 10% a.a.)")
print("-" * 80)

resultado_2 = guardar_dinheiro(
    valor_imovel=400000,
    valor_entrada_inicial=80000,                  # 20%
    valor_mensal_guardar=5000,                    # Mais agressivo
    valor_aluguel=2000,
    taxa_rendimento_mensal=0.00797,               # 10% a.a. ≈ 0.797% a.m.
    prazo_meses=360,
    taxa_reajuste_aluguel_anual=0.06,
    fgts_saldo_inicial=20000,
    renda_familiar_bruta=10000,
    fgts_mensal_percent=8.0
)

print(f"✓ Imóvel: {formatar_moeda(400000)}")
print(f"✓ Entrada necessária: {formatar_moeda(80000)}")
print(f"✓ Poupança mensal: {formatar_moeda(5000)}")
print(f"✓ Aluguel inicial: {formatar_moeda(2000)}")
print(f"\n📈 RESULTADOS:")
print(f"  Conseguiu guardar? {resultado_2['viavel']}")
if resultado_2['viavel']:
    print(f"  ⏰ Tempo para comprar: {resultado_2['tempo_para_comprar_anos']} anos e {resultado_2['tempo_para_comprar_meses']} meses")
    print(f"  💰 Capital final: {formatar_moeda(resultado_2['capital_final'])}")
    print(f"     - Poupança: {formatar_moeda(resultado_2['poupanca_final'])}")
    print(f"     - FGTS: {formatar_moeda(resultado_2['fgts_final'])}")
else:
    print(f"  ❌ Não conseguiu em 30 anos")

print(f"  📊 Total gasto com aluguel: {formatar_moeda(resultado_2['total_aluguel_pago'])}")
print(f"  📝 Total guardado: {formatar_moeda(resultado_2['total_guardado'])}")


# CENÁRIO 3: Cenário Ultra-Conservador (Quem tem pouca renda)
print("\n\n📊 CENÁRIO 3: MICRO-POUPANÇA (Quem tem renda baixa)")
print("-" * 80)

resultado_3 = guardar_dinheiro(
    valor_imovel=200000,                          # Imóvel mais barato
    valor_entrada_inicial=40000,                  # 20%
    valor_mensal_guardar=800,                     # Poupar apenas R$ 800/mês
    valor_aluguel=1200,                           # Aluguel menor
    taxa_rendimento_mensal=0.00041,               # 0.5% a.a.
    prazo_meses=360,
    taxa_reajuste_aluguel_anual=0.05,
    fgts_saldo_inicial=5000,                      # Pouco FGTS
    renda_familiar_bruta=3500,                    # Renda baixa
    fgts_mensal_percent=8.0
)

print(f"✓ Imóvel: {formatar_moeda(200000)}")
print(f"✓ Entrada necessária: {formatar_moeda(40000)}")
print(f"✓ Poupança mensal: {formatar_moeda(800)}")
print(f"✓ Aluguel inicial: {formatar_moeda(1200)}")
print(f"\n📈 RESULTADOS:")
print(f"  Conseguiu guardar? {resultado_3['viavel']}")
if resultado_3['viavel']:
    print(f"  ⏰ Tempo para comprar: {resultado_3['tempo_para_comprar_anos']} anos e {resultado_3['tempo_para_comprar_meses']} meses")
    print(f"  💰 Capital final: {formatar_moeda(resultado_3['capital_final'])}")
else:
    print(f"  ❌ Não conseguiu em 30 anos (necessitaria 40+ anos)")
    print(f"  💰 Capital após 30 anos: {formatar_moeda(resultado_3['capital_final'])}")

print(f"  📊 Total gasto com aluguel: {formatar_moeda(resultado_3['total_aluguel_pago'])}")


# COMPARATIVO SIMPLIFICADO
print("\n\n" + "=" * 80)
print("📊 COMPARATIVO RESUMIDO")
print("=" * 80)

print(f"\n{'Cenário':<30} {'Tempo':<20} {'Custo Aluguel':<20} {'Capital Final':<20}")
print("-" * 80)

if resultado_1['viavel']:
    tempo_1 = f"{resultado_1['tempo_para_comprar_anos']}a {resultado_1['tempo_para_comprar_meses']}m"
else:
    tempo_1 = "30+ anos"

if resultado_2['viavel']:
    tempo_2 = f"{resultado_2['tempo_para_comprar_anos']}a {resultado_2['tempo_para_comprar_meses']}m"
else:
    tempo_2 = "30+ anos"

if resultado_3['viavel']:
    tempo_3 = f"{resultado_3['tempo_para_comprar_anos']}a {resultado_3['tempo_para_comprar_meses']}m"
else:
    tempo_3 = "30+ anos"

print(f"{'Conservador (R$3k/mês)':<30} {tempo_1:<20} {formatar_moeda(resultado_1['total_aluguel_pago']):<20} {formatar_moeda(resultado_1['capital_final']):<20}")
print(f"{'Agressivo (R$5k/mês)':<30} {tempo_2:<20} {formatar_moeda(resultado_2['total_aluguel_pago']):<20} {formatar_moeda(resultado_2['capital_final']):<20}")
print(f"{'Micro-Poupança (R$800/mês)':<30} {tempo_3:<20} {formatar_moeda(resultado_3['total_aluguel_pago']):<20} {formatar_moeda(resultado_3['capital_final']):<20}")

print("\n" + "=" * 80)
print("✅ TESTE CONCLUÍDO COM SUCESSO")
print("=" * 80)
