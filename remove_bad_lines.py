#!/usr/bin/env python
# -*- coding: utf-8 -*-

print('Lendo arquivo...')
with open('simulacao/calculadora_financeira.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'Total de linhas antes: {len(lines)}')

# Remover linhas 1016-1019 (indices 1015-1018) que estão corrompidas
lines_to_remove = [1015, 1016, 1017, 1018]  # indices

for idx in sorted(lines_to_remove, reverse=True):
    if idx < len(lines):
        print(f'Removendo linha {idx+1}: {lines[idx].strip()}')
        del lines[idx]

print(f'\nTotal de linhas depois: {len(lines)}')

print('Salvando arquivo...')
with open('simulacao/calculadora_financeira.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('\u2705 Linhas corrompidas removidas!')
print('\nAgora execute: python manage.py runserver')
