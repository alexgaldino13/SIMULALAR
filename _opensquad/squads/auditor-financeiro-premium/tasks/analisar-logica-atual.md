# Tarefa: Analisar Lógica Atual 📊
**Agente:** Dante Dados

## 🎯 Objetivo
Analisar o código fonte do projeto para entender como os cálculos financeiros são feitos atualmente.

## 📋 Instruções
1. Abra os arquivos `simulacao/calculadora_financeira.py` e `simulacao/wizard_views_v2.py`.
2. Mapeie as seguintes variáveis no código:
   - Fórmulas de amortização (SAC e Price).
   - Constantes de seguros (MIP e DFI). Onde estão definidas? São fixas ou variáveis?
   - Taxas administrativas mensais e custos de documentação.
   - Lógica do MCMV (faixas de renda, subsídios e taxas por faixa).
   - Lógica de Aluguel vs Investimento (taxas de reajuste, inflação e rendimento padrão).
3. Documente o comportamento atual do código:
   - O que o código assume por padrão?
   - Quais parâmetros o usuário pode alterar?
4. Gere um resumo técnico (Snapshot) da lógica atual para comparação.

## 📥 Input
- Arquivos do projeto: `simulacao/calculadora_financeira.py`, `simulacao/wizard_views_v2.py`.

## 📤 Output
- Contexto de trabalho interno para a próxima tarefa (`mapear-divergencias-tecnicas`).

## 💡 Dicas
- Procure por comentários `# Constantes` ou funções como `obter_taxa_mip_por_idade`.
- Note se o código usa decimais (`Decimal`) ou floats, para checar precisão.
