from decimal import Decimal
import math
import sys
import os

# Adiciona o diretório do projeto ao path para importar a calculadora
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from simulacao.calculadora_financeira import calcular_price_sac

def audit_simulations():
    print("=== SIMULALAR FINANCIAL AUDIT 2026 ===")
    
    # Cenário Base: R$ 500.000, 10.5% a.a., 360 meses (30 anos)
    principal = Decimal('500000')
    taxa_anual = Decimal('10.5')
    prazo = 360
    idade = 35
    
    print(f"\nCenário: R$ {principal:,.2f} | {taxa_anual}% a.a. | {prazo} meses | Idade: {idade}")
    
    # 1. Teste SAC
    sac_res = calcular_price_sac('sac', principal, taxa_anual, prazo, idade=idade)
    print("\n--- Tabela SAC ---")
    print(f"Parcela Inicial: R$ {sac_res['parcela_inicial']:,.2f}")
    print(f"Última Parcela: R$ {sac_res['ultima_parcela']:,.2f}")
    print(f"Total Juros: R$ {sac_res['total_juros']:,.2f}")
    print(f"Total Seguros/Taxas: R$ {sac_res['total_seguros_taxas']:,.2f}")
    
    # Validação Matemática SAC: 
    # Amortização Constant = 500.000 / 360 = 1388.89
    # Juros Mês 1 = 500.000 * (10.5 / 12 / 100) = 500.000 * 0.00875 = 4375.00
    expected_amort = principal / prazo
    expected_juros_1 = principal * (taxa_anual / 12 / 100)
    print(f"SAC Amortização Esperada: {expected_amort:,.2f}")
    print(f"SAC Juros 1 Esperado: {expected_juros_1:,.2f}")
    
    # 2. Teste PRICE
    price_res = calcular_price_sac('price', principal, taxa_anual, prazo, idade=idade)
    print("\n--- Tabela PRICE ---")
    print(f"Parcela (Principal + Juros): R$ {price_res['parcela_inicial']:,.2f}")
    print(f"Total Juros: R$ {price_res['total_juros']:,.2f}")
    
    # Validação PRICE PMT:
    i = taxa_anual / 100 / 12
    n = prazo
    pmt = principal * ( (i * (1+i)**n) / ((1+i)**n - 1) )
    print(f"PRICE PMT Esperado (Principal + Juros): {pmt:,.2f}")
    
    # 3. Teste Amortização FGTS (Reduzindo Prazo)
    # Amortização de R$ 50k no mês 24
    fgts_res = calcular_price_sac('sac', principal, taxa_anual, prazo, 
                                  idade=idade, 
                                  usar_fgts_financiamento=True, 
                                  fgts_saldo=50000, 
                                  mes_uso_fgts_financiamento=24,
                                  tipo_amortizacao_fgts='reduzir_prazo')
    
    prazo_original = sac_res['prazo_final_meses']
    prazo_novo = fgts_res['prazo_final_meses']
    reducao = prazo_original - prazo_novo
    
    print("\n--- Teste FGTS (Redução de Prazo) ---")
    print(f"Prazo Original: {prazo_original} meses")
    print(f"Prazo pós-amortização (R$ 50k): {prazo_novo} meses")
    print(f"Meses economizados: {reducao}")
    print(f"Economia de Juros: R$ {sac_res['total_juros'] - fgts_res['total_juros']:,.2f}")

if __name__ == "__main__":
    audit_simulations()
