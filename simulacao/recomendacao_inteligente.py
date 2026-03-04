"""
Motor de Recomendação Inteligente
Analisa perfil do usuário e prioridades para recomendar melhor opção
"""

from decimal import Decimal


def analisar_perfil_e_recomendar(wizard_data, resultados):
    """
    Analisa o perfil do usuário e recomenda a melhor opção
    
    Args:
        wizard_data: Dicionário com todos os dados do wizard
        resultados: Dict com resultados de cada cenário
        
    Returns:
        Dict com recomendação personalizada
    """
    
    # Extrai dados do perfil
    perfil = wizard_data.get('perfil_objetivos', {})
    perfil_usuario = perfil.get('perfil_usuario', 'comprador_morar')
    prioridade = perfil.get('prioridade_principal', 'equilibrio')
    
    # Prepara análise
    analise = {
        'recomendacao_principal': None,
        'motivo_recomendacao': '',
        'alertas': [],
        'destaques': {},
        'argumentos_pro': [],
        'argumentos_contra': [],
    }
    
    # Identifica métricas de cada cenário
    metricas = {}
    for nome, resultado in resultados.items():
        if resultado:
            metricas[nome] = {
                'custo_total': resultado.get('total_desembolso', resultado.get('total_custo', 0)),
                'parcela_inicial': resultado.get('parcela_inicial', 0),
                'prazo_anos': resultado.get('prazo_final_anos', resultado.get('prazo_anos', 0)),
                'patrimonio_final': resultado.get('patrimonio_final', 0),
            }
    
    if not metricas:
        return analise
    
    # Identifica extremos
    menor_custo = min(metricas.items(), key=lambda x: x[1]['custo_total'])
    menor_parcela = min(metricas.items(), key=lambda x: x[1]['parcela_inicial'])
    menor_prazo = min(metricas.items(), key=lambda x: x[1]['prazo_anos'])
    
    analise['destaques'] = {
        'mais_economico': {
            'cenario': _formatar_nome_cenario(menor_custo[0]),
            'valor': menor_custo[1]['custo_total'],
            'economia': max(metricas.items(), key=lambda x: x[1]['custo_total'])[1]['custo_total'] - menor_custo[1]['custo_total']
        },
        'menor_parcela': {
            'cenario': _formatar_nome_cenario(menor_parcela[0]),
            'valor': menor_parcela[1]['parcela_inicial']
        },
        'menor_prazo': {
            'cenario': _formatar_nome_cenario(menor_prazo[0]),
            'anos': menor_prazo[1]['prazo_anos']
        }
    }
    
    # LÓGICA DE RECOMENDAÇÃO BASEADA EM PRIORIDADE
    
    if prioridade == 'pagar_menos':
        # Prioridade: Economia máxima
        analise['recomendacao_principal'] = menor_custo[0]
        analise['motivo_recomendacao'] = f"🏆 Esta é a opção mais econômica! Você vai economizar R$ {_formatar_moeda(analise['destaques']['mais_economico']['economia'])} comparado à opção mais cara."
        
        if menor_custo[0] == 'consorcio':
            analise['argumentos_pro'] = [
                f"✅ Sem juros bancários: economia de R$ {_formatar_moeda(analise['destaques']['mais_economico']['economia'])}",
                "✅ Flexibilidade para dar lances e antecipar contemplação",
                "✅ Parcelas fixas e previsíveis",
            ]
            analise['argumentos_contra'] = [
                "⚠️ Você continua pagando aluguel enquanto não é contemplado",
                "⚠️ Prazo de contemplação é incerto (pode ser sorteado ou ofertar lance)",
                "⚠️ Não mora no imóvel imediatamente",
            ]
            analise['alertas'].append("💡 Dica: Se tem urgência para morar, considere financiamento. Se pode esperar, consórcio é muito mais econômico!")
        
    elif prioridade == 'parcelas_suaves':
        # Prioridade: Menor parcela
        analise['recomendacao_principal'] = menor_parcela[0]
        parcela_valor = menor_parcela[1]['parcela_inicial']
        analise['motivo_recomendacao'] = f"🏆 Esta opção tem a menor parcela inicial: R$ {_formatar_moeda(parcela_valor)}. Cabe melhor no seu orçamento!"
        
        if 'price' in menor_parcela[0]:
            analise['argumentos_pro'] = [
                f"✅ Parcela fixa e previsível: R$ {_formatar_moeda(parcela_valor)}",
                "✅ Mais fácil de planejar o orçamento mensal",
                "✅ Você mora no imóvel desde o início",
            ]
            analise['argumentos_contra'] = [
                f"⚠️ Custo total maior: R$ {_formatar_moeda(menor_custo[1]['custo_total'] - menor_parcela[1]['custo_total'])} a mais que a opção mais econômica",
                "⚠️ Amortização lenta no início (paga mais juros)",
            ]
            
    elif prioridade == 'quitar_rapido':
        # Prioridade: Menor prazo
        analise['recomendacao_principal'] = menor_prazo[0]
        prazo_valor = menor_prazo[1]['prazo_anos']
        analise['motivo_recomendacao'] = f"🏆 Esta opção tem o menor prazo: {prazo_valor:.1f} anos. Você fica livre da dívida mais rápido!"
        
        if 'sac' in menor_prazo[0]:
            analise['argumentos_pro'] = [
                f"✅ Quitação em apenas {prazo_valor:.1f} anos",
                "✅ Parcelas decrescem com o tempo",
                "✅ Economia significativa em juros",
            ]
            analise['argumentos_contra'] = [
                f"⚠️ Parcela inicial mais alta: R$ {_formatar_moeda(menor_prazo[1]['parcela_inicial'])}",
                "⚠️ Exige maior comprometimento de renda no início",
            ]
            
    elif prioridade == 'flexibilidade':
        # Prioridade: Flexibilidade
        if 'consorcio' in metricas:
            analise['recomendacao_principal'] = 'consorcio'
            analise['motivo_recomendacao'] = "🏆 Consórcio oferece maior flexibilidade: pode dar lances, transferir cota, ou resgatar valor."
            analise['argumentos_pro'] = [
                "✅ Pode transferir a cota para outra pessoa",
                "✅ Pode dar lances para antecipar",
                "✅ Se desistir, resgata valor pago (com desconto)",
                "✅ Sem análise de crédito rigorosa",
            ]
        else:
            analise['recomendacao_principal'] = menor_prazo[0]
            analise['motivo_recomendacao'] = "🏆 Prazo menor = mais flexibilidade futura. Você fica livre da dívida mais rápido."
            
    else:  # equilibrio
        # Prioridade: Equilíbrio (usa scoring)
        scores = {}
        for nome, metrica in metricas.items():
            # Normaliza valores (0-100, quanto maior melhor)
            score_custo = 100 * (1 - metrica['custo_total'] / max(m['custo_total'] for m in metricas.values()))
            score_parcela = 100 * (1 - metrica['parcela_inicial'] / max(m['parcela_inicial'] for m in metricas.values()))
            score_prazo = 100 * (1 - metrica['prazo_anos'] / max(m['prazo_anos'] for m in metricas.values()))
            
            # Score total (pesos iguais)
            scores[nome] = (score_custo + score_parcela + score_prazo) / 3
        
        melhor_equilibrio = max(scores.items(), key=lambda x: x[1])
        analise['recomendacao_principal'] = melhor_equilibrio[0]
        analise['motivo_recomendacao'] = "🏆 Esta opção oferece o melhor equilíbrio entre custo, parcela e prazo."
    
    # PERSONALIZAÇÃO POR PERFIL DE USUÁRIO
    
    if perfil_usuario == 'corretor':
        analise['dica_profissional'] = _gerar_dica_corretor(analise, metricas, wizard_data)
    elif perfil_usuario == 'vendedor_consorcio':
        analise['argumentos_venda'] = _gerar_argumentos_consorcio(metricas, wizard_data)
    
    return analise


def _formatar_nome_cenario(nome):
    """Formata nome do cenário para exibição"""
    nomes = {
        'price': 'Financiamento PRICE',
        'sac': 'Financiamento SAC',
        'consorcio': 'Consórcio',
        'aluguel_investimento': 'Aluguel + Investimento',
        'compra_a_vista': 'Compra à Vista',
    }
    return nomes.get(nome, nome.upper())


def _formatar_moeda(valor):
    """Formata valor para exibição em moeda brasileira"""
    if not valor:
        return '0,00'
    
    valor_float = float(valor)
    # Formata com separador de milhar (vírgula) e decimal (ponto) - padrão EUA
    valor_str_eua = f"{valor_float:,.2f}"
    
    # Troca vírgula por ponto (milhar) e ponto por vírgula (decimal)
    return valor_str_eua.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')


def _gerar_dica_corretor(analise, metricas, wizard_data):
    """Gera dicas específicas para corretores"""
    
    dicas = {
        'titulo': '📊 VISÃO DO PROFISSIONAL',
        'recomendacao_cliente': '',
        'pontos_atencao': [],
        'argumentos_venda': [],
    }
    
    renda = wizard_data.get('trabalho_renda', {}).get('renda_familiar_bruta', 0)
    capital = wizard_data.get('financas_atuais', {}).get('saldo_dinheiro_guardado', 0)
    
    recomendado = analise['recomendacao_principal']
    if recomendado in metricas:
        parcela = metricas[recomendado]['parcela_inicial']
        entrada_necessaria = capital
        
        dicas['recomendacao_cliente'] = f"✅ Mostre ao cliente: {_formatar_nome_cenario(recomendado)}"
        dicas['pontos_atencao'].append(f"⚠️ Cliente precisa ter R$ {_formatar_moeda(entrada_necessaria)} de entrada")
        
        if renda > 0:
            comprometimento = (parcela / renda) * 100
            if comprometimento > 30:
                dicas['pontos_atencao'].append(f"⚠️ Comprometimento de renda: {comprometimento:.1f}% (ideal <30%)")
            else:
                dicas['argumentos_venda'].append(f"✅ Comprometimento saudável: {comprometimento:.1f}% da renda")
        
        if 'destaques' in analise:
            economia = analise['destaques']['mais_economico']['economia']
            if economia > 0:
                dicas['argumentos_venda'].append(f"💡 Argumento forte: Economia de R$ {_formatar_moeda(economia)} vs opção mais cara")
    
    return dicas


def _gerar_argumentos_consorcio(metricas, wizard_data):
    """Gera argumentos específicos para vendedores de consórcio"""
    
    args = {
        'titulo': '🎲 ARGUMENTOS PRÓ-CONSÓRCIO',
        'vantagens': [],
        'como_contornar_objecoes': [],
    }
    
    if 'consorcio' in metricas and 'price' in metricas:
        economia = metricas['price']['custo_total'] - metricas['consorcio']['custo_total']
        
        args['vantagens'] = [
            f"✅ Sem juros bancários: Economia de R$ {_formatar_moeda(economia)}",
            "✅ Flexibilidade: Pode dar lances para antecipar",
            "✅ Parcelas fixas e menores",
            "✅ Não precisa comprovar renda tão rigorosamente",
        ]
        
        args['como_contornar_objecoes'] = [
            {
                'objecao': '"Mas eu preciso morar logo!"',
                'resposta': 'Lance de entrada pode te contemplar em 30-60 dias. Além disso, você economiza R$ {:.0f} - dá pra pagar muito aluguel com isso!'.format(economia),
            },
            {
                'objecao': '"E se eu não for sorteado?"',
                'resposta': 'Estatisticamente, 90% são contemplados em até 3 anos. E você sempre pode ofertar lance. Não é "se", é "quando".',
            },
            {
                'objecao': '"Financiamento é mais garantido"',
                'resposta': f'Sim, mas custa R$ {_formatar_moeda(economia)} a mais. É pagar pela "urgência". Se pode esperar um pouco, vale muito a pena.',
            },
        ]
    
    return args
