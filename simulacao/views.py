from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from .forms import FinanciamentoForm, InvestidorImobiliarioForm
from . import utils
import json
from .calculadora_financeira import calcular_investidor_imobiliario
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from .models import SavedSimulation
from .decorators import premium_required
from .lgpd_views import audit_log
from .subscription_models import Subscription, SubscriptionPlan
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.widgets.markers import makeMarker

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

@login_required
@premium_required
def exportar_simulacao_excel(request, sim_id):
    """
    Exporta os dados de uma simulação salva para um arquivo Excel.
    Feature exclusiva para usuários Premium.
    """
    try:
        simulacao = SavedSimulation.objects.get(id=sim_id, user=request.user)
    except SavedSimulation.DoesNotExist:
        messages.error(request, "Simulação não encontrada ou não pertence a você.")
        return redirect('dashboard')

    # Cria o workbook e a planilha
    wb = Workbook()
    ws = wb.active
    ws.title = "Tabela de Amortização"

    # Cabeçalho
    headers = ["Mês", "Parcela", "Juros", "Amortização", "Saldo Devedor"]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # Dados da simulação (assumindo que os resultados estão em JSON)
    # Acessa a tabela do cenário mais vantajoso, ou a primeira que encontrar
    resultados = simulacao.resultados or {}
    tabela_amortizacao = resultados.get('price', {}).get('tabela') or resultados.get('sac', {}).get('tabela') or []
    
    if not tabela_amortizacao:
        messages.error(request, "Não há dados de tabela de amortização para exportar.")
        return redirect('dashboard')

    for linha in tabela_amortizacao:
        ws.append([
            linha.get('mes'),
            linha.get('parcela'),
            linha.get('juros'),
            linha.get('amortizacao'),
            linha.get('saldo_devedor')
        ])

    # Configura a resposta HTTP para download
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="simulacao_{simulacao.nome.replace(" ", "_")}_{sim_id}.xlsx"'
    wb.save(response)

    return response

@login_required
@premium_required
def exportar_simulacao_pdf(request, sim_id):
    """
    Exporta os dados de uma simulação salva para um arquivo PDF com formatação profissional.
    Feature exclusiva para usuários Premium.
    Corretores com Plano Profissional recebem cabeçalho White-Label personalizado.
    """
    try:
        simulacao = SavedSimulation.objects.get(id=sim_id, user=request.user)
    except SavedSimulation.DoesNotExist:
        messages.error(request, "Simulação não encontrada ou não pertence a você.")
        return redirect('dashboard')

    # Verifica se o plano do usuário suporta White-Label
    from .subscription_models import Subscription
    from django.utils import timezone as tz
    from reportlab.platypus import Image as RLImage
    import os

    tem_white_label = Subscription.objects.filter(
        usuario=request.user,
        status='ATIVA',
        data_expiracao__gt=tz.now(),
        plano__pdf_white_label=True
    ).exists()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()

    # ── CABEÇALHO ──────────────────────────────────────────────────────────────
    if tem_white_label:
        # Cabeçalho personalizado do corretor
        profile = request.user.profile
        header_data = [[]]
        header_style = []

        # Logo (coluna esquerda)
        if profile.logo_empresa and os.path.exists(profile.logo_empresa.path):
            logo_img = RLImage(profile.logo_empresa.path, width=120, height=50, kind='proportional')
            header_data[0].append(logo_img)
        else:
            header_data[0].append(Paragraph("<b>🏠 ImobCalc</b>", styles['Title']))

        # Info do corretor (coluna direita)
        nome_completo = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.email
        info_lines = [f"<b>{nome_completo}</b>"]
        if profile.nome_empresa:
            info_lines.append(profile.nome_empresa)
        if profile.creci:
            info_lines.append(f"CRECI: {profile.creci}")
        if request.user.telefone:
            info_lines.append(f"Tel: {request.user.telefone}")

        info_text = "<br/>".join(info_lines)
        header_data[0].append(Paragraph(info_text, styles['Normal']))

        header_table = Table(header_data, colWidths=[220, '*'])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#667eea')),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 10))

        elements.append(Paragraph(f"Relatório de Simulação: <b>{simulacao.titulo if hasattr(simulacao, 'titulo') else sim_id}</b>", styles['Heading2']))
    else:
        # Cabeçalho padrão ImobCalc
        elements.append(Paragraph(f"Relatório de Simulação: {simulacao.titulo if hasattr(simulacao, 'titulo') else sim_id}", styles['Title']))

    elements.append(Spacer(1, 8))

    # Metadados
    elements.append(Paragraph(f"<b>Data da Simulação:</b> {simulacao.criado_em.strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 24))

    # Extração dos dados
    resultados = simulacao.resultados or {}
    cenario_usado = 'price' if 'price' in resultados else 'sac'
    cenario_resultado = resultados.get(cenario_usado, {})
    tabela_amortizacao = cenario_resultado.get('tabela', [])

    # Seção de Resumo da Simulação
    elements.append(Paragraph("Resumo da Simulação", styles['Heading2']))
    resumo_data = [
        ['Sistema de Amortização:', cenario_usado.upper()],
        ['Valor da Parcela Inicial:', f"R$ {cenario_resultado.get('parcela_inicial', 0):,.2f}"],
        ['Total de Juros Pagos:', f"R$ {cenario_resultado.get('total_juros', 0):,.2f}"],
        ['Custo Efetivo Total (CET):', f"{cenario_resultado.get('cet_anual', 0):.2f}% a.a." if cenario_resultado.get('cet_anual') else "N/A"],
    ]
    summary_table = Table(resumo_data, hAlign='LEFT', colWidths=[200, '*'])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 24))

    if tabela_amortizacao:
        elements.append(Paragraph("Tabela de Amortização", styles['Heading2']))
        elements.append(Spacer(1, 12))

        # Cabeçalho da Tabela
        data = [['Mês', 'Parcela', 'Juros', 'Amortização', 'Saldo Devedor']]
        
        # Dados
        for linha in tabela_amortizacao:
            data.append([
                str(linha.get('mes', '')),
                f"R$ {linha.get('parcela', 0):,.2f}",
                f"R$ {linha.get('juros', 0):,.2f}",
                f"R$ {linha.get('amortizacao', 0):,.2f}",
                f"R$ {linha.get('saldo_devedor', 0):,.2f}"
            ])

        # Estilo Profissional da Tabela
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # Alinhar valores numéricos à direita
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ]))
        elements.append(table)

        # Gráfico de Evolução do Saldo Devedor
        elements.append(Spacer(1, 24))
        elements.append(Paragraph("Evolução do Saldo Devedor", styles['Heading2']))
        elements.append(Spacer(1, 12))

        drawing = Drawing(width=500, height=250)
        chart_data = [(linha['mes'], linha['saldo_devedor']) for linha in tabela_amortizacao]
        
        lp = LinePlot()
        lp.x = 50
        lp.y = 50
        lp.height = 180
        lp.width = 420
        lp.data = [chart_data]
        lp.strokeColor = colors.HexColor('#667eea')
        lp.lines[0].strokeWidth = 2
        lp.lines.symbol = makeMarker('Circle', size=3, fillColor=colors.HexColor('#764ba2'))

        # Eixo X (Meses)
        lp.xValueAxis.valueMin = 0
        lp.xValueAxis.valueMax = max(d[0] for d in chart_data) if chart_data else 1
        lp.xValueAxis.valueStep = max(1, len(chart_data) // 10)
        lp.xValueAxis.labels.fontName = 'Helvetica'
        lp.xValueAxis.labels.fontSize = 7

        # Eixo Y (Saldo Devedor)
        lp.yValueAxis.valueMin = 0
        lp.yValueAxis.valueMax = max(d[1] for d in chart_data) if chart_data else 1
        lp.yValueAxis.labels.fontName = 'Helvetica'
        lp.yValueAxis.labels.fontSize = 7
        lp.yValueAxis.labelTextFormat = lambda v: f'R${v/1000:.0f}k'

        drawing.add(lp)
        elements.append(drawing)

    else:
        elements.append(Paragraph("Não há dados detalhados para exibir neste relatório.", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(content_type='application/pdf')
    filename = f"simulacao_{simulacao.nome.replace(' ', '_')}_{sim_id}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(buffer.getvalue())
    
    return response


# ============================================
# TAREFA 1 - API DE STATUS DE ASSINATURA
# ============================================
def api_assinatura_status(request):
    """
    Retorna se o usuário atual tem assinatura premium ativa.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'is_premium': False})
    
    from .subscription_models import Subscription
    from django.utils import timezone
    
    has_active = Subscription.objects.filter(
                    usuario=request.user,
                                status='ATIVA',
        data_expiracao__gt=timezone.now()
    ).exists()
    
    return JsonResponse({'is_premium': has_active})

def redirecionar_afiliado(request, link_id):
    from .models import LinkAfiliado, CliqueAfiliado
    link = get_object_or_404(LinkAfiliado, id=link_id, ativo=True)
    
    # Registrar clique
    CliqueAfiliado.objects.create(
        link=link,
        usuario=request.user if request.user.is_authenticated else None,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        pagina_origem=request.META.get('HTTP_REFERER', '')
    )
    
    return redirect(link.url_afiliado)

def api_links_afiliados(request):
    from .models import LinkAfiliado
    tipo = request.GET.get('tipo', None)
    links = LinkAfiliado.objects.filter(ativo=True)
    if tipo:
        links = links.filter(tipo=tipo)
    
    data = [{'id': l.id, 'nome': l.nome, 'tipo': l.tipo, 'url': f'/afiliado/{l.id}/', 'logo': l.logo.url if l.logo else None, 'descricao': l.descricao} for l in links]
    
    return JsonResponse({'links': data})