# 📋 ANÁLISE DOS 5 PONTOS DE ATENÇÃO - FI System

**Data:** 25 de Janeiro de 2026  
**Status:** 🔴 Em Análise (baseado em ANALISE_CONTRATO_ITAU.md + PDFs Itaú)

---

## 📊 SUMÁRIO EXECUTIVO

| # | Ponto | Impacto | Complexidade | Status |
|----|-------|---------|--------------|--------|
| 1 | **TR (Taxa Referencial)** | 🔴 CRÍTICO | 🟠 MÉDIO | ⚠️ NÃO IMPLEMENTADO |
| 2 | **IOF** | 🟠 ALTO | 🟢 BAIXO | ⚠️ NÃO IMPLEMENTADO |
| 3 | **IPTU/Condomínio** | 🟠 ALTO | 🟢 BAIXO | ⚠️ PARCIAL |
| 4 | **IR sobre Rendimentos** | 🟠 ALTO | 🟠 MÉDIO | ⚠️ NÃO IMPLEMENTADO |
| 5 | **Bug Consórcio (0.7%)** | 🔴 CRÍTICO | 🟢 BAIXO | ⚠️ EM INVESTIGAÇÃO |

---

## 1️⃣ TR - TAXA REFERENCIAL

### 📌 O que é?
A **Taxa Referencial (TR)** é um índice econômico brasileiro que corrige o saldo devedor em financiamentos imobiliários (SFH - Sistema Financeiro da Habitação). É publicada diariamente pelo Banco Central.

### 📋 Situação Atual no Código

**Arquivo:** [simulacao/calculadora_financeira.py](simulacao/calculadora_financeira.py)  
**Função:** `calcular_price_sac()` + `simular_sac_realista.py`

```python
# LINHA ~L800: Atualmente, TR é ignorada
# Saldo é corrigido com taxa = 1.0 (sem aplicação)

def calcular_price_sac(metodo, valor_principal, taxa_anual, prazo_meses, 
                       seguro_mensal=0.0, taxa_admin_mensal=0.0, **kwargs):
    # TR não está nos kwargs
    # Saldo corrigido = Saldo Anterior × 1.0  ← PROBLEMA
```

### 🎯 O que precisa ser implementado?

**Passo 1: Integrar TR Mensal**

```python
def calcular_price_sac(
    metodo, valor_principal, taxa_anual, prazo_meses,
    seguro_mensal=0.0,
    taxa_admin_mensal=0.0,
    tr_mensal=0.0,  # ← NOVO PARÂMETRO
    **kwargs
):
    """
    tr_mensal: Taxa Referencial do mês (padrão: 0.0 = sem correção)
    Exemplo: tr_mensal=0.0015 (0.15% no período)
    """
    
    # Em cada mês do SAC:
    saldo_corrigido = saldo_anterior * Decimal(str(1.0 + tr_mensal))
```

**Passo 2: Valores Reais de TR (últimos 12 meses)**

Baseado nos PDFs do Itaú:

```
Jan/2025: 0.16% a.m. (acumulado: 1.94% a.a.)
Fev/2025: 0.15% a.m.
Mar/2025: 0.14% a.m.
...
Média: ~0.15% a.m. (histórico recente 2024-2025)
```

### 📊 Exemplo de Impacto

**Contrato Itaú (Validado):**
- Saldo: R$ 327.650,72
- Taxa: 6,69% a.a.
- Prazo: 360 meses
- **SEM TR:** Total pago = R$ 775.860,11
- **COM TR (0.15% a.m.):** Total pago ≈ R$ 785.000 (1.2% mais caro)

### ✅ Solução Proposta

1. Adicionar `tr_mensal` como kwarg optativo em `calcular_price_sac()`
2. Criar função auxiliar `obter_tr_historica(data_inicio, data_fim)` 
3. Permitir usuário escolher entre:
   - TR histórica (mais preciso)
   - TR fixa (0.0 = sem correção) **← ATUAL**
   - TR média dos últimos 12 meses

---

## 2️⃣ IOF - IMPOSTO SOBRE OPERAÇÕES FINANCEIRAS

### 📌 O que é?
**IOF** é um imposto federal sobre transações financeiras. Para financiamentos imobiliários:
- **Alíquota:** 0,0938% a.m. (parcela linear) + 0,5% (parcela relativa)
- **Incidência:** Calculado sobre o valor financiado
- **Cobrança:** Geralmente embutida nas primeiras parcelas ou na entrada

### 📋 Situação Atual no Código

**Status:** ❌ NÃO IMPLEMENTADO

No `calculadora_financeira.py`, não há cálculo de IOF:
```python
# FALTA: Cálculo de IOF
# Deveria haver:
iof_total = valor_financiado * 0.00938  # 0,938% linear
```

### 🎯 O que precisa ser implementado?

**Fórmula IOF:**
```
IOF_linear = Valor_Financiado × 0,00938 (0,938% ao ano)
IOF_relativo = Parcela_Mensal × 0,005 (0,5% por parcela)
IOF_Total = IOF_linear + (IOF_relativo × nº parcelas)
```

**Exemplos reais (PDFs Itaú):**
```
Financiamento: R$ 327.650,72
IOF Linear: 327.650,72 × 0,00938 = R$ 3.075,14
IOF Relativo (360 parcelas): Var. conforme parcela

Total IOF: ~R$ 5.000 - R$ 6.000
```

### ✅ Solução Proposta

Criar nova função em `calculadora_financeira.py`:

```python
def calcular_iof(
    valor_financiado: float,
    parcelas_mensais: List[float],
    incluir_no_calculo: bool = True  # True: somar ao valor final
) -> Dict:
    """
    Calcula IOF conforme Lei nº 7.798/89 + Anexo do Decreto 9.867/2019
    
    Args:
        valor_financiado: Valor do empréstimo
        parcelas_mensais: Lista com valor de cada parcela
        incluir_no_calculo: Se True, IOF é somado nas parcelas
    
    Returns:
        {
            'iof_linear': float,
            'iof_relativo': float,
            'iof_total': float,
            'parcelas_com_iof': List[float],  # Se incluir_no_calculo=True
            'primeira_parcela_iof': float
        }
    """
    iof_linear = Decimal(str(valor_financiado)) * Decimal('0.00938')
    iof_relativo = sum([
        Decimal(str(p)) * Decimal('0.005') 
        for p in parcelas_mensais
    ])
    
    return {
        'iof_linear': float(iof_linear),
        'iof_relativo': float(iof_relativo),
        'iof_total': float(iof_linear + iof_relativo),
    }
```

**Integração com Wizard:**
- Etapa de Financiamento → checkbox "Incluir IOF no cálculo"
- Mostra: "IOF será de ~R$ X.XXX (embutido nas parcelas)"

---

## 3️⃣ IPTU / CONDOMÍNIO

### 📌 O que é?
Despesas mensais/anuais do imóvel:
- **IPTU:** Imposto Predial Territorial Urbano (varia 0.5% - 1.5% do valor venal/ano)
- **Condomínio:** Taxa mensal de manutenção de prédios (R$ 300 - R$ 2.000/mês)
- **Seguro Predial:** Opcional (0.3% - 0.5% do valor/ano)

### 📋 Situação Atual no Código

**Arquivo:** [simulacao/calculadora_financeira.py](simulacao/calculadora_financeira.py)  
**Status:** ⚠️ PARCIAL - Mencionado mas não integrado nos cenários

```python
# LINHA ~L600 (teste_10_perfis_completo.py):
# Comentário:
# "FALTA: Despesas com imóvel alugado (IPTU, condomínio, seguro)"

# Atualmente:
simular_aluguel_investimento()  # Não inclui IPTU/Condomínio
calcular_price_sac()            # Não inclui IPTU/Condomínio
```

### 🎯 O que precisa ser implementado?

**Passo 1: Criar função auxiliar**

```python
def calcular_despesas_imovel(
    valor_imovel: float,
    tipo_imovel: str = 'apartamento',  # casa, apartamento, terreno
    aliquota_iptu: float = 0.012,      # 1.2% ao ano
    valor_condominio_mensal: float = 500.0,
    percentual_seguro: float = 0.004,  # 0.4% ao ano
    prazo_meses: int = 360
) -> Dict:
    """
    Calcula despesas anuais/mensais do imóvel
    
    Returns:
        {
            'iptu_mensal': float,
            'iptu_anual': float,
            'condominio_mensal': float,
            'seguro_mensal': float,
            'total_mensal': float,
            'total_anual': float,
            'despesa_30anos': float
        }
    """
    valor_dec = Decimal(str(valor_imovel))
    
    iptu_anual = valor_dec * Decimal(str(aliquota_iptu))
    iptu_mensal = iptu_anual / 12
    
    seguro_mensal = (valor_dec * Decimal(str(percentual_seguro))) / 12
    
    total_mensal = iptu_mensal + Decimal(str(valor_condominio_mensal)) + seguro_mensal
    
    return {
        'iptu_mensal': float(iptu_mensal),
        'condominio_mensal': valor_condominio_mensal,
        'seguro_mensal': float(seguro_mensal),
        'total_mensal': float(total_mensal),
        'despesa_30anos': float(total_mensal * 360)
    }
```

**Passo 2: Integrar em comparações**

```python
def comparar_cenarios_e_formatar(dados_form):
    # ... código existente ...
    
    # NOVO: Incluir despesas do imóvel
    despesas = calcular_despesas_imovel(
        valor_imovel=dados_form['valor_imovel'],
        tipo_imovel=dados_form.get('tipo_imovel', 'apartamento'),
        aliquota_iptu=0.012,  # Ou obter do formulário
        valor_condominio_mensal=dados_form.get('condominio_mensal', 500)
    )
    
    # Ajustar parcelas:
    # Parcela real = Parcela Financiamento + IPTU + Condomínio + Seguro
    parcela_ajustada = tabela[0]['parcela'] + despesas['total_mensal']
```

### ✅ Solução Proposta

1. **Etapa 3 do Wizard (Imóvel):** Adicionar campos:
   - [ ] Valor estimado do IPTU (auto-calculado ou informado)
   - [ ] Valor do condomínio (se aplicável)
   - [ ] Tem seguro predial? (Sim/Não)

2. **Exibição de resultados:** Mostrar breakdown:
   ```
   PARCELA MENSAL TOTAL
   ├─ Financiamento: R$ 2.600
   ├─ IPTU: R$ 240
   ├─ Condomínio: R$ 650
   └─ Seguro: R$ 110
   ═══════════════════
   TOTAL: R$ 3.600/mês
   ```

---

## 4️⃣ IR SOBRE RENDIMENTOS

### 📌 O que é?
Imposto de Renda incide sobre rendimentos de investimentos:
- **Poupança:** 17,5% de IR (regressivo conforme dias) 
- **CDI/LCI:** 15% - 22,5% de IR (regressivo conforme dias)
- **Tesouro Direto:** 15% (variável conforme título)
- **Ações:** 15% (operações normais)

### 📋 Situação Atual no Código

**Arquivo:** [simulacao/calculadora_financeira.py](simulacao/calculadora_financeira.py)  
**Função:** `simular_aluguel_investimento()` + `guardar_dinheiro()`

**Status:** ❌ NÃO IMPLEMENTADO

```python
# LINHA ~L1200 (simular_aluguel_investimento):
# Atualmente calcula:
rendimento = investimento * (1 + taxa_mensal)

# MAS FALTA:
# imposto_renda = rendimento * 0.15  # ou outro percentual
# rendimento_liquido = rendimento - imposto_renda
```

### 🎯 O que precisa ser implementado?

**Passo 1: Criar função de IR**

```python
def calcular_ir_rendimentos(
    valor_investido: float,
    rendimento_bruto: float,
    tipo_investimento: str = 'cdi',  # cdi, poupanca, tesouro, acoes
    dias_aplicacao: int = 30
) -> Dict:
    """
    Calcula Imposto de Renda sobre rendimentos conforme tabela regressiva
    
    Tabela Regressiva (CDI/LCI):
    - Até 180 dias: 22,5%
    - 181 a 365 dias: 20%
    - 366 a 720 dias: 17,5%
    - Acima de 720 dias: 15%
    """
    
    # Tabela regressiva
    if tipo_investimento in ['cdi', 'lci']:
        if dias_aplicacao <= 180:
            aliquota = 0.225
        elif dias_aplicacao <= 365:
            aliquota = 0.20
        elif dias_aplicacao <= 720:
            aliquota = 0.175
        else:
            aliquota = 0.15
    elif tipo_investimento == 'poupanca':
        # Poupança tem regime especial (17,5% fixo após 1 mês)
        aliquota = 0.175
    else:
        aliquota = 0.15  # Tesouro, ações, etc.
    
    ir_devido = Decimal(str(rendimento_bruto)) * Decimal(str(aliquota))
    rendimento_liquido = Decimal(str(rendimento_bruto)) - ir_devido
    
    return {
        'rendimento_bruto': float(rendimento_bruto),
        'aliquota_ir': aliquota * 100,
        'ir_devido': float(ir_devido),
        'rendimento_liquido': float(rendimento_liquido),
        'valor_total_com_ir': float(Decimal(str(valor_investido)) + rendimento_liquido)
    }
```

**Passo 2: Integrar nos cenários de investimento**

```python
def simular_aluguel_investimento(
    valor_imovel_total, entrada_total, taxa_investimento, 
    aluguel_inicial, taxa_inflacao, prazo_meses,
    recursos_proprios_iniciais=0.0,
    opcao_pagamento_aluguel='investimento',
    fgts_saldo=0.0,
    rendimento_fgts=3.0,
    fgts_mensal_percent=8.0,
    aporte_13=1000,
    renda_familiar_bruta=5000,
    valorizacao_imovel=3.0,
    taxa_anual_financiamento=7.5,
    aplicar_ir_rendimentos=True,  # ← NOVO
    tipo_investimento='cdi'        # ← NOVO
):
    """
    Simula cenário aluguel + investimento COM cálculo de IR
    """
    
    # ... código existente ...
    
    for mes in range(1, prazo_meses + 1):
        # ... acumular investimento ...
        
        if aplicar_ir_rendimentos and mes % 30 == 0:  # A cada 30 dias
            ir_info = calcular_ir_rendimentos(
                valor_investido=investimento_acumulado,
                rendimento_bruto=rendimento_do_mes,
                tipo_investimento=tipo_investimento,
                dias_aplicacao=30
            )
            investimento_acumulado = ir_info['valor_total_com_ir']
```

### ✅ Solução Proposta

1. **Novo parâmetro no Wizard (Etapa 7 - Investimento):**
   - [ ] Tipo de investimento: Poupança / CDI / LCI / Tesouro Direto / Ações
   - [ ] Aplicar IR nos cálculos? (Sim/Não)

2. **Comparativa completa:**
   ```
   ALUGUEL + INVESTIMENTO (COM IR)
   ├─ Investimento inicial: R$ 100.000
   ├─ Rendimento bruto (30 anos): R$ 450.000
   ├─ IR (15-22,5%): -R$ 75.000
   ├─ Rendimento líquido: R$ 375.000
   └─ TOTAL ACUMULADO: R$ 475.000
   
   vs.
   
   COMPRA COM FINANCIAMENTO
   ├─ Entrada: R$ 100.000
   ├─ Parcelas (360×): R$ 900.000
   ├─ Total Juros: R$ 320.000
   ├─ Valor Imóvel Hoje: R$ 600.000
   └─ PATRIMÔNIO FINAL: R$ 600.000 (casa)
   ```

---

## 5️⃣ BUG DO CONSÓRCIO (0.7%)

### 📌 O Problema
No sistema de consórcio, a parcela mensal é calculada como **0.7% do valor do bem**, porém há inconsistências na implementação:

### 📋 Situação Atual no Código

**Arquivo:** [simulacao/calculadora_financeira.py](simulacao/calculadora_financeira.py)  
**Função:** `simular_consorcio()`

**LINHA ~L328:**
```python
def simular_consorcio(valor_imovel, prazo_meses, taxa_adm, fundo_reserva, fgts_saldo=0.0):
    """
    Simula consórcio imobiliário com parcela de 0.7% a.m.
    """
    
    # PARCELA FIXA
    parcela_fixa = Decimal(str(valor_imovel)) * Decimal('0.007')  # ✓ 0.7%
    
    # ... resto do código ...
    
    return resultado
```

**Status:** ⚠️ EM INVESTIGAÇÃO

### 🔍 Bugs Identificados

Baseado em [teste_10_perfis_completo.py](teste_10_perfis_completo.py) linha ~365:

```python
print("  [ALERTA] CRITICO: Parcela 0.7% pode estar baixa\n")
```

**Problema 1:** Falta de Taxa de Administração correta
```python
# ESPERADO (banco real):
parcela_mensal = 0.7% + Taxa_Adm (1.5%-2.5%)

# ATUAL (código):
parcela_mensal = 0.7%  ← Sem taxa de administração integrada
taxa_adm_mensal = (taxa_adm_anual / 12) × valor_imovel  ← Calculada separada
```

**Problema 2:** Fundo de Reserva não é deduzido corretamente
```python
# ESPERADO:
Parcela = 0.7% + Taxa_Adm + Fundo_Reserva

# ATUAL:
Parcela = 0.7%
+ taxa_adm_mensal (separado)
+ fundo_reserva_mensal (separado)
→ Usuário vê "parcela" mas na verdade paga mais
```

**Problema 3:** Cálculo de Contemplação
```python
# ATUAL (linha ~L360):
mes_contemplacao = int(prazo_meses * 0.40)  # 40% conservador

# MAS: Deveria considerar:
- Quantidade de participantes
- Número de sorteios
- Frequência de lances
```

### ✅ Solução Proposta

**Nova função corrigida:**

```python
def simular_consorcio_corrigido(
    valor_imovel: float,
    prazo_meses: int,
    taxa_adm_percentual_anual: float = 1.5,  # 1.5% a.a.
    fundo_reserva_percentual_anual: float = 0.5,  # 0.5% a.a.
    percentual_parcela_base: float = 0.7,  # 0.7% a.m.
    metodo_contemplacao: str = 'conservador',  # conservador, medio, otimista
    fgts_saldo: float = 0.0,
) -> Dict:
    """
    Simula consórcio com cálculo correto de todos os componentes
    
    PARCELA MENSAL = 0.7% + Taxa Admin + Fundo Reserva
    
    Exemplo (Valor R$ 500.000):
    - Base (0.7%): R$ 3.500
    - Taxa Adm (1.5%/12): R$ 625
    - Fundo Reserva (0.5%/12): R$ 208
    ─────────────────────────────
    PARCELA TOTAL: R$ 4.333/mês
    """
    
    valor_dec = Decimal(str(valor_imovel))
    
    # Componente 1: Parcela Base (0.7% mensal)
    parcela_base = valor_dec * Decimal(str(percentual_parcela_base / 100))
    
    # Componente 2: Taxa de Administração (anual → mensal)
    taxa_adm_mensal = (valor_dec * Decimal(str(taxa_adm_percentual_anual / 100))) / 12
    
    # Componente 3: Fundo de Reserva (anual → mensal)
    fundo_reserva_mensal = (valor_dec * Decimal(str(fundo_reserva_percentual_anual / 100))) / 12
    
    # PARCELA TOTAL MENSAL
    parcela_mensal_total = parcela_base + taxa_adm_mensal + fundo_reserva_mensal
    
    # Cálculo de Contemplação
    if metodo_contemplacao == 'conservador':
        mes_contemplacao = max(int(prazo_meses * 0.40), 48)  # Min 48 meses
    elif metodo_contemplacao == 'medio':
        mes_contemplacao = max(int(prazo_meses * 0.30), 36)  # Min 36 meses
    else:  # otimista
        mes_contemplacao = max(int(prazo_meses * 0.25), 24)  # Min 24 meses
    
    # Gerar tabela
    tabela = []
    saldo_acumulado = Decimal('0')
    
    for mes in range(1, prazo_meses + 1):
        saldo_acumulado += parcela_mensal_total
        
        tabela.append({
            'mes': mes,
            'parcela_base': float(parcela_base),
            'taxa_adm': float(taxa_adm_mensal),
            'fundo_reserva': float(fundo_reserva_mensal),
            'parcela_total': float(parcela_mensal_total),
            'saldo_acumulado': float(saldo_acumulado),
            'contemplado': mes == mes_contemplacao,
            'meses_restantes': prazo_meses - mes
        })
    
    total_pago = float(parcela_mensal_total * prazo_meses)
    
    return {
        'valor_imovel': valor_imovel,
        'parcela_base_mensal': float(parcela_base),
        'taxa_adm_mensal': float(taxa_adm_mensal),
        'fundo_reserva_mensal': float(fundo_reserva_mensal),
        'parcela_total_mensal': float(parcela_mensal_total),
        'mes_contemplacao': mes_contemplacao,
        'total_pago': total_pago,
        'custo_total_taxa_adm': float(taxa_adm_mensal * prazo_meses),
        'custo_total_fundo': float(fundo_reserva_mensal * prazo_meses),
        'economia_vs_financiamento': float(Decimal('0')),  # Comparar com PRICE/SAC
        'tabela': tabela,
    }
```

### 📊 Comparação Antes/Depois

**ANTES (Bugado):**
```
Consórcio R$ 500.000 | 180 meses

Parcela mostrada: R$ 3.500 (0.7%)
Custos reais:   + R$ 625 (taxa adm)
                + R$ 208 (fundo reserva)
                = R$ 4.333 (não é explícito)

Problema: Usuário vê "R$ 3.500/mês" mas paga R$ 4.333
```

**DEPOIS (Corrigido):**
```
Consórcio R$ 500.000 | 180 meses

PARCELA MENSAL TOTAL: R$ 4.333
├─ Base (0.7%): R$ 3.500
├─ Taxa Adm (1.5%/12): R$ 625
└─ Fundo Reserva (0.5%/12): R$ 208

Total 180 meses: R$ 779.940
Contemplação: Mês 72 (conservador) / Mês 54 (médio)
```

---

## 🎯 ROADMAP DE IMPLEMENTAÇÃO

### Fase 1: CRÍTICO (Semana 1)
- [ ] 5 - Corrigir bug consórcio 0.7%
- [ ] 2 - Implementar IOF
- [ ] 3 - Integrar IPTU/Condomínio

### Fase 2: IMPORTANTE (Semana 2)
- [ ] 1 - Implementar TR (Taxa Referencial)
- [ ] 4 - Implementar IR sobre rendimentos

### Fase 3: REFINAMENTO (Semana 3)
- [ ] Testes integrados com PDFs do Itaú
- [ ] Validação de precisão (99%+)
- [ ] Documentação de usuário

---

## 📚 REFERÊNCIAS

**PDFs Itaú (Documentos auxiliares/):**
1. `Contrato Itaú TF224.pdf` - Contrato real validado
2. `ITAU DEMONSTRATIVO FINANCIAMENTO IMOBILIÁRIO.pdf` - DDC de 360 parcelas

**Regulamentações Brasileiras:**
- Lei nº 7.798/89 (IOF)
- Resolução BCB Nº 272/2020 (TR)
- Lei nº 4.591/64 (Consórcio)
- Lei nº 5.172/66 (IPTU)

**Arquivos do Projeto:**
- [ANALISE_CONTRATO_ITAU.md](ANALISE_CONTRATO_ITAU.md) - Análise completa
- [simulacao/calculadora_financeira.py](simulacao/calculadora_financeira.py) - Core functions
- [simulacao/sac_realista.py](simulacao/sac_realista.py) - SAC com TR

---

**Próximos passos:** 
1. Revisar com você qual ponto começar
2. Implementar solução proposta
3. Validar com PDFs do Itaú
4. Integrar ao Wizard

**Quer que eu comece por qual ponto?**
