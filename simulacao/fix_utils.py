# Script para corrigir utils.py removendo duplicacao

with open('utils.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Manter apenas as primeiras 591 linhas
with open('utils.py', 'w', encoding='utf-8') as f:
    f.writelines(lines[:591])

print('Arquivo utils.py corrigido!')
