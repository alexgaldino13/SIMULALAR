#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corrigir o arquivo wizard_forms_novo.py
Adiciona o campo custas_documentacao_forma corretamente
"""

import os
import shutil
from datetime import datetime

# Caminhos
ARQUIVO = r'D:\PROJETOS\FI\simulacao\wizard_forms_novo.py'
BACKUP = ARQUIVO + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

print('\n' + '='*60)
print('CORREÇÃO DO ARQUIVO wizard_forms_novo.py')
print('='*60 + '\n')

# 1. Fazer backup
print(f'➡️  Criando backup: {os.path.basename(BACKUP)}')
shutil.copy(ARQUIVO, BACKUP)
print('✅ Backup criado!\n')

# 2. Ler arquivo
print('➡️  Lendo arquivo...')
with open(ARQUIVO, 'r', encoding='utf-8') as f:
    linhas = f.readlines()
print(f'✅ {len(linhas)} linhas lidas!\n')

# 3. Encontrar linha do saldo_fgts
print('➡️  Procurando campo saldo_fgts...')
indice_fgts = -1
for i, linha in enumerate(linhas):
    if 'saldo_fgts = forms.DecimalField(' in linha:
        indice_fgts = i
        break

if indice_fgts == -1:
    print('❌ ERRO: Campo saldo_fgts não encontrado!')
    exit(1)

print(f'✅ Encontrado na linha {indice_fgts + 1}!\n')

# 4. Encontrar fim do campo saldo_fgts
print('➡️  Procurando fim do campo saldo_fgts...')
indice_fim_fgts = -1
for i in range(indice_fgts, len(linhas)):
    if linhas[i].strip() == ')' and i > indice_fgts:
        indice_fim_fgts = i
        break

if indice_fim_fgts == -1:
    print('❌ ERRO: Fim do campo saldo_fgts não encontrado!')
    exit(1)

print(f'✅ Fim encontrado na linha {indice_fim_fgts + 1}!\n')

# 5. Encontrar próximo campo (recebe_13 ou qualquer outro)
print('➡️  Procurando próximo campo...')
indice_proximo_campo = -1
for i in range(indice_fim_fgts + 1, len(linhas)):
    linha_stripped = linhas[i].strip()
    if linha_stripped and not linha_stripped.startswith('#') and '=' in linha_stripped:
        # Encontrou um campo
        indice_proximo_campo = i
        break

if indice_proximo_campo == -1:
    print('❌ ERRO: Próximo campo não encontrado!')
    exit(1)

print(f'✅ Próximo campo encontrado na linha {indice_proximo_campo + 1}!\n')

# 6. Remover linhas corrompidas entre fim_fgts e proximo_campo
print(f'➡️  Removendo linhas corrompidas ({indice_fim_fgts + 2} a {indice_proximo_campo})...')
linhas_removidas = indice_proximo_campo - indice_fim_fgts - 1
novas_linhas = linhas[:indice_fim_fgts + 1] + linhas[indice_proximo_campo:]
print(f'✅ {linhas_removidas} linhas removidas!\n')

# 7. Adicionar campo custas_documentacao_forma
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

# Inserir campo após saldo_fgts
novas_linhas.insert(indice_fim_fgts + 1, campo_custas)
print('✅ Campo adicionado!\n')

# 8. Salvar arquivo
print('➡️  Salvando arquivo corrigido...')
with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.writelines(novas_linhas)
print('✅ Arquivo salvo!\n')

# 9. Resumo
print('='*60)
print('✅ CORREÇÃO CONCLUÍDA COM SUCESSO!')
print('='*60)
print(f'\n💾 Backup salvo em: {BACKUP}')
print(f'📝 Campo custas_documentacao_forma adicionado após linha {indice_fim_fgts + 1}')
print(f'🗑️  {linhas_removidas} linhas corrompidas removidas')
print(f'\n🚀 Próximo passo: python manage.py runserver\n')
