import os
import sys
import django
from decimal import Decimal
import traceback

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ImobCalc.settings')
django.setup()

from simulacao.calculadora_financeira import (
    calcular_cet,
    calcular_price_sac
)
from simulacao.formatacao import formatar_moeda_brl


def teste_calcular_cet():
    """Testa a função calcular_cet() com tabela SAC."""
    
    # Parâmetros da simulação
    valor_imovel = Decimal('300000')
    taxa_anual = Decimal('7.0')
    num_parcelas = 360
    
    print(f"\n{'='*60}")
    print("TESTE - Cálculo de CET (Custo Efetivo Total)")
    print(f"{'='*60}\n")
    
    # Gerar tabela SAC usando calcular_price_sac
    print(f"Gerando tabela SAC com {num_parcelas} parcelas...")
    resultado = calcular_price_sac(
        metodo='sac',
        valor_principal=float(valor_imovel),
        taxa_anual=float(taxa_anual),
        prazo_meses=num_parcelas
    )
    
    tabela_sac = resultado['tabela']
    print(f"✓ Tabela gerada com {len(tabela_sac)} linhas\n")
    
    # Extrair parcelas como lista de floats
    parcelas_mensais = [float(linha['parcela']) for linha in tabela_sac]
    
    # Definir custos iniciais padrão
    custos_iniciais = {
        'taxa_avaliacao': 2500.0,
        'tarifa_cadastro': 0.0,
        'registro_cartorio_percent': 2.5,
        'itbi_percent': 2.0,
        'custas_registro': 5000.0,
        'taxa_vistoria': 1000.0,
    }
    
    print("Custos iniciais (padrão):")
    for chave, valor in custos_iniciais.items():
        print(f"  {chave}: {valor}")
    print()
    
    # Chamar calcular_cet()
    print("Calculando CET...")
    try:
        resultado_cet = calcular_cet(
            valor_financiado=float(valor_imovel),
            parcelas_mensais=parcelas_mensais,
            custos_iniciais=custos_iniciais
        )
        
        print(f"✓ CET calculado com sucesso!\n")
        
        # Exibir resultados formatados
        print(f"{'='*60}")
        print("RESULTADOS")
        print(f"{'='*60}")
        print(f"CET Mensal:  {resultado_cet['cet_mensal']:.4f}% a.m.")
        print(f"CET Anual:   {resultado_cet['cet_anual']:.4f}% a.a.")
        print(f"{'='*60}\n")
        
        # Detalhamento de custos
        print("DETALHAMENTO DE CUSTOS INICIAIS:")
        for chave, valor in resultado_cet['detalhamento_custos'].items():
            print(f"  {chave}: {formatar_moeda_brl(valor)}")
        print(f"  Total: {formatar_moeda_brl(resultado_cet['total_custos_iniciais'])}\n")
        
        # Resumo da simulação
        print("RESUMO DA SIMULAÇÃO:")
        print(f"  Valor do Imóvel:     {formatar_moeda_brl(float(valor_imovel))}")
        print(f"  Taxa de Juros:       {taxa_anual:.2f}% a.a.")
        print(f"  Número de Parcelas:  {num_parcelas}")
        print(f"  Primeira Parcela:    {formatar_moeda_brl(tabela_sac[0]['parcela'])}")
        print(f"  Última Parcela:      {formatar_moeda_brl(tabela_sac[-1]['parcela'])}")
        print(f"  Valor Líquido Liberado: {formatar_moeda_brl(resultado_cet['valor_liquido_liberado'])}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro ao calcular CET: {e}")
        traceback.print_exc()
        return False


if __name__ == '__main__':
    teste_calcular_cet()