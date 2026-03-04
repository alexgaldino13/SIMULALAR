"""
Teste das funções calcular_cet_completo() e calcular_mcmv()
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ImobCalc.settings')
django.setup()

from simulacao.calculadora_financeira import (
    calcular_cet_completo,
    calcular_mcmv,
)
from simulacao.formatacao import formatar_moeda_brl


def teste_cet_completo():
    """Testa calcular_cet_completo() com cenário realista."""
    
    print(f"\n{'='*70}")
    print("TESTE 1: CET Completo (Todas as Taxas)")
    print(f"{'='*70}\n")
    
    # Parâmetros
    valor_imovel = 300000.0
    valor_financiado = 240000.0  # 80% do imóvel
    taxa_juros_anual = 7.0
    prazo_meses = 360
    
    print(f"CENÁRIO:")
    print(f"  Valor do Imóvel:     {formatar_moeda_brl(valor_imovel)}")
    print(f"  Valor Financiado:    {formatar_moeda_brl(valor_financiado)}")
    print(f"  Taxa de Juros:       {taxa_juros_anual}% a.a.")
    print(f"  Prazo:               {prazo_meses} meses ({prazo_meses // 12} anos)")
    print()
    
    try:
        resultado = calcular_cet_completo(
            valor_imovel=valor_imovel,
            valor_financiado=valor_financiado,
            taxa_juros_anual=taxa_juros_anual,
            prazo_meses=prazo_meses,
            seguro_mip_taxa_anual=0.6,
            seguro_dfi_taxa_anual=0.3,
            taxa_administracao=25.0,
            taxa_avaliacao=2500.0,
            registro_cartorio_percent=2.5,
            itbi_percent=2.0,
            custas_registro=5000.0,
            taxa_vistoria=1000.0,
            iof_percent=0.0,
        )
        
        print(f"{'='*70}")
        print("RESULTADOS - CET COMPLETO")
        print(f"{'='*70}\n")
        
        print(f"CET Mensal:          {resultado['cet_mensal']:.4f}% a.m.")
        print(f"CET Anual:           {resultado['cet_anual']:.4f}% a.a.")
        print(f"Taxa Nominal:        {resultado['taxa_nominal_anual']:.2f}% a.a.")
        print(f"Diferença (CET-Nom): {(resultado['cet_anual'] - resultado['taxa_nominal_anual']):.2f}%")
        print()
        
        print("DETALHAMENTO DE CUSTOS INICIAIS:")
        for chave, valor in resultado['detalhamento_custos'].items():
            if isinstance(valor, float):
                print(f"  {chave:.<40} {formatar_moeda_brl(valor)}")
        
        print(f"  {'Total Custos':-<40} {formatar_moeda_brl(resultado['total_custos_iniciais'])}")
        print()
        
        print(f"Valor Líquido Liberado: {formatar_moeda_brl(resultado['valor_liquido_liberado'])}")
        print(f"Parcela Média:          {formatar_moeda_brl(resultado['parcela_media'])}")
        print(f"Parcela Mínima:         {formatar_moeda_brl(resultado['parcela_minima'])}")
        print(f"Parcela Máxima:         {formatar_moeda_brl(resultado['parcela_maxima'])}")
        print()
        
        print(f"✅ TESTE CET COMPLETO: PASSOU")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def teste_mcmv():
    """Testa calcular_mcmv() com 3 faixas de renda."""
    
    print(f"\n{'='*70}")
    print("TESTE 2: MCMV (Minha Casa Minha Vida)")
    print(f"{'='*70}\n")
    
    testes_mcmv = [
        {
            'nome': 'Faixa 1 (Renda Baixa)',
            'renda': 2400.0,
            'imovel': 150000.0,
            'entrada': 0.0,
        },
        {
            'nome': 'Faixa 2 (Renda Média)',
            'renda': 3500.0,
            'imovel': 200000.0,
            'entrada': 20000.0,
        },
        {
            'nome': 'Faixa 3 (Renda Média-Alta)',
            'renda': 6000.0,
            'imovel': 300000.0,
            'entrada': 50000.0,
        },
    ]
    
    resultados = []
    
    for teste in testes_mcmv:
        print(f"\n{'-'*70}")
        print(f"CENÁRIO: {teste['nome']}")
        print(f"  Renda Familiar:      {formatar_moeda_brl(teste['renda'])}")
        print(f"  Valor do Imóvel:     {formatar_moeda_brl(teste['imovel'])}")
        print(f"  Entrada Disponível:  {formatar_moeda_brl(teste['entrada'])}")
        
        try:
            resultado = calcular_mcmv(
                valor_imovel=teste['imovel'],
                renda_familiar_mensal=teste['renda'],
                valor_entrada=teste['entrada'],
                prazo_meses=360,
                usa_fgts=True,
                valor_fgts_disponivel=10000.0,
            )
            
            if resultado['qualificado']:
                print(f"\n  ✅ QUALIFICADO!")
                print(f"    Faixa:               {resultado['faixa']}")
                print(f"    Subsídio:            {formatar_moeda_brl(resultado['subsidio'])}")
                print(f"    Taxa de Juros:       {resultado['taxa_juros']}% a.a.")
                print(f"    Valor a Financiar:   {formatar_moeda_brl(resultado['valor_financiado'])}")
                print(f"    Parcela Média:       {formatar_moeda_brl(resultado['parcela_media'])}")
                print(f"    Economia vs Mercado: {formatar_moeda_brl(resultado['economia_vs_tradicional'])}")
                resultados.append(True)
            else:
                print(f"\n  ❌ NÃO QUALIFICADO: {resultado['motivo']}")
                resultados.append(False)
        
        except Exception as e:
            print(f"\n  ❌ ERRO: {e}")
            import traceback
            traceback.print_exc()
            resultados.append(False)
    
    print(f"\n{'='*70}")
    print(f"RESUMO: {sum(resultados)}/{len(resultados)} testes passaram")
    print(f"{'='*70}\n")
    
    return all(resultados)


def teste_cet_com_mcmv():
    """Testa CET para um financiamento MCMV."""
    
    print(f"\n{'='*70}")
    print("TESTE 3: CET para Financiamento MCMV")
    print(f"{'='*70}\n")
    
    # Simular MCMV Faixa 2
    valor_imovel = 200000.0
    renda = 3500.0
    entrada = 20000.0
    
    resultado_mcmv = calcular_mcmv(
        valor_imovel=valor_imovel,
        renda_familiar_mensal=renda,
        valor_entrada=entrada,
        prazo_meses=360,
    )
    
    if not resultado_mcmv['qualificado']:
        print(f"❌ Não qualificado: {resultado_mcmv['motivo']}")
        return False
    
    print(f"CENÁRIO: MCMV Faixa {resultado_mcmv['faixa']}")
    print(f"  Valor do Imóvel:     {formatar_moeda_brl(resultado_mcmv['valor_imovel'])}")
    print(f"  Renda Familiar:      {formatar_moeda_brl(resultado_mcmv['renda_familia'])}")
    print(f"  Subsídio:            {formatar_moeda_brl(resultado_mcmv['subsidio'])}")
    print(f"  Valor Financiado:    {formatar_moeda_brl(resultado_mcmv['valor_financiado'])}")
    print()
    
    # Calcular CET para este financiamento
    try:
        resultado_cet = calcular_cet_completo(
            valor_imovel=valor_imovel,
            valor_financiado=resultado_mcmv['valor_financiado'],
            taxa_juros_anual=resultado_mcmv['taxa_juros'],
            prazo_meses=360,
            seguro_mip_taxa_anual=resultado_mcmv['seguro_mip_taxa'],
            seguro_dfi_taxa_anual=resultado_mcmv['seguro_dfi_taxa'],
            taxa_administracao=0.0,  # MCMV sem taxa de administração
        )
        
        print(f"{'='*70}")
        print("CET DO FINANCIAMENTO MCMV")
        print(f"{'='*70}\n")
        
        print(f"CET Anual:           {resultado_cet['cet_anual']:.4f}% a.a.")
        print(f"CET Mensal:          {resultado_cet['cet_mensal']:.4f}% a.m.")
        print(f"Taxa Nominal:        {resultado_cet['taxa_nominal_anual']:.2f}% a.a.")
        print(f"Diferença:           {(resultado_cet['cet_anual'] - resultado_cet['taxa_nominal_anual']):.2f}%")
        print()
        
        print(f"Economia vs MCMV:    {formatar_moeda_brl(resultado_mcmv['economia_vs_tradicional'])}")
        print(f"Parcela Média MCMV:  {formatar_moeda_brl(resultado_mcmv['parcela_media'])}")
        print()
        
        print(f"✅ TESTE CET+MCMV: PASSOU")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print(f"\n{'#'*70}")
    print("# TESTES: CET Completo e MCMV")
    print(f"{'#'*70}")
    
    resultado1 = teste_cet_completo()
    resultado2 = teste_mcmv()
    resultado3 = teste_cet_com_mcmv()
    
    print(f"\n{'='*70}")
    print(f"RESUMO FINAL")
    print(f"{'='*70}")
    print(f"  CET Completo:        {'✅ PASSOU' if resultado1 else '❌ FALHOU'}")
    print(f"  MCMV:                {'✅ PASSOU' if resultado2 else '❌ FALHOU'}")
    print(f"  CET + MCMV:          {'✅ PASSOU' if resultado3 else '❌ FALHOU'}")
    print(f"{'='*70}\n")
    
    if all([resultado1, resultado2, resultado3]):
        print(f"🎉 TODOS OS TESTES PASSARAM!\n")
        sys.exit(0)
    else:
        print(f"⚠️ ALGUNS TESTES FALHARAM\n")
        sys.exit(1)
