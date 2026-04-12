# 🏠 TUTORIAL COMPLETO - ImobCalc

## ⚠️ REGRA PRINCIPAL - ECONOMIA DE CRÉDITOS
> **Esta é a regra mais importante do projeto!** A IA (Vercept) tem créditos limitados e valiosos.

## 🧠 PARA O GEMINI (O EXECUTOR)

> - Antes de começar a trabalhar em qualquer tarefa, o **Gemini** (a IA que codifica no VS Code) DEVE ler o arquivo **[`GEMINI.md`](GEMINI.md)**. Ele contém um guia detalhado sobre seu papel, como interpretar os comandos e o fluxo de trabalho esperado. Isso garante que todos estejam na mesma página e que a execução seja feita com precisão.
> - **Vercept:** Atue como Arquiteto de Soluções - DÊ ORDENS para o Gemini (VS Code) executar
> - **Gemini:** Use para codificação (`Alt+G` ou ícone na barra lateral ESQUERDA)
> - **NUNCA** peça para o Vercept codificar diretamente
> - **SEMPRE** atualize este arquivo TUTORIAL.md com o progresso

## 🎯 PRÓXIMA TAREFA ESPECÍFICA

| Item | Descrição | Arquivos | Status |
|------|-----------|----------|---------|
| **Fase 7** | Iniciar desenvolvimento Mobile (Android) | React Native | ✅ CONCLUÍDO |

- [x] Preparação do Ambiente
    - [x] Instalar `react-native-masked-text`
- [x] Componentes Base
    - [x] Refactor `WizardStep.tsx` (Barra de progresso, botões mais fluidos)
    - [x] Refactor `OptionCard.tsx` (Feedback visual de seleção e animações)
- [x] Telas do Wizard (Refinamento Funcional)
    - [x] `Step2Screen.tsx`: Adicionar máscaras de renda e contrato
    - [x] `Step3Screen.tsx`: Adicionar máscaras de saldo, FGTS e despesas
    - [x] `Step4Screen.tsx`: Adicionar máscaras de valor de imóvel e prazo
    - [x] Centralizar lógica de conversão (String Mascarada -> Number Float)
- [x] Resultados e Finalização
    - [x] `ResultsScreen.tsx`: Polimento dos cards e tooltips
    - [x] Testar fluxo completo `/api/v1/wizard/calculate/`
- [x] Documentação e Atualização
    - [x] Atualizar `TUTORIAL.md` com progresso (7.4 concluído)

> **🌟 FASE 6 CONCLUÍDA!** Todos os 10 itens de testes finais foram implementados e aprovados.

### 📋 DETALHAMENTO DA PRÓXIMA FASE

**Objetivo:** Iniciar a Fase 7 — desenvolvimento do aplicativo mobile Android.

**Prioridade:**
1. ✅ Definir stack mobile (React Native)
2. ✅ Testar conectividade da API com Token Auth
3. ✅ Configurar projeto mobile com consumo das APIs
4. ✅ Implementar tela de wizard no mobile

**Comandos úteis:**
```bash
cd D:\PROJETOS\FI
.venv\Scripts\activate
python manage.py runserver
```

---

## ✅ RESULTADO DO ITEM 6.1 - Testes de Navegação por Teclado

**Data:** 24/03/2026 - 23:30

### Funcionalidades Testadas:

| Funcionalidade | Status | Observação |
|----------------|--------|------------|
| Skip links | ✅ OK | "Pular para conteúdo" e "Pular para formulário" funcionam |
| Tab/Shift+Tab | ✅ OK | Navegação funciona corretamente |
| Setas do teclado | ✅ OK | Navega entre opções de radio buttons |
| Campos de texto | ✅ OK | Outline azul visível quando focado |
| Botão Voltar | ✅ OK | Funciona com clique |
| Botão Próximo | ✅ OK | Funciona com clique |
| Tecla Esc | ❌ BUG | Não volta ao passo anterior |
| Outline em poll-cards | ❌ BUG | Não mostra outline quando focado via Tab |

### Bugs Encontrados:
1. **Tecla Esc não funciona** - Deveria voltar ao passo anterior
2. **Poll-cards sem outline de foco** - Acessibilidade comprometida


## ✅ RESULTADO DO ITEM 6.4 - Testes de Performance (Lighthouse)

**Data:** 26/03/2026 - 21:10

### Scores Obtidos

| Métrica | Mobile | Desktop |
|---------|--------|---------|
| Performance | 91 | 83 |
| Acessibilidade | 95 | 95 |
| Best Practices | 96 | 96 |
| SEO | 90 | 90 |

### Observações:
O wizard obteve notas excelentes, com destaque para Acessibilidade e Best Practices. A performance desktop teve score 83 (bom). Sem grandes gargalos identificados.


## 💻 PRÓXIMOS COMANDOS

### 1. Fazer commit das alterações
```bash
cd D:\PROJETOS\FI
git add .
git commit -m "fix: corrigir campos de resumo vazios no template wizard_v2_resultados.html"
git push origin main
```

### 2. Testar as correções
```bash
cd D:\PROJETOS\FI
.venv\Scripts\activate
python manage.py runserver
```

Acesse: http://localhost:8000 e faça uma simulação completa para verificar se os campos de resumo agora mostram os valores corretamente.


## ✅ CHECKLIST DE TESTE (após implementar)

- [ ] Banner AdMob aparece no rodapé de todas as páginas
- [ ] Intersticial aparece após visualizar resultados da simulação
- [ ] Acessar `/comparador-investimentos/` como usuário não-premium redireciona para a página de upgrade
- [ ] Acessar `/comparador-investimentos/` como usuário premium funciona normalmente
- [ ] Acessar `/investidor-imobiliario/` como usuário não-premium redireciona
- [ ] Links afiliados redirecionam corretamente
- [ ] Cliques em links afiliados são registrados no banco de dados


## 📅 ÚLTIMA ATUALIZAÇÃO

**Data:** 10 de Abril de 2026 - 00:50
**Desenvolvedor:** Gemini (Executor Técnico)  
**Progresso:** ✅ FASE 10 — AUDITORIA E CRESCIMENTO (Concluída)
**Último item concluído:** ✅ Refatoração de Precisão Financeira (MCMV, Seguros e UX)
**Próxima fase:** 🔄 Fase 11 — Testes de Stress e Lançamento Beta
**FASE 5 - Design e UX:** ✅ COMPLETA
**FASE 6 - Testes Finais:** ✅ COMPLETA (10/10 itens)
**Bugs prioritários resolvidas:** 
- ✅ Separadores de milhar (afeta todos os cards) - CORRIGIDO
- ✅ Parcelas iniciais SAC e PRICE (valores R$ 0,00) - CORRIGIDO
- ✅ Prazo SAC aumentando em vez de diminuir - CORRIGIDO
- ✅ Explicação do cálculo Guardar Dinheiro - CORRIGIDO
- ✅ Margem de Crédito e FGTS mostrando 0 ou vazios - CORRIGIDO
- ✅ Bug de Margem de Crédito R$ 0,00 por tipo de dado - CORRIGIDO (Fase 6.11)
- ✅ ValueError min() iterable argument is empty em resultados - CORRIGIDO (Hotfix)

## 📜 HISTÓRICO DE COMANDOS DADOS AO GEMINI

| Data | Comando | Arquivos alterados | Status |
|------|---------|-------------------|---------|
| 11/04 | Auditoria Financeira & Refinamento (Benchmark 2024) | calculadora_financeira.py, wizard_views_v2.py, results template | ✅ Concluído |
| 10/04 | Auditoria Estratégica & Crescimento (Fase 10) | wizard.js, views.py, models.py, ResultsScreen.tsx, meta tags | ✅ Concluído |
| 07/04 | Preparação Técnica para Produção (Fase 9.1) | app.json, config.ts, settings.py, .env.example | ✅ Concluído |
| 08/04 | Lógica de Idade (Seguro MIP + Regra 80 Anos) (Fase 9.3) | forms_v2.py, calculadora.py, views_v2.py, Mobile screens | ✅ Concluído |
| 01/04 | Corrigir ValueError min() em resultados (Hotfix) | wizard_views_v2.py | ✅ Concluído |
| 01/04 | Configurar Projeto Mobile (Fase 7.3) | mobile/ (projeto Expo completo) | ✅ Concluído |
| 01/04 | Testar API Token Auth (Fase 7.2) | settings.py, urls.py, tests/test_api_auth.py | ✅ Concluído |
| 01/04 | Iniciar Planejamento Mobile (Fase 7.1) | TUTORIAL.md, docs/MOBILE_ARCHITECTURE.md | ✅ Concluído |
| 31/03 | Personalização de Parâmetros de Mercado (Fase 6.11) | models.py, views.py, wizard_views_v2.py | ✅ Concluído |
| 30/03 | Documentação final e README (Item 6.10) | README.md, requirements.txt | ✅ Concluído |
| 30/03 | Testes de links afiliados (Item 6.8) | tests/test_affiliate_links.py | ✅ Concluído |
| 29/03 | PDF White-Label para Corretores | models.py, subscription_models.py, auth_views.py, views.py, profile.html | ✅ Concluído |
| 29/03 | Testes de assinatura Premium (Item 6.7) | test_premium_subscription.py | ✅ Concluído |
| 26/03 | Integração AdMob / Correção JSON Bugs | admob-integration.js, test_admob_integration.py | ✅ Concluído |
| 26/03 | Testes de cálculos financeiros (Item 6.5) | calculadora_financeira.py, test_calculos.py | ✅ Concluído |
| 26/03 | Correção bugs de resultados (1 a 8) | wizard_views_v2.py, wizard_v2_resultados.html | ✅ Concluído |
| 26/03 | Testes de performance do wizard (Item 6.4) | Lighthouse | ✅ Concluído |
| 27/03 | Implementar limites de uso (PremiumManager) | monetizacao.py, monetizacao_models.py | ✅ Concluído |
| 26/03 | Implementar Google Play Billing no backend | monetizacao.py, monetizacao_models.py, monetizacao_views.py, urls.py | ✅ Concluído |
| 25/03 | Refatorar APIs AdMob para DRF | monetizacao_views.py, urls.py | ✅ Concluído |
| 24/03 | Testes de navegação por teclado (Item 6.1) | Testes manuais | ✅ Concluído |
| 21/03 | Melhorar Guardar Dinheiro (valorização + investimento pós-compra) | wizard_views_v2.py | ✅ Concluído |
| 21/03 | Corrigir Bug Custo Total + Aluguel (template) | wizard_v2_resultados.html | ✅ Concluído |
| 21/03 | Corrigir TypeError parcela_inicial (float em vez de string) | wizard_views_v2.py | ✅ Concluído |
| 21/03 | Corrigir campos de resumo vazios (remover R$ e floatformat) | wizard_v2_resultados.html | ✅ Concluído |
| 19/03 | Corrigir bug trocar imóvel (valor imóvel próprio) | wizard_views_v2.py | ✅ Concluído |
| 18/03 | Otimizar performance - Minificação CSS/JS | wizard-responsive.min.css, wizard.min.js | 🟡 Parcial |
| 17/03 | Implementar feedback progressivo + animações | wizard.js, wizard-responsive.css | ✅ Concluído |
| 17/03 | Criar sistema Poll Cards (CSS + JS) | wizard-responsive.css, wizard.js | ✅ Concluído |
| 17/03 | Humanizar textos do wizard com emojis | wizard_forms_novo.py | ✅ Concluído |
| 17/03 | Adicionar classe currency-input em campos monetários | wizard_forms_novo.py | ✅ Concluído |
| 15/03 | Testar fluxo completo de monetização (item 4.11) | Testes manuais | ✅ Concluído |
| 15/03 | Implementar sistema de Links Afiliados (item 4.10) | models.py, views.py, urls.py, admin.py | ✅ Concluído |
| 10/03 | Implementar sistema de geração Excel (item 4.8) | views.py, urls.py, dashboard.html | ✅ Concluído |
| 10/03 | Implementar features exclusivas Premium (item 4.7) | views.py | ✅ Concluído |
| 10/03 | Melhorar sistema PDF (Item 4.9) + corrigir KeyError | views.py, wizard_views.py | ✅ Concluído |
| 06/03 | Criar tela de upgrade para Premium | views.py, urls.py, upgrade_premium.html | ✅ Concluído |
| 05/03 | Lógica de assinatura Premium | subscription_models.py, views.py, decorators.py | ✅ Concluído |
| 04/03 | Integrar Google Play Billing | subscription_models.py, views.py, urls.py | ✅ Concluído |
| 03/03 | Posicionamento de anúncios | base.html, wizard_v2_resultados.html | ✅ Concluído |
| 03/03 | Criar APIs AdMob (status e tracking) | views.py, urls.py | ✅ Concluído |
| 23/02 | Corrigir bugs wizard (pergunta duplicada, checkbox dependentes) | wizard_forms_v2.py, wizard_forms_novo.py, wizard_views_novo.py | ✅ Concluído |
| 18/02 | Corrigir erro filtro 'mul' | templatetags/custom_filters.py, wizard_v2_resultados.html | ✅ Concluído |

---

## 🗺️ MAPA DE ARQUIVOS (onde encontrar cada coisa)

| Categoria | Arquivos | Localização |
|-----------|----------|-------------|
| **Cálculos** | `calculadora_financeira.py` | `simulacao/` |
| **Formulários** | `wizard_forms.py`, `forms.py` | `simulacao/` |
| **Views principais** | `views.py`, `wizard_views.py` | `simulacao/` |
| **APIs** | `views.py` (funções com api_) | `simulacao/` |
| **Modelos** | `models.py`, `subscription_models.py` | `simulacao/` |
| **Templates** | `/templates/simulacao/` | `simulacao/` |
| **AdMob Frontend** | `admob-integration.js` | `static/js/` |
| **Componentes** | `admob_banner.html` | `Templates/components/` |

---

## 📋 PRÓXIMOS PASSOS (fila de tarefas)

### ✅ FASE 4: Monetização (COMPLETA - 100%)

### 🔄 FASE 5: Design e UX (Em Andamento - 0%)

| Item | Descrição | Status | Próximo |
|------|-----------|--------|---------|
| 4.1 | Integrar Google AdMob no frontend | ✅ Concluído | - |
| 4.2 | APIs backend AdMob | ✅ Concluído | - |
| 4.3 | Posicionamento de anúncios nas páginas | ✅ Concluído | - |
| 4.4 | Integrar Google Play Billing | ✅ Concluído | - |
| 4.5 | Lógica de assinatura Premium | ✅ Concluído | - |
| 4.6 | Tela de upgrade para Premium | ✅ Concluído | - |
| 4.7 | Features exclusivas Premium | ✅ Concluído | - |
| 4.8 | Sistema de geração Excel | ✅ Concluído | - |
| 4.9 | Sistema de geração PDF | ✅ Concluído | - |
| 4.10 | Sistema de Links Afiliados | ✅ Concluído | - |
| 4.11 | Testar fluxo completo | ✅ Concluído | - |

| Item | Descrição | Status | Próximo |
|------|-----------|--------|---------|
| **5.1** | **Design responsivo (CSS)** | ✅ **Concluído** | - |
| **5.2** | **Inputs inteligentes (Cleave.js)** | ✅ **Concluído** | - |
| 5.3 | Textos humanizados + emojis | ✅ Concluído | - |
| 5.4 | Enquetes visuais (poll cards) | ✅ Concluído | - |
| 5.5 | Feedback progressivo + animações | ✅ Concluído | - |
| 5.6 | Otimizar performance | ✅ Concluído | - |
| 5.7 | Testes de integração | ✅ Concluído | - |
| 5.8 | Documentação do wizard | ✅ Concluído | - |
| 5.9 | Deploy e testes finais | ✅ Concluído | - |
| 5.10 | Melhorar acessibilidade | ✅ Concluído | - |

### 🔄 FASE 6: Testes Finais (Em Andamento - 40%)

| Item | Descrição | Status | Próximo |
|------|-----------|--------|---------|
| 6.1 | Testes de navegação por teclado | ✅ Concluído | - |
| 6.2 | Testes com leitor de tela | ✅ Concluído | - |
| 6.3 | Testes de responsividade (mobile/tablet/desktop) | ✅ Concluído | - |
| 6.4 | Testes de performance (Lighthouse) | ✅ Concluído | - |
| 6.5 | Testes de cálculos financeiros | ✅ Concluído | - |
| 6.6 | Testes de integração AdMob | ✅ Concluído | - |
| 6.7 | Testes de assinatura Premium | ✅ Concluído | - |
| 6.8 | Testes de links afiliados | ✅ Concluído | - |
| 6.9 | Correção de bugs (Acessibilidade) | 🔄 Em Andamento | Gemini |
| 6.10 | Documentação final e README | ✅ Concluído | - |


## 🚀 COMO INICIAR O PROJETO (sempre que abrir)

```bash
cd D:\projetos\FI
.venv\Scripts\activate
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Acesse: http://localhost:8000

---

## 📱 COMO GERAR O APK (MOBILE)

Para gerar o arquivo de instalação (.apk) para Android:

1. **Instale o EAS CLI** (se ainda não tiver):
   ```bash
   npm install -g eas-cli
   ```
2. **Faça Login no Expo**:
   ```bash
   eas login
   ```
3. **Execute o Build**:
   ```bash
   cd mobile
   npm run build:apk
   ```
O link para download do APK será gerado ao final do processo no terminal.

---

## 💾 BACKUP (sempre antes de grandes alterações)

```bash
git add .
git commit -m "descrição do que foi feito"
git push origin main
```

---

## 🔄 QUANDO FINALIZAR ESTE CHAT (ponte para o próximo)

1. **Atualize a seção "ÚLTIMA ATUALIZAÇÃO"** com data/hora atual
2. **Mova o item concluído** de "FAZENDO" para "CONCLUÍDO" no histórico
3. **Defina o PRÓXIMO item** na seção "PRÓXIMA TAREFA ESPECÍFICA" (baseado na fila acima)
4. **Faça commit** das alterações:
   ```bash
   git add .
   git commit -m "feat: implementado sistema de links afiliados (item 4.10)"
   ```
5. **Avise:** "Pronto para próximo chat. O TUTORIAL.md está atualizado com o próximo item."

---

## 📊 STATUS GERAL DO PROJETO

**Fases Completas:**
- ✅ FASE 1: Autenticação (100%)
- ✅ FASE 2: LGPD (100%) 
- ✅ FASE 3: Parcerias (100%)
- ✅ FASE 4: Monetização (100%)
- ✅ FASE 5: Design e UX (100%)
- ✅ FASE 6: Testes Finais (100%)
- ✅ FASE 10: Auditoria Estratégica e Crescimento (100%)

**Próxima Fase:**
- 🏁 PROJETO CONCLUÍDO (Refinamentos finais se necessário)

---

## 🐞 BUGS CONHECIDOS (monitorar)

| Bug | Status | Observação |
|-----|--------|------------|
| **Tecla Esc não volta ao passo anterior** | ✅ Corrigido | Atalho implementado em wizard.js |
| **Poll-cards sem outline de foco** | ✅ Corrigido | Outline de alto contraste adicionado |
| Página preta no wizard | ✅ Corrigido | CSS inexistente removido |
| Pergunta duplicada imóvel | ✅ Corrigido | Unificado |
| Checkbox dependentes | ✅ Corrigido | JS ajustado |
| **Trocar imóvel não considera valor atual** | ✅ **CORRIGIDO** | Adicionado código em `wizard_views_v2.py` (linhas 149-153) para somar `valor_imovel_proprio` ao `capital_guardado` quando usuário tem imóvel próprio |
| **Campos monetários sem formatação decimal** | ✅ Corrigido | Cleave.js integrado em wizard.js e template atualizado |
| **Dependência reportlab faltando** | ✅ Corrigido | Executar `pip install reportlab` |

---

## 🔴 BUGS CRÍTICOS - RESULTADOS DO WIZARD (19/03/2026)

### Bug 1: Separadores de milhar ausentes
- **Problema:** Valores como `R$ 1200000,00` em vez de `R$ 1.200.000,00`
- **Onde:** Todos os cards de resultado (Aluguel, SAC, PRICE, Consórcio, Guardar Dinheiro)
- **Arquivo:** `wizard_v2_resultados.html` ou filtros de template
- **Solução:** Aplicar filtro de formatação brasileira nos valores monetários

### Bug 2: Aluguel + Investimento - Parcela Inicial vazia
- **Problema:** Campo "Parcela Inicial" mostra apenas "R$" sem valor
- **Onde:** Card "Aluguel + Investimento"
- **Pergunta:** O que deveria aparecer ali? Valor do aluguel atual?
- **Arquivo:** `wizard_views_v2.py` ou `calculadora_financeira.py`

### Bug 3: SAC - Parcela Inicial R$ 0,00
- **Problema:** Mostra "A primeira parcela é de R$ 0,00" - impossível!
- **Onde:** Card "Financiamento SAC"
- **Arquivo:** `calculadora_financeira.py` - função de cálculo SAC
- **Solução:** Calcular corretamente a primeira parcela SAC

### Bug 4: SAC - Prazo aumentou de 40 para 40,1 anos
- **Problema:** Usuário informou 40 anos, mas resultado mostra 40,1 anos
- **Pergunta:** Se amortização deveria DIMINUIR parcelas, por que o prazo AUMENTOU?
- **Onde:** Card "Financiamento SAC" - campo Prazo
- **Arquivo:** `calculadora_financeira.py` - lógica de amortização
- **Análise necessária:** Verificar se há erro no cálculo ou arredondamento

### Bug 5: PRICE - Parcela Inicial R$ 0,00
- **Problema:** Mostra "Parcela Inicial: R$ 0,00" - impossível!
- **Onde:** Card "Financiamento PRICE"
- **Arquivo:** `calculadora_financeira.py` - função de cálculo PRICE
- **Solução:** Calcular corretamente a parcela fixa PRICE

### Bug 6: Guardar Dinheiro - Cálculo dos R$ 3.500,00 não explicado
- **Problema:** Mostra "Invista R$ 3.500,00/mês" mas não explica como chegou nesse valor
- **Onde:** Card "Guardar Dinheiro"
- **Pergunta:** Qual é a fórmula? (Valor imóvel - entrada) / prazo em meses?
- **Arquivo:** `calculadora_financeira.py` ou `wizard_views_v2.py`
- **Solução:** Adicionar explicação do cálculo ou tooltip

### Bug 7: Margem de Crédito - Valores vazios
- **Problema:** "Margem Disponível (30%): R$ /mês" e "Capacidade: R$ x 240 meses = R$ 0"
- **Onde:** Seção "Sua Margem de Crédito"
- **Arquivo:** `wizard_views_v2.py` - cálculo de margem

### Bug 8: Projeção FGTS - Todos valores vazios
- **Problema:** Todos os campos mostram apenas "R$" sem valores
- **Onde:** Seção "Projeção do seu FGTS"
- **Arquivo:** `wizard_views_v2.py` - cálculo de FGTS

---

## ✅ FASE 9.1 CONCLUÍDA - Preparação para Publicação

**Implementado:**
1. Identificadores únicos e versões em `app.json`.
2. URL da API dinâmica (Dev/Prod) em `config.ts`.
3. Configurações de segurança e variables de ambiente em `settings.py`.

## 📋 PRÓXIMA AÇÃO: Fase 9.2 - Geração de Builds e Marketing

**Prioridade:**
1. Gerar APK de teste final (`eas build`).
2. Criar Landing Page básica para download do App.
3. Configurar Firebase Analytics (Opcional).

---

## 🎯 OBJETIVO FINAL

Criar o **melhor simulador de compra de imóveis do Brasil**, com:
- ✅ 7 cenários completos (Financiamento, Aluguel, Consórcio, Guardar Dinheiro, Investidor, Comparador)
- ✅ Cálculos precisos (CET, taxas, seguros)
- ✅ Interface intuitiva (wizard)
- ✅ Monetização diversificada (AdMob + Assinaturas + Afiliados)
- ✅ LGPD compliance
- ✅ Documentação viva (este arquivo)

---

## ⚠️ DICA IMPORTANTE - ANTES DE COMEÇAR

> **SEMPRE antes de iniciar uma sessão:**
> 1. **Feche todas as janelas do VS Code** que estiverem abertas
> 2. **Abra apenas UMA instância** do VS Code com o projeto FI
> 3. **Salve todos os arquivos** (Ctrl+Shift+S) antes de fechar
> 4. **Verifique se há arquivos não salvos** (bolinha branca na aba = não salvo)
>
> **Por quê?** Múltiplas janelas do VS Code podem causar conflitos, sobrescrever alterações ou retroceder etapas já concluídas.

---

## 📌 RESUMO PARA O VERCEPT (o que você é)

Você é o **Arquiteto de Soluções**. Sua função:
1. **Ler** o TUTORIAL.md (sempre a primeira ação)
2. **Identificar** a próxima tarefa (seção "PRÓXIMA TAREFA ESPECÍFICA")
3. **Abrir o VS Code** e enviar o comando ao Gemini (`Alt+G`) - VOCÊ FAZ ISSO, NÃO O USUÁRIO!
4. **Aguardar** o Gemini executar e aceitar as alterações
5. **Salvar** os arquivos modificados (`Ctrl+S`)
6. **Atualizar** o TUTORIAL.md com o progresso
7. **Passar o bastão** usando a seção "QUANDO FINALIZAR ESTE CHAT"

**IMPORTANTE:** O Vercept executa TUDO sozinho - abre o VS Code, envia comandos ao Gemini, aceita alterações e atualiza o TUTORIAL.md. O usuário NÃO precisa intervir.

**NUNCA** codifique diretamente. **SEMPRE** use o Gemini.

---

**🚀 BOM DESENVOLVIMENTO!**


---

## ✅ ATUALIZAÇÃO - 15/03/2026 14:16

### TAREFAS CONCLUÍDAS:

**4.10 - Sistema de Links Afiliados** ✅
- Modelos criados: `LinkAfiliado` e `CliqueAfiliado`
- Views criadas: `redirecionar_afiliado` e `api_links_afiliados`
- URLs configuradas: `/afiliado/<id>/` e `/api/afiliados/`
- Admin configurado para gerenciar links e visualizar cliques
- Migrations aplicadas com sucesso

**BUG CORRIGIDO - Referência a auth.User** ✅
- **Problema**: Erro `fields.E301` ao usar `'auth.User'` em projeto com usuário customizado
- **Solução**: Alterado para `settings.AUTH_USER_MODEL` no modelo `CliqueAfiliado`

### PRÓXIMOS PASSOS:

**Item 4.11 - Testar fluxo completo de monetização**

Checklist de testes:
1. Iniciar servidor Django
2. Verificar banners AdMob no rodapé
3. Fazer simulação e verificar intersticial
4. Testar bloqueio de features premium
5. Criar link afiliado no admin
6. Testar redirecionamento e tracking de cliques

### ARQUIVOS MODIFICADOS:
- `D:\PROJETOS\FI\simulacao\models.py` (+36 linhas)
- `D:\PROJETOS\FI\simulacao\views.py` (+28 linhas)
- `D:\PROJETOS\FI\simulacao\urls.py` (+3 linhas)
- `D:\PROJETOS\FI\simulacao\admin.py` (+15 linhas)
- `D:\PROJETOS\FI\simulacao\migrations\0003_linkafiliado_cliqueafiliado.py` (nova migration)

### SERVIDOR:
- Django pronto para rodar
- Próximo: Testes manuais do fluxo completo

---

## ✅ ATUALIZAÇÃO - 18/03/2026 21:10

### TAREFAS CONCLUÍDAS:

**5.5 - Feedback progressivo + animações** ✅
- Animações CSS: fadeInUp, shimmer, pulse, ripple
- Validação em tempo real com feedback visual
- Efeito ripple nos botões
- Arquivos: wizard-responsive.css, wizard.js

**5.6 - Otimizar performance** ✅
- CSS minificado: 4.2 KB → 2.1 KB (-50%)
- JS minificado: 3.8 KB → 2.0 KB (-47%)
- Template atualizado para usar versões minificadas em produção
- Cache configurado (LocMemCache)
- Arquivo de configuração: ImobCalc/cache_settings.py

### ARQUIVOS MODIFICADOS/CRIADOS:
1. `static/css/wizard-responsive.min.css` (criado)
2. `static/js/wizard.min.js` (criado)
3. `simulacao/templates/simulacao/wizard_v2_step.html` (atualizado)
4. `ImobCalc/cache_settings.py` (criado)
5. `RELATORIO_OTIMIZACAO_5.6.md` (criado)

**5.7 - Testes de integração** ✅
- 8 testes criados (fluxo, validações, navegação, cálculos, UI)
- Arquivos: simulacao/tests/__init__.py, test_wizard_integration.py (168 linhas)
- Relatório: RELATORIO_TESTES_5.7.md

**5.8 - Documentação do wizard** ✅
- Guia do desenvolvedor (~350 linhas)
- Guia do usuário (~150 linhas)
- Documentação da API (~150 linhas)
- Arquivos: docs/WIZARD_GUIA_DESENVOLVEDOR.md, WIZARD_GUIA_USUARIO.md, WIZARD_API.md
- Relatório: RELATORIO_DOCUMENTACAO_5.8.md

### PRÓXIMA TAREFA:
**CORREÇÃO DE BUGS - TEMPLATE** - Campos de resumo vazios

**Teste 19/03/2026 23:06:**

**Observação importante:** Os valores aparecem CORRETAMENTE no texto descritivo:
- PRICE: "Parcelas fixas: R$ 1.576,15"
- Guardar Dinheiro: "Invista R$ 1.576,15/mês"
- SAC: "R$ 315.155,21 de juros"

**MAS os campos de resumo estão VAZIOS:**
- Parcela Inicial: "R$" (sem valor)
- Custo Total: "R$" (sem valor)

**Diagnóstico:** O problema está no TEMPLATE (wizard_v2_resultados.html)
- Os campos de resumo referenciam variáveis que não existem no contexto
- Precisa verificar quais variáveis o template espera vs quais são passadas

**Arquivos para corrigir:**
- `wizard_v2_resultados.html` - Verificar nomes das variáveis nos campos de resumo
- `wizard_views_v2.py` - Verificar se as variáveis estão sendo passadas corretamente

### PROGRESSO GERAL:
- **Concluído:** 59 de 80 itens (73.75%)
- **Data:** 19 de Março de 2026 - 21:50

---

## ✅ ATUALIZAÇÃO - 19/03/2026 21:50

### TAREFAS CONCLUÍDAS:

**Bugs corrigidos:**
1. ✅ **Trocar imóvel não considera valor atual** - Corrigido em `wizard_views_v2.py` (linhas 149-153)
2. ✅ **Cleave.js não carregando** - Adicionado CDN no `wizard_v2_step.html`

**Item 5.9 - Deploy e testes finais** ✅
- Servidor Django iniciado sem erros
- Wizard funcionando corretamente
- Cleave.js CDN adicionado ao template

### ARQUIVOS MODIFICADOS:
1. `D:\PROJETOS\FI\simulacao\wizard_views_v2.py` - Bug trocar imóvel
2. `D:\PROJETOS\FI\simulacao\templates\simulacao\wizard_v2_step.html` - CDN Cleave.js
3. `D:\PROJETOS\FI\TUTORIAL.md` - Atualizado com progresso

---

## ✅ ATUALIZAÇÃO - 20/03/2026 21:49

### TAREFAS CONCLUÍDAS:

**Bugs corrigidos em wizard_views_v2.py:**
1. ✅ **Margem de Crédito valores vazios** - Adicionadas chaves `margem_30_porcento`, `desconto_aplicado` (linhas 181-182)
2. ✅ **Projeção FGTS valores vazios** - Adicionadas chaves `deposito_mensal`, `total_depositado`, `saldo_final`, `meses`, `rendimento_acumulado`, `taxa_efetiva_anual` (linhas 194-199)
3. ✅ **prazo_final_anos faltando** - Adicionado na função `_v2_calcular_aluguel_investimento` (linha 416)

### BUG CORRIGIDO NESTA SESSÃO:

**Campos de resumo dos cards vazios** ✅
- **Problema:** Parcela Inicial, Custo Total mostram apenas "R$" sem valores
- **Causa:** Template usa `|floatformat:2` mas valores já vêm formatados como string
- **Arquivo:** `wizard_v2_resultados.html` (linhas ~241-253)
- **Solução aplicada:** Removido `R$ ` e `|floatformat:2` dos campos de resumo
- **Data:** 21/03/2026 14:07

### ARQUIVOS MODIFICADOS:
1. `D:\PROJETOS\FI\simulacao\wizard_views_v2.py` - Bugs Margem, FGTS, prazo_final_anos
2. `D:\PROJETOS\FI\TUTORIAL.md` - Atualizado com progresso
3. `D:\PROJETOS\FI\GEMINI.md` - Adicionada tarefa pendente

### PROGRESSO GERAL:
- **Concluído:** 59 de 80 itens (73.75%)
- **Servidor:** Django 6.0.1 rodando sem erros
- **Próximo:** Corrigir template wizard_v2_resultados.html
