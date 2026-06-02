# Relatório de Divergências Técnicas 📊
**Agente:** Dante Dados

## 1. Minha Casa, Minha Vida (MCMV)
**Divergência Crítica Identificada.**
- **Código Atual:** Faixa 1 limitada a R$ 2.850,00. Limite Max de R$ 9.000,00.
- **Mercado (2025):** Faixa 1 até R$ 3.200,00. Faixa 4 até R$ 13.000,00.
- **Impacto:** O simulador está redirecionando usuários de baixa/média renda para o SBPE (juros caros) indevidamente.
- **Localização:** `calculadora_financeira.py` (Linhas 17-19).

## 2. Seguros Habitacionais (MIP/DFI)
**Divergência de Precisão.**
- **MIP (60 anos):** O código usa 0,082%. Benchmarks da Rita indicam que para 60 anos a taxa real de mercado (Caixa/Itaú) já ultrapassa 0,15%.
- **Impacto:** Subestimação do custo da parcela para o público sênior em quase 50% no componente de seguro.
- **Localização:** `calculadora_financeira.py` (Linha 42).

## 3. Financiamento SBPE (Taxas Base)
- **Código:** `TAXA_JUROS_PADRAO = Decimal('10.5')`.
- **Mercado:** Variando entre 10,26% (Caixa) e 12,79% (Bradesco).
- **Impacto:** O padrão de 10.5% é otimista para o cenário de bancos privados em 2025/2026.
- **Ação Sugerida:** Tornar o campo de taxa padrão no Wizard dinâmico baseado na média do Top 3 bancos.

## 4. Aluguel + Investimento
- **Lógica:** Consistente com o mercado (9,3% taxa adm).
- **Ponto de Atenção:** O rendimento do FGTS (3% + TR) está correto, mas o rendimento de investimentos padrão no formulário precisa ser validado contra o CDI atual (11%).

---
**Status da Auditoria:** 3 inconsistências graves, 2 inconsistências leves.
**Recomendação:** Refatoração imediata dos limites MCMV e tabela MIP.
