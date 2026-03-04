#!/usr/bin/env python
# -*- coding: utf-8 -*-

print('Lendo arquivo...')
with open('simulacao/calculadora_financeira.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'Total de linhas: {len(lines)}')

# Corrigir linha 1017 (índice 1016)
if len(lines) > 1017:
    print('Corrigindo linha 1017...')
    lines[1016] = '            ir_mes = calcular_ir_rendimentos(rendimento_fgts_mensal, mes)\n'

# Corrigir linha 1019 (índice 1018)  
if len(lines) > 1019:
    print('Corrigindo linha 1019...')
    lines[1018] = '            rendimento_fgts_mensal_liquido = rendimento_fgts_mensal - ir_mes\n'

print('Salvando arquivo...')
with open('simulacao/calculadora_financeira.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('\u2705 Corre\u00e7\u00f5es aplicadas!')
print('\nAgora execute: python manage.py runserver')
