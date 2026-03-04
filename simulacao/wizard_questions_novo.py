"""
NOVO WIZARD - Estrutura didática e realista para simulação imobiliária

Flow:
1. Situação Atual (onde mora, aluguel, patrimônio)
2. Capital Disponível (guardado, FGTS, 13º, etc)
3. Objetivo (imóvel alvo, prazo, location)
4. Renda & Custos (renda familiar, despesas)
5. Seleção de Cenários (qual quer comparar)
6. Resultado (tabela comparativa)
"""

from typing import Dict, Any, List

# ============================================================================
# ETAPA 1: SITUAÇÃO ATUAL
# ============================================================================
ETAPA_1_SITUACAO_ATUAL = [
    {
        'key': 'onde_mora_atualmente',
        'label': 'Onde você mora atualmente?',
        'type': 'choice',
        'options': [
            'Aluga imóvel',
            'Mora com pais/parentes (sem aluguel)',
            'Tem imóvel próprio',
            'Mora de favor/cedido'
        ],
        'default': 'Aluga imóvel',
        'required': True,
        'help': '💡 Essa informação é importante para calcular seus gastos atuais'
    },
    {
        'key': 'aluguel_atual',
        'label': 'Quanto você paga de aluguel por mês? (R$)',
        'type': 'money',
        'default': 1500,
        'min': 0,
        'placeholder': '1500',
        'help': '💡 Se não paga aluguel, deixe em branco',
        'visible_if': {'onde_mora_atualmente': 'Aluga imóvel'}
    },
    {
        'key': 'tempo_mora_atualmente',
        'label': 'Há quanto tempo mora no imóvel atual?',
        'type': 'choice',
        'options': [
            'Menos de 1 ano',
            '1-3 anos',
            '3-5 anos',
            '5-10 anos',
            'Mais de 10 anos'
        ],
        'default': '1-3 anos',
        'required': False,
        'help': '📍 Ajuda a prever estabilidade e possibilidade de mudança'
    }
]

# ============================================================================
# ETAPA 2: CAPITAL DISPONÍVEL
# ============================================================================
ETAPA_2_CAPITAL = [
    {
        'key': 'tem_imovel_proprio',
        'label': 'Você tem algum imóvel próprio?',
        'type': 'bool',
        'default': False,
        'help': '🏠 Incluir imóvel alugado ou que mora'
    },
    {
        'key': 'valor_imovel_proprio',
        'label': 'Qual é o valor estimado do seu imóvel? (R$)',
        'type': 'money',
        'default': 0,
        'min': 0,
        'placeholder': '500000',
        'help': '💡 Use valores de mercado ou avaliação de imobiliária',
        'visible_if': {'tem_imovel_proprio': True}
    },
    {
        'key': 'saldo_dinheiro_guardado',
        'label': 'Quanto você tem guardado em poupança/investimento? (R$)',
        'type': 'money',
        'default': 50000,
        'min': 0,
        'placeholder': '50000',
        'required': True,
        'help': '💰 Poupança, CDB, Tesouro, etc. (valor total disponível)'
    },
    {
        'key': 'saldo_fgts',
        'label': 'Saldo de FGTS disponível? (R$)',
        'type': 'money',
        'default': 0,
        'min': 0,
        'placeholder': '20000',
        'help': '💼 Consulte em www.caixa.gov.br (só CLT)'
    },
    {
        'key': 'recebe_13',
        'label': 'Você recebe 13º mês (gratificação)?',
        'type': 'bool',
        'default': True,
        'help': '🎁 Afeta sua capacidade anual de investimento'
    },
    {
        'key': 'valor_13_estimado',
        'label': 'Valor estimado do 13º (R$)',
        'type': 'money',
        'default': 0,
        'min': 0,
        'placeholder': '5000',
        'visible_if': {'recebe_13': True},
        'help': '📊 Média do seu salário mensal'
    }
]

# ============================================================================
# ETAPA 3: OBJETIVO FINAL
# ============================================================================
ETAPA_3_OBJETIVO = [
    {
        'key': 'objetivo_principal',
        'label': 'O que você quer fazer?',
        'type': 'choice',
        'options': [
            'Comprar imóvel para morar',
            'Comprar imóvel para alugar (investimento)',
            'Trocar de imóvel (vender e comprar)',
            'Só explorar cenários'
        ],
        'default': 'Comprar imóvel para morar',
        'required': True,
        'help': '🎯 Ajuda a personalizar os cálculos'
    },
    {
        'key': 'valor_imovel_desejado',
        'label': 'Qual é o valor do imóvel que deseja? (R$)',
        'type': 'money',
        'default': 500000,
        'min': 10000,
        'max': 20000000,
        'placeholder': '500000',
        'required': True,
        'help': '🏠 Use preço de mercado na região que quer morar',
        'visible_if': {'objetivo_principal': ['Comprar imóvel para morar', 'Comprar imóvel para alugar (investimento)', 'Trocar de imóvel (vender e comprar)']}
    },
    {
        'key': 'prazo_desejado_anos',
        'label': 'Em quantos anos quer conseguir o imóvel?',
        'type': 'int',
        'default': 10,
        'min': 1,
        'max': 40,
        'placeholder': '10',
        'required': True,
        'help': '⏱️ Isso vai impactar significativamente a decisão',
        'visible_if': {'objetivo_principal': ['Comprar imóvel para morar', 'Comprar imóvel para alugar (investimento)']}
    },
    {
        'key': 'regiao_imovel',
        'label': 'Onde quer morar/comprar?',
        'type': 'text',
        'default': 'São Paulo',
        'placeholder': 'Cidade, estado',
        'help': '📍 Ajuda a estimar valorização'
    }
]

# ============================================================================
# ETAPA 4: RENDA E CUSTOS
# ============================================================================
ETAPA_4_RENDA_CUSTOS = [
    {
        'key': 'renda_familiar_bruta',
        'label': 'Renda familiar bruta mensal (R$)',
        'type': 'money',
        'default': 8000,
        'min': 0,
        'placeholder': '8000',
        'required': True,
        'help': '💵 Salário + benefícios de todos da família'
    },
    {
        'key': 'tem_dependentes',
        'label': 'Você tem dependentes?',
        'type': 'bool',
        'default': False,
        'help': '👨‍👩‍👧‍👦 Filhos, idosos, etc. (afeta capacidade de investimento)'
    },
    {
        'key': 'num_dependentes',
        'label': 'Quantos dependentes?',
        'type': 'int',
        'default': 1,
        'min': 1,
        'visible_if': {'tem_dependentes': True},
        'help': '📊 Incluindo você mesmo'
    },
    {
        'key': 'outras_despesas_mensais',
        'label': 'Outras despesas mensais (não aluguel)? (R$)',
        'type': 'money',
        'default': 2000,
        'min': 0,
        'placeholder': '2000',
        'help': '🛒 Alimentação, energia, água, transporte, etc.'
    },
    {
        'key': 'tipo_contrato',
        'label': 'Qual seu tipo de contrato?',
        'type': 'choice',
        'options': [
            'CLT (carteira assinada)',
            'Autônomo/PJ',
            'Empresário',
            'Aposentado',
            'Outro'
        ],
        'default': 'CLT (carteira assinada)',
        'help': '📋 Afeta acesso a crédito e FGTS'
    },
    {
        'key': 'tipo_renda_estavel',
        'label': 'Sua renda é estável?',
        'type': 'choice',
        'options': [
            'Muito estável (público)',
            'Estável (CLT consolidado)',
            'Moderadamente estável (pode variar ±20%)',
            'Instável (varia bastante)',
            'Recém começou'
        ],
        'default': 'Estável (CLT consolidado)',
        'help': '📈 Afeta risco do investimento'
    }
]

# ============================================================================
# ETAPA 5: SELEÇÃO DE CENÁRIOS
# ============================================================================
ETAPA_5_CENARIOS = [
    {
        'key': 'comparar_financiamento_price',
        'label': 'Financiamento PRICE (parcelas iguais)',
        'type': 'bool',
        'default': True,
        'help': '✓ Parcelas fixas, mais previsíveis'
    },
    {
        'key': 'comparar_financiamento_sac',
        'label': 'Financiamento SAC (parcelas decrescentes)',
        'type': 'bool',
        'default': True,
        'help': '✓ Parcelas caem com o tempo, menos juros'
    },
    {
        'key': 'comparar_consorcio',
        'label': 'Consórcio',
        'type': 'bool',
        'default': True,
        'help': '✓ Sem juros, parcelas fixas, risco de sorteio'
    },
    {
        'key': 'comparar_aluguel_investimento',
        'label': 'Continuar alugando + Investir diferença',
        'type': 'bool',
        'default': True,
        'help': '✓ Pagar aluguel e deixar dinheiro trabalhar'
    },
    {
        'key': 'comparar_compra_a_vista',
        'label': 'Compra à vista + Investir sobra',
        'type': 'bool',
        'default': False,
        'help': '✓ Se tiver dinheiro suficiente'
    },
    {
        'key': 'usar_fgts',
        'label': 'Considerar uso de FGTS para amortização?',
        'type': 'bool',
        'default': True,
        'help': '💼 Amortiza a cada 2 anos, reduz prazo'
    },
    {
        'key': 'taxa_investimento_esperada',
        'label': 'Taxa de retorno esperada do investimento (% a.a.)',
        'type': 'percent',
        'default': 9.5,
        'min': 0.5,
        'max': 30,
        'step': 0.5,
        'help': '📊 Poupança ~6%, CDB ~12%, Ações ~15%+ (com risco)'
    }
]

# ============================================================================
# MAPPING: Converter respostas em dados para cálculo
# ============================================================================

def map_answers_to_dados_form(answers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converte respostas do novo wizard em formato esperado pelos cálculos
    """
    
    # Determine onde a pessoa vai morar durante o período
    morada_durante = 'aluguel'
    if answers.get('onde_mora_atualmente') == 'Mora com pais/parentes (sem aluguel)':
        morada_durante = 'gratis'
        aluguel_durante = 0
    elif answers.get('onde_mora_atualmente') == 'Tem imóvel próprio':
        morada_durante = 'proprio'
        aluguel_durante = 0
    else:
        aluguel_durante = answers.get('aluguel_atual', 1500)
    
    # Capital inicial
    capital_inicial = answers.get('saldo_dinheiro_guardado', 0)
    fgts_saldo = answers.get('saldo_fgts', 0)
    
    # Se tem imóvel próprio, soma ao capital
    if answers.get('tem_imovel_proprio'):
        capital_inicial += answers.get('valor_imovel_proprio', 0)
    
    return {
        # Imóvel alvo
        'valor_imovel': answers.get('valor_imovel_desejado', 500000),
        'entrada': min(capital_inicial * 0.2, answers.get('valor_imovel_desejado', 500000) * 0.4),  # Entrada conservadora
        
        # Capital e renda
        'renda_familiar_bruta': answers.get('renda_familiar_bruta', 8000),
        'fgts_saldo': fgts_saldo,
        'capital_disponivel_inicial': capital_inicial,
        'aporte_mensal_possivel': (answers.get('renda_familiar_bruta', 8000) - answers.get('outras_despesas_mensais', 2000)) * 0.1,  # 10% do que sobra
        
        # Prazo
        'prazo_anos': answers.get('prazo_desejado_anos', 10),
        
        # Taxa (padrão de mercado 2025)
        'taxa_anual': 8.5,
        'taxa_investimento': answers.get('taxa_investimento_esperada', 9.5),
        
        # Morada durante
        'aluguel_durante_periodo': aluguel_durante,
        'morada_durante': morada_durante,
        
        # Configurações
        'usar_fgts': answers.get('usar_fgts', True),
        'incluir_13': answers.get('recebe_13', True),
        'valor_13': answers.get('valor_13_estimado', 0),
        
        # Cenários
        'cenarios': {
            'price': answers.get('comparar_financiamento_price', True),
            'sac': answers.get('comparar_financiamento_sac', True),
            'consorcio': answers.get('comparar_consorcio', True),
            'aluguel_investimento': answers.get('comparar_aluguel_investimento', True),
            'compra_a_vista': answers.get('comparar_compra_a_vista', False),
        }
    }


# Estrutura do wizard completo
WIZARD_STEPS = [
    {'etapa': 1, 'titulo': 'Situação Atual', 'perguntas': ETAPA_1_SITUACAO_ATUAL},
    {'etapa': 2, 'titulo': 'Capital Disponível', 'perguntas': ETAPA_2_CAPITAL},
    {'etapa': 3, 'titulo': 'Seu Objetivo', 'perguntas': ETAPA_3_OBJETIVO},
    {'etapa': 4, 'titulo': 'Renda & Custos', 'perguntas': ETAPA_4_RENDA_CUSTOS},
    {'etapa': 5, 'titulo': 'Cenários a Comparar', 'perguntas': ETAPA_5_CENARIOS},
]
