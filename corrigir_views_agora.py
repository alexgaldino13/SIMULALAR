#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil
from datetime import datetime

ARQUIVO = r'D:\projetos\fi\simulacao\wizard_views_novo.py'
BACKUP = ARQUIVO + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

print('Corrigindo wizard_views_novo.py...')

# Backup
shutil.copy(ARQUIVO, BACKUP)
print(f'Backup: {BACKUP}')

# Ler
with open(ARQUIVO, 'r', encoding='utf-8') as f:
    content = f.read()

# Corrigir linha 63
content = content.replace(
    "form_class = step_info['form']python fix_forms_indentation.py",
    "form_class = step_info['form']"
)

# Remover linha 64
content = content.replace(
    "    python fix_all_indentation.py\n",
    ""
)

# Salvar
with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.write(content)

print('\u2705 Arquivo corrigido!')
print('Execute: python manage.py runserver')
