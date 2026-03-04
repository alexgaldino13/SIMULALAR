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

class InvestidorImobiliarioForm(forms.Form):
    valor_imovel = forms.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        label="Valor do Imóvel (R$)", 
        required=True
    )
    entrada = forms.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        label="Valor da Entrada (R$)", 
        required=True
    )
    taxa_juros_anual = forms.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        label="Taxa de Juros Anual (%)", 
        required=True
    )
    prazo_anos = forms.IntegerField(
        label="Prazo (anos)", 
        required=True
    )
    sistema_amortizacao = forms.ChoiceField(
        choices=[('SAC', 'SAC'), ('PRICE', 'PRICE')], 
        label="Sistema de Amortização", 
        required=True
    )
    imovel_sera_alugado = forms.BooleanField(
        label="O imóvel será alugado?", 
        required=False, 
        initial=True
    )
    valor_aluguel_mensal = forms.DecimalField(
        max_digits=10, decimal_places=2, label="Valor do Aluguel Mensal (R$)", required=False
    )
    usar_aluguel_para_prestacao = forms.BooleanField(
        label="Usar aluguel para pagar prestação?", required=False, initial=True
    )
    taxa_administracao = forms.DecimalField(
        max_digits=5, decimal_places=2, label="Taxa de Administração (%)", initial=Decimal('8.00'), required=False
    )
    taxa_vacancia = forms.DecimalField(
        max_digits=5, decimal_places=2, label="Taxa de Vacância (%)", initial=Decimal('5.00'), required=False
    )
    iptu_mensal = forms.DecimalField(
        max_digits=10, decimal_places=2, label="IPTU Mensal (R$)", required=False, initial=Decimal('0.00')
    )
    condominio_mensal = forms.DecimalField(
        max_digits=10, decimal_places=2, label="Condomínio Mensal (R$)", required=False, initial=Decimal('0.00')
    )