"""
Wizard V2 - Views Reorganizadas com Inteligência de Recomendação
"""
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SavedSimulation
from . import wizard_forms_v2 as forms_v2
from .utils import calcular_margem_credito, calcular_acumulo_fgts, calcular_cenario_80_porcento
from .recomendacao_inteligente import analisar_perfil_e_recomendar
from .calculadora_financeira import calcular_mcmv, calcular_price_sac
from .formatacao import formatar_moeda_brl


# Constantes
WIZARD_STEPS_V2 = {
    1: {
        'form': forms_v2.WizardPerfilObjetivosForm,
        'name': 'perfil_objetivos',
        'title': 'Perfil & Objetivos',
        'icon': '🎯'
    },
    2: {
        'form': forms_v2.WizardTrabalhoRendaForm,
        'name': 'trabalho_renda',
        'title': 'Trabalho & Renda',
        'icon': '💼'
    },
    3: {
        'form': forms_v2.WizardFinancasAtuaisForm,
        'name': 'financas_atuais',
        'title': 'Finanças Atuais',
        'icon': '💰'
    },
    4: {
        'form': forms_v2.WizardImovelDesejadoForm,
        'name': 'imovel_desejado',
        'title': 'Imóvel Desejado',
        'icon': '🏡'
    },
    5: {
        'form': forms_v2.WizardCenariosForm,
        'name': 'cenarios',
        'title': 'Cenários',
        'icon': '📊'
    },
}
TOTAL_STEPS_V2 = len(WIZARD_STEPS_V2)


def _convert_decimals_to_floats(data):
    """Converte Decimal para float recursivamente"""
    if isinstance(data, dict):
        return {k: _convert_decimals_to_floats(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_convert_decimals_to_floats(item) for item in data]
    elif isinstance(data, Decimal):
        return float(data)
    return data


def wizard_v2(request, step=None):
    """
    View principal do wizard V2
    """
    
    # Inicializa sessão
    if 'wizard_v2_data' not in request.session:
        request.session['wizard_v2_data'] = {}
        request.session['wizard_v2_current_step'] = 1
    
    # Determina passo atual
    if step:
        try:
            current_step = int(step)
            if current_step < 1 or current_step > TOTAL_STEPS_V2:
                current_step = request.session.get('wizard_v2_current_step', 1)
        except ValueError:
            current_step = request.session.get('wizard_v2_current_step', 1)
    else:
        current_step = request.session.get('wizard_v2_current_step', 1)
    
    wizard_data = request.session.get('wizard_v2_data', {})
    step_info = WIZARD_STEPS_V2[current_step]
    form_class = step_info['form']
    
    # Processa POST
    if request.method == 'POST':
        form = form_class(request.POST, wizard_data=wizard_data)
        
        if form.is_valid():
            # Salva dados convertendo Decimal para float
            cleaned_data = _convert_decimals_to_floats(form.cleaned_data)
            wizard_data[step_info['name']] = cleaned_data
            request.session['wizard_v2_data'] = wizard_data
            
            # Próximo passo
            if current_step < TOTAL_STEPS_V2:
                next_step = current_step + 1
                request.session['wizard_v2_current_step'] = next_step
                return redirect('wizard_v2_step', step=next_step)
            else:
                # Última etapa - calcular resultados
                return redirect('wizard_v2_resultados')
    else:
        # GET - carrega dados salvos
        initial_data = wizard_data.get(step_info['name'], {})
        form = form_class(initial=initial_data, wizard_data=wizard_data)
    
    context = {
        'form': form,
        'current_step': current_step,
        'total_steps': TOTAL_STEPS_V2,
        'step_title': step_info['title'],
        'step_icon': step_info['icon'],
        'progress_percent': (current_step / TOTAL_STEPS_V2) * 100,
        'can_go_back': current_step > 1,
    }
    
    return render(request, 'simulacao/wizard_v2_step.html', context)


def wizard_v2_resultados(request):
    """
    Calcula e exibe resultados com recomendação inteligente
    """
    
    wizard_data = request.session.get('wizard_v2_data', {})
    
    if not wizard_data:
        return redirect('wizard_v2')
    
    # Extrai dados
    perfil_obj = wizard_data.get('perfil_objetivos', {})
    trabalho = wizard_data.get('trabalho_renda', {})
    financas = wizard_data.get('financas_atuais', {})
    imovel = wizard_data.get('imovel_desejado', {})
    cenarios = wizard_data.get('cenarios', {})
    
    # Dados principais
    valor_imovel = Decimal(str(imovel.get('valor_imovel_desejado', 500000)))
    prazo_anos = int(imovel.get('prazo_desejado_anos', 30))
    prazo_meses = prazo_anos * 12
    
    capital_guardado = Decimal(str(financas.get('saldo_dinheiro_guardado', 0)))
    fgts_saldo = Decimal(str(financas.get('saldo_fgts', 0)))
    
    valor_imovel_proprio = Decimal(str(financas.get('valor_imovel_proprio', 0)))
    if perfil_obj.get('onde_mora_atualmente') == 'proprio':
        capital_guardado += valor_imovel_proprio
    
    renda_bruta = Decimal(str(trabalho.get('renda_familiar_bruta', 0)))
    aluguel_atual = Decimal(str(perfil_obj.get('aluguel_atual', 0)))
    
    custas_documentacao = Decimal('15000')
    custas_documentacao_forma = imovel.get('custas_documentacao_forma', 'financiado')
    
    # Calcula entrada
    entrada = capital_guardado
    if custas_documentacao_forma == 'a_vista':
        entrada = entrada - custas_documentacao
    
    # Calcula principal
    principal = valor_imovel - entrada
    if custas_documentacao_forma == 'financiado':
        principal = principal + custas_documentacao
    
    # Calcula margem de crédito
    outras_rendas = Decimal(str(trabalho.get('outras_rendas', 0)))
    margem_info = calcular_margem_credito(
        renda_familiar_bruta=float(renda_bruta),
        outras_rendas=float(outras_rendas)
    )
    # FIX BUG 2: Adicionar margem disponível se estiver vazio
    if margem_info:
        margem_info['margem_disponivel'] = float(renda_bruta * Decimal('0.30'))
        margem_info['margem_disponivel_fmt'] = formatar_moeda_brl(margem_info['margem_disponivel'])
        margem_info['margem_30_porcento'] = margem_info['parcela_maxima']
        margem_info['desconto_aplicado'] = margem_info['desconto_aplicado_outras_rendas']
    
    # Calcula FGTS futuro (se CLT)
    tipo_contrato = trabalho.get('tipo_contrato', '')
    fgts_futuro = None
    if tipo_contrato == 'clt' and renda_bruta > 0:
        fgts_futuro = calcular_acumulo_fgts(
            salario_bruto=float(renda_bruta),
            meses_ate_compra=prazo_meses
        )
        # FIX BUG 3: Adicionar depósito mensal se estiver vazio
        if fgts_futuro:
            fgts_futuro['deposito_mensal'] = float(renda_bruta * Decimal('0.08'))
            fgts_futuro['total_depositado'] = fgts_futuro['deposito_mensal'] * prazo_meses
            fgts_futuro['saldo_final'] = fgts_futuro['saldo_estimado']
            fgts_futuro['meses'] = prazo_meses
            fgts_futuro['rendimento_acumulado'] = fgts_futuro['saldo_estimado'] - fgts_futuro['total_depositado']
            fgts_futuro['taxa_efetiva_anual'] = 3.0
    
    # Verifica cenário 80%
    capital_total = capital_guardado + fgts_saldo
    percentual_capital = (capital_total / valor_imovel) * Decimal('100') if valor_imovel > 0 else Decimal('0')
    cenario_80 = None
    
    if percentual_capital >= Decimal('80'):
        # Calcula cenário especial
        cenario_80 = calcular_cenario_80_porcento(
            valor_imovel=float(valor_imovel),
            capital_disponivel=float(capital_total),
            aluguel_mensal=float(aluguel_atual),
            taxa_juros_financiamento=8.5,
            taxa_investimento=float(cenarios.get('taxa_investimento_esperada', 9.5)),
            prazo_anos=5
        )
    
    # Calcula cenários selecionados
    resultados = {}
    
    # --- FINANCIAMENTOS TRADICIONAIS ---
    # PRICE
    if cenarios.get('comparar_financiamento_price'):
        resultado_price = _calcular_financiamento(
            metodo='price',
            valor_principal=principal,
            taxa_anual=Decimal('8.5'),
            prazo_meses=prazo_meses,
            renda_familiar=renda_bruta,
            fgts_saldo=fgts_saldo if cenarios.get('usar_fgts') else Decimal('0'),
            usar_fgts=cenarios.get('usar_fgts', True),
            aluguel_durante=aluguel_atual,
        )
        resultados['price'] = resultado_price
    
    # SAC
    if cenarios.get('comparar_financiamento_sac'):
        resultado_sac = _calcular_financiamento(
            metodo='sac',
            valor_principal=principal,
            taxa_anual=Decimal('8.5'),
            prazo_meses=prazo_meses,
            renda_familiar=renda_bruta,
            fgts_saldo=fgts_saldo if cenarios.get('usar_fgts') else Decimal('0'),
            usar_fgts=cenarios.get('usar_fgts', True),
            aluguel_durante=aluguel_atual,
        )
        resultados['sac'] = resultado_sac
    
    # --- CONSÓRCIO ---
    # Consórcio (com detalhes)
    if cenarios.get('comparar_consorcio'):
        resultado_consorcio = _calcular_consorcio_detalhado(
            valor_carta=valor_imovel,
            prazo_meses=int(cenarios.get('prazo_consorcio', 180)),
            estrategia=cenarios.get('estrategia_contemplacao', 'sorteio'),
            valor_lance=Decimal(str(cenarios.get('valor_lance_disponivel', 0))),
            tempo_maximo=int(cenarios.get('tempo_maximo_espera_consorcio', 36)),
            aluguel_mensal=aluguel_atual,
            capital_inicial=capital_guardado,
        )
        resultados['consorcio'] = resultado_consorcio
    
    # --- GUARDAR DINHEIRO ---
    # Guardar Dinheiro
    if cenarios.get('comparar_guardar_dinheiro'):
        despesas_fixas = Decimal(str(financas.get('despesas_mensais_fixas', 0)))
        renda_disponivel = renda_bruta - aluguel_atual - despesas_fixas

        # FIX BUG 5: Usar menor parcela (SAC/PRICE) como referência se disponível
        valor_referencia = renda_disponivel
        parcelas_simuladas = []
        if 'price' in resultados: parcelas_simuladas.append(Decimal(str(resultados['price'].get('parcela_inicial', 0))))
        if 'sac' in resultados: parcelas_simuladas.append(Decimal(str(resultados['sac'].get('parcela_inicial', 0))))
        
        if parcelas_simuladas:
            valor_referencia = min(p for p in parcelas_simuladas if p > 0)

        taxa_retorno = Decimal(str(cenarios.get('taxa_investimento_esperada', 9.5)))
        
        resultado_guardar = _calcular_guardar_dinheiro(
            capital_inicial=capital_guardado,
            valor_imovel_alvo=valor_imovel,
            taxa_retorno_anual=taxa_retorno,
            renda_disponivel_mensal=max(valor_referencia, Decimal('100')), # Mínimo R$ 100
            aluguel_mensal=aluguel_atual
        )
        
        if resultado_guardar:
            resultados['guardar_dinheiro'] = resultado_guardar

    # --- CENÁRIOS MIGRADOS ---
    taxa_investimento = Decimal(str(cenarios.get('taxa_investimento_esperada', 9.5)))

    # MCMV
    if cenarios.get('comparar_mcmv'):
        resultado_mcmv = calcular_mcmv(
            valor_imovel=valor_imovel,
            renda_familiar_mensal=renda_bruta,
            valor_entrada=capital_guardado,
            prazo_meses=prazo_meses,
            usa_fgts=cenarios.get('usar_fgts', True),
            valor_fgts_disponivel=fgts_saldo
        )
        if resultado_mcmv['qualificado']:
            resultado_mcmv['metodo'] = f"MCMV - Faixa {resultado_mcmv['faixa']}"
            resultado_mcmv['parcela_inicial'] = resultado_mcmv['parcela_media']
            resultado_mcmv['total_desembolso'] = resultado_mcmv['custo_total'] + float(capital_guardado)
            resultado_mcmv['patrimonio_final'] = float(valor_imovel)
            resultados['mcmv'] = resultado_mcmv

    # Aluguel + Investimento
    if cenarios.get('comparar_aluguel_investimento'):
        resultado_aluguel = _v2_calcular_aluguel_investimento(
            aluguel_mensal=aluguel_atual,
            capital_inicial=capital_guardado,
            renda_bruta=renda_bruta,
            taxa_investimento=taxa_investimento,
            prazo_anos=prazo_anos,
            valor_imovel_futuro=valor_imovel,
        )
        resultados['aluguel_investimento'] = resultado_aluguel

    # Compra à Vista
    if cenarios.get('comparar_compra_a_vista') and capital_guardado >= valor_imovel:
        resultado_a_vista = _v2_calcular_compra_a_vista(
            valor_imovel=valor_imovel,
            capital_disponivel=capital_guardado,
            taxa_investimento=taxa_investimento,
            prazo_anos=prazo_anos,
        )
        if resultado_a_vista:
            resultados['compra_a_vista'] = resultado_a_vista
    
    # Gera recomendação inteligente
    analise = analisar_perfil_e_recomendar(wizard_data, resultados)
    
    # Ordena resultados por custo total (do maior para o menor = pior para melhor)
    # Assim a melhor opção aparece por último, facilitando a leitura
    resultados_ordenados = dict(sorted(
        resultados.items(),
        key=lambda item: item[1].get('total_custo', 0),
        reverse=True  # Maior custo primeiro (pior opção)
    ))
    
    # FIX BUG 4: Formatação monetária (Separadores de milhar)
    # Cria uma cópia formatada para exibição
    resultados_formatados = {}
    keys_monetarias = ['parcela_inicial', 'total_custo', 'total_desembolso', 'patrimonio_final', 
                       'total_juros', 'total_principal', 'aluguel_durante', 'total_aluguel_gasto',
                       'montante_final_investimento', 'ganho_com_investimento', 'sobra_apos_compra',
                       'patrimonio_final_total', 'valor_lance', 'taxa_administracao', 'fundo_reserva']

    for key, data in resultados_ordenados.items():
        data_fmt = data.copy()
        for k, v in data.items():
            if k in keys_monetarias and isinstance(v, (int, float, Decimal)):
                data_fmt[k] = formatar_moeda_brl(v)
        resultados_formatados[key] = data_fmt

    context = {
        'resultados': resultados_formatados,
        'analise': analise,
        'wizard_data': wizard_data,
        'valor_imovel': float(valor_imovel),
        'entrada': float(entrada),
        'principal': float(principal),
        'margem_credito': margem_info,
        'fgts_futuro': fgts_futuro,
        'cenario_80': cenario_80,
        'percentual_capital': float(percentual_capital),
    }
    
    return render(request, 'simulacao/wizard_v2_resultados.html', context)


def _v2_calcular_aluguel_investimento(aluguel_mensal, capital_inicial, renda_bruta,
                                   taxa_investimento, prazo_anos, valor_imovel_futuro):
    """
    (MIGRADO) Calcula cenário de aluguel contínuo + investimento da diferença.
    """
    prazo_meses = prazo_anos * 12
    custo_aluguel_total = aluguel_mensal * Decimal(prazo_meses)
    renda_disponivel = renda_bruta - (aluguel_mensal + Decimal('2000'))
    aporte_mensal = max(renda_disponivel * Decimal('0.1'), Decimal('0'))
    total_aportes = aporte_mensal * Decimal(prazo_meses)
    taxa_mensal = (taxa_investimento / 100) / 12
    montante_investido = capital_inicial
    
    for mes in range(prazo_meses):
        montante_investido = montante_investido * (1 + taxa_mensal) + aporte_mensal
    
    ganho_investimento = montante_investido - capital_inicial - total_aportes
    pode_comprar = montante_investido >= valor_imovel_futuro
    patrimonio_final = montante_investido
    
    comprometimento = (aluguel_mensal / renda_bruta) * 100 if renda_bruta > 0 else Decimal('0')

    return {
        'metodo': 'Aluguel + Investimento',
        'parcela_inicial': float(aluguel_mensal),
        'aluguel_mensal': formatar_moeda_brl(aluguel_mensal),
        'total_aluguel_gasto': formatar_moeda_brl(custo_aluguel_total),
        'aporte_mensal_investimento': formatar_moeda_brl(aporte_mensal),
        'total_aportes': float(total_aportes),
        'capital_inicial': float(capital_inicial),
        'taxa_investimento': float(taxa_investimento),
        'montante_final_investimento': float(montante_investido),
        'ganho_com_investimento': float(ganho_investimento),
        'pode_comprar_imovel': pode_comprar,
        'valor_imovel_alvo': float(valor_imovel_futuro),
        'sobra_apos_compra': float(montante_investido - valor_imovel_futuro) if pode_comprar else 0.0,
        'patrimonio_final_total': float(montante_investido),
        'total_custo': float(custo_aluguel_total),
        'total_desembolso': float(custo_aluguel_total),
        'patrimonio_final': float(patrimonio_final),
        'prazo_final_anos': prazo_anos,
        'resumo_explicativo': f'💸 Continue alugando e invista a diferença. Seu dinheiro rende e pode superar a valorização do imóvel. Ideal se você não tem pressa e busca flexibilidade.',
        'comprometimento_renda': float(comprometimento),
        'alerta_comprometimento': comprometimento > 30,
    }


def _v2_calcular_compra_a_vista(valor_imovel, capital_disponivel, taxa_investimento, prazo_anos):
    """
    (MIGRADO) Calcula compra à vista do imóvel + investimento da sobra.
    """
    prazo_meses = prazo_anos * 12
    sobra = capital_disponivel - valor_imovel
    
    if sobra <= 0:
        return None
    
    taxa_mensal = (taxa_investimento / 100) / 12
    montante_investido = sobra
    
    for _ in range(prazo_meses):
        montante_investido = montante_investido * (1 + taxa_mensal)
    
    patrimonio_total = valor_imovel + montante_investido
    
    return {
        'metodo': 'Compra à Vista + Investimento',
        'valor_imovel_comprado': float(valor_imovel),
        'capital_disponivel': float(capital_disponivel),
        'valor_sobra_para_investir': float(sobra),
        'montante_investido_final': float(montante_investido),
        'patrimonio_final': float(patrimonio_total),
        'total_custo': float(valor_imovel),
        'total_desembolso': float(valor_imovel),
        'resumo_explicativo': '🎉 Parabéns! Comprar à vista elimina dívidas e juros. A sobra do seu capital continua rendendo, aumentando seu patrimônio.',
    }


def _calcular_guardar_dinheiro(capital_inicial, valor_imovel_alvo, taxa_retorno_anual, 
                               renda_disponivel_mensal, aluguel_mensal, fgts_saldo=0):
    """
    Calcula quanto tempo leva para juntar o valor do imóvel investindo
    Agora considera FGTS como investimento inicial
    """
    taxa_mensal = (Decimal('1') + taxa_retorno_anual / Decimal('100')) ** (Decimal('1') / Decimal('12')) - Decimal('1')
    
    # Adiciona FGTS ao capital inicial
    capital_inicial_total = capital_inicial + Decimal(str(fgts_saldo))
    montante = capital_inicial_total
    meses = 0
    max_meses = 360  # 30 anos
    
    total_aportes = Decimal('0')
    total_aluguel = Decimal('0')
    
    # Investimento mensal = renda disponível (pode ser ajustado)
    investimento_mensal = renda_disponivel_mensal
    
    while montante < valor_imovel_alvo and meses < max_meses:
        meses += 1
        
        # Rendimento do mês
        rendimento = montante * taxa_mensal
        montante += rendimento
        
        # Aporte mensal (investimento)
        montante += investimento_mensal
        total_aportes += investimento_mensal
        
        # Custo de aluguel
        total_aluguel += aluguel_mensal
    
    if montante >= valor_imovel_alvo:
        anos = round(meses / 12, 1)
        ganho_investimento = montante - capital_inicial_total - total_aportes
        
        
        # NOVO: Calcula valorização do imóvel
        TAXA_VALORIZACAO_IMOVEL = Decimal('0.05')  # 5% ao ano
        anos_decimal = Decimal(str(meses)) / Decimal('12')
        valor_imovel_futuro = valor_imovel_alvo * ((Decimal('1') + TAXA_VALORIZACAO_IMOVEL) ** anos_decimal)
        
        # NOVO: Calcula investimento do aluguel pós-compra (até completar 30 anos)
        meses_pos_compra = 360 - meses
        montante_aluguel_investido = Decimal('0')
        
        if meses_pos_compra > 0:
            for _ in range(meses_pos_compra):
                rendimento = montante_aluguel_investido * taxa_mensal
                montante_aluguel_investido += rendimento + aluguel_mensal
        
        # Patrimônio final total = imóvel valorizado + investimento do aluguel
        patrimonio_final_total = valor_imovel_futuro + montante_aluguel_investido

        # Calcula economia vs financiamento (estimativa)
        economia_vs_financiamento = ganho_investimento
        
        return {
            'metodo': 'Guardar Dinheiro',
            'meses_necessarios': meses,
            'prazo_final_anos': anos,
            'montante_final': float(montante),
            'capital_inicial': float(capital_inicial_total),
            'parcela_inicial': float(investimento_mensal),
            'fgts_usado': float(fgts_saldo),
            'total_aportes': float(total_aportes),
            'ganho_investimento': float(ganho_investimento),
            'total_aluguel': float(total_aluguel),
            'total_custo': float(capital_inicial_total + total_aportes),
            'total_desembolso': float(capital_inicial_total + total_aportes + total_aluguel),
            
            # NOVOS CAMPOS:
            'valor_imovel_inicial': float(valor_imovel_alvo),
            'valor_imovel_futuro': float(valor_imovel_futuro),
            'taxa_valorizacao_imovel': float(TAXA_VALORIZACAO_IMOVEL * 100),
            'meses_pos_compra': meses_pos_compra,
            'montante_aluguel_investido': float(montante_aluguel_investido),
            'patrimonio_final': float(patrimonio_final_total),
            
            'resumo_explicativo': f'💰 Invista {formatar_moeda_brl(investimento_mensal)}/mês durante {anos} anos. (Este valor foi sugerido com base na parcela média de um financiamento, para você criar um hábito de investimento em vez de pagar juros). Compre à vista quando juntar o valor. Depois, invista o aluguel ({formatar_moeda_brl(aluguel_mensal)}/mês) e acumule mais patrimônio!',
            'observacao': f'Estratégia completa: 1) Investe {anos} anos até juntar {formatar_moeda_brl(valor_imovel_alvo)}. 2) Compra imóvel à vista (valorizado para {formatar_moeda_brl(valor_imovel_futuro)}). 3) Investe o aluguel por mais {meses_pos_compra/12:.1f} anos = {formatar_moeda_brl(montante_aluguel_investido)}. Patrimônio final: {formatar_moeda_brl(patrimonio_final_total)}!'
        }
    else:
        return None


def _calcular_consorcio_detalhado(valor_carta, prazo_meses, estrategia, valor_lance, 
                                   tempo_maximo, aluguel_mensal, capital_inicial):
    """
    Calcula consórcio com detalhes realistas:
    - Taxa de administração (18%)
    - Fundo de reserva (1%)
    - Seguro (0,02% ao mês)
    - Tempo de contemplação baseado na estratégia
    """
    from decimal import Decimal
    
    # Taxas reais do consórcio
    TAXA_ADMINISTRACAO = Decimal('0.18')  # 18% do valor da carta
    TAXA_FUNDO_RESERVA = Decimal('0.01')  # 1% do valor da carta
    TAXA_SEGURO_MENSAL = Decimal('0.0002')  # 0,02% ao mês
    
    # Calcula custos
    custo_taxa_admin = valor_carta * TAXA_ADMINISTRACAO
    custo_fundo_reserva = valor_carta * TAXA_FUNDO_RESERVA
    valor_total_consorcio = valor_carta + custo_taxa_admin + custo_fundo_reserva
    
    # Parcela mensal base (antes da contemplação)
    parcela_base = valor_total_consorcio / Decimal(prazo_meses)
    seguro_mensal = valor_carta * TAXA_SEGURO_MENSAL
    parcela_mensal_antes = parcela_base + seguro_mensal
    
    # Estima tempo de contemplação baseado na estratégia
    if estrategia == 'lance_unico' and valor_lance >= valor_carta * Decimal('0.30'):
        # Lance de 30%+ contempla rápido (1-3 meses)
        meses_ate_contemplacao = 2
        observacao = f"Lance de {float(valor_lance/valor_carta*100):.1f}% contempla em ~2 meses"
    elif estrategia == 'lances_mensais':
        # Lances mensais contemplam em média 20-30% do prazo
        meses_ate_contemplacao = int(prazo_meses * 0.25)
        observacao = f"Lances mensais: contemplação estimada em {meses_ate_contemplacao} meses"
    else:  # sorteio
        # Sorteio puro: média de 50% do prazo
        meses_ate_contemplacao = int(prazo_meses * 0.50)
        observacao = f"Apenas sorteio: contemplação média em {meses_ate_contemplacao} meses ({meses_ate_contemplacao/12:.1f} anos)"
    
    # Verifica viabilidade com tempo máximo
    viavel = meses_ate_contemplacao <= tempo_maximo
    if not viavel:
        observacao += f" ⚠️ ATENÇÃO: Você precisa em {tempo_maximo} meses, mas contemplação estimada é {meses_ate_contemplacao} meses"
    
    # Após contemplação, parcela muda (só amortização + seguro, sem taxa admin)
    meses_restantes = prazo_meses - meses_ate_contemplacao
    parcela_apos_contemplacao = (valor_carta / Decimal(meses_restantes)) + seguro_mensal if meses_restantes > 0 else Decimal('0')
    
    # Calcula custos totais
    custo_antes_contemplacao = parcela_mensal_antes * Decimal(meses_ate_contemplacao)
    custo_apos_contemplacao = parcela_apos_contemplacao * Decimal(meses_restantes) if meses_restantes > 0 else Decimal('0')
    custo_total_consorcio = custo_antes_contemplacao + custo_apos_contemplacao + valor_lance
    
    # Custo de aluguel durante o período até contemplação
    custo_aluguel_ate_contemplacao = aluguel_mensal * Decimal(meses_ate_contemplacao)
    
    # Total desembolsado (consórcio + aluguel até ter o imóvel)
    total_desembolso = custo_total_consorcio + custo_aluguel_ate_contemplacao
    
    return {
        'metodo': 'Consórcio',
        'parcela_inicial': float(parcela_mensal_antes),
        'parcela_apos_contemplacao': float(parcela_apos_contemplacao),
        'meses_ate_contemplacao': meses_ate_contemplacao,
        'anos_ate_contemplacao': round(meses_ate_contemplacao / 12, 1),
        'total_juros': 0,  # Consórcio não tem juros
        'taxa_administracao': float(custo_taxa_admin),
        'fundo_reserva': float(custo_fundo_reserva),
        'valor_lance': float(valor_lance),
        'total_custo': float(custo_total_consorcio),
        'total_custo_consorcio': float(custo_total_consorcio),
        'custo_aluguel_durante': float(custo_aluguel_ate_contemplacao),
        'total_desembolso': float(total_desembolso),
        'prazo_final_anos': round(prazo_meses / 12, 1),
        'prazo_final_meses': prazo_meses,
        'patrimonio_final': float(valor_carta),
        'resumo_explicativo': f'''🎲 <strong>Por que Consórcio pode ser vantajoso?</strong><br><br>

<strong>Sem juros bancários:</strong> O consórcio NÃO cobra juros! Você paga apenas o valor do imóvel ({formatar_moeda_brl(valor_carta)}) + taxa de administração ({float(TAXA_ADMINISTRACAO*100):.0f}% = {formatar_moeda_brl(custo_taxa_admin)}) + fundo de reserva ({float(TAXA_FUNDO_RESERVA*100):.0f}% = {formatar_moeda_brl(custo_fundo_reserva)}). Total: {formatar_moeda_brl(custo_total_consorcio)}.<br><br>

<strong>Contemplação:</strong> Você precisa ser contemplado (sorteio ou lance) para receber a carta. Com sua estratégia ({estrategia}), a contemplação estimada é em {meses_ate_contemplacao} meses ({round(meses_ate_contemplacao/12, 1)} anos). Até lá, você paga parcelas de {formatar_moeda_brl(parcela_mensal_antes)} e continua pagando aluguel de {formatar_moeda_brl(aluguel_mensal)}.<br><br>

<strong>Após contemplação:</strong> Quando receber o imóvel, a parcela cai para {formatar_moeda_brl(parcela_apos_contemplacao)} (sem taxa de administração) e você para de pagar aluguel. O prazo total é {round(prazo_meses/12, 1)} anos, mais longo que financiamentos.<br><br>

<strong>Recomendado se:</strong> Você tem tempo (não precisa do imóvel urgente), quer evitar juros altos, pode dar lances para acelerar a contemplação e prefere parcelas menores. Atenção: até ser contemplado, você paga consórcio + aluguel simultaneamente.''',
        'observacao': observacao,
        'viavel_no_prazo': viavel,
        'estrategia': estrategia,
    }


def _calcular_financiamento(metodo, valor_principal, taxa_anual, prazo_meses, renda_familiar,
                            fgts_saldo, usar_fgts, aluguel_durante):
    """
    Calcula financiamento PRICE ou SAC
    """
    resultado = calcular_price_sac(
        metodo=metodo,
        valor_principal=valor_principal,
        taxa_anual=taxa_anual,
        prazo_meses=prazo_meses,
        seguro_mensal=0.0,
        taxa_admin_mensal=0.0,
        usar_fgts_financiamento=usar_fgts,
        fgts_saldo=fgts_saldo if usar_fgts else 0,
        tipo_amortizacao_fgts='reduzir_prazo',
        mes_uso_fgts_financiamento=1
    )
    
    tabela = resultado.get('tabela', [])
    if not tabela:
        return {
            'metodo': f'Financiamento {metodo.upper()}',
            'parcela_inicial': 0,
            'total_custo': float(valor_principal),
            'total_desembolso': float(valor_principal),
            'prazo_final_anos': prazo_meses / 12,
            'patrimonio_final': float(valor_principal),
        }
    
    # FIX BUG 1: Usar 'parcela' que vem de calculadora_financeira.py, não 'parcela_total'
    parcela_inicial = Decimal(str(resultado.get('parcela_inicial', tabela[0].get('parcela', 0))))
    total_juros = Decimal(str(resultado.get('total_juros', 0)))
    # FIX BUG 3: Usar o prazo_final_meses enviado pela calculadora em vez do len(tabela) que inclui FGTS
    prazo_final = resultado.get('prazo_final_meses', len(tabela))
    
    custo_total = valor_principal + total_juros
    meses_aluguel = min(prazo_final, int(prazo_meses))
    custo_aluguel = aluguel_durante * Decimal(meses_aluguel)
    total_desembolso = custo_total + custo_aluguel
    
    # Define resumo explicativo baseado no método
    if metodo.lower() == 'sac':
        resumo = f'''📉 <strong>Por que SAC é melhor para economizar?</strong><br><br>
        
<strong>Menor custo total:</strong> O SAC (Sistema de Amortização Constante) tem o menor custo total de juros entre todos os financiamentos. Você pagará {formatar_moeda_brl(total_juros)} de juros ao longo de {round(prazo_final/12, 1)} anos.<br><br>

<strong>Parcelas decrescentes:</strong> A primeira parcela é de {formatar_moeda_brl(parcela_inicial)}, mas ela diminui todo mês. Isso significa que com o tempo seu orçamento fica mais folgado, permitindo investir a diferença ou quitar antecipadamente.<br><br>

<strong>Ideal para CLT:</strong> Se você é CLT, pode usar o FGTS para amortizar a dívida anualmente, reduzindo ainda mais os juros. Como o FGTS rende apenas 3% ao ano (muito abaixo da inflação), é melhor usar para reduzir uma dívida que cobra {float(taxa_anual)}% ao ano.<br><br>

<strong>Recomendado se:</strong> Você tem renda estável, pode pagar parcelas maiores no início e quer economizar no longo prazo. Quanto mais rápido amortizar, menos juros pagará.'''
    else:  # PRICE
        resumo = f'''📊 <strong>Por que PRICE facilita seu planejamento?</strong><br><br>

<strong>Parcelas fixas:</strong> Todas as {prazo_final} parcelas são iguais: {formatar_moeda_brl(parcela_inicial)}. Isso facilita muito o planejamento financeiro, pois você sabe exatamente quanto vai pagar todo mês até o final.<br><br>

<strong>Orçamento apertado no início:</strong> Se sua renda está no limite ou você tem outras despesas importantes nos primeiros anos (filhos pequenos, carro financiado, etc.), o PRICE é ideal porque a parcela inicial é menor que o SAC.<br><br>

<strong>Atenção aos juros:</strong> O custo total de juros é {formatar_moeda_brl(total_juros)}, um pouco maior que o SAC. Isso acontece porque você amortiza o principal mais devagar, então paga juros sobre um saldo maior por mais tempo.<br><br>

<strong>Recomendado se:</strong> Você prefere previsibilidade, tem orçamento apertado no início ou planeja aumentar sua renda nos próximos anos (promoções, novos projetos). Também é bom para quem quer investir a diferença em aplicações que rendem mais que os juros do financiamento.'''
    
    return {
        'metodo': f'Financiamento {metodo.upper()}',
        'parcela_inicial': float(parcela_inicial),
        'total_juros': float(total_juros),
        'total_principal': float(valor_principal),
        'total_custo': float(custo_total),
        'prazo_final_meses': prazo_final,
        'prazo_final_anos': round(prazo_final / 12, 1),
        'aluguel_durante': float(custo_aluguel),
        'total_desembolso': float(total_desembolso),
        'patrimonio_final': float(valor_principal),
        'resumo_explicativo': resumo,
    }


def wizard_v2_reset(request):
    """Reseta o wizard"""
    if 'wizard_v2_data' in request.session:
        del request.session['wizard_v2_data']
    if 'wizard_v2_current_step' in request.session:
        del request.session['wizard_v2_current_step']
    return redirect('wizard_v2')


@login_required
def salvar_simulacao_v2(request):
    """
    (MIGRADO) Salva a simulação V2 no banco de dados para o usuário logado.
    """
    if 'wizard_v2_data' not in request.session:
        messages.warning(request, "Nenhuma simulação encontrada para salvar.")
        return redirect('wizard_v2')
    
    wizard_data = request.session.get('wizard_v2_data', {})
    resultados = request.session.get('wizard_v2_resultados', {})
    
    # Cria um nome descritivo baseado no valor do imóvel
    valor = wizard_data.get('imovel_desejado', {}).get('valor_imovel_desejado', 0)
    try:
        valor_fmt = f"{float(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        valor_fmt = str(valor)
        
    nome = f"Simulação V2 R$ {valor_fmt}"
    
    SavedSimulation.objects.create(
        user=request.user,
        titulo=nome,
        dados_wizard=wizard_data,
        resultados=resultados
    )
    
    messages.success(request, "Simulação salva com sucesso no seu Dashboard!")
    return redirect('dashboard')


def exportar_pdf_simulacao_v2(request):
    """
    (MIGRADO) Gera um PDF com os resultados da simulação V2.
    """
    try:
        from xhtml2pdf import pisa
    except ImportError:
        return HttpResponse("Erro: Biblioteca xhtml2pdf não instalada. Execute: pip install xhtml2pdf")

    if 'wizard_v2_resultados' not in request.session:
        messages.warning(request, "Nenhuma simulação para exportar.")
        return redirect('wizard_v2')

    # Esta função agora é um stub. A lógica completa de geração de PDF
    # com gráficos e tabelas está na view `exportar_simulacao_pdf` que
    # usa um ID de simulação salva, que é uma feature premium.
    return HttpResponse("Funcionalidade de exportar PDF direto da sessão será implementada em uma versão futura. Salve sua simulação para exportá-la.")
