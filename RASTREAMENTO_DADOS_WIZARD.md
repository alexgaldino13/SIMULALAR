# 🔀 RASTREAMENTO DE DADOS: Do Wizard Aos Resultados

## 📊 Matriz de Rastreamento Completa

```
╔════════════════════════════════════════════════════════════════════════════╗
║                         FLUXO COMPLETO DE DADOS                            ║
╚════════════════════════════════════════════════════════════════════════════╝

ENTRADA (WIZARD)
    ↓
TRANSFORMAÇÃO (VIEW)
    ↓
CÁLCULO (ENGINE)
    ↓
SAÍDA (TEMPLATE)

```

---

## 🔴 ETAPA 1: SITUAÇÃO ATUAL

```
┌─────────────────────────────────────────────────────────────────┐
│ INPUT: Situação Atual                                            │
├─────────────────────────────────────────────────────────────────┤
│ [1] Onde você reside?                                            │
│     ├─ ◉ Aluga imóvel                                            │
│     ├─ ◯ Possui imóvel próprio                                   │
│     └─ ◯ Mora com família (sem próprio)                         │
│                                                                  │
│ [2] [Condicional se "aluga"]                                    │
│     Qual o aluguel mensal? R$ ___________________                │
│                                                                  │
│ OUTPUT: wizard_data['situacao_atual'] = "aluga"                 │
│         wizard_data['aluguel_atual'] = 1500.00                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                   (Salvo em Session)
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ USA EM:                                                          │
│ ✓ comparar_cenarios_novo() → aluguel_atual                      │
│   ├─ Calcula custo aluguel em PRICE/SAC                         │
│   ├─ Calcula custo aluguel em Consórcio                         │
│   ├─ Usa como base em Aluguel+Investimento                      │
│   └─ Desconsidera em Compra à Vista (já tem capital)            │
│                                                                  │
│ ✓ Template → Mostra no resumo: "Aluguel atual: R$ 1.500"        │
└─────────────────────────────────────────────────────────────────┘

⚠️ PROBLEMA IDENTIFICADO:
   └─ Se "mora com família" → aluguel_atual = 0 ou NULL
      └─ Afeta cálculos? Deve considerar "aluguel de mercado"
         para comparação realista
```

---

## 🟠 ETAPA 2: CAPITAL DISPONÍVEL

```
┌──────────────────────────────────────────────────────────────────────┐
│ INPUT: Capital Disponível                                             │
├──────────────────────────────────────────────────────────────────────┤
│ [1] Quanto tem guardado (poupança)? R$ _____________________          │
│     OUTPUT: capital_guardado = 50000.00                               │
│                                                                       │
│ [2] Saldo FGTS disponível? R$ _____________________                  │
│     OUTPUT: fgts_saldo = 25000.00                                     │
│                                                                       │
│ [3] Valor do imóvel que possui? R$ _________________ [ou N/A]       │
│     OUTPUT: imovel_atual_valor = 0 (se N/A) ou 200000                │
└──────────────────────────────────────────────────────────────────────┘
                            ↓
                   (Salvo em Session)
                            ↓
┌──────────────────────────────────────────────────────────────────────┐
│ USA EM:                                                               │
│                                                                       │
│ ✓ capital_guardado:                                                   │
│   ├─ PRICE/SAC: entrada = capital_guardado * 0.20                    │
│   │           (se < 20% do imóvel)                                   │
│   ├─ Consórcio: capital inicial para sorteios                        │
│   ├─ Aluguel+Inv: capital base para investimento                     │
│   └─ Compra à Vista: pode comprar se >= valor imóvel                 │
│                                                                       │
│ ✓ fgts_saldo:                                                         │
│   ├─ PRICE/SAC: amortização extra a cada 24 meses                    │
│   │           (reduz prazo automaticamente)                          │
│   ├─ Consórcio: aplica como abono                                    │
│   ├─ Aluguel+Inv: [não usa]                                          │
│   └─ Compra à Vista: soma ao capital                                 │
│                                                                       │
│ ✗ imovel_atual_valor:                                                 │
│   ├─ [NÃO USA EM NENHUM LUGAR]  ❌ BUG                                │
│   └─ Deveria: Somar à entrada se "possui imóvel"                     │
└──────────────────────────────────────────────────────────────────────┘

🚨 PROBLEMA CRÍTICO:
   ├─ Campo coletado mas NUNCA usado
   ├─ Se usuário vai vender imóvel, entrada seria:
   │  capital_guardado + imovel_atual_valor
   │  (não apenas capital_guardado)
   └─ Afeta cálculo de TODOS os 5 cenários!
```

---

## 🟡 ETAPA 3: SEU OBJETIVO

```
┌──────────────────────────────────────────────────────────────────────┐
│ INPUT: Objetivo                                                       │
├──────────────────────────────────────────────────────────────────────┤
│ [1] Valor do imóvel desejado? R$ _____________________                │
│     OUTPUT: valor_imovel = 350000.00                                  │
│                                                                       │
│ [2] Em quantos anos quer comprar?                                    │
│     ◉ 1-3 anos   ◯ 3-5 anos   ◯ 5-10 anos   ◯ 10+ anos              │
│     OUTPUT: prazo_anos = "3-5"                                        │
│     TRANSFORMA EM: prazo_meses = 60 (meio da faixa)                   │
│                                                                       │
│ [3] Qual cidade? [Autocomplete]                                       │
│     OUTPUT: cidade = "São Paulo"                                      │
└──────────────────────────────────────────────────────────────────────┘
                            ↓
                   (Salvo em Session)
                            ↓
┌──────────────────────────────────────────────────────────────────────┐
│ USA EM:                                                               │
│                                                                       │
│ ✓ valor_imovel:                                                       │
│   ├─ PRICE: principal do financiamento - entrada                     │
│   ├─ SAC: principal do financiamento - entrada                       │
│   ├─ Consórcio: valor de contemplação                                │
│   ├─ Aluguel+Inv: meta de compra futura                              │
│   └─ Compra à Vista: se tem capital, compra                          │
│                                                                       │
│ ✓ prazo_meses (convertido):                                          │
│   ├─ Todos os 5 cenários: prazo total de análise                     │
│   └─ Afeta: parcela mensal e juros totais                            │
│                                                                       │
│ ✗ cidade:                                                             │
│   ├─ [COLETADO MAS NÃO USADO]  ❌                                    │
│   ├─ Futuro: Deve ajustar preço regional                             │
│   └─ Futuro: Mostrar imóveis disponíveis em Zap                      │
└──────────────────────────────────────────────────────────────────────┘

⚠️ PROBLEMA:
   └─ Prazo em "faixas" (1-3, 3-5) é impreciso
      Usuário pensa "5 anos" mas sistema calcula "3-5 anos" = 48 meses?
      Melhor: Slider ou input direto "quantos meses"
```

---

## 🟢 ETAPA 4: RENDA & CUSTOS

```
┌──────────────────────────────────────────────────────────────────────┐
│ INPUT: Renda & Custos                                                 │
├──────────────────────────────────────────────────────────────────────┤
│ [1] Renda familiar BRUTA? R$ _____________________                    │
│     OUTPUT: renda_familiar_bruta = 5000.00                            │
│                                                                       │
│ [2] Quantos dependentes?                                              │
│     OUTPUT: dependentes = 2                                           │
│                                                                       │
│ [3] Tipo de renda?                                                    │
│     ◉ Emprego fixo   ◯ Autônomo   ◯ Ambos                            │
│     OUTPUT: tipo_renda = "emprego_fixo"                               │
└──────────────────────────────────────────────────────────────────────┘
                            ↓
                   (Salvo em Session)
                            ↓
┌──────────────────────────────────────────────────────────────────────┐
│ USA EM:                                                               │
│                                                                       │
│ ✓ renda_familiar_bruta:                                               │
│   ├─ Calcula FGTS mensal: fgts_mensal = renda * 0.08                 │
│   │  (Usado em PRICE/SAC para amortização)                           │
│   ├─ Calcula comprometimento: parcela / renda                        │
│   │  (Deve estar <30% para aprovação)                                │
│   └─ Mostrado no resumo                                              │
│                                                                       │
│ ✗ dependentes:                                                        │
│   ├─ [COLETADO MAS NÃO USADO]  ❌                                    │
│   ├─ Deveria: Reduzir % máximo de renda                              │
│   │  (Com dependentes, limite é menor)                               │
│   └─ Ou remover do formulário                                        │
│                                                                       │
│ ✗ tipo_renda:                                                         │
│   ├─ [COLETADO MAS NÃO USADO]  ❌                                    │
│   ├─ Deveria: Afetar limite de financiamento                         │
│   │  (Autônomo consegue ~70% do que empregado CLT)                   │
│   └─ Ou remover do formulário                                        │
└──────────────────────────────────────────────────────────────────────┘

🚨 PROBLEMAS:
   ├─ 2 campos coletados (dependentes, tipo_renda) NÃO USAM
   ├─ Não pergunta sobre OUTRAS DESPESAS FIXAS
   │  (educação, saúde, carro, seguro, etc)
   │  → Afeta real comprometimento de renda
   └─ Falta validação: Se renda muito baixa, avisar
```

---

## 🔵 ETAPA 5: CENÁRIOS & PREFERÊNCIAS

```
┌──────────────────────────────────────────────────────────────────────┐
│ INPUT: Cenários                                                       │
├──────────────────────────────────────────────────────────────────────┤
│ Qual(is) cenário(s) quer comparar? [Checkboxes]                      │
│                                                                       │
│ ☑ Financiamento PRICE                                                │
│ ☑ Financiamento SAC                                                  │
│ ☑ Consórcio                                                          │
│ ☑ Aluguel + Investimento                                             │
│ ☐ Compra à Vista                                                     │
│                                                                       │
│ Taxa esperada de investimento? [Slider]                              │
│ [1% ←→ 15%] atualmente: 7% ao ano                                    │
│                                                                       │
│ ☑ Usar FGTS para amortizar? [Checkbox]                               │
│                                                                       │
│ OUTPUT:                                                               │
│   - comparar_price = True                                             │
│   - comparar_sac = True                                               │
│   - comparar_consorcio = True                                         │
│   - comparar_aluguel_inv = True                                       │
│   - comparar_compra_vista = False                                     │
│   - taxa_investimento = 0.07                                          │
│   - usar_fgts = True                                                  │
└──────────────────────────────────────────────────────────────────────┘
                            ↓
                   calcular_cenarios_novo()
                            ↓
┌──────────────────────────────────────────────────────────────────────┐
│ USA EM:                                                               │
│                                                                       │
│ ✓ comparar_price, comparar_sac, etc:                                 │
│   ├─ Ativa cálculo de cada cenário                                   │
│   └─ Se False: cenário não entra em resultados                       │
│                                                                       │
│ ✓ taxa_investimento:                                                  │
│   └─ Aluguel+Investimento: rentabilidade anual esperada              │
│      (Composto mensalmente)                                          │
│                                                                       │
│ ✓ usar_fgts:                                                          │
│   └─ PRICE/SAC: amortização FGTS a cada 24 meses                     │
│      └─ Reduz prazo automaticamente                                  │
└──────────────────────────────────────────────────────────────────────┘

⚠️ PROBLEMAS:
   ├─ Sem mínimo de cenários selecionados
   │  (usuário pode desselecionar TODOS = erro)
   ├─ "Compra à Vista" sempre desmarcada
   │  (não valida se tem capital)
   ├─ Taxa de investimento complexa
   │  (usuário comum não sabe o que colocar)
   └─ FGTS perguntado mesmo se fgts_saldo = 0
      (deveria ser condicional)
```

---

## 📤 SAÍDA: Página de Resultados

```
┌────────────────────────────────────────────────────────────────────────┐
│ RESULTADO: Análise Comparativa                                         │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ 📊 RESUMO DE ENTRADA:                                                  │
│ ├─ Valor do Imóvel Alvo: R$ 350.000                                    │
│ ├─ Prazo Desejado: 5 anos                                              │
│ ├─ Renda Familiar: R$ 5.000                                            │
│ ├─ Capital Disponível: R$ 50.000                                       │
│ └─ Aluguel Atual: R$ 1.500                                             │
│                                                                         │
│ 🎯 RECOMENDAÇÃO:                                                        │
│ ├─ Melhor Opção: Financiamento SAC                                     │
│ ├─ Razão: Menor custo total (R$ 650.000 vs R$ 680.000)                 │
│ └─ Status: ✓ Você se encaixa (parcela 28% da renda)                    │
│                                                                         │
│ ⚠️ ALERTAS:                                                             │
│ ├─ Seu seguro pode ser mais barato!                                    │
│ │  └─ Economize R$ 46,88/mês com seguro externo                        │
│ └─ Você tem direitos! Contrate seguro em qualquer lugar                │
│                                                                         │
│ 5 CARTÕES CENÁRIOS:                                                    │
│ ├─ [Cartão 1] PRICE: Parcela R$ 2.100 | Juros R$ 490k | Total R$ 700k │
│ ├─ [Cartão 2] SAC: Parcela R$ 2.300→1.600 | Juros R$ 420k | Total R$ 650k
│ ├─ [Cartão 3] Consórcio: Parcela R$ 1.800 | Contemplação? | Total R$ 680k
│ ├─ [Cartão 4] Aluguel+Inv: Parcela R$ 1.500 (aluguel) | Ganho R$ 280k
│ └─ [Cartão 5] Compra à Vista: Não aplica (capital insuficiente)
│                                                                         │
│ 📊 TABELA COMPARATIVA:                                                 │
│ ┌─────────────┬──────────────┬──────────────┬──────────────┐            │
│ │ Cenário     │ Parcela Mês  │ Juros Total  │ Custo Total  │            │
│ ├─────────────┼──────────────┼──────────────┼──────────────┤            │
│ │ PRICE       │ R$ 2.100     │ R$ 490.000   │ R$ 700.000   │            │
│ │ SAC         │ Variável     │ R$ 420.000   │ R$ 650.000   │ ← MELHOR  │
│ │ Consórcio   │ R$ 1.800     │ R$ 330.000   │ R$ 680.000   │            │
│ │ Aluguel+Inv │ R$ 1.500     │ -R$ 150.000  │ R$ 580.000   │            │
│ │ Compra Vista│ N/A          │ N/A          │ N/A          │            │
│ └─────────────┴──────────────┴──────────────┴──────────────┘            │
│                                                                         │
│ 🔗 PRÓXIMOS PASSOS:                                                    │
│ ├─ [ ] Fale com nossos especialistas                                   │
│ ├─ [ ] Solicite cotação formal no seu banco                            │
│ └─ [ ] Leia nossa guia sobre direitos do consumidor                    │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🔴 PROBLEMAS CRÍTICOS ENCONTRADOS

| # | Problema | Etapa | Severidade | Impacto |
|---|----------|-------|------------|---------|
| 1 | `imovel_atual_valor` coletado mas não usado | 2 | 🔴 CRÍTICO | Entrada calculada errada se vai vender |
| 2 | `dependentes` não afeta limite financiamento | 4 | 🔴 CRÍTICO | Aprovação pode estar errada |
| 3 | `tipo_renda` não afeta limite de financiamento | 4 | 🔴 CRÍTICO | Limite pode estar super-estimado |
| 4 | `cidade` coletado mas não usado | 3 | 🟠 ALTO | Sem preço regional |
| 5 | Nenhuma validação de dados | 1-5 | 🟠 ALTO | Usuário pode colocar valores absurdos |
| 6 | FGTS perguntado mesmo se saldo = 0 | 5 | 🟡 MÉDIO | Confusão UX |
| 7 | Compra à Vista sempre desmarcada | 5 | 🟡 MÉDIO | Se não pode comprar, deveria estar desabilida |
| 8 | Falta perguntar outras despesas fixas | 4 | 🟡 MÉDIO | Comprometimento de renda impreciso |

---

## ✅ O QUE ESTÁ CERTO

| Aspecto | Status | Nota |
|--------|--------|------|
| Fluxo lógico das 5 etapas | ✅ | Sequência faz sentido |
| Cálculo de cenários | ✅ | 5 opções bem estruturadas |
| SAC_Realista integrado | ✅ | Dados reais de banco (Itaú) |
| Alertas CDC | ✅ | Educação consumidor funcionando |
| Template responsivo | ✅ | Mobile-friendly |
| Cálculo FGTS mensal | ✅ | Amortização a cada 24 meses |

---

## 💡 PRÓXIMOS PASSOS RECOMENDADOS

**Sprint 1 (Urgente):**
- [ ] Remover ou implementar `dependentes`, `tipo_renda`, `imovel_atual_valor`
- [ ] Adicionar validação de dados em todas as etapas
- [ ] Tornar FGTS condicional (só perguntar se tem)

**Sprint 2 (Importantes):**
- [ ] Adicionar perguntas sobre outras despesas fixas
- [ ] Implementar lógica de "Compra à Vista" (habilitar/desabilitar)
- [ ] UX testing com usuários reais

**Sprint 3 (Futuro):**
- [ ] Integrar preços regionais por cidade
- [ ] Link para Zap/Imobiliário com filtro de cidade
- [ ] ChatBot educativo antes do wizard

