#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
exemplo_uso_sac_realista_simples.py

Demonstra como usar o novo módulo SAC_Realista (sem Django).
"""

from simulacao.sac_realista import SAC_Realista
from datetime import datetime


def formatar_moeda(valor):
    """Formata valor em moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def exemplo_1_contrato_itau():
    """
    Exemplo 1: Simula o contrato Itaú real (TF224 - ALEX GALDINO)
    """
    print("=" * 80)
    print("EXEMPLO 1: Contrato Itaú Realista")
    print("=" * 80)
    
    sac = SAC_Realista(
        saldo_devedor_inicial=327650.72,
        taxa_juros_mensal=0.00557579,  # 6,690948% / 12
        prazo_meses=360,
        taxa_adm_mensal=25.0,
        seguro_mip_mensal=112.22,
        seguro_dfi_mensal=22.16,
        indice_correcao_mensal=1.0,
        data_inicio=datetime(2021, 9, 24),
    )
    
    tabela = sac.gerar_tabela_amortizacao(meses=360)
    resumo = sac.resumo_contrato()
    
    print(f"\n📊 RESUMO GERAL")
    print(f"  Saldo Inicial: {formatar_moeda(resumo['saldo_inicial'])}")
    print(f"  Prazo: {resumo['prazo_meses']} meses ({resumo['prazo_meses']/12:.0f} anos)")
    print(f"  Taxa Mensal: {resumo['taxa_juros_mensal_pct']:.4f}%")
    print(f"  Parcela Primeira: {formatar_moeda(tabela[0]['parcela_total'])}")
    print(f"  Parcela Última: {formatar_moeda(tabela[-1]['parcela_total'])}")
    
    print(f"\n💰 CUSTOS TOTAIS")
    print(f"  Juros: {formatar_moeda(resumo['total_juros'])}")
    print(f"  Taxa Admin: {formatar_moeda(resumo['total_adm'])}")
    print(f"  Seguros (MIP+DFI): {formatar_moeda(resumo['total_seguros_mip'] + resumo['total_seguros_dfi'])}")
    print(f"  TOTAL A PAGAR: {formatar_moeda(resumo['total_pago'])}")
    
    print(f"\n📋 Primeiras 3 parcelas:")
    print(f"{'Mês':<5} | {'Juros':<15} | {'Admin+Seg':<15} | {'Parcela':<15} | {'Saldo':<15}")
    print("-" * 75)
    for i in range(3):
        p = tabela[i]
        admin_seg = p['taxa_adm'] + p['seguro_mip'] + p['seguro_dfi']
        print(
            f"{p['mes']:<5} | "
            f"{formatar_moeda(p['juros']):<15} | "
            f"{formatar_moeda(admin_seg):<15} | "
            f"{formatar_moeda(p['parcela_total']):<15} | "
            f"{formatar_moeda(p['saldo_devedor_novo']):<15}"
        )


def exemplo_2_financiamento_customizado():
    """
    Exemplo 2: Simula um financiamento customizado
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 2: Financiamento Customizado (R$ 300.000)")
    print("=" * 80)
    
    sac = SAC_Realista(
        saldo_devedor_inicial=300000.00,
        taxa_juros_mensal=0.00625,  # 7,5% / 12
        prazo_meses=240,  # 20 anos
        taxa_adm_mensal=20.0,
        seguro_mip_mensal=100.00,
        seguro_dfi_mensal=25.00,
    )
    
    tabela = sac.gerar_tabela_amortizacao(meses=240)
    resumo = sac.resumo_contrato()
    
    print(f"\n📊 RESUMO GERAL")
    print(f"  Saldo Inicial: {formatar_moeda(resumo['saldo_inicial'])}")
    print(f"  Prazo: {resumo['prazo_meses']} meses ({resumo['prazo_meses']/12:.0f} anos)")
    print(f"  Parcela Média: {formatar_moeda(sum(p['parcela_total'] for p in tabela) / len(tabela))}")
    
    print(f"\n💰 CUSTOS TOTAIS")
    print(f"  Juros: {formatar_moeda(resumo['total_juros'])}")
    print(f"  Admin + Seguros: {formatar_moeda(resumo['total_adm'] + resumo['total_seguros_mip'] + resumo['total_seguros_dfi'])}")
    print(f"  TOTAL: {formatar_moeda(resumo['total_pago'])}")
    
    print(f"\n📈 ESTRUTURA DA PARCELA (Mês 1)")
    p1 = tabela[0]
    print(f"  Amortização: {formatar_moeda(p1['amortizacao'])}")
    print(f"  Juros: {formatar_moeda(p1['juros'])}")
    print(f"  Taxa Admin: {formatar_moeda(p1['taxa_adm'])}")
    print(f"  Seguro MIP: {formatar_moeda(p1['seguro_mip'])}")
    print(f"  Seguro DFI: {formatar_moeda(p1['seguro_dfi'])}")
    print(f"  {'─'*40}")
    print(f"  TOTAL: {formatar_moeda(p1['parcela_total'])}")


def exemplo_3_progressao_juros():
    """
    Exemplo 3: Demonstra como os juros diminuem ao longo do SAC
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 3: Progressão de Juros no SAC")
    print("=" * 80)
    
    sac = SAC_Realista(
        saldo_devedor_inicial=100000.00,
        taxa_juros_mensal=0.00833,  # 10% / 12
        prazo_meses=60,
        taxa_adm_mensal=0.0,
        seguro_mip_mensal=0.0,
        seguro_dfi_mensal=0.0,
    )
    
    tabela = sac.gerar_tabela_amortizacao(meses=60)
    
    print(f"\n📊 SAC com {tabela[0]['amortizacao']:.2f} de amortização fixa por mês\n")
    print(f"{'Mês':<5} | {'Juros (R$)':<15} | {'Amort (R$)':<15} | {'Parcela (R$)':<15} | {'Saldo (R$)':<15}")
    print("-" * 75)
    
    # Mostrar alguns meses (1, 10, 20, 30, 40, 50, 60)
    meses_mostrar = [0, 9, 19, 29, 39, 49, 59]
    for idx in meses_mostrar:
        if idx < len(tabela):
            p = tabela[idx]
            print(
                f"{p['mes']:<5} | "
                f"{p['juros']:>13,.2f} | "
                f"{p['amortizacao']:>13,.2f} | "
                f"{p['parcela_total']:>13,.2f} | "
                f"{p['saldo_devedor_novo']:>13,.2f}"
            )
    
    print(f"\n💡 Observe: Juros DIMINUEM, Amortização CONSTANTE → Parcela AUMENTA")


def exemplo_4_amortizacao_extra():
    """
    Exemplo 4: Simula amortização extra via FGTS
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 4: Impacto de Amortizações Extras (FGTS)")
    print("=" * 80)
    
    # Sem FGTS
    sac_sem = SAC_Realista(
        saldo_devedor_inicial=300000.00,
        taxa_juros_mensal=0.00583,  # 7% / 12
        prazo_meses=360,
    )
    
    # Com FGTS (amortização extra em mês 24 e 48)
    fgts = [(24, 20000.0), (48, 30000.0)]
    
    print(f"\n💰 Comparação")
    print(f"  Saldo: {formatar_moeda(300000.00)}")
    print(f"  Taxa: 7% ao ano")
    
    tabela_sem = sac_sem.gerar_tabela_amortizacao(meses=360)
    tabela_com = sac_sem.gerar_tabela_amortizacao(
        meses=360,
        fgts_amortizacoes=fgts
    )
    
    juros_sem = sum(p['juros'] for p in tabela_sem)
    juros_com = sum(p['juros'] for p in tabela_com)
    
    print(f"\n  SEM FGTS:")
    print(f"    Parcelas: {len(tabela_sem)}")
    print(f"    Juros totais: {formatar_moeda(juros_sem)}")
    
    print(f"\n  COM FGTS (50k em 2 anos):")
    print(f"    Parcelas: {len(tabela_com)}")
    print(f"    Juros totais: {formatar_moeda(juros_com)}")
    
    economia_juros = juros_sem - juros_com
    redacao_meses = len(tabela_sem) - len(tabela_com)
    
    print(f"\n  ✅ GANHO:")
    print(f"    Juros economizados: {formatar_moeda(economia_juros)}")
    print(f"    Prazo reduzido: {redacao_meses} meses (~{redacao_meses/12:.1f} anos)")


def exemplo_5_comparacao_cenarios():
    """
    Exemplo 5: Compara 3 cenários diferentes
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 5: Comparação de 3 Cenários")
    print("=" * 80)
    
    valor_imovel = 350000.00
    entrada_20pct = valor_imovel * 0.20
    saldo_financiar = valor_imovel - entrada_20pct
    
    cenarios = [
        {
            'nome': 'Conservador (25 anos)',
            'taxa': 6.5,
            'prazo': 300,
        },
        {
            'nome': 'Moderado (30 anos)',
            'taxa': 7.0,
            'prazo': 360,
        },
        {
            'nome': 'Agressivo (20 anos)',
            'taxa': 7.5,
            'prazo': 240,
        },
    ]
    
    print(f"\nImóvel: {formatar_moeda(valor_imovel)}")
    print(f"Entrada (20%): {formatar_moeda(entrada_20pct)}")
    print(f"A financiar: {formatar_moeda(saldo_financiar)}\n")
    
    print(f"{'Cenário':<25} | {'Parcela Média':<15} | {'Juros Totais':<15} | {'Total a Pagar':<15}")
    print("-" * 80)
    
    for cenario in cenarios:
        sac = SAC_Realista(
            saldo_devedor_inicial=saldo_financiar,
            taxa_juros_mensal=(cenario['taxa'] / 100 / 12),
            prazo_meses=cenario['prazo'],
        )
        
        tabela = sac.gerar_tabela_amortizacao(meses=cenario['prazo'])
        resumo = sac.resumo_contrato()
        
        parcela_media = sum(p['parcela_total'] for p in tabela) / len(tabela)
        
        print(
            f"{cenario['nome']:<25} | "
            f"{formatar_moeda(parcela_media):<15} | "
            f"{formatar_moeda(resumo['total_juros']):<15} | "
            f"{formatar_moeda(resumo['total_pago']):<15}"
        )


if __name__ == '__main__':
    exemplo_1_contrato_itau()
    exemplo_2_financiamento_customizado()
    exemplo_3_progressao_juros()
    exemplo_4_amortizacao_extra()
    exemplo_5_comparacao_cenarios()
    
    print("\n" + "=" * 80)
    print("✅ Exemplos concluídos com sucesso!")
    print("=" * 80)
