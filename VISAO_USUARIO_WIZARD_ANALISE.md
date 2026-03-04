# 🎯 VISÃO DE USUÁRIO: Análise Executiva do Wizard

## TL;DR - O Que o Usuário Quer

```
"Quero saber: devo COMPRAR ou ALUGAR?
 Se comprar: qual é o melhor jeito?
 Financiamento? Consórcio? Compra à vista?
 Quanto vou pagar?
 Estou fazendo a coisa certa?"
```

---

## ✅ ESTÁ FUNCIONANDO BEM

### 1. **Perguntas Fazem Sentido** ✅

Usuário entende naturalmente:
```
Etapa 1: "Onde você mora?" → Claro!
Etapa 2: "Quanto tem guardado?" → Fácil!
Etapa 3: "Quanto custa o imóvel que quer?" → Óbvio!
Etapa 4: "Quanto ganha?" → Normal!
Etapa 5: "Qual cenário quer ver?" → Faz sentido!
```

### 2. **Comparação Entre Cenários** ✅

Mostra lado a lado:
- 💰 PRICE vs SAC (qual parcela é menor?)
- 💳 Consórcio (vale a pena esperar?)
- 🏠 Aluguel+Invest (ficar alugando pode ser melhor?)
- 🎯 Recomendação clara (essa é a melhor opção)

### 3. **Educação do Consumidor** ✅

Alertas mostram:
- ⚖️ Seus direitos (Lei 12.490/2011)
- 💰 Economia em seguros (pode poupar R$ 12k+)
- 📋 Como agir (passos concretos)

---

## ⚠️ PROBLEMAS ENCONTRADOS

### 🔴 CRÍTICO: Dados Coletados Mas Nunca Usados

```javascript
// Etapa 2: Usuário informa
imovel_atual_valor = 200000;  // Vai vender este imóvel

// Problema: Sistema IGNORA este valor
entrada = capital_guardado;   // ❌ Deveria ser:
                              // entrada = capital_guardado + imovel_atual_valor

// Resultado: TODOS os 5 cenários calculam entrada errada!
```

**Impacto:** Usuário com R$ 50k guardado + imóvel de R$ 200k = R$ 250k de entrada
Mas sistema calcula como se tivesse apenas R$ 50k!

---

### 🔴 CRÍTICO: Tipo de Renda Não Afeta Limite

```javascript
// Etapa 4: Usuário marca "Autônomo"
tipo_renda = "autonomo";

// Problema: Sistema IGNORA isto
limite_financiamento = renda * 3;  // ❌ Deveria ser:
                                   // limite_financiamento = renda * 2.1
                                   // (autônomo consegue ~70% que CLT)

// Resultado: Limite super-estimado para autônomos!
```

---

### 🔴 CRÍTICO: Dependentes Não Reduzem % Máximo

```javascript
// Etapa 4: Usuário marca "3 dependentes"
dependentes = 3;

// Problema: Sistema IGNORA isto
max_percentual_renda = 0.30;   // ❌ Deveria considerar:
                                // max_percentual_renda = 0.25;
                                // (com dependentes, é menor)

// Resultado: Comprometimento de renda pode estar errado!
```

---

### 🟠 ALTO: Falta Validação de Dados

**Cenário 1: Aluguel = R$ 0**
```
Usuário marca "aluga" em Etapa 1
Mas aluguel = R$ 0 em Etapa 1

Sistema não avisa ❌
→ Cálculos todos errados
```

**Cenário 2: Renda < Aluguel**
```
Usuário informa:
  renda = R$ 1.000
  aluguel = R$ 1.500

Sistema não avisa ❌ (Impossível!)
→ Cálculos absurdos
```

**Cenário 3: Capital > Imóvel**
```
Usuário informa:
  capital = R$ 500.000
  imovel = R$ 300.000

Sistema não diz: "Você pode comprar à vista!"
```

---

### 🟠 ALTO: Não Pergunta Despesas Importantes

**Falta:**
```
Despesas fixas mensais (além de aluguel):
  ├─ Educação filhos?
  ├─ Carro/Combustível?
  ├─ Seguros?
  ├─ Internet/Telefone?
  └─ Outras dívidas (cheque especial, crédito)?

Resultado: % de comprometimento de renda impreciso!
```

---

### 🟡 MÉDIO: Campos Desnecessários

```
Etapa 3: Por que pergunta "Cidade"?
├─ Recolhe "São Paulo"
├─ Mas... não usa em lugar nenhum!
└─ Deveria ser: "Futuro: vai integrar com Zap/Imobiliário"

Etapa 5: Por que pergunta FGTS se não tem?
├─ Se fgts_saldo = 0 em Etapa 2
├─ Por que pergunta "Usar FGTS?" em Etapa 5?
└─ Deveria ser: condicional
```

---

## 🎨 FLUXO IDEAL (SUGESTÃO)

```
┌───────────────────────────────────────────────────────────────┐
│ HOJE: Fluxo Atual                                              │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│ Pergunta 1: Onde mora?                                         │
│ Pergunta 2: Quanto tem guardado + FGTS + Imóvel atual         │
│ Pergunta 3: Qual imóvel quer? (cidade, valor, prazo)          │
│ Pergunta 4: Renda, dependentes, tipo de renda                 │
│ Pergunta 5: Qual cenário comparar?                            │
│                                                                │
│ ❌ Problema: Coleta mas não usa alguns dados                  │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│ IDEAL: Fluxo Otimizado                                         │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│ Passo 1: SITUAÇÃO ATUAL                                        │
│ ├─ "Você aluga, possui próprio, ou mora com família?"        │
│ └─ [Se aluga] "Qual o aluguel mensal?"                        │
│                                                                │
│ Passo 2: CAPITAL PARA ENTRADA                                 │
│ ├─ "Quanto tem guardado?"                                     │
│ ├─ "Tem FGTS? [Sim/Não/Não sei - link FGTS]"                 │
│ └─ [Condicional: se "possui"] "Vai vender? Por quanto?"       │
│    → Total entrada = guardado + FGTS + venda imóvel           │
│                                                                │
│ Passo 3: DESPESAS FIXAS (NOVO!)                               │
│ ├─ "Outras despesas mensais?"                                 │
│ │  ├─ Educação: R$ ___                                        │
│ │  ├─ Carro: R$ ___                                           │
│ │  ├─ Seguro/Saúde: R$ ___                                    │
│ │  └─ Total: R$ ___ (calculado)                               │
│ └─ Aviso: "Com aluguel + despesas = 40% da renda!"            │
│                                                                │
│ Passo 4: RENDA E TIPO                                          │
│ ├─ "Renda bruta total? R$ ___"                                │
│ ├─ "Tipo de renda?"                                           │
│ │  ├─ ◉ CLT/Servidor (100% limite)                            │
│ │  ├─ ◯ Autônomo (70% limite)                                 │
│ │  └─ ◯ PJ/Empresário (60% limite)                            │
│ │     → Informação: "Isso afeta limite de aprovação"          │
│ ├─ "Dependentes?"                                              │
│ │  └─ 0 / 1 / 2 / 3+ → Afeta % máximo de comprometimento      │
│ └─ Resumo calculado:                                           │
│    "Você pode comprometer até R$ 1.200/mês de renda"          │
│                                                                │
│ Passo 5: OBJETIVO                                              │
│ ├─ "Quanto custa o imóvel que quer? R$ ___"                   │
│ ├─ "Em quantos anos comprar? ___ anos" [ou slider]            │
│ └─ [Condicional] "Qual cidade?" [Autocomplete]                │
│                                                                │
│ Passo 6: CENÁRIOS (SIMPLIFICADO!)                             │
│ ├─ "Qual(is) opções quer ver?"                                │
│ ├─ ☑ Financiamento (PRICE ou SAC?)                            │
│ ├─ ☑ Consórcio                                                │
│ ├─ ☑ Aluguel + Investimento                                   │
│ ├─ ☑ Compra à Vista [Habilitado só se capital >= imóvel]      │
│ └─ [Condicional: se tem FGTS] "Usar FGTS? Sim/Não"            │
│                                                                │
│ ✅ RESULTADO: Todos dados coletados SÃO USADOS!               │
└───────────────────────────────────────────────────────────────┘
```

---

## 📊 MATRIZ DE DECISÃO

```
DECIDA PARA CADA CAMPO:
┌────────────────────────────┬──────────┬─────────────────┐
│ Campo                      │ Usar em? │ Decisão          │
├────────────────────────────┼──────────┼─────────────────┤
│ dependentes                │ ❌ Não   │ IMPLEMENTAR uso  │
│ tipo_renda                 │ ❌ Não   │ IMPLEMENTAR uso  │
│ imovel_atual_valor         │ ❌ Não   │ IMPLEMENTAR uso  │
│ cidade                     │ ❌ Não   │ REMOVER ou USAR  │
│ outras_despesas            │ ❌ Falta │ ADICIONAR campo  │
├────────────────────────────┼──────────┼─────────────────┤
│ situacao_atual             │ ✅ Sim   │ Manter           │
│ aluguel_atual              │ ✅ Sim   │ Manter           │
│ capital_guardado           │ ✅ Sim   │ Manter           │
│ fgts_saldo                 │ ✅ Sim   │ Manter           │
│ valor_imovel               │ ✅ Sim   │ Manter           │
│ prazo_meses                │ ✅ Sim   │ Manter           │
│ renda_familiar_bruta       │ ✅ Sim   │ Manter           │
│ taxa_investimento          │ ✅ Sim   │ Manter           │
│ usar_fgts                  │ ✅ Sim   │ Manter           │
└────────────────────────────┴──────────┴─────────────────┘
```

---

## 🎯 DIAGNÓSTICO FINAL

### Pontuação: 7/10

**O que está bem (7 pontos):**
- ✅ Estrutura de 5 etapas faz sentido
- ✅ Perguntas são claras
- ✅ Múltiplos cenários permitem comparação
- ✅ Alertas educam consumidor
- ✅ SAC_Realista tem dados reais
- ✅ Template é responsivo
- ✅ Cálculo de FGTS mensal está correto

**O que não está (3 pontos perdidos):**
- ❌ Campos coletados mas não utilizados (3 campos)
- ❌ Falta validação de dados (impossíveis/absurdos)
- ❌ Não pergunta despesas importantes
- ❌ Lógica condicional inadequada

---

## 🚀 RECOMENDAÇÃO

**Atual:** Sistema funciona, mas tem ineficiências.

**Ação:** Em 2 sprints, pode subir para 9/10:

```
SPRINT 1 (1-2 semanas): CRÍTICO
├─ [ ] Usar imovel_atual_valor em cálculos
├─ [ ] Usar tipo_renda para limite de financiamento
├─ [ ] Usar dependentes para % máximo
├─ [ ] Adicionar validação de dados
└─ [ ] Tornar FGTS condicional

SPRINT 2 (2-3 semanas): IMPORTANTE
├─ [ ] Adicionar perguntas sobre despesas fixas
├─ [ ] Lógica condicional para "Compra à Vista"
├─ [ ] UX Testing com usuários reais
└─ [ ] Documentar fluxo final para dev
```

**ROI:** Após implementar:
- ✅ Cálculos 100% precisos
- ✅ Experiência UX melhor (menos confusão)
- ✅ Recomendações mais realistas
- ✅ Usuários mais satisfeitos

---

## 💬 FEEDBACK PARA USUÁRIO

> "Estamos no caminho CERTO! 
>  O wizard tem boa arquitetura, mas precisa de ajustes para usar TUDO que coleta.
>  Vou revisar os 3 campos não utilizados e adicionar lógica condicional.
>  Resultado: Sistema vai de 70% eficiente para 95% eficiente."

