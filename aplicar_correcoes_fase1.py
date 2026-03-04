#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para aplicar correções da FASE 1 - CRÍTICO
Projeto: Calculadora Imobiliária
"""

import os
import re

# Caminho base do projeto
BASE_DIR = r"D:\PROJETOS\FI\simulacao"

def backup_file(filepath):
    """Cria backup do arquivo antes de modificar"""
    backup_path = filepath + ".backup"
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup criado: {backup_path}")

def correcao_1_remover_campo_duplicado():
    """Remove campos duplicados tem_imovel_proprio e valor_imovel_proprio da WizardCapitalForm"""
    filepath = os.path.join(BASE_DIR, "wizard_forms_novo.py")
    
    print("\n🔴 CORREÇÃO 1: Removendo campos duplicados...")
    backup_file(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Encontrar e remover as linhas 187-208 (campos duplicados na WizardCapitalForm)
    new_lines = []
    skip_lines = False
    in_capital_form = False
    
    for i, line in enumerate(lines, 1):
        # Detectar início da WizardCapitalForm
        if 'class WizardCapitalForm' in line:
            in_capital_form = True
            new_lines.append(line)
            continue
        
        # Detectar fim da WizardCapitalForm (próxima classe)
        if in_capital_form and line.strip().startswith('class ') and 'WizardCapitalForm' not in line:
            in_capital_form = False
        
        # Remover campos duplicados apenas dentro da WizardCapitalForm
        if in_capital_form:
            if 'tem_imovel_proprio' in line or 'valor_imovel_proprio' in line:
                # Pular esta linha e as próximas até encontrar o próximo campo
                skip_lines = True
                continue
            
            if skip_lines:
                # Continuar pulando até encontrar próximo campo ou método
                if line.strip() and not line.strip().startswith(')') and not line.strip().startswith(','):
                    if '=' in line or 'def ' in line or 'class ' in line:
                        skip_lines = False
                    else:
                        continue
                else:
                    continue
        
        new_lines.append(line)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ Campos duplicados removidos de WizardCapitalForm")

def correcao_2_validacao_entrada():
    """Adiciona validação de entrada mínima (20%) na WizardObjetivoForm"""
    filepath = os.path.join(BASE_DIR, "wizard_forms_novo.py")
    
    print("\n🔴 CORREÇÃO 2: Adicionando validação de entrada mínima...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Procurar a classe WizardObjetivoForm
    if 'class WizardObjetivoForm' in content:
        # Adicionar método clean após a definição dos campos
        validation_code = '''
    def clean(self):
        cleaned_data = super().clean()
        valor_imovel = cleaned_data.get('valor_imovel', 0)
        poupanca = cleaned_data.get('poupanca', 0) or 0
        fgts = cleaned_data.get('fgts', 0) or 0
        entrada_total = poupanca + fgts
        
        if valor_imovel and entrada_total < valor_imovel * 0.20:
            raise forms.ValidationError(
                'Entrada insuficiente. É necessário no mínimo 20% do valor do imóvel. '
                f'Valor mínimo: R$ {valor_imovel * 0.20:,.2f}'
            )
        return cleaned_data
'''
        
        # Encontrar o final da classe WizardObjetivoForm
        pattern = r'(class WizardObjetivoForm.*?)(class \w+|$)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            objetivo_form_content = match.group(1)
            # Adicionar o método clean antes da próxima classe
            if 'def clean(self):' not in objetivo_form_content:
                # Encontrar a última linha da classe
                lines = objetivo_form_content.split('\n')
                # Inserir antes da próxima classe
                new_content = content.replace(match.group(1), objetivo_form_content + validation_code + '\n')
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print("✅ Validação de entrada mínima adicionada")
            else:
                print("⚠️  Validação já existe")
        else:
            print("❌ Não foi possível encontrar WizardObjetivoForm")
    else:
        print("❌ WizardObjetivoForm não encontrada")

def correcao_3_validacao_renda():
    """Adiciona validação de comprometimento de renda (35%) na WizardRendaCustosForm"""
    filepath = os.path.join(BASE_DIR, "wizard_forms_novo.py")
    
    print("\n🔴 CORREÇÃO 3: Adicionando validação de comprometimento de renda...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    validation_code = '''
    def clean(self):
        cleaned_data = super().clean()
        renda_familiar = cleaned_data.get('renda_familiar', 0)
        
        # Armazenar comprometimento máximo para usar nos cálculos
        if renda_familiar:
            cleaned_data['comprometimento_maximo'] = renda_familiar * 0.35
        
        return cleaned_data
'''
    
    # Procurar a classe WizardRendaCustosForm
    if 'class WizardRendaCustosForm' in content:
        pattern = r'(class WizardRendaCustosForm.*?)(class \w+|$)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            renda_form_content = match.group(1)
            if 'def clean(self):' not in renda_form_content:
                new_content = content.replace(match.group(1), renda_form_content + validation_code + '\n')
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print("✅ Validação de comprometimento de renda adicionada")
            else:
                print("⚠️  Validação já existe")
        else:
            print("❌ Não foi possível encontrar WizardRendaCustosForm")
    else:
        print("❌ WizardRendaCustosForm não encontrada")

def main():
    print("=" * 60)
    print("APLICANDO CORREÇÕES DA FASE 1 - CRÍTICO")
    print("Projeto: Calculadora Imobiliária")
    print("=" * 60)
    
    try:
        correcao_1_remover_campo_duplicado()
        correcao_2_validacao_entrada()
        correcao_3_validacao_renda()
        
        print("\n" + "=" * 60)
        print("✅ TODAS AS CORREÇÕES APLICADAS COM SUCESSO!")
        print("=" * 60)
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Teste o wizard no navegador: http://127.0.0.1:8000/wizard-novo/")
        print("2. Verifique se os campos duplicados sumiram")
        print("3. Teste as validações de entrada e renda")
        print("4. Se algo der errado, restaure os backups (.backup)")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("Restaure os arquivos .backup se necessário")

if __name__ == "__main__":
    main()
