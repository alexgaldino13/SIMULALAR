#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script completo para corrigir todos os erros de indentação
"""

print('=== CORREÇÃO COMPLETA DO ARQUIVO ===')
print('\nLendo arquivo...')
with open('simulacao/calculadora_financeira.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'Total de linhas: {len(lines)}')

errors_fixed = 0

# Verificar e corrigir linha por linha na região problemática
print('\nCorrigindo região 1014-1020...')

# Linha 1015 deve ter 4 espaços
if len(lines) > 1014 and 'valorizacao_imovel_anual_percent' in lines[1014]:
    lines[1014] = '    valorizacao_imovel_anual_percent = Decimal(str(valorizacao_imovel)) / 100\n'
    errors_fixed += 1

# Linha 1016 deve estar vazia ou ter comentário
if len(lines) > 1015:
    lines[1015] = '    \n'
    errors_fixed += 1

# Linha 1017 - remover se tiver apenas espaços ou texto estranho
if len(lines) > 1016:
    if lines[1016].strip() == '' or 'Aplicar IR' in lines[1016]:
        lines[1016] = '    # Aplicar IR sobre rendimentos se necessário\n'
        errors_fixed += 1

# Linha 1018 - deve ter 4 espaços (comentado por enquanto)
if len(lines) > 1017:
    lines[1017] = '    # ir_mes = calcular_ir_rendimentos(rendimento_fgts_mensal, mes)\n'
    errors_fixed += 1

# Linha 1019 - deve ter 4 espaços (comentado por enquanto)
if len(lines) > 1018:
    lines[1018] = '    # rendimento_fgts_mensal_liquido = rendimento_fgts_mensal - ir_mes\n'
    errors_fixed += 1

# Linha 1020 - Prazo deve ter 4 espaços
if len(lines) > 1019 and 'Prazo' in lines[1019]:
    lines[1019] = '    # Prazo (deve ser Int)\n'
    errors_fixed += 1

if len(lines) > 1020 and 'prazo_meses_int' in lines[1020]:
    lines[1020] = '    prazo_meses_int = int(prazo_meses)\n'
    errors_fixed += 1

print(f'Erros corrigidos: {errors_fixed}')

print('\nSalvando arquivo...')
with open('simulacao/calculadora_financeira.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('\u2705 Arquivo corrigido!')
print('\nAgora execute: python manage.py runserver')
