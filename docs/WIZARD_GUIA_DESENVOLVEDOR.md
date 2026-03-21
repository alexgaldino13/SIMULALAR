# Guia do Desenvolvedor - Wizard ImobCalc

## Visão Geral

O Wizard ImobCalc é um sistema de simulação de financiamento imobiliário em 4 etapas que guia o usuário desde a entrada de dados básicos até a visualização de resultados detalhados.

## Arquitetura

### Estrutura de Arquivos

```
ImobCalc/
├── simulacao/
│   ├── views.py              # Lógica do wizard (WizardView)
│   ├── forms.py              # Formulários de cada step
│   ├── models.py             # Modelos de dados
│   ├── templates/simulacao/
│   │   └── wizard_v2_step.html  # Template principal
│   └── tests/
│       └── test_wizard_integration.py
├── static/
│   ├── css/
│   │   ├── wizard-responsive.css
│   │   └── wizard-responsive.min.css
│   └── js/
│       ├── wizard.js
│       └── wizard.min.js
└── ImobCalc/
    ├── settings.py
    └── cache_settings.py
```

### Fluxo de Dados

1. **Step 1 - Dados Básicos**
   - Valor do imóvel
   - Valor de entrada
   - Prazo (meses)
   - Taxa de juros anual

2. **Step 2 - Sistema de Amortização**
   - SAC (Sistema de Amortização Constante)
   - PRICE (Tabela Price)

3. **Step 3 - Dados Pessoais**
   - Nome completo
   - Email
   - Telefone
   - Renda mensal

4. **Step 4 - Resultado**
   - Tabela de amortização
   - Gráficos
   - Resumo financeiro

## Componentes Principais

### WizardView (views.py)

```python
class WizardView(SessionWizardView):
    """View principal do wizard multi-step."""
    
    template_name = 'simulacao/wizard_v2_step.html'
    form_list = [
        ('dados_basicos', DadosBasicosForm),
        ('sistema_amortizacao', SistemaAmortizacaoForm),
        ('dados_pessoais', DadosPessoaisForm),
        ('resultado', ResultadoForm)
    ]
```

**Métodos importantes:**
- `get_context_data()` - Adiciona dados ao contexto do template
- `done()` - Processa dados finais e redireciona
- `get_form_initial()` - Define valores iniciais dos formulários

### Formulários (forms.py)

Cada step tem seu próprio formulário:

```python
class DadosBasicosForm(forms.Form):
    valor_imovel = forms.DecimalField(
        label='Valor do Imóvel',
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'R$ 0,00'
        })
    )
    # ... outros campos
```

### Template (wizard_v2_step.html)

Template responsivo com:
- Barra de progresso dinâmica
- Validação em tempo real
- Animações CSS
- Suporte mobile

### JavaScript (wizard.js)

Funcionalidades:
- Validação de campos em tempo real
- Efeito ripple em botões
- Máscaras de entrada
- Feedback visual

### CSS (wizard-responsive.css)

Estilização:
- Design responsivo (mobile-first)
- Animações (fadeInUp, shimmer, pulse, ripple)
- Temas de cores
- Breakpoints: 768px, 992px, 1200px

## Cálculos Financeiros

### Sistema SAC

```python
def calcular_sac(valor_financiado, taxa_mensal, prazo_meses):
    amortizacao = valor_financiado / prazo_meses
    saldo_devedor = valor_financiado
    parcelas = []
    
    for mes in range(1, prazo_meses + 1):
        juros = saldo_devedor * taxa_mensal
        parcela = amortizacao + juros
        saldo_devedor -= amortizacao
        
        parcelas.append({
            'mes': mes,
            'parcela': parcela,
            'juros': juros,
            'amortizacao': amortizacao,
            'saldo': max(0, saldo_devedor)
        })
    
    return parcelas
```

### Sistema PRICE

```python
def calcular_price(valor_financiado, taxa_mensal, prazo_meses):
    parcela_fixa = (valor_financiado * taxa_mensal * 
                    (1 + taxa_mensal) ** prazo_meses) / \
                   ((1 + taxa_mensal) ** prazo_meses - 1)
    
    saldo_devedor = valor_financiado
    parcelas = []
    
    for mes in range(1, prazo_meses + 1):
        juros = saldo_devedor * taxa_mensal
        amortizacao = parcela_fixa - juros
        saldo_devedor -= amortizacao
        
        parcelas.append({
            'mes': mes,
            'parcela': parcela_fixa,
            'juros': juros,
            'amortizacao': amortizacao,
            'saldo': max(0, saldo_devedor)
        })
    
    return parcelas
```

## Testes

### Executar Testes

```bash
# Todos os testes
python manage.py test simulacao.tests

# Testes específicos
python manage.py test simulacao.tests.test_wizard_integration

# Com verbosidade
python manage.py test simulacao.tests --verbosity=2
```

### Cobertura de Testes

- Fluxo completo: ✅
- Validações: ✅
- Navegação: ✅
- Cálculos: ✅
- Interface: ✅

## Performance

### Otimizações Implementadas

1. **Minificação de Assets**
   - CSS: 4.2 KB → 2.1 KB (-50%)
   - JS: 3.8 KB → 2.0 KB (-47%)

2. **Cache**
   - LocMemCache configurado
   - Timeout: 5 min (dev) / 24h (prod)

3. **Lazy Loading**
   - Carregamento sob demanda de recursos

4. **Versões Condicionais**
   - `.css` e `.js` em desenvolvimento
   - `.min.css` e `.min.js` em produção

## Customização

### Adicionar Novo Step

1. Criar formulário em `forms.py`:
```python
class NovoStepForm(forms.Form):
    campo = forms.CharField()
```

2. Adicionar ao `form_list` em `views.py`:
```python
form_list = [
    # ... steps existentes
    ('novo_step', NovoStepForm),
]
```

3. Atualizar template para incluir novo step

### Modificar Estilos

Editar `static/css/wizard-responsive.css` e regenerar minificado:
```bash
# Minificar CSS
python -c "import csscompressor; print(csscompressor.compress(open('static/css/wizard-responsive.css').read()))" > static/css/wizard-responsive.min.css
```

### Adicionar Validações

Em `forms.py`:
```python
def clean_campo(self):
    valor = self.cleaned_data['campo']
    if condicao:
        raise forms.ValidationError('Mensagem de erro')
    return valor
```

## Troubleshooting

### Problema: Wizard não avança
- Verificar validações do formulário
- Checar console do navegador para erros JS
- Validar dados da sessão

### Problema: Cálculos incorretos
- Verificar taxa de juros (anual vs mensal)
- Conferir arredondamentos
- Executar testes unitários

### Problema: Estilos não aplicados
- Limpar cache do navegador
- Verificar se versão minificada está atualizada
- Checar `DEBUG` em settings.py

## Referências

- [Django FormWizard](https://django-formtools.readthedocs.io/)
- [SAC vs PRICE](https://www.bcb.gov.br/)
- [RELATORIO_OTIMIZACAO_5.6.md](../RELATORIO_OTIMIZACAO_5.6.md)
- [RELATORIO_TESTES_5.7.md](../RELATORIO_TESTES_5.7.md)

## Changelog

### v2.0 - 18/03/2026
- ✅ Wizard responsivo implementado
- ✅ Animações e feedback progressivo
- ✅ Otimizações de performance
- ✅ Testes de integração
- ✅ Documentação completa

### v1.0 - Data anterior
- Versão inicial do wizard
