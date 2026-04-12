# Tarefa: Mapear Divergências Técnicas 📉
**Agente:** Dante Dados

## 🎯 Objetivo
Cruzar os dados reais de mercado com a lógica do código e apontar onde o app está falhando na precisão.

## 📋 Instruções
1. Leia o `research-brief.md` gerado pela Rita Referência.
2. Compare os dados de mercado com o snapshot da lógica atual que você mapeou.
3. Identifique as divergências (Deltas) críticas:
   - Seguros: Há subestimativa ou superestimativa?
   - Taxas: O CET calculado pelo app bate com o real dos bancos?
   - MCMV: As faixas de renda e taxas no código estão defasadas?
   - Aluguel: As taxas de administração e yield estão alinhadas com o QuintoAndar?
4. Para cada divergência encontrada, documente:
   - **Localização:** Arquivo e linha de código.
   - **Descrição do Erro:** O que está errado e por que.
   - **Benchmark:** Qual o valor correto segundo a Rita.
   - **Impacto:** Como isso afeta o usuário final (em Reais R$).
5. Identifique bugs de UX relacionados a finanças (ex: formatação de moeda, campos vazios).

## 📥 Input
- `research-brief.md` (Rita).
- Snapshot interno da lógica do código.

## 📤 Output
- Arquivo: `analysis-report.md` (Mapeamento detalhado de divergências e erros).

## 💡 Dicas
- Use exemplos reais (Simulando um imóvel de 500k com comprador de 40 anos) para mostrar o erro na prática.
- Se o erro for pequeno (<1%), avalie se vale a pena a correção ou se é apenas arredondamento.
