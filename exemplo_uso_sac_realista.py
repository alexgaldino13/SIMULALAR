#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
exemplo_uso_sac_realista.py

Demonstra como usar o novo módulo SAC_Realista integrado com o simulador.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ImobCalc.settings')
django.setup()

from simulacao.calculadora_financeira import calcular_sac_contrato_real
from simulacao.formatacao import formatar_moeda_brl


def exemplo_1_contrato_itau():
    """
    Exemplo 1: Simula o contrato Itaú real (TF224 - ALEX GALDINO)
    """
    print("=" * 80)
    print("EXEMPLO 1: Contrato Itaú Realista")
    print("=" * 80)
    
    resultado = calcular_sac_contrato_real(
        saldo_inicial=327650.72,
        taxa_juros_anual=6.690948,  # 6,690948% ao ano
        prazo_meses=360,
        taxa_adm_mensal=25.0,
        seguro_mip_inicial=112.22,
        seguro_dfi_fixo=22.16,
        tr_mensal=1.0,  # Sem TR para simplificar
    )
    
    print(f"\n📊 RESUMO GERAL")
    print(f"  Saldo Inicial: {formatar_moeda_brl(resultado['resumo']['saldo_inicial'])}")
    print(f"  Prazo: {resultado['resumo']['prazo_meses']} meses")
    print(f"  Taxa Mensal: {resultado['resumo']['taxa_juros_mensal_pct']:.4f}%")
    print(f"  Parcela Primeira: {formatar_moeda_brl(resultado['parcela_primeira'])}")
    print(f"  Parcela Última: {formatar_moeda_brl(resultado['parcela_ultima'])}")
    print(f"  Parcela Média: {formatar_moeda_brl(resultado['parcela_media'])}")
    
    print(f"\n💰 CUSTOS TOTAIS")
    print(f"  Juros: {formatar_moeda_brl(resultado['juros_totais'])}")
    print(f"  Taxa Admin + Seguros: {formatar_moeda_brl(resultado['custo_total'] - resultado['juros_totais'])}")
    print(f"  CUSTO TOTAL: {formatar_moeda_brl(resultado['custo_total'])}")
    
    print(f"\n📈 TOTAL A PAGAR")
    print(f"  {formatar_moeda_brl(resultado['resumo']['saldo_inicial'] + resultado['custo_total'])}")
    
    print(f"\n📋 Primeiras 3 parcelas:")
    print(f"{'Mês':<6} | {'Juros':<15} | {'Admin+Seg':<15} | {'Parcela':<15} | {'Saldo':<15}")
    print("-" * 75)
    for i, parcela in enumerate(resultado['tabela'][:3], 1):
        print(
            f"{i:<6} | "
            f"{formatar_moeda_brl(parcela['juros']):<15} | "
            f"{formatar_moeda_brl(parcela['taxa_adm'] + parcela['seguro_mip'] + parcela['seguro_dfi']):<15} | "
            f"{formatar_moeda_brl(parcela['parcela_total']):<15} | "
            f"{formatar_moeda_brl(parcela['saldo_devedor_novo']):<15}"
        )


def exemplo_2_financiamento_customizado():
    """
    Exemplo 2: Simula um financiamento customizado
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 2: Financiamento Customizado (R$ 300.000)")
    print("=" * 80)
    
    resultado = calcular_sac_contrato_real(
        saldo_inicial=300000.00,
        taxa_juros_anual=7.50,  # Taxa de 7,50% ao ano
        prazo_meses=240,  # 20 anos
        taxa_adm_mensal=20.0,
        seguro_mip_inicial=100.00,
        seguro_dfi_fixo=25.00,
    )
    
    print(f"\n📊 RESUMO GERAL")
    print(f"  Saldo Inicial: {formatar_moeda_brl(resultado['resumo']['saldo_inicial'])}")
    print(f"  Prazo: {resultado['resumo']['prazo_meses']} meses ({resultado['resumo']['prazo_meses'] / 12:.0f} anos)")
    print(f"  Taxa Mensal: {resultado['resumo']['taxa_juros_mensal_pct']:.4f}%")
    print(f"  Parcela Média: {formatar_moeda_brl(resultado['parcela_media'])}")
    
    print(f"\n💰 CUSTOS TOTAIS")
    print(f"  Juros: {formatar_moeda_brl(resultado['juros_totais'])}")
    print(f"  Admin + Seguros: {formatar_moeda_brl(resultado['custo_total'] - resultado['juros_totais'])}")
    print(f"  TOTAL: {formatar_moeda_brl(resultado['custo_total'])}")
    
    print(f"\n📈 ESTRUTURA DA PARCELA (Mês 1)")
    parcela_1 = resultado['tabela'][0]
    print(f"  Amortização: {formatar_moeda_brl(parcela_1['amortizacao'])}")
    print(f"  Juros: {formatar_moeda_brl(parcela_1['juros'])}")
    print(f"  Taxa Admin: {formatar_moeda_brl(parcela_1['taxa_adm'])}")
    print(f"  Seguro MIP: {formatar_moeda_brl(parcela_1['seguro_mip'])}")
    print(f"  Seguro DFI: {formatar_moeda_brl(parcela_1['seguro_dfi'])}")
    print(f"  ────────────")
    print(f"  TOTAL: {formatar_moeda_brl(parcela_1['parcela_total'])}")


def exemplo_3_comparacao_com_price():
    """
    Exemplo 3: Demonstra diferença entre SAC e PRICE
    (SAC tem parcelas que diminuem, PRICE tem parcelas fixas)
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 3: SAC vs PRICE - Demonstração")
    print("=" * 80)
    
    sac = calcular_sac_contrato_real(
        saldo_inicial=100000.00,
        taxa_juros_anual=10.0,
        prazo_meses=60,  # 5 anos
    )
    
    print(f"\n📊 SAC (Sistema de Amortização Constante)")
    print(f"  Saldo: {formatar_moeda_brl(sac['resumo']['saldo_inicial'])}")
    print(f"  Taxa: 10% ao ano")
    print(f"  Prazo: 60 meses")
    print(f"\n  Evolução das parcelas:")
    print(f"  Mês 1: {formatar_moeda_brl(sac['tabela'][0]['parcela_total'])} (menor juros)")
    print(f"  Mês 30: {formatar_moeda_brl(sac['tabela'][29]['parcela_total'])}")
    print(f"  Mês 60: {formatar_moeda_brl(sac['tabela'][59]['parcela_total'])} (maior juros)")
    print(f"\n  ⚠️  No SAC, as parcelas AUMENTAM ao longo do tempo!")
    print(f"      (Amortização constante + Juros decrescentes = Parcela variável)")
    
    # Nota: Para PRICE, seria necessário usar calcular_price_sac('price', ...)
    print(f"\n🔄 Diferença PRICE:")
    print(f"   - PRICE: Parcela fixa de ~{sac['parcela_media']:.2f}")
    print(f"   - SAC: Parcelas variam de {sac['parcela_ultima']:.2f} até {sac['parcela_primeira']:.2f}")


def exemplo_4_amortizacao_extra_fgts():
    """
    Exemplo 4: Simula amortização extra via FGTS
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 4: Amortização Extra via FGTS")
    print("=" * 80)
    
    # Simula amortizações extras no mês 24 e 48
    fgts_amort = [
        (24, 20000.00),  # 20 mil em fevereiro (ano 2)
        (48, 30000.00),  # 30 mil em fevereiro (ano 4)
    ]
    
    resultado = calcular_sac_contrato_real(
        saldo_inicial=300000.00,
        taxa_juros_anual=7.0,
        prazo_meses=360,
        fgts_amortizacoes=fgts_amort,
    )
    
    print(f"\n💰 IMPACTO DO FGTS")
    print(f"  Sem FGTS: ~360 meses")
    print(f"  Com FGTS (R$ 50.000): {resultado['quantidade_parcelas']} meses")
    print(f"  Redução: {360 - resultado['quantidade_parcelas']} meses (~{(360 - resultado['quantidade_parcelas']) / 12:.1f} anos)")
    
    print(f"\n📉 Juros economizados com FGTS: ~{formatar_moeda_brl((resultado['resumo']['total_juros']))}")


def exemplo_5_integracao_wizard():
    """
    Exemplo 5: Mostra como integrar com o wizard
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 5: Integração com Wizard ImobCalc")
    print("=" * 80)
    
    # Dados que viriam do wizard
    dados_wizard = {
        'valor_imovel': 350000.00,
        'entrada': 50000.00,
        'renda_familiar': 5000.00,
        'prazo_preferido': 25,  # anos
        'cidade': 'São Paulo',
    }
    
    saldo_financiar = dados_wizard['valor_imovel'] - dados_wizard['entrada']
    prazo_meses = dados_wizard['prazo_preferido'] * 12
    
    print(f"\n📍 Dados do Cenário (Wizard)")
    print(f"  Local: {dados_wizard['cidade']}")
    print(f"  Valor do Imóvel: {formatar_moeda_brl(dados_wizard['valor_imovel'])}")
    print(f"  Entrada (20%): {formatar_moeda_brl(dados_wizard['entrada'])}")
    print(f"  Financiamento: {formatar_moeda_brl(saldo_financiar)}")
    print(f"  Renda Familiar: {formatar_moeda_brl(dados_wizard['renda_familiar'])}")
    print(f"  Prazo Desejado: {dados_wizard['prazo_preferido']} anos")
    
    resultado = calcular_sac_contrato_real(
        saldo_inicial=saldo_financiar,
        taxa_juros_anual=7.5,
        prazo_meses=prazo_meses,
        taxa_adm_mensal=25.0,
        seguro_mip_inicial=150.0,
    )
    
    print(f"\n💳 Cálculo da Parcela")
    print(f"  Parcela Mensal: {formatar_moeda_brl(resultado['parcela_media'])}")
    print(f"  % da Renda: {(resultado['parcela_media'] / dados_wizard['renda_familiar']) * 100:.1f}%")
    
    if (resultado['parcela_media'] / dados_wizard['renda_familiar']) > 0.30:
        print(f"  ⚠️  Atenção: Parcela > 30% da renda (limite recomendado)")
    else:
        print(f"  ✓ Parcela dentro do limite recomendado (<30% da renda)")


if __name__ == '__main__':
    exemplo_1_contrato_itau()
    exemplo_2_financiamento_customizado()
    exemplo_3_comparacao_com_price()
    exemplo_4_amortizacao_extra_fgts()
    exemplo_5_integracao_wizard()
    
    print("\n" + "=" * 80)
    print("✅ Exemplos concluídos com sucesso!")
    print("=" * 80)
