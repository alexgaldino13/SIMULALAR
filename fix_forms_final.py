#!/usr/bin/env python
# -*- coding: utf-8 -*-

print('Corrigindo wizard_forms_novo.py...')

with open('simulacao/wizard_forms_novo.py', 'r', encoding='utf-8') as f:
    content = f.read()

print(f'Tamanho original: {len(content)} caracteres')

# Adicionar fechamento do campo e novo campo
if content.endswith('help_text="🔍 Ajuda a prever estabilidade e possibilidade de mudança"'):
    content += '''
    )
    
    elegivel_mcmv = forms.BooleanField(
        label="Renda familiar se enquadra no Minha Casa Minha Vida? (até R$ 8.000)",
        required=False,
        initial=False,
        help_text="🏠 MCMV oferece subsídios de até R$ 55.000"
    )
'''
    print('Adicionado fechamento e campo elegivel_mcmv')
else:
    print('AVISO: Final do arquivo não corresponde ao esperado')
    print('Últimos 100 caracteres:', repr(content[-100:]))

with open('simulacao/wizard_forms_novo.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Arquivo salvo!')
print('Execute: python manage.py runserver')
