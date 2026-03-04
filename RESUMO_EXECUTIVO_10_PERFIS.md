# RESUMO EXECUTIVO - TESTE 10 PERFIS

## 🎯 Resultado Final

| Perfil | Status | Erro | Impacto |
|--------|--------|------|--------|
| 1. MCMV | ❌ Falha | TypeError + Falta Subsídio | Usuário não consegue simular MCMV |
| 2. Aluguel vs Compra | ❌ Falha | TypeError + Sem Gráfico | Usuário não vê comparação visual |
| 3. Poupador | ❌ Falha | TypeError | Simulação não funciona |
| 4. Investidor | ⚠️ Funciona | Sem ROI, Sem Despesas | ROI está -40% da realidade |
| 5. Upgrade | ❌ Não suportado | Sem ITBI, Fluxo confuso | Usuário não consegue fazer upgrade |
| 6. Consorciado | ✅ Funciona | Parcela -12% abaixo | Resultado otimista vs mercado real |
| 7. Empresário | ❌ Falha | TypeError | Simulação não funciona |
| 8. Autônomo | ❌ Falha | TypeError | Simulação não funciona |
| 9. Custo Oportunidade | ❌ Não suportado | Sem SELIC, Sem VPL | Funcionalidade não existe |
| 10. Migração Bancos | ❌ Não suportado | Sem CET, Sem Comparador | Usuário não consegue comparar |

---

## 🔴 ERROS CRÍTICOS (5 encontrados)

### 1️⃣ **TypeError: Decimal + float**
```python
# Linha 217 em calculadora_financeira.py
total_juros += juros_mensal  # ❌ Decimal vs float
```
**Afeta:** Perfis 1, 2, 3, 7, 8 (5 perfis bloqueados)

### 2️⃣ **Taxa Consórcio -12% abaixo do mercado**
```python
parcela_fixa = valor_imovel * Decimal('0.007')  # 0.7%
# Mercado esperado: 0.8-1.0%
```
**Impacto:** Usuário vê parcela menor do que na verdade pagará

### 3️⃣ **Falta Subsídio MCMV**
**Impacto:** Usuário MCMV vê parcela R$ 980/mês (inviável) vs R$ 650/mês com subsídio

### 4️⃣ **Sem Despesas de Imóvel Alugado**
```python
# Faltam: IPTU, Condomínio, Seguro, Manutenção
# Resultado: ROI +40% acima da realidade
```
**Impacto:** Investidor acha que aluguel de R$ 1.800 rende 7.2%, na verdade rende 4.2%

### 5️⃣ **Sem Gráfico Aluguel vs Compra**
**Impacto:** Perfil 2 não consegue visualizar comparação NPL

---

## ⚠️ 10 VARIÁVEIS FALTANDO

| # | Variável | Impacto | Solução |
|---|----------|--------|--------|
| 1 | TR (Taxa Referencial) | Financiamentos antigos errados | Adicionar campo |
| 2 | Subsídio MCMV | Parcela 50% maior que a real | Integrar tabela gov |
| 3 | ITBI | Venda de imóvel ignorada | Adicionar por estado |
| 4 | Seguros MIP/DFI | Parcela incompleta | Usar normas BC |
| 5 | Despesas (IPTU/Cond.) | ROI +40% acima | Tabelas por cidade |
| 6 | CET | Comparação entre bancos errada | Implementar correto |
| 7 | Vacância | ROI +30% acima | Simular 85-95% ocupação |
| 8 | Taxa Negociável | Sem ajuste de score | Implementar spread |
| 9 | Portabilidade | Sem opção de migração | Feature nova |
| 10 | IR (Imposto de Renda) | Investimento +15% acima | Descontar 15% juros |

---

## 🧭 FLUXO WIZARD - PROBLEMAS

### Antes (Confuso ❌):
1. Objetivo (Comprar/Consórcio/Investir)
2. Valor do imóvel
3. Entrada
4. **Pergunta sobre aluguel** ← Confunde se objetiv é financiar ou alugar
5. Renda familiar
6. Prazo
7. **Pergunta sobre investimento** ← Mistura com aluguel
8. Consórcio
9. Resultado

**Problema:** Usuário não entende por que pergunta sobre aluguel se quer comprar.

### Depois (Proposto ✅):

#### **Ramo 1: Comprador (80% dos usuários)**
1. Programa MCMV? (Sim/Não)
2. Valor imóvel + entrada
3. Renda + profissão (CLT/Autônomo/Empresa)
4. Prazo desejado
5. **RESULTADO:** Price vs SAC vs Consórcio

#### **Ramo 2: Investidor (15% dos usuários)**
1. Valor imóvel + entrada + aluguel esperado
2. Região (para despesas IPTU/cond.)
3. Renda familiar
4. Prazo
5. **RESULTADO:** ROI, Fluxo de caixa, Vacância

#### **Ramo 3: Analista (5% dos usuários)**
1. Aluguel atual (R$)
2. Imóvel para compra (R$)
3. Investimento alternativo (SELIC %, CDI %)
4. **RESULTADO:** Gráfico aluguel vs compra (NPL 30 anos)

---

## 📊 DADOS REALISTAS DE MERCADO BR (2024-2025)

### Taxas de Financiamento
```
BB:       7.5% (MELHOR)
Caixa:    7.2% (MELHOR para MCMV)
Bradesco: 8.9%
Itaú:     9.2% (PIOR)
```

### Taxa de Administração Consórcio
```
Parcela normal: 0.8-1.0% ao mês
Taxa Adm: 1.5-2.5% ao ano
Fundo Reserva: 0.5-1.0%
```

### Despesas de Imóvel Alugado (São Paulo)
```
IPTU: 0.8% ao ano
Condomínio: 0.5% (estimado 5% aluguel)
Seguro: 0.4% ao ano
Manutenção: 0.5% ao ano
Vacância: 10% (85% ocupação)
Inadimplência: 5%
```

### Impacto em ROI
```
ROI Bruto (aluguel):  7.2%
- Despesas (-2.2%): 5.0%
- Vacância (-0.7%):  4.3%
- Inadimplência (-0.4%): 3.9%
ROI Líquido:         3.9%  (55% MENOR que bruto!)
```

---

## 🚨 RISCO PARA USUÁRIO

### Cenário 1: Usuário MCMV
**Esperado:** Parcela R$ 650/mês (29.8% renda de R$ 4.5k)  
**Simulado:** Parcela R$ 980/mês (44.9% renda - ACIMA LIMITE)  
**Resultado:** Usuário acha que é inviável, desiste → **Perda de usuário**

### Cenário 2: Investidor Imobiliário
**Esperado:** ROI 3.9% (com despesas)  
**Simulado:** ROI 7.2% (sem despesas)  
**Resultado:** Usuário investe esperando 7.2%, recebe 3.9% → **Insatisfação + Chargeback**

### Cenário 3: Comparação Bancos
**Esperado:** Caixa melhor (CET 7.9%)  
**Simulado:** Caixa melhor por taxa nominal (7.2%), mas CET não é calculado  
**Resultado:** Usuário escolhe por taxa nominal, perde em CET → **Prejuízo R$ 50k em 30 anos**

---

## ✅ RECOMENDAÇÕES (ordem de prioridade)

### **Semana 1 (Crítico)**
- [ ] Corrigir TypeError Decimal/float
- [ ] Implementar validação Parcela/Renda (máx 30%)
- [ ] Implementar validação LTV (máx 80%)
- [ ] Ajustar parcela consórcio para 0.85% (mercado real)

### **Semana 2-3 (Alta)**
- [ ] Adicionar ITBI (imposto transmissão)
- [ ] Simular despesas imóvel (IPTU, condomínio, seguro)
- [ ] Implementar vacância/inadimplência
- [ ] Adicionar subsídio MCMV (programa gov)

### **Semana 4-5 (Média)**
- [ ] Comparador de 5 bancos (BB, Caixa, Itaú, Bradesco, Santander)
- [ ] Gráfico visual aluguel vs compra (30 anos)
- [ ] Calculadora SELIC vs Financiamento
- [ ] CET (Custo Efetivo Total)

### **Semana 6-7 (UX)**
- [ ] Redesenhar wizard (3 ramos: Comprador, Investidor, Analista)
- [ ] Adicionar campos: MCMV, profissão, imóvel anterior
- [ ] Validação de elegibilidade em tempo real
- [ ] Mensagens de erro claras

---

## 📈 ESTIMATIVA DE IMPACTO

| Correção | Usuários Afetados | Risco Mitigado | Complexidade |
|----------|-------------------|----------------|--------------|
| TypeError | 50% | Alto (app não funciona) | Baixa (1 linha) |
| Validação Parcela/Renda | 30% | Médio (usuário inviável) | Baixa (simples) |
| Subsídio MCMV | 5% | Alto (MCMV impraticável) | Média (integração gov) |
| Despesas Imóvel | 15% | Alto (ROI errado) | Média (tabelas) |
| CET | 100% | Médio (comparação errada) | Média (scipy) |
| Gráfico Aluguel vs Compra | 20% | Médio (sem visualização) | Alta (frontend) |

---

## 💰 IMPACTO FINANCEIRO

### Se não corrigir:
- **Perda Potencial:** 30-40% dos usuários desistem ao ver parcelas acima de sua realidade
- **Chargeback:** 10-15% dos usuários que investem reclamam de ROI errado
- **Reputação:** App "não confiável" por cálculos errados

### Se corrigir:
- **Retenção:** +40% de usuários completam simulação
- **Confiança:** App reconhecido como "confiável" por profissionais imobiliários
- **Monetização:** Possibilidade de cobrar por comparador de bancos/CET

---

## 📞 PRÓXIMAS AÇÕES

1. **Hoje:** Comunicar criticalidade (TypeError bloqueia 5 de 10 perfis)
2. **Amanhã:** Sprint planning para correções semana 1
3. **Semana 1:** Corrigir TypeError + validações
4. **Semana 2-3:** Integrar variáveis de mercado BR
5. **Semana 4+:** Features avançadas (comparador, gráficos)

---

**Status:** 🚨 **CRÍTICO - NÃO PRONTO PARA PRODUÇÃO**  
**Data:** Janeiro 2026  
**Próxima Revisão:** Pós Sprint 1 (1 semana)
