# 💰 SISTEMA DE MONETIZAÇÃO - FI (Financiamento Imobiliário)

📅 **Versão:** 1.0  
🎯 **Status:** Pronto para Implementação  
💻 **Plataformas:** Android (Google Play), iOS (App Store), Web  

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Versão Grátis com AdMob](#versão-grátis-com-admob)
3. [Versão Premium](#versão-premium)
4. [Integração Google Play (Android)](#integração-google-play-android)
5. [Integração App Store (iOS)](#integração-app-store-ios)
6. [Implementação em Django](#implementação-em-django)
7. [Uso em Templates](#uso-em-templates)
8. [Testes](#testes)
9. [FAQ](#faq)

---

## 🎯 Visão Geral

O sistema de monetização oferece duas versões:

| Recurso | Grátis | Premium |
|---------|--------|---------|
| **Simulações/dia** | 5 | Ilimitado |
| **Comparações/dia** | 2 | Ilimitado |
| **Exportação Excel** | 1/mês | Ilimitado |
| **Anúncios** | ✓ Sim | ✗ Não |
| **Gráficos Avançados** | ✗ Não | ✓ Sim |
| **Múltiplos Cenários** | 2 | Ilimitado |
| **Preço** | R$ 0,00 | R$ 9,90/mês ou R$ 49,90/ano |

---

## 📱 VERSÃO GRÁTIS COM ADMOB

### O que é AdMob?

**AdMob** é plataforma de publicidade do Google que exibe anúncios em apps/web.

- Ganhe dinheiro por **impressões** (visualizações)
- Ganhe dinheiro por **cliques**
- Ganhe dinheiro por **conversões** (compras)

### Tipos de Anúncios

#### 1️⃣ **Banner**
- Tamanho: 320x50px (mobile) ou 728x90px (tablet/web)
- Posição: Topo ou rodapé
- Taxa de clique: ~2-3%
- Receita: $0.25-2.00 por 1.000 impressões (CPM)

```
┌─────────────────────────────────────────┐
│  Simulador de Financiamento Imobiliário  │
├─────────────────────────────────────────┤
│  [         ANÚNCIO GOOGLE ADMOB         ]  ← Banner no topo
├─────────────────────────────────────────┤
│  Valor do Imóvel: R$ [________]          │
│  ...                                     │
└─────────────────────────────────────────┘
```

#### 2️⃣ **Intersticial**
- Tela cheia, aparece entre transições
- Exemplo: Após visualizar resultado
- Taxa de clique: ~5-8%
- Receita: $1.00-8.00 por 1.000 impressões (CPM)

```
Usuário clica "Exportar" 
        ↓
┌────────────────────────┐
│   ANÚNCIO INTERSTICIAL │
│                        │
│   [Imagem do Anúncio]  │
│                        │
│  [ X Fechar ]          │
└────────────────────────┘
        ↓
Começa exportação
```

#### 3️⃣ **Recompensa**
- Usuário assiste anúncio para ganhar benefício
- Exemplo: "Assista anúncio = 1 comparação extra"
- Taxa de conclusão: ~90%
- Receita: $2.00-15.00 por 1.000 impressões (CPM)

```
🎁 Você atingiu limite de comparações diárias

[ Assista anúncio para +1 comparação ]

Usuário assiste → Recebe +1 comparação
```

### Posições de Anúncios no App

```
┌──────────────────────────────────┐
│  [Banner - TOPO]                 │  ← above_fold
├──────────────────────────────────┤
│                                  │
│     CONTEÚDO PRINCIPAL           │
│     (Formulário/Resultados)      │
│                                  │
│                                  │
│  [Intersticial - MEIO]           │  ← middle (entre resultados)
│                                  │
│     MAIS CONTEÚDO                │
│                                  │
├──────────────────────────────────┤
│  [Banner - RODAPÉ]               │  ← bottom
└──────────────────────────────────┘
```

### IDs de Teste do AdMob

Durante desenvolvimento, use SEMPRE estes IDs de teste. Usando IDs de produção durante testes viola políticas do Google!

**App ID de Teste (Google)**
```
Android: ca-app-pub-3940256099942544~3347511713
iOS: ca-app-pub-3940256099942544~1458002754
```

**Anúncios de Teste (colocar em seu app)**

| Formato | Android | iOS |
|---------|---------|-----|
| Banner | ca-app-pub-3940256099942544/6300978111 | ca-app-pub-3940256099942544/2934735945 |
| Intersticial | ca-app-pub-3940256099942544/1033173712 | ca-app-pub-3940256099942544/4411468910 |
| Recompensa | ca-app-pub-3940256099942544/6978759866 | ca-app-pub-3940256099942544/5224354917 |

👉 **Fonte:** [Google AdMob Testing Documentation](https://developers.google.com/admob/android/test-ads)

### Setup Básico em Django

#### 1️⃣ Instalar openpyxl (já feito)
```bash
pip install openpyxl
```

#### 2️⃣ Adicionar modelos ao `simulacao/models.py`

Copiar os modelos da seção comentada em `monetizacao.py`:

```python
# simulacao/models.py
from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    plano = models.CharField(
        max_length=20,
        choices=[('gratis', 'Grátis'), ('premium', 'Premium')],
        default='gratis'
    )
    premium_ativo = models.BooleanField(default=False)
    premium_expira = models.DateTimeField(null=True, blank=True)
    # ... (veja monetizacao.py para código completo)

class ContadorAnuncios(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    banner_hoje = models.IntegerField(default=0)
    # ... (veja monetizacao.py)
```

#### 3️⃣ Configurar em `settings.py`

```python
# ImobCalc/settings.py

# ========== MONETIZAÇÃO ==========

# Ambiente (teste ou producao)
ADMOB_AMBIENTE = 'teste'  # Mude para 'producao' quando publicar

# IDs de Publicador (conseguir em https://admob.google.com/)
ADMOB_BANNER_ANDROID = 'ca-app-pub-3940256099942544/6300978111'  # TESTE
ADMOB_BANNER_IOS = 'ca-app-pub-3940256099942544/2934735945'      # TESTE

# Chave secreta para validação de compra (gerar)
GOOGLE_PLAY_SECRET_KEY = 'sua-chave-secreta-base64-aqui'
APP_STORE_SHARED_SECRET = 'sua-chave-compartilhada-app-store'

# Limite de anúncios (anti-spam)
ADMOB_MAX_BANNER_DIA = 20
ADMOB_MAX_INTERSTICIAL_DIA = 5
ADMOB_MAX_RECOMPENSA_DIA = 10
```

#### 4️⃣ Executar migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 💳 VERSÃO PREMIUM

### Produtos In-App

Dois planos oferecem flexibilidade:

**Premium Mensal: R$ 9,90**
- Válido por 30 dias
- Sem anúncios
- Recursos ilimitados
- Cancela a qualquer momento

**Premium Anual: R$ 49,90**
- Válido por 365 dias
- Sem anúncios
- Recursos ilimitados
- Melhor valor (58% de desconto)

### Fluxo de Compra (Google Play)

```
Usuário clica "Upgrade para Premium"
            ↓
┌───────────────────────────────┐
│  Tela de Seleção de Plano    │
│  • Premium Mensal: R$ 9,90    │
│  • Premium Anual: R$ 49,90    │
└───────────────────────────────┘
            ↓
Usuário clica "Comprar"
            ↓
┌───────────────────────────────┐
│  Google Play Billing Dialog   │
│  Autenticação com Google      │
│  Processamento do pagamento   │
└───────────────────────────────┘
            ↓
Transação bem-sucedida
            ↓
┌───────────────────────────────┐
│  ✓ Premium Ativado!           │
│  Válido até: 25/02/2026      │
│  Aproveite recursos ilimitados│
└───────────────────────────────┘
            ↓
App chamada: PremiumManager.ativar_premium()
            ↓
Perfil atualizado no banco de dados
```

### Verificação de Premium em Tempo Real

```python
# Em qualquer view
from simulacao.monetizacao import PremiumManager

def minha_view(request):
    pm = PremiumManager(request.user)
    
    if pm.eh_premium():
        # Usuário é premium
        return render(request, 'resultado_completo.html', dados)
    else:
        # Usuário é grátis
        if pm.pode_exportar_excel():
            # Pode exportar (ainda tem cota)
            return render(request, 'resultado_com_anuncios.html', dados)
        else:
            # Atingiu limite
            return render(request, 'bloqueado.html', contexto_upgrade)
```

---

## 🤖 INTEGRAÇÃO GOOGLE PLAY (ANDROID)

### Passo 1: Criar Conta Google Play Developer

1. Acesse https://play.google.com/console
2. Clique "Criar aplicativo" 
3. Preencha dados básicos:
   - Nome: "FI - Financiamento Imobiliário"
   - Categoria: "Finanças"
   - Classificação: "12+" (ou conforme necessário)

### Passo 2: Configurar Produtos In-App

Em **Play Console → Seu App → Monetização → Produtos In-App:**

#### Criar "com.ficalc.premium.mensal"

```
ID do Produto: com.ficalc.premium.mensal
Título: FI Premium Mensal
Descrição: Acesso premium por 30 dias - sem anúncios, recursos ilimitados
Preço: R$ 9,90
Período de faturamento: Mensal (30 dias)
```

#### Criar "com.ficalc.premium.anual"

```
ID do Produto: com.ficalc.premium.anual
Título: FI Premium Anual
Descrição: Acesso premium por 365 dias - sem anúncios, recursos ilimitados
Preço: R$ 49,90
Período de faturamento: Anual (365 dias)
```

### Passo 3: Configurar Chave de Segurança

Em **Play Console → Seu App → Configuração → Chaves de API:**

1. Clique "Gerar nova chave"
2. Salve em local seguro (ex: `.env` ou `settings.py`)

```python
# .env
GOOGLE_PLAY_PACKAGE_NAME=com.fi.calculadora
GOOGLE_PLAY_LICENSE_KEY="MIIBIjANBgkqhkiG9w0BA..."
```

### Passo 4: Integrar SDK do Google Play Billing em Android

No seu projeto Android (se tiver):

```gradle
// build.gradle (Module: app)
dependencies {
    implementation "com.google.android.play:core:1.10.3"
}
```

Implementar listener de compra:

```kotlin
// MainActivity.kt
import com.android.billingclient.api.*

class MainActivity : AppCompatActivity() {
    private lateinit var billingClient: BillingClient
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setupBillingClient()
    }
    
    private fun setupBillingClient() {
        billingClient = BillingClient.newBuilder(this)
            .setListener(purchasesUpdatedListener)
            .enablePendingPurchases()
            .build()
        
        billingClient.startConnection(object : BillingClientStateListener {
            override fun onBillingSetupFinished(billingResult: BillingResult) {
                if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                    querySkuDetails()
                }
            }
            
            override fun onBillingServiceDisconnected() {
                // Reconectar
            }
        })
    }
    
    private fun querySkuDetails() {
        val skuList = listOf("com.ficalc.premium.mensal", "com.ficalc.premium.anual")
        val params = SkuDetailsParams.newBuilder()
            .setSkusList(skuList)
            .setType(BillingClient.SkuType.SUBS)
            .build()
        
        billingClient.querySkuDetailsAsync(params) { billingResult, skuDetailsList ->
            if (billingResult.responseCode == BillingClient.BillingResponseCode.OK && skuDetailsList != null) {
                for (skuDetails in skuDetailsList) {
                    // Mostrar opção de compra
                    showPremiumOption(skuDetails)
                }
            }
        }
    }
    
    private fun launchPurchaseFlow(skuDetails: SkuDetails) {
        val billingFlowParams = BillingFlowParams.newBuilder()
            .setSkuDetails(skuDetails)
            .build()
        
        billingClient.launchBillingFlow(this, billingFlowParams)
    }
    
    private val purchasesUpdatedListener = PurchasesUpdatedListener { billingResult, purchases ->
        if (billingResult.responseCode == BillingClient.BillingResponseCode.OK && purchases != null) {
            for (purchase in purchases) {
                handlePurchase(purchase)
            }
        }
    }
    
    private fun handlePurchase(purchase: Purchase) {
        // Verificar assinatura
        if (purchase.purchaseState == Purchase.PurchaseState.PURCHASED) {
            // Enviar para servidor (Django) para verificar assinatura
            sendReceiptToServer(purchase.originalJson, purchase.signature)
        }
    }
    
    private fun sendReceiptToServer(purchaseData: String, signature: String) {
        // Fazer POST para seu servidor Django
        // POST /api/verificar-compra/
        // {
        //     "receipt": purchaseData,
        //     "signature": signature,
        //     "produto": "com.ficalc.premium.mensal"
        // }
    }
}
```

### Passo 5: Verificar Compra no Django

Criar endpoint que verifica a assinatura:

```python
# simulacao/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from simulacao.monetizacao import validar_assinatura_compra, PremiumManager
import json

@csrf_exempt
def verificar_compra_google(request):
    """Verifica compra do Google Play."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        dados = json.loads(request.body)
        receipt = dados.get('receipt')
        signature = dados.get('signature')
        produto = dados.get('produto')
        
        # Validar assinatura
        # (em produção, usar Google Play API para validação)
        # Para teste: validar assinatura local
        
        if validar_receipt_google(receipt, signature):
            # Ativar Premium
            pm = PremiumManager(request.user)
            pm.ativar_premium(produto)
            
            return JsonResponse({
                'sucesso': True,
                'mensagem': 'Premium ativado com sucesso!',
                'expira_em': pm.perfil.premium_expira.isoformat()
            })
        else:
            return JsonResponse({
                'sucesso': False,
                'erro': 'Assinatura inválida'
            }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'sucesso': False,
            'erro': str(e)
        }, status=500)
```

---

## 🍎 INTEGRAÇÃO APP STORE (IOS)

### Passo 1: Criar App no App Store Connect

1. Acesse https://appstoreconnect.apple.com/
2. Clique "Meus Apps" → "Novo App"
3. Preencha dados:
   - Nome: "FI - Financiamento Imobiliário"
   - Bundle ID: `com.seudominio.ficalc`
   - Categoria: "Finanças"

### Passo 2: Configurar In-App Purchases

Em **App Store Connect → Seu App → Recursos → In-App Purchases:**

#### Assinatura "com.ficalc.premium.mensal"

```
Tipo: Subscription (Renovável)
ID: com.ficalc.premium.mensal
Descrição: Premium Mensal - 30 dias
Preço: R$ 9,90 (configurar por região)
Período de renovação: 1 mês
```

#### Assinatura "com.ficalc.premium.anual"

```
Tipo: Subscription (Renovável)
ID: com.ficalc.premium.anual
Descrição: Premium Anual - 365 dias
Preço: R$ 49,90 (configurar por região)
Período de renovação: 1 ano
```

### Passo 3: Obter Certificado de Compartilhamento de Segredos

Em **App Store Connect → Seu App → Configuração → Certificados, IDs e Perfis:**

1. Anote o **Identificador do Pacote Compartilhado** (Shared Secret)
2. Salve em `settings.py`:

```python
APP_STORE_SHARED_SECRET = 'seu-segredo-compartilhado-aqui'
```

### Passo 4: Integrar StoreKit em iOS

No seu projeto Xcode (se tiver):

```swift
// ViewController.swift
import StoreKit

class PremiumViewController: UIViewController, SKPaymentTransactionObserver {
    
    override func viewDidLoad() {
        super.viewDidLoad()
        SKPaymentQueue.default().add(self)
        loadProducts()
    }
    
    func loadProducts() {
        let productIDs: Set<String> = [
            "com.ficalc.premium.mensal",
            "com.ficalc.premium.anual"
        ]
        
        let request = SKProductsRequest(productIdentifiers: productIDs)
        request.delegate = self
        request.start()
    }
    
    func purchaseProduct(_ product: SKProduct) {
        let payment = SKPayment(product: product)
        SKPaymentQueue.default().add(payment)
    }
    
    func paymentQueue(_ queue: SKPaymentQueue, updatedTransactions transactions: [SKPaymentTransaction]) {
        for transaction in transactions {
            switch transaction.transactionState {
            case .purchased:
                handlePurchase(transaction)
                SKPaymentQueue.default().finishTransaction(transaction)
                
            case .failed:
                SKPaymentQueue.default().finishTransaction(transaction)
                
            case .restored:
                handlePurchase(transaction)
                SKPaymentQueue.default().finishTransaction(transaction)
                
            case .deferred, .purchasing:
                break
            }
        }
    }
    
    func handlePurchase(_ transaction: SKPaymentTransaction) {
        // Enviar receipt para Django
        if let receipt = Bundle.main.appStoreReceiptURL {
            let data = try? Data(contentsOf: receipt)
            let receiptString = data?.base64EncodedString()
            
            // POST para servidor Django
            sendReceiptToServer(
                receipt: receiptString ?? "",
                produto: transaction.payment.productIdentifier
            )
        }
    }
}
```

### Passo 5: Validar Receipt no Django

```python
# simulacao/views.py
import requests
import json

def validar_receipt_app_store(receipt_data):
    """Valida receipt do App Store com Apple."""
    
    shared_secret = settings.APP_STORE_SHARED_SECRET
    
    # URL de produção (usar sandbox para teste)
    url = "https://buy.itunes.apple.com/validationUrl"  # Produção
    # url = "https://sandbox.itunes.apple.com/verifyReceipt"  # Sandbox/Teste
    
    payload = {
        "receipt-data": receipt_data,
        "password": shared_secret
    }
    
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        
        # Status 0 = receipt válido
        if result['status'] == 0:
            return True, result.get('latest_receipt_info')
        else:
            return False, None
    
    except Exception as e:
        print(f"Erro validando receipt: {e}")
        return False, None
```

---

## 🔧 IMPLEMENTAÇÃO EM DJANGO

### 1️⃣ Adicionar à `settings.py`

```python
# ImobCalc/settings.py

INSTALLED_APPS = [
    # ...
    'simulacao',
    'django_extensions',  # opcional mas útil
]

# ===== MONETIZAÇÃO =====
ADMOB_AMBIENTE = 'teste'  # 'teste' ou 'producao'
GOOGLE_PLAY_SECRET_KEY = 'sua-chave-secreta'
APP_STORE_SHARED_SECRET = 'sua-chave-compartilhada'
```

### 2️⃣ Criar URLs de API

```python
# simulacao/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # ... URLs existentes ...
    
    # Monetização
    path('api/verificar-compra/', views.verificar_compra_google, name='verificar_compra'),
    path('api/status-premium/', views.obter_status_premium, name='status_premium'),
    path('api/limites-uso/', views.obter_limites_uso, name='limites_uso'),
]
```

### 3️⃣ Implementar Views

```python
# simulacao/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from simulacao.monetizacao import PremiumManager, AdMobManager
import json

@login_required
@require_http_methods(["GET"])
def obter_status_premium(request):
    """Retorna status Premium do usuário."""
    pm = PremiumManager(request.user)
    return JsonResponse(pm.obter_status())

@login_required
@require_http_methods(["GET"])
def obter_limites_uso(request):
    """Retorna limites de uso do usuário."""
    pm = PremiumManager(request.user)
    status = pm.obter_status()
    
    return JsonResponse({
        'usuario': request.user.username,
        'eh_premium': pm.eh_premium(),
        'pode_exportar': pm.pode_exportar_excel(),
        'pode_simular': pm.pode_fazer_simulacao(),
        'pode_comparar': pm.pode_comparar_cenarios(),
    })

@login_required
@require_http_methods(["POST"])
def verificar_compra_google(request):
    """Verifica e ativa compra do Google Play."""
    try:
        dados = json.loads(request.body)
        produto = dados.get('produto')
        
        if produto not in ['com.ficalc.premium.mensal', 'com.ficalc.premium.anual']:
            return JsonResponse({'erro': 'Produto inválido'}, status=400)
        
        pm = PremiumManager(request.user)
        sucesso = pm.ativar_premium(produto)
        
        if sucesso:
            return JsonResponse({
                'sucesso': True,
                'status': pm.obter_status()
            })
        else:
            return JsonResponse({'erro': 'Erro ao ativar'}, status=400)
    
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)
```

### 4️⃣ Middleware para Contexto Global

```python
# simulacao/middleware.py

from simulacao.monetizacao import PremiumManager, AdMobManager

class MonetizacaoMiddleware:
    """Adiciona contexto de monetização a todas as requisições."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            request.premium_manager = PremiumManager(request.user)
            request.ad_manager = AdMobManager(request.user)
        
        response = self.get_response(request)
        return response

# Adicionar em settings.py
MIDDLEWARE = [
    # ... middlewares existentes ...
    'simulacao.middleware.MonetizacaoMiddleware',
]
```

---

## 🎨 USO EM TEMPLATES

### Template Base com Anúncios

```html
<!-- simulacao/templates/base.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>FI - Financiamento Imobiliário</title>
    <meta name="google-site-verification" content="...">
    
    <!-- Google AdSense (para web) -->
    {% if not request.premium_manager.eh_premium %}
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-app-pub-xxxxxxxxxxxxxxxx"></script>
    {% endif %}
</head>
<body>
    
    <!-- Banner topo (visível apenas grátis) -->
    {% if not request.premium_manager.eh_premium %}
    <div class="ad-container ad-banner-top">
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-app-pub-xxxxxxxxxxxxxxxx"
             data-ad-slot="xxxxxxxxxx"
             data-ad-format="horizontal"></ins>
        <script>
            (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
    </div>
    {% endif %}
    
    <!-- Menu Premium / Status -->
    <nav class="navbar">
        {% if request.user.is_authenticated %}
            {% if request.premium_manager.eh_premium %}
                <span class="badge-premium">⭐ PREMIUM ATIVO</span>
            {% else %}
                <a href="{% url 'upgrade_premium' %}" class="btn-upgrade">
                    Upgrade para Premium
                </a>
            {% endif %}
        {% endif %}
    </nav>
    
    <!-- Conteúdo principal -->
    <main class="container">
        {% block content %}{% endblock %}
    </main>
    
    <!-- Banner rodapé (visível apenas grátis) -->
    {% if not request.premium_manager.eh_premium %}
    <div class="ad-container ad-banner-bottom">
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-app-pub-xxxxxxxxxxxxxxxx"
             data-ad-slot="xxxxxxxxxx"
             data-ad-format="horizontal"></ins>
        <script>
            (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
    </div>
    {% endif %}

</body>
</html>
```

### Template de Resultados

```html
<!-- simulacao/templates/resultado.html -->
{% extends "base.html" %}

{% block content %}

<div class="resultado-container">
    
    <!-- Aviso se limite atingido -->
    {% if not request.premium_manager.pode_exportar %}
    <div class="alert alert-warning">
        ⚠️ Você atingiu seu limite mensal de exportação (1/mês).
        <a href="{% url 'upgrade_premium' %}">Upgrade para Premium</a> para ilimitado.
    </div>
    {% endif %}
    
    <!-- Resultados -->
    <div class="resultados">
        {{ dados.resumo|safe }}
    </div>
    
    <!-- Anúncio intersticial (entre resultados) -->
    {% if not request.premium_manager.eh_premium %}
    <div class="ad-intersticial">
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-app-pub-xxxxxxxxxxxxxxxx"
             data-ad-slot="xxxxxxxxxx"
             data-ad-format="in-article"></ins>
        <script>
            (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
    </div>
    {% endif %}
    
    <!-- Botões de ação -->
    <div class="botoes-acao">
        {% if request.premium_manager.pode_exportar %}
            <a href="{% url 'exportar' %}" class="btn btn-primary">
                📥 Exportar para Excel
            </a>
        {% else %}
            <button disabled class="btn btn-secondary">
                📥 Exportar (Limite Atingido)
            </button>
            <a href="{% url 'upgrade_premium' %}" class="btn btn-warning">
                Upgrade +
            </a>
        {% endif %}
        
        {% if request.premium_manager.pode_comparar %}
            <a href="{% url 'comparar' %}" class="btn btn-primary">
                📊 Comparar Cenários
            </a>
        {% else %}
            <button disabled class="btn btn-secondary">
                📊 Comparar (Limite Atingido)
            </button>
        {% endif %}
    </div>
    
</div>

{% endblock %}
```

### Página de Upgrade Premium

```html
<!-- simulacao/templates/upgrade_premium.html -->
{% extends "base.html" %}

{% block content %}

<div class="premium-upgrade">
    
    <h1>✨ Upgrade para Premium</h1>
    
    {% if request.premium_manager.eh_premium %}
        <div class="alert alert-success">
            ✓ Você já é Premium! 
            Status válido até {{ request.premium_manager.perfil.premium_expira|date:"d/m/Y" }}
        </div>
    {% else %}
    
    <div class="planos-container">
        
        <!-- Plano Mensal -->
        <div class="plano">
            <h2>📅 Premium Mensal</h2>
            <p class="preco">R$ 9,90</p>
            <p class="periodo">por mês</p>
            <ul class="beneficios">
                <li>✓ Sem anúncios</li>
                <li>✓ Simulações ilimitadas</li>
                <li>✓ Exportação ilimitada</li>
                <li>✓ Gráficos avançados</li>
                <li>✓ Comparações ilimitadas</li>
            </ul>
            <button class="btn-comprar" onclick="comprarPremium('com.ficalc.premium.mensal')">
                Comprar
            </button>
        </div>
        
        <!-- Plano Anual (mais popular) -->
        <div class="plano destaque">
            <span class="badge">Mais Popular!</span>
            <h2>🎯 Premium Anual</h2>
            <p class="preco">R$ 49,90</p>
            <p class="periodo">por ano</p>
            <p class="economia">58% de economia</p>
            <ul class="beneficios">
                <li>✓ Sem anúncios</li>
                <li>✓ Simulações ilimitadas</li>
                <li>✓ Exportação ilimitada</li>
                <li>✓ Gráficos avançados</li>
                <li>✓ Comparações ilimitadas</li>
                <li>✓ Suporte prioritário</li>
            </ul>
            <button class="btn-comprar btn-destaque" onclick="comprarPremium('com.ficalc.premium.anual')">
                Comprar Agora
            </button>
        </div>
    </div>
    
    {% endif %}
    
</div>

<script>
function comprarPremium(produtoId) {
    // Em app nativa (Android/iOS):
    // window.webkit.messageHandlers.iniciarCompra.postMessage({
    //     'produto': produtoId
    // });
    
    // Em web (com Google Play Billing):
    // fetch('/api/comprar/', {
    //     method: 'POST',
    //     body: JSON.stringify({produto: produtoId})
    // })
}
</script>

{% endblock %}
```

---

## 🧪 TESTES

### Teste Unitário AdMob

```python
# simulacao/tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from simulacao.monetizacao import AdMobManager, PremiumManager

class TesteAdMob(TestCase):
    
    def setUp(self):
        self.usuario = User.objects.create_user('testuser', 'test@example.com', 'pass')
    
    def test_usuario_gratis_ve_anuncios(self):
        ad_mgr = AdMobManager(self.usuario)
        self.assertFalse(ad_mgr.eh_premium)
        
        banner_id = ad_mgr.obter_id_anuncio('banner')
        self.assertIsNotNone(banner_id)
    
    def test_usuario_premium_nao_ve_anuncios(self):
        pm = PremiumManager(self.usuario)
        pm.ativar_premium('premium_mensal')
        
        ad_mgr = AdMobManager(self.usuario)
        self.assertTrue(ad_mgr.eh_premium)
        
        banner_id = ad_mgr.obter_id_anuncio('banner')
        self.assertIsNone(banner_id)

class TestePremium(TestCase):
    
    def setUp(self):
        self.usuario = User.objects.create_user('testuser', 'test@example.com', 'pass')
        self.pm = PremiumManager(self.usuario)
    
    def test_usuario_gratis_tem_limites(self):
        self.assertFalse(self.pm.eh_premium())
        
        # Pode fazer 5 simulações
        for i in range(5):
            self.assertTrue(self.pm.pode_fazer_simulacao())
        
        # 6ª simulação bloqueada
        self.assertFalse(self.pm.pode_fazer_simulacao())
    
    def test_usuario_premium_sem_limites(self):
        self.pm.ativar_premium('premium_mensal')
        self.assertTrue(self.pm.eh_premium())
        
        # Pode fazer unlimited
        for i in range(100):
            self.assertTrue(self.pm.pode_fazer_simulacao())
```

### Teste Manual

```bash
# Django shell
python manage.py shell

from django.contrib.auth.models import User
from simulacao.monetizacao import PremiumManager

usuario = User.objects.get(username='seu_usuario')
pm = PremiumManager(usuario)

# Testar Premium
pm.ativar_premium('premium_mensal')
print(pm.obter_status())

# Testar Limites
print(f"Pode exportar: {pm.pode_exportar_excel()}")
print(f"Pode simular: {pm.pode_fazer_simulacao()}")
```

---

## 📋 FAQ

### P: Como ganho dinheiro com AdMob?

**R:** Google paga quando usuários:
- **Veem anúncios** (CPM - por 1.000 impressões): $0.25-8.00
- **Clicam em anúncios** (CPC - por clique): $0.05-0.50
- **Convertem** (CPA - por conversão): Variável

Estimativa: Com 10.000 usuários ativos, ganho **R$ 2.000-5.000/mês** em AdMob.

### P: Qual é minha comissão de Premium?

**R:** Google Play e App Store ficam com 30%, você fica com 70%.

- Premium Mensal R$ 9,90 → Você recebe R$ 6,93
- Premium Anual R$ 49,90 → Você recebe R$ 34,93

### P: Como validar receipts em produção?

**R:** Use as APIs oficiais:
- **Google Play**: https://developers.google.com/play/billing/billing_library_overview
- **App Store**: https://developer.apple.com/app-store/receipt-validation/

### P: Os IDs de teste do AdMob funcionam em produção?

**R:** Não! Mudar para IDs reais após publicar. IDs de teste mostram anúncios de teste.

### P: Posso usar AdMob e AdSense ao mesmo tempo?

**R:** Não na mesma página. Escolha um:
- **Mobile app**: Usar AdMob
- **Web**: Usar AdSense ou AdMob

### P: Como monitoro ganhos?

**R:** Em https://admob.google.com e https://appstoreconnect.apple.com (relatórios).

---

## 🎯 CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Adicionar modelos a `simulacao/models.py`
- [ ] Executar migrations
- [ ] Configurar `settings.py`
- [ ] Criar URLs de API
- [ ] Implementar views
- [ ] Adicionar middleware
- [ ] Atualizar templates
- [ ] Testar localmente com IDs de teste
- [ ] Publicar no Google Play
- [ ] Publicar no App Store
- [ ] Ativar AdMob com IDs reais
- [ ] Monitorar ganhos

---

**Sucesso! 💰🚀**

Qualquer dúvida, consulte:
- [Google AdMob Docs](https://support.google.com/admob)
- [Google Play Billing Docs](https://developer.android.com/google-play/billing)
- [App Store Small Business Program](https://developer.apple.com/app-store/small-business-program/)
