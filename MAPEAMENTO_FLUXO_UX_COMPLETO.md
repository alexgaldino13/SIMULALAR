# 📊 ANÁLISE DE FLUXO UX: Wizard ImobCalc - Visão Completa

## 🎯 Objetivo da Análise

Mapear o fluxo completo do wizard (pergunta → resposta → cálculo) para:
- ✅ Verificar se faz sentido para o usuário
- ✅ Identificar dados redundantes ou faltantes
- ✅ Otimizar sequência de perguntas
- ✅ Validar se dados chegam onde deveriam

---

## 🔄 FLUXO COMPLETO DO WIZARD (5 Etapas)

### 📍 ETAPA 1: "Situação Atual"

#### Pergunta: Onde você está hoje?

```
[Radio Button]
1. Aluga imóvel
2. Possui imóvel próprio
3. Mora com família (sem imóvel próprio)
```

**Campo adicional:**
- Se "aluga": [Input numérico] "Quanto paga de aluguel? R$ ___"

---

#### 📌 Dados Coletados:

| Campo | Tipo | Valor Exemplo | Uso |
|-------|------|--------------|-----|
| `situacao_atual` | enum | "aluga" | Determina cenário base |
| `aluguel_atual` | decimal | 1500.00 | Cálculo de custo em todos cenários |

#### 🔍 Análise UX:

✅ **Faz sentido?** SIM
- Pergunta clara e direta
- Usuário sabe sua situação
- Aluguel é informação essencial para comparação

⚠️ **Possível melhoria:**
- Se "mora com família", poderia perguntar: "Quanto é o aluguel do imóvel onde mora?" (para comparação)
- Contextualizar: "Isso nos ajudará a comparar: continuar alugando vs comprar"

---

### 📍 ETAPA 2: "Capital Disponível"

#### Perguntas:

```
1. Quanto tem guardado (poupança/aplicações)?
   [Input: R$ ___]

2. Saldo de FGTS disponível?
   [Input: R$ ___]

3. Valor do imóvel que possui hoje?
   [Input: R$ ___] OU [N/A]
```

---

#### 📌 Dados Coletados:

| Campo | Tipo | Valor Exemplo | Uso |
|-------|------|--------------|-----|
| `poupanca` | decimal | 50000.00 | Capital para entrada |
| `fgts_saldo` | decimal | 25000.00 | Amortização FGTS |
| `imovel_atual_valor` | decimal | 200000.00 | Para venda/troca |

#### 🔍 Análise UX:

✅ **O que funciona:**
- Perguntas diretas
- Usuário geralmente conhece seus saldos

❌ **Problema 1: Contexto Faltante**
- Usuário não entende por que está sendo perguntado
- Falta mensagem tipo: "Esse capital será a sua entrada + amortizações"

❌ **Problema 2: FGTS Confuso**
- Muitos não sabem se têm FGTS
- Falta checkbox: "Não sei meu saldo" com link para consulta
- Deveria sugerir: "Consulte no app FGTS ou site CEF"

❌ **Problema 3: Imóvel Atual**
- Se "aluga" (Etapa 1), por que pergunta imóvel?
- Falta lógica condicional clara

#### 💡 **Sugestão de Melhoria:**

```
ETAPA 2 (Revisada):

1. "Quanto você tem guardado para ENTRADA?"
   └─ Input: R$ ___ 
      └─ Hint: "Quanto pretende usar de seus economias"

2. "Tem FGTS disponível?" 
   ├─ "Sim, tenho R$ ___"
   ├─ "Não tenho FGTS"
   ├─ "Não sei" → [Link: Consulte aqui]

3. [CONDICIONAL - APENAS SE "possui imóvel" em Etapa 1]
   "Se vender seu imóvel atual, quanto poderia obter?"
   └─ Input: R$ ___
```

---

### 📍 ETAPA 3: "Seu Objetivo"

#### Perguntas:

```
1. Qual o valor do imóvel que deseja?
   [Input: R$ ___]

2. Em quantos anos quer comprar?
   [Radio: 1-3 anos / 3-5 anos / 5-10 anos / 10+ anos]

3. [Autocomplete] Em qual cidade?
   [Datalist com 200+ cidades brasileiras]
```

---

#### 📌 Dados Coletados:

| Campo | Tipo | Valor Exemplo | Uso |
|-------|------|--------------|-----|
| `valor_imovel_alvo` | decimal | 350000.00 | Principal para financiamentos |
| `prazo_desejado` | int | 5 | Converte para prazo_meses (60) |
| `cidade` | string | "São Paulo" | Referência (futura: preço regional) |

#### 🔍 Análise UX:

✅ **O que funciona:**
- Clareza nas perguntas
- Autocomplete de cidades é prático
- Prazo em "anos" é mais intuitivo que "meses"

❌ **Problema 1: Valor do Imóvel**
- Usuário não sabe exatamente que valor quer
- Falta contexto: "Pesquisou no Zap? Qual a faixa?"

❌ **Problema 2: Prazo em Categorias**
- Categorias genéricas demais
- Melhor: Slider ou input direto

❌ **Problema 3: Cidade**
- Por que pedir cidade se não usa em cálculo?
- Futura funcionalidade? Falta mensagem clara

#### 💡 **Sugestão de Melhoria:**

```
ETAPA 3 (Revisada):

1. "Qual o valor do imóvel desejado?"
   ├─ Input: R$ ___
   └─ Hint: "Pesquise em Zap, Immobiliário ou similar"

2. "Em quantos ANOS quer comprar?"
   ├─ Slider visual: [1 ←→ 35 anos]
   ├─ Ou Input: ___ anos
   └─ Mostrar: "Prazo: 120 meses"

3. "Onde você quer comprar? (Opcional)"
   ├─ Datalist: [São Paulo ▼]
   └─ Nota: "Usaremos para análises futuras"
```

---

### 📍 ETAPA 4: "Renda & Custos"

#### Perguntas:

```
1. Qual a renda familiar BRUTA total?
   [Input: R$ ___]

2. Quantos dependentes?
   [Input: número ___]

3. Qual seu tipo de renda?
   [Radio: Emprego fixo / Autônomo / Ambos]
```

---

#### 📌 Dados Coletados:

| Campo | Tipo | Valor Exemplo | Uso |
|-------|------|--------------|-----|
| `renda_familiar_bruta` | decimal | 5000.00 | Cálculo FGTS mensal (8%) + LTV |
| `dependentes` | int | 2 | ⚠️ NÃO UTILIZADO ATUALMENTE |
| `tipo_renda` | enum | "emprego_fixo" | ⚠️ NÃO UTILIZADO ATUALMENTE |

#### 🔍 Análise UX:

✅ **O que funciona:**
- Pergunta sobre renda é natural

❌ **PROBLEMA CRÍTICO 1: Dados Não Utilizados**
- `dependentes` e `tipo_renda` são coletados mas **não usam em cálculos**
- Causa confusão: "Por que está pedindo se não usa?"

❌ **PROBLEMA CRÍTICO 2: Renda Bruta vs Líquida**
- Usuário comum confunde "bruta" com "líquida"
- Não explica por que precisa de bruta

❌ **PROBLEMA 3: Falta Informação Importante**
- Não pergunta sobre **outras despesas fixas** (educação, saúde, carro)
- Apenas usa "aluguel atual" para comparação

#### 💡 **Sugestão de Melhoria:**

```
ETAPA 4 (Revisada):

1. "Qual a RENDA BRUTA total da família?"
   ├─ Input: R$ ___
   └─ Dica: "Valor antes de descontos (INSS, IR, etc)"

2. "Outras despesas fixas mensais?"
   ├─ Educação: R$ ___
   ├─ Saúde: R$ ___
   ├─ Carro/Transporte: R$ ___
   ├─ Outras: R$ ___
   └─ Total estimado: R$ ___ [calculado]

3. [Opcional] Estabilidade de renda?
   ├─ ✓ Emprego fixo (CLTI/Servidor Público)
   ├─ ⚠️ Autônomo/PJ (renda variável)
   └─ ℹ️ Isso afeta limite de financiamento
```

---

### 📍 ETAPA 5: "Cenários & Preferências"

#### Perguntas:

```
[Checkboxes - Selecione qual(is) comparar]

☑️ Financiamento PRICE (parcela fixa)
☑️ Financiamento SAC (parcela decrescente)
☑️ Consórcio (contemplação)
☑️ Aluguel + Investimento (não comprar)
☑️ Compra à Vista (se tiver capital)

[Slider] Qual taxa de retorno espera em investimentos?
[______] _____% ao ano (ex: 6% a 8%)

[Checkbox] ☑️ Usar FGTS para amortizar dívida?
```

---

#### 📌 Dados Coletados:

| Campo | Tipo | Valor Exemplo | Uso |
|-------|------|--------------|-----|
| `comparar_price` | bool | True | Ativa cálculo PRICE |
| `comparar_sac` | bool | True | Ativa cálculo SAC |
| `comparar_consorcio` | bool | True | Ativa cálculo Consórcio |
| `comparar_aluguel_inv` | bool | True | Ativa cálculo Aluguel+Inv |
| `comparar_compra_vista` | bool | False | Ativa cálculo Compra à Vista |
| `taxa_investimento` | decimal | 6.5 | % anual esperada |
| `usar_fgts` | bool | True | Flag para amortizar |

#### 🔍 Análise UX:

✅ **O que funciona:**
- Usuário vê quais cenários será comparados
- Taxa de investimento é pergunta relevante

⚠️ **Confusão 1: Checkboxes vs Botão "Simular"**
- Usuário pode desselecionar TODOS (erro?)
- Não há validação: "Selecione pelo menos 1 cenário"

⚠️ **Confusão 2: "Compra à Vista"**
- Se não tem capital, por que está marcada?
- Deveria ser condicional: "Se capital > valor imóvel"

⚠️ **Confusão 3: Taxa de Retorno**
- Muito técnico para usuário comum
- Deveria ter preset: "Conservador (5%) / Moderado (7%) / Agressivo (9%)"

⚠️ **Confusão 4: FGTS**
- Se não tem FGTS (Etapa 2), por que pergunta?
- Deveria ser condicional

#### 💡 **Sugestão de Melhoria:**

```
ETAPA 5 (Revisada):

1. "Qual(is) cenários quer comparar?"
   ☑️ Financiamento (PRICE/SAC)
   ☑️ Consórcio
   ☑️ Aluguel + Investimento
   ☑️ Compra à Vista [APENAS se capital suficiente]
   └─ Mínimo 2 cenários selecionados

2. "Se investir (aluguel+inv), qual retorno espera?"
   ├─ 🟢 Conservador: 5% ao ano
   ├─ 🟡 Moderado: 7% ao ano
   ├─ 🔴 Agressivo: 9% ao ano
   └─ Customizado: ___ % ao ano

3. [CONDICIONAL - SE FGTS > 0 em Etapa 2]
   "Usar FGTS para reduzir dívida?"
   ├─ Sim, a cada 24 meses
   ├─ Não, apenas investir
```

---

## 🔄 FLUXO DE DADOS: Onde Vai Cada Informação?

```
ETAPA 1 (Situação)
├─ situacao_atual → determina "custo_aluguel_durante"
├─ aluguel_atual → TODOS OS 5 CENÁRIOS
│  ├─ Financiamento PRICE/SAC: Comparação
│  ├─ Consórcio: Enquanto espera contemplação
│  ├─ Aluguel+Inv: Custo até compra
│  └─ Compra à Vista: Investindo restante

ETAPA 2 (Capital)
├─ poupanca → entrada (20% do imóvel alvo)
├─ fgts_saldo → PRICE/SAC (amortização + desconto 0% juros)
├─ imovel_atual → [NÃO USADO] Valor de revenda?
│  └─ ❌ PROBLEMA: Se vai vender, reduziria entrada necessária

ETAPA 3 (Objetivo)
├─ valor_imovel_alvo → principal de TODOS os cenários
├─ prazo_desejado → converte prazo_meses (5 anos = 60m)
└─ cidade → [FUTURO] ajustes regionais de preço

ETAPA 4 (Renda)
├─ renda_familiar_bruta → cálculo FGTS mensal (8%)
│  ├─ PRICE/SAC: FGTS acumula e amortiza a cada 24m
│  └─ Limite de LTV (% máximo financiável)
├─ dependentes → [NÃO USADO] ❌
└─ tipo_renda → [NÃO USADO] ❌

ETAPA 5 (Cenários)
├─ comparar_price → se True: calcula PRICE
├─ comparar_sac → se True: calcula SAC
├─ comparar_consorcio → se True: calcula Consórcio
├─ comparar_aluguel_inv → se True: calcula Aluguel+Inv
├─ taxa_investimento → Aluguel+Inv (rentabilidade esperada)
└─ usar_fgts → PRICE/SAC (amortização extra)

RESULTADO (Página de Resultados)
├─ Recomendação: cenário com menor custo total
├─ 5 Cartões: cada cenário detalhado
├─ Alertas CDC: sobre seguros
├─ Tabela Comparativa: lado a lado
└─ CTA: "Conversar com especialista"
```

---

## 🚨 GAPS E PROBLEMAS IDENTIFICADOS

### 1️⃣ **Dados Coletados Mas Não Utilizados**

| Campo | Coletado em | Usado em | Status |
|-------|------------|---------|--------|
| `dependentes` | Etapa 4 | ❌ NUNCA | REMOVER ou USAR |
| `tipo_renda` | Etapa 4 | ❌ NUNCA | REMOVER ou USAR |
| `imovel_atual_valor` | Etapa 2 | ❌ NÃO | Deveria ajustar entrada |

**Ação:** Remover campos não utilizados OU implementar uso real

---

### 2️⃣ **Dados Necessários Mas Não Coletados**

| Dado | Por que precisa | Onde entra |
|------|-----------------|-----------|
| Outras despesas | Calcular comprometimento de renda | LTV, aprovação |
| Estabilidade renda | Risco de financiamento | Sugestão de prazo |
| Forma de pagamento preferida | UX | Mostrar PRICE vs SAC |
| Idade do cliente | FGTS tem limite de saque | Plano futuro |

**Ação:** Adicionar questões relevantes ou remover necessidade

---

### 3️⃣ **Lógica Condicional Faltante**

Perguntas que deveriam ser condicionais:

```javascript
// ❌ ATUAL (sem lógica)
Se Etapa 1 = "aluga"
  └─ Ainda assim pergunta sobre "imovel_atual_valor"?

// ✅ DEVERIA SER
Se Etapa 1 = "aluga"
  └─ Não perguntar sobre imóvel atual

// ❌ ATUAL (sem lógica)
Se Etapa 5 = dependentes selecionados
  └─ Ainda assim não usa em cálculos?

// ✅ DEVERIA SER
Se Etapa 5 != dependentes
  └─ Usar para calcular % mínimo de renda disponível
```

---

### 4️⃣ **Contexto Confuso para Usuário**

```
Pergunta atual: "Qual a renda familiar BRUTA?"

Problema: Usuário pensa "Por que bruta? Pago com minha renda LÍQUIDA!"

Solução: Explicar
  "Usamos a renda BRUTA porque bancos calculam 
   limite de financiamento com base nisso, 
   considerando FGTS (8% de abono mensal)."
```

---

### 5️⃣ **Dados de Entrada Não Validados**

```
Exemplo de validação faltante:

1. Se aluguel_atual = 0 e situacao_atual = "aluga"
   └─ ❌ Aviso: "Aluga mas aluguel = 0? Verificar"

2. Se poupanca < (valor_imovel * 0.2)
   └─ ⚠️ Aviso: "Entrada < 20% - Pode ter restrições"

3. Se taxa_investimento > 15%
   └─ ⚠️ Aviso: "Taxa acima do mercado? Revisar expectativa"

4. Se renda_familiar < aluguel_atual * 3
   └─ ⚠️ Aviso: "Aluguel é 33%+ da renda - Alto!"
```

---

## 🎯 RESUMO: O USUÁRIO QUER ENTENDER

```
┌─────────────────────────────────────────────┐
│ "Sou ALUGUEL ou COMPRA?"                     │
│ ├─ Quanto custa hoje (aluguel)               │
│ └─ Quanto custaria depois (financiamento)    │
├─────────────────────────────────────────────┤
│ "QUANTO PRECISO DE ENTRADA?"                 │
│ ├─ Tenho capital: $ ___                      │
│ ├─ Tenho FGTS: $ ___                         │
│ └─ Faltam: $ ___                             │
├─────────────────────────────────────────────┤
│ "QUAL A MELHOR OPÇÃO PARA MIM?"              │
│ ├─ Financiamento (Caixa/Itaú/etc)           │
│ ├─ Consórcio (contemplação)                  │
│ ├─ Aluguel + Investir                        │
│ └─ Comprar à vista                           │
├─────────────────────────────────────────────┤
│ "QUANTO VOU PAGAR POR MÊS?"                  │
│ ├─ Cenário A: R$ 2.000/mês                   │
│ ├─ Cenário B: R$ 2.500/mês                   │
│ └─ Qual é o mais barato?                     │
├─────────────────────────────────────────────┤
│ "QUANTO VOU GASTAR NO TOTAL?"                │
│ ├─ 30 anos: R$ XXX.XXX                       │
│ ├─ 25 anos: R$ YYY.YYY                       │
│ └─ E se usar FGTS?                           │
├─────────────────────────────────────────────┤
│ "ESTOU NO CAMINHO CERTO?"                    │
│ ├─ Recomendação clara (melhor opção)         │
│ ├─ Alertas: "Cuidado com esses riscos"       │
│ └─ Próximos passos: "O que fazer agora"      │
└─────────────────────────────────────────────┘
```

---

## ✅ ESTAMOS NO CAMINHO CERTO?

### Pontos Fortes ✅
1. ✅ Fluxo lógico de 5 etapas
2. ✅ Perguntas geralmente claras
3. ✅ Múltiplos cenários para comparação
4. ✅ Integração com SAC_Realista (dados reais)
5. ✅ Alertas CDC educando consumidor

### Pontos a Melhorar ⚠️
1. ⚠️ Remover/usar dados coletados mas não utilizados
2. ⚠️ Adicionar contexto/explicação para cada pergunta
3. ⚠️ Implementar lógica condicional adequada
4. ⚠️ Validar dados de entrada
5. ⚠️ Simplificar Etapa 5 (menos checkboxes, mais direcionamento)

### Próximos Passos 🚀
1. 🔄 Validar fluxo com usuários reais (UX testing)
2. 📱 Adaptar para mobile (interface atual é responsiva?)
3. 📊 Adicionar visão de "quanto falta economizar"
4. 🏦 Integrar dados Caixa Federal (quando tiver PDF)
5. 💬 ChatBot educativo antes do wizard (orientação)

---

## 📋 CONCLUSÃO

**Diagnóstico:** Arquitetura do wizard é BOA, mas há **ineficiências no fluxo UX**

**Recomendação:** Implementar melhorias em 2 sprints:

**Sprint 1 (Crítico):**
- ✅ Remover campos não utilizados
- ✅ Adicionar contexto/explicações
- ✅ Validar dados de entrada

**Sprint 2 (Melhorias):**
- ✅ Lógica condicional avançada
- ✅ UX testing com usuários
- ✅ Integração com dados reais de bancos

**Atual:** 7/10 (funciona bem, mas pode ser mais intuitivo)
**Após melhorias:** 9/10 (excelente fluxo UX)

