from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .forms import FinanciamentoForm, InvestidorImobiliarioForm
from . import utils
import json
from .calculadora_financeira import calcular_investidor_imobiliario
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from .models import SavedSimulation
from .decorators import premium_required
from .lgpd_views import audit_log
from .subscription_models import Subscription, SubscriptionPlan

def simulacao_view(request):
    """
    View antiga - mantida para compatibilidade
    Recomenda usar o wizard para melhor experiência
    """
    # Redireciona para o wizard na primeira visita
    if request.method == 'GET' and 'wizard_recommended' not in request.session:
        request.session['wizard_recommended'] = True
        messages.info(request, "💡 Dica: Use nosso Wizard guiado para descobrir qual método é mais vantajoso para você!")
    
    form = FinanciamentoForm()
    
    context = {
        'form': form,
        'tabela_amortizacao': None,
        'resultado_final': None,
    }

    if request.method == 'POST':
        form = FinanciamentoForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            
            valor_imovel = data['valor_imovel']
            valor_entrada = data['valor_entrada']
            taxa_anual_percentual = data['taxa_anual']
            prazo_meses = data['prazo_meses']
            metodo = data['metodo']
            
            # Calcular o Saldo Devedor Principal
            saldo_devedor = valor_imovel - valor_entrada
            
            # Usa a função correta do utils.py
            resultado = utils.simular_financiamento_geral(
                metodo=metodo,
                valor_principal=float(saldo_devedor),
                taxa_anual=float(taxa_anual_percentual),
                prazo_meses=int(prazo_meses)
            )       
            if resultado and resultado.get('tabela'):
                # Extrai a tabela do resultado
                tabela_final = resultado['tabela']
                context['tabela_amortizacao'] = tabela_final
                context['resultado_final'] = f"Simulação {metodo.upper()} calculada com sucesso!"
                context['parcela_inicial'] = resultado.get('parcela_inicial', 0)
                context['total_juros'] = resultado.get('total_juros', 0)
            else:
                context['resultado_final'] = "Erro no cálculo! Verifique os parâmetros."
        else:
            context['resultado_final'] = "Erro! Verifique os dados do formulário."
    
    return render(request, 'simulacao/index.html', context)

@login_required
@audit_log('READ', 'DASHBOARD', 'Usuário acessou dashboard')
def dashboard(request):
    # Busca as simulações do usuário logado, ordenadas da mais recente para a mais antiga
    simulacoes = SavedSimulation.objects.filter(user=request.user).order_by('-criado_em')
    return render(request, 'dashboard.html', {'simulacoes': simulacoes})

@login_required
@premium_required
def investidor_imobiliario_view(request):
    """
    View para o Cenário 6: Investidor Imobiliário.
    Recebe dados via POST e retorna JSON com a análise de viabilidade.
    """
    if request.method == 'POST':
        form = InvestidorImobiliarioForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            
            # Mapeia os dados do formulário para o formato esperado pela calculadora
            dados_calc = {
                'valor_imovel': data['valor_imovel'],
                'valor_entrada': data['entrada'],
                'prazo_meses': data['prazo_anos'] * 12,
                'taxa_juros_anual': data['taxa_juros_anual'],
                'sistema_amortizacao': data['sistema_amortizacao'],
                'valor_aluguel_mensal': data.get('valor_aluguel_mensal') or 0,
                'usar_aluguel_para_prestacao': data['usar_aluguel_para_prestacao'],
                'taxa_administracao_pct': data['taxa_administracao'] or 0,
                'iptu_anual': (data.get('iptu_mensal') or 0) * 12,
                'condominio_mensal': data.get('condominio_mensal') or 0,
            }
            
            resultado = calcular_investidor_imobiliario(dados_calc)
            return JsonResponse(resultado)
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    
    form = InvestidorImobiliarioForm()
    return render(request, 'simulacao/investidor_imobiliario.html', {'form': form})

@login_required
@premium_required
def comparador_investimentos_view(request):
    """
    View para o Cenário 7: Comparador de Investimentos.
    Permite comparar múltiplos investimentos e visualizar qual é mais vantajoso.
    """
    if request.method == 'POST':
        # Processar dados do formulário
        investimentos = []
        i = 1
        while f'nome_{i}' in request.POST:
            investimento = {
                'nome': request.POST.get(f'nome_{i}', ''),
                'tipo': request.POST.get(f'tipo_{i}', ''),
                'valor_inicial': float(request.POST.get(f'valor_inicial_{i}', 0)),
                'taxa_juros': float(request.POST.get(f'taxa_juros_{i}', 0)),
                'prazo_meses': int(request.POST.get(f'prazo_meses_{i}', 0)),
            }
            investimentos.append(investimento)
            i += 1
        
        # Calcular comparação
        resultado = calcular_comparador_investimentos(investimentos)
        return JsonResponse(resultado)
    else:
        # Renderizar formulário
        return render(request, 'simulacao/comparador_investimentos.html')
    
@login_required
def upgrade_premium_view(request):
    """
    Exibe a página de upgrade para planos Premium, mostrando os planos disponíveis.
    """
    # Busca todos os planos ativos e ordena pelo preço
    planos = SubscriptionPlan.objects.filter(ativo=True).order_by('preco')
    
    context = {
        'planos': planos
    }
    return render(request, 'simulacao/upgrade_premium.html', context)



def calcular_comparador_investimentos(investimentos):
    """
    Função para calcular o comparador de investimentos.
    Recebe uma lista de investimentos e retorna uma análise comparativa.
    """
    resultados = []
    for inv in investimentos:
        valor_final = inv['valor_inicial'] * (1 + inv['taxa_juros'] / 100) ** (inv['prazo_meses'] / 12)
        resultados.append({
            'nome': inv['nome'],
            'tipo': inv['tipo'],
            'valor_final': round(valor_final, 2),
            'rentabilidade': round((valor_final - inv['valor_inicial']) / inv['valor_inicial'] * 100, 2)
        })
    
    # Ordenar por valor final decrescente
    resultados.sort(key=lambda x: x['valor_final'], reverse=True)
    
    return {'resultados': resultados}


# ============================================
# APIs para AdMob/Monetizacao
# ============================================

def api_assinatura_status(request):
    """
    Retorna se o usuario atual tem assinatura premium ativa.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'is_premium': False})
    
    # Verifica assinaturas ativas
    active_sub = None
    subscriptions = Subscription.objects.filter(usuario=request.user, status='ATIVA')
    
    for sub in subscriptions:
        if sub.esta_ativa():
            active_sub = sub
            break
            
    if active_sub:
        return JsonResponse({
            'is_premium': True,
            'plano': active_sub.plano.nome,
            'dias_restantes': active_sub.dias_restantes()
        })
    
    return JsonResponse({
        'is_premium': False,
        'plano': None
    })


def api_registrar_ad_view(request):
    """
    Registra visualizacao de anuncio para analytics.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Metodo nao permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        ad_type = data.get('ad_type', 'unknown')
        page = data.get('page', 'unknown')
        
        # Log para analytics (pode ser expandido depois)
        print(f"Ad view: {ad_type} on {page}")
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)