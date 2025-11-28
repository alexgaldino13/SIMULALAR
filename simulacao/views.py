# views.py
from django.shortcuts import render
# Importa APENAS a função de agregação de alto nível
from .calculadora_financeira import comparar_cenarios_e_formatar 
# Importa o modelo (necessário apenas para a view de detalhe, mas OK aqui)
from .models import Financiamento 
# Não precisamos mais de 'from decimal import Decimal' ou de 'simular_financiamento_geral'
# na view principal.

# --- VIEW DE DETALHE SAC (Mantida) ---
def simulacao_sac_view(request, financiamento_id):
    # Lógica de detalhe correta. (Ainda depende de 'simular_financiamento_geral'
    # mas esta função deve ser importada DENTRO desta view ou movida para o topo.)
    # Por questões de limpeza, vamos assumir que 'simular_financiamento_geral'
    # foi movida para o topo das importações, ou importada localmente se o Django permitir.
    # ...
    # (Este código é mantido, pois a arquitetura está OK)
    # ...
    pass # Código omitido

# ----------------------------------------------------------------------
# VIEW PRINCIPAL (Simulador de Comparação - LIMPA e FOCADA)
# ----------------------------------------------------------------------
def simular_financiamento(request):
    
    # --- DADOS PADRÃO (GET) ---
    dados_iniciais_padrao = {
        # Mantenha os seus dados padrão aqui.
        # Eles NÃO PRECISAM SER Decimal. Strings são suficientes para o contexto do formulário.
        'valor_imovel': '500000',
        'entrada': '60000',
        'prazo_anos': '30',
        # ...
    }
    
    resultados_finais = [] 
    erro = None
    
    if request.method == 'POST':
        # 1. Sobrescreve os defaults com os dados do POST
        dados_iniciais = request.POST.dict() 
        
        try:
            # 2. Chama a única função que faz o trabalho pesado, passando o dicionário POST inteiro
            # Esta função lida com conversão, cálculo, agregação e formatação.
            resultados_finais = comparar_cenarios_e_formatar(dados_iniciais)
            
            if resultados_finais is None:
                 erro = "Erro ao processar os dados. Verifique se todos os campos estão preenchidos corretamente."

        except Exception as e:
            # Captura qualquer erro inesperado durante o cálculo
            erro = f"Ocorreu um erro inesperado durante a simulação. Erro técnico: {e}"
            print(f"Erro no processamento: {e}")
            
        contexto = {
            'titulo': 'ImobCalc - Simulador Financeiro Completo',
            'dados_iniciais': dados_iniciais, # Usa os dados submetidos
            'resumo_comparativo': resultados_finais,
            'erro': erro
        }
        
        # 3. ESTE É O RETURN CORRETO PARA O POST.
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