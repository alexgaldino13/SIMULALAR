# RESEARCH BRIEF: Auditoria Financeira SIMULALAR
**Data:** 10/04/2026
**Foco:** Seguros MIP/DFI e Taxas de Mercado (Caixa/Santander/QuintoAndar)

---

## 1. Seguros Obrigatórios (MIP e DFI)

| Banco | Tipo | Base de Cálculo | Taxa/Valor Visto | Notas |
|-------|------|-----------------|------------------|-------|
| **Caixa** | MIP | Saldo Devedor x Idade | 0.0104% (30a) a 0.23% (70a) | Escalonamento agressivo após 55 anos. |
| **Caixa** | DFI | Valor Imóvel (Avaliação) | ~0.0050% | Ex: Imóvel 500k = R$ 25,00/mês. |
| **Santander** | MIP | Saldo Devedor x Idade | 0.015% a 0.20% | Ligeiramente superior à Caixa em idades baixas. |
| **Santander** | DFI | Valor Reconstrução | 0.005% a 0.008% | Varia conforme contrato. |

**Divergência Crítica:** O app SIMULALAR usa um valor fixo de **R$ 30,00** para DFI. Em um imóvel de R$ 1MM, o DFI real seria ~R$ 50,00 (Erro de 40%).

---

## 2. Taxas de Administração e CET

- **Santander:** Taxa de Administração Mensal de **R$ 25,00**.
- **Caixa:** Taxa de Administração Mensal de **R$ 25,00** (SBPE).
- **Custo Efetivo Total (CET):** Em média **1.2% a 1.5%** acima da taxa nominal devido a taxas e seguros.
- **MCMV (Minha Casa Minha Vida):** Novas faixas de renda (Faixa 1 até R$ 2.640, Faixa 2 até R$ 4.400, Faixa 3 até R$ 8.000). Taxas variam de 4% a 7.66% + TR.

---

## 3. Benchmark QuintoAndar (Aluguel)

- **Taxa de Administração:** 8% a 10% (Média **9.3%**).
- **Corretagem (1º Aluguel):** 100%.
- **Rental Yield (Residencial SP):** ~0.45% a 0.55% do valor do imóvel.
- **Valorização Imobiliária (IGP-M/IPCA):** Reajuste anual pelo índice contratado + valorização real histórica (~2-3% aa).

---

## 4. Fontes e Confiança
1. [Simulador CEF](https://habita-internet.caixa.gov.br/) - Confiança: **Alta**
2. [Tabela de Tarifas Santander](https://www.santander.com.br/) - Confiança: **Alta**
3. [Relatório Mensal QuintoAndar](https://www.quintoandar.com.br/) - Confiança: **Média** (Varia por bairro)

**Acesso em:** 10/04/2026
**Responsável:** Rita Referência
