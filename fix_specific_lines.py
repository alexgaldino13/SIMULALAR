# Script para corrigir apenas as linhas 158, 159 e 164

with open('D:\\PROJETOS\\FI\\simulacao\\wizard_views_novo.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Corrigir apenas as linhas específicas
# Linha 158 (índice 157)
if len(lines) > 157 and 'custas_documentacao' in lines[157]:
    lines[157] = '    custas_documentacao = Decimal(str(capital.get(\'custas_documentacao\', 15000)) or 15000)\n'
    print(f"Linha 158 corrigida")

# Linha 159 (índice 158)
if len(lines) > 158 and 'taxa_investimento' in lines[158]:
    lines[158] = '    taxa_investimento = Decimal(str(cenarios_selecionados.get(\'taxa_investimento_esperada\', 9.5)))\n'
    print(f"Linha 159 corrigida")

# Linha 164 (índice 163)
if len(lines) > 163 and 'principal = principal + custas_documentacao' in lines[163]:
    lines[163] = '    principal = principal + custas_documentacao  # Adiciona custas de documentacao ao financiamento\n'
    print(f"Linha 164 corrigida")

with open('D:\\PROJETOS\\FI\\simulacao\\wizard_views_novo.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Arquivo corrigido com sucesso!")
