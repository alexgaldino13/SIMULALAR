"""
Teste da função simular_consorcio_com_lances()
Simula cenários reais de consórcio com diferentes tipos de lances
"""

import sys
sys.path.insert(0, r'd:\PROJETOS\FI')

from simulacao.calculadora_financeira import simular_consorcio_com_lances
import json

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_tabela_cenario(tabela, limite_linhas=12):
    """Exibe apenas as primeiras linhas da tabela + últimas linhas"""
    print("\n  Mês │ Parcela      │ Status         │ Detalhes")
    print("  ────┼──────────────┼────────────────┼────────────────────────")
    
    if len(tabela) <= limite_linhas:
        for linha in tabela:
            status = "✅ CONTEMPLADO" if linha['contemplado'] else f"  {linha['status'].upper()}"
            print(f"  {linha['mes']:3d} │ {formatar_moeda(linha['parcela']):12s} │ {status:<14s} │")
    else:
        # Mostra primeiras linhas
        for linha in tabela[:5]:
            status = "✅ CONTEMPLADO" if linha['contemplado'] else f"  {linha['status'].upper()}"
            print(f"  {linha['mes']:3d} │ {formatar_moeda(linha['parcela']):12s} │ {status:<14s} │")
        
        # Linha de intervalo
        print(f"  ... │ (omitido)    │ ...            │ ({len(tabela) - 10} linhas)")
        
        # Últimas linhas
        for linha in tabela[-5:]:
            status = "✅ CONTEMPLADO" if linha['contemplado'] else f"  {linha['status'].upper()}"
            print(f"  {linha['mes']:3d} │ {formatar_moeda(linha['parcela']):12s} │ {status:<14s} │")

print("=" * 100)
print("TESTE: FUNÇÃO simular_consorcio_com_lances()")
print("=" * 100)

# CENÁRIO 1: LANCE LIVRE (o consorciado oferece valor)
print("\n\n📊 CENÁRIO 1: LANCE LIVRE (30% do imóvel)")
print("-" * 100)

resultado_1 = simular_consorcio_com_lances(
    valor_imovel=300000,
    prazo_meses=120,                    # 10 anos
    taxa_adm=2.0,                       # 2% ao ano
    fundo_reserva=1.0,                  # 1%
    tipo_lance='livre',
    percentual_lance=30.0,              # 30% = R$ 90.000
    taxa_sobre_lance=0.5,               # Taxa de 0.5% sobre o lance
    numero_cotas_ativas=120,
    probabilidade_sorteio='normal'
)

print(f"✓ Imóvel: {formatar_moeda(resultado_1['valor_imovel'])}")
print(f"✓ Parcela mensal (sem lance): {formatar_moeda(resultado_1['parcela_total_mensal'])}")
print(f"✓ Valor do lance: {formatar_moeda(resultado_1['valor_lance'])}")
print(f"✓ Taxa sobre lance: {resultado_1['taxa_sobre_lance']:.2f}%")

print(f"\n🎯 MELHOR CASO (Contemplado no mês {resultado_1['melhor_caso']['mes_contemplacao']})")
print(f"  Total pago: {formatar_moeda(resultado_1['melhor_caso']['total_pago'])}")
print(f"  Meses pagos: {resultado_1['melhor_caso']['meses_pagos']}")
print(f"  Economizado: {formatar_moeda(resultado_1['melhor_caso']['economizado'])}")
formatar_tabela_cenario(resultado_1['melhor_caso']['tabela'])

print(f"\n📊 CASO MÉDIO (Contemplado no mês {resultado_1['caso_medio']['mes_contemplacao']})")
print(f"  Total pago: {formatar_moeda(resultado_1['caso_medio']['total_pago'])}")
print(f"  Meses pagos: {resultado_1['caso_medio']['meses_pagos']}")
print(f"  Economizado: {formatar_moeda(resultado_1['caso_medio']['economizado'])}")
formatar_tabela_cenario(resultado_1['caso_medio']['tabela'])

print(f"\n😱 PIOR CASO (Contemplado no mês {resultado_1['pior_caso']['mes_contemplacao']})")
print(f"  Total pago: {formatar_moeda(resultado_1['pior_caso']['total_pago'])}")
print(f"  Meses pagos: {resultado_1['pior_caso']['meses_pagos']}")
print(f"  Economizado: {formatar_moeda(resultado_1['pior_caso']['economizado'])}")

print(f"\n💡 ANÁLISE:")
print(f"  Diferença entre melhor e pior: {formatar_moeda(resultado_1['diferenca_melhor_pior'])}")
print(f"  Economia esperada com lance: {formatar_moeda(resultado_1['economia_esperada'])}")
print(f"  Recomendação: {resultado_1['recomendacao']}")


# CENÁRIO 2: LANCE FIXO (administradora define)
print("\n\n" + "=" * 100)
print("📊 CENÁRIO 2: LANCE FIXO (25% ao mês - Administradora Define)")
print("-" * 100)

resultado_2 = simular_consorcio_com_lances(
    valor_imovel=450000,
    prazo_meses=120,
    taxa_adm=2.0,
    fundo_reserva=1.0,
    tipo_lance='fixo',
    percentual_lance=25.0,              # 25% fixo = R$ 112.500
    taxa_sobre_lance=0.0,               # Sem taxa adicional
    numero_cotas_ativas=120,
    probabilidade_sorteio='otimista'    # Topo 10% = melhor chance
)

print(f"✓ Imóvel: {formatar_moeda(resultado_2['valor_imovel'])}")
print(f"✓ Parcela mensal (sem lance): {formatar_moeda(resultado_2['parcela_total_mensal'])}")
print(f"✓ Lance fixo mensal: {formatar_moeda(resultado_2['valor_lance'])}")

print(f"\n🎯 MELHOR CASO (Contemplado no mês {resultado_2['melhor_caso']['mes_contemplacao']})")
print(f"  Total pago: {formatar_moeda(resultado_2['melhor_caso']['total_pago'])}")
print(f"  Meses pagos: {resultado_2['melhor_caso']['meses_pagos']}")

print(f"\n📊 CASO MÉDIO (Contemplado no mês {resultado_2['caso_medio']['mes_contemplacao']})")
print(f"  Total pago: {formatar_moeda(resultado_2['caso_medio']['total_pago'])}")
print(f"  Meses pagos: {resultado_2['caso_medio']['meses_pagos']}")

print(f"\n😱 PIOR CASO (Contemplado no mês {resultado_2['pior_caso']['mes_contemplacao']})")
print(f"  Total pago: {formatar_moeda(resultado_2['pior_caso']['total_pago'])}")
print(f"  Meses pagos: {resultado_2['pior_caso']['meses_pagos']}")

print(f"\n💡 ANÁLISE:")
print(f"  Diferença: {formatar_moeda(resultado_2['diferenca_melhor_pior'])}")
print(f"  Economia esperada: {formatar_moeda(resultado_2['economia_esperada'])}")


# CENÁRIO 3: LANCE EMBUTIDO (valor distribuído nas parcelas)
print("\n\n" + "=" * 100)
print("📊 CENÁRIO 3: LANCE EMBUTIDO (35% distribuído nas parcelas)")
print("-" * 100)

resultado_3 = simular_consorcio_com_lances(
    valor_imovel=250000,
    prazo_meses=120,
    taxa_adm=2.0,
    fundo_reserva=1.0,
    tipo_lance='embutido',
    percentual_lance=35.0,              # 35% distribuído = R$ 87.500
    taxa_sobre_lance=0.0,               # Sem taxa separada
    numero_cotas_ativas=120,
    probabilidade_sorteio='pessimista'  # Topo 50% = mais competido
)

print(f"✓ Imóvel: {formatar_moeda(resultado_3['valor_imovel'])}")
print(f"✓ Parcela base: {formatar_moeda(resultado_3['parcela_base'])}")
print(f"✓ Parcela com taxa/fundo: {formatar_moeda(resultado_3['parcela_total_mensal'])}")
print(f"✓ Lance embutido total: {formatar_moeda(resultado_3['valor_lance'])} (distribuído mensalmente)")

print(f"\n🎯 MELHOR CASO (Contemplado no mês {resultado_3['melhor_caso']['mes_contemplacao']})")
print(f"  Total pago: {formatar_moeda(resultado_3['melhor_caso']['total_pago'])}")
print(f"  Meses pagos: {resultado_3['melhor_caso']['meses_pagos']}")

print(f"\n📊 CASO MÉDIO (Contemplado no mês {resultado_3['caso_medio']['mes_contemplacao']})")
print(f"  Total pago: {formatar_moeda(resultado_3['caso_medio']['total_pago'])}")
print(f"  Meses pagos: {resultado_3['caso_medio']['meses_pagos']}")

print(f"\n😱 PIOR CASO (Contemplado no mês {resultado_3['pior_caso']['mes_contemplacao']})")
print(f"  Total pago: {formatar_moeda(resultado_3['pior_caso']['total_pago'])}")
print(f"  Meses pagos: {resultado_3['pior_caso']['meses_pagos']}")


# COMPARATIVO FINAL
print("\n\n" + "=" * 100)
print("📊 COMPARATIVO DOS 3 CENÁRIOS")
print("=" * 100)

print(f"\n{'Tipo de Lance':<20} {'Melhor Caso':<18} {'Caso Médio':<18} {'Pior Caso':<18} {'Diferença':<18}")
print("-" * 100)

print(f"{'Lance Livre 30%':<20} {formatar_moeda(resultado_1['melhor_caso']['total_pago']):<18} {formatar_moeda(resultado_1['caso_medio']['total_pago']):<18} {formatar_moeda(resultado_1['pior_caso']['total_pago']):<18} {formatar_moeda(resultado_1['diferenca_melhor_pior']):<18}")

print(f"{'Lance Fixo 25%':<20} {formatar_moeda(resultado_2['melhor_caso']['total_pago']):<18} {formatar_moeda(resultado_2['caso_medio']['total_pago']):<18} {formatar_moeda(resultado_2['pior_caso']['total_pago']):<18} {formatar_moeda(resultado_2['diferenca_melhor_pior']):<18}")

print(f"{'Lance Embutido 35%':<20} {formatar_moeda(resultado_3['melhor_caso']['total_pago']):<18} {formatar_moeda(resultado_3['caso_medio']['total_pago']):<18} {formatar_moeda(resultado_3['pior_caso']['total_pago']):<18} {formatar_moeda(resultado_3['diferenca_melhor_pior']):<18}")


# ANÁLISE: Qual é melhor?
print("\n\n" + "=" * 100)
print("🏆 ANÁLISE: QUAL TIPO DE LANCE É MELHOR?")
print("=" * 100)

print(f"""
1️⃣  LANCE LIVRE (30%)
    ✓ Você controla o valor
    ✓ Mais flexível
    ✓ Taxa: 0.5%
    ✓ Custo caso médio: {formatar_moeda(resultado_1['caso_medio']['total_pago'])}
    
2️⃣  LANCE FIXO (25%)
    ✓ Padronizado pela administradora
    ✓ Sem taxa extra
    ✓ Custo caso médio: {formatar_moeda(resultado_2['caso_medio']['total_pago'])}
    
3️⃣  LANCE EMBUTIDO (35%)
    ✓ Distribuído na parcela
    ✓ Aumenta parcela gradualmente
    ✓ Custo caso médio: {formatar_moeda(resultado_3['caso_medio']['total_pago'])}

💡 RECOMENDAÇÃO:
   - Se quer contemplação rápida: Lance Livre com maior % 
   - Se quer simplicidade: Lance Fixo
   - Se quer menor parcela inicial: Lance Embutido
""")

print("\n" + "=" * 100)
print("✅ TESTE CONCLUÍDO COM SUCESSO")
print("=" * 100)
