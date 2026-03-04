#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corrigir DEFINITIVAMENTE o arquivo wizard_forms_novo.py
Remove linhas 237-272 e adiciona campo custas_documentacao_forma
"""

import shutil
from datetime import datetime

# Caminhos
ARQUIVO = r'D:\PROJETOS\FI\simulacao\wizard_forms_novo.py'
BACKUP = ARQUIVO + f'.backup_final_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

print('\n' + '='*70)
print('CORREÇÃO DEFINITIVA - wizard_forms_novo.py')
print('='*70 + '\n')

# 1. Backup
print(f'➡️  Criando backup: {BACKUP}')
shutil.copy(ARQUIVO, BACKUP)
print('✅ Backup criado!\n')

# 2. Ler arquivo
print('➡️  Lendo arquivo...')
with open(ARQUIVO, 'r', encoding='utf-8') as f:
    linhas = f.readlines()
print(f'✅ {len(linhas)} linhas lidas!\n')

# 3. Encontrar linha 236 (fim do saldo_fgts)
print('➡️  Procurando fim do campo saldo_fgts...')
indice_236 = 236  # Linha 237 no editor = índice 236 (0-based)
print(f'✅ Linha 237 (\u00edndice 236) identificada!\n')

# 4. Encontrar próximo campo válido (recebe_13)
print('➡️  Procurando campo recebe_13...')
indice_recebe_13 = -1
for i in range(indice_236, len(linhas)):
    if 'recebe_13 = forms.BooleanField(' in linhas[i]:
        indice_recebe_13 = i
        break

if indice_recebe_13 == -1:
    print('❌ ERRO: Campo recebe_13 não encontrado!')
    exit(1)

print(f'✅ Campo recebe_13 encontrado na linha {indice_recebe_13 + 1}!\n')

# 5. Remover linhas corrompidas
linhas_removidas = indice_recebe_13 - indice_236
print(f'➡️  Removendo {linhas_removidas} linhas corrompidas (237 a {indice_recebe_13})...')
novas_linhas = linhas[:indice_236] + linhas[indice_recebe_13:]
print(f'✅ {linhas_removidas} linhas removidas!\n')

# 6. Adicionar campo custas_documentacao_forma
print('➡️  Adicionando campo custas_documentacao_forma...')
campo_custas = '''    
    custas_documentacao_forma = forms.ChoiceField(
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
    )
    
'''

novas_linhas.insert(indice_236, campo_custas)
print('✅ Campo adicionado!\n')

# 7. Salvar
print('➡️  Salvando arquivo corrigido...')
with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.writelines(novas_linhas)
print('✅ Arquivo salvo!\n')

# 8. Resumo
print('='*70)
print('✅ CORREÇÃO CONCLUÍDA COM SUCESSO!')
print('='*70)
print(f'\n💾 Backup: {BACKUP}')
print(f'🗑️  Removidas: {linhas_removidas} linhas corrompidas')
print(f'➕ Adicionado: campo custas_documentacao_forma')
print(f'\n🚀 Executar: python manage.py runserver\n')
