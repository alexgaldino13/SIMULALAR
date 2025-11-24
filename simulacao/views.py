from django.shortcuts import render
from decimal import Decimal
from .calculadora_financeira import simular_financiamento_geral
from .models import Usuario, Simulacao, CenarioComparativo, ResultadoComparacao


def simular_financiamento(request):
    
    # --- FUNÇÕES AUXILIARES ---
    # Função para formatar o resumo dos resultados (deve estar no escopo da view)
    def preparar_resumo(metodo, parcela_inicial, custo_total, total_pago, extra_data=None):
        return {
            'metodo': metodo,
            'parcela_inicial': Decimal(str(parcela_inicial)),
            'custo_total': Decimal(str(custo_total)),
            'total_pago': Decimal(str(total_pago)),
            'extra': extra_data if extra_data else {}
        }

    # Função para lidar com campos de formulário vazios (converte para Decimal ou int)
    def to_decimal(value, default=0):
        return Decimal(value) if value and value.strip() else Decimal(default)
    def to_int(value, default=0):
        return int(value) if value and value.strip() else int(default)
    
    # --- DADOS PADRÃO (GET) ---
    # Usado para carregar a página pela primeira vez.
    dados_iniciais_padrao = {
        'nome_usuario': 'Alex',
        'email_usuario': 'jo@globo.com',
        'valor_imovel': Decimal('500000'),
        'entrada': Decimal('60000'),
        'prazo_anos': 30,
        'taxa_anual': Decimal('8.5'),
        'seguro_mensal': Decimal('50.00'),
        'taxa_admin_mensal': Decimal('25.00'),
        'taxa_adm': Decimal('1.0'),
        'fundo_reserva': Decimal('0.5'),
        'aluguel_inicial': Decimal('1500'),
        'taxa_inflacao': Decimal('4.0'),
        'taxa_investimento': Decimal('8.0'),
        'renda_familiar_bruta': Decimal('8000.00'),
        'fgts_mensal_percent': Decimal('8.0'),
        'fgts_saldo': Decimal('10000.00'),
        'valorizacao_imovel': Decimal('6.0'),
        'rendimento_fgts': Decimal('6.5'),
        'aporte_13': Decimal('0'),
        'recursos_proprios_iniciais': Decimal('0'), # <--- NOVO CAMPO
        'opcao_pagamento_aluguel': 'renda',
        'usar_fgts_financiamento': '',
        'tipo_amortizacao_fgts': 'reduzir_prazo',
        'mes_uso_fgts_financiamento': 1,
    }
    
    resultados_finais = [] # Inicializa
    
    
    if request.method == 'POST':
        try:
            # ---------------------------
            # 1. COLETA E CONVERSÃO (USANDO to_decimal/to_int)
            # ---------------------------
            nome_usuario = request.POST.get('nome_usuario', '')
            email_usuario = request.POST.get('email_usuario', '')
            
            # DADOS DO IMÓVEL
            valor_imovel = to_decimal(request.POST.get('valor_imovel'))
            entrada = to_decimal(request.POST.get('entrada'))
            prazo_anos = to_int(request.POST.get('prazo_anos'))

            # DADOS BASE DE CÁLCULO
            prazo_meses = prazo_anos * 12
            valor_financiado = valor_imovel - entrada
            taxa_anual_financiamento = to_decimal(request.POST.get('taxa_anual'))
            seguro_mensal = to_decimal(request.POST.get('seguro_mensal'))
            taxa_admin_mensal = to_decimal(request.POST.get('taxa_admin_mensal'))
            taxa_adm_consorcio = to_decimal(request.POST.get('taxa_adm'))
            fundo_reserva_consorcio = to_decimal(request.POST.get('fundo_reserva'))

            # Dados Aluguel + Investimento
            aluguel_inicial = to_decimal(request.POST.get('aluguel_inicial'))
            opcao_pagamento_aluguel = request.POST.get('opcao_pagamento_aluguel', 'renda') 
            recursos_proprios_iniciais = to_decimal(request.POST.get('recursos_proprios_iniciais'))
            renda_familiar_bruta = to_decimal(request.POST.get('renda_familiar_bruta'))
            fgts_mensal_percent = to_decimal(request.POST.get('fgts_mensal_percent'))
            fgts_saldo = to_decimal(request.POST.get('fgts_saldo'))
            
            # VARIÁVEIS DE CENÁRIO
            taxa_inflacao = to_decimal(request.POST.get('taxa_inflacao'))
            taxa_investimento = to_decimal(request.POST.get('taxa_investimento'))
            valorizacao_imovel = to_decimal(request.POST.get('valorizacao_imovel'))
            rendimento_fgts = to_decimal(request.POST.get('rendimento_fgts'))
            aporte_13 = to_decimal(request.POST.get('aporte_13'))

            # USO DO FGTS NO FINANCIAMENTO
            usar_fgts_financiamento = request.POST.get('usar_fgts_financiamento') == 'on'
            tipo_amortizacao_fgts = request.POST.get('tipo_amortizacao_fgts', 'reduzir_prazo')
            mes_uso_fgts_financiamento = to_int(request.POST.get('mes_uso_fgts_financiamento'), 1)


            # ---------------------------
            # 2. FINANCIAMENTO (PRICE e SAC)
            # ---------------------------
            if valor_financiado > 0 and taxa_anual_financiamento > 0 and prazo_meses > 0:
                taxa_float = float(taxa_anual_financiamento)
                valor_float = float(valor_financiado)
                custos_adicionais_totais = (seguro_mensal + taxa_admin_mensal) * prazo_meses

                # --- PRICE ---
                res_price = simular_financiamento_geral(
                    'price', valor_float, taxa_float, prazo_meses, 
                    seguro_mensal=float(seguro_mensal), taxa_admin_mensal=float(taxa_admin_mensal),
                    usar_fgts_financiamento=usar_fgts_financiamento, tipo_amortizacao_fgts=tipo_amortizacao_fgts,
                    fgts_saldo=float(fgts_saldo), mes_uso_fgts_financiamento=mes_uso_fgts_financiamento
                )
                if res_price:
                    juros_bancarios = Decimal(str(sum(item['juros'] for item in res_price)))
                    custo_total_final = juros_bancarios + custos_adicionais_totais
                    total_pago_price = valor_financiado + entrada + custo_total_final
                    resultados_finais.append(preparar_resumo('Tabela Price', res_price[0]['parcela'], custo_total_final, total_pago_price))

                # --- SAC ---
                res_sac = simular_financiamento_geral(
                    'sac', valor_float, taxa_float, prazo_meses, 
                    seguro_mensal=float(seguro_mensal), taxa_admin_mensal=float(taxa_admin_mensal),
                    usar_fgts_financiamento=usar_fgts_financiamento, tipo_amortizacao_fgts=tipo_amortizacao_fgts,
                    fgts_saldo=float(fgts_saldo), mes_uso_fgts_financiamento=mes_uso_fgts_financiamento
                )
                if res_sac:
                    juros_bancarios = Decimal(str(sum(item['juros'] for item in res_sac)))
                    custo_total_final = juros_bancarios + custos_adicionais_totais
                    total_pago_sac = valor_financiado + entrada + custo_total_final
                    resultados_finais.append(preparar_resumo('Tabela SAC', res_sac[0]['parcela'], custo_total_final, total_pago_sac))


            # ---------------------------
            # 3. CONSÓRCIO (COM LÓGICA DE FGTS)
            # ---------------------------
            if taxa_adm_consorcio > 0 and valor_imovel > 0 and prazo_meses > 0:
                # ADICIONANDO fgts_saldo para uso como lance
                res_cons = simular_financiamento_geral(
                    'consorcio', float(valor_imovel), 0, prazo_meses,
                    taxa_adm=float(taxa_adm_consorcio), fundo_reserva=float(fundo_reserva_consorcio),
                    fgts_saldo=float(fgts_saldo)
                )
                if res_cons and 'parcela_fixa' in res_cons:
                    valor_lance_fgts = Decimal(str(res_cons.get('valor_lance_fgts', 0))) 
                    custo_total_cons = Decimal(str(res_cons['total_custo']))
                    
                    # Custo total para o usuário (Valor do Imóvel - Lance FGTS) + Taxas
                    total_pago_cons = valor_imovel - valor_lance_fgts + custo_total_cons
                    
                    extra_cons = {}
                    if valor_lance_fgts > 0:
                        extra_cons['lance_fgts'] = f"Lance de FGTS utilizado: R$ {valor_lance_fgts:,.2f}"
                        
                    resultados_finais.append(
                        preparar_resumo('Consórcio', res_cons['parcela_fixa'], custo_total_cons, total_pago_cons, extra_data=extra_cons)
                    )


            # ---------------------------
            # 4. ALUGUEL + INVESTIMENTO (COM RECURSOS PRÓPRIOS E FGTS DINÂMICO)
            # ---------------------------
            if aluguel_inicial > 0 and taxa_investimento > 0 and valor_imovel > 0 and prazo_meses > 0:
                # Chamada com todos os parâmetros dinâmicos
                res_renda = simular_financiamento_geral(
                    'renda', 0, 0, prazo_meses,
                    valor_imovel_total=float(valor_imovel), entrada_total=float(entrada),
                    taxa_investimento=float(taxa_investimento), aluguel_inicial=float(aluguel_inicial),
                    taxa_inflacao=float(taxa_inflacao), recursos_proprios_iniciais=float(recursos_proprios_iniciais),
                    opcao_pagamento_aluguel=opcao_pagamento_aluguel, fgts_saldo=float(fgts_saldo),
                    rendimento_fgts=float(rendimento_fgts), fgts_mensal_percent=float(fgts_mensal_percent),
                    aporte_13=float(aporte_13), valorizacao_imovel=float(valorizacao_imovel)
                )

                if res_renda and 'acumulado_final' in res_renda:
                    total_aluguel_gasto = Decimal(str(res_renda['total_gasto_aluguel']))
                    acumulado_final = Decimal(str(res_renda['acumulado_final']))
                    fgts_final = Decimal(str(res_renda['fgts_final']))
                    valor_imovel_final = Decimal(str(res_renda['valor_imovel_final']))

                    # Métrica de comparação principal (Saldo Total Acumulado)
                    saldo_liquido_total = acumulado_final + fgts_final 
                    
                    # Detalhamento para o usuário leigo (para ser exibido na tabela)
                    resultado_renda_detalhado = {
                        'detalhes': [
                            f"Acúmulo Investimento Final: R$ {acumulado_final:,.2f}",
                            f"Saldo FGTS Final: R$ {fgts_final:,.2f}",
                            f"Valorização Estimada do Imóvel: R$ {valor_imovel_final:,.2f}",
                            f"Total Gasto com Aluguel (Bruto): R$ {total_aluguel_gasto:,.2f}"
                        ],
                        'acumulado_total': f"R$ {saldo_liquido_total:,.2f}" # Usado como Custo Total
                    }
                    
                    # Para o Aluguel, a métrica de custo deve ser o Saldo Acumulado Total (Acumulado Final + FGTS Final)
                    resultados_finais.append(
                        preparar_resumo('Aluguel + Investimento', aluguel_inicial, saldo_liquido_total, total_aluguel_gasto, extra_data=resultado_renda_detalhado)
                    )


            # ---------------------------
            # 5. ATUALIZAÇÃO DO CONTEXTO E PERSISTÊNCIA (POST)
            # ---------------------------
            # Dicionário de persistência (dados do POST)
            dados_iniciais = {
                'nome_usuario': nome_usuario,
                'email_usuario': email_usuario,
                'valor_imovel': valor_imovel, 'entrada': entrada, 'prazo_anos': prazo_anos,
                'taxa_anual': taxa_anual_financiamento, 'seguro_mensal': seguro_mensal, 'taxa_admin_mensal': taxa_admin_mensal,
                'taxa_adm': taxa_adm_consorcio, 'fundo_reserva': fundo_reserva_consorcio, 'aluguel_inicial': aluguel_inicial,
                'taxa_inflacao': taxa_inflacao, 'taxa_investimento': taxa_investimento, 'renda_familiar_bruta': renda_familiar_bruta,
                'fgts_mensal_percent': fgts_mensal_percent, 'fgts_saldo': fgts_saldo, 'valorizacao_imovel': valorizacao_imovel,
                'rendimento_fgts': rendimento_fgts, 'aporte_13': aporte_13, 'recursos_proprios_iniciais': recursos_proprios_iniciais,
                'opcao_pagamento_aluguel': opcao_pagamento_aluguel,
                'usar_fgts_financiamento': 'on' if usar_fgts_financiamento else '',
                'tipo_amortizacao_fgts': tipo_amortizacao_fgts,
                'mes_uso_fgts_financiamento': mes_uso_fgts_financiamento,
            }
            
            contexto = {
                'titulo': 'ImobCalc - Simulador Financeiro Completo',
                'dados_iniciais': dados_iniciais, # Usa os dados do POST para persistência
                'resumo_comparativo': resultados_finais
            }
            
            # ESTE É O RETURN CORRETO PARA O POST.
            return render(request, 'simulacao/tabela_price.html', contexto)

        except Exception as e:
            # Em caso de erro, re-exibimos o formulário com uma mensagem de erro.
            print(f"Erro no processamento: {e}")
            contexto = {
                'titulo': 'ImobCalc - Simulador Financeiro Completo',
                'dados_iniciais': dados_iniciais_padrao, # Usa dados padrão ou os dados do POST que causaram o erro
                'resumo_comparativo': [],
                'erro': f"Ocorreu um erro no cálculo. Verifique se todos os campos estão preenchidos corretamente com números válidos. Erro técnico: {e}"
            }
            return render(request, 'simulacao/tabela_price.html', contexto)

    # ----------------------------------------------------------------------
    # FLUXO GET (Primeira carga da página)
    # ----------------------------------------------------------------------
    else:
        # Define o contexto inicial com os valores padrão
        contexto = {
            'titulo': 'ImobCalc - Simulador Financeiro Completo',
            'dados_iniciais': dados_iniciais_padrao, # Usa os dados padrão
            'resumo_comparativo': []
        }
        
        # Este é o return para o GET.
        return render(request, 'simulacao/tabela_price.html', contexto)