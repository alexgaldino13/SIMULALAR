# 📐 PLANO DE IMPLEMENTAÇÃO: 5 Pontos de Atenção

**Data:** 25 de Janeiro de 2026  
**Status:** ✅ Pronto para começar  
**Tempo Estimado Total:** ~1 semana (40-48 horas)

---

## 🗺️ VISÃO GERAL

```
DIA 1: Bug Consórcio + IOF
DIA 2: IPTU/Condomínio  
DIA 3: TR (Taxa Referencial)
DIA 4: IR Rendimentos
DIA 5: Testes + Integração
```

---

## ⚡ FASE 1: BUG CONSÓRCIO (2-3 HORAS)

### 🎯 Objetivo
Corrigir o cálculo da parcela de consórcio que está omitindo taxa de administração e fundo de reserva.

### 📍 Arquivo Principal
[simulacao/calculadora_financeira.py](simulacao/calculadora_financeira.py) - Linha ~328

### 🔴 Problema Atual
```python
# LINHA 328
def simular_consorcio(valor_imovel, prazo_meses, taxa_adm, fundo_reserva, fgts_saldo=0.0):
    # ... código ...
    parcela_fixa = Decimal(str(valor_imovel)) * Decimal('0.007')  # ✓ Cálculo OK
    
    # MAS depois:
    # taxa_adm_mensal, fundo_reserva_mensal são calculados separados
    # Usuário vê parcela menor do que realmente paga
```

### ✅ Solução: Nova Função

**Inserir APÓS a função `simular_consorcio()` existente:**

```python
# LINHA ~380 (NOVO)
def simular_consorcio_v2(
    valor_imovel: float,
    prazo_meses: int,
    taxa_adm_anual: float = 1.5,           # % ao ano
    fundo_reserva_anual: float = 0.5,      # % ao ano
    percentual_parcela_base: float = 0.7,  # % ao mês
    metodo_contemplacao: str = 'conservador',
    fgts_saldo: float = 0.0,
) -> Dict:
    """
    VERSÃO CORRIGIDA: Calcula consórcio com todas as despesas explícitas
    
    PARCELA MENSAL TOTAL = Base (0.7%) + Taxa Adm + Fundo Reserva
    
    Args:
        valor_imovel: Valor do bem em consórcio
        prazo_meses: Duração total do consórcio (típico: 180-240 meses)
        taxa_adm_anual: Taxa de administração anual (%)
        fundo_reserva_anual: Fundo de reserva anual (%)
        percentual_parcela_base: Parcela base mensal (%)
        metodo_contemplacao: Como estimar quando será contemplado
        fgts_saldo: FGTS disponível para lance
    
    Returns:
        Dict com parcelas detalhadas, tabela mês-a-mês, total pago
    
    Exemplo:
        resultado = simular_consorcio_v2(
            valor_imovel=500000,
            prazo_meses=180,
            taxa_adm_anual=1.5,
            fundo_reserva_anual=0.5
        )
        # resultado['parcela_total_mensal'] = 4.333,33
    """
    
    from decimal import Decimal
    
    valor_dec = Decimal(str(valor_imovel))
    
    # ===== COMPONENTES DA PARCELA =====
    
    # 1. Parcela Base (0.7% mensal)
    parcela_base = valor_dec * Decimal(str(percentual_parcela_base)) / Decimal('100')
    
    # 2. Taxa de Administração (anual → mensal)
    # Exemplo: 1.5% a.a. = 0.125% a.m.
    taxa_adm_mensal = (valor_dec * Decimal(str(taxa_adm_anual)) / Decimal('100')) / Decimal('12')
    
    # 3. Fundo de Reserva (anual → mensal)
    # Exemplo: 0.5% a.a. = 0.0416% a.m.
    fundo_reserva_mensal = (valor_dec * Decimal(str(fundo_reserva_anual)) / Decimal('100')) / Decimal('12')
    
    # TOTAL MENSAL (o que o usuário realmente paga)
    parcela_mensal_total = parcela_base + taxa_adm_mensal + fundo_reserva_mensal
    
    # ===== ESTIMATIVA DE CONTEMPLAÇÃO =====
    
    if metodo_contemplacao == 'conservador':
        # 40% do prazo (esperado: demora mais)
        mes_contemplacao = max(int(prazo_meses * Decimal('0.40')), 48)
    elif metodo_contemplacao == 'medio':
        # 30% do prazo
        mes_contemplacao = max(int(prazo_meses * Decimal('0.30')), 36)
    else:  # otimista
        # 25% do prazo (espera menos)
        mes_contemplacao = max(int(prazo_meses * Decimal('0.25')), 24)
    
    # ===== GERAÇÃO DE TABELA MÊS-A-MÊS =====
    
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
            'meses_restantes': prazo_meses - mes,
        })
    
    # ===== RESUMO FINAL =====
    
    total_pago = float(parcela_mensal_total * Decimal(str(prazo_meses)))
    total_taxa_adm = float(taxa_adm_mensal * Decimal(str(prazo_meses)))
    total_fundo = float(fundo_reserva_mensal * Decimal(str(prazo_meses)))
    
    return {
        'valor_imovel': float(valor_imovel),
        'prazo_meses': prazo_meses,
        
        # Detalhamento da parcela mensal
        'parcela_base_mensal': float(parcela_base),
        'taxa_adm_mensal': float(taxa_adm_mensal),
        'fundo_reserva_mensal': float(fundo_reserva_mensal),
        'parcela_total_mensal': float(parcela_mensal_total),
        
        # Custos totais
        'total_pago': total_pago,
        'total_taxa_adm': total_taxa_adm,
        'total_fundo_reserva': total_fundo,
        'custo_total_despesas': total_taxa_adm + total_fundo,
        
        # Contemplação
        'mes_contemplacao': mes_contemplacao,
        'meses_espera': mes_contemplacao,
        'meses_pos_contemplacao': prazo_meses - mes_contemplacao,
        
        # Tabela completa
        'tabela': tabela,
        
        # Integração FGTS
        'fgts_saldo': float(fgts_saldo),
        'lance_com_fgts': float(fgts_saldo),  # FGTS pode ser usado para lance
    }
```

### 🧪 Teste Imediato

Adicionar em [teste_consorcio_com_lances.py](teste_consorcio_com_lances.py):

```python
# NOVO TESTE
from simulacao.calculadora_financeira import simular_consorcio_v2

print("=" * 80)
print("TESTE: CONSÓRCIO CORRIGIDO (v2)")
print("=" * 80)

resultado = simular_consorcio_v2(
    valor_imovel=500000,
    prazo_meses=180,
    taxa_adm_anual=1.5,
    fundo_reserva_anual=0.5,
)

print(f"\n✓ Valor do Bem: R$ {resultado['valor_imovel']:,.2f}")
print(f"✓ Prazo: {resultado['prazo_meses']} meses")

print(f"\n📊 PARCELA MENSAL DETALHADA:")
print(f"  ├─ Base (0.7%): R$ {resultado['parcela_base_mensal']:,.2f}")
print(f"  ├─ Taxa Adm: R$ {resultado['taxa_adm_mensal']:,.2f}")
print(f"  ├─ Fundo Reserva: R$ {resultado['fundo_reserva_mensal']:,.2f}")
print(f"  └─ TOTAL: R$ {resultado['parcela_total_mensal']:,.2f}")

print(f"\n💰 CUSTOS TOTAIS:")
print(f"  ├─ Total Pago (parcelas): R$ {resultado['total_pago']:,.2f}")
print(f"  ├─ Total Taxa Adm: R$ {resultado['total_taxa_adm']:,.2f}")
print(f"  ├─ Total Fundo: R$ {resultado['total_fundo_reserva']:,.2f}")

print(f"\n📅 CONTEMPLAÇÃO:")
print(f"  ├─ Mês esperado: {resultado['mes_contemplacao']}")
print(f"  └─ Meses de espera: {resultado['meses_espera']}")

# Validação
assert resultado['parcela_total_mensal'] > resultado['parcela_base_mensal'], \
    "Parcela total deveria ser maior que base!"

print(f"\n✅ TESTE PASSOU - Bug consórcio corrigido!")
```

### 📝 Alterações Necessárias

1. **[simulacao/calculadora_financeira.py](simulacao/calculadora_financeira.py):**
   - Inserir função `simular_consorcio_v2()` após linha 390
   - Manter função antiga para compatibilidade

2. **[simulacao/wizard_views.py](simulacao/wizard_views.py):**
   - Substituir chamada de `simular_consorcio()` por `simular_consorcio_v2()`
   - Linhas: ~850 (step 8)

3. **Templates:**
   - [templates/simulacao/wizard_resultados.html](templates/simulacao/wizard_resultados.html)
   - Mostrar breakdown: Base + Taxa Adm + Fundo

---

## ⚡ FASE 2: IOF - IMPOSTO (2-3 HORAS)

### 🎯 Objetivo
Calcular IOF (Imposto sobre Operações Financeiras) conforme Lei nº 7.798/89.

### 📍 Arquivo Principal
[simulacao/calculadora_financeira.py](simulacao/calculadora_financeira.py) - Inserir após line 100

### 📐 Fórmula IOF

```
IOF Linear = Valor_Financiado × 0,00938 (0,938% ao ano, linear)
IOF Relativo = Σ(Parcela_Mensal × 0,005) (0,5% por parcela)
IOF TOTAL = IOF_Linear + IOF_Relativo
```

### ✅ Solução: Nova Função

**Inserir ANTES de `calcular_price_sac()`:**

```python
# LINHA ~100 (NOVO)
def calcular_iof(
    valor_financiado: float,
    parcelas_mensais: List[float],
    prazo_meses: int,
    aliquota_linear: float = 0.00938,  # 0,938% a.a.
    aliquota_relativa: float = 0.005,  # 0,5% por parcela
) -> Dict:
    """
    Calcula Imposto sobre Operações Financeiras (IOF)
    
    Lei nº 7.798/89
    Decreto nº 9.867/2019 (conversão em renda fixa)
    
    Args:
        valor_financiado: Valor do empréstimo
        parcelas_mensais: Lista com valor de cada parcela
        prazo_meses: Número total de parcelas
        aliquota_linear: Alíquota linear (%)
        aliquota_relativa: Alíquota por parcela (%)
    
    Returns:
        Dict com IOF linear, relativo, total e impacto nas parcelas
    
    Exemplo:
        >>> iof = calcular_iof(327650.72, [2764]*360, 360)
        >>> print(iof['iof_total'])
        5234.56  # Aproximado
    """
    
    valor_dec = Decimal(str(valor_financiado))
    
    # ===== IOF LINEAR =====
    # Aplicado uma única vez sobre o valor total
    iof_linear = valor_dec * Decimal(str(aliquota_linear))
    
    # ===== IOF RELATIVO =====
    # Aplicado sobre cada parcela
    iof_relativo = Decimal('0')
    for parcela in parcelas_mensais:
        iof_relativo += Decimal(str(parcela)) * Decimal(str(aliquota_relativa))
    
    # ===== TOTAL IOF =====
    iof_total = iof_linear + iof_relativo
    
    # ===== IMPACTO NAS PARCELAS =====
    # Distribuir IOF ao longo das parcelas
    iof_por_parcela = iof_total / Decimal(str(prazo_meses))
    
    parcelas_com_iof = []
    for parcela in parcelas_mensais:
        parcelas_com_iof.append(float(Decimal(str(parcela)) + iof_por_parcela))
    
    # ===== PRIMEIRA PARCELA COM IOF CONCENTRADO =====
    # Alternativa: colocar IOF linear inteiro na 1ª parcela
    parcelas_com_iof_concentrado = parcelas_mensais.copy()
    parcelas_com_iof_concentrado[0] += float(iof_linear / Decimal(str(prazo_meses)))
    
    return {
        'valor_financiado': float(valor_dec),
        
        # Componentes do IOF
        'iof_linear_percentual': aliquota_linear * 100,
        'iof_linear_valor': float(iof_linear),
        
        'iof_relativo_percentual': aliquota_relativa * 100,
        'iof_relativo_valor': float(iof_relativo),
        
        'iof_total': float(iof_total),
        'iof_percentual_total': (float(iof_total) / float(valor_dec)) * 100,
        
        # Impacto nas parcelas
        'iof_por_parcela_distribuido': float(iof_por_parcela),
        'parcelas_com_iof_distribuido': parcelas_com_iof,
        'parcelas_com_iof_primeira': parcelas_com_iof_concentrado,
        
        # Custo total do financiamento
        'valor_total_com_iof': sum(parcelas_com_iof),
        'aumento_percentual': (sum(parcelas_com_iof) - sum(parcelas_mensais)) / sum(parcelas_mensais) * 100,
    }
```

### 🧪 Teste Imediato

```python
# NOVO TESTE
from simulacao.calculadora_financeira import calcular_iof

print("=" * 80)
print("TESTE: CÁLCULO DE IOF")
print("=" * 80)

# Usar valores do contrato Itaú
parcelas = [2764.0] * 360  # Aproximado
iof = calcular_iof(327650.72, parcelas, 360)

print(f"\n💰 VALOR FINANCIADO: R$ {iof['valor_financiado']:,.2f}")

print(f"\n📊 COMPONENTES DO IOF:")
print(f"  ├─ IOF Linear (0,938%): R$ {iof['iof_linear_valor']:,.2f}")
print(f"  ├─ IOF Relativo (0,5%): R$ {iof['iof_relativo_valor']:,.2f}")
print(f"  └─ TOTAL IOF: R$ {iof['iof_total']:,.2f}")

print(f"\n📈 IMPACTO NAS PARCELAS:")
print(f"  ├─ Parcelas SEM IOF: R$ {sum(parcelas):,.2f}")
print(f"  ├─ Parcelas COM IOF: R$ {iof['valor_total_com_iof']:,.2f}")
print(f"  └─ Aumento: {iof['aumento_percentual']:.2f}%")

# Validação
assert iof['iof_total'] > 0, "IOF deve ser positivo!"
assert iof['iof_total'] < sum(parcelas) * 0.05, "IOF não deve ser > 5% do total"

print(f"\n✅ TESTE PASSOU - IOF calculado corretamente!")
```

---

## ⚡ FASE 3: IPTU / CONDOMÍNIO (2-3 HORAS)

[Continua como as outras fases...]

---

## 📋 PRÓXIMOS PASSOS

Quer que eu continue com as Fases 3, 4 e 5? Ou prefere que comecemos implementando a **Fase 1 (Consórcio + IOF)** imediatamente?

**Recomendação:** 
1. Implementar Fase 1 agora (mais rápido, mais impacto)
2. Testes contra PDFs Itaú
3. Depois Fase 2

Qual sua preferência? 🚀
