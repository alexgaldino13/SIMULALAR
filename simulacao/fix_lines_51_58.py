# Script para corrigir linhas 51-58 do wizard_views_novo.py

with open('wizard_views_novo.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Corrigir linhas 51-58 (índices 50-57)
lines[50] = '    # Determina passo atual\n'
lines[51] = '    if step:\n'
lines[52] = '        try:\n'
lines[53] = '            current_step = int(step)\n'
lines[54] = '            if current_step < 1 or current_step > TOTAL_STEPS_NEW:\n'
lines[55] = '                current_step = request.session.get(\'wizard_novo_current_step\', 1)\n'
lines[56] = '        except ValueError:\n'
lines[57] = '            current_step = request.session.get(\'wizard_novo_current_step\', 1)\n'

with open('wizard_views_novo.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Arquivo corrigido com sucesso!')
