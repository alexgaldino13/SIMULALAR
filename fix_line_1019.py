#!/usr/bin/env python
# -*- coding: utf-8 -*-

print('Lendo arquivo...')
with open('simulacao/calculadora_financeira.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'Total de linhas: {len(lines)}')

# Remover linhas com texto inválido
lines_clean = []
removed = []

for i, line in enumerate(lines, 1):
    # Remover linhas que contêm apenas comandos de terminal
    if line.strip() in ['terminal', 'pip install PyJWT']:
        removed.append(f'Linha {i}: {line.strip()}')
        continue
    lines_clean.append(line)

print(f'\nLinhas removidas: {len(removed)}')
for r in removed:
    print(f'  - {r}')

print('\nSalvando arquivo...')
with open('simulacao/calculadora_financeira.py', 'w', encoding='utf-8') as f:
    f.writelines(lines_clean)

print('\u2705 Arquivo limpo com sucesso!')
print(f'Total de linhas após limpeza: {len(lines_clean)}')
print('\nAgora execute: python manage.py runserver')
