# Aprendizados do Squad Studio Visual

## Sessão: Overhaul do Dashboard (16/04/2026)

### Descobertas Técnicas
- A biblioteca `react-native-chart-kit` exige `react-native-svg` (já instalado).
- `expo-linear-gradient` foi essencial para atingir o nível de profundidade visual desejado pelo Leo.
- O uso de `rgba` em backgrounds é superior ao `opacity` do componente, pois não afeta a opacidade do texto interno (essencial para Glassmorphism).

### Padrão de Design
- Definido o "Royal Global Style" para a LALA MIX: 
  - Gradientes: `#6a11cb` -> `#2575fc`.
  - Cards: `rgba(255, 255, 255, 0.05)` com borda fina de `0.1`.

### Próximos Passos
- Implementar agregação real de dados financeiros no backend para substituir os mocks do Dashboard.
- Criar animações de entrada usando `react-native-reanimated`.
