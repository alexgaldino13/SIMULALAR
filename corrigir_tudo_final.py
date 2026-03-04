#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para corrigir TODOS os erros de sintaxe"""

import shutil
from datetime import datetime

print('\n' + '='*70)
print('CORREÇÃO FINAL - Todos os Erros de Sintaxe')
print('='*70 + '\n')

# Arquivo 1: wizard_views_novo.py
ARQUIVO1 = r'D:\projetos\fi\simulacao\wizard_views_novo.py'
BACKUP1 = ARQUIVO1 + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

print('1. Corrigindo wizard_views_novo.py...')
shutil.copy(ARQUIVO1, BACKUP1)

with open(ARQUIVO1, 'r', encoding='utf-8') as f:
    content1 = f.read()

# Corrigir linha 63
content1 = content1.replace(
    "form_class = step_info['form']python fix_forms_indentation.py",
    "form_class = step_info['form']"
)

# Remover linha 64
content1 = content1.replace(
    "    python fix_all_indentation.py\n",
    ""
)

with open(ARQUIVO1, 'w', encoding='utf-8') as f:
    f.write(content1)

print('✅ wizard_views_novo.py corrigido!')

# Arquivo 2: wizard_forms_novo.py
ARQUIVO2 = r'D:\projetos\fi\simulacao\wizard_forms_novo.py'
BACKUP2 = ARQUIVO2 + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

print('\n2. Corrigindo wizard_forms_novo.py...')
shutil.copy(ARQUIVO2, BACKUP2)

with open(ARQUIVO2, 'r', encoding='utf-8') as f:
    content2 = f.read()

# Corrigir linha 244
content2 = content2.replace(
    "        initial='financiado',d:",
    "        initial='financiado',"
)

with open(ARQUIVO2, 'w', encoding='utf-8') as f:
    f.write(content2)

print('✅ wizard_forms_novo.py corrigido!')

print('\n' + '='*70)
print('✅ TODOS OS ERROS CORRIGIDOS COM SUCESSO!')
print('='*70)
print(f'\nBackups:')
print(f'  - {BACKUP1}')
print(f'  - {BACKUP2}')
print('\n🚀 Execute agora: python manage.py runserver\n')
