with open('simulacao/calculadora_financeira.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Linha 504 (index 503)
lines[503] = '    # NOVO: Par\u00e2metros de FGTS acumulado\n'
# Linha 505 (index 504)  
lines[504] = "    tr_mensal_dec = Decimal(str(kwargs.get('tr_mensal', 0.0))) / 100  # TR em percentual\n"

with open('simulacao/calculadora_financeira.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
    
print('Corrigido!')
