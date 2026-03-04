from decimal import Decimal
import math

# Use centralized formatting helpers
from simulacao.formatacao import (
    formatar_moeda_brl,
    formatar_percentual,
    formatar_numero,
    formatar_meses_anos,
)

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
    
    # Variáveis de Soma (para o resumo)
    total_juros = Decimal(0)
    total_seguros_taxas = Decimal(0)
    
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
                        # Recalcula o número de parcelas restantes (n)
                        novo_n = math.log(parcela_fixa_float / (parcela_fixa_float - taxa_mensal_float * saldo_devedor_float)) / math.log(1 + taxa_mensal_float)
                        prazo_restante = math.ceil(novo_n)
                        prazo_atual = mes_original + prazo_restante - 1 
                    except ValueError:
                        prazo_restante = 0 
                        prazo_atual = mes_original 
                        
                elif metodo == 'sac':
                    if prazo_restante > 0:
                        # Recalcula a amortização constante com o novo saldo
                        amortizacao_fixa = saldo_devedor / prazo_restante
            
            elif tipo_amortizacao == 'reduzir_parcela':
                
                if metodo == 'price' and prazo_restante > 0 and taxa_mensal > 0:
                    # Recalcula a Parcela Fixa (mantendo como Decimal)
                    fator_novo = (taxa_mensal * (1 + taxa_mensal) ** prazo_restante) / (((1 + taxa_mensal) ** prazo_restante) - 1)
                    parcela_fixa = saldo_devedor * fator_novo
                
                elif metodo == 'sac' and prazo_restante > 0:
                    # Recalcula a amortização constante com o novo saldo (não muda o prazo)
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
        
        # Acumula juros e taxas
        total_juros += juros_mensal
        total_seguros_taxas += seguro_mensal_dec + taxa_admin_mensal_dec
        
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
        
    return {
        'tabela': tabela,
        'parcela_inicial': float(tabela[0]['parcela']) if tabela else 0.0,
        'total_juros': float(total_juros),
        'total_seguros_taxas': float(total_seguros_taxas),
        'prazo_final_meses': mes_original - 1 # O número do último mês simulado
    }

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
            # Subtrai do investimento (se saldo positivo)
            if saldo_investimento_atual >= aluguel_mensal_atual:
                 saldo_investimento_atual -= aluguel_mensal_atual
            else:
                 # Se o investimento não cobre o aluguel, o saldo vai a zero.
                 # Neste cenário, o aluguel restante teria que vir da renda
                 # ou o investimento é insuficiente. Para simplificar, zeramos.
                 saldo_investimento_atual = Decimal(0)

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
        'valor_imovel_final': float(valor_imovel_final),
        'capital_inicial': float(capital_inicial),
        'aluguel_inicial': float(aluguel_inicial_dec)
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

# ----------------------------------------------------------------------
# FUNÇÃO CENTRAL DE AGREGAÇÃO E FORMATAÇÃO (CHAMADA PELO VIEWS.PY)
# ----------------------------------------------------------------------

def comparar_cenarios_e_formatar(dados_form):
    """
    Função principal que recebe os dados brutos, coordena os cálculos
    e retorna o resumo comparativo FORMATADO para o template.
    """
    
    # 1. PARSE E PREPARAÇÃO DOS DADOS DE ENTRADA (LÓGICA DE NEGÓCIO)
    try:
        # Variáveis Core
        valor_imovel_num = float(dados_form.get('valor_imovel'))
        entrada_num = float(dados_form.get('entrada'))
        valor_despesas_num = float(dados_form.get('valor_despesas'))
        prazo_anos_num = int(dados_form.get('prazo_anos'))
        prazo_meses_num = prazo_anos_num * 12
        
        # Variáveis de Configuração
        taxa_anual_num = float(dados_form.get('taxa_anual'))
        seguro_mensal_num = float(dados_form.get('seguro_mensal'))
        taxa_admin_mensal_num = float(dados_form.get('taxa_admin_mensal'))
        fgts_saldo_num = float(dados_form.get('fgts_saldo'))
        incorporar_despesas = dados_form.get('incorporar_despesas') == 'on'
        
        # 2. CÁLCULO DO PRINCIPAL FINANCIADO (CARTA DE CRÉDITO)
        principal_base = valor_imovel_num - entrada_num
        principal_financiado = principal_base
        
        if incorporar_despesas:
            principal_financiado += valor_despesas_num
        else:
            # Se não incorporar, a despesa deve ser adicionada ao "desembolso" total
            pass 
        
        # Dicionário de Kwargs para as funções de cálculo
        kwargs_comuns = {
            'seguro_mensal': seguro_mensal_num,
            'taxa_admin_mensal': taxa_admin_mensal_num,
            'fgts_saldo': fgts_saldo_num,
            'usar_fgts_financiamento': dados_form.get('usar_fgts_financiamento') == 'on',
            'tipo_amortizacao_fgts': dados_form.get('tipo_amortizacao_fgts'),
            'mes_uso_fgts_financiamento': int(dados_form.get('mes_uso_fgts_financiamento')),
            
            # Variáveis para Consórcio e Aluguel
            'taxa_adm': float(dados_form.get('taxa_adm')),
            'fundo_reserva': float(dados_form.get('fundo_reserva')),
            'valor_imovel_total': valor_imovel_num,
            'entrada_total': entrada_num,
            'taxa_investimento': float(dados_form.get('taxa_investimento')),
            'aluguel_inicial': float(dados_form.get('aluguel_inicial')),
            'taxa_inflacao': float(dados_form.get('taxa_inflacao')),
            'recursos_proprios_iniciais': float(dados_form.get('recursos_proprios_iniciais')),
            'opcao_pagamento_aluguel': dados_form.get('opcao_pagamento_aluguel'),
            'rendimento_fgts': float(dados_form.get('rendimento_fgts')),
            'fgts_mensal_percent': float(dados_form.get('fgts_mensal_percent')),
            'aporte_13': float(dados_form.get('aporte_13')),
            'renda_familiar_bruta': float(dados_form.get('renda_familiar_bruta')), 
            'valorizacao_imovel': float(dados_form.get('valorizacao_imovel'))
        }

    except Exception as e:
        # Se algum campo numérico obrigatório falhar, retorna erro
        print(f"Erro de conversão de dados: {e}")
        return None 
    
    resumo = []
    
    # 3. CENÁRIO 1: FINANCIAMENTO (PRICE E SAC)
    
    for metodo in ['price', 'sac']:
        # Simulação com as opções do formulário
        resultado = simular_financiamento_geral(
            metodo=metodo,
            valor_principal=principal_financiado,
            taxa_anual=taxa_anual_num,
            prazo_meses=prazo_meses_num,
            **kwargs_comuns
        )

        # Simulação baseline: sem uso de FGTS / sem amortizações extras
        baseline_kwargs = kwargs_comuns.copy()
        baseline_kwargs['usar_fgts_financiamento'] = False
        baseline_kwargs['fgts_saldo'] = 0.0
        baseline = simular_financiamento_geral(
            metodo=metodo,
            valor_principal=principal_financiado,
            taxa_anual=taxa_anual_num,
            prazo_meses=prazo_meses_num,
            **baseline_kwargs
        )

        # Se a simulação falhar ou retornar lista vazia
        if not resultado or not resultado['tabela']:
             continue

        total_juros_e_taxas = resultado['total_juros'] + resultado['total_seguros_taxas']
        total_desembolsado = principal_base + valor_despesas_num + total_juros_e_taxas

        # Baseline totals (sem amortização/FGTS)
        baseline_juros_taxas = baseline['total_juros'] + baseline['total_seguros_taxas']
        baseline_desembolsado = principal_base + valor_despesas_num + baseline_juros_taxas

        # Economia obtida ao aplicar FGTS/amortizações (positivo se economizou)
        economia_valor = baseline_desembolsado - total_desembolsado
        prazo_reducao = max(0, baseline.get('prazo_final_meses', prazo_meses_num) - resultado.get('prazo_final_meses', prazo_meses_num))
        
        # Mapeamento do nome
        nome_metodo = 'Tabela Price' if metodo == 'price' else 'Tabela SAC'

        resumo.append({
            'metodo': nome_metodo,
            'parcela_inicial': formatar_moeda_brl(resultado['parcela_inicial']),
            'custo_total': formatar_moeda_brl(total_juros_e_taxas),
            'total_pago': formatar_moeda_brl(total_desembolsado),
            'economia': formatar_moeda_brl(economia_valor),
            'prazo_reducao_meses': prazo_reducao,
            'extra': f'Prazo Final: {resultado["prazo_final_meses"] // 12} anos e {resultado["prazo_final_meses"] % 12} meses.'
        })

    # 4. CENÁRIO 2: CONSÓRCIO
    
    resultado_cons = simular_financiamento_geral(
        metodo='consorcio',
        valor_principal=valor_imovel_num, # O principal do consórcio é o valor do bem (carta de crédito)
        taxa_anual=0, # A taxa de juros não se aplica aqui
        prazo_meses=prazo_meses_num,
        **kwargs_comuns
    )
    
    # Total pago = Valor do Imóvel + Custos (taxa adm + reserva) + Despesas de transação
    total_pago_cons = valor_imovel_num + resultado_cons['total_custo'] + valor_despesas_num

    resumo.append({
        'metodo': 'Consórcio',
        'parcela_inicial': formatar_moeda_brl(resultado_cons['parcela_fixa']),
        'custo_total': formatar_moeda_brl(resultado_cons['total_custo']), # Total de Taxas
        'total_pago': formatar_moeda_brl(total_pago_cons),
        'extra': f'Lance FGTS: {formatar_moeda_brl(resultado_cons["valor_lance_fgts"])} usado.'
    })


    # 5. CENÁRIO 3: ALUGUEL + INVESTIMENTO
    
    resultado_aluguel = simular_financiamento_geral(
        metodo='renda',
        valor_principal=0, # Não se aplica
        taxa_anual=0, # Não se aplica
        prazo_meses=prazo_meses_num,
        **kwargs_comuns
    )
    
    # Saldo final acumulado (Investimento + FGTS Final)
    saldo_total_acumulado = resultado_aluguel['acumulado_final'] + resultado_aluguel['fgts_final']
    
    # Detalhes para o campo 'Resultado/Vantagem Extra'
    detalhes = [
        f'Saldo Investimento Final: {formatar_moeda_brl(resultado_aluguel["acumulado_final"])}',
        f'Saldo FGTS Final: {formatar_moeda_brl(resultado_aluguel["fgts_final"])}',
        f'Valor Final do Imóvel (Estimado): {formatar_moeda_brl(resultado_aluguel["valor_imovel_final"])}',
        f'Ganho Líquido Total: <strong style="color: green;">{formatar_moeda_brl(saldo_total_acumulado - resultado_aluguel["capital_inicial"])}</strong>',
    ]

    resumo.append({
        'metodo': 'Aluguel + Investimento',
        'parcela_inicial': formatar_moeda_brl(resultado_aluguel['aluguel_inicial']),
        'custo_total': formatar_moeda_brl(saldo_total_acumulado), # Acumulado Total (GANHO)
        'total_pago': formatar_moeda_brl(resultado_aluguel['total_gasto_aluguel']), # Gasto Total com Aluguel Bruto
        'extra': {'detalhes': detalhes}
    })
    
    return resumo




def calcular_investidor_imobiliario(dados_form):
    """
    Cenário 6: Investidor Imobiliário
    Calcula a viabilidade de comprar um imóvel para investimento com aluguel.
    """
    from decimal import Decimal, ROUND_HALF_UP
    
    # 1. DADOS DO IMÓVEL
    valor_imovel = float(dados_form.get('valor_imovel', 0))
    valor_entrada = float(dados_form.get('valor_entrada', 0))
    
    # 2. DADOS DO FINANCIAMENTO
    prazo_meses = int(dados_form.get('prazo_meses', 360))
    taxa_juros_anual = float(dados_form.get('taxa_juros_anual', 10.0))
    sistema_amortizacao = dados_form.get('sistema_amortizacao', 'SAC')
    
    # 3. DADOS DO ALUGUEL
    valor_aluguel_mensal = float(dados_form.get('valor_aluguel_mensal', 0))
    usar_estimativa_aluguel = dados_form.get('usar_estimativa_aluguel', False)
    
    # Se não forneceu aluguel e quer estimativa, usar 0.5% do valor do imóvel
    if usar_estimativa_aluguel or valor_aluguel_mensal == 0:
        valor_aluguel_mensal = valor_imovel * 0.005
    
    # 4. ESTRATÉGIA DE USO DO ALUGUEL
    usar_aluguel_para_prestacao = dados_form.get('usar_aluguel_para_prestacao', True)
    
    # 5. CUSTOS ADICIONAIS
    taxa_administracao_pct = float(dados_form.get('taxa_administracao_pct', 8.0))
    iptu_anual = float(dados_form.get('iptu_anual', 0))
    condominio_mensal = float(dados_form.get('condominio_mensal', 0))
    
    # 6. INVESTIMENTO ALTERNATIVO
    taxa_investimento_anual = float(dados_form.get('taxa_investimento_anual', 12.0))
    
    # CÁLCULOS
    valor_financiado = valor_imovel - valor_entrada
    taxa_juros_mensal = taxa_juros_anual / 12 / 100
    taxa_investimento_mensal = taxa_investimento_anual / 12 / 100
    
    # Calcular financiamento (SAC ou PRICE)
    if sistema_amortizacao == 'SAC':
        amortizacao_mensal = valor_financiado / prazo_meses
        tabela_financiamento = []
        saldo_devedor = valor_financiado
        
        for mes in range(1, prazo_meses + 1):
            juros = saldo_devedor * taxa_juros_mensal
            prestacao = amortizacao_mensal + juros
            saldo_devedor -= amortizacao_mensal
            
            tabela_financiamento.append({
                'mes': mes,
                'prestacao': round(prestacao, 2),
                'juros': round(juros, 2),
                'amortizacao': round(amortizacao_mensal, 2),
                'saldo_devedor': round(max(0, saldo_devedor), 2)
            })
    else:
        if taxa_juros_mensal > 0:
            prestacao_fixa = valor_financiado * (taxa_juros_mensal * (1 + taxa_juros_mensal)**prazo_meses) / ((1 + taxa_juros_mensal)**prazo_meses - 1)
        else:
            prestacao_fixa = valor_financiado / prazo_meses
            
        tabela_financiamento = []
        saldo_devedor = valor_financiado
        
        for mes in range(1, prazo_meses + 1):
            juros = saldo_devedor * taxa_juros_mensal
            amortizacao = prestacao_fixa - juros
            saldo_devedor -= amortizacao
            
            tabela_financiamento.append({
                'mes': mes,
                'prestacao': round(prestacao_fixa, 2),
                'juros': round(juros, 2),
                'amortizacao': round(amortizacao, 2),
                'saldo_devedor': round(max(0, saldo_devedor), 2)
            })
    
    # Calcular custos mensais do imóvel
    taxa_administracao = valor_aluguel_mensal * (taxa_administracao_pct / 100)
    iptu_mensal = iptu_anual / 12
    custo_mensal_imovel = taxa_administracao + iptu_mensal + condominio_mensal
    aluguel_liquido = valor_aluguel_mensal - custo_mensal_imovel
    
    # CENÁRIO A: Sem aluguel
    total_pago_a = sum([p['prestacao'] for p in tabela_financiamento])
    custo_total_a = valor_entrada + total_pago_a + (custo_mensal_imovel * prazo_meses)
    
    # CENÁRIO B: Aluguel usado para pagar prestação
    fluxo_caixa_b = []
    saldo_investido_b = 0
    
    for mes_data in tabela_financiamento:
        prestacao = mes_data['prestacao']
        diferenca = aluguel_liquido - prestacao
        
        if diferenca >= 0:
            saldo_investido_b = saldo_investido_b * (1 + taxa_investimento_mensal) + diferenca
            desembolso_mensal = 0
        else:
            desembolso_mensal = abs(diferenca)
            saldo_investido_b = saldo_investido_b * (1 + taxa_investimento_mensal)
        
        fluxo_caixa_b.append({
            'mes': mes_data['mes'],
            'aluguel_liquido': round(aluguel_liquido, 2),
            'prestacao': round(prestacao, 2),
            'diferenca': round(diferenca, 2),
            'desembolso': round(desembolso_mensal, 2),
            'saldo_investido': round(saldo_investido_b, 2)
        })
    
    total_desembolsado_b = valor_entrada + sum([f['desembolso'] for f in fluxo_caixa_b])
    patrimonio_final_b = valor_imovel + saldo_investido_b
    
    # CENÁRIO C: Aluguel totalmente investido
    saldo_investido_c = 0
    for mes in range(1, prazo_meses + 1):
        saldo_investido_c = saldo_investido_c * (1 + taxa_investimento_mensal) + aluguel_liquido
    
    total_desembolsado_c = valor_entrada + total_pago_a
    patrimonio_final_c = valor_imovel + saldo_investido_c
    
    # INDICADORES
    yield_bruto = (valor_aluguel_mensal * 12 / valor_imovel) * 100
    yield_liquido = (aluguel_liquido * 12 / valor_imovel) * 100
    roi_b = ((patrimonio_final_b - total_desembolsado_b) / total_desembolsado_b) * 100 if total_desembolsado_b > 0 else 0
    roi_c = ((patrimonio_final_c - total_desembolsado_c) / total_desembolsado_c) * 100 if total_desembolsado_c > 0 else 0
    
    payback_meses_b = 0
    acumulado = 0
    for f in fluxo_caixa_b:
        acumulado += f['diferenca']
        if acumulado >= valor_entrada:
            payback_meses_b = f['mes']
            break
    
    resultado = {
        'dados_entrada': {
            'valor_imovel': valor_imovel,
            'valor_entrada': valor_entrada,
            'valor_financiado': valor_financiado,
            'prazo_meses': prazo_meses,
            'taxa_juros_anual': taxa_juros_anual,
            'sistema_amortizacao': sistema_amortizacao,
            'valor_aluguel_mensal': valor_aluguel_mensal,
            'aluguel_estimado': usar_estimativa_aluguel,
        },
        'custos_mensais': {
            'taxa_administracao': round(taxa_administracao, 2),
            'iptu_mensal': round(iptu_mensal, 2),
            'condominio': round(condominio_mensal, 2),
            'total_custos': round(custo_mensal_imovel, 2),
            'aluguel_liquido': round(aluguel_liquido, 2),
        },
        'financiamento': {
            'primeira_prestacao': tabela_financiamento[0]['prestacao'],
            'ultima_prestacao': tabela_financiamento[-1]['prestacao'],
            'total_juros': round(sum([p['juros'] for p in tabela_financiamento]), 2),
            'total_pago': round(total_pago_a, 2),
        },
        'cenario_a_sem_aluguel': {
            'descricao': 'Imóvel vazio (sem aluguel)',
            'custo_total': round(custo_total_a, 2),
            'patrimonio_final': round(valor_imovel, 2),
        },
        'cenario_b_aluguel_prestacao': {
            'descricao': 'Aluguel usado para pagar prestação',
            'total_desembolsado': round(total_desembolsado_b, 2),
            'saldo_investido_final': round(saldo_investido_b, 2),
            'patrimonio_final': round(patrimonio_final_b, 2),
            'lucro': round(patrimonio_final_b - total_desembolsado_b, 2),
            'roi_percentual': round(roi_b, 2),
        },
        'cenario_c_aluguel_investido': {
            'descricao': 'Aluguel totalmente investido',
            'total_desembolsado': round(total_desembolsado_c, 2),
            'saldo_investido_final': round(saldo_investido_c, 2),
            'patrimonio_final': round(patrimonio_final_c, 2),
            'lucro': round(patrimonio_final_c - total_desembolsado_c, 2),
            'roi_percentual': round(roi_c, 2),
        },
        'indicadores': {
            'yield_bruto': round(yield_bruto, 2),
            'yield_liquido': round(yield_liquido, 2),
            'payback_meses': payback_meses_b if payback_meses_b > 0 else 'Não recupera',
            'payback_anos': round(payback_meses_b / 12, 1) if payback_meses_b > 0 else 'N/A',
        },
        'melhor_cenario': 'B' if patrimonio_final_b > patrimonio_final_c else 'C',
        'tabela_financiamento': tabela_financiamento[:12],
        'fluxo_caixa_b': fluxo_caixa_b[:12],
    }
    
    return resultado


# FUNÇÃO MCMV (Minha Casa Minha Vida)
def calcular_mcmv(valor_imovel, renda_familiar_mensal, valor_entrada, prazo_meses, usa_fgts=False, valor_fgts_disponivel=0):
    """
    Calcula simulação do programa MCMV.
    Retorna dicionário com resultado da simulação.
    """
    from decimal import Decimal
    
    # Determinar faixa MCMV baseado na renda
    renda_anual = renda_familiar_mensal * 12
    
    subsidio = Decimal('0')
    if renda_familiar_mensal <= 2640:
        faixa = 'faixa1'
        taxa_juros = Decimal('0.04')  # 4% ao ano
        subsidio_percent = Decimal('0.90')  # até 90% de subsídio
    elif renda_familiar_mensal <= 4400:
        faixa = 'faixa2'
        taxa_juros = Decimal('0.045')  # 4.5% ao ano
        subsidio_percent = Decimal('0.50')
    elif renda_familiar_mensal <= 8000:
        faixa = 'faixa3'
        taxa_juros = Decimal('0.075')  # 7.5% ao ano
        subsidio_percent = Decimal('0.0')
    else:
        return {
            'qualificado': False,
            'erro': 'Renda familiar acima do limite do MCMV (R$ 8.000)'
        }
    
    # Calcular subsídio
        subsidio = Decimal(str(valor_imovel)) * subsidio_percent
        if subsidio > Decimal('55000'):
            subsidio = Decimal('55000')    
    # Valor financiado
    valor_financiado = Decimal(str(valor_imovel)) - Decimal(str(valor_entrada)) - subsidio
    if usa_fgts:
        valor_financiado -= valor_fgts_disponivel
    
    if valor_financiado <= 0:
        valor_financiado = 0
        parcela_media = 0
        custo_total = valor_entrada
    else:
        # Calcular parcela (SAC simplificado)
        taxa_mensal = float(taxa_juros) / 12
        parcela_media = valor_financiado * (taxa_mensal * (1 + taxa_mensal)**prazo_meses) / ((1 + taxa_mensal)**prazo_meses - 1)
        custo_total = parcela_media * prazo_meses + valor_entrada
    
    return {
        'qualificado': True,
        'faixa': faixa,
        'metodo': f'MCMV - Faixa {faixa[-1]}',
        'taxa_juros_anual': float(taxa_juros) * 100,
        'subsidio': round(subsidio, 2),
        'valor_financiado': round(valor_financiado, 2),
        'parcela_inicial': round(parcela_media * 1.1, 2),
        'parcela_media': round(parcela_media, 2),
        'parcela_final': round(parcela_media * 0.9, 2),
        'custo_total': round(custo_total, 2),
        'patrimonio_final': valor_imovel
    }

    