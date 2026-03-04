# simulacao/wizard_views_novo.py
"""
Nova view do wizard - estruturada para cenários realistas
"""

from django.shortcuts import render, redirect, HttpResponse
from django.template.loader import get_template
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SavedSimulation
from decimal import Decimal
from . import wizard_forms_novo as forms_novo
from . import wizard_questions_novo as questions_novo
from .calculadora_financeira import simular_financiamento_geral, simular_consorcio, calcular_mcmv
from .alerta_consumidor import integrar_alertas_ao_contexto
from .utils import calcular_price_sac
import json


def _convert_decimals_to_floats(data):
    """
    Converte Decimal para float recursivamente para JSON serialization
    """
    if isinstance(data, dict):
        return {k: _convert_decimals_to_floats(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_convert_decimals_to_floats(item) for item in data]
    elif isinstance(data, Decimal):
        return float(data)
    return data


# Constantes
WIZARD_STEPS_NEW = {
    1: {'form': forms_novo.WizardObjetivoForm, 'name': 'objetivo', 'title': 'Seu Objetivo'},
    2: {'form': forms_novo.WizardSituacaoAtualForm, 'name': 'situacao', 'title': 'Situação Atual'},
    3: {'form': forms_novo.WizardCapitalForm, 'name': 'capital', 'title': 'Capital Disponível'},
    4: {'form': forms_novo.WizardRendaCustosForm, 'name': 'renda_custos', 'title': 'Renda & Custos'},
    5: {'form': forms_novo.WizardCenariosForm, 'name': 'cenarios', 'title': 'Cenários'},
}
TOTAL_STEPS_NEW = len(WIZARD_STEPS_NEW)


def _calcular_financiamento(metodo, valor_principal, taxa_anual, prazo_meses, renda_familiar, 
                           fgts_saldo, usar_fgts, aluguel_durante):
    """
    Wrapper para calcular financiamento PRICE ou SAC
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
    
    # Processa resultado
    tabela = resultado.get('tabela', [])
    if not tabela:
        return {
            'metodo': f'Financiamento {metodo.upper()}',
            'parcela_inicial': 0,
            'total_juros': 0,
            'total_principal': float(valor_principal),
            'total_custo': float(valor_principal),
            'prazo_final_meses': prazo_meses,
            'prazo_final_anos': round(prazo_meses / 12, 1),
            'aluguel_durante': 0,
            'total_desembolso': float(valor_principal),
            'patrimonio_final': float(valor_principal),
            'economia_com_fgts': 0,
        }
    
    parcela_inicial = Decimal(str(resultado.get('parcela_inicial', tabela[0].get('parcela', 0))))
    total_juros = Decimal(str(resultado.get('total_juros', 0)))
    prazo_final = len(tabela)
    
    # Custo total (principal + juros)
    custo_total = valor_principal + total_juros
    
    # Custo com aluguel durante o período
    meses_aluguel = min(prazo_final, int(prazo_meses))
    custo_aluguel = aluguel_durante * Decimal(meses_aluguel)
    
    total_desembolso = custo_total + custo_aluguel
    
    # Cálculo de comprometimento de renda
    comprometimento = Decimal('0')
    if renda_familiar > 0:
        comprometimento = (parcela_inicial / renda_familiar) * 100

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
        'economia_com_fgts': float(total_juros * Decimal('0.1')) if usar_fgts and fgts_saldo > 0 else 0,
        'comprometimento_renda': float(comprometimento),
        'alerta_comprometimento': comprometimento > 30,
    }


def wizard_novo(request, step=None):
    """
    Nova view do wizard - didática e realista
    """
    
    # Inicializa sessão
    if 'wizard_novo_data' not in request.session:
        request.session['wizard_novo_data'] = {}
        request.session['wizard_novo_current_step'] = 1
    
    # Determina passo atual
    if step:
        try:
            current_step = int(step)
            if current_step < 1 or current_step > TOTAL_STEPS_NEW:
                current_step = request.session.get('wizard_novo_current_step', 1)
        except ValueError:
            current_step = request.session.get('wizard_novo_current_step', 1)
    else:
        current_step = request.session.get('wizard_novo_current_step', 1)

    wizard_data = request.session.get('wizard_novo_data', {})
    step_info = WIZARD_STEPS_NEW[current_step]
    form_class = step_info['form']

    
    # Processa POST
    if request.method == 'POST':
        if current_step == 5:
            form = form_class(request.POST, wizard_data=wizard_data)
        else:
            form = form_class(request.POST)
        
        if form.is_valid():
            # Salva dados convertendo Decimal para float
            cleaned_data = _convert_decimals_to_floats(form.cleaned_data)
            wizard_data[step_info['name']] = cleaned_data
            request.session['wizard_novo_data'] = wizard_data
            
            # Próximo passo
            if current_step < TOTAL_STEPS_NEW:
                next_step = current_step + 1
                request.session['wizard_novo_current_step'] = next_step
                return redirect('wizard_novo_step', step=next_step)
            else:
                # Último passo - calcular e ir para resultados
                resultados = calcular_cenarios_novo(wizard_data)
                request.session['wizard_novo_resultados'] = resultados
                return redirect('wizard_novo_resultados')
    else:
        # GET - renderiza form atual
        form = form_class()
    
    # Contexto
    context = {
        'form': form,
        'step_title': step_info['title'],
        'current_step': current_step,
        'total_steps': TOTAL_STEPS_NEW,
        'progress': int((current_step / TOTAL_STEPS_NEW) * 100),
        'can_go_back': current_step > 1,
        'is_last_step': current_step == TOTAL_STEPS_NEW,
    }
    
    return render(request, 'simulacao/wizard_novo_step.html', context)


@require_http_methods(['GET'])
def wizard_novo_resultados(request):
    """
    Exibe os resultados comparativos dos cenários
    """
    
    resultados = request.session.get('wizard_novo_resultados', {})
    wizard_data = request.session.get('wizard_novo_data', {})
    
    if not resultados:
        return redirect('wizard_novo')
    
    # Converte para formato para template
    context = {
        'resultados': resultados,
        'wizard_data': wizard_data,
        'resumo': _criar_resumo_resultados(resultados, wizard_data),
    }
    
    # Extrair dados corretamente da estrutura aninhada
    objetivo = wizard_data.get('objetivo', {})
    valor_imovel = float(objetivo.get('valor_imovel_desejado', 0) or 0)
    prazo_anos = int(objetivo.get('prazo_desejado_anos', 30) or 30)
    
    # Adiciona alertas de consumidor
    context = integrar_alertas_ao_contexto(
        context,
        financiamento_data={
            'saldo_devedor_atual': valor_imovel,
            'prazo_restante': prazo_anos * 12
        }
    )
    
    return render(request, 'simulacao/wizard_novo_resultados.html', context)


def calcular_cenarios_novo(wizard_data):
    """
    Calcula todos os cenários selecionados com base nos dados do wizard
    """
    
    # Extrai dados
    situacao = wizard_data.get('situacao', {})
    capital = wizard_data.get('capital', {})
    objetivo = wizard_data.get('objetivo', {})
    renda_custos = wizard_data.get('renda_custos', {})
    cenarios_selecionados = wizard_data.get('cenarios', {})
    
    # Converte para Decimal
    valor_imovel = Decimal(str(objetivo.get('valor_imovel_desejado', 500000)))
    prazo_anos = objetivo.get('prazo_desejado_anos', 10)
    prazo_meses = prazo_anos * 12
    renda_bruta = Decimal(str(renda_custos.get('renda_familiar_bruta', 8000)))
    aluguel_atual = Decimal(str(situacao.get('aluguel_atual', 0)))
    capital_guardado = Decimal(str(capital.get('saldo_dinheiro_guardado', 0)))
    valor_imovel_proprio = Decimal(str(capital.get('valor_imovel_proprio', 0) or 0))
    objetivo_principal = objetivo.get('objetivo_principal', '')

    # Tratar valores vazios ou inválidos
    try:
        fgts_saldo = Decimal(str(capital.get('saldo_fgts', 0) or 0))
    except:
        fgts_saldo = Decimal('0')
    custas_documentacao = Decimal(str(capital.get('custas_documentacao', 15000)) or 15000)
    custas_documentacao_forma = capital.get('custas_documentacao_forma', 'financiado')
    
    
    # Calcula entrada disponível
    entrada = capital_guardado
    
    # Se o objetivo for trocar de imóvel, soma o valor do imóvel atual à entrada
    if objetivo_principal == 'trocar':
        entrada += max(valor_imovel_proprio - Decimal(str(capital.get('divida_imovel_atual', 0) or 0)), Decimal('0'))

    principal = valor_imovel - entrada
    
    # Adiciona custas de documentação ao financiamento apenas se a opção for 'financiado'
    if custas_documentacao_forma == 'financiado':
        principal = principal + custas_documentacao
    resultados = {}
    
    # CENÁRIO 1: Financiamento PRICE
    if cenarios_selecionados.get('comparar_financiamento_price'):
        resultado_price = _calcular_financiamento(
    metodo='price',
    valor_principal=principal,
    taxa_anual=Decimal('8.5'),
    prazo_meses=prazo_meses,
    renda_familiar=renda_bruta,
    fgts_saldo=fgts_saldo if cenarios_selecionados.get('usar_fgts') else Decimal('0'),
    usar_fgts=cenarios_selecionados.get('usar_fgts', True),
    aluguel_durante=aluguel_atual,
        )
        resultados['price'] = resultado_price
    
    # CENÁRIO 2: Financiamento SAC
    if cenarios_selecionados.get('comparar_financiamento_sac'):
        resultado_sac = _calcular_financiamento(
    metodo='sac',
    valor_principal=principal,
    taxa_anual=Decimal('8.5'),
    prazo_meses=prazo_meses,
    renda_familiar=renda_bruta,
    fgts_saldo=fgts_saldo if cenarios_selecionados.get('usar_fgts') else Decimal('0'),
    usar_fgts=cenarios_selecionados.get('usar_fgts', True),
    aluguel_durante=aluguel_atual,
        )
        resultados['sac'] = resultado_sac
    
    # CENÁRIO MCMV (Minha Casa Minha Vida)
    # Lógica Automática: Se selecionado OU se a renda permite (<= R$ 8.000), tentamos calcular.
    # A função calcular_mcmv valida internamente o valor do imóvel e outras regras.
    if cenarios_selecionados.get('comparar_mcmv') or renda_bruta <= Decimal('8000'):
        # MCMV usa o capital guardado como entrada (pode ser menor que 20%)
        # e o saldo FGTS disponível
        resultado_mcmv = calcular_mcmv(
            valor_imovel=valor_imovel,
            renda_familiar_mensal=renda_bruta,
            valor_entrada=capital_guardado,
            prazo_meses=prazo_meses,
            usa_fgts=cenarios_selecionados.get('usar_fgts', True),
            valor_fgts_disponivel=fgts_saldo
        )
        
        if resultado_mcmv['qualificado']:
            # Adapta para o formato padrão de exibição
            resultado_mcmv['metodo'] = f"MCMV - Faixa {resultado_mcmv['faixa']}"
            resultado_mcmv['parcela_inicial'] = resultado_mcmv['parcela_media']
            # Total desembolsado = custo total do financiamento + entrada paga
            resultado_mcmv['total_desembolso'] = resultado_mcmv['custo_total'] + capital_guardado
            resultado_mcmv['patrimonio_final'] = float(valor_imovel)
            resultados['mcmv'] = resultado_mcmv
        else:
            # Se não qualificado, podemos optar por não mostrar ou mostrar erro
            pass

    # CENÁRIO 3: Consórcio
    if cenarios_selecionados.get('comparar_consorcio'):
        resultado_consorcio = _calcular_consorcio_novo(
    valor_imovel=valor_imovel,
    prazo_anos=prazo_anos,
    aluguel_durante=aluguel_atual,
    renda_bruta=renda_bruta,
    capital_guardado=capital_guardado,
    taxa_investimento=taxa_investimento,
    fgts_saldo=fgts_saldo,
        )
        resultados['consorcio'] = resultado_consorcio
    
    # CENÁRIO 4: Aluguel + Investimento
    if cenarios_selecionados.get('comparar_aluguel_investimento'):
        resultado_aluguel = _calcular_aluguel_investimento(
    aluguel_mensal=aluguel_atual,
    capital_inicial=capital_guardado,
    renda_bruta=renda_bruta,
    taxa_investimento=taxa_investimento,
    prazo_anos=prazo_anos,
    valor_imovel_futuro=valor_imovel,
        )
        resultados['aluguel_investimento'] = resultado_aluguel
    
    # CENÁRIO 5: Compra à Vista
    if cenarios_selecionados.get('comparar_compra_a_vista') and capital_guardado >= valor_imovel:
        resultado_a_vista = _calcular_compra_a_vista(
    valor_imovel=valor_imovel,
    capital_disponivel=capital_guardado,
    taxa_investimento=taxa_investimento,
    prazo_anos=prazo_anos,
        )
        resultados['compra_a_vista'] = resultado_a_vista

            # CENÁRIO 6: Guardar Dinheiro
    if cenarios_selecionados.get('comparar_guardar_dinheiro'):
        # Calcula renda disponível (renda - aluguel - despesas básicas)
        despesas_basicas = Decimal('2000')  # Estimativa de despesas básicas
        renda_disponivel_guardar = max(renda_bruta - aluguel_atual - despesas_basicas, Decimal('0'))
        
        resultado_guardar = _calcular_guardar_dinheiro(
            valor_imovel=valor_imovel,
            capital_inicial=capital_guardado,
            renda_disponivel=renda_disponivel_guardar,
            taxa_investimento=taxa_investimento,
            aluguel_mensal=aluguel_atual,
            prazo_anos=prazo_anos,
        )
        resultados['guardar_dinheiro'] = resultado_guardar

    
    return resultados


def _calcular_consorcio_novo(valor_imovel, prazo_anos, aluguel_durante, 
                             renda_bruta, capital_guardado, taxa_investimento, fgts_saldo):
    """
    Calcula consórcio considerando morada durante o período
    """
    
    prazo_meses = prazo_anos * 12
    
    # Calcula consórcio básico
    resultado = simular_consorcio(
        valor_imovel=valor_imovel,
        prazo_meses=prazo_meses,
        taxa_adm=Decimal('2.0'),
        fundo_reserva=Decimal('0.8'),
        fgts_saldo=fgts_saldo,
    )
    
    if not resultado:
        return None
    
    parcela_consorcio = Decimal(str(resultado.get('parcela_fixa', 0)))
    custo_total = Decimal(str(resultado.get('total_custo', 0)))
    
    # Tempo até contemplação (estimado 40% do prazo)
    mes_contemplacao = resultado.get('mes_contemplacao_estimado', int(prazo_meses * 0.4))
    
    # Custo com aluguel durante TODA o período (até ser contemplado)
    custo_aluguel_total = aluguel_durante * Decimal(mes_contemplacao)
    
    # Custo total do consórcio (parcelas até contemplação)
    custo_parcelas_consorcio = parcela_consorcio * Decimal(mes_contemplacao)
    
    total_desembolso = custo_parcelas_consorcio + custo_aluguel_total
    
    # Cálculo de comprometimento de renda
    comprometimento = Decimal('0')
    if renda_bruta > 0:
        comprometimento = (parcela_consorcio / renda_bruta) * 100

    return {
        'metodo': 'Consórcio',
        'parcela_inicial': float(parcela_consorcio),
        'total_custo_consorcio': float(custo_total),
        'mes_contemplacao_estimado': mes_contemplacao,
        'anos_ate_contemplacao': round(mes_contemplacao / 12, 1),
        'custo_parcelas': float(custo_parcelas_consorcio),
        'custo_aluguel_durante': float(custo_aluguel_total),
        'total_desembolso': float(total_desembolso),
        'patrimonio_final': float(valor_imovel),
        'observacao': f'Contemplação estimada em {mes_contemplacao} meses ({round(mes_contemplacao/12, 1)} anos)',
        'comprometimento_renda': float(comprometimento),
        'alerta_comprometimento': comprometimento > 30,
    }


def _calcular_aluguel_investimento(aluguel_mensal, capital_inicial, renda_bruta, 
                                   taxa_investimento, prazo_anos, valor_imovel_futuro):
    """
    Calcula cenário de aluguel contínuo + investimento da diferença
    """
    
    prazo_meses = prazo_anos * 12
    
    # Custo total de aluguel
    custo_aluguel_total = aluguel_mensal * Decimal(prazo_meses)
    
    # Aporte mensal para investimento (assume 10% da renda disponível)
    renda_disponivel = renda_bruta - (aluguel_mensal + Decimal('2000'))  # 2000 outras despesas
    aporte_mensal = max(renda_disponivel * Decimal('0.1'), Decimal('0'))
    
    # Total de aporte acumulado sem juros
    total_aportes = aporte_mensal * Decimal(prazo_meses)
    
    # Calcula montante com juros compostos
    taxa_mensal = (Decimal(str(taxa_investimento)) / 100) / 12
    montante_investido = capital_inicial
    
    for mes in range(prazo_meses):
        montante_investido = montante_investido * (1 + taxa_mensal) + aporte_mensal
    
    # Ganho com investimento (retorno)
    ganho_investimento = montante_investido - capital_inicial - total_aportes
    
    # Verificar se consegue comprar o imóvel com o investimento acumulado
    pode_comprar = montante_investido >= valor_imovel_futuro
    
    # Se conseguir comprar, sobra fica como patrimônio líquido
    # Se não conseguir, o patrimônio é só o investimento
    patrimonio_final = montante_investido
    
    # Cálculo de comprometimento de renda (Aluguel)
    comprometimento = Decimal('0')
    if renda_bruta > 0:
        comprometimento = (aluguel_mensal / renda_bruta) * 100

    return {
        'metodo': 'Aluguel + Investimento',
        'aluguel_mensal': float(aluguel_mensal),
        'total_aluguel_gasto': float(custo_aluguel_total),
        'aporte_mensal_investimento': float(aporte_mensal),
        'total_aportes': float(total_aportes),
        'capital_inicial': float(capital_inicial),
        'taxa_investimento': float(taxa_investimento),
        'montante_final_investimento': float(montante_investido),
        'ganho_com_investimento': float(ganho_investimento),
        'pode_comprar_imovel': pode_comprar,
        'valor_imovel_alvo': float(valor_imovel_futuro),
        'sobra_apos_compra': float(montante_investido - valor_imovel_futuro) if pode_comprar else 0.0,
        'patrimonio_final_total': float(montante_investido),
        'observacao': f'Investimento acumulado: R$ {montante_investido:,.2f}. Ganho: R$ {ganho_investimento:,.2f}. {"Consegue comprar o imóvel!" if pode_comprar else "Precisa de mais tempo/retorno para comprar."}',
        'comprometimento_renda': float(comprometimento),
        'alerta_comprometimento': comprometimento > 30,
    }


def _calcular_compra_a_vista(valor_imovel, capital_disponivel, taxa_investimento, prazo_anos):
    """
    Calcula compra à vista do imóvel + investimento da sobra
    """
    
    prazo_meses = prazo_anos * 12
    
    # Sobra para investir
    sobra = capital_disponivel - valor_imovel
    
    if sobra <= 0:
        return None
    
    # Calcula montante de investimento com juros compostos
    taxa_mensal = (Decimal(str(taxa_investimento)) / 100) / 12
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
        'patrimonio_final_total': float(patrimonio_total),
        'taxa_investimento': float(taxa_investimento),
        'observacao': 'Imóvel comprado à vista, sobra investida. Sem dívida, maior liberdade.',
    }


def _criar_resumo_resultados(resultados, wizard_data):
    """
    Cria um resumo comparativo dos cenários
    """
    
    resumo = {
        'dados_entrada': {
    'valor_imovel_alvo': wizard_data.get('objetivo', {}).get('valor_imovel_desejado'),
    'prazo_desejado': wizard_data.get('objetivo', {}).get('prazo_desejado_anos'),
    'renda_bruta': wizard_data.get('renda_custos', {}).get('renda_familiar_bruta'),
    'aluguel_atual': wizard_data.get('situacao', {}).get('aluguel_atual'),
        },
        'cenarios': resultados,
        'melhor_opcao': _achar_melhor_opcao(resultados),
    }
    
    return resumo


def _calcular_guardar_dinheiro(valor_imovel, capital_inicial, renda_disponivel, 
                                taxa_investimento, aluguel_mensal, prazo_anos):
    """
    Calcula quanto tempo leva para juntar o valor do imóvel
    considerando capital inicial + rendimentos + aportes mensais
    """
    
    prazo_meses = prazo_anos * 12
    valor_faltante = valor_imovel - capital_inicial
    
    if valor_faltante <= 0:
        # Já tem o valor total
        return {
            'metodo': 'Guardar Dinheiro',
            'meses_necessarios': 0,
            'anos_necessarios': 0,
            'capital_inicial': float(capital_inicial),
            'valor_imovel': float(valor_imovel),
            'ja_possui_valor': True,
            'custo_aluguel_total': 0,
            'total_investido': float(capital_inicial),
            'patrimonio_final': float(valor_imovel),
            'observacao': 'Você já possui o valor total do imóvel!'
        }
    
    # Taxa mensal de investimento
    taxa_mensal = (taxa_investimento / 100) / 12
    
    # Simula mês a mês até atingir o valor
    montante = capital_inicial
    mes = 0
    total_aportes = Decimal('0')
    
    while montante < valor_imovel and mes < prazo_meses:
        # Rendimento do mês
        montante = montante * (1 + taxa_mensal)
        # Aporte mensal
        montante = montante + renda_disponivel
        total_aportes = total_aportes + renda_disponivel
        mes += 1
    
    # Custo de aluguel durante o período
    custo_aluguel_total = aluguel_mensal * Decimal(mes)
    
    # Total desembolsado (aportes + aluguel)
    total_desembolso = total_aportes + custo_aluguel_total + capital_inicial
    
    return {
        'metodo': 'Guardar Dinheiro',
        'meses_necessarios': mes,
        'anos_necessarios': round(mes / 12, 1),
        'capital_inicial': float(capital_inicial),
        'valor_imovel': float(valor_imovel),
        'valor_faltante': float(valor_faltante),
        'ja_possui_valor': False,
        'montante_final': float(montante),
        'total_aportes': float(total_aportes),
        'aporte_mensal': float(renda_disponivel),
        'custo_aluguel_total': float(custo_aluguel_total),
        'aluguel_mensal': float(aluguel_mensal),
        'total_desembolso': float(total_desembolso),
        'patrimonio_final': float(valor_imovel),
        'taxa_investimento': float(taxa_investimento),
        'observacao': f'Tempo necessário: {mes} meses ({round(mes/12, 1)} anos). Custo aluguel: R$ {custo_aluguel_total:,.2f}'
    }



def _achar_melhor_opcao(resultados):
    """
    Identifica qual cenário é mais favorável (menor desembolso total)
    """
    
    if not resultados:
        return None
    
    melhor = None
    menor_custo = float('inf')
    
    for nome, resultado in resultados.items():
        if resultado and 'total_desembolso' in resultado:
            custo = resultado['total_desembolso']
            if custo < menor_custo:
                menor_custo = custo
                melhor = nome
    
    return melhor


def wizard_novo_reset(request):
    """
    Reseta o wizard novo, limpando a sessão
    """
    if 'wizard_novo_data' in request.session:
        del request.session['wizard_novo_data']
    if 'wizard_novo_current_step' in request.session:
        del request.session['wizard_novo_current_step']
    
    return redirect('wizard_novo')


@login_required
def salvar_simulacao(request):
    """
    Salva a simulação atual no banco de dados para o usuário logado
    """
    if 'wizard_novo_data' not in request.session:
        messages.warning(request, "Nenhuma simulação encontrada para salvar.")
        return redirect('wizard_novo')
    
    wizard_data = request.session.get('wizard_novo_data', {})
    resultados = request.session.get('wizard_novo_resultados', {})
    
    # Cria um nome descritivo baseado no valor do imóvel
    valor = wizard_data.get('objetivo', {}).get('valor_imovel_desejado', 0)
    try:
        valor_fmt = f"{float(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        valor_fmt = str(valor)
        
    nome = f"Simulação R$ {valor_fmt}"
    
    SavedSimulation.objects.create(
        user=request.user,
        nome=nome,
        dados_wizard=wizard_data,
        resultados=resultados
    )
    
    messages.success(request, "Simulação salva com sucesso no Dashboard!")
    return redirect('dashboard')


def exportar_pdf_simulacao(request):
    """
    Gera um PDF com os resultados da simulação atual da sessão
    """
    try:
        from xhtml2pdf import pisa
    except ImportError:
        return HttpResponse("Erro: Biblioteca xhtml2pdf não instalada. Execute: pip install xhtml2pdf")

    if 'wizard_novo_resultados' not in request.session:
        messages.warning(request, "Nenhuma simulação para exportar.")
        return redirect('wizard_novo')

    resultados = request.session.get('wizard_novo_resultados', {})
    wizard_data = request.session.get('wizard_novo_data', {})

    context = {
        'resultados': resultados,
        'wizard_data': wizard_data,
    }

    template_path = 'simulacao/pdf_relatorio.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_imobcalc.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Erro ao gerar PDF <pre>' + html + '</pre>')
    
    return response

def wizard_onboarding(request):
    """Tela inicial de boas-vindas (Mobile First)"""
    return render(request, 'simulacao/wizard_onboarding.html')
