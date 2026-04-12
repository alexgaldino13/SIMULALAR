# RELATÓRIO DE ANÁLISE: Divergências Financeiras
**Responsável:** Dante Dados 📊
**Data:** 10/04/2026

## 1. Mapeamento de Divergências Críticas

### 1.1. Seguro DFI (Danos Físicos ao Imóvel)
- **Local:** `calculadora_financeira.py:165`
- **Comportamento Atual:** Valor fixo de `Decimal('30.00')`.
- **Benchmark (Caixa/Santander):** ~0.005% sobre o valor de avaliação/reconstrução do imóvel.
- **Impacto:** 
  - Imóvel R$ 200k: Erro de +R$ 20/mês (Superestimado).
  - Imóvel R$ 1.2M: Erro de -R$ 30/mês (Subestimado).
- **Risco:** Perda de credibilidade em imóveis de alto padrão ou populares (MCMV).

### 1.2. Seguro MIP (Morte e Invalidez) por Faixa Etária
- **Local:** `calculadora_financeira.py:23-34` (Função `obter_taxa_mip_por_idade`)
- **Divergência:** As taxas para idades acima de 50 anos estão defasadas em relação à Tabela CEF 2024.
  - **Código (51-60a):** 0.065%.
  - **Mercado (Caixa):** ~0.071% a 0.085%.
- **Impacto:** O app subestima o custo do financiamento para o público sênior, gerando "surpresa negativa" na hora da contratação real.

### 1.3. Faixas de Renda MCMV (Minha Casa Minha Vida)
- **Local:** `calculadora_financeira.py:794` em diante.
- **Divergência:** Os limites de renda para Faixa 1 (atualmente R$ 2.640 no código) foram reajustados.
- **Benchmark:** Novo limite Faixa 1 é de **R$ 2.850,00**.
- **Impacto:** Usuários com renda entre 2.640 e 2.850 são classificados incorretamente na Faixa 2, pagando juros maiores na simulação do que pagariam na realidade.

### 1.4. Taxa de Administração Mensal
- **Local:** `calculadora_financeira.py:40` e `wizard_views_v2.py:235`.
- **Divergência:** No `wizard_views_v2.py` (linha 235), há uma taxa de juros fixa de 8.5% e admin fee não é explicitada ou resetada conforme o banco.
- **Benchmark:** Caixa e Santander cobram **R$ 25,00/mês** fixos para manutenção de contrato (SBPE).

---

## 2. Visão de Investimento e Aluguel

### 2.1. Taxa de Administração de Aluguel
- **Local:** `calculadora_financeira.py` (Funções de Aluguel/Investidor).
- **Divergência:** A função `simular_aluguel_investimento` não deduz a taxa de administração do proprietário.
- **Benchmark (QuintoAndar):** 9.3% de taxa de gestão sobre o aluguel bruto.
- **Impacto:** Superestatística do ganho líquido do investidor. O app diz que ele ganha mais do que realmente sobrará no bolso.

---

## 3. Resumo de Bugs de Experiência (UX)

1. **Campos Vazios no Resultado:** No template `wizard_v2_resultados.html`, o campo 'Custo Total + Aluguel' estava aparecendo vazio (corrigido parcialmente na sessão anterior mas requer validação em cenários de Consórcio).
2. **Moeda Redundante:** O uso de `R$ {{ valor|floatformat }}` causa exibição duplicada caso o helper `formatar_moeda_brl` já injete o símbolo.

---

## 4. Próximos Passos Recomendados

1.  **Parametrizar DFI:** Alterar a constante fixa por uma função `calcular_dfi(valor_imovel)`.
2.  **Atualizar Tabela MIP:** Sincronizar as faixas de 50, 60 e 70 anos com os índices atuais (Caixa/Santander).
3.  **Ajustar MCMV:** Atualizar limites de renda para adequação à portaria do Governo Federal de 2024.
4.  **Taxa de Gestão:** Incluir o parâmetro `taxa_administracao_aluguel` nas simulações de investimento.

---
**Status:** Análise Concluída. Pronto para Auditoria Final da Vera Veredito.
