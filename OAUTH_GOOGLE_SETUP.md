# Configuração do OAuth Google para ImobCalc

## Status Atual
✅ **CONCLUÍDO**: Infraestrutura OAuth Google configurada no Django

## O que foi feito

### 1. Instalação de Dependências
- ✅ PyJWT instalado
- ✅ cryptography instalado
- ✅ Pillow instalado (necessário para ImageField do avatar)

### 2. Configuração do Django

#### settings.py
```python
INSTALLED_APPS = [
    # ...
    'allauth.socialaccount.providers.google',  # OAuth Google
]

# Configurações de OAuth Social (Google, Apple, etc.)
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': 'SEU_GOOGLE_CLIENT_ID',
            'secret': 'SEU_GOOGLE_CLIENT_SECRET',
            'key': ''
        }
    }
}

SOCIALACCOUNT_AUTO_SIGNUP = True  # Cria conta automaticamente no primeiro login social
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'  # Email já verificado pelo provider
```

#### urls.py
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # Já configurado
    path('', include('simulacao.urls')),
]
```

### 3. Migrações
- ✅ Todas as migrações aplicadas com sucesso
- ✅ Tabelas do socialaccount criadas no banco de dados

## Próximos Passos para Ativar o OAuth Google

### Passo 1: Criar Projeto no Google Cloud Console

1. Acesse: https://console.cloud.google.com/
2. Crie um novo projeto ou selecione um existente
3. Nome sugerido: "ImobCalc"

### Passo 2: Ativar a Google+ API

1. No menu lateral, vá em: **APIs e Serviços > Biblioteca**
2. Procure por: "Google+ API" ou "Google Identity"
3. Clique em **Ativar**

### Passo 3: Criar Credenciais OAuth 2.0

1. Vá em: **APIs e Serviços > Credenciais**
2. Clique em: **+ CRIAR CREDENCIAIS > ID do cliente OAuth 2.0**
3. Tipo de aplicativo: **Aplicativo da Web**
4. Nome: "ImobCalc Web Client"
5. **URIs de redirecionamento autorizados**:
   ```
   http://127.0.0.1:8000/accounts/google/login/callback/
   http://localhost:8000/accounts/google/login/callback/
   ```
   
   Para produção, adicionar:
   ```
   https://seudominio.com/accounts/google/login/callback/
   ```

6. Clique em **Criar**
7. **IMPORTANTE**: Copie o **Client ID** e o **Client Secret**

### Passo 4: Configurar no Django Admin

1. Acesse: http://127.0.0.1:8000/admin/
2. Login: `admin` / `admin123456`
3. Vá em: **Sites > Sites**
4. Edite o site existente:
   - Domain name: `127.0.0.1:8000` (desenvolvimento) ou `seudominio.com` (produção)
   - Display name: `ImobCalc`

5. Vá em: **Social accounts > Social applications**
6. Clique em **Add Social Application**
7. Preencha:
   - Provider: **Google**
   - Name: **Google OAuth**
   - Client id: *cole o Client ID do Google*
   - Secret key: *cole o Client Secret do Google*
   - Sites: Selecione o site "ImobCalc" e mova para "Chosen sites"
8. Clique em **Save**

### Passo 5: Testar o Login

1. Acesse: http://127.0.0.1:8000/accounts/login/
2. Você deverá ver um botão "Sign in with Google"
3. Clique e teste o fluxo de autenticação

## URLs Importantes

- **Login**: http://127.0.0.1:8000/accounts/login/
- **Logout**: http://127.0.0.1:8000/accounts/logout/
- **Signup**: http://127.0.0.1:8000/accounts/signup/
- **Google Login**: http://127.0.0.1:8000/accounts/google/login/
- **Admin**: http://127.0.0.1:8000/admin/

## Estrutura de Dados

### Models Criados

1. **CustomUser** (estende AbstractUser)
   - telefone
   - data_nascimento
   - tipo_conta (FREE/PREMIUM)
   - premium_expira_em
   - aceitou_termos
   - aceitou_privacidade

2. **UserProfile**
   - user (OneToOne com CustomUser)
   - cpf
   - renda_mensal
   - avatar
   - notificacoes_email
   - notificacoes_push

3. **SavedSimulation**
   - user (ForeignKey)
   - nome
   - dados_wizard (JSON)
   - resultados (JSON)
   - criado_em
   - atualizado_em

4. **SimulationShare**
   - simulation (ForeignKey)
   - token (UUID)
   - criado_em
   - expira_em

## Segurança

### Para Produção

1. **Mover credenciais para variáveis de ambiente**:
   ```python
   import os
   
   SOCIALACCOUNT_PROVIDERS = {
       'google': {
           'APP': {
               'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
               'secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
           }
       }
   }
   ```

2. **Atualizar SECRET_KEY**:
   ```python
   SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
   ```

3. **Desabilitar DEBUG**:
   ```python
   DEBUG = False
   ```

4. **Configurar ALLOWED_HOSTS**:
   ```python
   ALLOWED_HOSTS = ['seudominio.com', 'www.seudominio.com']
   ```

## Troubleshooting

### Erro: "redirect_uri_mismatch"
- Verifique se a URI de redirecionamento no Google Cloud Console está exatamente igual à configurada
- Certifique-se de incluir a barra final: `/accounts/google/login/callback/`

### Erro: "Site matching query does not exist"
- Configure o Site no Django Admin (passo 4 acima)
- Verifique se o SITE_ID no settings.py está correto

### Botão "Sign in with Google" não aparece
- Verifique se a Social Application foi criada no Django Admin
- Certifique-se de que o site foi adicionado em "Chosen sites"

## Referências

- Django Allauth: https://django-allauth.readthedocs.io/
- Google OAuth 2.0: https://developers.google.com/identity/protocols/oauth2
- Google Cloud Console: https://console.cloud.google.com/
