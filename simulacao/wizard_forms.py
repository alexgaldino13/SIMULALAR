# simulacao/wizard_forms.py
"""
Forms para o sistema Wizard (multi-step form)
Cada etapa do wizard tem seu próprio form
"""

from django import forms
from decimal import Decimal


# ============================================================================
# ETAPA 1: PERFIL DO USUÁRIO
# ============================================================================

class WizardPerfilForm(forms.Form):
    """Etapa 1: Identifica o perfil do usuário"""
    
    PERFIL_CHOICES = (
        ('comprador', 'Sou Comprador/Interessado'),
        ('corretor', 'Sou Corretor de Imóveis'),
        ('vendedor', 'Sou Vendedor de Consórcio'),
        ('banco', 'Sou do Banco/Financeira'),
        ('outro', 'Outro'),
    )
    
    perfil = forms.ChoiceField(
        choices=PERFIL_CHOICES,
        label="Quem é você?",
        widget=forms.RadioSelect,
        required=True,
        initial='comprador'
    )
    
    nome = forms.CharField(
        max_length=100,
        label="Seu nome (opcional)",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Nome para personalização'})
    )


# ============================================================================
# ETAPA 0 (NOVA): CONSENTIMENTO / PRIVACIDADE / IA
# ============================================================================


class WizardPrivacyForm(forms.Form):
    """Etapa inicial: consentimentos rápidos e preferências de IA"""

    aceitar_privacidade = forms.BooleanField(
        label="Aceito os termos de privacidade e uso de dados (necessário)",
        required=True,
        initial=False,
        help_text="Permite que os dados fornecidos sejam usados localmente para simulações."
    )

    permitir_ia = forms.BooleanField(
        label="Permitir sugestões automáticas (IA)",
        required=False,
        initial=True,
        help_text="Ativa dicas automáticas e sugestões de cenário usando IA local/servidor."
    )

    receber_publicidade = forms.BooleanField(
        label="Aceito receber ofertas e publicidade (opcional)",
        required=False,
        initial=False,
        help_text="Ajuda a monetizar a versão gratuita via anúncios."
    )


# ============================================================================
# ETAPA 2: DADOS DO IMÓVEL
# ============================================================================

class WizardImovelForm(forms.Form):
    """Etapa 2: Dados básicos do imóvel e recursos"""
    
    valor_imovel = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Valor do Imóvel (R$)",
        required=True,
        initial=Decimal('300000.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'class': 'form-control'
        }),
        help_text="Valor total do imóvel que deseja adquirir"
    )
    
    entrada = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Valor da Entrada (R$)",
        required=True,
        initial=Decimal('60000.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'class': 'form-control'
        }),
        help_text="Valor que você tem disponível para entrada"
    )
    
    fgts_saldo = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Saldo FGTS Disponível (R$)",
        required=False,
        initial=Decimal('0.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'class': 'form-control'
        }),
        help_text="Saldo disponível no FGTS (pode usar na entrada ou como lance)"
    )


# ============================================================================
# ETAPA 3: MÉTODOS DE INTERESSE
# ============================================================================

class WizardMetodosForm(forms.Form):
    """Etapa 3: Seleção de métodos para comparar"""
    
    comparar_price = forms.BooleanField(
        label="Financiamento PRICE",
        required=False,
        initial=True,
        help_text="Parcelas fixas durante todo o período"
    )
    
    comparar_sac = forms.BooleanField(
        label="Financiamento SAC",
        required=False,
        initial=True,
        help_text="Parcelas decrescentes (amortização constante)"
    )
    
    comparar_consorcio = forms.BooleanField(
        label="Consórcio",
        required=False,
        initial=True,
        help_text="Parcelas fixas, contemplação por sorteio ou lance"
    )
    
    comparar_guardar_dinheiro = forms.BooleanField(
        label="Guardar Dinheiro (Investimento)",
        required=False,
        initial=True,
        help_text="Investir o valor em poupança, CDB, Tesouro, etc."
    )
    
    comparar_aluguel_investimento = forms.BooleanField(
        label="Aluguel + Investimento",
        required=False,
        initial=False,
        help_text="Alugar e investir a diferença"
    )
    
    def clean(self):
        """Garante que pelo menos um método foi selecionado"""
        cleaned_data = super().clean()
        metodos_selecionados = [
            cleaned_data.get('comparar_price'),
            cleaned_data.get('comparar_sac'),
            cleaned_data.get('comparar_consorcio'),
            cleaned_data.get('comparar_guardar_dinheiro'),
            cleaned_data.get('comparar_aluguel_investimento'),
        ]
        
        if not any(metodos_selecionados):
            raise forms.ValidationError(
                "Selecione pelo menos um método para comparar."
            )
        
        return cleaned_data


# ============================================================================
# ETAPA 4: PARÂMETROS DO FINANCIAMENTO
# ============================================================================

class WizardFinanciamentoForm(forms.Form):
    """Etapa 4: Parâmetros específicos do financiamento (PRICE/SAC)"""
    
    taxa_anual = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        label="Taxa de Juros Anual (%)",
        required=True,
        initial=Decimal('7.90'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'max': '30',
            'class': 'form-control'
        }),
        help_text="Taxa de juros anual do financiamento (ex: 7,90%)"
    )
    
    prazo_anos = forms.IntegerField(
        label="Prazo (anos)",
        required=True,
        initial=30,
        min_value=1,
        max_value=40,
        widget=forms.NumberInput(attrs={
            'min': '1',
            'max': '40',
            'class': 'form-control'
        }),
        help_text="Prazo total do financiamento em anos"
    )
    
    seguro_mensal = forms.DecimalField(
        max_digits=5,
        decimal_places=3,
        label="Seguro Mensal MIP/DFI (% sobre saldo devedor)",
        required=False,
        initial=Decimal('0.030'),
        widget=forms.NumberInput(attrs={
            'step': '0.001',
            'min': '0',
            'class': 'form-control'
        }),
        help_text="Percentual mensal de seguro (ex: 0,030% = 0,03%)"
    )
    
    usar_fgts_financiamento = forms.BooleanField(
        label="Usar FGTS para amortização?",
        required=False,
        initial=False,
        help_text="Amortizar o financiamento com saldo do FGTS"
    )
    
    tipo_amortizacao_fgts = forms.ChoiceField(
        choices=[
            ('reduzir_prazo', 'Reduzir o Prazo'),
            ('reduzir_parcela', 'Reduzir o Valor da Parcela'),
        ],
        label="Como usar o FGTS?",
        required=False,
        initial='reduzir_prazo',
        widget=forms.RadioSelect,
        help_text="Escolha como o FGTS será aplicado"
    )
    
    mes_uso_fgts = forms.IntegerField(
        label="Usar FGTS no mês:",
        required=False,
        initial=1,
        min_value=1,
        max_value=360,
        widget=forms.NumberInput(attrs={
            'min': '1',
            'max': '360',
            'class': 'form-control'
        }),
        help_text="Em qual mês usar o FGTS (ex: 12 = 1 ano)"
    )


# ============================================================================
# ETAPA 5: PARÂMETROS DO CONSÓRCIO
# ============================================================================

class WizardConsorcioForm(forms.Form):
    """Etapa 5: Parâmetros específicos do consórcio"""
    
    prazo_anos_consorcio = forms.IntegerField(
        label="Prazo do Consórcio (anos)",
        required=True,
        initial=15,
        min_value=5,
        max_value=30,
        widget=forms.NumberInput(attrs={
            'min': '5',
            'max': '30',
            'class': 'form-control'
        }),
        help_text="Prazo total do consórcio (geralmente 10-20 anos)"
    )
    
    taxa_adm_anual = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        label="Taxa de Administração Anual (%)",
        required=True,
        initial=Decimal('1.20'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0.5',
            'max': '3.0',
            'class': 'form-control'
        }),
        help_text="Taxa anual cobrada sobre a carta de crédito (geralmente 0,5% a 2%)"
    )
    
    fundo_reserva = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        label="Fundo de Reserva (%)",
        required=True,
        initial=Decimal('0.50'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'max': '2.0',
            'class': 'form-control'
        }),
        help_text="Percentual do fundo de reserva (geralmente 0,5% a 1,5%)"
    )
    
    lance_fgts = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Lance Inicial com FGTS (R$)",
        required=False,
        initial=Decimal('0.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'class': 'form-control'
        }),
        help_text="Valor do FGTS que deseja usar como lance inicial"
    )
    
    estrategia_lance = forms.ChoiceField(
        choices=[
            ('minimo', 'Lance Mínimo (5-10% da carta)'),
            ('medio', 'Lance Médio (20-30% da carta)'),
            ('maximo', 'Lance Máximo (50%+ da carta)'),
            ('sem_lance', 'Sem Lance (Apenas Sorteio)'),
        ],
        label="Estratégia de Lance",
        required=True,
        initial='sem_lance',
        widget=forms.RadioSelect,
        help_text="Estratégia para aumentar chances de contemplação"
    )
    
    percentual_lance_mensal = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        label="Percentual de Lance Mensal (%)",
        required=False,
        initial=Decimal('0.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'max': '50',
            'class': 'form-control'
        }),
        help_text="Percentual sobre a carta de crédito que será usado como lance mensal (ex: 5%)"
    )


# ============================================================================
# ETAPA 6: PARÂMETROS DE INVESTIMENTO (GUARDAR DINHEIRO)
# ============================================================================

class WizardInvestimentoForm(forms.Form):
    """Etapa 6: Parâmetros de investimento (Guardar Dinheiro)"""
    
    tipo_investimento = forms.ChoiceField(
        choices=[
            ('poupanca', 'Poupança (SELIC ou 0,5% + TR)'),
            ('cdb', 'CDB (90-130% do CDI)'),
            ('tesouro_ipca', 'Tesouro IPCA+ (IPCA + taxa fixa)'),
            ('lci_lca', 'LCI/LCA (85-95% do CDI, isento IR)'),
            ('outro', 'Outro (taxa personalizada)'),
        ],
        label="Tipo de Investimento",
        required=True,
        initial='cdb',
        widget=forms.RadioSelect,
        help_text="Escolha o tipo de investimento"
    )
    
    taxa_rendimento_anual = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        label="Taxa de Rendimento Anual (%)",
        required=True,
        initial=Decimal('10.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'max': '20',
            'class': 'form-control'
        }),
        help_text="Taxa anual de rendimento esperada (ajuste conforme o tipo)"
    )
    
    aporte_mensal = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Aporte Mensal (R$)",
        required=False,
        initial=Decimal('0.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'class': 'form-control'
        }),
        help_text="Valor mensal que será investido (além do valor inicial)"
    )
    
    aporte_13 = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Aporte 13º Salário (R$)",
        required=False,
        initial=Decimal('0.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'class': 'form-control'
        }),
        help_text="Valor do 13º salário que será investido anualmente"
    )


# ============================================================================
# ETAPA 7: PARÂMETROS ADICIONAIS (ALUGUEL + INVESTIMENTO)
# ============================================================================

class WizardAluguelForm(forms.Form):
    """Etapa 7 (Opcional): Parâmetros para Aluguel + Investimento"""
    
    aluguel_inicial = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        label="Aluguel Mensal Inicial (R$)",
        required=True,
        initial=Decimal('1500.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'class': 'form-control'
        }),
        help_text="Valor do aluguel mensal inicial"
    )
    
    taxa_inflacao_anual = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        label="Taxa de Inflação Anual (%)",
        required=True,
        initial=Decimal('4.50'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'max': '15',
            'class': 'form-control'
        }),
        help_text="Taxa de reajuste anual do aluguel (ex: IPCA)"
    )
    
    valorizacao_imovel_anual = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        label="Valorização do Imóvel Anual (%)",
        required=True,
        initial=Decimal('5.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'max': '20',
            'class': 'form-control'
        }),
        help_text="Taxa de valorização esperada do imóvel por ano"
    )
