# Script para corrigir indentação do wizard_views_novo.py

with open('simulacao/wizard_views_novo.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Substituir linhas 51-58 (índices 50-57) com indentação correta
new_lines = [
    "        try:\n",
    "            current_step = int(step)\n",
    "            if current_step < 1 or current_step > TOTAL_STEPS_NEW:\n",
    "                current_step = request.session.get('wizard_novo_current_step', 1)\n",
    "        except ValueError:\n",
    "            current_step = request.session.get('wizard_novo_current_step', 1)\n",
    "    else:\n",
    "        current_step = request.session.get('wizard_novo_current_step', 1)\n"
]

# Substituir as linhas problemáticas
lines[51:59] = new_lines

with open('simulacao/wizard_views_novo.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Indentação corrigida com sucesso!")
