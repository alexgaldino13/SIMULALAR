# simulacao/formatacao.py
"""
Funções de formatação PT-BR para números, moeda e percentuais
"""

from decimal import Decimal


def formatar_moeda_brl(valor):
    """
    Formata float/Decimal para string de moeda brasileira (R$ 1.234.567,89).
    """
    if not isinstance(valor, (int, float, Decimal)):
        return 'R$ 0,00'
    
    valor_float = float(valor)
    
    # Formata com separador de milhar (vírgula) e decimal (ponto) - padrão EUA
    valor_str_eua = f"{valor_float:,.2f}"
    
    # Lógica de swap: ponto para vírgula (decimal) e vírgula para ponto (milhar)
    final_str = valor_str_eua.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
    
    return f"R$ {final_str}"


def formatar_percentual(valor, casas_decimais=2):
    """
    Formata float/Decimal para percentual brasileiro (12,34%).
    
    Args:
        valor: Valor numérico (ex: 7.9 para 7,90%)
        casas_decimais: Número de casas decimais (padrão: 2)
    """
    if not isinstance(valor, (int, float, Decimal)):
        return '0,00%'
    
    valor_float = float(valor)
    
    # Formata com ponto como separador decimal (padrão Python)
    valor_str_eua = f"{valor_float:,.{casas_decimais}f}"
    
    # Lógica de swap: ponto para vírgula (decimal) e vírgula para ponto (milhar)
    final_str = valor_str_eua.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
    
    return f"{final_str}%"


def formatar_numero(valor, casas_decimais=0):
    """
    Formata número com separador de milhar brasileiro (1.234.567).
    
    Args:
        valor: Valor numérico
        casas_decimais: Número de casas decimais (padrão: 0)
    """
    if not isinstance(valor, (int, float, Decimal)):
        return '0'
    
    valor_float = float(valor)
    
    if casas_decimais == 0:
        valor_str_eua = f"{valor_float:,.0f}"
    else:
        valor_str_eua = f"{valor_float:,.{casas_decimais}f}"
    
    # Lógica de swap
    final_str = valor_str_eua.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
    
    return final_str


def formatar_meses_anos(meses):
    """
    Formata meses em anos e meses legíveis (ex: "15 anos e 3 meses").
    """
    if not isinstance(meses, (int, float)):
        return "0 meses"
    
    meses_int = int(meses)
    anos = meses_int // 12
    meses_restantes = meses_int % 12
    
    if anos == 0:
        return f"{meses_restantes} {'mês' if meses_restantes == 1 else 'meses'}"
    elif meses_restantes == 0:
        return f"{anos} {'ano' if anos == 1 else 'anos'}"
    else:
        return f"{anos} {'ano' if anos == 1 else 'anos'} e {meses_restantes} {'mês' if meses_restantes == 1 else 'meses'}"
