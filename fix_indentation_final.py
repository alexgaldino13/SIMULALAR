#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Corrige indentação do else na linha 81"""

import shutil
from datetime import datetime

ARQUIVO = r'D:\projetos\fi\simulacao\wizard_views_novo.py'
BACKUP = ARQUIVO + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

print('Corrigindo indentação do else...')
shutil.copy(ARQUIVO, BACKUP)
print(f'Backup criado: {BACKUP}')

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Corrigir linha 81 (índice 80)
if len(lines) > 80:
    linha_81 = lines[80]
    # Se a linha começa com 4 espaços + 'else:'
    if linha_81.strip() == 'else:' and linha_81.startswith('    else:'):
        # Substituir por 12 espaços + 'else:'
        lines[80] = '            else:\n'
        print('✅ Linha 81 corrigida: 4 espaços -> 12 espaços')
    else:
        print(f'⚠️ Linha 81 não corresponde ao esperado: {repr(linha_81)}')

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('\n✅ Correção concluída!')
print('\nExecute agora: python manage.py runserver')
