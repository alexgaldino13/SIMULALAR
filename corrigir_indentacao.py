#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corrigir erros de indentação no calculadora_financeira.py
"""

import re

# Ler o arquivo
with open('simulacao/calculadora_financeira.py', 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# Corrigir linha 505 (já corrigida, mas vamos garantir)
if len(linhas) > 504:
    if 'ensal_dec = Decimal' in linhas[504]:
        linhas[504] = '        ensal_dec = Decimal(str(tr_mensal)) / 100  # TR em percentual\n'

# Corrigir linhas 606-608
if len(linhas) > 605:
    # Linha 606
    if '# Aplicar TR' in linhas[605]:
        linhas[605] = '        # Aplicar TR (Taxa Referencial) ANTES dos juros\n'
    # Linha 607
    if 'saldo_devedor = saldo_devedor *' in linhas[606]:
        linhas[606] = "        saldo_devedor = saldo_devedor * (Decimal('1') + tr_mensal_dec)\n"
    # Linha 608
    if 'total_juros +=' in linhas[607]:
        linhas[607] = '        total_juros += juros_mensal\n'

# Remover linhas com texto estranho (terminal, pip install PyJWT)
linhas_limpas = []
for i, linha in enumerate(linhas):
    # Pular linhas que contêm apenas "terminal" ou "pip install PyJWT"
    if linha.strip() in ['terminal', 'pip install PyJWT']:
        print(f"Removendo linha {i+1}: {linha.strip()}")
        continue
    linhas_limpas.append(linha)

# Salvar arquivo corrigido
with open('simulacao/calculadora_financeira.py', 'w', encoding='utf-8') as f:
    f.writelines(linhas_limpas)

print("\nCorreções aplicadas com sucesso!")
print(f"Total de linhas removidas: {len(linhas) - len(linhas_limpas)}")
