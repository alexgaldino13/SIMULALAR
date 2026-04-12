# 🏠 ImobCalc — Simulador de Aquisição de Imóvel

> **O melhor simulador de compra de imóveis do Brasil.**  
> Compare financiamento SAC, PRICE, consórcio, aluguel + investimento e muito mais — tudo em um único wizard intuitivo.

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Arquitetura](#-arquitetura)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação e Execução](#-instalação-e-execução)
- [Variáveis de Ambiente](#-variáveis-de-ambiente)
- [Estrutura de Pastas](#-estrutura-de-pastas)
- [Modelos de Dados](#-modelos-de-dados)
- [APIs Disponíveis](#-apis-disponíveis)
- [Planos e Monetização](#-planos-e-monetização)
- [Testes](#-testes)
- [Deploy em Produção](#-deploy-em-produção)
- [Roadmap](#-roadmap)

---

## 🎯 Visão Geral

O **ImobCalc** é uma aplicação web Django que guia o usuário por um **wizard de 5 etapas** para coletar seus dados financeiros e de perfil, gerando ao final uma análise comparativa completa entre os principais cenários de aquisição imobiliária no Brasil.

### Cenários Suportados

| # | Cenário | Descrição |
|---|---------|-----------|
| 1 | **Financiamento SAC** | Sistema de Amortização Constante — parcelas decrescentes |
| 2 | **Financiamento PRICE** | Parcelas fixas — tabela Price tradicional |
| 3 | **Consórcio** | Análise de consórcio com e sem lances |
| 4 | **Aluguel + Investimento** | Custo de oportunidade de alugar e investir a diferença |
| 5 | **Guardar Dinheiro** | Poupança progressiva até acumular o valor do imóvel |
| 6 | **Investidor Imobiliário** | Análise de viabilidade para compra visando renda |
| 7 | **Comparador de Investimentos** | Comparação livre entre múltiplos cenários (Premium) |

---

## ✨ Funcionalidades

### Wizard de Simulação
- ✅ 5 etapas guiadas com validação em tempo real
- ✅ Poll cards visuais para escolhas categóricas
- ✅ Inputs monetários formatados automaticamente (Cleave.js)
- ✅ Feedback progressivo com animações
- ✅ Responsivo (mobile, tablet e desktop)
- ✅ Navegação via teclado (acessibilidade WCAG)

### Resultados
- ✅ Cards comparativos com todos os cenários
- ✅ Cálculo de CET (Custo Efetivo Total)
- ✅ Projeção do FGTS
- ✅ Margem de crédito disponível
- ✅ Juros reais vs. correção monetária

### Usuário e Perfil
- ✅ Cadastro/login por e-mail e username
- ✅ OAuth Google (via django-allauth)
- ✅ Simulações salvas no dashboard
- ✅ Perfil de corretor com CRECI e logo (Plano Profissional)

### Monetização
- ✅ **Plano Free** — wizard completo com anúncios AdMob
- ✅ **Plano Premium** — sem anúncios + exportação Excel/PDF
- ✅ **Plano Profissional** — PDF White-Label com marca do corretor
- ✅ Links afiliados com rastreamento de cliques
- ✅ Integração Google Play Billing (webhook)
- ✅ APIs REST para AdMob (status de assinatura, tracking de anúncios)

### LGPD
- ✅ Consentimento granular
- ✅ Exportação de dados pessoais
- ✅ Solicitação de exclusão de conta
- ✅ Auditoria de acessos

---

## 🏗️ Arquitetura

```
ImobCalc/             ← Configurações Django (settings, urls, wsgi)
simulacao/            ← App principal
  ├── models.py                  ← CustomUser, Simulação, LinkAfiliado, ...
  ├── subscription_models.py     ← SubscriptionPlan, Subscription
  ├── monetizacao_models.py      ← AdView, UsoRecursos, Transacao
  ├── calculadora_financeira.py  ← Motor de cálculo (SAC, PRICE, Consórcio...)
  ├── wizard_views_v2.py         ← Views do wizard (lógica principal)
  ├── wizard_forms_v2.py         ← Formulários de cada etapa
  ├── views.py                   ← Views auxiliares e APIs REST
  ├── auth_views.py              ← Login, cadastro, perfil, OAuth
  ├── lgpd_views.py              ← LGPD (consentimento, exportação, exclusão)
  ├── monetizacao_views.py       ← APIs DRF (AdMob, billing)
  ├── decorators.py              ← @premium_required
  ├── middleware.py              ← Sessão (atividade + segurança)
  └── tests/                     ← Suite de testes
static/
  ├── css/wizard-responsive.css  ← Estilos do wizard
  └── js/
      ├── wizard.js              ← Lógica frontend do wizard
      └── admob-integration.js   ← Gerenciador de anúncios AdMob
Templates/
  ├── simulacao/                 ← Templates do wizard e resultados
  └── components/admob_banner.html
```

---

## 📦 Pré-requisitos

| Dependência | Versão mínima |
|-------------|---------------|
| Python | 3.10+ |
| Django | 4.2+ |
| django-allauth | qualquer |
| reportlab | qualquer |
| openpyxl | qualquer |
| djangorestframework | qualquer |

---

## 🚀 Instalação e Execução

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/imobcalc.git
cd imobcalc
```

### 2. Criar e ativar o ambiente virtual

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

> **Dependências completas utilizadas no projeto:**
> ```
> Django>=4.2
> django-allauth
> reportlab
> openpyxl
> djangorestframework
> pillow
> ```

### 4. Aplicar migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Criar superusuário (admin)

```bash
python manage.py createsuperuser
```

### 6. Iniciar o servidor

```bash
python manage.py runserver
```

Acesse: **http://localhost:8000**  
Admin: **http://localhost:8000/admin/**

---

## 🔐 Variáveis de Ambiente

Para produção, substitua os valores hardcoded no `settings.py` por variáveis de ambiente. Crie um arquivo `.env` na raiz:

```env
# Segurança
SECRET_KEY=sua-secret-key-super-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=seudominio.com.br,www.seudominio.com.br

# Banco de dados (produção — PostgreSQL recomendado)
DATABASE_URL=postgresql://usuario:senha@host:5432/imobcalc

# E-mail (produção)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu@email.com
EMAIL_HOST_PASSWORD=sua-senha-smtp

# OAuth Google (obrigatório para login social)
GOOGLE_CLIENT_ID=seu-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=seu-google-client-secret

# Mídia (produção — usar S3 ou similar)
MEDIA_ROOT=/var/www/imobcalc/media
```

> ⚠️ **Nunca commite o arquivo `.env` no repositório.** Ele já está no `.gitignore`.

### Configuração do OAuth Google

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto e habilite a **Google Identity API**
3. Em **Credenciais → Criar credenciais → ID do cliente OAuth 2.0**
4. Adicione `http://localhost:8000/accounts/google/login/callback/` como URI de redirecionamento autorizado
5. Copie o Client ID e Secret para o `.env`
6. No admin Django (`/admin/`), configure o **Social Application** com os mesmos dados

---

## 📂 Estrutura de Pastas

```
d:\PROJETOS\FI\
├── ImobCalc/               # Configurações do projeto Django
│   ├── settings.py
│   ├── urls.py
│   ├── cache_settings.py   # Configuração de cache (LocMemCache)
│   └── auth_settings.py
├── simulacao/              # App principal
│   ├── migrations/         # Histórico de migrations
│   ├── static/             # Arquivos estáticos do app
│   ├── templates/          # Templates HTML
│   │   └── simulacao/
│   │       ├── wizard_v2_step.html       # Etapas do wizard
│   │       └── wizard_v2_resultados.html # Página de resultados
│   ├── tests/              # Suite de testes automatizados
│   │   ├── test_affiliate_links.py       # Item 6.8
│   │   ├── test_admob_integration.py     # Item 6.6
│   │   ├── test_calculos.py              # Item 6.5
│   │   ├── test_premium_subscription.py  # Item 6.7
│   │   └── test_wizard_integration.py    # Item 5.7
│   └── docs/               # Documentação técnica
│       ├── WIZARD_GUIA_DESENVOLVEDOR.md
│       ├── WIZARD_GUIA_USUARIO.md
│       └── WIZARD_API.md
├── static/                 # Arquivos estáticos globais
│   ├── css/
│   │   ├── wizard-responsive.css
│   │   └── wizard-responsive.min.css
│   └── js/
│       ├── wizard.js
│       ├── wizard.min.js
│       └── admob-integration.js
├── Templates/              # Templates globais (base.html, etc.)
├── media/                  # Uploads de usuários (avatares, logos)
├── db.sqlite3              # Banco de dados (desenvolvimento)
├── manage.py
├── requirements.txt
└── TUTORIAL.md             # Documento mestre do projeto
```

---

## 🗄️ Modelos de Dados

### Usuário
| Modelo | Descrição |
|--------|-----------|
| `CustomUser` | Estende `AbstractUser` — adiciona `tipo_conta`, `premium_expira_em`, `telefone` |
| `UserProfile` | Perfil estendido — `cpf`, `renda_mensal`, `creci`, `logo_empresa` |

### Simulação
| Modelo | Descrição |
|--------|-----------|
| `SavedSimulation` | Simulações salvas — dados em JSON + resultados calculados |
| `SimulationShare` | Token para compartilhamento de simulação via link |

### Monetização
| Modelo | Descrição |
|--------|-----------|
| `SubscriptionPlan` | Planos disponíveis (Free, Premium, Profissional) |
| `Subscription` | Assinatura do usuário com data de expiração |
| `LinkAfiliado` | Links de parceiros com código de rastreamento |
| `CliqueAfiliado` | Registro de cada clique (IP, user-agent, usuário) |
| `AdView` | Rastreamento de visualizações de anúncios AdMob |

---

## 🌐 APIs Disponíveis

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `GET` | `/api/assinaturas/status/` | Status da assinatura do usuário | Sim |
| `POST` | `/api/monetizacao/ad-view/` | Registra visualização de anúncio | Não |
| `POST` | `/api/monetizacao/google-play-billing-webhook/` | Webhook Google Play | Não |
| `GET` | `/api/afiliados/` | Lista links afiliados ativos | Não |
| `GET` | `/api/afiliados/?tipo=banco` | Filtra por tipo de afiliado | Não |
| `GET` | `/afiliado/<id>/` | Redireciona e registra clique | Não |

---

## 💰 Planos e Monetização

| Recurso | Free | Premium | Profissional |
|---------|:----:|:-------:|:------------:|
| Wizard completo | ✅ | ✅ | ✅ |
| Resultados comparativos | ✅ | ✅ | ✅ |
| Anúncios AdMob | ✅ | ❌ | ❌ |
| Salvar simulações | ✅ | ✅ | ✅ |
| Exportar PDF | ❌ | ✅ | ✅ |
| Exportar Excel | ❌ | ✅ | ✅ |
| Investidor Imobiliário | ❌ | ✅ | ✅ |
| Comparador de Investimentos | ❌ | ✅ | ✅ |
| PDF White-Label (logo da imobiliária) | ❌ | ❌ | ✅ |

---

## 🧪 Testes

### Executar todos os testes

```bash
python manage.py test simulacao.tests -v 2
```

### Executar um módulo específico

```bash
# Testes do wizard
python manage.py test simulacao.tests.test_wizard_integration -v 2

# Testes de cálculos financeiros
python manage.py test simulacao.tests.test_calculos -v 2

# Testes de assinatura Premium
python manage.py test simulacao.tests.test_premium_subscription -v 2

# Testes AdMob
python manage.py test simulacao.tests.test_admob_integration -v 2

# Testes de Links Afiliados
python manage.py test simulacao.tests.test_affiliate_links -v 2
```

### Cobertura de Testes

| Módulo | Arquivo | Testes |
|--------|---------|--------|
| Wizard (integração) | `test_wizard_integration.py` | 8 |
| Cálculos financeiros | `test_calculos.py` | ~12 |
| Assinatura Premium | `test_premium_subscription.py` | 4 |
| Integração AdMob | `test_admob_integration.py` | ~6 |
| Links Afiliados | `test_affiliate_links.py` | 9 |

### Performance (Lighthouse)

| Métrica | Mobile | Desktop |
|---------|--------|---------|
| Performance | 91 | 83 |
| Acessibilidade | 95 | 95 |
| Best Practices | 96 | 96 |
| SEO | 90 | 90 |

---

## 🚢 Deploy em Produção

### Checklist de Produção

```bash
# 1. Coletar arquivos estáticos
python manage.py collectstatic --noinput

# 2. Verificar configurações de segurança
python manage.py check --deploy

# 3. Aplicar migrations
python manage.py migrate

# 4. Criar superusuário
python manage.py createsuperuser
```

### Configurações críticas para produção (`settings.py`)

```python
DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']          # Nunca hardcoded!
ALLOWED_HOSTS = ['seudominio.com.br']
SESSION_COOKIE_SECURE = True                   # Exige HTTPS
CSRF_COOKIE_SECURE = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```

---

## 🗺️ Roadmap

### ✅ Completo
- Fase 1 — Autenticação (Custom User, OAuth Google, recuperação de senha)
- Fase 2 — LGPD (consentimento, exportação, exclusão, auditoria)
- Fase 3 — Parcerias (links afiliados, APIs de parceiros)
- Fase 4 — Monetização (AdMob, assinaturas, Google Play Billing)
- Fase 5 — Design e UX (wizard responsivo, poll cards, animações, acessibilidade)
- Fase 6 — Testes Finais (Lighthouse, integração, cálculos, assinatura, afiliados)

### ⏳ Próximas Fases
- **Fase 7 — Mobile**: App Android nativo com React Native ou Flutter
- **Fase 8 — Publicação**: Google Play Store, domínio, CI/CD GitHub Actions

---

## 👤 Autor

Desenvolvido por **Alex Galdino** — [@alexgaldino13](https://github.com/alexgaldino13)

---

> 📄 Para entender o histórico completo de decisões e progresso do projeto, consulte o [`TUTORIAL.md`](TUTORIAL.md).
