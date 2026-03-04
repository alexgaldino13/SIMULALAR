#!/usr/bin/env python
# -*- coding: utf-8 -*-

print('Corrigindo wizard_forms_novo.py...')

with open('simulacao/wizard_forms_novo.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Contar parênteses abertos e fechados
open_count = content.count('(')
close_count = content.count(')')

print(f'Parênteses abertos: {open_count}')
print(f'Parênteses fechados: {close_count}')
print(f'Diferença: {open_count - close_count}')

# Ler linha por linha para encontrar o problema
with open('simulacao/wizard_forms_novo.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'\nTotal de linhas: {len(lines)}')

# Verificar linhas 160-190
print('\nLinhas 160-190:')
for i in range(159, min(190, len(lines))):
    print(f'{i+1}: {lines[i].rstrip()}')
