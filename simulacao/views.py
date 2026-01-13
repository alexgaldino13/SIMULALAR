from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FinanciamentoForm
from . import utils
from decimal import Decimal 

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
                prazo_meses=int(prazo_meses),
                seguro_mensal=float(data.get('seguro_mensal', 0.03)),
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