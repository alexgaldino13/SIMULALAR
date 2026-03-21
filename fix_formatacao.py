#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corrigir formatação monetária em wizard_views_v2.py
Substitui float() por formatar_moeda_brl() em campos monetários
"""

import re

# Ler o arquivo
with open('simulacao/wizard_views_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Lista de campos monetários que devem usar formatar_moeda_brl
campos_monetarios = [
    'total_aportes',
    'capital_inicial',
    'montante_final_investimento',
    'ganho_com_investimento',
    'valor_imovel_alvo',
    'sobra_apos_compra',
    'patrimonio_final_total',
    'total_custo',
    'total_desembolso',
    'patrimonio_final',
    'valor_entrada',
    'valor_financiado',
    'total_juros',
    'custo_total',
    'primeira_parcela',
    'ultima_parcela',
    'parcela_fixa',
    'total_pago',
    'economia_vs_aluguel',
    'custo_oportunidade',
    'valor_parcela_consorcio',
    'total_pago_consorcio',
    'lance_sugerido',
    'economia_juros',
    'aporte_mensal_necessario',
    'total_investido',
    'rendimento_total',
    'tempo_para_comprar',
]

# Fazer as substituições
for campo in campos_monetarios:
    # Padrão: 'campo': float(variavel)
    pattern = f"'{campo}':\\s*float\\(([^)]+)\\)"
    replacement = f"'{campo}': formatar_moeda_brl(\\1)"
    content = re.sub(pattern, replacement, content)

# Salvar o arquivo
with open('simulacao/wizard_views_v2.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Correções aplicadas com sucesso!")
print(f"✅ {len(campos_monetarios)} campos monetários corrigidos")
