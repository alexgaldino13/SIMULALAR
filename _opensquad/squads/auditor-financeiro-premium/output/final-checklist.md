# CHECKLIST DE AUDITORIA: Melhoria de Precisão e Confiabilidade (V1.0)
**Auditado por:** Vera Veredito ✅
**Status:** Aprovado para Refatoração Técnica

Este checklist contém as ações necessárias para tornar o SIMULALAR a ferramenta de simulação mais precisa do Brasil, alinhada aos padrões bancários de 2024.

---

## 🛠️ 1. Correções de Lógica Financeira (CRÍTICO)

### [ ] Item 1.1: Dinamização do Seguro DFI
- **Problema:** Valor fixo de R$ 30,00 subestima custos em imóveis caros e superestima em imóveis baratos.
- **Ação:** Em `calculadora_financeira.py:165`, substituir o valor fixo por uma chamada à nova função `obter_seguro_dfi(valor_imovel)` que utilize o coeficiente de **0.005%**.
- **Critério de Aceite:** Simulação de imóvel de R$ 1MM deve mostrar DFI de R$ 50,00.

### [ ] Item 1.2: Atualização da Tabela MIP (Referência CEF/Santander)
- **Problema:** Taxas para idades acima de 50 anos estão defasadas.
- **Ação:** Atualizar o dicionário/condicionais em `obter_taxa_mip_por_idade` (calculadora_financeira.py:23).
  - 51-60a: 0.082% (Novo)
  - 61-70a: 0.165% (Novo)
- **Critério de Aceite:** Valor do seguro para comprador de 60 anos deve subir ~20% em relação ao cálculo atual.

### [ ] Item 1.3: Reajuste Faixa 1 MCMV
- **Problema:** Limite de renda defasado (R$ 2.640 vs R$ 2.850 real).
- **Ação:** Atualizar a constante de limite da Faixa 1 em `calcular_mcmv` (calculadora_financeira.py:794).
- **Critério de Aceite:** Renda de R$ 2.700 deve ser enquadrada na Faixa 1 (juros menores).

---

## 💎 2. Visão Humana e Monetização (EXPERIÊNCIA)

### [ ] Item 2.1: Taxa de Gestão do Investidor
- **Problema:** O simulador de investimento ignora que o proprietário paga ~9.3% para imobiliárias (QuintoAndar/Zap) gerirem o aluguel.
- **Ação:** Adicionar `taxa_administracao_aluguel` como parâmetro em `simular_aluguel_investimento`. Deduzir este valor do aluguel líquido reinvestido.
- **Motivo Monetização:** Corretores que usam o app para vender imóveis como investimento precisam de números reais. Números inflados queimam a venda no longo prazo.

### [ ] Item 2.2: Padronização de Nomenclatura UX
- **Ação:** Alterar labels no `wizard_v2_resultados.html` de "MIP" para "Seguro Morte/Invalidez" e "DFI" para "Seguro do Imóvel".
- **Motivo:** Linguagem humana aumenta a confiança do usuário leigo.

---

## ⚖️ VEREDITO DA AUDITORIA
O SIMULALAR possui uma base matemática sólida para SAC e PRICE, mas as **contas de apoio (Seguros e Taxas)** são o "ponto cego" que impede o app de ser considerado nível bancário hoje. 

**Recomendação:** Executar os itens críticos deste checklist imediatamente para garantir que o app possa ser monetizado com segurança perante corretores e investidores.

---
**Pronto para Execução?** Caso sim, posso iniciar a aplicação dos pontos técnicos listados.
