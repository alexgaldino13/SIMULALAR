"""Teste rápido de validação da função simular_consorcio_com_lances"""

import sys
sys.path.insert(0, r'd:\PROJETOS\FI')

from simulacao.calculadora_financeira import simular_consorcio_com_lances

print('\n' + '='*70)
print('✅ TESTE RÁPIDO: simular_consorcio_com_lances()')
print('='*70 + '\n')

resultado = simular_consorcio_com_lances(
    valor_imovel=300000,
    prazo_meses=120,
    taxa_adm=2.0,
    fundo_reserva=1.0,
    tipo_lance='livre',
    percentual_lance=30.0,
    taxa_sobre_lance=0.5,
    probabilidade_sorteio='normal'
)

print(f"✓ Tipo de Lance: {resultado['tipo_lance'].upper()}")
print(f"✓ Valor da Carta: R$ {resultado['valor_imovel']:,.2f}")
print(f"✓ Valor do Lance: R$ {resultado['valor_lance']:,.2f}")
print(f"✓ Taxa sobre Lance: {resultado['taxa_sobre_lance']:.2f}%")

print(f"\n📊 CENÁRIOS DE CONTEMPLAÇÃO:")
print(f"  🎯 Melhor (Mês {resultado['melhor_caso']['mes_contemplacao']}):  R$ {resultado['melhor_caso']['total_pago']:,.2f}")
print(f"  📊 Médio (Mês {resultado['caso_medio']['mes_contemplacao']}):   R$ {resultado['caso_medio']['total_pago']:,.2f}")
print(f"  😱 Pior (Mês {resultado['pior_caso']['mes_contemplacao']}):     R$ {resultado['pior_caso']['total_pago']:,.2f}")

print(f"\n💰 ANÁLISE ECONÔMICA:")
print(f"  Diferença (Melhor vs Pior): R$ {resultado['diferenca_melhor_pior']:,.2f}")
print(f"  Economia Esperada: R$ {resultado['economia_esperada']:,.2f}")

print(f"\n✅ FUNÇÃO OPERACIONAL!")
print('='*70 + '\n')
