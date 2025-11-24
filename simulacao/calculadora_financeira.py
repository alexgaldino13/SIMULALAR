# simulacao/calculadora_financeira.py

from decimal import Decimal
import math # ESSENCIAL: Necessário para o cálculo logarítmico na amortização PRICE

# ----------------------------------------------------------------------
# FUNÇÃO 1: CÁLCULO PRICE/SAC (COM LÓGICA DE AMORTIZAÇÃO FGTS) - CORRIGIDA
# ----------------------------------------------------------------------

def calcular_price_sac(metodo, valor_principal, taxa_anual, prazo_meses, seguro_mensal=0.0, taxa_admin_mensal=0.0, **kwargs):
    """
    Calcula a tabela de amortização (Price ou SAC) e retorna a lista de parcelas.
    Inclui suporte à amortização extra com FGTS.
    """
    
    # CONVERSÃO DOS PARÂMETROS AUXILIARES PARA DECIMAL (Correção do TypeError)
    seguro_mensal_dec = Decimal(str(seguro_mensal))
    taxa_admin_mensal_dec = Decimal(str(taxa_admin_mensal))
    fgts_saldo_amortizacao_dec = Decimal(str(kwargs.get('fgts_saldo', 0.0)))
    
    # NOVOS PARAMETROS FGTS
    usar_fgts = kwargs.get('usar_fgts_financiamento', False)
    tipo_amortizacao = kwargs.get('tipo_amortizacao_fgts', 'reduzir_prazo')
    mes_uso = kwargs.get('mes_uso_fgts_financiamento', 1)
    
    # 1. Inicialização de Variáveis
    taxa_mensal = taxa_anual / 12 / 100 # taxa_anual já é Decimal vindo da função 4
    saldo_devedor = valor_principal # valor_principal já é Decimal vindo da função 4
    tabela = []

    if taxa_mensal == 0 and saldo_devedor > 0:
        return []

    # Variáveis mutáveis do financiamento
    prazo_atual = prazo_meses
    amortizacao_fixa = valor_principal / prazo_meses # SAC inicial
    parcela_fixa = Decimal(0) # Price inicial
    
    # 2. Cálculo do Fator de Pagamento Inicial (Price)
    if metodo == 'price' and taxa_mensal > 0 and prazo_atual > 0:
        try:
            # Fórmula da Parcela Fixa (PMT)
            # Operação com ** é mais precisa com float, mas a biblioteca decimal suporta.
            # Mantemos como Decimal, mas garantimos que parcela_fixa seja Decimal(0) em caso de erro.
            fator = (taxa_mensal * (1 + taxa_mensal) ** prazo_atual) / (((1 + taxa_mensal) ** prazo_atual) - 1)
            parcela_fixa = valor_principal * fator
        except ZeroDivisionError:
            parcela_fixa = Decimal(0)

    # 3. Simulação Mês a Mês
    mes_original = 1
    while saldo_devedor > Decimal('0.001') and mes_original <= prazo_meses + 10: 
        
        # --- LÓGICA DE AMORTIZAÇÃO EXTRA COM FGTS (NO MÊS ESCOLHIDO) ---
        if usar_fgts and mes_original == mes_uso and fgts_saldo_amortizacao_dec > 0:
            
            valor_amortizado_fgts = min(saldo_devedor, fgts_saldo_amortizacao_dec) 
            saldo_anterior = saldo_devedor
            saldo_devedor -= valor_amortizado_fgts # Reduz o saldo devedor
            
            prazo_restante = prazo_atual - mes_original + 1 
            
            if tipo_amortizacao == 'reduzir_prazo':
                
                if metodo == 'price' and taxa_mensal > 0 and parcela_fixa > 0:
                    # CONVERSÃO PARA FLOAT NECESSÁRIA PARA math.log (Correção Crítica)
                    parcela_fixa_float = float(parcela_fixa)
                    taxa_mensal_float = float(taxa_mensal)
                    saldo_devedor_float = float(saldo_devedor)
                    
                    try:
                        novo_n = math.log(parcela_fixa_float / (parcela_fixa_float - taxa_mensal_float * saldo_devedor_float)) / math.log(1 + taxa_mensal_float)
                        prazo_restante = math.ceil(novo_n)
                        prazo_atual = mes_original + prazo_restante - 1 
                    except ValueError:
                        prazo_restante = 0 
                        prazo_atual = mes_original 
                        
                elif metodo == 'sac':
                    if prazo_restante > 0:
                        amortizacao_fixa = saldo_devedor / prazo_restante
            
            elif tipo_amortizacao == 'reduzir_parcela':
                
                if metodo == 'price' and prazo_restante > 0 and taxa_mensal > 0:
                    # Recalcula a Parcela Fixa (mantendo como Decimal)
                    fator_novo = (taxa_mensal * (1 + taxa_mensal) ** prazo_restante) / (((1 + taxa_mensal) ** prazo_restante) - 1)
                    parcela_fixa = saldo_devedor * fator_novo
                
                elif metodo == 'sac' and prazo_restante > 0:
                    amortizacao_fixa = saldo_devedor / prazo_restante
            
            # Adiciona o evento FGTS
            tabela.append({
                'mes': mes_original - Decimal('0.1'),
                'saldo_inicial': float(saldo_anterior), 
                'juros': 0.0,
                'amortizacao': float(valor_amortizado_fgts),
                'parcela': 0.0,
                'saldo_final': float(saldo_devedor),
                'tipo': 'FGTS_LumpSum'
            })
            
            if saldo_devedor <= Decimal('0.001'):
                break
        
        # B) CÁLCULO DO MÊS NORMAL
        if mes_original > prazo_atual:
            break
            
        juros_mensal = saldo_devedor * taxa_mensal
        
        if metodo == 'price':
            amortizacao = parcela_fixa - juros_mensal
            # CORRIGIDO: Agora Decimal + Decimal
            parcela = parcela_fixa + seguro_mensal_dec + taxa_admin_mensal_dec
            
        elif metodo == 'sac':
            amortizacao = amortizacao_fixa
            # CORRIGIDO: Agora Decimal + Decimal
            parcela = amortizacao + juros_mensal + seguro_mensal_dec + taxa_admin_mensal_dec
        
        # Aplica a amortização
        if saldo_devedor > Decimal('0.001') and amortizacao > 0:
            saldo_anterior_mes = saldo_devedor
            saldo_devedor -= amortizacao
            
            # Correção de arredondamento para o último mês
            if saldo_devedor < Decimal('0.01'):
                amortizacao += saldo_devedor
                saldo_devedor = Decimal(0)
            
            tabela.append({
                'mes': mes_original,
                'saldo_inicial': float(saldo_anterior_mes),
                'juros': float(juros_mensal),
                'amortizacao': float(amortizacao),
                'parcela': float(parcela),
                'saldo_final': float(saldo_devedor),
                'tipo': metodo
            })
        
        mes_original += 1
        
    return tabela

# ----------------------------------------------------------------------
# FUNÇÃO 2: CÁLCULO CONSÓRCIO (AGORA INCLUI LANCE FGTS NO RESULTADO) - CORRIGIDA
# ----------------------------------------------------------------------

def simular_consorcio(valor_imovel, prazo_meses, taxa_adm, fundo_reserva, fgts_saldo=0.0):
    """
    Calcula os custos totais e a parcela fixa do Consórcio.
    """
    # valor_imovel já é Decimal vindo da função 4
    valor_imovel_total = valor_imovel
    
    # CONVERSÃO DOS PARÂMETROS PARA DECIMAL (Correção do TypeError)
    prazo_meses_dec = Decimal(str(prazo_meses))
    valor_lance_fgts = Decimal(str(fgts_saldo))
    taxa_adm_anual = Decimal(str(taxa_adm)) / 100
    fundo_reserva_percent = Decimal(str(fundo_reserva)) / 100
    
    # 1. CUSTOS TOTAIS (Taxas sobre a Carta de Crédito)
    # Total de Taxa de Administração (Taxa Anual * Prazo em Anos * Valor)
    taxa_adm_total = taxa_adm_anual * (prazo_meses_dec / 12) * valor_imovel_total
    # Fundo de Reserva Total (% total * Valor)
    fundo_reserva_total = fundo_reserva_percent * valor_imovel_total 

    total_custo = taxa_adm_total + fundo_reserva_total
    
    # 2. CÁLCULO DA PARCELA
    parcela_fixa = (valor_imovel_total + total_custo) / prazo_meses_dec
    
    return {
        'parcela_fixa': float(parcela_fixa),
        'total_custo': float(total_custo),
        'valor_lance_fgts': float(valor_lance_fgts),
        'taxa_administracao_total': float(taxa_adm_total),
        'fundo_reserva_total': float(fundo_reserva_total)
    }


# ----------------------------------------------------------------------
# FUNÇÃO 3: CÁLCULO ALUGUEL + INVESTIMENTO (DINÂMICO) - REVISADA
# ----------------------------------------------------------------------

def simular_aluguel_investimento(
    valor_imovel_total, entrada_total, taxa_investimento, aluguel_inicial, 
    taxa_inflacao, prazo_meses, recursos_proprios_iniciais, opcao_pagamento_aluguel,
    fgts_saldo, rendimento_fgts, fgts_mensal_percent, aporte_13,
    renda_familiar_bruta, 
    valorizacao_imovel,
    taxa_anual_financiamento
):
    """
    Simula o cenário Aluguel + Investimento mês a mês.
    """
    
    # 1. CONVERSÃO INICIAL DE TODOS OS PARÂMETROS PARA DECIMAL OU INT
    
    # Valores numéricos puros (devem ser Decimal para cálculo)
    valor_imovel_total_dec = Decimal(str(valor_imovel_total))
    entrada_total_dec = Decimal(str(entrada_total))
    recursos_proprios_iniciais_dec = Decimal(str(recursos_proprios_iniciais))
    fgts_saldo_dec = Decimal(str(fgts_saldo))
    aluguel_inicial_dec = Decimal(str(aluguel_inicial))
    renda_familiar_bruta_dec = Decimal(str(renda_familiar_bruta))
    aporte_13_dec = Decimal(str(aporte_13))
    
    # Taxas (convertidas para Decimal e Mensal/Anual)
    taxa_investimento_mensal = Decimal(str(taxa_investimento)) / 100 / 12
    rendimento_fgts_mensal = Decimal(str(rendimento_fgts)) / 100 / 12
    fgts_mensal_percent = Decimal(str(fgts_mensal_percent)) / 100
    taxa_inflacao_anual_percent = Decimal(str(taxa_inflacao)) / 100 
    valorizacao_imovel_anual_percent = Decimal(str(valorizacao_imovel)) / 100
    
    # Prazo (deve ser Int)
    prazo_meses_int = int(prazo_meses)
    
    # 2. Inicialização de Variáveis
    aluguel_mensal_atual = aluguel_inicial_dec 
    total_gasto_aluguel = Decimal(0)
    valor_imovel_final = valor_imovel_total_dec 

    # Capital Inicial é a Entrada (Investida) + Recursos Próprios Iniciais
    capital_inicial = entrada_total_dec + recursos_proprios_iniciais_dec
    saldo_investimento_atual = capital_inicial
    fgts_saldo_atual = fgts_saldo_dec
    
    # 3. Loop de Simulação
    for mes in range(1, prazo_meses_int + 1): 
        
        # A) RENDIMENTO MENSAL DOS INVESTIMENTOS E FGTS
        saldo_investimento_atual *= (1 + taxa_investimento_mensal) 
        fgts_saldo_atual *= (1 + rendimento_fgts_mensal)
        
        # B) DEPÓSITO MENSAL NO FGTS
        deposito_fgts_mensal = renda_familiar_bruta_dec * fgts_mensal_percent
        fgts_saldo_atual += deposito_fgts_mensal
        
        # C) PAGAMENTO DO ALUGUEL
        total_gasto_aluguel += aluguel_mensal_atual
        
        # Decisão de onde o aluguel é pago
        if opcao_pagamento_aluguel == 'investimento':
            saldo_investimento_atual -= aluguel_mensal_atual

        # D) TRATAMENTO DO APORTE ANUAL
        if mes % 12 == 0:
            saldo_investimento_atual += aporte_13_dec

        # E) REAJUSTE ANUAL (Aluguel e Valorização do Imóvel)
        if mes % 12 == 0 and mes < prazo_meses_int:
            aluguel_mensal_atual *= (1 + taxa_inflacao_anual_percent) 
            valor_imovel_final *= (1 + valorizacao_imovel_anual_percent)

    # 4. Cálculo Final
    return {
        'acumulado_final': float(saldo_investimento_atual),
        'total_gasto_aluguel': float(total_gasto_aluguel),
        'fgts_final': float(fgts_saldo_atual),
        'valor_imovel_final': float(valor_imovel_final)
    }


# ----------------------------------------------------------------------
# FUNÇÃO 4: PRINCIPAL DE DISTRIBUIÇÃO (ATUALIZADA) - CORRIGIDA
# ----------------------------------------------------------------------

def simular_financiamento_geral(metodo, valor_principal, taxa_anual, prazo_meses, **kwargs):
    """
    Função principal que roteia a simulação para o método correto.
    """
    
    # CONVERSÃO DOS ARGUMENTOS CORE PARA DECIMAL OU INT (CORREÇÃO CRÍTICA)
    try:
        vp_dec = Decimal(str(valor_principal))
        ta_dec = Decimal(str(taxa_anual))
        pm_int = int(prazo_meses)
    except Exception:
        # Retorna lista vazia ou levanta exceção se a conversão falhar.
        return [] 
        
    if metodo in ['price', 'sac']:
        # Roteia para Financiamento com os valores base convertidos
        return calcular_price_sac(metodo, vp_dec, ta_dec, pm_int, **kwargs)
        
    elif metodo == 'consorcio':
        # Roteia para Consórcio (vp_dec e pm_int serão convertidos internamente)
        taxa_adm = kwargs.get('taxa_adm', 0.0)
        fundo_reserva = kwargs.get('fundo_reserva', 0.0)
        fgts_saldo = kwargs.get('fgts_saldo', 0.0) 
        return simular_consorcio(vp_dec, pm_int, taxa_adm, fundo_reserva, fgts_saldo)
        
    elif metodo == 'renda':
        # Roteia para Aluguel + Investimento
        return simular_aluguel_investimento(
            valor_imovel_total=kwargs.get('valor_imovel_total', 0.0), # Será convertido dentro da função
            entrada_total=kwargs.get('entrada_total', 0.0),
            taxa_investimento=kwargs.get('taxa_investimento', 0.0),
            aluguel_inicial=kwargs.get('aluguel_inicial', 0.0),
            taxa_inflacao=kwargs.get('taxa_inflacao', 0.0), 
            prazo_meses=pm_int,
            recursos_proprios_iniciais=kwargs.get('recursos_proprios_iniciais', 0.0),
            opcao_pagamento_aluguel=kwargs.get('opcao_pagamento_aluguel', 'renda'),
            
            fgts_saldo=kwargs.get('fgts_saldo', 0.0),
            rendimento_fgts=kwargs.get('rendimento_fgts', 0.0),
            fgts_mensal_percent=kwargs.get('fgts_mensal_percent', 0.0),
            aporte_13=kwargs.get('aporte_13', 0.0),
            taxa_anual_financiamento=ta_dec,
            renda_familiar_bruta=kwargs.get('renda_familiar_bruta', 0.0), 
            valorizacao_imovel=kwargs.get('valorizacao_imovel', 0.0) 
        )

    return []