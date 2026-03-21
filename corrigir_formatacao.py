# Script para corrigir formatação monetária em wizard_views_v2.py
import re

# Ler o arquivo
with open(r'D:\PROJETOS\FI\simulacao\wizard_views_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Lista de campos monetários que devem usar formatar_moeda_brl()
campos_monetarios = [
    'parcela_inicial', 'aluguel_mensal', 'total_aluguel_gasto', 
    'aporte_mensal_investimento', 'total_aportes', 'capital_inicial',
    'montante_final_investimento', 'ganho_com_investimento', 'valor_imovel_alvo',
    'sobra_apos_compra', 'patrimonio_final_total', 'total_custo', 
    'total_desembolso', 'patrimonio_final', 'valor_imovel_comprado',
    'capital_disponivel', 'valor_sobra_para_investir', 'montante_investido_final',
    'montante_final', 'fgts_usado', 'ganho_investimento', 'total_aluguel',
    'valor_carta', 'taxa_admin_total', 'parcela_mensal', 'total_pago',
    'custo_total_consorcio', 'primeira_parcela', 'ultima_parcela',
    'total_juros', 'custo_total_financiamento', 'valor_financiado',
    'entrada', 'margem_30_porcento', 'desconto_aplicado', 'deposito_mensal',
    'total_depositado', 'saldo_final', 'rendimento_acumulado'
]

# Substituir float() por formatar_moeda_brl() para campos monetários
for campo in campos_monetarios:
    # Padrão: 'campo': float(valor)
    pattern = f"'{campo}':\\s*float\\(([^)]+)\\)"
    replacement = f"'{campo}': formatar_moeda_brl(\\1)"
    content = re.sub(pattern, replacement, content)

# Salvar o arquivo
with open(r'D:\PROJETOS\FI\simulacao\wizard_views_v2.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Correções aplicadas com sucesso!')
print('Campos corrigidos:', len(campos_monetarios))
