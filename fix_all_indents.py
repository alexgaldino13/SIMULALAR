#!/usr/bin/env python
# -*- coding: utf-8 -*-

print('Lendo arquivo...')
with open('simulacao/calculadora_financeira.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'Total de linhas: {len(lines)}')

# Corrigir linhas 606-608 (índices 605-607)
if len(lines) > 608:
    print('Corrigindo linhas 606-608...')
    lines[605] = '        # Aplicar TR (Taxa Referencial) ANTES dos juros\n'
    lines[606] = "        saldo_devedor = saldo_devedor * (Decimal('1') + tr_mensal_dec)\n"
    lines[607] = '        total_juros += juros_mensal\n'

print('Salvando arquivo...')
with open('simulacao/calculadora_financeira.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('✅ Correções aplicadas!')
print('\nAgora execute: python manage.py runserver')
