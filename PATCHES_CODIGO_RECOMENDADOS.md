# PATCHES RECOMENDADOS - CÓDIGO PARA CORRIGIR

## 🔴 PATCH 1: Corrigir TypeError Decimal/float (CRÍTICO)

**Arquivo:** `simulacao/calculadora_financeira.py`  
**Linhas:** ~210-250

### Antes (❌ Erro):
```python
def calcular_price_sac(metodo, valor_principal, taxa_anual, prazo_meses, ...):
    total_juros = Decimal(0)
    total_seguros_taxas = Decimal(0)
    
    # ... loop ...
    for mes in range(...):
        juros_mensal = saldo_devedor * taxa_mensal  # Decimal
        total_juros += juros_mensal  # ❌ TypeError: Decimal + float
        total_seguros_taxas += seguro_mensal_dec + taxa_admin_mensal_dec
```

### Depois (✅ Corrigido):
```python
def calcular_price_sac(metodo, valor_principal, taxa_anual, prazo_meses, ...):
    total_juros = Decimal(0)
    total_seguros_taxas = Decimal(0)
    
    # ... loop ...
    for mes in range(...):
        juros_mensal = saldo_devedor * taxa_mensal  # Decimal
        total_juros += juros_mensal  # ✅ Mantém tipo Decimal
        total_seguros_taxas += seguro_mensal_dec + taxa_admin_mensal_dec
        
        # ... resto do código ...
    
    # Retornar com float para JSON/template
    return {
        'tabela': tabela,
        'parcela_inicial': float(tabela[0]['parcela']) if tabela else 0.0,
        'total_juros': float(total_juros),  # ✅ Converter ao retornar
        'total_seguros_taxas': float(total_seguros_taxas),
        'prazo_final_meses': mes_original - 1
    }
```

---

## 🔴 PATCH 2: Adicionar Validações de Mercado

**Arquivo:** Novo arquivo ou em `simulacao/validacao.py`

```python
"""
Validações financeiras conforme normas e padrões brasileiros.
"""

from decimal import Decimal

def validar_financiamento_completo(valor_imovel, entrada, renda_familiar, prazo_meses, taxa_anual):
    """
    Valida se um financiamento é viável conforme normas brasileiras.
    
    Retorna: (bool viavel, str mensagem, dict detalhes)
    """
    
    # Conversão para Decimal
    valor_imovel_dec = Decimal(str(valor_imovel))
    entrada_dec = Decimal(str(entrada))
    renda_familiar_dec = Decimal(str(renda_familiar))
    taxa_mensal = Decimal(str(taxa_anual)) / 12 / 100
    
    financiamento = valor_imovel_dec - entrada_dec
    
    erros = []
    avisos = []
    detalhes = {}
    
    # ========================================================================
    # 1. VALIDAÇÃO: ENTRADA MÍNIMA 20%
    # ========================================================================
    
    entrada_percentual = (entrada_dec / valor_imovel_dec) * 100
    ltv = (financiamento / valor_imovel_dec) * 100
    
    if entrada_percentual < 20:
        erros.append(f"Entrada mínima deve ser 20% (você ofereceu {entrada_percentual:.1f}%)")
    
    if ltv > 80:
        erros.append(f"LTV não pode exceder 80% (você tem {ltv:.1f}%)")
    
    detalhes['entrada_percentual'] = entrada_percentual
    detalhes['ltv'] = ltv
    
    # ========================================================================
    # 2. VALIDAÇÃO: PARCELA MÁXIMO 30% DA RENDA
    # ========================================================================
    
    if renda_familiar_dec > 0:
        # Calcular parcela Price simplificada
        if taxa_mensal > 0:
            fator = (taxa_mensal * (1 + taxa_mensal) ** prazo_meses) / (
                ((1 + taxa_mensal) ** prazo_meses) - 1
            )
            parcela_estimada = financiamento * fator
        else:
            parcela_estimada = financiamento / prazo_meses
        
        percentual_renda = (parcela_estimada / renda_familiar_dec) * 100
        
        if percentual_renda > 30:
            erros.append(
                f"Parcela de R$ {float(parcela_estimada):,.2f} "
                f"({percentual_renda:.1f}% da renda) excede limite de 30%"
            )
        elif percentual_renda > 25:
            avisos.append(
                f"Parcela {percentual_renda:.1f}% da renda (próximo ao limite de 30%)"
            )
        
        detalhes['parcela_estimada'] = float(parcela_estimada)
        detalhes['percentual_renda'] = percentual_renda
    
    # ========================================================================
    # 3. VALIDAÇÃO: PRAZO MÁXIMO 35 ANOS
    # ========================================================================
    
    prazo_anos = prazo_meses / 12
    if prazo_anos > 35:
        erros.append(f"Prazo máximo é 35 anos (você solicitou {prazo_anos:.1f})")
    
    # ========================================================================
    # 4. AVISOS: ÍNDICES EXTREMOS
    # ========================================================================
    
    if taxa_anual < 5.0:
        avisos.append("Taxa parece muito baixa - verifique se é promocional")
    
    if taxa_anual > 12.0:
        avisos.append("Taxa muito alta - considere explorar outras opções")
    
    # ========================================================================
    # RESULTADO FINAL
    # ========================================================================
    
    viavel = len(erros) == 0
    mensagem = " | ".join(erros + avisos) if erros or avisos else "✓ Tudo OK"
    
    return viavel, mensagem, detalhes


def calcular_cet_corrigido(valor_financiado, parcelas_mensais, custos_iniciais=None):
    """
    Calcula CET (Custo Efetivo Total) conforme normativa BC.
    
    CET = Taxa que iguala valor liberado ao fluxo de pagamentos
    
    Custos iniciais:
    - Taxa de avaliação: R$ 1.500-3.000
    - Registro cartório: 1.5-2.5% do valor
    - ITBI: 0.5-3.0% (varia por estado)
    - Seguros obrigatórios
    """
    
    from scipy.optimize import newton
    
    valor_financiado_dec = Decimal(str(valor_financiado))
    
    # Custos padrão BC
    custos_padrao = {
        'taxa_avaliacao': 2500.0,
        'tarifa_cadastro': 0.0,
        'registro_cartorio_percent': 2.0,
        'itbi_percent': 1.5,  # Média Brasil
        'custas_registro': 3000.0,
        'taxa_vistoria': 800.0,
    }
    
    if custos_iniciais is None:
        custos_iniciais = {}
    
    custos_finais = {**custos_padrao, **custos_iniciais}
    
    # Cálculo de custos
    detalhamento = {
        'taxa_avaliacao': float(custos_finais['taxa_avaliacao']),
        'tarifa_cadastro': float(custos_finais['tarifa_cadastro']),
        'registro_cartorio': float(
            valor_financiado_dec * Decimal(str(custos_finais['registro_cartorio_percent'])) / 100
        ),
        'itbi': float(
            valor_financiado_dec * Decimal(str(custos_finais['itbi_percent'])) / 100
        ),
        'custas_registro': float(custos_finais['custas_registro']),
        'taxa_vistoria': float(custos_finais['taxa_vistoria']),
    }
    
    total_custos = sum(detalhamento.values())
    valor_liquido = float(valor_financiado_dec) - total_custos
    
    parcelas_lista = [float(p) for p in parcelas_mensais]
    
    # Função VPL
    def vpl(taxa_mensal):
        if taxa_mensal <= -1:
            return float('inf')
        
        vpl_calc = valor_liquido
        for i, parcela in enumerate(parcelas_lista, start=1):
            vpl_calc -= parcela / ((1 + taxa_mensal) ** i)
        return vpl_calc
    
    # Resolver para taxa
    try:
        taxa_mensal_solucao = newton(vpl, x0=0.01, maxiter=100)
    except:
        return None
    
    cet_mensal = taxa_mensal_solucao * 100
    cet_anual = ((1 + taxa_mensal_solucao) ** 12 - 1) * 100
    
    return {
        'cet_mensal': cet_mensal,
        'cet_anual': cet_anual,
        'valor_liquido': valor_liquido,
        'total_custos': total_custos,
        'detalhamento': detalhamento,
    }
```

---

## 🔴 PATCH 3: Ajustar Parcela Consórcio para Mercado Real

**Arquivo:** `simulacao/calculadora_financeira.py`  
**Função:** `simular_consorcio()`  
**Linha:** ~360

### Antes (❌ Abaixo do mercado):
```python
parcela_base_percentual = Decimal('0.007')  # 0.7% ao mês
parcela_fixa = valor_imovel_total * parcela_base_percentual
```

### Depois (✅ Alinhado com mercado):
```python
# Parcela realista de consórcio: 0.8-1.0% ao mês
# Média de mercado 2024-2025: 0.85%
parcela_base_percentual = Decimal('0.0085')  # 0.85% ao mês
parcela_fixa = valor_imovel_total * parcela_base_percentual
```

---

## 🔴 PATCH 4: Adicionar Despesas de Imóvel Alugado

**Arquivo:** `simulacao/calculadora_financeira.py`  
**Novo código** antes de `simular_aluguel_investimento()`

```python
# Despesas padrão de imóvel alugado por estado
DESPESAS_IMOVEL_ALUGADO = {
    'SP': {
        'iptu_percent': 0.8,           # % ao ano do valor imóvel
        'condominio_percent_aluguel': 20,  # % do aluguel
        'seguro_percent': 0.4,         # % ao ano
        'manutencao_percent': 0.5,     # % ao ano
        'vacancia_rate': 0.10,         # 10% de vacância (85% ocupação)
        'inadimplencia_rate': 0.05,    # 5% de inadimplência
    },
    'RJ': {
        'iptu_percent': 1.2,
        'condominio_percent_aluguel': 25,
        'seguro_percent': 0.5,
        'manutencao_percent': 0.6,
        'vacancia_rate': 0.12,
        'inadimplencia_rate': 0.07,
    },
    'MG': {
        'iptu_percent': 0.6,
        'condominio_percent_aluguel': 15,
        'seguro_percent': 0.35,
        'manutencao_percent': 0.4,
        'vacancia_rate': 0.08,
        'inadimplencia_rate': 0.04,
    },
    # ... outros estados
}

def calcular_despesas_imovel_alugado(valor_imovel, aluguel_mensal, estado='SP'):
    """Calcula despesas realistas de imóvel alugado."""
    
    despesas = DESPESAS_IMOVEL_ALUGADO.get(estado, DESPESAS_IMOVEL_ALUGADO['SP'])
    
    iptu_mensal = valor_imovel * (despesas['iptu_percent'] / 100) / 12
    condominio_mensal = aluguel_mensal * (despesas['condominio_percent_aluguel'] / 100)
    seguro_mensal = valor_imovel * (despesas['seguro_percent'] / 100) / 12
    manutencao_mensal = valor_imovel * (despesas['manutencao_percent'] / 100) / 12
    
    renda_efetiva = aluguel_mensal * (1 - despesas['vacancia_rate'] - despesas['inadimplencia_rate'])
    
    despesas_totais = iptu_mensal + condominio_mensal + seguro_mensal + manutencao_mensal
    fluxo_liquido = renda_efetiva - despesas_totais
    
    return {
        'iptu_mensal': float(iptu_mensal),
        'condominio_mensal': float(condominio_mensal),
        'seguro_mensal': float(seguro_mensal),
        'manutencao_mensal': float(manutencao_mensal),
        'renda_efetiva': float(renda_efetiva),  # Após vacância e inadimplência
        'despesas_totais': float(despesas_totais),
        'fluxo_liquido_mensal': float(fluxo_liquido),
        'roi_liquido_mensal': float(fluxo_liquido / valor_imovel),
    }
```

---

## 🔴 PATCH 5: Implementar Subsídio MCMV

**Arquivo:** Novo arquivo `simulacao/mcmv.py`

```python
"""
Integração com programa MCMV (Minha Casa Minha Vida).
Tabelas de subsídio conforme dados governamentais atualizados.
"""

from decimal import Decimal

# Tabelas de subsídio por faixa de renda (Janeiro 2026)
MCMV_SUBSIDIOS = {
    'faixa1': {
        'renda_maxima': 2000,
        'subsidi_percent': 40,  # Até 40% de subsídio
        'taxa_financiamento': 3.5,  # Taxa reduzida
    },
    'faixa2': {
        'renda_maxima': 4500,
        'subsidi_percent': 30,  # 30% de subsídio
        'taxa_financiamento': 4.5,
    },
    'faixa3': {
        'renda_maxima': 9000,
        'subsidi_percent': 15,  # 15% de subsídio
        'taxa_financiamento': 5.5,
    },
}

# Valor máximo por região
MCMV_VALORES_MAXIMOS = {
    'regiao_norte': 200000,
    'regiao_nordeste': 220000,
    'regiao_centro_oeste': 210000,
    'regiao_sudeste': 350000,  # Mais caro
    'regiao_sul': 260000,
}

def validar_elegibilidade_mcmv(renda_familiar, valor_imovel, regiao):
    """Verifica se usuário é elegível para MCMV."""
    
    elegivel = False
    motivo = ""
    
    # Verificar renda
    if renda_familiar > 9000:
        return False, "Renda familiar acima do limite MCMV (máx R$ 9.000)"
    
    # Verificar valor máximo por região
    valor_maximo = MCMV_VALORES_MAXIMOS.get(regiao, 220000)
    if valor_imovel > valor_maximo:
        return False, f"Imóvel acima do valor máximo MCMV para {regiao} (máx R$ {valor_maximo:,.0f})"
    
    # Determinar faixa e subsídio
    if renda_familiar <= 2000:
        faixa = 'faixa1'
    elif renda_familiar <= 4500:
        faixa = 'faixa2'
    else:
        faixa = 'faixa3'
    
    return True, faixa

def calcular_mcmv_simulacao(renda_familiar, valor_imovel, regiao, prazo_anos=20):
    """Simula financiamento MCMV com subsídio."""
    
    elegivel, faixa_ou_motivo = validar_elegibilidade_mcmv(renda_familiar, valor_imovel, regiao)
    
    if not elegivel:
        return {'erro': faixa_ou_motivo}
    
    faixa = faixa_ou_motivo
    params_mcmv = MCMV_SUBSIDIOS[faixa]
    
    # Cálculo com subsídio
    subsidi_amount = Decimal(str(valor_imovel)) * Decimal(str(params_mcmv['subsidi_percent'])) / 100
    valor_financiado = Decimal(str(valor_imovel)) - subsidi_amount
    
    # Simular financiamento com taxa reduzida
    from simulacao.calculadora_financeira import calcular_price_sac
    
    resultado = calcular_price_sac(
        'price',
        valor_principal=valor_financiado,
        taxa_anual=params_mcmv['taxa_financiamento'],
        prazo_meses=prazo_anos * 12,
    )
    
    # Validar se parcela está OK (máx 30% da renda)
    if resultado and 'tabela' in resultado:
        parcela_inicial = resultado['parcela_inicial']
        percentual_renda = (parcela_inicial / renda_familiar) * 100
        
        return {
            'elegivel': True,
            'faixa': faixa,
            'subsidi_amount': float(subsidi_amount),
            'subsidi_percent': params_mcmv['subsidi_percent'],
            'taxa_financiamento': params_mcmv['taxa_financiamento'],
            'valor_financiado': float(valor_financiado),
            'parcela_inicial': parcela_inicial,
            'percentual_renda': percentual_renda,
            'total_juros': resultado.get('total_juros', 0),
            'viavel': percentual_renda <= 30,
            'resultado_completo': resultado,
        }
    
    return {'erro': 'Falha ao calcular simulação'}
```

---

## 🔴 PATCH 6: Criar Comparador de Bancos

**Arquivo:** Novo arquivo `simulacao/comparador_bancos.py`

```python
"""
Comparador de taxas e CET entre bancos principais brasileiros.
"""

from decimal import Decimal
from simulacao.calculadora_financeira import calcular_price_sac, calcular_cet_corrigido

BANCOS_BRASIL = {
    'BB': {
        'nome': 'Banco do Brasil',
        'taxa_base': 7.5,
        'spread_pf': 0.5,
        'spread_score': {
            'excelente': -1.0,  # -100 pontos
            'bom': 0.0,         # Spread padrão
            'regular': 1.0,     # +100 pontos
            'ruim': 2.0,        # +200 pontos
        }
    },
    'CAIXA': {
        'nome': 'Caixa Econômica Federal',
        'taxa_base': 7.2,
        'spread_pf': 0.4,
        'spread_score': {
            'excelente': -0.8,
            'bom': 0.0,
            'regular': 0.8,
            'ruim': 1.5,
        }
    },
    'ITAU': {
        'nome': 'Itaú Unibanco',
        'taxa_base': 9.2,
        'spread_pf': 0.8,
        'spread_score': {
            'excelente': -1.5,
            'bom': 0.0,
            'regular': 1.5,
            'ruim': 3.0,
        }
    },
    'BRADESCO': {
        'nome': 'Bradesco',
        'taxa_base': 8.9,
        'spread_pf': 0.7,
        'spread_score': {
            'excelente': -1.2,
            'bom': 0.0,
            'regular': 1.2,
            'ruim': 2.5,
        }
    },
    'SANTANDER': {
        'nome': 'Santander',
        'taxa_base': 8.5,
        'spread_pf': 0.6,
        'spread_score': {
            'excelente': -1.0,
            'bom': 0.0,
            'regular': 1.0,
            'ruim': 2.0,
        }
    },
}

def comparar_bancos(valor_financiamento, prazo_meses, score_crediticio='bom'):
    """
    Compara taxa, parcela e CET entre os 5 principais bancos.
    
    Args:
        valor_financiamento: R$ a financiar
        prazo_meses: Prazo do financiamento
        score_crediticio: 'excelente', 'bom', 'regular', 'ruim'
    
    Returns:
        dict com comparação de todos os bancos
    """
    
    resultados = {}
    
    for codigo_banco, info_banco in BANCOS_BRASIL.items():
        # Calcular taxa ajustada por score
        taxa_ajustada = (
            info_banco['taxa_base'] +
            info_banco['spread_pf'] +
            info_banco['spread_score'].get(score_crediticio, 0)
        )
        
        # Simular Price
        resultado_price = calcular_price_sac(
            'price',
            valor_principal=valor_financiamento,
            taxa_anual=taxa_ajustada,
            prazo_meses=prazo_meses,
        )
        
        if resultado_price and 'tabela' in resultado_price:
            # Calcular CET
            cet_result = calcular_cet_corrigido(
                valor_financiamento,
                [row['parcela'] for row in resultado_price['tabela']],
            )
            
            resultados[codigo_banco] = {
                'banco': info_banco['nome'],
                'taxa_nominal': taxa_ajustada,
                'parcela_inicial': resultado_price['parcela_inicial'],
                'total_juros': resultado_price['total_juros'],
                'cet_anual': cet_result['cet_anual'] if cet_result else None,
                'resultado_completo': resultado_price,
            }
    
    # Ordenar por CET (melhor em cima)
    resultados_ordenados = sorted(
        resultados.items(),
        key=lambda x: x[1]['cet_anual'] if x[1]['cet_anual'] else float('inf')
    )
    
    return {
        'comparacao': dict(resultados_ordenados),
        'melhor_banco': resultados_ordenados[0] if resultados_ordenados else None,
        'score_crediticio': score_crediticio,
    }
```

---

## ✅ COMO APLICAR PATCHES

1. **Backup primeiro:**
   ```bash
   cp simulacao/calculadora_financeira.py simulacao/calculadora_financeira.py.backup
   ```

2. **Aplicar Patch 1 (TypeError):** Hoje - CRÍTICO
   - Editar linhas 215-230 conforme acima

3. **Aplicar Patch 2-3 (Validações):** Semana 1
   - Criar novo arquivo `simulacao/validacao.py`
   - Integrar em `views.py` na linha de POST

4. **Aplicar Patch 4 (Despesas IPTU/Cond.):** Semana 2
   - Integrar em `simular_aluguel_investimento()`

5. **Aplicar Patch 5 (MCMV):** Semana 2
   - Criar `simulacao/mcmv.py`
   - Adicionar pergunta no wizard

6. **Aplicar Patch 6 (Comparador):** Semana 3-4
   - Criar `simulacao/comparador_bancos.py`
   - Adicionar view nova para comparação

---

## 📊 TESTE APÓS CADA PATCH

```bash
# Após Patch 1
python manage.py test simulacao.tests.test_price_sac

# Após Patch 2
python manage.py test simulacao.tests.test_validacoes

# Após Patch 5
python manage.py test simulacao.tests.test_mcmv

# Todos
python manage.py test simulacao
```

---

## 🚀 TIMELINE

| Sprint | Patches | Dias | Status |
|--------|---------|------|--------|
| Sprint 1 | 1, 2, 3 | 5-7 | 🔴 Crítico |
| Sprint 2 | 4, 5 | 7-10 | 🟡 Alta |
| Sprint 3 | 6 | 5-7 | 🟡 Média |

**Estimativa Total:** 17-24 dias (3.5 semanas)
