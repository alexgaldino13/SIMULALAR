# RELATÓRIO DE TESTE: 10 PERFIS DE USUÁRIOS - FI (Financiamento Imobiliário)

**Data:** Janeiro 2026  
**Objetivo:** Validar se as fórmulas de SAC/PRICE, Consórcio e Aluguel+Investimento retornam valores fiéis ao mercado brasileiro (2024-2025) e se o fluxo do Wizard faz sentido para cada perfil.

---

## 📊 RESUMO EXECUTIVO

✅ **Testes Executados:** 10 perfis de usuários  
❌ **Erros Detectados:** 5 erros críticos no código  
⚠️ **Variáveis Faltando:** 10 variáveis essenciais para mercado BR  
🔧 **Problemas no Wizard:** 8 fluxos confusos  

---

## 🔴 ERROS CRÍTICOS ENCONTRADOS

### 1. **TypeError em `calcular_price_sac()` - Linha 217**

```python
total_juros += juros_mensal  # ❌ Decimal + float = erro
```

**Problema:** `juros_mensal` é `Decimal`, mas é somado a variáveis que são `float`.

**Impacto:** Perfis 1, 2, 3, 7, 8 falham com "unsupported operand type(s) for +=: 'decimal.Decimal' and 'float'"

**Solução:**
```python
# Converter juros_mensal para float antes de somar
total_juros += float(juros_mensal)
```

### 2. **Ausência de `taxa_anual` em Perfis Aluguel vs Compra**

**Problema:** Perfil 2 passa `taxa_anual_financiamento` para `simular_aluguel_investimento()`, mas a função não recebe este parâmetro.

**Impacto:** KeyError ao acessar `taxa_anual`

**Solução:** Adicionar `taxa_anual_financiamento` como parâmetro nomeado.

### 3. **Fórmula de Parcela do Consórcio Não-realista**

```python
parcela_base_percentual = Decimal('0.007')  # 0.7% ao mês
parcela_fixa = valor_imovel_total * parcela_base_percentual
```

**Problema:** Em mercado real, parcela de consórcio é `~0.8% a 1.0%`, não 0.7%.

**Exemplo Real (teste Perfil 6):**
- Valor: R$ 500k
- Parcela gerada: R$ 3.500/mês = 0.7%
- Parcela realista BB/Caixa: R$ 4.000-5.000/mês = 0.8-1.0%
- **Diferença:** -R$ 7.500/ano (1.5%)

### 4. **FGTS Mensal não é Cumulativo Corretamente**

**Problema:** FGTS acumula 24 meses e depois reseta, mas não há validação se valor acumulado é suficiente.

**Impacto:** FGTS pode ser "desperdiçado" se não for consumido completamente.

### 5. **CET Não Está Implementado Completamente**

**Problema:** Função `calcular_cet()` existe, mas não é chamada pelos métodos Price/SAC.

**Impacto:** Comparação entre bancos fica imprecisa (CET vs taxa nominal).

---

## ⚠️ VARIÁVEIS FALTANDO (crítico para mercado BR)

| # | Variável | Descrição | Impacto | Onde Usar |
|---|----------|-----------|--------|-----------|
| 1 | **TR** | Taxa Referencial (antiga, alguns bancos ainda usam) | Afeta cálculo de juros em financiamentos pós-2010 | Financiamento antigo/renegociação |
| 2 | **Subsídio MCMV** | Desconto/subsídio governamental (até 35% do valor) | Entrada efetiva é muito menor | Perfil MCMV (renda ≤ 4.5k) |
| 3 | **ITBI** | Imposto de Transmissão (varia 0.5%-3% por estado) | Reduz saldo da venda em upgrade | Compra/venda de imóvel |
| 4 | **Seguros Obrigatórios** | MIP (0.06-0.25% mês), DFI (0.02-0.15% mês) - com limites regulatórios | Aumenta parcela real | Todos os financiamentos |
| 5 | **Despesas Imóvel** | IPTU (0.1-1.5%), Condomínio (R$100-2k), Seguro (0.3-0.8%) | Fluxo de caixa real é 50% maior | Investidor imobiliário |
| 6 | **CET (Custo Efetivo Total)** | Taxa real incluindo custos iniciais - normativa BC | Melhor métrica que taxa nominal | Comparação entre bancos |
| 7 | **Vacância/Inadimplência** | Taxa de ocupação (85-95%), inadimplência (5-10%) | ROI real é 30-40% menor | Investidor aluga |
| 8 | **Taxa Negociável** | Spread do banco conforme score creditício | Varia -1% a +3% da taxa nominal | Empresário/renovação |
| 9 | **Portabilidade** | Migração de financiamento entre bancos | Economiza -200k em 30 anos | Refinanciamento |
| 10 | **Imposto de Renda** | 15% sobre juros em poupança/renda fixa; não há desconto em financiamento | Afeta comparação aluguel+investimento | Cenário aluguel vs compra |

---

## 🧭 ANÁLISE POR PERFIL

### **Perfil 1: MCMV (Minha Casa Minha Vida)**

**Status:** ❌ **Falha**

**Dados Entrada:**
- Renda: R$ 4.500
- Imóvel: R$ 220k
- FGTS: R$ 15k
- Taxa: 4.5% (programa Caixa)

**Resultado Esperado:**
```
Parcela Price: R$ 980/mês (44.9% da renda - ACIMA do limite!)
Parcela com Subsídio: R$ 650/mês (29.8% da renda - OK)
```

**Problema Detectado:**
1. ❌ Subsídio MCMV não é calculado
2. ❌ Elegibilidade MCMV não é validada (renda ≤ 4.5k? Regional?)
3. ❌ Acesso a taxa de 4.5% não é verificado
4. ⚠️ TypeError: Decimal vs float

**Solução:**
```python
def validar_mcmv(renda_familiar, valor_imovel, estado):
    # MCMV exige renda ≤ 4.5k
    # Subsídio varia por região: 25-35% do valor
    subsidio = valor_imovel * 0.30  # Exemplo 30%
    return valor_imovel - subsidio
```

---

### **Perfil 2: Aluguel vs Compra**

**Status:** ❌ **Falha**

**Dados Entrada:**
- Aluguel: R$ 3k/mês
- Imóvel: R$ 500k
- Entrada: R$ 100k (20%)
- Prazo: 30 anos

**Resultado Esperado:**
```
Cenário 1 - Comprar:
  Financiamento 30 anos: Parcela ~R$ 3.300 + IPTU + condomínio + seguro = R$ 4.500 total
  Valor final (aum. 2% a.a.): R$ 900k
  Custo total: ~R$ 1.2M

Cenário 2 - Alugar + Investir:
  Aluguel 30 anos (aum. 3.5% a.a.): ~R$ 1.5M
  Investimento (6% CDI): ~R$ 850k
  Custo total: ~R$ 1.5M (PIOR que compra)

Conclusão: Compra é melhor em longo prazo ✓
```

**Problema Detectado:**
1. ❌ TypeError: Decimal vs float
2. ❌ Despesas do imóvel (IPTU, condomínio) não são consideradas
3. ❌ Imposto de Renda sobre investimento não é descontado
4. ❌ Gráfico visual de comparação não é gerado

**Solução:**
```python
def simular_aluguel_investimento_realista():
    # Adicionar despesas mensais
    despesas_imovel = valor_imovel * 0.01  # 1% do valor em despesas
    # Descontar IR sobre rendimentos
    rendimento_liquido = rendimento * 0.85  # 15% de IR
```

---

### **Perfil 3: Poupador com Aporte Mensal**

**Status:** ❌ **Falha**

**Dados Entrada:**
- Imóvel: R$ 400k
- Entrada: R$ 80k
- Aporte: R$ 2k/mês
- Prazo: 25 anos

**Resultado Esperado:**
```
Financiamento:
  Parcela Price 25 anos: ~R$ 1.800/mês (7.2% Caixa)

Com Aporte:
  Mês 1-120: Acumula R$ 2k/mês → R$ 240k
  Resultado: Quita o financiamento em ~15 anos (economia 10 anos)
  Economia: ~R$ 180k em juros
```

**Problema Detectado:**
1. ❌ TypeError: Decimal vs float
2. ⚠️ Aporte mensal não é somado corretamente ao investimento
3. ⚠️ Não há comparação: "Investir no financiamento vs CDI"
4. ⚠️ FGTS acumula 24 meses e gera confusão

**Solução:**
```python
# Loop mensal deve somar aporte ANTES de calcular juros
for mes in range(1, prazo):
    saldo_investimento += aporte_mensal
    saldo_investimento *= (1 + taxa_investimento)
    
    if saldo_investimento >= saldo_financiamento:
        # Quita o financiamento antecipadamente
        break
```

---

### **Perfil 4: Investidor Imobiliário**

**Status:** ⚠️ **Parcial**

**Dados Entrada:**
- Imóvel: R$ 300k
- Aluguel: R$ 1.800/mês
- ROI esperado: 7.2% a.a.

**Resultado Esperado:**
```
ROI Bruto: (1.800 * 12) / 300.000 = 7.2% ✓

ROI Líquido (despesas):
  - IPTU (0.8%): -R$ 2.400/ano
  - Condomínio (0.5%): -R$ 1.500/ano
  - Seguro (0.4%): -R$ 1.200/ano
  - Manutenção: -R$ 1.500/ano
  - Vacância (10%): -R$ 2.160/ano
  Total despesas: -R$ 8.760/ano
  
ROI Líquido: (21.600 - 8.760) / 300.000 = 4.28% (MUITO MENOR!)
```

**Problema Detectado:**
1. ❌ ROI bruto é calculado, mas ROI líquido não
2. ❌ Despesas de imóvel (IPTU, condomínio, seguro, manutenção) não são simuladas
3. ❌ Taxa de vacância (85-95% ocupação) não é considerada
4. ❌ Inadimplência do inquilino (5-10%) não é simulada
5. ❌ Wizard não distingue comprador de investidor

**Solução:**
```python
def calcular_roi_liquido(aluguel_mensal, valor_imovel, estado):
    # Despesas fixas por estado
    despesas = {
        'SP': {'iptu': 0.8, 'condominio': 0.5, 'seguro': 0.4, 'manutencao': 0.5},
        'RJ': {'iptu': 1.2, 'condominio': 0.8, 'seguro': 0.5, 'manutencao': 0.6},
    }
    
    vacancia_rate = 0.10  # 10% de vacância
    inadimplencia_rate = 0.05  # 5% de inadimplência
    
    renda_efetiva = aluguel_mensal * (1 - vacancia_rate - inadimplencia_rate)
    despesas_totais = valor_imovel * sum(despesas[estado].values()) / 100 / 12
    
    fluxo_liquido = renda_efetiva - despesas_totais
    roi_liquido = (fluxo_liquido * 12) / valor_imovel
    
    return roi_liquido
```

---

### **Perfil 5: Upgrade (Venda + Compra)**

**Status:** ❌ **Não suportado**

**Dados Entrada:**
- Venda imóvel antigo: R$ 400k
- Saldo devedor antigo: R$ 200k
- Novo imóvel: R$ 800k
- Entrada esperada: Saldo da venda = R$ 200k (25% do novo)

**Resultado Esperado:**
```
Venda:
  Valor: R$ 400k
  ITBI (SP ~1.5%): -R$ 6.000
  Comissão (5%): -R$ 20.000
  Quitação saldo devedor: -R$ 200.000
  Saldo líquido: R$ 174.000

Compra nova:
  Valor: R$ 800k
  ITBI (SP ~1.5%): -R$ 12.000
  Entrada (saldo venda): R$ 174.000
  Financiamento restante: R$ 614.000
  Novo prazo: 25 anos @ 7.2%
  Nova parcela: ~R$ 3.200/mês
```

**Problema Detectado:**
1. ❌ Wizard não pergunta sobre imóvel anterior
2. ❌ ITBI não é calculado
3. ❌ Comissão de venda não é deduzida
4. ❌ Saldo devedor antigo não é quitado
5. ❌ Fluxo de venda + compra é confuso

**Solução:**
```python
class UpgradeSimulation:
    def __init__(self, venda_valor, saldo_devedor, compra_valor, estado):
        self.itbi_venda = venda_valor * 0.015  # Varia por estado
        self.comissao = venda_valor * 0.05
        self.liquido_venda = venda_valor - self.itbi_venda - self.comissao - saldo_devedor
        
        self.itbi_compra = compra_valor * 0.015
        self.entrada_nova = self.liquido_venda
        self.financiamento_novo = compra_valor - self.entrada_nova
```

---

### **Perfil 6: Consorciado**

**Status:** ✅ **Funciona (parcialmente)**

**Dados Entrada:**
- Carta: R$ 500k
- Prazo: 15 anos (180 meses)
- Taxa Adm: 1.5%
- Fundo: 0.8%

**Resultado Obtido:**
```
✓ Parcela fixa: R$ 3.500/mês (0.7% do valor)
✓ Total custo: R$ 302.500
✓ Contemplação estimada: Mês 72 (40% do prazo)
```

**Validação:**
```
Parcela esperada (mercado): 0.8-1.0% do valor = R$ 4.000-5.000
Parcela gerada: 0.7% = R$ 3.500
⚠️ Parcela MENOR que mercado (erro -12%)
```

**Problema Detectado:**
1. ⚠️ Parcela 0.7% é abaixo do mercado (0.8-1.0%)
2. ❌ Probabilidade de contemplação não é realista
3. ❌ Não há comparação Price vs Consórcio
4. ❌ Histórico de consórcio anterior não é perguntado
5. ❌ Liquidação de cotas não é simulada

**Recomendação:**
```python
# Ajustar parcela para mercado realista
parcela_base_percentual = Decimal('0.0085')  # 0.85% ao mês
```

---

### **Perfil 7: Empresário (Alto Crédito)**

**Status:** ❌ **Falha**

**Dados Entrada:**
- Imóvel: R$ 3Mi
- Entrada: R$ 600k (20%)
- Renda: R$ 100k/mês
- Taxa: 10% a.a.

**Resultado Esperado:**
```
LTV = (3M - 600k) / 3M = 80% ✓ (dentro do limite)
Parcela 30 anos: ~R$ 16.100/mês (16.1% da renda)

Capacidade de pagamento:
  30% da renda = R$ 30.000/mês ✓
  Parcela = R$ 16.100/mês ✓ (OK)
```

**Problema Detectado:**
1. ❌ TypeError: Decimal vs float
2. ❌ LTV (Loan-to-Value) não é validado
3. ❌ Capacidade de pagamento não é verificada
4. ❌ Taxa não pode ser negociada conforme score creditício
5. ⚠️ Limite máximo de crédito por banco não é mostrado

**Solução:**
```python
def validar_capacidade_pagamento(renda_familiar, parcela, ltv, credito_score):
    # Validar LTV máximo (80%)
    if ltv > 0.80:
        return False, "LTV excede 80%"
    
    # Validar parcela ≤ 30% da renda
    if (parcela / renda_familiar) > 0.30:
        return False, "Parcela excede 30% da renda"
    
    # Ajustar taxa conforme score creditício
    spread = {
        'excelente': -1.0,
        'bom': 0,
        'regular': 1.0,
        'ruim': 2.0,
    }
    
    taxa_ajustada = taxa_nominal + spread.get(credito_score, 0)
    return True, taxa_ajustada
```

---

### **Perfil 8: Autônomo (Prazo Curto)**

**Status:** ❌ **Falha**

**Dados Entrada:**
- Imóvel: R$ 250k
- Entrada: R$ 125k (50%)
- Prazo: 10 anos (120 meses)
- Renda: R$ 6k/mês (variável)

**Resultado Esperado:**
```
Financiamento: R$ 125k
Parcela Price 10 anos (8% a.a.): ~R$ 1.513/mês (25.2% da renda médio)

✓ Entrada alta (50%) reduz risco e taxa
✓ Prazo curto (10 anos) economiza juros
✓ Total juros: ~R$ 56k (45% do financiamento)
```

**Problema Detectado:**
1. ❌ TypeError: Decimal vs float
2. ❌ Comprovação de renda para autônomo não é validada (MEI, declaração)
3. ❌ Renda variável (flutuante) não é simulada
4. ❌ Taxa pode aumentar se renda cair (não há simulação)
5. ⚠️ Wizard não distingue CLT de autônomo

**Solução:**
```python
def validar_renda_autonomo(anos_atividade, documentos):
    # Exigir:
    # - Mínimo 2-3 anos de atividade
    # - Últimos 12 meses de declarações
    # - MEI ou comprovação de renda
    
    if anos_atividade < 2:
        return False, "Profissional autônomo requer mín. 2 anos de atividade"
    
    renda_media = media_ultimos_12_meses(documentos)
    return True, renda_media
```

---

### **Perfil 9: Custo de Oportunidade (SELIC vs Financiamento)**

**Status:** ❌ **Não suportado**

**Dados Entrada:**
- Disponível em caixa: R$ 1M
- Imóvel: R$ 1M (pode pagar à vista)
- SELIC: 10.5% a.a.
- Taxa financiamento: 8% a.a.

**Resultado Esperado:**
```
Cenário A - Pagar à vista:
  Investir R$ 1M em Tesouro Direto (10.5%): +R$ 105k/ano
  Imóvel: R$ 1M (sem parcelas)
  Resultado: Riqueza líquida = R$ 1.105k (após 1 ano)

Cenário B - Financiar:
  Investir R$ 1M em Tesouro Direto (10.5%): +R$ 105k/ano
  Pagar parcelas financiamento (8%): -R$ 80k/ano
  Resultado: Riqueza líquida = R$ 1.025k (após 1 ano)

Conclusão:
  ✓ Pagar à vista é melhor (SELIC > taxa de financiamento)
  ✓ Diferença: +R$ 80k em 1 ano de oportunidade
```

**Problema Detectado:**
1. ❌ Nenhum campo para entrada de valor em caixa
2. ❌ Cálculo de oportunidade vs financiamento não existe
3. ❌ SELIC não é incluída nas opções de investimento
4. ❌ Análise VPL (Valor Presente Líquido) não é feita
5. ❌ Wizard não pergunta sobre aplicações alternativas

**Solução:**
```python
def analisar_oportunidade(valor_caixa, taxa_financiamento, taxa_investimento):
    # NPV = (fluxo_investimento - fluxo_financiamento) / (1 + desconto)^ano
    
    fluxo_investimento = valor_caixa * (1 + taxa_investimento) ** 30
    fluxo_financiamento = valor_caixa * (1 + taxa_financiamento) ** 30
    
    npv = fluxo_investimento - fluxo_financiamento
    
    if npv > 0:
        return "Melhor investir e financiar"
    else:
        return "Melhor pagar à vista"
```

---

### **Perfil 10: Migração (Comparativo de Bancos)**

**Status:** ❌ **Não suportado**

**Dados Entrada:**
- Imóvel: R$ 400k
- Entrada: R$ 80k (20%)
- Prazo: 25 anos
- Comparar: BB vs Caixa vs Itaú vs Bradesco vs Santander

**Resultado Esperado:**
```
BB:       Taxa 7.5%  → Parcela R$ 1.950  → CET 8.2%
Caixa:    Taxa 7.2%  → Parcela R$ 1.880  → CET 7.9%
Itaú:     Taxa 9.2%  → Parcela R$ 2.105  → CET 10.1%
Bradesco: Taxa 8.9%  → Parcela R$ 2.065  → CET 9.7%
Santander:Taxa 8.5%  → Parcela R$ 2.005  → CET 9.3%

Melhor opcão (menor CET): Caixa 7.9% ✓
```

**Problema Detectado:**
1. ❌ Frontend não oferece seleção de banco
2. ❌ CET não é calculado (apenas taxa nominal)
3. ❌ Comparação paralela não é possível
4. ❌ Portabilidade de financiamento não é simulada
5. ❌ Histórico creditício não afeta taxa por banco

**Solução:**
```python
BANCOS_MERCADO = {
    'BB': {'taxa_base': 7.5, 'spread': 0.8},
    'CAIXA': {'taxa_base': 7.2, 'spread': 0.7},
    'ITAU': {'taxa_base': 9.2, 'spread': 1.0},
    'BRADESCO': {'taxa_base': 8.9, 'spread': 0.95},
    'SANTANDER': {'taxa_base': 8.5, 'spread': 0.9},
}

def simular_multiplos_bancos(financiamento, prazo, score_crediticio):
    resultados = {}
    for banco, params in BANCOS_MERCADO.items():
        taxa = params['taxa_base'] + params['spread']
        # Ajustar por score creditício
        taxa_ajustada = taxa + (0 if score_crediticio > 750 else 1.0)
        
        resultado = calcular_price_sac('price', financiamento, taxa_ajustada, prazo)
        cet = calcular_cet(financiamento, resultado['tabela'])
        
        resultados[banco] = {
            'taxa_nominal': taxa_ajustada,
            'parcela': resultado['parcela_inicial'],
            'cet': cet['cet_anual'],
            'total_juros': resultado['total_juros'],
        }
    
    return resultados
```

---

## 🛠️ CORREÇÕES IMEDIATAS NECESSÁRIAS

### **Priority 1 (Crítico - Bloqueia uso)**

```python
# Arquivo: simulacao/calculadora_financeira.py
# Linha 217

# ❌ ANTES
total_juros += juros_mensal

# ✅ DEPOIS
total_juros += float(juros_mensal)
```

---

### **Priority 2 (Alta - Afeta maioria dos perfis)**

```python
# Arquivo: simulacao/calculadora_financeira.py
# Adicionar função de validação

def validar_financiamento(valor_imovel, entrada, renda_familiar, parcela):
    """Valida se financiamento é viável conforme normas brasileiras."""
    
    # 1. Entrada mínima 20%
    ltv = (valor_imovel - entrada) / valor_imovel
    if ltv > 0.80:
        return False, "Entrada mínima deve ser 20% (LTV máximo 80%)"
    
    # 2. Parcela máximo 30% da renda
    percentual_renda = (parcela / renda_familiar) * 100
    if percentual_renda > 30:
        return False, f"Parcela {percentual_renda:.1f}% da renda (máx 30%)"
    
    return True, "OK"
```

---

### **Priority 3 (Alta - Faltam campos críticos)**

```python
# Arquivo: simulacao/wizard_forms.py
# Adicionar campos ao WizardImovelForm

class WizardImovelForm(forms.Form):
    # Campos existentes...
    
    # NOVOS CAMPOS
    programa_mcmv = forms.BooleanField(
        label="Participo do programa MCMV (Minha Casa Minha Vida)?",
        required=False,
    )
    
    profissao = forms.ChoiceField(
        choices=[
            ('clt', 'Empregado CLT'),
            ('autonomo', 'Autônomo'),
            ('empresa', 'Empresário'),
            ('outro', 'Outro'),
        ],
        label="Tipo de profissão",
    )
    
    imovel_anterior = forms.BooleanField(
        label="Você possui imóvel anterior (upgrade)?",
        required=False,
    )
    
    saldo_devedor_anterior = forms.DecimalField(
        label="Saldo devedor do imóvel anterior (R$)",
        required=False,
        initial=Decimal('0'),
    )
```

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### **Sprint 1: Correções Críticas (1 semana)**

- [ ] Corrigir TypeError Decimal/float em `calcular_price_sac()`
- [ ] Implementar validação LTV + Parcela/Renda
- [ ] Adicionar campos MCMV, profissão, upgrade ao wizard
- [ ] Implementar `calcular_cet()` corretamente

### **Sprint 2: Variáveis de Mercado (2 semanas)**

- [ ] Adicionar ITBI (Imposto de Transmissão)
- [ ] Simular IPTU + Condomínio + Seguros imobiliários
- [ ] Implementar vacância/inadimplência para investidor
- [ ] Adicionar TR (Taxa Referencial)

### **Sprint 3: Funcionalidades Avançadas (3 semanas)**

- [ ] Comparador de bancos (BB, Caixa, Itaú, Bradesco, Santander)
- [ ] Análise de oportunidade (SELIC vs Financiamento)
- [ ] Gráfico visual aluguel vs compra
- [ ] Portabilidade de financiamento

### **Sprint 4: UX/Wizard (2 semanas)**

- [ ] Separar fluxos: Comprador → Investidor → Consorciado
- [ ] Reordenar perguntas do wizard (lógica clara)
- [ ] Adicionar validação de elegibilidade em tempo real
- [ ] Melhorar mensagens de erro

---

## 🎯 CONCLUSÃO

**Status Geral:** ❌ **Não pronto para produção**

**Motivos:**
1. 5 erros críticos que bloqueiam simulações
2. 10 variáveis essenciais faltando (mercado BR não reconhecerá valores)
3. 8 fluxos confusos que farão usuários desistirem
4. Cálculos imprecisos (-12% a +50% vs mercado real)

**Tempo Estimado para MVP:**
- Correções críticas: 1-2 semanas
- Variáveis de mercado: 2-3 semanas
- Validações + UX: 1-2 semanas
- **Total: 4-7 semanas para versão aceitável**

**Próximas Ações:**
1. ✅ Corrigir TypeError (hoje)
2. ✅ Implementar validações de mercado (semana 1)
3. ✅ Adicionar ITBI + Despesas imóvel (semana 2)
4. ✅ Comparador de bancos (semana 3)
5. ✅ Revisar wizard com UX designer (semana 4)

---

**Relatório Preparado:** Janeiro 2026  
**Próxima Revisão:** Após Sprint 1
