# 🔴 BUG DO CONSÓRCIO (0.7%) - LOCALIZAÇÃO E ANÁLISE

**Data:** 25 de Janeiro de 2026  
**Status:** 🔍 Localizado e Documentado

---

## 📍 LOCALIZAÇÃO EXATA DO BUG

### Arquivo Principal
📄 **[simulacao/calculadora_financeira.py](simulacao/calculadora_financeira.py)**

### Função 1: `simular_consorcio()`
**Linhas:** 328-393

```python
def simular_consorcio(valor_imovel, prazo_meses, taxa_adm, fundo_reserva, fgts_saldo=0.0):
    """
    Simula o Consórcio de forma realista com sorteios e lances.
    ...
    """
    
    # LINHA 358: ← BUG AQUI!
    parcela_base_percentual = Decimal('0.007')  # 0.7% ao mês
    parcela_fixa = valor_imovel_total * parcela_base_percentual
    
    # LINHA 362-363: Taxa e Fundo calculados SEPARADO
    taxa_adm_mensal = valor_imovel_total * taxa_adm_mensal_percent
    fundo_reserva_mensal = valor_imovel_total * fundo_reserva_percent / 12
```

### Função 2: `simular_consorcio_com_lances()`
**Linhas:** 395-460+

```python
def simular_consorcio_com_lances(...):
    """
    Simula o Consórcio com LANCES (Livre, Fixo ou Embutido)...
    """
    
    # LINHA 452: ← BUG AQUI TAMBÉM!
    parcela_base = valor_imovel_dec * Decimal('0.007')  # 0.7% ao mês
    taxa_adm_mensal = valor_imovel_dec * taxa_adm_dec
    fundo_reserva_mensal = valor_imovel_dec * fundo_reserva_dec
    parcela_total_mensal = parcela_base + taxa_adm_mensal + fundo_reserva_mensal
```

---

## 🐛 QUAL É O BUG EXATAMENTE?

### O Problema

A função calcula **3 componentes separados**:
1. **Parcela Base:** `0.7%` do valor (✓ Correto)
2. **Taxa de Administração:** Calculada separadamente
3. **Fundo de Reserva:** Calculado separadamente

### O Resultado Enganoso

```python
# Quando o usuário chama:
resultado = simular_consorcio(
    valor_imovel=500000,
    prazo_meses=180,
    taxa_adm=1.5,
    fundo_reserva=0.5
)

# A função retorna:
print(resultado['parcela_fixa'])  # R$ 3.500,00  ← Isto está ERRADO!
                                  # (só mostra a parcela base 0.7%)

# MAS quando o usuário realmente paga:
# parcela_fixa = R$ 3.500
# + taxa_adm_mensal = R$ 625
# + fundo_reserva_mensal = R$ 208
# ═══════════════════════════════════
# TOTAL REAL = R$ 4.333  ← Oculto do usuário!
```

### Exemplos Específicos

**Para R$ 500.000 em 180 meses:**

| Item | Valor | % do Total |
|------|-------|-----------|
| **Parcela Base (0.7%)** | R$ 3.500/mês | 80,7% |
| **Taxa Adm (1.5% ÷ 12)** | R$ 625/mês | 14,4% |
| **Fundo Reserva (0.5% ÷ 12)** | R$ 208/mês | 4,8% |
| **TOTAL REAL** | **R$ 4.333/mês** | **100%** |

**Diferença:** R$ 833/mês (23,7% a mais do que é mostrado!)

---

## 📊 IMPACTO EM 30 ANOS (360 MESES)

| Item | Sem Taxa/Fundo | Com Taxa/Fundo |
|------|---|---|
| **Parcela Base** | R$ 1.260.000 | R$ 1.260.000 |
| **Taxa Adm** | — | R$ 225.000 |
| **Fundo Reserva** | — | R$ 75.000 |
| **TOTAL** | R$ 1.260.000 | **R$ 1.560.000** |
| **Diferença** | — | **+R$ 300.000 (23,8%)** |

---

## 🔧 COMO CORRIGIR

### Opção 1: Integrar na Parcela (Mais Simples)

**Antes (Bugado):**
```python
# LINHA 358
parcela_base_percentual = Decimal('0.007')  # 0.7% ao mês
parcela_fixa = valor_imovel_total * parcela_base_percentual

# LINHA 362-363
taxa_adm_mensal = valor_imovel_total * taxa_adm_mensal_percent
fundo_reserva_mensal = valor_imovel_total * fundo_reserva_percent / 12

# Return só mostra parcela_fixa (ERRADO!)
return {
    'parcela_fixa': float(parcela_fixa),  # ← Incompleto!
    'custo_total_taxa_adm': float(custo_total_taxa_adm),
    'custo_total_fundo': float(custo_total_fundo),
    # ...
}
```

**Depois (Corrigido):**
```python
# LINHA 358-363
parcela_base_percentual = Decimal('0.007')  # 0.7% ao mês
parcela_fixa = valor_imovel_total * parcela_base_percentual

taxa_adm_mensal_percent = Decimal(str(taxa_adm)) / 100 / 12
fundo_reserva_percent = Decimal(str(fundo_reserva)) / 100

taxa_adm_mensal = valor_imovel_total * taxa_adm_mensal_percent
fundo_reserva_mensal = valor_imovel_total * fundo_reserva_percent / 12

# LINHA ~365 (NOVO):
# Integrar na parcela total
parcela_mensal_total = parcela_fixa + taxa_adm_mensal + fundo_reserva_mensal

# Return mostra a parcela REAL
return {
    'parcela_base_mensal': float(parcela_fixa),
    'taxa_adm_mensal': float(taxa_adm_mensal),
    'fundo_reserva_mensal': float(fundo_reserva_mensal),
    'parcela_total_mensal': float(parcela_mensal_total),  # ← NOVA CHAVE!
    'parcela_fixa': float(parcela_mensal_total),  # Manter compatibilidade
    # ...
}
```

---

## 📋 CHECKLIST DE CORREÇÃO

### Passo 1: Função `simular_consorcio()` (L328-393)
- [ ] Adicionar cálculo de `parcela_mensal_total` (base + taxa + fundo)
- [ ] Retornar breakdown claro no dict
- [ ] Manter chave `'parcela_fixa'` para compatibilidade, mas com o valor TOTAL

### Passo 2: Função `simular_consorcio_com_lances()` (L395+)
- [ ] Refazer o cálculo da parcela base (linhas ~452-454)
- [ ] Integrar taxa + fundo na parcela total
- [ ] Atualizar return com breakdown

### Passo 3: Templates
- [ ] Atualizar [templates/simulacao/wizard_resultados.html](templates/simulacao/wizard_resultados.html)
- [ ] Mostrar breakdown: Base + Taxa Adm + Fundo Reserva

### Passo 4: Testes
- [ ] Adicionar teste em [teste_consorcio_com_lances.py](teste_consorcio_com_lances.py)
- [ ] Validar que `parcela_total_mensal` = base + taxa + fundo
- [ ] Testar contra valores conhecidos

### Passo 5: Integração
- [ ] Atualizar [simulacao/wizard_views.py](simulacao/wizard_views.py) para usar nova chave
- [ ] Validar que todos os testes passam

---

## 🧪 TESTE IMEDIATO

Para validar que o bug existe, rode:

```python
from simulacao.calculadora_financeira import simular_consorcio
from decimal import Decimal

resultado = simular_consorcio(
    valor_imovel=500000,
    prazo_meses=180,
    taxa_adm=1.5,
    fundo_reserva=0.5,
    fgts_saldo=0.0
)

print(f"Parcela mostrada: R$ {resultado['parcela_fixa']:,.2f}")
# Mostra: R$ 3.500,00 ← ERRADO!

print(f"Taxa Adm mensal: R$ {resultado['custo_total_taxa_adm']/180:,.2f}")
# Mostra: R$ 625,00

print(f"Fundo mensal: R$ {resultado['custo_total_fundo']/180:,.2f}")
# Mostra: R$ 208,00

# Total REAL que usuário paga: 3500 + 625 + 208 = R$ 4.333
# Mas a função só retorna 'parcela_fixa' = R$ 3.500
```

---

## 🎯 PRÓXIMOS PASSOS

Quer que eu:

1. **Corrija as funções imediatamente?** (Editar `calculadora_financeira.py`)
2. **Crie testes primeiro?** (Confirmar o bug com `pytest`)
3. **Implemente com nova função `simular_consorcio_v2()`?** (Sem quebrar compatibilidade)

**Recomendação:** Começar com a opção **3** - criar `simular_consorcio_v2()` e depois migrar gradualmente. 🚀
