#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Recria wizard_views_novo.py do zero removendo corrupções"""

import shutil
from datetime import datetime

ARQUIVO_BACKUP = r'D:\projetos\fi\simulacao\wizard_views_novo.py.backup_20260130_110649'
ARQUIVO_DESTINO = r'D:\projetos\fi\simulacao\wizard_views_novo.py'
BACKUP_FINAL = ARQUIVO_DESTINO + f'.backup_antes_recriar_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

print('Recriando wizard_views_novo.py do zero...')

# Backup do arquivo atual
shutil.copy(ARQUIVO_DESTINO, BACKUP_FINAL)
print(f'Backup criado: {BACKUP_FINAL}')

# Ler backup
with open(ARQUIVO_BACKUP, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# Remover linhas corrompidas (63-64)
linhas_limpas = []
for i, linha in enumerate(linhas, 1):
    # Pular linhas 63-64 que contêm comandos Python
    if i in [63, 64]:
        continue
    # Corrigir indentação das linhas 72-77
    if i == 72 and linha.strip().startswith('# Salva dados'):
        linhas_limpas.append('            # Salva dados convertendo Decimal para float\n')
    elif i == 73 and 'cleaned_data = _convert_decimals_to_floats' in linha:
        linhas_limpas.append('            cleaned_data = _convert_decimals_to_floats(form.cleaned_data)\n')
    elif i == 74 and 'wizard_data[step_info' in linha:
        linhas_limpas.append('            wizard_data[step_info[\'name\']] = cleaned_data\n')
    elif i == 75 and 'request.session' in linha:
        linhas_limpas.append('            request.session[\'wizard_novo_data\'] = wizard_data\n')
    elif i == 76 and linha.strip() == '':
        linhas_limpas.append('            \n')
    elif i == 77 and '# Pr' in linha:
        linhas_limpas.append('            # Próximo passo\n')
    elif i == 78 and 'if current_step' in linha:
        linhas_limpas.append('            if current_step < TOTAL_STEPS_NEW:\n')
    elif i == 82 and linha.strip() == 'else:':
        linhas_limpas.append('            else:\n')
    else:
        linhas_limpas.append(linha)

# Salvar arquivo limpo
with open(ARQUIVO_DESTINO, 'w', encoding='utf-8') as f:
    f.writelines(linhas_limpas)

print('✅ Arquivo recriado com sucesso!')
print('\nExecute: python manage.py runserver')
