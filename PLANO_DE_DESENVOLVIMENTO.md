# Plano de Desenvolvimento - App ImobCalc

## 📋 Visão Geral
App completo para simulação de financiamento imobiliário, consórcio e investimento, com versão grátis (com anúncios) e paga (com tabela de acompanhamento).

## 🎯 Público-Alvo
- Compradores
- Corretores
- Vendedores de consórcio
- Lojas/Bancos

## 🚀 Estrutura do Wizard (Fluxo Guiado)

### Etapa 1: Perfil do Usuário
- Quem é você? (Comprador/Corretor/Vendedor/Banco)
- Nome (opcional)
- Email (opcional, para salvar simulações)

### Etapa 2: Dados do Imóvel
- Valor do imóvel (R$)
- Valor da entrada (R$)
- Recursos disponíveis (FGTS, poupança, etc.)

### Etapa 3: Métodos de Interesse
- Quais métodos quer comparar?
  - ✅ Financiamento PRICE
  - ✅ Financiamento SAC
  - ✅ Consórcio
  - ✅ Guardar Dinheiro (Investimento)
  - ✅ Aluguel + Investimento

### Etapa 4: Parâmetros do Financiamento (se selecionado)
- Taxa de juros anual (%)
- Prazo (anos/meses)
- Seguro MIP/DFI (%)
- Usar FGTS? (sim/não, quando, reduzir prazo ou parcela)

### Etapa 5: Parâmetros do Consórcio (se selecionado)
- Taxa de administração anual (%)
- Fundo de reserva (%)
- Lance inicial FGTS (R$)
- Estratégia de lance (mínimo/médio/máximo por mês)
- Percentual mínimo/máximo de lance (% sobre carta de crédito)

### Etapa 6: Parâmetros de Investimento (se selecionado)
- Tipo de investimento (Poupança/CDB/Tesouro IPCA)
- Taxa de rendimento anual (%)
- Aportes mensais (R$)
- Aporte 13º (R$)

### Etapa 7: Comparação e Resultados
- Tabela comparativa
- Gráficos
- Recomendações

## 🔧 Melhorias Necessárias

### 1. Consórcio (Prioridade Alta)
**Variáveis Reais do Mercado:**
- Taxa de administração (0.5% a 2% a.a. sobre carta de crédito)
- Fundo de reserva (0.5% a 1.5% do valor total)
- Sistema de lances:
  - Lance mínimo: geralmente 5-10% da carta de crédito
  - Lance máximo: geralmente 50-100% da carta de crédito
  - Taxa sobre lance: 0% a 1.5% (depende da administradora)
- Sorteios mensais (distribuição aleatória)
- Contemplação por lance (melhor lance ganha)
- Cronograma de pagamento:
  - Parcela fixa = (Valor carta + Taxa adm total + Fundo reserva) / Prazo
  - Se contemplado antes do prazo: para de pagar após contemplação
  - Se não contemplado: continua até o fim

**Cenários a simular:**
1. Contemplado no primeiro mês (melhor caso)
2. Contemplado no meio do prazo (caso médio)
3. Contemplado no último mês (pior caso)
4. Probabilidade de contemplação (distribuição estatística)

### 2. Guardar Dinheiro (Prioridade Alta)
**Tipos de Investimento:**
- **Poupança**: Taxa SELIC (atual ~10.5% a.a.) ou 0.5% + TR
- **CDB**: 90-130% do CDI (CDI ~10% a.a.)
- **Tesouro IPCA+**: IPCA + taxa fixa (ex: IPCA + 5%)
- **LCI/LCA**: 85-95% do CDI (isento de IR)

**Variáveis:**
- Valor inicial
- Aportes mensais
- Aporte 13º
- Imposto de Renda (tabela regressiva: 22.5% até 180 dias, reduz até 15% após 720 dias)
- IOF (primeiros 30 dias)

**Cálculo:**
- Simulação mês a mês
- Rendimento composto
- Desconto de IR/IOF
- Comparação com valorização do imóvel

### 3. Fluxo Wizard (Prioridade Média)
- Multi-step form usando Django Sessions
- Progress bar visual
- Navegação voltar/avançar
- Validação por etapa
- Salvar progresso (para usuários logados)

### 4. Interface e UX (Prioridade Média)
- Design responsivo (mobile-first)
- Gráficos comparativos (Chart.js ou similar)
- Tabelas interativas
- Exportação de resultados (PDF/Excel)
- Compartilhamento

### 5. Sistema de Persistência (Prioridade Baixa)
- Salvar simulações (usuários logados)
- Histórico de comparações
- Favoritos
- Compartilhamento com link único

## 📊 Estrutura de Dados

### Modelos Novos Necessários:
- `WizardSession`: Armazena dados temporários do wizard
- `SimulacaoCompleta`: Salva simulações finais
- `Comparacao`: Salva comparações entre métodos
- `PerfilUsuario`: Dados do perfil (tipo: comprador/corretor/etc)

## 🎨 Próximos Passos Imediatos

1. ✅ Criar estrutura base do Wizard
2. ⏳ Melhorar cálculo de Consórcio
3. ⏳ Melhorar simulação Guardar Dinheiro
4. ⏳ Criar templates do Wizard
5. ⏳ Implementar comparação visual
