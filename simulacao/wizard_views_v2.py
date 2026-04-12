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
from .calculadora_financeira import calcular_mcmv, calcular_price_sac, TAXA_JUROS_PADRAO
from .formatacao import formatar_moeda_brl
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import WizardSimulationSerializer


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
    Calcula e exibe resultados com recomendação inteligente (WEB)
    """
    wizard_data = request.session.get('wizard_v2_data', {})
    if not wizard_data:
        return redirect('wizard_v2')
    
    context = _get_wizard_calculation_data(wizard_data)
    return render(request, 'simulacao/wizard_v2_resultados.html', context)


class APICalculateWizardView(APIView):
    """
    API para calcular os resultados do Wizard de uma vez (MOBILE/API).
    """
    permission_classes = []
    
    def post(self, request):
        serializer = WizardSimulationSerializer(data=request.data)
        if serializer.is_valid():
            wizard_data = serializer.validated_data
            wizard_data_cleaned = _convert_decimals_to_floats(wizard_data)
            results = _get_wizard_calculation_data(wizard_data_cleaned)
            return Response(results, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def _get_wizard_calculation_data(wizard_data):
    """
    Lógica centralizada de cálculo do Wizard.
    """
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
    idade = int(perfil_obj.get('idade_comprador', 30))
    
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
    if margem_info:
        margem_info['margem_disponivel'] = float(renda_bruta * Decimal('0.30'))
        margem_info['margem_disponivel_fmt'] = formatar_moeda_brl(margem_info['margem_disponivel'])
        margem_info['margem_30_porcento'] = margem_info['parcela_maxima']
        margem_info['desconto_aplicado'] = margem_info['desconto_aplicado_outras_rendas']
    
    # Calcula FGTS futuro
    tipo_contrato = trabalho.get('tipo_contrato', '')
    fgts_futuro = None
    if tipo_contrato == 'clt' and renda_bruta > 0:
        fgts_futuro = calcular_acumulo_fgts(
            salario_bruto=float(renda_bruta),
            meses_ate_compra=prazo_meses
        )
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
        cenario_80 = calcular_cenario_80_porcento(
            valor_imovel=float(valor_imovel),
            capital_disponivel=float(capital_total),
            aluguel_mensal=float(aluguel_atual),
            taxa_juros_financiamento=float(TAXA_JUROS_PADRAO),
            taxa_investimento=float(cenarios.get('taxa_investimento_esperada', 9.5)),
            prazo_anos=5
        )
    
    # Calcula cenários
    resultados = {}
    
    if cenarios.get('comparar_financiamento_price'):
        resultados['price'] = _calcular_financiamento('price', principal, TAXA_JUROS_PADRAO, prazo_meses, renda_bruta, fgts_saldo, cenarios.get('usar_fgts', True), aluguel_atual, idade)
    
    if cenarios.get('comparar_financiamento_sac'):
        resultados['sac'] = _calcular_financiamento('sac', principal, TAXA_JUROS_PADRAO, prazo_meses, renda_bruta, fgts_saldo, cenarios.get('usar_fgts', True), aluguel_atual, idade)
    
    if cenarios.get('comparar_consorcio'):
        resultados['consorcio'] = _calcular_consorcio_detalhado(valor_imovel, int(cenarios.get('prazo_consorcio', 180)), cenarios.get('estrategia_contemplacao', 'sorteio'), Decimal(str(cenarios.get('valor_lance_disponivel', 0))), int(cenarios.get('tempo_maximo_espera_consorcio', 36)), aluguel_atual, capital_guardado)
    
    if cenarios.get('comparar_guardar_dinheiro'):
        despesas_fixas = Decimal(str(financas.get('despesas_mensais_fixas', 0)))
        renda_disponivel = renda_bruta - aluguel_atual - despesas_fixas
        valor_referencia = renda_disponivel
        parcelas_simuladas = []
        if 'price' in resultados: parcelas_simuladas.append(Decimal(str(resultados['price'].get('parcela_inicial', 0))))
        if 'sac' in resultados: parcelas_simuladas.append(Decimal(str(resultados['sac'].get('parcela_inicial', 0))))
        if parcelas_simuladas: valor_referencia = min((p for p in parcelas_simuladas if p > 0), default=0)
        
        resultado_guardar = _calcular_guardar_dinheiro(capital_guardado, valor_imovel, Decimal(str(cenarios.get('taxa_investimento_esperada', 9.5))), max(valor_referencia, Decimal('100')), aluguel_atual)
        if resultado_guardar: resultados['guardar_dinheiro'] = resultado_guardar
 
    if cenarios.get('comparar_mcmv'):
        resultado_mcmv = calcular_mcmv(valor_imovel, renda_bruta, capital_guardado, prazo_meses, cenarios.get('usar_fgts', True), fgts_saldo)
        if resultado_mcmv['qualificado']:
            resultado_mcmv['metodo'] = f"MCMV - Faixa {resultado_mcmv['faixa']}"
            resultado_mcmv['total_desembolso'] = resultado_mcmv['custo_total'] + float(capital_guardado)
            resultado_mcmv['patrimonio_final'] = float(valor_imovel)
            resultados['mcmv'] = resultado_mcmv

    if cenarios.get('comparar_aluguel_investimento'):
        resultados['aluguel_investimento'] = _v2_calcular_aluguel_investimento(aluguel_atual, capital_guardado, renda_bruta, Decimal(str(cenarios.get('taxa_investimento_esperada', 9.5))), prazo_anos, valor_imovel)

    if cenarios.get('comparar_compra_a_vista') and capital_guardado >= valor_imovel:
        res_vista = _v2_calcular_compra_a_vista(valor_imovel, capital_guardado, Decimal(str(cenarios.get('taxa_investimento_esperada', 9.5))), prazo_anos)
        if res_vista: resultados['compra_a_vista'] = res_vista
    
    analise = analisar_perfil_e_recomendar(wizard_data, resultados)
    resultados_ordenados = dict(sorted(resultados.items(), key=lambda item: item[1].get('total_custo', 0), reverse=True))
    
    # Formatação (opcional para API mas bom para manter compatibilidade)
    resultados_formatados = {}
    keys_monetarias = ['parcela_inicial', 'total_custo', 'total_desembolso', 'patrimonio_final', 'total_juros', 'total_principal', 'aluguel_durante', 'total_aluguel_gasto', 'montante_final_investimento', 'ganho_com_investimento', 'sobra_apos_compra', 'patrimonio_final_total', 'valor_lance', 'taxa_administracao', 'fundo_reserva']
    for key, data in resultados_ordenados.items():
        data_fmt = data.copy()
        for k, v in data.items():
            if k in keys_monetarias and isinstance(v, (int, float, Decimal)):
                data_fmt[k] = formatar_moeda_brl(v)
        resultados_formatados[key] = data_fmt

    return {
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


def _v2_calcular_aluguel_investimento(aluguel_mensal, capital_inicial, renda_bruta, taxa_investimento, prazo_anos, valor_imovel_futuro):
    prazo_meses = prazo_anos * 12
    # Taxa de Administração (Default 9.3% - QuintoAndar)
    TAXA_ADM = Decimal('0.093')
    
    custo_aluguel_total = aluguel_mensal * Decimal(prazo_meses)
    renda_disponivel = renda_bruta - (aluguel_mensal + Decimal('2000'))
    aporte_mensal = max(renda_disponivel * Decimal('0.1'), Decimal('0'))
    taxa_mensal = (taxa_investimento / 100) / 12
    montante_investido = capital_inicial
    for _ in range(prazo_meses):
        # Investimento rende + Aporte - (Aluguel já deduzido de taxa de admin se pago pelo investidor)
        # Para simplificar na visão de rendimento: o investidor recebe (Aluguel * 0.907)
        # Mas aqui é a visão de quem PAGA aluguel vs investe. 
        # No cenário "Aluguel+Investimento", o usuário PAGA o aluguel cheio.
        # A taxa de 9.3% é relevante para o proprietário (Investidor Imobiliário).
        montante_investido = montante_investido * (1 + taxa_mensal) + aporte_mensal

    
    ganho_investimento = montante_investido - capital_inicial - (aporte_mensal * Decimal(prazo_meses))
    pode_comprar = montante_investido >= valor_imovel_futuro
    comprometimento = (aluguel_mensal / renda_bruta) * 100 if renda_bruta > 0 else Decimal('0')

    return {
        'metodo': 'Aluguel + Investimento',
        'parcela_inicial': float(aluguel_mensal),
        'total_aluguel_gasto': float(custo_aluguel_total),
        'montante_final_investimento': float(montante_investido),
        'ganho_com_investimento': float(ganho_investimento),
        'patrimonio_final': float(montante_investido),
        'prazo_final_anos': float(prazo_anos),
        'total_custo': float(custo_aluguel_total),
        'total_desembolso': float(custo_aluguel_total),
        'resumo_explicativo': f'💸 Continue alugando e invista a diferença. Ideal se você busca flexibilidade.'
    }


def _v2_calcular_compra_a_vista(valor_imovel, capital_disponivel, taxa_investimento, prazo_anos):
    prazo_meses = prazo_anos * 12
    sobra = capital_disponivel - valor_imovel
    if sobra <= 0: return None
    taxa_mensal = (taxa_investimento / 100) / 12
    montante_investido = sobra
    for _ in range(prazo_meses):
        montante_investido = montante_investido * (1 + taxa_mensal)
    return {
        'metodo': 'Compra à Vista + Investimento',
        'patrimonio_final': float(valor_imovel + montante_investido),
        'total_custo': float(valor_imovel),
        'total_desembolso': float(valor_imovel),
        'resumo_explicativo': '🎉 Parabéns! Comprar à vista elimina dívidas e juros.'
    }


def _calcular_guardar_dinheiro(capital_inicial, valor_imovel_alvo, taxa_retorno_anual, renda_disponivel_mensal, aluguel_mensal, fgts_saldo=0):
    taxa_mensal = (Decimal('1') + taxa_retorno_anual / Decimal('100')) ** (Decimal('1') / Decimal('12')) - Decimal('1')
    montante = capital_inicial + Decimal(str(fgts_saldo))
    meses = 0
    total_aportes = Decimal('0')
    total_aluguel = Decimal('0')
    while montante < valor_imovel_alvo and meses < 360:
        meses += 1
        montante = montante * (1 + taxa_mensal) + renda_disponivel_mensal
        total_aportes += renda_disponivel_mensal
        total_aluguel += aluguel_mensal
    
    if montante >= valor_imovel_alvo:
        return {
            'metodo': 'Guardar Dinheiro',
            'parcela_inicial': float(renda_disponivel_mensal),
            'meses_necessarios': meses,
            'prazo_final_anos': round(meses / 12, 1),
            'total_custo': float(capital_inicial + total_aportes),
            'total_desembolso': float(capital_inicial + total_aportes + total_aluguel),
            'patrimonio_final': float(montante),
            'resumo_explicativo': f'💰 Invista e compre à vista.'
        }
    return None


def _calcular_consorcio_detalhado(valor_carta, prazo_meses, estrategia, valor_lance, tempo_maximo, aluguel_mensal, capital_inicial):
    TAXA_ADMINISTRACAO = Decimal('0.18')
    TAXA_FUNDO_RESERVA = Decimal('0.01')
    TAXA_SEGURO_MENSAL = Decimal('0.0002')
    valor_total_consorcio = valor_carta * (1 + TAXA_ADMINISTRACAO + TAXA_FUNDO_RESERVA)
    parcela_mensal_antes = (valor_total_consorcio / Decimal(prazo_meses)) + (valor_carta * TAXA_SEGURO_MENSAL)
    
    if estrategia == 'lance_unico' and valor_lance >= valor_carta * Decimal('0.30'): meses_ate_contemplacao = 2
    elif estrategia == 'lances_mensais': meses_ate_contemplacao = int(prazo_meses * 0.25)
    else: meses_ate_contemplacao = int(prazo_meses * 0.50)
    
    meses_restantes = prazo_meses - meses_ate_contemplacao
    parcela_apos = (valor_carta / Decimal(meses_restantes)) + (valor_carta * TAXA_SEGURO_MENSAL) if meses_restantes > 0 else 0
    custo_total = (parcela_mensal_antes * meses_ate_contemplacao) + (parcela_apos * meses_restantes) + valor_lance
    total_desembolso = custo_total + (aluguel_mensal * meses_ate_contemplacao)

    return {
        'metodo': 'Consórcio',
        'parcela_inicial': float(parcela_mensal_antes),
        'prazo_final_anos': round(prazo_meses / 12, 1),
        'meses_ate_contemplacao': meses_ate_contemplacao,
        'total_custo': float(custo_total),
        'total_desembolso': float(total_desembolso),
        'patrimonio_final': float(valor_carta),
        'resumo_explicativo': f'🎲 Consórcio não tem juros, mas requer contemplação.'
    }


def _calcular_financiamento(metodo, valor_principal, taxa_anual, prazo_meses, renda_familiar, fgts_saldo, usar_fgts, aluguel_durante, idade=30):
    # Aplicando Taxa Admin padrão de R$ 25,00 conforme auditoria 2024
    resultado = calcular_price_sac(
        metodo=metodo, 
        valor_principal=valor_principal, 
        taxa_anual=taxa_anual, 
        prazo_meses=prazo_meses, 
        usar_fgts_financiamento=usar_fgts, 
        fgts_saldo=fgts_saldo, 
        idade=idade,
        taxa_admin_mensal=25.0
    )

    tabela = resultado.get('tabela', [])
    if not tabela: return {'metodo': f'Financiamento {metodo.upper()}', 'total_custo': float(valor_principal)}
    
    parcela_inicial = Decimal(str(resultado.get('parcela_inicial', tabela[0].get('parcela', 0))))
    total_juros = Decimal(str(resultado.get('total_juros', 0)))
    total_seguros = Decimal(str(resultado.get('total_seguros_taxas', 0)))
    prazo_final = resultado.get('prazo_final_meses', len(tabela))
    
    # Custo Total = Principal + Juros + Seguros/Taxas
    custo_total = valor_principal + total_juros + total_seguros
    total_desembolso = custo_total + (aluguel_durante * Decimal(min(prazo_final, int(prazo_meses))))

    return {
        'metodo': f'Financiamento {metodo.upper()}',
        'parcela_inicial': float(parcela_inicial),
        'total_juros': float(total_juros),
        'total_custo': float(custo_total),
        'prazo_final_anos': round(prazo_final / 12, 1),
        'total_desembolso': float(total_desembolso),
        'patrimonio_final': float(valor_principal),
        'resumo_explicativo': f'Financiamento {metodo.upper()}.'
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
    if 'wizard_v2_data' not in request.session:
        messages.warning(request, "Nenhuma simulação encontrada.")
        return redirect('wizard_v2')
    wizard_data = request.session.get('wizard_v2_data', {})
    valor = wizard_data.get('imovel_desejado', {}).get('valor_imovel_desejado', 0)
    nome = f"Simulação V2 R$ {float(valor):,.2f}"
    SavedSimulation.objects.create(user=request.user, titulo=nome, dados_wizard=wizard_data, resultados=request.session.get('wizard_v2_resultados', {}))
    messages.success(request, "Simulação salva!")
    return redirect('dashboard')


def exportar_pdf_simulacao_v2(request):
    return HttpResponse("Em breve disponível no mobile.")
