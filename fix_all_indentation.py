#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para corrigir TODA a indentação do wizard_forms_novo.py"""

with open('simulacao/wizard_forms_novo.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar e deletar linhas 238-269 (campos com indentação ruim)
lines_to_keep = lines[:237]  # Até linha 237 (saldo_fgts)
lines_to_keep.append('\n')

# Adicionar campo custas_documentacao_forma com indentação correta
lines_to_keep.extend([
    '    custas_documentacao_forma = forms.ChoiceField(\n',
    '        label="Como pretende pagar as custas de documentação? (~R$ 15.000)",\n',
    '        required=True,\n',
    '        choices=[\n',
    "            ('a_vista', 'À vista (precisa ter na entrada)'),\n",
    "            ('financiado', 'Financiado (aumenta parcela ~R$ 120/mês)'),\n",
    '        ],\n',
    "        initial='financiado',\n",
    '        widget=forms.RadioSelect(attrs={\n',
    "            'class': 'form-check-input',\n",
    '        }),\n',
    '        help_text="💰 ITBI + Registro + Escritura + Avaliação + Seguro"\n',
    '    )\n',
    '\n',
])

# Adicionar o resto do arquivo (a partir de recebe_13)
for i, line in enumerate(lines):
    if 'recebe_13 = forms.BooleanField(' in line:
        lines_to_keep.extend(lines[i:])
        break

# Salvar
with open('simulacao/wizard_forms_novo.py', 'w', encoding='utf-8') as f:
    f.writelines(lines_to_keep)

print("✅ Arquivo corrigido com sucesso!")
print(f"Total de linhas: {len(lines_to_keep)}")
