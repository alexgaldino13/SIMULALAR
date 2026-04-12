# 📱 ImobCalc Mobile - Arquitetura do Sistema (Fase 7)

## 🎯 Visão Geral
O aplicativo mobile será uma extensão da plataforma ImobCalc, focada na experiência do usuário em dispositivos Android, utilizando **React Native**. O objetivo é oferecer a mesma precisão de cálculos do backend Django com uma interface nativa e fluida.

## 🏗️ Stack Tecnológica
- **Framework:** React Native (Expo Managed Workflow)
- **Linguagem:** TypeScript
- **Gerenciamento de Estado:** Context API ou Redux Toolkit
- **Navegação:** React Navigation (Stack e Tab)
- **Requisições API:** Axios
- **Formatação:** `react-native-masked-text` (Equivalente ao Cleave.js)
- **Gráficos:** React Native SVG Charts

## 🔗 Integração com Backend
O app consumirá os endpoints REST já existentes no Django:
1. **Auth:** `/accounts/login/`, `/accounts/signup/`
2. **Simulações:** `/api/simulacoes/` (Listagem e Salvamento)
3. **Monetização:** `/api/assinaturas/status/`, `/api/monetizacao/ad-view/`
4. **Afiliados:** `/api/afiliados/`

## 📂 Estrutura de Pastas Sugerida
```
mobile/
├── src/
│   ├── api/             # Configurações do Axios e endpoints
│   ├── assets/          # Imagens, ícones e fontes
│   ├── components/      # Componentes reutilizáveis (Botões, Inputs, Cards)
│   ├── contexts/        # AuthContext, SimulationContext
│   ├── hooks/           # Custom hooks (useAuth, useSimulation)
│   ├── navigation/      # Configuração das rotas
│   ├── screens/         # Telas (Home, Login, Wizard, Results)
│   │   └── Wizard/      # Steps do Wizard mobile
│   ├── theme/           # Cores (Gradient Roxo), espaçamentos
│   └── utils/           # Formatadores e validadores
├── App.tsx              # Ponto de entrada
└── package.json
```

## 🚀 Fluxo do Wizard Mobile
Diferente da web, o mobile usará um fluxo de `Steps` com transições laterais:
- **Step 1:** Perfil e Objetivos (Cards selecionáveis com animação)
- **Step 2:** Dados Financeiros (Inputs com máscaras monetárias)
- **Step 3:** Imóvel e Prazo
- **Step 4:** Seleção de Cenários
- **Resultado:** Dashboard comparativo com possibilidade de exportação

## 💰 Monetização Mobile
- **AdMob:** Integração via `react-native-google-mobile-ads`.
- **Assinaturas:** Google Play Billing via `react-native-iap`.

## 📅 Próximos Passos
1. Inicializar projeto Expo com TypeScript.
2. Configurar Axios com a URL base do servidor Django.
3. Implementar tela de Login e integração com Auth.