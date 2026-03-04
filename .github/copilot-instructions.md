## Guia do Assistente IA: FI (Financiamento Imobiliário)

### Visão Geral do Projeto
Aplicação Django para simulações de financiamento imobiliário brasileiro: Tabela Price (parcelas constantes), SAC (parcelas decrescentes), consórcio e aluguel+investimento (análise comparativa aluguel vs. compra).

### Setup & Dependências
**Instalação inicial:**
```sh
pip install -r requirements.txt
pip install scipy numpy  # CRÍTICO: não estão em requirements.txt mas são usados em CET
python manage.py migrate
python manage.py runserver
```

**Notas críticas:**
- `requirements.txt` incompleto (scipy/numpy faltando). Instale manualmente.
- Banco de dados: SQLite em `./db.sqlite3`. Uma única instância.
- Allauth integrado para autenticação social (Google, etc.)

### Arquitetura de Fluxo Dados
```
Usuário (Forms HTML)
    ↓
wizard_views.py (WizardStep 1-8)  ou  views.py (Price/SAC direto)
    ↓
wizard_forms.py / forms.py (Validação)
    ↓
calculadora_financeira.py (Funções core de cálculo - Decimal para precisão)
    ↓
formatacao.py (Conversão float, formatação moeda)
    ↓
templates/ (Renderização com custom_filters.py)
```

**Componentes principais:**
- [simulacao/calculadora_financeira.py](simulacao/calculadora_financeira.py) (1551 linhas)—fonte única da verdade; toda lógica financeira; usa Decimal internamente
- [simulacao/wizard_views.py](simulacao/wizard_views.py)—orquestra fluxo multi-step com estado em sessão; 8 etapas (privacidade, perfil, imóvel, métodos, financiamento, consórcio, investimento, aluguel)
- [simulacao/views.py](simulacao/views.py)—vista alternativa para cálculos diretos (Price/SAC sem wizard)
- [simulacao/wizard_questions.py](simulacao/wizard_questions.py)—mapeamento Q&A → campos de formulário via `map_answers_to_dados_form()`
- [simulacao/wizard_forms.py](simulacao/wizard_forms.py)—8 formulários correspondentes aos steps; validação de entrada

### Funções Core de Cálculo (API Pública)
Importar direto em testes ou novas views:
```python
from simulacao.calculadora_financeira import (
    calcular_price_sac,              # (metodo, valor_principal, taxa_anual, prazo_meses, **kwargs)
    simular_consorcio,                # (valor_imovel, prazo_meses, taxa_adm, fundo_reserva, fgts_saldo=0)
    simular_consorcio_com_lances,     # Versão com cronograma de lances
    simular_aluguel_investimento,     # Análise aluguel vs. compra (VPL)
    calcular_cet,                     # (valor_financiado, parcelas_mensais, custos_iniciais=None)
    comparar_cenarios_e_formatar      # Orquestrador: roteador de cenários + formatação final
)

# Exemplo direto (testes):
resultado = calcular_price_sac('price', valor_principal=300000, taxa_anual=7.0, prazo_meses=360)
print(resultado['tabela'][0])  # Primeiro mês
print(resultado['total_juros'])
```

**Contrato de assinatura:**
- Aceita valores numéricos (float/int); converte internamente para `Decimal(str(x))`—nunca literal float
- `**kwargs` para flags opcionais: `seguro_mensal`, `fgts_saldo`, `tipo_amortizacao_fgts`, etc.
- Retorna dict com chaves float (serialização JSON/sessão)
- Chaves esperadas em templates: `'tabela'`, `'total_juros'`, `'parcela_inicial'`, `'cet_anual'`, `'saldo_final'`

### Regra de Ouro: Decimal para Precisão Monetária
```python
from decimal import Decimal
# ✓ CORRETO
valor = Decimal(str(entrada_usuario))  # Sempre de string, não float literal
saldo = Decimal('300000')

# ✗ ERRADO
valor = Decimal(0.1)  # Float literal → erro de arredondamento
saldo = Decimal(300000.0)
```
Centavos reais dependem disso. Use Decimal em todo código de `calculadora_financeira.py`.

### Fluxo Wizard (Multi-step Stateful)
Controle em [simulacao/wizard_views.py](simulacao/wizard_views.py), linha ~40 (WIZARD_STEPS dict):

**8 Steps → 8 Formulários:**
1. **Privacy** (`WizardPrivacyForm`)—consentimento, preferências de privacidade
2. **Perfil** (`WizardPerfilForm`)—renda, idade, estado civil
3. **Imóvel** (`WizardImovelForm`)—localização, valor, tipo
4. **Métodos** (`WizardMetodosForm`)—seleção de cenários (Price/SAC/Consórcio/Aluguel)
5. **Financiamento** (`WizardFinanciamentoForm`)—taxa, prazo, entrada
6. **Consórcio** (`WizardConsorcioForm`)—taxa de administração, fundo de reserva
7. **Investimento** (`WizardInvestimentoForm`)—rendimento, aplicação
8. **Aluguel** (`WizardAluguelForm`)—aluguel inicial, inflação; chama `comparar_cenarios_e_formatar()`

**Fluxo de dados wizard:**
- Dados em sessão: `request.session['wizard_data']`—dict com dados de cada step
- Step 8 recolhe tudo, chama `map_answers_to_dados_form()` para mapear respostas a nomes de campos
- Passa para `comparar_cenarios_e_formatar(dados_form)` que roteador 4 cenários simultâneos
- Renderiza `wizard_resultados.html` com comparação lado-a-lado

**Tipagem de sessão:**
- Armazena floats (não Decimal)—use helper `_convert_decimal_to_float()` antes de serializar
- Recupere e reconverta com `Decimal(str(valor_sessao))` ao chamar funções de cálculo

### Testes
```sh
python manage.py test simulacao  # Executa todos em tests.py

# Debug rápido (shell):
python manage.py shell
>>> from simulacao.calculadora_financeira import calcular_price_sac
>>> resultado = calcular_price_sac('price', 300000, 7.0, 360)
>>> print(resultado['tabela'][0])
```

**Padrão em [simulacao/tests.py](simulacao/tests.py):**
- `SimpleTestCase` para funções puras (sem banco de dados)
- Chama core functions diretamente: `calcular_price_sac()`, `simular_consorcio()`, etc.
- Valida chaves de retorno e intervalos esperados

### Padrões Comuns de Modificação

**Adicionar novo campo de entrada:**
1. Novo field em `WizardFinanciamentoForm` (ou formulário apropriado em [simulacao/wizard_forms.py](simulacao/wizard_forms.py))
2. Receba em [simulacao/wizard_views.py](simulacao/wizard_views.py) view; passe como kwarg a `comparar_cenarios_e_formatar()`
3. Atualize assinatura de função core em [simulacao/calculadora_financeira.py](simulacao/calculadora_financeira.py) (adicione `novo_param=0.0` em `**kwargs`)
4. Atualize template de resultado para referenciar nova chave

**Mudar lógica de cálculo:**
1. Edite função em [simulacao/calculadora_financeira.py](simulacao/calculadora_financeira.py) (ex: `calcular_price_sac()`)
2. Garanta que chaves dict retornadas existem: `'tabela'`, `'total_juros'`, `'cet_anual'`
3. Se chaves forem renomeadas, atualize views + templates que usam dict hardcoded
4. Execute testes: `python manage.py test simulacao`

**Adicionar nova métrica:**
1. Calcule em função de simulação relevante (ex: `calcular_price_sac()`)
2. Retorne como chave dict em float (não Decimal)
3. Adicione a resultado de `comparar_cenarios_e_formatar()`
4. Em template, referencie chave; use custom_filters se for moeda (ex: `|formatar_moeda_brl`)

### Funcionalidades Especiais

**CET (Custo Efetivo Total)**—[simulacao/calculadora_financeira.py](simulacao/calculadora_financeira.py)~L18
- Usa `scipy.optimize.newton()` para encontrar TIR
- Iguala valor líquido liberado = fluxo de caixa dos pagamentos
- Retorna `cet_mensal` e `cet_anual` (%)
- Requer scipy instalado

**FGTS Integration**—kwargs `fgts_saldo`, `uso_fgts_financiamento`, `tipo_amortizacao_fgts`
- Roteador em funções de simulação; deduz saldo FGTS da entrada
- Três tipos de amortização: padrão, diferido, outros
- Sempre converta Decimal antes de armazenar em sessão

**Consórcio com Lances**—[simulacao/calculadora_financeira.py](simulacao/calculadora_financeira.py)~L395 `simular_consorcio_com_lances()`
- Cronograma dinâmico; determina quem saca e quando via lances competitivos
- Distinto de `simular_consorcio()` básico (parcelas fixas, sem lances)
- Retorna tabela mensal com situação de cada participante

**Aluguel+Investimento**—análise VPL tri-cenário
- Cenário 1: Compra com financiamento
- Cenário 2: Compra à vista (recursos próprios)
- Cenário 3: Aluguel + investir entrada em ativos (rendimento %)
- Compara riqueza cumulativa (casa + poupança vs. aluguel + investimento)

**SAC Realista**—[simulacao/sac_realista.py](simulacao/sac_realista.py)
- Variante de SAC com seguros diferidos (não linear como SAC padrão)
- Alternativa para análises realistas de crédito imobiliário

### Convenções do Projeto
- **Idioma**: Português para lógica de domínio; inglês para utilities genéricas
- **Persistência sessão**: Sempre Decimal → float antes de armazenar; reconverta ao ler
- **Formatação**: Use [simulacao/templatetags/custom_filters.py](simulacao/templatetags/custom_filters.py) (ex: `|formatar_moeda_brl`) em templates; evite floats brutos
- **API Stability**: Funções core são API pública—mudanças de assinatura requerem updates em views + templates

### Pré-commit Checklist
- [ ] Testes passam: `python manage.py test simulacao`
- [ ] Se modificar função de cálculo: grep `calculadora_financeira` em `views.py`, `wizard_views.py` para verificar todos os chamadores
- [ ] Se adicionar chaves dict: encontre em templates (`grep -r` por chave em `templates/`) e valide referências
- [ ] Inputs numéricos usam `Decimal(str(...))` em código de cálculo
- [ ] scipy/numpy instalado se tocar em `calcular_cet()` ou otimização numérica
