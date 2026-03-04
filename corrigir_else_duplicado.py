#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Corrige else duplicado no wizard_views_novo.py"""

import shutil
from datetime import datetime

ARQUIVO = r'D:\projetos\fi\simulacao\wizard_views_novo.py'
BACKUP = ARQUIVO + f'.backup_else_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

print('Corrigindo else duplicado...')
shutil.copy(ARQUIVO, BACKUP)

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Corrigir linha 82 (índice 81) - deve ter 12 espaços, não 4
if len(lines) > 81:
    if lines[81].strip() == 'else:':
        # Verificar se tem apenas 4 espaços
        if lines[81].startswith('    else:') and not lines[81].startswith('            else:'):
            lines[81] = '            else:\n'
            print('✅ Linha 82 corrigida: indentação ajustada para 12 espaços')

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('✅ Correção concluída!')
print(f'Backup: {BACKUP}')
print('\nExecute: python manage.py runserver')
