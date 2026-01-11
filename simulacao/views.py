from django.shortcuts import render
from .forms import FinanciamentoForm
# 1. IMPORTAR a lógica de cálculo do utils.py
from . import utils # Importa tudo do utils.py

# Também é bom importar Decimal para garantir que os cálculos funcionem
from decimal import Decimal 

def simulacao_view(request):
    form = FinanciamentoForm()
    
    context = {
        'form': form,
        'tabela_amortizacao': None,
        'resultado_final': None,
    }

    # Verifica se a requisição é POST (o usuário enviou o formulário)
    if request.method == 'POST':
        form = FinanciamentoForm(request.POST)

        if form.is_valid():
            # 2. CAPTURAR OS DADOS (já em Decimal devido ao settings.py)
            data = form.cleaned_data
            
            valor_imovel = data['valor_imovel']
            valor_entrada = data['valor_entrada']
            taxa_anual_percentual = data['taxa_anual']
            prazo_meses = data['prazo_meses']
            metodo = data['metodo']
            
            # Calcular o Saldo Devedor Principal
            saldo_devedor = valor_imovel - valor_entrada
            
            # 3. CHAMAR A LÓGICA DE CÁLCULO
            
            tabela_final = []
            
            if metodo == 'price':
                # Chamando sua função PRICE (assumindo que ela existe em utils.py)
                tabela_final = utils.calcular_price(
                    saldo_devedor, 
                    taxa_anual_percentual, 
                    prazo_meses
                )
                context['resultado_final'] = "Simulação PRICE calculada com sucesso!"

            elif metodo == 'sac':
                # Chamando sua função SAC (assumindo que ela existe em utils.py)
                tabela_final = utils.calcular_sac(
                    saldo_devedor, 
                    taxa_anual_percentual, 
                    prazo_meses
                )
                context['resultado_final'] = "Simulação SAC calculada com sucesso!"
                
            # Adicione aqui os métodos 'renda' e 'consorcio'
            # ...
            
            # 4. ENVIAR OS RESULTADOS PARA O TEMPLATE
            context['tabela_amortizacao'] = tabela_final
            
        else:
            # Se a validação falhar (ex: campo vazio)
            context['resultado_final'] = "Erro! Verifique os dados do formulário."
    
    # 5. RENDERIZAR
    return render(request, 'simulacao/index.html', context)