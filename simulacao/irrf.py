from decimal import Decimal

"""
Módulo para cálculo de IRRF (Imposto de Renda Retido na Fonte) sobre aplicações financeiras.

Tabela de alíquotas conforme legislação brasileira:
- Até 180 dias: 22,5%
- De 181 a 360 dias: 20%
- De 361 a 720 dias: 17,5%
- Acima de 720 dias: 15%
"""


def calcular_irrf(valor_rendimento, dias_aplicacao):
    """
    Calcula o IRRF sobre o rendimento de uma aplicação financeira.
    
    Args:
        valor_rendimento: Valor do rendimento (lucro) da aplicação
        dias_aplicacao: Número de dias que o dinheiro ficou aplicado
    
    Returns:
        dict com:
            - irrf: Valor do imposto a ser retido
            - aliquota: Alíquota aplicada (em decimal)
            - valor_liquido: Rendimento líquido após IRRF
    """
    # Conversão para Decimal para precisão
    valor_rendimento = Decimal(str(valor_rendimento))
    
    # Determina a alíquota baseada no prazo
    if dias_aplicacao <= 180:
        aliquota = Decimal('0.225')  # 22,5%
    elif dias_aplicacao <= 360:
        aliquota = Decimal('0.20')   # 20%
    elif dias_aplicacao <= 720:
        aliquota = Decimal('0.175')  # 17,5%
    else:
        aliquota = Decimal('0.15')   # 15%
    
    # Calcula o IRRF
    irrf = valor_rendimento * aliquota
    valor_liquido = valor_rendimento - irrf
    
    return {
        'irrf': irrf,
        'aliquota': aliquota,
        'aliquota_percentual': float(aliquota * 100),
        'valor_liquido': valor_liquido
    }


def calcular_rendimento_com_irrf(valor_inicial, taxa_juros, dias_aplicacao):
    """
    Calcula o rendimento de uma aplicação já descontando o IRRF.
    
    Args:
        valor_inicial: Valor inicial da aplicação
        taxa_juros: Taxa de juros (em decimal, ex: 0.10 para 10%)
        dias_aplicacao: Número de dias da aplicação
    
    Returns:
        dict com:
            - valor_inicial: Valor investido
            - valor_bruto: Valor final antes do IRRF
            - rendimento_bruto: Lucro antes do IRRF
            - irrf: Valor do imposto
            - aliquota_percentual: Alíquota aplicada em %
            - rendimento_liquido: Lucro após IRRF
            - valor_final_liquido: Valor final após IRRF
    """
    valor_inicial = Decimal(str(valor_inicial))
    taxa_juros = Decimal(str(taxa_juros))
    
    # Calcula rendimento bruto
    rendimento_bruto = valor_inicial * taxa_juros
    valor_bruto = valor_inicial + rendimento_bruto
    
    # Calcula IRRF sobre o rendimento
    resultado_irrf = calcular_irrf(rendimento_bruto, dias_aplicacao)
    
    return {
        'valor_inicial': valor_inicial,
        'valor_bruto': valor_bruto,
        'rendimento_bruto': rendimento_bruto,
        'irrf': resultado_irrf['irrf'],
        'aliquota_percentual': resultado_irrf['aliquota_percentual'],
        'rendimento_liquido': resultado_irrf['valor_liquido'],
        'valor_final_liquido': valor_inicial + resultado_irrf['valor_liquido']
    }
