"""
Wizard V2 - Formulários Reorganizados com Foco em Personalização
Estrutura otimizada baseada no perfil e objetivos do usuário
"""

from django import forms
from decimal import Decimal



# ============================================================================
# CLASSE BASE PARA FORMULÁRIOS DO WIZARD
# ============================================================================
class BaseWizardForm(forms.Form):
    """Classe base que lida com a injeção de wizard_data"""
    def __init__(self, *args, **kwargs):
        self.wizard_data = kwargs.pop('wizard_data', {})
        super().__init__(*args, **kwargs)


# ============================================================================
# ETAPA 1: PERFIL & OBJETIVOS
# ============================================================================
class WizardPerfilObjetivosForm(BaseWizardForm):
    """Quem você é e o que busca?"""
    
    perfil_usuario = forms.ChoiceField(
        label="Qual o seu perfil?",
        choices=[
            ('comprador_morar', '🏠 Comprador - Quero morar no imóvel'),
            ('investidor', '💼 Investidor - Quero alugar/revender'),
            ('corretor', '🏢 Corretor de imóveis - Orientar clientes'),
            ('vendedor_consorcio', '🎲 Vendedor de consórcio - Mostrar viabilidade'),
            ('explorando', '📊 Só estou explorando possibilidades'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='comprador_morar',
        help_text="🎯 Isso vai personalizar as recomendações para você"
    )
    
    prioridade_principal = forms.ChoiceField(
        label="O que é mais importante pra você?",
        choices=[
            ('pagar_menos', '💰 Pagar o menor valor total (economia máxima)'),
            ('parcelas_suaves', '📉 Prestações mais suaves (cabe no bolso)'),
            ('quitar_rapido', '⏱️ Quitar rápido (menor prazo possível)'),
            ('flexibilidade', '🔄 Flexibilidade (poder trocar/vender facilmente)'),
            ('equilibrio', '⚖️ Equilíbrio (bom custo-benefício geral)'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='equilibrio',
        help_text="💡 Vamos destacar a melhor opção baseada nisso"
    )
    
    onde_mora_atualmente = forms.ChoiceField(
        label="Onde você mora atualmente?",
        choices=[
            ('aluga', 'Aluga imóvel'),
            ('pais', 'Mora com pais/parentes (sem aluguel)'),
            ('proprio', 'Tem imóvel próprio'),
            ('favor', 'Mora de favor/cedido'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='aluga',
        help_text="🏠 Importante para calcular seus gastos atuais"
    )
    
    aluguel_atual = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Quanto você paga de aluguel por mês? (R$)",
        required=False,
        initial=Decimal('1500.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'class': 'form-control currency-input',
            'placeholder': '1.500,00'
        }),
        help_text="💡 Se não paga aluguel, deixe em branco ou zero"
    )
    
    tempo_mora_atualmente = forms.ChoiceField(
        label="Há quanto tempo mora no imóvel atual?",
        choices=[
            ('menos_1', 'Menos de 1 ano'),
            ('1_3', '1-3 anos'),
            ('3_5', '3-5 anos'),
            ('5_10', '5-10 anos'),
            ('mais_10', 'Mais de 10 anos'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='1_3',
        help_text="📍 Ajuda a prever estabilidade"
    )


# ============================================================================
# ETAPA 2: TRABALHO & RENDA
# ============================================================================
class WizardTrabalhoRendaForm(BaseWizardForm):
    """Sua situação profissional e renda"""
    
    renda_familiar_bruta = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Renda Familiar CLT/Formal (R$)",
        required=True,
        initial=Decimal('8000.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '1000',
            'class': 'form-control currency-input',
            'placeholder': '8.000,00'
        }),
        help_text="💼 Salário com carteira assinada + aposentadoria (gera FGTS e conta 100% para financiamento)"
    )
    
    tipo_contrato = forms.ChoiceField(
        label="Qual seu tipo de contrato?",
        choices=[
            ('clt', 'CLT (carteira assinada)'),
            ('autonomo', 'Autônomo/PJ'),
            ('empresario', 'Empresário'),
            ('aposentado', 'Aposentado'),
            ('outro', 'Outro'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='clt',
        help_text="📋 Afeta acesso a crédito e FGTS"
    )
    
    renda_estavel = forms.ChoiceField(
        label="Sua renda é estável?",
        choices=[
            ('muito_estavel', 'Muito estável (público)'),
            ('estavel', 'Estável (CLT consolidado)'),
            ('moderada', 'Moderadamente estável (pode variar ±20%)'),
            ('instavel', 'Instável (varia bastante)'),
            ('recente', 'Recém começou'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='estavel',
        help_text="📊 Afeta risco do investimento"
    )
    
    recebe_13_salario = forms.BooleanField(
        label="Recebe 13º salário?",
        required=False,
        initial=True,
        help_text="🎁 Usamos isso para calcular renda anual real"
    )
    
    quantos_dependentes = forms.IntegerField(
        label="Quantos dependentes? (0 se nenhum)",
        required=False,
        initial=1,
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'min': '0',
            'max': '10',
            'class': 'form-control',
            'placeholder': '1'
        }),
        help_text="📊 Incluindo você mesmo"
    )
    
    outras_rendas = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Outras Rendas Comprovadas (R$)",
        required=False,
        initial=Decimal('0.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'class': 'form-control currency-input',
            'placeholder': '0,00'
        }),
        help_text="💰 Aluguéis, autônomo, pensão alimentícia (bancos aceitam com desconto de 25% no cálculo)"
    )


# ============================================================================
# ETAPA 3: FINANÇAS ATUAIS
# ============================================================================
class WizardFinancasAtuaisForm(BaseWizardForm):
    """Seu patrimônio e gastos"""
    
    valor_imovel_proprio = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Valor do seu imóvel próprio (R$ 0 se não tiver)",
        required=False,
        initial=Decimal('0.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'class': 'form-control currency-input',
            'placeholder': '0,00'
        }),
        help_text="💡 Use valores de mercado ou avaliação"
    )
    
    saldo_dinheiro_guardado = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Quanto você tem guardado? (R$)",
        required=True,
        initial=Decimal('50000.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'class': 'form-control currency-input',
            'placeholder': '50.000,00'
        }),
        help_text="💰 Poupança, CDB, Tesouro, ações, etc. (total disponível)"
    )
    
    saldo_fgts = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Saldo de FGTS disponível? (R$)",
        required=False,
        initial=Decimal('0.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'class': 'form-control currency-input',
            'placeholder': '0,00'
        }),
        help_text="💼 Consulte em www.caixa.gov.br (só CLT)"
    )
    
    despesas_mensais_fixas = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Outras despesas mensais fixas (R$)",
        required=False,
        initial=Decimal('2000.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'class': 'form-control currency-input',
            'placeholder': '2.000,00'
        }),
        help_text="🛒 Alimentação, energia, água, transporte, escola, etc. (não incluir aluguel)"
    )


# ============================================================================
# ETAPA 4: IMÓVEL DESEJADO
# ============================================================================
class WizardImovelDesejadoForm(BaseWizardForm):
    """Características do imóvel que você quer"""
    
    valor_imovel_desejado = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Qual o valor do imóvel que deseja? (R$)",
        required=True,
        initial=Decimal('500000.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '50000',
            'max': '20000000',
            'class': 'form-control currency-input',
            'placeholder': '500.000,00'
        }),
        help_text="🏠 Use preço de mercado na região desejada"
    )
    
    # CAMPO REMOVIDO: regiao_imovel
    # Motivo: Não está sendo usado para buscar valores de mercado
    # TODO: Implementar integração com API de preços de imóveis no futuro
    # regiao_imovel = forms.CharField(
    #     max_length=100,
    #     label="Onde quer morar/comprar?",
    #     required=False,
    #     initial='São Paulo - SP',
    #     widget=forms.TextInput(attrs={
    #         'class': 'form-control',
    #         'placeholder': 'Digite a cidade'
    #     }),
    #     help_text="📍 Digite a cidade desejada"
    # )
    
    prazo_desejado_anos = forms.IntegerField(
        label="Em quantos anos quer pagar o financiamento?",
        required=True,
        initial=30,
        min_value=5,
        max_value=40,
        widget=forms.NumberInput(attrs={
            'min': '5',
            'max': '40',
            'class': 'form-control',
            'placeholder': '30'
        }),
        help_text="🏦 Prazo padrão: 30 anos (360 meses). Quanto maior o prazo, menor a parcela, mas mais juros"
    )
    
    custas_documentacao_forma = forms.ChoiceField(
        label="Como vai pagar as custas de documentação? (~R$ 15.000)",
        required=True,
        choices=[
            ('a_vista', 'À vista (precisa ter na entrada)'),
            ('financiado', 'Financiado (aumenta parcela ~R$ 120/mês)'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='financiado',
        help_text="💰 ITBI + Registro + Escritura + Avaliação + Seguro"
    )
    
    # Init herdado de BaseWizardForm funciona aqui sem precisar sobrescrever explicitamente, 
    # pois ele já faz o que tinha antes: captura wizard_data e chama super().
    
    def clean(self):
        cleaned_data = super().clean()
        valor_imovel = cleaned_data.get('valor_imovel_desejado')
        
        # Pegar dados das etapas anteriores (acessando os dicionários corretos)
        trabalho_renda = self.wizard_data.get('trabalho_renda', {})
        financas = self.wizard_data.get('financas_atuais', {})
        
        # Converter para Decimal pois dados da sessão vêm como float
        renda_bruta = Decimal(str(trabalho_renda.get('renda_familiar_bruta', '0')))
        capital_guardado = Decimal(str(financas.get('saldo_dinheiro_guardado', '0')))
        saldo_fgts = Decimal(str(financas.get('saldo_fgts', '0')))
        
        if valor_imovel and renda_bruta:
            # Validação entrada mínima
            entrada_minima = valor_imovel * Decimal('0.20')
            capital_total_disponivel = capital_guardado + saldo_fgts
            
            if capital_total_disponivel < entrada_minima:
                faltam = entrada_minima - capital_total_disponivel
                self.add_error('valor_imovel_desejado', 
                    f"⚠️ Atenção: Para este imóvel, você precisa de pelo menos R$ {entrada_minima:,.2f} de entrada (20%). "
                    f"Você tem R$ {capital_guardado:,.2f} guardado + R$ {saldo_fgts:,.2f} FGTS = R$ {capital_total_disponivel:,.2f} total. "
                    f"Faltam R$ {faltam:,.2f}. Considere o cenário 'Guardar Dinheiro' para juntar a diferença."
                )
        
        return cleaned_data


# ============================================================================
# ETAPA 5: CENÁRIOS A COMPARAR
# ============================================================================
class WizardCenariosForm(BaseWizardForm):
    """Quais cenários quer comparar?"""
    
    comparar_financiamento_price = forms.BooleanField(
        label="Financiamento PRICE (parcelas iguais)",
        required=False,
        initial=True,
        help_text="✓ Parcelas fixas, mais previsíveis"
    )
    
    comparar_financiamento_sac = forms.BooleanField(
        label="Financiamento SAC (parcelas decrescentes)",
        required=False,
        initial=True,
        help_text="✓ Parcelas caem com o tempo, menos juros"
    )
    
    comparar_consorcio = forms.BooleanField(
        label="Consórcio",
        required=False,
        initial=True,
        help_text="✓ Sem juros, parcelas fixas, risco de sorteio"
    )
    
    # Detalhes do Consórcio (aparecem se comparar_consorcio = True)
    prazo_consorcio = forms.ChoiceField(
        label="Prazo do grupo de consórcio",
        choices=[
            ('120', '10 anos (120 meses)'),
            ('150', '12,5 anos (150 meses)'),
            ('180', '15 anos (180 meses)'),
            ('200', '16,6 anos (200 meses)'),
        ],
        required=False,
        initial='180',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        help_text="📅 Grupos mais longos = parcelas menores, mas mais taxa de administração"
    )
    
    estrategia_contemplacao = forms.ChoiceField(
        label="Como pretende ser contemplado?",
        choices=[
            ('sorteio', '🎲 Apenas sorteio (sem lance) - Tempo médio: 50% do prazo'),
            ('lance_unico', '💰 Lance único (quando tiver o valor) - Contemplação garantida'),
            ('lances_mensais', '📈 Lances mensais (acelerar contemplação) - Mais rápido'),
        ],
        required=False,
        initial='sorteio',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        help_text="🎯 Lances aumentam muito a chance de contemplação rápida"
    )
    
    valor_lance_disponivel = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Quanto tem disponível para lance? (R$)",
        required=False,
        initial=Decimal('0.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'class': 'form-control currency-input',
            'placeholder': '0,00'
        }),
        help_text="💵 Pode usar FGTS ou dinheiro guardado. Lance de 30-40% geralmente contempla rápido"
    )
    
    tempo_maximo_espera_consorcio = forms.IntegerField(
        label="Em quanto tempo PRECISA do imóvel? (meses)",
        required=False,
        initial=36,
        min_value=1,
        max_value=240,
        widget=forms.NumberInput(attrs={
            'min': '1',
            'max': '240',
            'class': 'form-control',
            'placeholder': '36'
        }),
        help_text="⏱️ Ajuda a calcular se consórcio é viável para seu prazo"
    )
    
    comparar_mcmv = forms.BooleanField(
        label="Minha Casa Minha Vida (MCMV)",
        required=False,
        initial=False,
        help_text="🏠 Subsídios e taxas reduzidas (se elegível)"
    )
    
    comparar_aluguel_investimento = forms.BooleanField(
        label="Continuar alugando + Investir diferença",
        required=False,
        initial=True,
        help_text="✓ Pagar aluguel e deixar dinheiro trabalhar"
    )
    
    comparar_compra_a_vista = forms.BooleanField(
        label="Compra à vista + Investir sobra",
        required=False,
        initial=False,
        help_text="✓ Apenas se o seu dinheiro guardado cobre o valor do imóvel"
    )
    
    comparar_guardar_dinheiro = forms.BooleanField(
        label="Guardar dinheiro até completar o valor",
        required=False,
        initial=True,
        help_text="💰 Investir e esperar acumular o valor total do imóvel"
    )
    
    pagar_aluguel_com_rendimentos = forms.BooleanField(
        label="Pagar aluguel com os rendimentos do investimento?",
        required=False,
        initial=False,
        help_text="💡 Se marcado, os rendimentos do investimento serão usados para pagar o aluguel"
    )
    
    usar_fgts = forms.BooleanField(
        label="Considerar uso de FGTS para amortização?",
        required=False,
        initial=True,
        help_text="🏦 Amortiza a cada 2 anos, reduz prazo"
    )
    
    taxa_investimento_esperada = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        label="Taxa de retorno esperada do investimento (% a.a.)",
        required=False,
        initial=Decimal('9.50'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'max': '50',
            'class': 'form-control',
            'placeholder': '9.50'
        }),
        help_text="📈 Poupança ~6%, CDB ~12%, Ações ~15%+ (com risco)"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Pegar dados das etapas anteriores (acessando os dicionários corretos)
        trabalho_renda = self.wizard_data.get('trabalho_renda', {})
        imovel_desejado = self.wizard_data.get('imovel_desejado', {})
        financas = self.wizard_data.get('financas_atuais', {})
        
        # Converter para Decimal pois dados da sessão vêm como float
        renda_bruta = Decimal(str(trabalho_renda.get('renda_familiar_bruta', '0')))
        valor_imovel = Decimal(str(imovel_desejado.get('valor_imovel_desejado', '0')))
        capital_guardado = Decimal(str(financas.get('saldo_dinheiro_guardado', '0')))
        saldo_fgts = Decimal(str(financas.get('saldo_fgts', '0')))
        tipo_contrato = trabalho_renda.get('tipo_contrato', '')
        
        # Validação: FGTS apenas para CLT
        usar_fgts = cleaned_data.get('usar_fgts')
        if usar_fgts and tipo_contrato != 'clt':
            # Debug para entender o erro se persistir
            # print(f"DEBUG: tipo_contrato={tipo_contrato} (esperado 'clt')")
            self.add_error('usar_fgts', 
                "⚠️ FGTS só está disponível para trabalhadores CLT (carteira assinada). "
                "Seu tipo de contrato não permite uso de FGTS."
            )
        
        # Validação: Lance de consórcio >= 10%
        comparar_consorcio = cleaned_data.get('comparar_consorcio')
        valor_lance = cleaned_data.get('valor_lance_disponivel', Decimal('0'))
        estrategia = cleaned_data.get('estrategia_contemplacao', '')
        
        if comparar_consorcio and estrategia in ['lance_unico', 'lances_mensais']:
            if valor_lance and valor_imovel:
                percentual_lance = (valor_lance / valor_imovel) * 100
                if percentual_lance < 10:
                    self.add_error('valor_lance_disponivel',
                        f"⚠️ Lance muito baixo ({percentual_lance:.1f}%). "
                        f"Lances abaixo de 10% raramente são contemplados. "
                        f"Mínimo recomendado: R$ {(valor_imovel * Decimal('0.10')):,.2f}"
                    )
        
        # Validação: Pelo menos um cenário selecionado
        cenarios_selecionados = [
            cleaned_data.get('comparar_financiamento_price'),
            cleaned_data.get('comparar_financiamento_sac'),
            cleaned_data.get('comparar_mcmv'),
            cleaned_data.get('comparar_consorcio'),
            cleaned_data.get('comparar_aluguel_investimento'),
            cleaned_data.get('comparar_compra_a_vista'),
            cleaned_data.get('comparar_guardar_dinheiro'),
        ]
        
        if not any(cenarios_selecionados):
            raise forms.ValidationError(
                "⚠️ Selecione pelo menos um cenário para comparar!"
            )
        
        return cleaned_data
