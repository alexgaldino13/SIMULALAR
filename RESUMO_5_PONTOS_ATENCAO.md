# 🚀 RESUMO EXECUTIVO: 5 PONTOS DE ATENÇÃO

**Data:** 25 de Janeiro de 2026  
**Documentação Completa:** [ANALISE_5_PONTOS_ATENCAO.md](ANALISE_5_PONTOS_ATENCAO.md)

---

## 📊 Matriz de Decisão

| Ponto | O Quê | Onde | Impacto | Status | Estimativa |
|-------|-------|------|---------|--------|-----------|
| **1️⃣ TR** | Taxa Referencial corrige saldo devedor | `calculadora_financeira.py:L800` | Aumento +1,2% no custo total | ❌ Não implementado | 4h |
| **2️⃣ IOF** | Imposto sobre financiamento (0,938%) | `calculadora_financeira.py:NEW` | Custo +R$ 5-6k em 30 anos | ❌ Não implementado | 3h |
| **3️⃣ IPTU/Cond** | Despesas do imóvel mensais | `calculadora_financeira.py:NEW` | Parcela real +R$ 300-800/mês | ⚠️ Parcialmente | 3h |
| **4️⃣ IR Rend** | Imposto de Renda (15-22,5%) | `calculadora_financeira.py:L1200` | Reduz rentabilidade em -17% | ❌ Não implementado | 4h |
| **5️⃣ Consórcio** | Parcela 0.7% + custos ocultos | `calculadora_financeira.py:L328` | Usuário vê R$3,5k mas paga R$4,3k | 🟠 Bugado | 2h |

---

## 🎯 Análise Rápida por Ponto

### 1️⃣ TR - Taxa Referencial
**Criticidade:** 🔴 CRÍTICO | **Complexidade:** 🟠 MÉDIA  

**Problema:**
- Código atualmente ignora TR (usa 1.0 = sem correção)
- Contrato Itaú deveria aplicar 0.15% a.m.
- Impacto: +R$ 9.000 em 30 anos

**Solução:**
- Adicionar `tr_mensal` como parâmetro
- Corrigir saldo: `saldo_novo = saldo_anterior × (1 + tr_mensal)`

---

### 2️⃣ IOF - Imposto Sobre Operações Financeiras
**Criticidade:** 🟠 ALTO | **Complexidade:** 🟢 BAIXO  

**Problema:**
- Não é calculado (ou é ignorado)
- Lei nº 7.798/89 exige 0,938% + 0,5% das parcelas
- Custo real: ~R$ 5.000-6.000 em 360 meses

**Solução:**
- Nova função: `calcular_iof(valor_financiado, parcelas_mensais)`
- Integrar no fluxo: mostrar "Valor financiado: R$ 327k | IOF: R$ 5,2k"

---

### 3️⃣ IPTU / CONDOMÍNIO
**Criticidade:** 🟠 ALTO | **Complexidade:** 🟢 BAIXO  

**Problema:**
- IPTU: ~1,2% a.a. do valor venal
- Condomínio: R$ 300-2.000/mês
- Não está integrado nas simulações

**Solução:**
- Nova função: `calcular_despesas_imovel(valor, tipo, aliquota_iptu, condominio)`
- Etapa 3 do Wizard: adicionar campos
- Mostrar "Parcela Real = Financiamento + IPTU + Cond"

---

### 4️⃣ IR Sobre Rendimentos
**Criticidade:** 🟠 ALTO | **Complexidade:** 🟠 MÉDIO  

**Problema:**
- Simulações de investimento ignoram IR
- Poupança: 17,5% | CDI: 15-22,5% (tabela regressiva)
- Reduz rentabilidade de ~12% a.a. para ~10% a.a.

**Solução:**
- Função: `calcular_ir_rendimentos(rendimento, tipo_investimento, dias_aplicacao)`
- Etapa 7 do Wizard: tipo de investimento + aplicar IR?
- Mostrar comparativo: "Rentabilidade bruta vs. líquida"

---

### 5️⃣ BUG CONSÓRCIO (0.7%)
**Criticidade:** 🔴 CRÍTICO | **Complexidade:** 🟢 BAIXO  

**Problema:**
```
Código mostra:  "Parcela: R$ 3.500" (só 0.7%)
Usuário paga:   R$ 3.500 + R$ 625 (taxa adm) + R$ 208 (fundo) = R$ 4.333

Diferença: +R$ 833/mês oculto (23% a mais!)
```

**Solução:**
- Função: `simular_consorcio_corrigido()` 
- Mostrar breakdown claro:
  ```
  PARCELA MENSAL: R$ 4.333
  ├─ Base (0.7%): R$ 3.500
  ├─ Taxa Adm: R$ 625
  └─ Fundo Reserva: R$ 208
  ```

---

## 💡 Recomendações

### Ordem de Implementação:
```
1. BUG CONSÓRCIO (crítico + fácil)
2. IOF (fácil + impacto visível)
3. IPTU/Condomínio (fácil + melhora UX)
4. TR (médio + crítico para precisão)
5. IR Rendimentos (médio + importante para investimentos)
```

### Tempo Estimado:
- **Total:** 16 horas de desenvolvimento
- **Testes:** 4 horas
- **Integração:** 4 horas
- **Documentação:** 2 horas
- **⏱️ Total: ~1 semana**

---

## 📋 Checklist de Implementação

### Fase 1: CRÍTICO (1-2 dias)
- [ ] Bug Consórcio: corrigir fórmula
- [ ] IOF: implementar função
- [ ] IPTU/Cond: integrar em cenários

### Fase 2: IMPORTANTE (2-3 dias)
- [ ] TR: adicionar parâmetro
- [ ] IR: implementar função

### Fase 3: VALIDAÇÃO (1-2 dias)
- [ ] Testar contra PDFs Itaú
- [ ] Validar precisão 99%+
- [ ] Atualizar Wizard

---

## 🔗 Links Importantes

- [ANALISE_5_PONTOS_ATENCAO.md](ANALISE_5_PONTOS_ATENCAO.md) - Documentação completa
- [ANALISE_CONTRATO_ITAU.md](ANALISE_CONTRATO_ITAU.md) - Validação com contrato real
- [simulacao/calculadora_financeira.py](simulacao/calculadora_financeira.py) - Core functions
- **PDFs Itaú:** `Documentos auxiliares/` 
  - `Contrato Itaú TF224.pdf`
  - `ITAU DEMONSTRATIVO FINANCIAMENTO IMOBILIÁRIO.pdf`

---

**Próximo passo:** Confirmar qual ponto começar! 🚀
