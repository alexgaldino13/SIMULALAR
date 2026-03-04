#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

print('Lendo arquivo...')
with open('simulacao/calculadora_financeira.py', 'r', encoding='utf-8') as f:
    content = f.read()

print('Aplicando correções...')

# Correção 1: Linha 504-505 corrompida
content = content.replace(
    '    # NOVO: Par\u00e2metros de FGTS acumuladoxa_admin_mensal_dec))\n            ensal_dec = Decimal(str(tr_mensal)) / 100  # TR em percentual',
    "    # NOVO: Par\u00e2metros de FGTS acumulado\n    tr_mensal_dec = Decimal(str(kwargs.get('tr_mensal', 0.0))) / 100  # TR em percentual"
)

print('Salvando arquivo...')
with open('simulacao/calculadora_financeira.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('\u2705 Arquivo corrigido com sucesso!')
print('\nAgora execute: python manage.py runserver')
