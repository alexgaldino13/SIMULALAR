# 🏠 TUTORIAL COMPLETO - ImobCalc

## ⚠️ REGRA PRINCIPAL - ECONOMIA DE CRÉDITOS
> **Esta é a regra mais importante do projeto!** A IA (Vercept) tem créditos limitados e valiosos.
> - **Vercept:** Atue como Arquiteto de Soluções - DÊ ORDENS para o Gemini (VS Code) executar
> - **Gemini:** Use para codificação (`Alt+G` ou ícone na barra lateral ESQUERDA)
> - **NUNCA** peça para o Vercept codificar diretamente
> - **SEMPRE** atualize este arquivo TUTORIAL.md com o progresso

## 🎯 PRÓXIMA TAREFA ESPECÍFICA

| Item | Descrição | Arquivos | Status |
|------|-----------|----------|--------|
| **5.1** | Melhorar design responsivo | `templates/`, `static/css/` | ⏳ PENDENTE |

### 📋 DETALHAMENTO DA TAREFA

**Objetivo:** Melhorar o design responsivo do sistema para mobile e tablet.

**Tarefas:**
1. Auditar todas as páginas em diferentes resoluções
2. Ajustar CSS para breakpoints mobile/tablet
3. Testar formulários em telas pequenas
4. Otimizar imagens e ícones
5. Melhorar navegação mobile

**Arquivos que serão modificados:**
1. `static/css/style.css` - Adicionar media queries
2. `Templates/base.html` - Ajustar estrutura responsiva
3. `simulacao/templates/` - Ajustar templates do wizard
- [ ] Links afiliados redirecionam corretamente
- [ ] Cliques são registrados no admin


## 🤖 COMANDO PRONTO PARA O GEMINI (copiar e colar)

Quando abrir o Gemini no VS Code (`Alt+G`), cole EXATAMENTE isto:

```
TAREFA: TESTE MANUAL DO FLUXO DE MONETIZAÇÃO

Não há código para implementar nesta etapa. 
Esta é uma tarefa de TESTE MANUAL que o desenvolvedor deve realizar:

1. Iniciar o servidor Django
2. Acessar http://127.0.0.1:8000/
3. Fazer uma simulação completa
4. Verificar se os banners AdMob aparecem
5. Verificar se o intersticial aparece após os resultados
6. Tentar acessar features premium sem estar logado
7. Criar um link afiliado no admin e testar o redirecionamento
8. Verificar no admin se os cliques foram registrados

Após os testes, atualizar o TUTORIAL.md com os resultados.
```


## ✅ CHECKLIST DE TESTE (após implementar)

- [ ] Banner AdMob aparece no rodapé de todas as páginas
- [ ] Intersticial aparece após visualizar resultados da simulação
- [ ] Acessar `/comparador-investimentos/` como usuário não-premium redireciona para a página de upgrade
- [ ] Acessar `/comparador-investimentos/` como usuário premium funciona normalmente
- [ ] Acessar `/investidor-imobiliario/` como usuário não-premium redireciona
- [ ] Links afiliados redirecionam corretamente
- [ ] Cliques em links afiliados são registrados no banco de dados


## 📅 ÚLTIMA ATUALIZAÇÃO

**Data:** 15 de Março de 2026 - 19:45
**Desenvolvedor:** Galdino  
**Progresso:** 61% (49 de 80 itens)
**Último item concluído:** ✅ Item 4.11 - Testes completos de monetização
**Próximo item:** ⬜ Item 5.1 - Melhorar design responsivo

## 📜 HISTÓRICO DE COMANDOS DADOS AO GEMINI

| Data | Comando | Arquivos alterados | Status |
|------|---------|-------------------|--------|
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
| **5.1** | **Melhorar design responsivo** | ⏳ **Pendente** | ➡️ |
| 5.2 | Otimizar performance | ⏳ Pendente | |
| 5.3 | Melhorar acessibilidade | ⏳ Pendente | |
| 5.4 | Adicionar animações | ⏳ Pendente | |
| 5.5 | Melhorar UX do wizard | ⏳ Pendente | |


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

**Fase em Andamento:**
- 🔄 FASE 5: Design e UX (0% - 0/10 itens)

**Fases Futuras:**
- ⏳ FASE 5: Design e UX (0%)
- ⏳ FASE 6: Testes Finais (0%)
- ⏳ FASE 7: Mobile (0%)
- ⏳ FASE 8: Publicação (0%)

---

## 🐞 BUGS CONHECIDOS (monitorar)

| Bug | Status | Observação |
|-----|--------|------------|
| Página preta no wizard | ✅ Corrigido | CSS inexistente removido |
| Pergunta duplicada imóvel | ✅ Corrigido | Unificado |
| Checkbox dependentes | ✅ Corrigido | JS ajustado |
| Trocar imóvel não considera valor atual | ✅ Corrigido | Lógica adicionada |

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

## 📌 RESUMO PARA O VERCEPT (o que você é)

Você é o **Arquiteto de Soluções**. Sua função:
1. **Ler** o TUTORIAL.md (sempre a primeira ação)
2. **Identificar** a próxima tarefa (seção "PRÓXIMA TAREFA ESPECÍFICA")
3. **Copiar** o comando pronto da seção "COMANDO PRONTO PARA O GEMINI"
4. **Colar** no Gemini (VS Code, `Alt+G`)
5. **Aguardar** o Gemini executar
6. **Testar** usando o checklist
7. **Atualizar** o TUTORIAL.md
8. **Passar o bastão** usando a seção "QUANDO FINALIZAR ESTE CHAT"

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
