"""
Wizard questions and mapping utilities for the simulation app.

This module contains a recommended set of ~10 installer-style questions
and a helper `map_answers_to_dados_form` that converts a user's answers
into the `dados_form` dict shape expected by `comparar_cenarios_e_formatar`.

Use this as the canonical mapping between UI wizard fields and the
calculation inputs (`simulacao/calculadora_financeira.py`).
"""

from typing import Dict, Any

# Wizard definition: list of questions shown to the user in order.
# Each item contains: key, label, type, help, default, and options (if any).
WIZARD_QUESTIONS = [
    {
        'key': 'objetivo',
        'label': 'Qual seu objetivo principal?',
        'type': 'choice',
        'options': ['Comprar imóvel', 'Consórcio', 'Investir e alugar', 'Pesquisar só'],
        'default': 'Comprar imóvel',
        'required': True,
        'help': 'Escolha o cenário que melhor descreve seu objetivo principal.'
    },
    {
        'key': 'valor_imovel',
        'label': 'Valor do imóvel (R$)',
        'type': 'money',
        'default': 300000,
        'required': True,
        'min': 10000,
        'max': 20000000,
        'placeholder': '300000',
        'help': 'Valor total do imóvel. Use apenas números, sem pontos ou vírgulas.'
    },
    {
        'key': 'entrada',
        'label': 'Valor da entrada (R$)',
        'type': 'money',
        'default': 60000,
        'min': 0,
        'max': 20000000,
        'placeholder': '60000',
        'help': 'Valor que pretende dar de entrada. Deixe 0 se não houver entrada.'
    },
    {
        'key': 'fgts_saldo',
        'label': 'Saldo FGTS disponível (R$)',
        'type': 'money',
        'default': 0,
        'min': 0,
        'placeholder': '0',
        'help': 'Informe o saldo disponível no FGTS se pretende utilizá-lo.'
    },
    {
        'key': 'paga_aluguel',
        'label': 'Você paga aluguel hoje?',
        'type': 'bool',
        'default': True,
        'help': 'Se você atualmente paga aluguel, o sistema considerará o cenário aluguel vs compra.'
    },
    {
        'key': 'aluguel_inicial',
        'label': 'Aluguel mensal atual (R$)',
        'type': 'money',
        'default': 1500,
        'min': 0,
        'placeholder': '1500',
        'help': 'Valor do aluguel que você paga atualmente.',
        'visible_if': {'paga_aluguel': True}
    },
    {
        'key': 'renda_familiar_bruta',
        'label': 'Renda Familiar Bruta Mensal (R$)',
        'type': 'money',
        'default': 8000,
        'min': 0,
        'placeholder': '8000',
        'help': 'Renda bruta total da família por mês. Usada em simulações de capacidade de pagamento.'
    },
    {
        'key': 'prazo_anos',
        'label': 'Prazo desejado (anos)',
        'type': 'int',
        'default': 30,
        'min': 1,
        'max': 40,
        'help': 'Número de anos do financiamento ou horizonte de investimento.'
    },
    {
        'key': 'prazo_anos_consorcio',
        'label': 'Prazo do consórcio (anos)',
        'type': 'int',
        'default': 15,
        'min': 5,
        'max': 25,
        'help': 'Prazo típico do consórcio (10-20 anos).',
        'visible_if': {'objetivo': 'Consórcio'}
    },
    {
        'key': 'taxa_anual',
        'label': 'Taxa de juros anual (%)',
        'type': 'percent',
        'default': 8.5,
        'min': 0,
        'max': 30,
        'step': 0.1,
        'help': 'Taxa anual em porcentagem. Use ponto como separador decimal se necessário.'
    },
    {
        'key': 'taxa_adm',
        'label': 'Taxa de administração anual do consórcio (%)',
        'type': 'percent',
        'default': 1.5,
        'min': 0,
        'max': 10,
        'help': 'Percentual cobrado de administração pelo consórcio.',
        'visible_if': {'objetivo': 'Consórcio'}
    },
    {
        'key': 'fundo_reserva',
        'label': 'Fundo de reserva (%)',
        'type': 'percent',
        'default': 0.5,
        'min': 0,
        'max': 5,
        'help': 'Percentual destinado ao fundo de reserva no consórcio.',
        'visible_if': {'objetivo': 'Consórcio'}
    },
    {
        'key': 'lance_fgts',
        'label': 'Valor do lance com FGTS (R$)',
        'type': 'money',
        'default': 0,
        'min': 0,
        'help': 'Valor a ser oferecido como lance usando FGTS (se aplicável).',
        'visible_if': {'objetivo': 'Consórcio'}
    },
    {
        'key': 'opcao_pagamento_aluguel',
        'label': 'Se paga aluguel, como pretende tratá-lo?',
        'type': 'choice',
        'options': ['renda', 'investimento'],
        'default': 'investimento',
        'help': 'Escolha se o valor do aluguel será interpretado como custo ou destinado a investimento.'
    },
    {
        'key': 'taxa_investimento',
        'label': 'Rendimento anual esperado do investimento (%)',
        'type': 'percent',
        'default': 6.0,
        'min': 0,
        'max': 50,
        'step': 0.1,
        'help': 'Rendimento anual esperado para investimentos.',
        'visible_if': {'objetivo': ['Investir e alugar', 'Pesquisar só']}
    },
    {
        'key': 'aporte_mensal',
        'label': 'Aporte mensal disponível (R$)',
        'type': 'money',
        'default': 0,
        'min': 0,
        'placeholder': '0',
        'help': 'Valor disponível para investir a cada mês.',
        'visible_if': {'objetivo': ['Investir e alugar', 'Pesquisar só']}
    },
    {
        'key': 'aporte_13',
        'label': 'Aporte anual disponível (R$)',
        'type': 'money',
        'default': 0,
        'min': 0,
        'help': 'Valor extra anual (ex: 13º) que pode ser usado para amortização ou investimento.'
    }
]


def map_answers_to_dados_form(answers: Dict[str, Any]) -> Dict[str, str]:
    """
    Converte um dicionário `answers` (chaves do wizard) em um `dados_form`
    compatível com `comparar_cenarios_e_formatar`.

    The function returns values as strings because the view expects
    request.POST-like values (strings); check templates/views that read these.
    """

    def s(v):
        # normalize to string values expected by views/forms
        if isinstance(v, bool):
            return 'on' if v else 'off'
        if v is None:
            return ''
        return str(v)

    # defaults
    dados = {
        'valor_imovel': s(answers.get('valor_imovel', 300000)),
        'entrada': s(answers.get('entrada', 60000)),
        'valor_despesas': s(answers.get('valor_despesas', 15000)),
        'prazo_anos': s(answers.get('prazo_anos', 30)),
        'taxa_anual': s(answers.get('taxa_anual', 8.5)),
        'seguro_mensal': s(answers.get('seguro_mensal', 0)),
        'taxa_admin_mensal': s(answers.get('taxa_admin_mensal', 0)),
        'fgts_saldo': s(answers.get('fgts_saldo', 0)),
        'incorporar_despesas': s(answers.get('incorporar_despesas', False)),
        'usar_fgts_financiamento': s(answers.get('usar_fgts_financiamento', bool(answers.get('fgts_saldo', 0)))),
        'tipo_amortizacao_fgts': s(answers.get('tipo_amortizacao_fgts', 'reduzir_prazo')),
        'mes_uso_fgts_financiamento': s(answers.get('mes_uso_fgts_financiamento', 1)),

        # Consórcio
        'taxa_adm': s(answers.get('taxa_adm', 1.5)),
        'fundo_reserva': s(answers.get('fundo_reserva', 0.5)),
        'prazo_anos_consorcio': s(answers.get('prazo_anos_consorcio', answers.get('prazo_anos', 15))),
        'lance_fgts': s(answers.get('lance_fgts', 0)),

        # Aluguel + Investimento
        'valor_imovel_total': s(answers.get('valor_imovel', 300000)),
        'entrada_total': s(answers.get('entrada', 60000)),
        'taxa_investimento': s(answers.get('taxa_investimento', 6.0)),
        'aluguel_inicial': s(answers.get('aluguel_inicial', 1500 if answers.get('paga_aluguel', True) else 0)),
        'taxa_inflacao': s(answers.get('taxa_inflacao', 3.0)),
        'recursos_proprios_iniciais': s(answers.get('recursos_proprios_iniciais', 0)),
        'opcao_pagamento_aluguel': s(answers.get('opcao_pagamento_aluguel', 'investimento')),
        'rendimento_fgts': s(answers.get('rendimento_fgts', 3.0)),
        'fgts_mensal_percent': s(answers.get('fgts_mensal_percent', 8.0)),
        'aporte_13': s(answers.get('aporte_13', 0)),
        'aporte_mensal': s(answers.get('aporte_mensal', 0)),
        'renda_familiar_bruta': s(answers.get('renda_familiar_bruta', 8000)),
        'valorizacao_imovel': s(answers.get('valorizacao_imovel', 2.0)),
    }

    return dados


if __name__ == '__main__':
    # quick demo
    sample = {
        'valor_imovel': 350000,
        'entrada': 70000,
        'fgts_saldo': 12000,
        'paga_aluguel': True,
        'renda_familiar_bruta': 9000,
        'prazo_anos': 25,
        'taxa_anual': 7.5,
        'opcao_pagamento_aluguel': 'investimento',
        'aporte_13': 2000,
    }

    import json
    print(json.dumps(map_answers_to_dados_form(sample), indent=2, ensure_ascii=False))
