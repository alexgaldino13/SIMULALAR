#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para corrigir wizard_views_novo.py"""

import re

# Ler o arquivo
with open('simulacao/wizard_views_novo.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Encontrar e substituir a seção corrompida
# Procurar por "# Determina passo atual" até "wizard_data = "
pattern = r'(    # Determina passo atual\n)(.*?)(    wizard_data = request\.session\.get)'

replacement = r'''\1    if step:
        try:
            current_step = int(step)
            if current_step < 1 or current_step > TOTAL_STEPS_NEW:
                current_step = request.session.get('wizard_novo_current_step', 1)
        except ValueError:
            current_step = request.session.get('wizard_novo_current_step', 1)
    else:
        current_step = request.session.get('wizard_novo_current_step', 1)

\3'''

# Aplicar substituição
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Salvar arquivo corrigido
with open('simulacao/wizard_views_novo.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Arquivo corrigido com sucesso!")
print("\nVerificando linhas 48-65:")
with open('simulacao/wizard_views_novo.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i in range(47, min(65, len(lines))):
        print(f"{i+1:3d}: {lines[i]}", end='')
