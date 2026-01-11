# simulacao/forms.py

from django import forms
from decimal import Decimal

# --- CONSTANTES DE ESCOLHA ---
METODOS_CHOICES = (
    ('price', 'Financiamento - PRICE'),
    ('sac', 'Financiamento - SAC'),
    ('renda', 'Aluguel + Investimento'),
    ('consorcio', 'Consórcio'),
)

class FinanciamentoForm(forms.Form):
    # DADOS BÁSICOS DO FINANCIAMENTO
    valor_imovel = forms.DecimalField(
        max_digits=15, # Maior precisão para valores altos
        decimal_places=2, 
        label="Valor do Imóvel (R$)",
        initial=Decimal('300000.00'),
        required=True
    )
    
    valor_entrada = forms.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        label="Valor da Entrada (R$)",
        initial=Decimal('60000.00'), # 20%
        required=True
    )
    
    prazo_meses = forms.IntegerField(
        label="Prazo (meses)",
        initial=360,
        required=True
    )
    
    # TAXAS E SISTEMA
    taxa_anual = forms.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        label="Taxa Anual de Juros (%)",
        initial=Decimal('7.90'), # Ex: 7,90%
        required=True
    )
    
    metodo = forms.ChoiceField(
        choices=METODOS_CHOICES, 
        label="Método de Simulação",
        required=True
    )
    
    # DADOS ADICIONAIS (Relevantes para SAC/PRICE e Aluguel+Investimento)
    
    # Seguro (MIP + DFI) - Essencial para o cálculo do Custo Efetivo Total (CET)
    seguro_mensal = forms.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        label="Seguro Mensal (MIP/DFI - % sobre o Saldo Devedor)",
        # Este percentual varia, mas é importante para o CET
        initial=Decimal('0.03'), # Exemplo: 0,03%
        required=False 
    )

    # Aluguel Inicial (Usado na simulação Aluguel + Investimento)
    aluguel_inicial = forms.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        label="Aluguel Inicial (R$)",
        required=False, 
        initial=Decimal('1500.00')
    )
    
    # Taxa de Rendimento (Usado na simulação Aluguel + Investimento)
    taxa_rendimento_anual = forms.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        label="Taxa de Rendimento Anual do Investimento (%)",
        required=False,
        initial=Decimal('8.50')
    )

    # ... Você pode adicionar outros campos aqui como FGTS, etc.