#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corrigir wizard_forms_novo.py removendo linhas órfãs
"""

import os
import shutil

# Caminho do arquivo
arquivo = r'D:\PROJETOS\FI\simulacao\wizard_forms_novo.py'

# Criar backup
backup = arquivo + '.backup2'
shutil.copy2(arquivo, backup)
print(f"✅ Backup criado: {backup}")

# Ler o arquivo
with open(arquivo, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

print(f"📄 Total de linhas: {len(linhas)}")

# Remover linhas 186-205 (índices 185-204 em Python)
# Essas são as linhas órfãs sem nome de campo
linhas_para_remover = list(range(186, 206))  # 186 a 205 inclusive

print(f"🗑️  Removendo linhas {linhas_para_remover[0]+1} a {linhas_para_remover[-1]+1}")

# Criar nova lista sem as linhas órfãs
novas_linhas = []
for i, linha in enumerate(linhas):
    if i not in linhas_para_remover:
        novas_linhas.append(linha)
    else:
        print(f"   Removendo linha {i+1}: {linha.strip()[:50]}...")

# Salvar arquivo corrigido
with open(arquivo, 'w', encoding='utf-8') as f:
    f.writelines(novas_linhas)

print(f"\n✅ Arquivo corrigido!")
print(f"📊 Linhas antes: {len(linhas)}")
print(f"📊 Linhas depois: {len(novas_linhas)}")
print(f"📊 Linhas removidas: {len(linhas) - len(novas_linhas)}")

# Validar sintaxe
print("\n🔍 Validando sintaxe Python...")
try:
    with open(arquivo, 'r', encoding='utf-8') as f:
        compile(f.read(), arquivo, 'exec')
    print("✅ Sintaxe válida!")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe: {e}")
    print(f"⚠️  Restaurando backup...")
    shutil.copy2(backup, arquivo)
    print("✅ Backup restaurado")
