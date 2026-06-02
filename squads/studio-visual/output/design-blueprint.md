# Blueprint de Design: Dashboard Premium SIMULALAR

**Designer:** Leo Visual
**Data:** 16 de Abril, 2026

## Visão Geral
O objetivo é transformar o Dashboard em uma central de comando financeira. Saímos de uma lista simples para uma interface baseada em "Widgets" informativos e cartões de impacto.

## Elementos Visuais
1. **Fundo:** Manter `#0f0c29` (Deep Midnight Blue) com sutis gradientes radiais em `rgba(106, 17, 203, 0.1)`.
2. **Cards (Glassmorphism):** 
   - `backgroundColor: 'rgba(255, 255, 255, 0.05)'`
   - `borderRadius: 24`
   - `borderWidth: 1`
   - `borderColor: 'rgba(255, 255, 255, 0.1)'`
3. **Tipografia:** 
   - Headlines: Inter ExtraBold.
   - Stats: Monospaced para números de valores financeiros.

## Layout da Tela
### 1. Header Dinâmico
- Avatar do usuário com anel de progresso da conta (Free vs Premium).
- Saudação contextual (Bom dia/Boa tarde).

### 2. Widget de "Poder de Compra" (NOVO)
- Um card grande em destaque mostrando o "Valor Máximo Recomendado" baseado na renda familiar informada na última simulação.
- Barra de progresso visual.

### 3. Estatísticas com Gráfico
- Uso do `react-native-chart-kit` para um gráfico de linha mostrando a "Economia em Juros" somada de todos os cenários salvos.
- Este card deve ter um brilho dourado se o usuário for Premium.

### 4. Simulações Recentes (Cards Horizontais)
- Em vez de uma lista vertical infinita, os 3 itens mais recentes em um carrossel horizontal ou cards compactos com badge do tipo (SAC/PRICE/Consórcio).

## Prompt para o Google Stitch
> "Create a high-end financial dashboard UI for a mobile app. Background: deep navy blue. Primary elements using glassmorphism (frosted glass) with subtle white borders. Include a prominent numeric display for 'Total Savings', a small line chart showing financial trends, and horizontal rectangular cards for recent activities. Use gold accents for premium features. Modern, clean typography (Inter). Style: Apple-esque minimalist but with vibrant gradients."

## Instruções para Bia Frontend
- Use `LinearGradient` da biblioteca `expo-linear-gradient`.
- Implementar o componente `SimulationItem` com `pressable` e feedback tátil.
- Integrar com `useSimulation` para dados em tempo real se necessário.
