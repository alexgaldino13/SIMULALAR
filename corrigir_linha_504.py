#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

# Ler o arquivo
with open('simulacao/calculadora_financeira.py', 'r', encoding='utf-8') as f:
    linhas = f.readlines()

print(f"Total de linhas: {len(linhas)}")
print(f"\nLinhas 503-507 ANTES da correção:")
for i in range(502, 507):
    print(f"{i+1}: {repr(linhas[i])}")

# Corrigir linha 504 (index 503)
linhas[503] = "    # NOVO: Parâmetros de FGTS acumulado\n"

# Corrigir linha 505 (index 504)
linhas[504] = "    tr_mensal_dec = Decimal(str(kwargs.get('tr_mensal', 0.0))) / 100  # TR em percentual\n"

print(f"\nLinhas 503-507 DEPOIS da correção:")
for i in range(502, 507):
    print(f"{i+1}: {repr(linhas[i])}")

# Salvar
with open('simulacao/calculadora_financeira.py', 'w', encoding='utf-8') as f:
    f.writelines(linhas)

print("\n✅ Correção aplicada com sucesso!")
