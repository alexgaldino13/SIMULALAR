#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Corrige indentação do wizard_views_novo.py"""

import shutil
from datetime import datetime

ARQUIVO = r'D:\projetos\fi\simulacao\wizard_views_novo.py'
BACKUP = ARQUIVO + f'.backup_indent_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

print('Corrigindo indentação...')
shutil.copy(ARQUIVO, BACKUP)

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Corrigir linhas 71-77 (índices 70-76)
if len(lines) > 76:
    # Linha 71: comentário
    if lines[70].strip().startswith('# Salva dados'):
        lines[70] = '            # Salva dados convertendo Decimal para float\n'
    
    # Linha 72: cleaned_data
    if 'cleaned_data = _convert_decimals_to_floats' in lines[71]:
        lines[71] = '            cleaned_data = _convert_decimals_to_floats(form.cleaned_data)\n'
    
    # Linha 73: wizard_data
    if 'wizard_data[step_info' in lines[72]:
        lines[72] = '            wizard_data[step_info[\'name\']] = cleaned_data\n'
    
    # Linha 74: request.session
    if 'request.session' in lines[73]:
        lines[73] = '            request.session[\'wizard_novo_data\'] = wizard_data\n'
    
    # Linha 75: linha vazia
    if lines[74].strip() == '':
        lines[74] = '            \n'
    
    # Linha 76: comentário Próximo passo
    if '# Pr' in lines[75] or 'ximo' in lines[75]:
        lines[75] = '            # Próximo passo\n'
    
    # Linha 77: if current_step
    if 'if current_step' in lines[76]:
        lines[76] = '            if current_step < TOTAL_STEPS_NEW:\n'

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('✅ Indentação corrigida!')
print(f'Backup: {BACKUP}')
print('\nExecute: python manage.py runserver')
