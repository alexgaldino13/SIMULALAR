#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para adicionar classe 'currency-input' nos campos monetários
do wizard_forms_novo.py
"""

import re

# Caminho do arquivo
file_path = r'D:\PROJETOS\FI\simulacao\wizard_forms_novo.py'

# Ler o arquivo
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Campos que precisam da classe currency-input
campos_monetarios = [
    'aluguel_atual',
    'saldo_fgts',
    'valor_imovel_desejado',
    'renda_familiar_bruta',
    'outras_despesas_mensais'
]

# Contador de modificações
modificacoes = 0

# Para cada campo monetário
for campo in campos_monetarios:
    # Padrão: encontrar o campo e adicionar currency-input na classe
    # Procura por: campo = forms.DecimalField( ... 'class': 'form-control', ... )
    pattern = rf"({campo}\s*=\s*forms\.DecimalField\([^)]*?'class':\s*'form-control)(')"
    replacement = r"\1 currency-input\2"
    
    # Fazer a substituição
    new_content, count = re.subn(pattern, replacement, content, count=1)
    
    if count > 0:
        content = new_content
        modificacoes += count
        print(f"✅ {campo}: classe 'currency-input' adicionada")
    else:
        print(f"❌ {campo}: não encontrado ou já modificado")

# Salvar o arquivo modificado
if modificacoes > 0:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n✅ Arquivo salvo com {modificacoes} modificações!")
else:
    print("\n⚠️ Nenhuma modificação realizada.")
