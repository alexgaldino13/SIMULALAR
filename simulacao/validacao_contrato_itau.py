# simulacao/validacao_contrato_itau.py
"""
Validação do SAC Realista contra o Demonstrativo Descritivo de Crédito (DDC)
do contrato Itaú 10166338005 - ALEX GALDINO

Dados extraídos do DDC (Emitido em 26.9.2025 às 10:29:14):
"""

from simulacao.sac_realista import SAC_Realista
from datetime import datetime
from decimal import Decimal


# ==============================================================================
# DADOS REAIS DO DEMONSTRATIVO ITAÚ
# ==============================================================================

DADOS_DEMONSTRATIVO_ITAU = {
    'contrato': '10166338005',
    'agencia': '0268',
    'conta': '41334-1',
    'cliente': 'ALEX GALDINO',
    
    # Parâmetros do contrato original
    'prazo_total': 360,
    'prazo_remanescente': 267,
    'saldo_devedor_inicial_contrato': 327650.72,
    'data_inicio_contrato': datetime(2021, 9, 24),
    'data_ultima_parcela_original': datetime(2051, 8, 24),
    
    # Taxas (do DDC)
    'taxa_juros_anual_nominal': 0.06690948,  # 6,690948%
    'taxa_juros_anual_efetiva': 0.06900000,  # 6,900000%
    'taxa_juros_mensal': 0.00557579,  # 0,557579%
    'cet_anual': 0.0839,  # 8,39%
    
    # Custos mensais (do DDC)
    'taxa_adm_mensal': 25.00,
    'mip_inicial': 112.22,  # Morte e Invalidez Permanente
    'dfi_fixo': 22.16,  # Danos Físicos ao Imóvel
    
    # Última parcela no vencimento (antes de qualquer amortização extra)
    'ultima_parcela_vencimento': 24,  # dia
    'valor_ultima_parcela_sem_vencimento': 1146.12,
    
    # Índice de correção (TR) - valor médio histórico
    'indice_correcao_medio': 1.0007,
}

# Dados do primeiro mês do demonstrativo (Operação inicializada 26/09/2021)
PRIMEIRA_PARCELA_DEMONSTRATIVO = {
    'data_vencimento': '24/10/2021',
    'saldo_devedor_anterior': 327650.72,
    'vencimento': 327650.72,
    'amortizacao': 910.14,  # Fornecido no demo
    'juros': 1828.81,
    'indice_correcao': 1.0000,
    'seguro_rest': 0.00,
    'seguro_seguro': 25.00,
    'tca': 0.00,
    'multa': 0.00,
    'mora': 0.00,
    'ajuste': 0.00,
    'fgts': 0.00,
    'indice_correcao_outro': 1.0000,
    'acordos': 0.00,
    'situacao': 'Paga',
    'valor_total_devedor': 2764.00,  # (parcela total)
    'saldo_devedor': 326739.99,  # Saldo após amortização
}

# Segunda parcela (24/11/2021)
SEGUNDA_PARCELA_DEMONSTRATIVO = {
    'data_vencimento': '24/11/2021',
    'saldo_devedor_anterior': 326739.99,
    'vencimento': 1821.84,
    'amortizacao': 910.14,
    'juros': 1821.84,
    'valor_total_devedor': 2757.98,
    'saldo_devedor': 325829.85,
    'situacao': 'Paga',
}

# Último mês do demonstrativo que temos (24/07/2047)
ULTIMA_PARCELA_PARCIALMENTE_PAGA = {
    'mes': 316,
    'data_vencimento': '24/07/2047',
    'saldo_devedor_anterior': 6.22,
    'amortizacao': 0.00,  # Prazo foi reduzido
    'juros': 0.00,
    'valor_total_devedor': 1146.32,
    'saldo_devedor': 0.00,
    'situacao': 'Proposta',
}


def validar_primeira_parcela():
    """
    Valida o cálculo da primeira parcela contra dados do demonstrativo.
    
    Esperado (DDC):
        - Amortização: 910.14
        - Juros: 1821.84
        - Parcela Total: ~2764.00
    """
    
    print("=" * 80)
    print("VALIDAÇÃO: PRIMEIRA PARCELA")
    print("=" * 80)
    
    sac = SAC_Realista(
        saldo_devedor_inicial=327650.72,
        taxa_juros_mensal=0.00557579,
        prazo_meses=360,
        taxa_adm_mensal=0.0,  # Primeira parcela não inclui TCA
        seguro_mip_mensal=0.0,  # Primeira parcela não inclui seguro
        seguro_dfi_mensal=25.0,  # DFI incluído
        indice_correcao_mensal=1.0,  # Sem TR na primeira
        data_inicio=datetime(2021, 9, 24),
    )
    
    # Calcula primeira parcela
    parcela = sac.calcular_parcela_mes(1, Decimal('327650.72'))
    
    print(f"\n{'Componente':<20} | {'Calculado':<15} | {'DDC':<15} | {'Diferença':<15}")
    print("-" * 70)
    
    amort_calc = parcela['amortizacao']
    amort_ddc = 910.14
    diff_amort = abs(amort_calc - amort_ddc)
    print(f"{'Amortização':<20} | R$ {amort_calc:>12,.2f} | R$ {amort_ddc:>12,.2f} | R$ {diff_amort:>12,.2f}")
    
    juros_calc = parcela['juros']
    juros_ddc = 1828.81  # Conforme DDC
    diff_juros = abs(juros_calc - juros_ddc)
    print(f"{'Juros':<20} | R$ {juros_calc:>12,.2f} | R$ {juros_ddc:>12,.2f} | R$ {diff_juros:>12,.2f}")
    
    dfi_calc = parcela['seguro_dfi']
    dfi_ddc = 25.00
    diff_dfi = abs(dfi_calc - dfi_ddc)
    print(f"{'DFI (Seguro)':<20} | R$ {dfi_calc:>12,.2f} | R$ {dfi_ddc:>12,.2f} | R$ {diff_dfi:>12,.2f}")
    
    parcela_total_calc = parcela['parcela_total']
    parcela_total_ddc = 2764.00  # Conforme DDC
    diff_parcela = abs(parcela_total_calc - parcela_total_ddc)
    print(f"{'Parcela Total':<20} | R$ {parcela_total_calc:>12,.2f} | R$ {parcela_total_ddc:>12,.2f} | R$ {diff_parcela:>12,.2f}")
    
    saldo_novo_calc = parcela['saldo_devedor_novo']
    saldo_novo_ddc = 326739.99
    diff_saldo = abs(saldo_novo_calc - saldo_novo_ddc)
    print(f"{'Saldo Devedor Novo':<20} | R$ {saldo_novo_calc:>12,.2f} | R$ {saldo_novo_ddc:>12,.2f} | R$ {diff_saldo:>12,.2f}")
    
    print("\n✅ Validação: PRIMEIRA PARCELA OK!" if diff_parcela < 1.0 else "\n❌ Validação: FALHA na primeira parcela!")
    return diff_parcela < 1.0


def validar_progressao_juros():
    """
    Valida que os juros diminuem mês a mês (propriedade do SAC).
    """
    
    print("\n" + "=" * 80)
    print("VALIDAÇÃO: PROGRESSÃO DE JUROS (Deve diminuir mensalmente)")
    print("=" * 80)
    
    sac = SAC_Realista(
        saldo_devedor_inicial=327650.72,
        taxa_juros_mensal=0.00557579,
        prazo_meses=360,
        taxa_adm_mensal=25.0,
        seguro_mip_mensal=112.22,
        seguro_dfi_mensal=22.16,
        indice_correcao_mensal=1.0,
    )
    
    tabela = sac.gerar_tabela_amortizacao(meses=12)
    
    print(f"\n{'Mês':<6} | {'Juros':<15} | {'Amortização':<15} | {'Parcela':<15}")
    print("-" * 60)
    
    juros_anterior = float('inf')
    decrescente_ok = True
    
    for p in tabela:
        juros = p['juros']
        amort = p['amortizacao']
        parcela = p['parcela_total']
        
        is_decreasing = juros < juros_anterior
        marker = "✓" if is_decreasing else "✗"
        
        print(f"{p['mes']:<6} | R$ {juros:>12,.2f} {marker} | R$ {amort:>12,.2f} | R$ {parcela:>12,.2f}")
        
        if not is_decreasing:
            decrescente_ok = False
        
        juros_anterior = juros
    
    print("\n✅ Validação: Juros DECRESCEM corretamente!" if decrescente_ok else "\n❌ Validação: FALHA na progressão!")
    return decrescente_ok


def comparar_com_demonstrativo_completo():
    """
    Compara nossa calculadora com o demonstrativo completo (primeiras 10 parcelas).
    
    IMPORTANTE: O demonstrativo mostra que TCA e Seguros foram adicionados APÓS 
    a primeira parcela. Logo, comparamos apenas amortização + juros.
    """
    
    print("\n" + "=" * 80)
    print("VALIDAÇÃO: COMPARAÇÃO COM DEMONSTRATIVO ITAÚ (10 primeiras parcelas)")
    print("=" * 80)
    
    # SAC sem TCA e sem Seguros para comparar apenas amortização + juros
    sac = SAC_Realista(
        saldo_devedor_inicial=327650.72,
        taxa_juros_mensal=0.00557579,
        prazo_meses=360,
        taxa_adm_mensal=0.0,  # NÃO inclui TCA
        seguro_mip_mensal=0.0,  # NÃO inclui MIP
        seguro_dfi_mensal=0.0,  # NÃO inclui DFI
        indice_correcao_mensal=1.0,  # Sem correção monetária por enquanto
    )
    
    tabela = sac.gerar_tabela_amortizacao(meses=10)
    
    # Dados comparativos do demonstrativo (primeiras linhas) - SEM TCA/SEGUROS
    dados_demo = [
        {'mes': 1, 'juros_ddc': 1828.81, 'amort_ddc': 910.14, 'parcela_ddc': 2738.95},  # 910.14 + 1828.81
        {'mes': 2, 'juros_ddc': 1821.84, 'amort_ddc': 910.14, 'parcela_ddc': 2731.98},  # 910.14 + 1821.84
        {'mes': 3, 'juros_ddc': 1814.84, 'amort_ddc': 910.14, 'parcela_ddc': 2724.98},  # 910.14 + 1814.84
        {'mes': 4, 'juros_ddc': 1807.80, 'amort_ddc': 910.14, 'parcela_ddc': 2717.94},  # 910.14 + 1807.80
        {'mes': 5, 'juros_ddc': 1800.86, 'amort_ddc': 910.14, 'parcela_ddc': 2711.00},  # 910.14 + 1800.86
    ]
    
    print(f"\n{'Mês':<5} | {'Juros (DDC)':<15} | {'Juros (Calc)':<15} | {'Diferença':<12} | {'Parcela (DDC)':<15} | {'Parcela (Calc)':<15}")
    print("-" * 110)
    
    desvios_totais = []
    
    for i, parcela in enumerate(tabela[:5], 1):
        dado = dados_demo[i - 1]
        juros_ddc = dado['juros_ddc']
        juros_calc = parcela['juros']
        diff_juros = abs(juros_calc - juros_ddc)
        
        parcela_ddc = dado['parcela_ddc']
        parcela_calc = parcela['parcela_total']
        diff_parcela = abs(parcela_calc - parcela_ddc)
        
        desvios_totais.append(diff_parcela)
        
        print(
            f"{i:<5} | R$ {juros_ddc:>12,.2f} | R$ {juros_calc:>12,.2f} | R$ {diff_juros:>10,.2f} | "
            f"R$ {parcela_ddc:>12,.2f} | R$ {parcela_calc:>12,.2f}"
        )
    
    desvio_medio = sum(desvios_totais) / len(desvios_totais)
    print(f"\n📊 Desvio médio nas parcelas: R$ {desvio_medio:.2f}")
    print("✅ Validação OK!" if desvio_medio < 5.0 else "⚠️  Desvio significativo - revisar!")
    
    return desvio_medio < 5.0


def resumo_simulador():
    """
    Gera um resumo completo do simulador.
    """
    
    print("\n" + "=" * 80)
    print("RESUMO DO SIMULADOR SAC_REALISTA")
    print("=" * 80)
    
    sac = SAC_Realista(
        saldo_devedor_inicial=327650.72,
        taxa_juros_mensal=0.00557579,
        prazo_meses=360,
        taxa_adm_mensal=25.0,
        seguro_mip_mensal=112.22,
        seguro_dfi_mensal=22.16,
        indice_correcao_mensal=1.0007,
    )
    
    resumo = sac.resumo_contrato()
    
    print(f"\nSaldo inicial: R$ {resumo['saldo_inicial']:,.2f}")
    print(f"Prazo: {resumo['prazo_meses']} meses")
    print(f"Taxa mensal: {resumo['taxa_juros_mensal_pct']:.4f}%")
    print(f"Taxa anual (nominal): {resumo['taxa_juros_anual_pct']:.4f}%")
    print(f"\nTotal a pagar após {resumo['parcelas_geradas']} meses:")
    print(f"  - Amortizações: R$ {resumo['total_amortizacoes']:,.2f}")
    print(f"  - Juros: R$ {resumo['total_juros']:,.2f}")
    print(f"  - Taxa de administração: R$ {resumo['total_adm']:,.2f}")
    print(f"  - Seguro MIP: R$ {resumo['total_seguros_mip']:,.2f}")
    print(f"  - Seguro DFI: R$ {resumo['total_seguros_dfi']:,.2f}")
    print(f"  {'─' * 40}")
    print(f"  TOTAL: R$ {resumo['total_pago']:,.2f}")
    
    custo_total = (
        resumo['total_juros'] +
        resumo['total_adm'] +
        resumo['total_seguros_mip'] +
        resumo['total_seguros_dfi']
    )
    pct_custo = (custo_total / resumo['total_pago']) * 100
    
    print(f"\nCusto total (juros + taxas): R$ {custo_total:,.2f} ({pct_custo:.1f}% do total)")
    print(f"Saldo devedor final: R$ {resumo['saldo_final']:,.2f}")


if __name__ == '__main__':
    ok1 = validar_primeira_parcela()
    ok2 = validar_progressao_juros()
    ok3 = comparar_com_demonstrativo_completo()
    resumo_simulador()
    
    print("\n" + "=" * 80)
    print("RESULTADO GERAL DA VALIDAÇÃO")
    print("=" * 80)
    
    resultados = [
        ("Primeira Parcela", ok1),
        ("Progressão de Juros", ok2),
        ("Comparação com DDC", ok3),
    ]
    
    for teste, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{teste:<30} {status}")
    
    todos_ok = all(r for _, r in resultados)
    print("\n" + ("🎉 TODOS OS TESTES PASSARAM!" if todos_ok else "⚠️  Alguns testes falharam - revisar!"))
