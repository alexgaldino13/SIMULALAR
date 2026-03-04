#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Corrige linha 228 do wizard_views_novo.py"""

import shutil
from datetime import datetime

ARQUIVO = r'D:\projetos\fi\simulacao\wizard_views_novo.py'
BACKUP = ARQUIVO + f'.backup_linha228_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

print('Corrigindo linha 228...')
shutil.copy(ARQUIVO, BACKUP)
print(f'Backup: {BACKUP}')

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# Corrigir linha 228 (índice 227)
if len(linhas) > 227:
    linha_228 = linhas[227]
    if 'entrada = min(capital_guardado' in linha_228:
        # Substituir min por max e simplificar
        linhas[227] = '    entrada = max(capital_guardado, valor_imovel * Decimal(\'0.2\'))  # Usa o maior: capital ou 20% imóvel\n'
        print('✅ Linha 228 corrigida: min() → max()')
    else:
        print(f'⚠️ Linha 228 não corresponde: {repr(linha_228)}')

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.writelines(linhas)

print('\n✅ Correção concluída!')
print('Execute: python manage.py runserver')
