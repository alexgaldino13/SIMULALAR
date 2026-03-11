# 🏠 TUTORIAL COMPLETO - ImobCalc

## ⚠️ REGRA PRINCIPAL - ECONOMIA DE CRÉDITOS
> **Esta é a regra mais importante do projeto!** A IA (Vercept) tem créditos limitados e valiosos.
> - **Vercept:** Atue como Arquiteto de Soluções - DÊ ORDENS para o Gemini (VS Code) executar
> - **Gemini:** Use para codificação (`Alt+G` ou ícone na barra lateral ESQUERDA)
> - **NUNCA** peça para o Vercept codificar diretamente
> - **SEMPRE** atualize este arquivo TUTORIAL.md com o progresso

a
## 🎯 PRÓXIMA TAREFA ESPECÍFICA (O QUE FAZER AGORA)

| Item | Descrição | Arquivos | Status |
|------|-----------|----------|--------|
| **4.3** | Posicionamento de anúncios | `templates/` | 🔄 FAZER AGORA |
| **4.4** | Integrar Google Play Billing | `subscription_models.py` | 🔄 FAZER AGORA |

### 📋 DETALHAMENTO DA TAREFA

**Objetivo:** Inserir os banners e intersticiais nas páginas do sistema.
**Objetivo:** Configurar produtos de assinatura e fluxo de pagamento.

**Arquivos que serão modificados:**
1. `D:\PROJETOS\FI\Templates\base.html` - Adicionar banner no rodapé
2. `D:\PROJETOS\FI\simulacao\templates\simulacao\wizard_v2_resultados.html` - Adicionar intersticial
1. `D:\PROJETOS\FI\simulacao\subscription_models.py` - Ajustar modelos se necessário
2. `D:\PROJETOS\FI\simulacao\views.py` - Adicionar verificação de compra

**Referências:**
- Componente `admob_banner.html`
- Frontend em `static/js/admob-integration.js`
- Documentação Google Play Billing
- `MONETIZACAO_SETUP.md`


## 🤖 COMANDO PRONTO PARA O GEMINI (copiar e colar)

Quando abrir o Gemini no VS Code (`Alt+G`), cole EXATAMENTE isto:

```

CONTEXTO:
- O frontend já tem um AdMobManager que chama /api/assinaturas/status/ e /api/monetizacao/ad-view/
- Essas APIs ainda não existem
- O modelo Subscription já existe em subscription_models.py

TAREFA 1 - API DE STATUS DE ASSINATURA:
1. Abra o arquivo D:\PROJETOS\FI\simulacao\views.py
2. Adicione no topo: from django.http import JsonResponse
3. Adicione: import json
4. Crie a seguinte função:

def api_assinatura_status(request):
    """
    Retorna se o usuário atual tem assinatura premium ativa.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'is_premium': False})
    
    from .subscription_models import Subscription
    from django.utils import timezone
    
    has_active = Subscription.objects.filter(
        user=request.user,
        ativo=True,
        data_expiracao__gt=timezone.now()
    ).exists()
    
    return JsonResponse({'is_premium': has_active})

TAREFA 2 - API DE TRACKING DE ANÚNCIOS:
1. No mesmo arquivo views.py, adicione:

def api_registrar_ad_view(request):
    """
    Registra visualização de anúncio (banner, interstitial, rewarded).
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        ad_type = data.get('ad_type', 'unknown')
        
        # Por enquanto só loga no console
        user_info = f"usuário {request.user.id}" if request.user.is_authenticated else "visitante anônimo"
        print(f"📊 AdMob - {ad_type} exibido para {user_info}")
        
        return JsonResponse({'status': 'logged', 'ad_type': ad_type})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

TAREFA 3 - ADICIONAR AS ROTAS:
1. Abra o arquivo D:\PROJETOS\FI\simulacao\urls.py
2. Adicione estas duas linhas no final do bloco urlpatterns:

    path('api/assinaturas/status/', views.api_assinatura_status, name='api_assinatura_status'),
    path('api/monetizacao/ad-view/', views.api_registrar_ad_view, name='api_registrar_ad_view'),

TAREFA 4 - VERIFICAÇÃO:
Após implementar, execute o servidor e teste:
- Acesse http://127.0.0.1:8000/api/assinaturas/status/ (deve retornar JSON)
- Use Postman ou Insomnia para testar POST em http://127.0.0.1:8000/api/monetizacao/ad-view/ com body: {"ad_type": "banner"}
```


## ✅ CHECKLIST DE TESTE (após implementar)

- [ ] Acessar `/comparador-investimentos/` como usuário não-premium redireciona para a página de upgrade.
- [ ] Acessar `/comparador-investimentos/` como usuário premium funciona normalmente.
- [ ] Acessar `/investidor-imobiliario/` como usuário não-premium redireciona.


## 📅 ÚLTIMA ATUALIZAÇÃO

**Data:** 10 de Março de 2026
**Desenvolvedor:** Galdino  
**Progresso:** 57% (47 de 80 itens)
**Último item concluído:** ✅ Item 4.9 - Sistema de geração PDF (melhorado com gráficos)
**Próximo item:** ⬜ Item 4.3 - Posicionamento de anúncios

## 📜 HISTÓRICO DE COMANDOS DADOS AO GEMINI

| Data | Comando | Arquivos alterados | Status |
|------|---------|-------------------|--------|
| 10/03 | Implementar sistema de geração Excel (item 4.8) | views.py, urls.py, dashboard.html | ✅ Concluído |
| 10/03 | Implementar features exclusivas Premium (item 4.7) | views.py | ✅ Concluído |
| 06/03 | Criar tela de upgrade para Premium | views.py, urls.py, upgrade_premium.html | ✅ Concluído |
| 05/03 | Lógica de assinatura Premium | subscription_models.py, views.py, decorators.py | ✅ Concluído |
| 04/03 | Integrar Google Play Billing | subscription_models.py, views.py, urls.py | ✅ Concluído |
| 03/03 | Posicionamento de anúncios | base.html, wizard_v2_resgit status
ados.html | ✅ Concluído |
| 03/03 | Criar APIs AdMob (status e tracking) | views.py, urls.py | ✅ Concluído |
| 23/02 | Corrigir bugs wizard (pergunta duplicada, checkbox dependentes) | wizard_forms_v2.py, wizard_forms_novo.py, wizard_views_novo.py | ✅ Concluído |
| 18/02 | Corrigir erro filtro 'mul' | templatetags/custom_filters.py, 
| 10/03 | Melhorar sistema PDF (Item 4.9) + corrigir KeyError | views.py, wizard_views.py | ✅ Concluído |wizard_v2_resultados.html | ✅ Concluído |

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

### 🔄 FASE 4: Monetização (Em Andamento - 18%)

| Item | Descrição | Status | Próximo |
|------|-----------|--------|---------|
| 4.1 | Integrar Google AdMob no frontend | ✅ Concluído | - |
| 4.2 | APIs backend AdMob | ✅ Concluído | - |
| 4.3 | Posicionamento de anúncios nas páginas | ✅ Concluído | - |
| 4.4 | Integrar Google Play Billing | ✅ Concluído | - |
| 4.5 | Lógica de assinatura Premium | ✅ Concluído | - |
| 4.6 | Tela de upgrade para Premium | ✅ Concluído | - |
| **4.7** | **Features exclusivas Premium** | ✅ **Concluído** | - |
| 4.8 | Sistema de geração Excel | ⏳ Pendente | ➡️ |
| 4.9 | Sistema de geração PDF | ⏳ Pendente | |
| 4.10 | Sistema de Links Afiliados | ⏳ Pendente | |
| 4.11 | Testar fluxo completo | ⏳ Pendente | - |


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
   git commit -m "feat: implementadas APIs AdMob (item 4.2)"
   ```
5. **Avise:** "Pronto para próximo chat. O TUTORIAL.md está atualizado com o próximo item."

---

## 📊 STATUS GERAL DO PROJETO

**Fases Completas:**
- ✅ FASE 1: Autenticação (100%)
- ✅ FASE 2: LGPD (100%) 
- ✅ FASE 3: Parcerias (100%)

**Fase em Andamento:**
- 🔄 FASE 4: Monetização (18% - 2/11 itens)

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
