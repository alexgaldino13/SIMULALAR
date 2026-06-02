# Veredito da Auditoria Financeira ✅
**Agente:** Vera Veredito

A auditoria concluiu que o SIMULALAR possui uma lógica robusta, porém com parâmetros defasados em relação ao mercado de 2025/2026. Para manter a promessa de "melhor simulador do Brasil", a refatoração abaixo é obrigatória.

## 📋 Checklist de Refatoração (Prioridade Máxima)

### 1. [CRÍTICO] Atualizar Limites MCMV
- **Onde:** `calculadora_financeira.py` (Linhas 17-19)
- **Alteração:**
  - `LIMITE_RENDA_MCMV_FAIXA_1` -> de 2850.00 para **3200.00**
  - `LIMITE_RENDA_MCMV_MAX` -> de 9000.00 para **13000.00**
- **Motivo:** Garantir que o simulador não exclua o novo público da Faixa 4 e do teto atualizado da Faixa 1.

### 2. [URGENTE] Revisar Tabela MIP (60+ anos)
- **Onde:** `calculadora_financeira.py` (Linhas 40-43)
- **Alteração:**
  - Taxa 60 anos: de 0.082 para **0.155** (Alinhamento com Benchmark Caixa 2025).
- **Motivo:** Evitar quebras de expectativa financeira para o público sênior.

### 3. [MELHORIA] Dinamização de Taxas SBPE
- **Onde:** `wizard_forms_v2.py` e `wizard_views_v2.py`.
- **Alteração:** Sugerir ao usuário a taxa do banco que ele selecionar (ou a média do mercado 11.2% em vez de 10.5%).
- **Motivo:** Precisão na estimativa de CET.

### 4. [UX] Explicação de Taxa de Administração
- **Onde:** `wizard_v2_resultados.html`
- **Ação:** Adicionar um tooltip informando que a taxa de R$ 25,00 (SBPE) é padrão regulatório e já está inclusa no CET.

---
**Conclusão:** O squad considera o sistema **APROVADO COM RESSALVAS**.
As correções acima levam o projeto ao estado de **Produção-Ready (Gold)**.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
