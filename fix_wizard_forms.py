#!/usr/bin/env python
# -*- coding: utf-8 -*-

print('Lendo arquivo wizard_forms_novo.py...')
with open('simulacao/wizard_forms_novo.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'Total de linhas: {len(lines)}')

# Corrigir linhas 175-184
if len(lines) > 184:
    # Linha 177 deve fechar o campo tempo_imovel_atual
    lines[176] = '        help_text="\ud83d\udccd Ajuda a prever estabilidade e possibilidade de mudan\u00e7a"\n'
    lines[177] = '    )\n'
    lines[178] = '    \n'
    lines[179] = '    elegivel_mcmv = forms.BooleanField(\n'
    lines[180] = '        label="Renda familiar se enquadra no Minha Casa Minha Vida? (at\u00e9 R$ 8.000)",\n'
    lines[181] = '        required=False,\n'
    lines[182] = '        initial=False,\n'
    lines[183] = '        help_text="\ud83c\udfe0 MCMV oferece subs\u00eddios de at\u00e9 R$ 55.000"\n'
    lines[184] = '    )\n'
    
    print('Linhas 175-184 corrigidas!')

print('Salvando arquivo...')
with open('simulacao/wizard_forms_novo.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('\u2705 Arquivo corrigido com sucesso!')
print('\nAgora execute: python manage.py runserver')
