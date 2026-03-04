"""
Script para corrigir wizard_views_novo.py e wizard_forms_novo.py
"""

# 1. Corrigir a importação e função _calcular_financiamento
import_fix = """from .utils import calcular_price_sac"""

# 2. Adicionar a função _calcular_financiamento que estava faltando
funcao_calcular = '''
def _calcular_financiamento(metodo, valor_principal, taxa_anual, prazo_meses, renda_familiar, 
                           fgts_saldo, usar_fgts, aluguel_durante):
    """
    Wrapper para calcular financiamento PRICE ou SAC
    """
    resultado = calcular_price_sac(
        metodo=metodo,
        valor_principal=valor_principal,
        taxa_anual=taxa_anual,
        prazo_meses=prazo_meses,
        seguro_mensal=0.0,
        taxa_admin_mensal=0.0,
        usar_fgts_financiamento=usar_fgts,
        fgts_saldo=fgts_saldo if usar_fgts else 0,
        tipo_amortizacao_fgts='reduzir_prazo',
        mes_uso_fgts_financiamento=1
    )
    
    # Processa resultado
    tabela = resultado.get('tabela', [])
    if not tabela:
        return {
            'metodo': f'Financiamento {metodo.upper()}',
            'parcela_inicial': 0,
            'total_juros': 0,
            'total_principal': float(valor_principal),
            'total_custo': float(valor_principal),
            'prazo_final_meses': prazo_meses,
            'prazo_final_anos': round(prazo_meses / 12, 1),
            'aluguel_durante': 0,
            'total_desembolso': float(valor_principal),
            'patrimonio_final': float(valor_principal),
            'economia_com_fgts': 0,
        }
    
    parcela_inicial = Decimal(str(resultado.get('parcela_inicial', tabela[0]['parcela_total'])))
    total_juros = Decimal(str(resultado.get('total_juros', 0)))
    prazo_final = len(tabela)
    
    # Custo total (principal + juros)
    custo_total = valor_principal + total_juros
    
    # Custo com aluguel durante o período
    meses_aluguel = min(prazo_final, int(prazo_meses))
    custo_aluguel = aluguel_durante * Decimal(meses_aluguel)
    
    total_desembolso = custo_total + custo_aluguel
    
    return {
        'metodo': f'Financiamento {metodo.upper()}',
        'parcela_inicial': float(parcela_inicial),
        'total_juros': float(total_juros),
        'total_principal': float(valor_principal),
        'total_custo': float(custo_total),
        'prazo_final_meses': prazo_final,
        'prazo_final_anos': round(prazo_final / 12, 1),
        'aluguel_durante': float(custo_aluguel),
        'total_desembolso': float(total_desembolso),
        'patrimonio_final': float(valor_principal),
        'economia_com_fgts': float(total_juros * Decimal('0.1')) if usar_fgts and fgts_saldo > 0 else 0,
    }
'''

print("Script de correção criado!")
print("\n1. Adicionar import: from .utils import calcular_price_sac")
print("2. Adicionar função _calcular_financiamento após os imports")
print("3. Remover código duplicado nas linhas 239-277")
