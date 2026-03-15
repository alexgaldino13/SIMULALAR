# simulacao/wizard_forms_novo.py
"""
Novos formulários do wizard - estruturados para ser didáticos e realistas
"""

from django import forms
from decimal import Decimal


# Lista completa de cidades brasileiras por estado
CIDADES_BRASIL = [
    # São Paulo
    "São Paulo - SP", "Guarulhos - SP", "Campinas - SP", "Santo André - SP",
    "São Bernardo do Campo - SP", "Osasco - SP", "Mauá - SP", "Sorocaba - SP",
    "Jundiaí - SP", "Santos - SP", "Ribeirão Preto - SP", "Piracicaba - SP",
    "Araraquara - SP", "Bauru - SP", "Botucatu - SP", "Marília - SP",
    "São José dos Campos - SP", "Praia Grande - SP", "Cubatão - SP",
    "Diadema - SP", "Carapicuíba - SP", "Itapevi - SP", "Taboão da Serra - SP",
    "Embu das Artes - SP", "Itaquaquecetuba - SP", "Suzano - SP",
    
    # Rio de Janeiro
    "Rio de Janeiro - RJ", "Niterói - RJ", "Duque de Caxias - RJ", "Nova Iguaçu - RJ",
    "São Gonçalo - RJ", "Volta Redonda - RJ", "Petrópolis - RJ", "Teresópolis - RJ",
    "Itaboraí - RJ", "Mesquita - RJ", "Nilópolis - RJ", "Seropédica - RJ",
    "Queimados - RJ", "Maricá - RJ", "Rio das Ostras - RJ", "Cabo Frio - RJ",
    "Araruama - RJ", "Macaé - RJ", "Campos dos Goytacazes - RJ",
    
    # Minas Gerais
    "Belo Horizonte - MG", "Contagem - MG", "Betim - MG", "Montes Claros - MG",
    "Juiz de Fora - MG", "Uberlândia - MG", "Divinópolis - MG", "Ipatinga - MG",
    "Governador Valadares - MG", "Viçosa - MG", "Uberaba - MG", "Sete Lagoas - MG",
    "Teófilo Otoni - MG", "Barbacena - MG", "Patos de Minas - MG", "Poços de Caldas - MG",
    "Varginha - MG", "Três Corações - MG", "Lavras - MG", "São João del Rei - MG",
    
    # Bahia
    "Salvador - BA", "Feira de Santana - BA", "Vitória da Conquista - BA",
    "Camaçari - BA", "Jequié - BA", "Ilhéus - BA", "Itabuna - BA", "Lauro de Freitas - BA",
    "Valéncia - BA", "Barreiras - BA", "Santo Estêvão - BA",
    
    # Ceará
    "Fortaleza - CE", "Caucaia - CE", "Maracanaú - CE", "Maranguape - CE",
    "Sobral - CE", "Juazeiro do Norte - CE", "Crato - CE", "Iguatu - CE",
    "Quixadá - CE", "Itapipoca - CE",
    
    # Pará
    "Belém - PA", "Ananindeua - PA", "Santarém - PA", "Marabá - PA",
    "Castanhal - PA", "Bragança - PA", "Tucuruí - PA", "Parauapebas - PA",
    
    # Amazonas
    "Manaus - AM", "Itacoatiara - AM", "Parintins - AM", "Coari - AM",
    "Maués - AM", "Taboca do Amazonas - AM",
    
    # Paraná
    "Curitiba - PR", "Londrina - PR", "Maringá - PR", "Cascavel - PR",
    "Ponta Grossa - PR", "Guarapuava - PR", "Paranaguá - PR", "Apucarana - PR",
    "Araçatuba - PR", "Cambé - PR", "Cornélio Procópio - PR",
    
    # Pernambuco
    "Recife - PE", "Jaboatão dos Guararapes - PE", "Olinda - PE", "Caruaru - PE",
    "Petrolina - PE", "Paulista - PE", "Goiana - PE", "Vitória de Santo Antão - PE",
    "Garanhuns - PE", "São Lourenço da Mata - PE",
    
    # Rio Grande do Sul
    "Porto Alegre - RS", "Caxias do Sul - RS", "Pelotas - RS", "Santa Maria - RS",
    "Gravataí - RS", "Viamão - RS", "Novo Hamburgo - RS", "São Leopoldo - RS",
    "Sapucaia do Sul - RS", "Alvorada - RS", "Cachoeirinha - RS", "Esteio - RS",
    "Campo Bom - RS", "Dois Irmãos - RS", "Igrejinha - RS",
    
    # Goiás
    "Goiânia - GO", "Aparecida de Goiânia - GO", "Anápolis - GO", "Abadia de Goiás - GO",
    "Novo Gama - GO", "Senador Canedo - GO", "Formosa - GO", "Cidade Ocidental - GO",
    "Planaltina - GO", "Brazabrantes - GO",
    
    # Distrito Federal
    "Brasília - DF",
    
    # Espírito Santo
    "Vitória - ES", "Vila Velha - ES", "Serra - ES", "Cariacica - ES",
    "Linhares - ES", "Cachoeiro de Itapemirim - ES", "Colatina - ES", "Aracruz - ES",
    "Marataízes - ES", "Conceição da Barra - ES",
    
    # Santa Catarina
    "Joinville - SC", "Blumenau - SC", "Florianópolis - SC", "Brusque - SC",
    "Itajaí - SC", "Chapecó - SC", "Criciúma - SC", "Lages - SC",
    "Jaraguá do Sul - SC", "Camboriú - SC", "Cambé - SC", "Balneário Camboriú - SC",
    
    # Mato Grosso
    "Cuiabá - MT", "Várzea Grande - MT", "Rondonópolis - MT", "Sinop - MT",
    "Lucas do Rio Verde - MT", "Tangará da Serra - MT", "Cáceres - MT", "Barra do Garças - MT",
    
    # Mato Grosso do Sul
    "Campo Grande - MS", "Dourados - MS", "Três Lagoas - MS", "Corumbá - MS",
    "Maracaju - MS", "Ponta Porã - MS", "Aquidauana - MS", "Nova Andradina - MS",
    
    # Tocantins
    "Palmas - TO", "Araguaína - TO", "Gurupi - TO",
    
    # Rondônia
    "Porto Velho - RO", "Ariquemes - RO", "Jaru - RO", "Vilhena - RO",
    
    # Acre
    "Rio Branco - AC", "Cruzeiro do Sul - AC",
    
    # Roraima
    "Boa Vista - RR", "Rorainópolis - RR",
    
    # Amapá
    "Macapá - AP", "Santana - AP",
    
    # Alagoas
    "Maceió - AL", "Arapiraca - AL", "Rio Largo - AL", "Penedo - AL",
    
    # Sergipe
    "Aracaju - SE", "Nossa Senhora do Socorro - SE", "Lagarto - SE",
    
    # Paraíba
    "João Pessoa - PB", "Campina Grande - PB", "Patos - PB", "Sousa - PB",
    "Guarabira - PB", "Bayeux - PB",
    
    # Piauí
    "Teresina - PI", "Parnaíba - PI", "Picos - PI", "Oeiras - PI",
    "Floriano - PI", "Campo Maior - PI",
    
    # Maranhão
    "São Luís - MA", "Imperatriz - MA", "Caxias - MA", "Timon - MA",
    "Codó - MA", "Balsas - MA",
]


# ============================================================================
# ETAPA 1: SITUAÇÃO ATUAL
# ============================================================================
class WizardSituacaoAtualForm(forms.Form):
    """Onde você mora agora? Quanto paga?"""
    
    onde_mora_atualmente = forms.ChoiceField(
        choices=[
            ('aluga', 'Aluga imóvel'),
            ('pais', 'Mora com pais/parentes (sem aluguel)'),
            ('proprio', 'Tem imóvel próprio'),
            ('favor', 'Mora de favor/cedido')
        ],
        label="Onde você mora atualmente?",
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='aluga',
        help_text="💡 Essa informação é importante para calcular seus gastos atuais"
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
            'class': 'form-control',
            'placeholder': '1500'
        }),
        help_text="💡 Se não paga aluguel, deixe em branco"
    )
    
    tempo_mora_atualmente = forms.ChoiceField(
        choices=[
            ('menos_1', 'Menos de 1 ano'),
            ('1_3', '1-3 anos'),
            ('3_5', '3-5 anos'),
            ('5_10', '5-10 anos'),
            ('mais_10', 'Mais de 10 anos')
        ],
        label="Há quanto tempo mora no imóvel atual?",
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=False,
        initial='1_3',
        help_text="📍 Ajuda a prever estabilidade e possibilidade de mudança"
    )


# ============================================================================
# ETAPA 2: CAPITAL DISPONÍVEL
# ============================================================================
class WizardCapitalForm(forms.Form):
    """Quanto você tem de capital para investir?"""
            
        
    
    saldo_fgts = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Saldo de FGTS disponível? (R$)",
        required=False,
        initial=Decimal('0.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'class': 'form-control',
            'placeholder': '20000'
        }),
        help_text="💼 Consulte em www.caixa.gov.br (só CLT)"
    )
    
    custas_documentacao_forma = forms.ChoiceField(
        label="Como pretende pagar as custas de documentação? (~R$ 15.000)",
        required=True,
        choices=[
            ('a_vista', 'À vista (precisa ter na entrada)'),
            ('financiado', 'Financiado (aumenta parcela ~R$ 120/mês)'),
        ],
        initial='financiado',
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
        }),
        help_text="💰 ITBI + Registro + Escritura + Avaliação + Seguro"
    )
# ============================================================================
# ETAPA 3: OBJETIVO
# ============================================================================
class WizardObjetivoForm(forms.Form):
    """O que você quer fazer? Qual o alvo?"""
    
    objetivo_principal = forms.ChoiceField(
        choices=[
            ('morar', 'Comprar imóvel para morar'),
            ('investir', 'Comprar imóvel para alugar (investimento)'),
            ('trocar', 'Trocar de imóvel (vender e comprar)'),
            ('explorar', 'Só explorar cenários')
        ],
        label="O que você quer fazer?",
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='morar',
        help_text="🎯 Ajuda a personalizar os cálculos"
    )
    
    valor_imovel_desejado = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Qual é o valor do imóvel que deseja? (R$)",
        required=True,
        initial=Decimal('500000.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '10000',
            'max': '20000000',
            'class': 'form-control',
            'placeholder': '500000'
        }),
        help_text="🏠 Use preço de mercado na região que quer morar"
    )
    
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
        help_text="🏦 Prazo padrão: 30 anos (360 meses). Quanto maior o prazo, menor a parcela, mas mais juros você paga"
    )

        # Campos para troca de imóvel (só aparecem quando objetivo_principal == 'trocar')
    valor_imovel_atual = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Qual é o valor do seu imóvel atual? (R$)",
        required=False,
        initial=Decimal('0.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'max': '20000000',
            'class': 'form-control',
            'placeholder': '300000'
        }),
        help_text="💰 Valor estimado de venda do seu imóvel atual"
    )

    divida_imovel_atual = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Quanto ainda deve no imóvel atual? (R$)",
        required=False,
        initial=Decimal('0.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'max': '20000000',
            'class': 'form-control',
            'placeholder': '0'
        }),
        help_text="💳 Se não tiver dívida, deixe em 0"
    )
    
    regiao_imovel = forms.CharField(
        max_length=100,
        label="Onde quer morar/comprar?",
        required=False,
        initial='São Paulo - SP',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a cidade',
            'list': 'cidades-lista',
        }),
        help_text="📍 Digite para buscar a cidade desejada"
    )


# ============================================================================
# ETAPA 4: RENDA & CUSTOS
# ============================================================================
class WizardRendaCustosForm(forms.Form):
    """Quanto ganha e quanto gasta?"""
    
    renda_familiar_bruta = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Renda familiar bruta mensal (R$)",
        required=True,
        initial=Decimal('8000.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'class': 'form-control',
            'placeholder': '8000'
        }),
        help_text="💵 Salário + benefícios de todos da família"
    )
    
    num_dependentes = forms.IntegerField(
        label="Quantos dependentes? (0 se nenhum)",
        required=False,
        initial=0,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'min': '0',
            'class': 'form-control'
        }),
        help_text="📊 Incluindo você mesmo"
    )
    
    outras_despesas_mensais = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Outras despesas mensais (não aluguel)? (R$)",
        required=False,
        initial=Decimal('2000.00'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'class': 'form-control',
            'placeholder': '2000'
        }),
        help_text="🛒 Alimentação, energia, água, transporte, etc."
    )
    
    tipo_contrato = forms.ChoiceField(
        choices=[
            ('clt', 'CLT (carteira assinada)'),
            ('autonomo', 'Autônomo/PJ'),
            ('empresario', 'Empresário'),
            ('aposentado', 'Aposentado'),
            ('outro', 'Outro')
        ],
        label="Qual seu tipo de contrato?",
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='clt',
        help_text="📋 Afeta acesso a crédito e FGTS"
    )
    
    tipo_renda_estavel = forms.ChoiceField(
        choices=[
            ('muito_estavel', 'Muito estável (público)'),
            ('estavel', 'Estável (CLT consolidado)'),
            ('moderada', 'Moderadamente estável (pode variar ±20%)'),
            ('instavel', 'Instável (varia bastante)'),
            ('recente', 'Recém começou')
        ],
        label="Sua renda é estável?",
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='estavel',
        help_text="📈 Afeta risco do investimento"
    )


# ============================================================================
# ETAPA 5: CENÁRIOS
# ============================================================================
class WizardCenariosForm(forms.Form):
    """Qual cenário você quer comparar?"""
    
    def __init__(self, *args, **kwargs):
        self.wizard_data = kwargs.pop('wizard_data', {})
        super().__init__(*args, **kwargs)

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
    
    comparar_mcmv = forms.BooleanField(
        label="Minha Casa Minha Vida (MCMV)",
        required=False,
        initial=False,
        help_text="🏠 Subsídios e taxas reduzidas (se elegível)"
    )
    
    comparar_consorcio = forms.BooleanField(
        label="Consórcio",
        required=False,
        initial=True,
        help_text="✓ Sem juros, parcelas fixas, risco de sorteio"
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
        help_text="✓ Se tiver dinheiro suficiente"
    )
    
    comparar_guardar_dinheiro = forms.BooleanField(
        label="Guardar dinheiro até completar o valor",
        required=False,
        initial=True,
        help_text="✓ Investir + aportes mensais até juntar o valor total"
    )
    
    usar_fgts = forms.BooleanField(
        label="Considerar uso de FGTS para amortização?",
        required=False,
        initial=True,
        help_text="💼 Amortiza a cada 2 anos, reduz prazo"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Pegar dados das etapas anteriores
        renda_custos = self.wizard_data.get('renda_custos', {})
        capital = self.wizard_data.get('capital', {})
        objetivo = self.wizard_data.get('objetivo', {})
        
        renda_bruta = Decimal(str(renda_custos.get('renda_familiar_bruta') or 0))
        valor_imovel = Decimal(str(objetivo.get('valor_imovel_desejado') or 0))
        capital_guardado = Decimal(str(capital.get('saldo_dinheiro_guardado') or 0))
        saldo_fgts = Decimal(str(capital.get('saldo_fgts') or 0))
        tipo_contrato = renda_custos.get('tipo_contrato', '')
        
        # Validação 1: FGTS apenas para CLT
        usar_fgts = cleaned_data.get('usar_fgts')
        if usar_fgts:
            if tipo_contrato != 'clt':
                self.add_error('usar_fgts', 
                    "⚠️ FGTS só está disponível para trabalhadores CLT (carteira assinada). "
                    "Seu tipo de contrato não permite uso de FGTS."
                )
            
            # Validação SFH: Limite de 1.5M para uso de FGTS
            if valor_imovel > Decimal('1500000'):
                self.add_error('usar_fgts',
                    "⚠️ Pelas regras do SFH (Sistema Financeiro da Habitação), "
                    "o uso do FGTS só é permitido para imóveis avaliados em até R$ 1.500.000,00."
                )
            
        # Validação 2: Entrada Mínima de 20% para Financiamento
        quer_financiamento = cleaned_data.get('comparar_financiamento_price') or cleaned_data.get('comparar_financiamento_sac')
        
        if quer_financiamento and valor_imovel > 0:
            entrada_total = capital_guardado + saldo_fgts
            entrada_minima = valor_imovel * Decimal('0.20')
            
            if entrada_total < entrada_minima:
                faltam = entrada_minima - entrada_total
                msg_erro = (
                    f"⚠️ Entrada insuficiente para Financiamento. "
                    f"O banco exige no mínimo 20% (R$ {entrada_minima:,.2f}). "
                    f"Você tem R$ {entrada_total:,.2f} (Dinheiro + FGTS). "
                    f"Faltam R$ {faltam:,.2f}. "
                    f"Desmarque as opções de Financiamento e tente 'Consórcio' ou 'Guardar Dinheiro'."
                )
                if cleaned_data.get('comparar_financiamento_price'):
                    self.add_error('comparar_financiamento_price', msg_erro)
                if cleaned_data.get('comparar_financiamento_sac'):
                    self.add_error('comparar_financiamento_sac', msg_erro)

        return cleaned_data

    taxa_investimento_esperada = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        label="Taxa de retorno esperada do investimento (% a.a.)",
        required=True,
        initial=Decimal('9.50'),
        min_value=Decimal('0.5'),
        max_value=Decimal('30'),
        widget=forms.NumberInput(attrs={
            'step': '0.5',
            'min': '0.5',
            'max': '30',
            'class': 'form-control'
        }),
        help_text="📊 Poupança ~6%, CDB ~12%, Ações ~15%+ (com risco)"
    )
