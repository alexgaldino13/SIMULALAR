#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para corrigir indentação do campo custas_documentacao_forma"""

import re

# Lê o arquivo
with open('simulacao/wizard_forms_novo.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Padrão para encontrar o campo com indentação errada
old_pattern = r'''    custas_documentacao_forma = forms\.ChoiceField\(
\s+label="Como pretende pagar as custas de documentação\? \(~R\$ 15\.000\)",
\s+required=True,
\s+choices=\[
\s+\('a_vista', 'À vista \(precisa ter na entrada\)'\),
\s+\('financiado', 'Financiado \(aumenta parcela ~R\$ 120/mês\)'\),
\s+\],
\s+initial='financiado',
\s+widget=forms\.RadioSelect\(attrs=\{
\s+'class': 'form-check-input',
\s+\}\),
\s+help_text="💰 ITBI \+ Registro \+ Escritura \+ Avaliação \+ Seguro"
\s+\)'''

# Novo campo com indentação correta
new_field = '''    custas_documentacao_forma = forms.ChoiceField(
        label="Como pretende pagar as custas de documentação? (~R$ 15.000)",
        required=True,
        choices=[
            ('a_vista', 'À vista (precisa ter na entrada)'),
            ('financiado', 'Financiado (aumenta parcela ~R$ 120/mês)'),
        ],
        initial='financiado',
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
        }),
        help_text="💰 ITBI + Registro + Escritura + Avaliação + Seguro"
    )'''

# Substitui
content_new = re.sub(old_pattern, new_field, content, flags=re.MULTILINE)

# Salva
with open('simulacao/wizard_forms_novo.py', 'w', encoding='utf-8') as f:
    f.write(content_new)

print("✅ Indentação corrigida com sucesso!")
