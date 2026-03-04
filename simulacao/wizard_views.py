# simulacao/wizard_views.py
"""
Views para o sistema Wizard (multi-step form)
Gerencia o fluxo guiado tipo Windows Setup
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from . import utils
from . import formatacao
from .wizard_forms import (
    WizardPrivacyForm,
    WizardPerfilForm,
    WizardImovelForm,
    WizardMetodosForm,
    WizardFinanciamentoForm,
    WizardConsorcioForm,
    WizardInvestimentoForm,
    WizardAluguelForm,
)
from . import utils
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .wizard_questions import WIZARD_QUESTIONS, map_answers_to_dados_form
from .calculadora_financeira import comparar_cenarios_e_formatar


# Constantes para controle do wizard
WIZARD_STEPS = {
    1: {'form': WizardPrivacyForm, 'name': 'privacy', 'title': 'Privacidade & Preferências'},
    2: {'form': WizardPerfilForm, 'name': 'perfil', 'title': 'Perfil do Usuário'},
    3: {'form': WizardImovelForm, 'name': 'imovel', 'title': 'Dados do Imóvel'},
    4: {'form': WizardMetodosForm, 'name': 'metodos', 'title': 'Métodos de Interesse'},
    5: {'form': WizardFinanciamentoForm, 'name': 'financiamento', 'title': 'Parâmetros do Financiamento'},
    6: {'form': WizardConsorcioForm, 'name': 'consorcio', 'title': 'Parâmetros do Consórcio'},
    7: {'form': WizardInvestimentoForm, 'name': 'investimento', 'title': 'Parâmetros de Investimento'},
    8: {'form': WizardAluguelForm, 'name': 'aluguel', 'title': 'Parâmetros de Aluguel'},
}

TOTAL_STEPS = len(WIZARD_STEPS)


def _convert_decimal_to_float(data):
    """
    Converte objetos Decimal para float para serialização JSON na sessão
    """
    from decimal import Decimal
    
    if isinstance(data, dict):
        return {key: _convert_decimal_to_float(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_convert_decimal_to_float(item) for item in data]
    elif isinstance(data, Decimal):
        return float(data)
    else:
        return data


def wizard_view(request, step=None):
    """
    View principal do wizard que gerencia todas as etapas
    Usa sessão do Django para armazenar dados entre etapas
    """
    
    # Inicializa a sessão do wizard se necessário
    if 'wizard_data' not in request.session:
        request.session['wizard_data'] = {}
        request.session['wizard_current_step'] = 1
    
    # Determina o passo atual
    if step:
        try:
            current_step = int(step)
            if current_step < 1 or current_step > TOTAL_STEPS:
                current_step = request.session.get('wizard_current_step', 1)
        except ValueError:
            current_step = request.session.get('wizard_current_step', 1)
    else:
        current_step = request.session.get('wizard_current_step', 1)
    
    wizard_data = request.session.get('wizard_data', {})
    step_info = WIZARD_STEPS[current_step]
    form_class = step_info['form']
    
    # Processa o formulário
    if request.method == 'POST':
        form = form_class(request.POST)
        
        if form.is_valid():
            # Salva os dados do formulário na sessão
            # Converte Decimal para float para serialização JSON
            cleaned_data = form.cleaned_data
            cleaned_data_serializable = _convert_decimal_to_float(cleaned_data)
            wizard_data[step_info['name']] = cleaned_data_serializable
            request.session['wizard_data'] = wizard_data
            
            # Salvar o valor do campo 'recebe_fgts_regular' na sessão
            if 'recebe_fgts_regular' in cleaned_data:
                wizard_data['recebe_fgts_regular'] = cleaned_data['recebe_fgts_regular']
            
            # Verifica se deve pular etapas baseado nas escolhas
            next_step = _get_next_step(current_step, wizard_data)
            request.session['wizard_current_step'] = next_step
            
            # Se não há próximo passo, redireciona para resultados
            if next_step > TOTAL_STEPS:
                request.session['wizard_current_step'] = TOTAL_STEPS  # Ajusta para não causar erro
                return redirect('wizard_resultados')
            
            # Redireciona para o próximo passo
            return redirect('wizard_step', step=next_step)
        
        else:
            # Form inválido, mostra erros
            messages.error(request, "Por favor, corrija os erros abaixo.")
    
    else:
        # GET: Preenche o form com dados da sessão se existirem
        initial_data = wizard_data.get(step_info['name'], {})
        form = form_class(initial=initial_data)
    
    # Calcula progresso
    progress = int((current_step / TOTAL_STEPS) * 100)
    
    # Prepara contexto
    context = {
        'form': form,
        'current_step': current_step,
        'total_steps': TOTAL_STEPS,
        'step_title': step_info['title'],
        'progress': progress,
        'wizard_data': wizard_data,
        'can_go_back': current_step > 1,
        'is_last_step': current_step == TOTAL_STEPS,
    }
    
    return render(request, 'simulacao/wizard_step.html', context)


def wizard_back(request, step):
    """
    Volta para o passo anterior do wizard
    """
    try:
        current_step = int(step)
        if current_step > 1:
            previous_step = current_step - 1
            request.session['wizard_current_step'] = previous_step
            return redirect('wizard_step', step=previous_step)
    except ValueError:
        pass
    
    return redirect('wizard_step', step=1)


def wizard_reset(request):
    """
    Reseta o wizard, limpando a sessão
    """
    if 'wizard_data' in request.session:
        del request.session['wizard_data']
    if 'wizard_current_step' in request.session:
        del request.session['wizard_current_step']
    
    messages.info(request, "Wizard reiniciado. Comece novamente.")
    return redirect('wizard_step', step=1)


def wizard_resultados(request):
    """
    Página final que exibe os resultados comparativos
    Processa todos os dados coletados no wizard e gera comparação
    """
    wizard_data = request.session.get('wizard_data', {})
    
    # Se não há dados, redireciona para o início
    if not wizard_data:
        messages.warning(request, "Nenhum dado encontrado. Comece uma nova simulação.")
        return redirect('wizard_step', step=1)
    
    # Verifica quais métodos foram selecionados
    metodos_data = wizard_data.get('metodos', {})
    comparar_price = metodos_data.get('comparar_price', False)
    comparar_sac = metodos_data.get('comparar_sac', False)
    comparar_consorcio = metodos_data.get('comparar_consorcio', False)
    comparar_guardar_dinheiro = metodos_data.get('comparar_guardar_dinheiro', False)
    comparar_aluguel = metodos_data.get('comparar_aluguel_investimento', False)
    
    # Prepara dados para a função de comparação
    imovel_data = wizard_data.get('imovel', {})
    financiamento_data = wizard_data.get('financiamento', {})
    consorcio_data = wizard_data.get('consorcio', {})
    investimento_data = wizard_data.get('investimento', {})
    aluguel_data = wizard_data.get('aluguel', {})
    
    # Constrói dicionário de dados no formato esperado
    dados_comparacao = {}
    
    # Dados básicos do imóvel
    dados_comparacao['valor_imovel'] = float(imovel_data.get('valor_imovel', 0))
    dados_comparacao['entrada'] = float(imovel_data.get('entrada', 0))
    dados_comparacao['fgts_saldo'] = float(imovel_data.get('fgts_saldo', 0))
    dados_comparacao['renda_familiar_bruta'] = float(imovel_data.get('renda_familiar_bruta', 8000.0))
    dados_comparacao['valor_despesas'] = 0  # Pode adicionar depois
    dados_comparacao['incorporar_despesas'] = False
    
    # Dados de financiamento
    if comparar_price or comparar_sac:
        dados_comparacao['taxa_anual'] = float(financiamento_data.get('taxa_anual', 7.9))
        dados_comparacao['prazo_anos'] = int(financiamento_data.get('prazo_anos', 30))
        dados_comparacao['seguro_mensal'] = float(financiamento_data.get('seguro_mensal', 0.03))
        dados_comparacao['taxa_admin_mensal'] = 0
        dados_comparacao['usar_fgts_financiamento'] = financiamento_data.get('usar_fgts_financiamento', False)
        dados_comparacao['tipo_amortizacao_fgts'] = financiamento_data.get('tipo_amortizacao_fgts', 'reduzir_prazo')
        dados_comparacao['mes_uso_fgts_financiamento'] = int(financiamento_data.get('mes_uso_fgts', 1))
    else:
        dados_comparacao['taxa_anual'] = 7.9
        dados_comparacao['prazo_anos'] = 30
        dados_comparacao['seguro_mensal'] = 0.03
        dados_comparacao['taxa_admin_mensal'] = 0
        dados_comparacao['usar_fgts_financiamento'] = False
        dados_comparacao['tipo_amortizacao_fgts'] = 'reduzir_prazo'
        dados_comparacao['mes_uso_fgts_financiamento'] = 1
    
    # Dados de consórcio
    if comparar_consorcio:
        dados_comparacao['taxa_adm'] = float(consorcio_data.get('taxa_adm_anual', 1.2))
        dados_comparacao['fundo_reserva'] = float(consorcio_data.get('fundo_reserva', 0.5))
        dados_comparacao['prazo_anos_consorcio'] = int(consorcio_data.get('prazo_anos_consorcio', 15))
        # Ajusta prazo para consórcio se diferente
        if not comparar_price and not comparar_sac:
            dados_comparacao['prazo_anos'] = dados_comparacao['prazo_anos_consorcio']
    else:
        dados_comparacao['taxa_adm'] = 1.2
        dados_comparacao['fundo_reserva'] = 0.5
    
    # Dados de investimento (guardar dinheiro)
    if comparar_guardar_dinheiro or comparar_aluguel:
        dados_comparacao['taxa_investimento'] = float(investimento_data.get('taxa_rendimento_anual', 10.0))
        dados_comparacao['aporte_mensal'] = float(investimento_data.get('aporte_mensal', 0))
        dados_comparacao['aporte_13'] = float(investimento_data.get('aporte_13', 0))
        dados_comparacao['recursos_proprios_iniciais'] = dados_comparacao['entrada']
    else:
        dados_comparacao['taxa_investimento'] = 10.0
        dados_comparacao['aporte_mensal'] = 0
        dados_comparacao['aporte_13'] = 0
        dados_comparacao['recursos_proprios_iniciais'] = dados_comparacao['entrada']
    
    # Dados de aluguel + investimento
    if comparar_aluguel:
        dados_comparacao['aluguel_inicial'] = float(aluguel_data.get('aluguel_inicial', 1500))
        dados_comparacao['taxa_inflacao'] = float(aluguel_data.get('taxa_inflacao_anual', 4.5))
        dados_comparacao['valorizacao_imovel'] = float(aluguel_data.get('valorizacao_imovel_anual', 5.0))
        dados_comparacao['opcao_pagamento_aluguel'] = 'renda'
        # renda_familiar_bruta já foi capturada dos dados do imóvel
        dados_comparacao['fgts_mensal_percent'] = 8.0  # 8% padrão
        dados_comparacao['rendimento_fgts'] = 3.0  # Taxa FGTS padrão
    else:
        dados_comparacao['aluguel_inicial'] = 1500
        dados_comparacao['taxa_inflacao'] = 4.5
        dados_comparacao['valorizacao_imovel'] = 5.0
        dados_comparacao['opcao_pagamento_aluguel'] = 'renda'
        # Mantém renda_familiar_bruta do imóvel
        dados_comparacao['fgts_mensal_percent'] = 8.0
        dados_comparacao['rendimento_fgts'] = 3.0
    
    # Chama a função de comparação (precisa ser adaptada)
    # Por enquanto, vamos criar uma versão simplificada
    resultados = _gerar_comparacao_simplificada(dados_comparacao, {
        'price': comparar_price,
        'sac': comparar_sac,
        'consorcio': comparar_consorcio,
        'guardar_dinheiro': comparar_guardar_dinheiro,
        'aluguel': comparar_aluguel,
    })
    
    context = {
        'wizard_data': wizard_data,
        'resultados': resultados,
        'perfil': wizard_data.get('perfil', {}).get('perfil', 'comprador'),
    }
    
    return render(request, 'simulacao/wizard_resultados.html', context)


def wizard_dynamic_view(request):
    """Serve a página do wizard dinâmico (client-driven)."""
    return render(request, 'simulacao/wizard_dynamic.html', {'titulo': 'Wizard Dinâmico'})


def wizard_api_questions(request):
    """Retorna o JSON com as perguntas do wizard (WIZARD_QUESTIONS)."""
    return JsonResponse({'questions': WIZARD_QUESTIONS})


@csrf_exempt
def wizard_api_submit(request):
    """Recebe respostas JSON do wizard dinâmico, mapeia para dados de formulário e
    retorna o resultado de `comparar_cenarios_e_formatar` em JSON.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception as e:
        return JsonResponse({'error': 'invalid json', 'detail': str(e)}, status=400)

    # payload expected to be a dict of answers keyed by wizard keys
    dados_form = map_answers_to_dados_form(payload)

    # comparar_cenarios_e_formatar expects a dict similar to request.POST-like values
    resumo = comparar_cenarios_e_formatar(dados_form)

    return JsonResponse({'resumo': resumo})


def api_cidades(request):
    """
    API para retornar uma lista de cidades com base no texto digitado.
    """
    if request.method == 'GET':
        query = request.GET.get('q', '').lower()
        cidades = [
            'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba', 'Porto Alegre',
            'Salvador', 'Fortaleza', 'Brasília', 'Recife', 'Manaus', 'Santos'
        ]
        resultados = [cidade for cidade in cidades if query in cidade.lower()]
        return JsonResponse({'results': resultados})
    return JsonResponse({'results': []})


def _get_next_step(current_step, wizard_data):
    """Determina o próximo passo do wizard baseado nas escolhas do usuário.

    Usa `step` por nome em vez de números fixos para ser mais resiliente
    a inserções ou remoções de etapas.
    """
    step_info = WIZARD_STEPS.get(current_step, {})
    step_name = step_info.get('name')

    # Após a etapa de seleção de métodos, pule etapas não solicitadas
    if step_name == 'metodos':
        metodos = wizard_data.get('metodos', {})
        next_step = current_step + 1

        # Se não selecionou financiamento (nem Price nem SAC), pula financiamento
        if not metodos.get('comparar_price') and not metodos.get('comparar_sac'):
            # financiamento está logo após 'metodos' no fluxo atual
            next_step += 1

        if next_step > TOTAL_STEPS:
            return TOTAL_STEPS + 1
        return next_step

    # Avança normalmente, mas pule etapas não selecionadas
    next_step = current_step + 1

    # Recupera nomes das etapas futuras para decisão
    while next_step <= TOTAL_STEPS:
        next_name = WIZARD_STEPS[next_step]['name']

        # Se a etapa for 'financiamento' e o usuário não selecionou price nem sac, pule
        if next_name == 'financiamento':
            metodos = wizard_data.get('metodos', {})
            if not metodos.get('comparar_price') and not metodos.get('comparar_sac'):
                next_step += 1
                continue

        # Se a etapa for 'consorcio' e não selecionou consórcio, pule
        if next_name == 'consorcio':
            metodos = wizard_data.get('metodos', {})
            if not metodos.get('comparar_consorcio'):
                next_step += 1
                continue

        # Se a etapa for 'investimento' e não selecionou guardar_dinheiro, pule
        if next_name == 'investimento':
            metodos = wizard_data.get('metodos', {})
            if not metodos.get('comparar_guardar_dinheiro'):
                next_step += 1
                continue

        # Se a etapa for 'aluguel' e o usuário não paga aluguel, pule
        if next_name == 'aluguel':
            imovel = wizard_data.get('imovel', {})
            paga_aluguel = imovel.get('paga_aluguel', True)
            if not paga_aluguel and not wizard_data.get('metodos', {}).get('comparar_aluguel_investimento'):
                next_step += 1
                continue

        # Se chegou aqui, a etapa deve ser exibida
        return next_step

    return TOTAL_STEPS + 1


def _calcular_comparacao_amortizacao(metodo, valor_principal, taxa_anual, prazo_meses, seguro_mensal, dados):
    """
    Calcula comparação antes/depois da amortização com FGTS.
    Retorna dicionário com cenário sem amortização, com amortização e economia.
    """
    from decimal import Decimal
    
    # Cenário SEM amortização (original)
    resultado_sem = utils.simular_financiamento_geral(
        metodo=metodo,
        valor_principal=float(valor_principal),
        taxa_anual=dados['taxa_anual'],
        prazo_meses=prazo_meses,
        seguro_mensal=seguro_mensal,
        usar_fgts_financiamento=False,
    )
    
    # Cenário COM amortização
    usar_fgts = dados.get('usar_fgts_financiamento', False)
    resultado_com = utils.simular_financiamento_geral(
        metodo=metodo,
        valor_principal=float(valor_principal),
        taxa_anual=dados['taxa_anual'],
        prazo_meses=prazo_meses,
        seguro_mensal=seguro_mensal,
        fgts_saldo=dados.get('fgts_saldo', 0),
        usar_fgts_financiamento=usar_fgts,
        tipo_amortizacao_fgts=dados.get('tipo_amortizacao_fgts', 'reduzir_prazo'),
        mes_uso_fgts_financiamento=dados.get('mes_uso_fgts_financiamento', 1),
    )
    
    if not resultado_sem or not resultado_com or not resultado_sem.get('tabela') or not resultado_com.get('tabela'):
        return None
    
    # Calcula totais
    principal_dec = Decimal(str(valor_principal))
    total_sem = principal_dec + Decimal(str(resultado_sem['total_juros'])) + Decimal(str(resultado_sem.get('total_seguros_taxas', 0)))
    total_com = principal_dec + Decimal(str(resultado_com['total_juros'])) + Decimal(str(resultado_com.get('total_seguros_taxas', 0)))
    
    economia = total_sem - total_com
    economia_percent = (economia / total_sem * 100) if total_sem > 0 else Decimal(0)
    meses_economizados = resultado_sem.get('prazo_final_meses', prazo_meses) - resultado_com.get('prazo_final_meses', prazo_meses)
    
    return {
        'sem_amortizacao': {
            'total_pago': float(total_sem),
            'total_juros': resultado_sem['total_juros'],
            'prazo_meses': resultado_sem.get('prazo_final_meses', prazo_meses),
            'parcela_inicial': resultado_sem['parcela_inicial'],
        },
        'com_amortizacao': {
            'total_pago': float(total_com),
            'total_juros': resultado_com['total_juros'],
            'prazo_meses': resultado_com.get('prazo_final_meses', prazo_meses),
            'parcela_inicial': resultado_com['parcela_inicial'],
        },
        'economia': {
            'valor': float(economia),
            'percentual': float(economia_percent),
            'meses': meses_economizados,
        },
        'usou_amortizacao': usar_fgts,
    }


def _gerar_comparacao_simplificada(dados, metodos_selecionados):
    """
    Gera comparação simplificada dos métodos selecionados
    TODO: Integrar com a função comparar_cenarios_e_formatar do utils.py
    """
    from decimal import Decimal
    
    resultados = []
    prazo_meses = dados['prazo_anos'] * 12
    valor_principal = Decimal(str(dados['valor_imovel'])) - Decimal(str(dados['entrada']))
    
    # PRICE
    if metodos_selecionados['price']:
        resultado = utils.simular_financiamento_geral(
            metodo='price',
            valor_principal=float(valor_principal),
            taxa_anual=dados['taxa_anual'],
            prazo_meses=prazo_meses,
            seguro_mensal=dados['seguro_mensal'],
            taxa_admin_mensal=dados.get('taxa_admin_mensal', 0),
            fgts_saldo=dados['fgts_saldo'],
            usar_fgts_financiamento=dados.get('usar_fgts_financiamento', False),
            tipo_amortizacao_fgts=dados.get('tipo_amortizacao_fgts', 'reduzir_prazo'),
            mes_uso_fgts_financiamento=dados.get('mes_uso_fgts_financiamento', 1),
        )
        if resultado and resultado.get('tabela'):
            total_pago = valor_principal + Decimal(str(resultado['total_juros'])) + Decimal(str(resultado.get('total_seguros_taxas', 0)))
            
            # Calcula comparação antes/depois da amortização
            comparacao = _calcular_comparacao_amortizacao('price', valor_principal, dados['taxa_anual'], prazo_meses, dados['seguro_mensal'], dados)
            
            resultado_dict = {
                'metodo': 'Tabela Price',
                'parcela_inicial': formatacao.formatar_moeda_brl(resultado['parcela_inicial']),
                'total_juros': formatacao.formatar_moeda_brl(resultado['total_juros']),
                'total_pago': formatacao.formatar_moeda_brl(float(total_pago)),
                'prazo_final': formatacao.formatar_meses_anos(resultado.get('prazo_final_meses', prazo_meses)),
                'prazo_final_meses': resultado.get('prazo_final_meses', prazo_meses),
            }
            
            if comparacao and comparacao['usou_amortizacao']:
                resultado_dict['comparacao'] = {
                    'sem_amortizacao': {
                        'total_pago': formatacao.formatar_moeda_brl(comparacao['sem_amortizacao']['total_pago']),
                        'prazo': formatacao.formatar_meses_anos(comparacao['sem_amortizacao']['prazo_meses']),
                    },
                    'com_amortizacao': {
                        'total_pago': formatacao.formatar_moeda_brl(comparacao['com_amortizacao']['total_pago']),
                        'prazo': formatacao.formatar_meses_anos(comparacao['com_amortizacao']['prazo_meses']),
                    },
                    'economia': {
                        'valor': formatacao.formatar_moeda_brl(comparacao['economia']['valor']),
                        'percentual': formatacao.formatar_percentual(comparacao['economia']['percentual'], 1),
                        'meses': comparacao['economia']['meses'],
                    },
                }
            
            resultados.append(resultado_dict)
    
    # SAC
    if metodos_selecionados['sac']:
        resultado = utils.simular_financiamento_geral(
            metodo='sac',
            valor_principal=float(valor_principal),
            taxa_anual=dados['taxa_anual'],
            prazo_meses=prazo_meses,
            seguro_mensal=dados['seguro_mensal'],
            taxa_admin_mensal=dados.get('taxa_admin_mensal', 0),
            fgts_saldo=dados['fgts_saldo'],
            usar_fgts_financiamento=dados.get('usar_fgts_financiamento', False),
            tipo_amortizacao_fgts=dados.get('tipo_amortizacao_fgts', 'reduzir_prazo'),
            mes_uso_fgts_financiamento=dados.get('mes_uso_fgts_financiamento', 1),
        )
        if resultado and resultado.get('tabela'):
            total_pago = valor_principal + Decimal(str(resultado['total_juros'])) + Decimal(str(resultado.get('total_seguros_taxas', 0)))
            
            # Calcula comparação antes/depois da amortização
            comparacao = _calcular_comparacao_amortizacao('sac', valor_principal, dados['taxa_anual'], prazo_meses, dados['seguro_mensal'], dados)
            
            resultado_dict = {
                'metodo': 'Tabela SAC',
                'parcela_inicial': formatacao.formatar_moeda_brl(resultado['parcela_inicial']),
                'total_juros': formatacao.formatar_moeda_brl(resultado['total_juros']),
                'total_pago': formatacao.formatar_moeda_brl(float(total_pago)),
                'prazo_final': formatacao.formatar_meses_anos(resultado.get('prazo_final_meses', prazo_meses)),
                'prazo_final_meses': resultado.get('prazo_final_meses', prazo_meses),
            }
            
            if comparacao and comparacao['usou_amortizacao']:
                resultado_dict['comparacao'] = {
                    'sem_amortizacao': {
                        'total_pago': formatacao.formatar_moeda_brl(comparacao['sem_amortizacao']['total_pago']),
                        'prazo': formatacao.formatar_meses_anos(comparacao['sem_amortizacao']['prazo_meses']),
                    },
                    'com_amortizacao': {
                        'total_pago': formatacao.formatar_moeda_brl(comparacao['com_amortizacao']['total_pago']),
                        'prazo': formatacao.formatar_meses_anos(comparacao['com_amortizacao']['prazo_meses']),
                    },
                    'economia': {
                        'valor': formatacao.formatar_moeda_brl(comparacao['economia']['valor']),
                        'percentual': formatacao.formatar_percentual(comparacao['economia']['percentual'], 1),
                        'meses': comparacao['economia']['meses'],
                    },
                }
            
            resultados.append(resultado_dict)
    
    # Consórcio
    if metodos_selecionados['consorcio']:
        prazo_consorcio = dados.get('prazo_anos_consorcio', dados['prazo_anos']) * 12
        resultado = utils.simular_consorcio(
            valor_imovel=Decimal(str(dados['valor_imovel'])),
            prazo_meses=prazo_consorcio,
            taxa_adm=dados['taxa_adm'],
            fundo_reserva=dados['fundo_reserva'],
            fgts_saldo=dados['fgts_saldo'],
        )
        if resultado:
            total_pago_cons = Decimal(str(dados['valor_imovel'])) + Decimal(str(resultado['total_custo']))
            
            # Detalhamento dos custos do consórcio
            detalhes_consorcio = [
                f'Parcela Base (0.7%): {formatacao.formatar_moeda_brl(resultado.get("parcela_base", 0))}',
                f'Taxa de Administração: {formatacao.formatar_moeda_brl(resultado.get("taxa_adm_mensal", 0))}/mês ({dados["taxa_adm"]:.2f}% a.a.)',
                f'Fundo de Reserva: {formatacao.formatar_moeda_brl(resultado.get("fundo_reserva_mensal", 0))}/mês ({dados["fundo_reserva"]:.2f}%)',
                f'Contemplação Estimada: Mês {resultado.get("mes_contemplacao_estimado", "N/A")}',
            ]
            
            resultados.append({
                'metodo': 'Consórcio',
                'parcela_inicial': formatacao.formatar_moeda_brl(resultado['parcela_fixa']),
                'total_custo': formatacao.formatar_moeda_brl(resultado['total_custo']),
                'total_pago': formatacao.formatar_moeda_brl(float(total_pago_cons)),
                'prazo_final': formatacao.formatar_meses_anos(prazo_consorcio),
                'prazo_final_meses': prazo_consorcio,
                'detalhes_consorcio': detalhes_consorcio,
            })
    
    # Guardar Dinheiro (Poupança)
    if metodos_selecionados.get('guardar_dinheiro', False):
        valor_mensal_guardar = dados.get('valor_mensal_guardar', 1000.0)
        taxa_rendimento_poupanca = dados.get('taxa_rendimento_poupanca', 6.0)  # 6% a.a. padrão (0.5% a.m.)
        valor_aluguel = dados.get('aluguel_inicial', 0.0)
        taxa_inflacao = dados.get('taxa_inflacao', 6.0)  # 6% a.a.
        
        resultado = utils.guardar_dinheiro(
            valor_imovel=float(dados['valor_imovel']),
            valor_entrada_inicial=float(dados['entrada']),
            valor_mensal_guardar=valor_mensal_guardar,
            valor_aluguel=valor_aluguel,
            taxa_rendimento_mensal=taxa_rendimento_poupanca / 100 / 12,
            prazo_meses=prazo_meses,
            taxa_reajuste_aluguel_anual=taxa_inflacao / 100,
            fgts_saldo_inicial=dados.get('fgts_saldo', 0.0),
            renda_familiar_bruta=dados.get('renda_familiar_bruta', 0.0),
            fgts_mensal_percent=8.0
        )
        
        if resultado:
            if resultado['viavel']:
                tempo_compra = f"{resultado['tempo_para_comprar_anos']} anos e {resultado['tempo_para_comprar_meses']} meses"
                status_message = f"✅ Viável! Você conseguiria juntar para comprar em {tempo_compra}"
            else:
                tempo_compra = f"Mais de {dados['prazo_anos']} anos"
                status_message = f"⚠️ Difícil alcançar a meta no prazo de {dados['prazo_anos']} anos"
            
            detalhes_guardar = [
                f'Poupança mensal: {formatacao.formatar_moeda_brl(valor_mensal_guardar)}',
                f'Rendimento: {taxa_rendimento_poupanca:.2f}% a.a.',
                f'Tempo para juntar entrada: {tempo_compra}',
                f'Total gasto com aluguel: {formatacao.formatar_moeda_brl(resultado["total_aluguel_pago"])}',
                f'Capital final acumulado: {formatacao.formatar_moeda_brl(resultado["capital_final"])}',
                f'  - Poupança: {formatacao.formatar_moeda_brl(resultado["poupanca_final"])}',
                f'  - FGTS: {formatacao.formatar_moeda_brl(resultado["fgts_final"])}',
            ]
            
            resultados.append({
                'metodo': 'Guardar Dinheiro',
                'parcela_inicial': formatacao.formatar_moeda_brl(valor_mensal_guardar),
                'total_custo': formatacao.formatar_moeda_brl(resultado['total_aluguel_pago']),
                'total_pago': formatacao.formatar_moeda_brl(resultado['total_aluguel_pago'] + resultado['custo_cartorio_registro']),
                'prazo_final': tempo_compra,
                'prazo_final_meses': resultado.get('meses_para_comprar', prazo_meses),
                'status_viabilidade': status_message,
                'detalhes_guardar': detalhes_guardar,
                'capital_final': formatacao.formatar_moeda_brl(resultado['capital_final']),
            })
    
    return resultados
