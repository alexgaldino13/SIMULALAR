#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Corrige linhas 160, 167-169 do wizard_views_novo.py"""

import shutil
from datetime import datetime

ARQUIVO = r'D:\projetos\fi\simulacao\wizard_views_novo.py'
BACKUP = ARQUIVO + f'.backup_final_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

print('Corrigindo linhas 160, 167-169...')
shutil.copy(ARQUIVO, BACKUP)
print(f'Backup: {BACKUP}')

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# Corrigir linha 160 (índice 159)
if len(linhas) > 159:
    linha_160 = linhas[159]
    if 'custas_documentacao_forma' in linha_160 and linha_160.startswith('        '):
        # Remover 4 espaços extras (de 8 para 4)
        linhas[159] = '    custas_documentacao_forma = capital.get(\'custas_documentacao_forma\', \'financiado\')\n'
        print('✅ Linha 160 corrigida')

# Corrigir linha 167 (índice 166)
if len(linhas) > 166:
    linha_167 = linhas[166]
    if '# Adiciona custas' in linha_167 and linha_167.startswith('        '):
        # Remover 4 espaços extras (de 8 para 4)
        linhas[166] = '    # Adiciona custas de documentação ao financiamento apenas se a opção for \'financiado\'\n'
        print('✅ Linha 167 corrigida')

# Corrigir linha 168 (índice 167)
if len(linhas) > 167:
    linha_168 = linhas[167]
    if 'if custas_documentacao_forma' in linha_168 and linha_168.startswith('            '):
        # Remover 8 espaços extras (de 12 para 4)
        linhas[167] = '    if custas_documentacao_forma == \'financiado\':\n'
        print('✅ Linha 168 corrigida')

# Corrigir linha 169 (índice 168)
if len(linhas) > 168:
    linha_169 = linhas[168]
    if 'principal = principal + custas_documentacao' in linha_169 and linha_169.startswith('                 '):
        # Remover 9 espaços extras (de 17 para 8)
        linhas[168] = '        principal = principal + custas_documentacao\n'
        print('✅ Linha 169 corrigida')

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.writelines(linhas)

print('\n✅ Correções aplicadas!')
print('Execute: python manage.py runserver')
