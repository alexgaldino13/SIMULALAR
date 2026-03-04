# Configuração do OAuth Apple (Sign in with Apple) para ImobCalc

## Status Atual
⚠️ **PENDENTE**: Infraestrutura básica preparada, aguardando configuração completa

## Pré-requisitos

1. **Conta Apple Developer** (US$ 99/ano)
   - Necessária para criar App IDs e Service IDs
   - Link: https://developer.apple.com/programs/

2. **Domínio verificado**
   - Apple requer um domínio verificado para OAuth
   - Para desenvolvimento, pode usar localhost com configurações especiais

## Passos para Implementação

### Passo 1: Instalar Provider Apple no Django

```bash
pip install django-allauth[socialaccount]
```

### Passo 2: Adicionar ao settings.py

```python
INSTALLED_APPS = [
    # ...
    'allauth.socialaccount.providers.apple',  # OAuth Apple
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # ... configuração existente
    },
    'apple': {
        'APP': {
            'client_id': 'com.imobcalc.service',  # Service ID
            'secret': 'SEU_APPLE_CLIENT_SECRET',  # Gerado via chave privada
            'key': 'SEU_APPLE_KEY_ID',  # Key ID da Apple
            'certificate_key': '''-----BEGIN PRIVATE KEY-----
SUA_CHAVE_PRIVADA_AQUI
-----END PRIVATE KEY-----''',
            'team': 'SEU_TEAM_ID',  # Team ID da Apple Developer
        },
        'SCOPE': ['name', 'email'],
    }
}
```

### Passo 3: Criar App ID no Apple Developer

1. Acesse: https://developer.apple.com/account/resources/identifiers/list
2. Clique em **+** para criar novo identificador
3. Selecione **App IDs** e clique em **Continue**
4. Selecione **App** e clique em **Continue**
5. Preencha:
   - Description: `ImobCalc`
   - Bundle ID: `com.imobcalc.app` (Explicit)
6. Em **Capabilities**, marque:
   - **Sign in with Apple**
7. Clique em **Continue** e depois **Register**

### Passo 4: Criar Service ID

1. Na mesma página de identificadores, clique em **+**
2. Selecione **Services IDs** e clique em **Continue**
3. Preencha:
   - Description: `ImobCalc Web Service`
   - Identifier: `com.imobcalc.service`
4. Marque **Sign in with Apple**
5. Clique em **Configure** ao lado de "Sign in with Apple"
6. Preencha:
   - Primary App ID: Selecione `com.imobcalc.app`
   - Domains and Subdomains: `seudominio.com` (ou `127.0.0.1` para dev)
   - Return URLs: `https://seudominio.com/accounts/apple/login/callback/`
     - Para desenvolvimento: `http://127.0.0.1:8000/accounts/apple/login/callback/`
7. Clique em **Save**, depois **Continue** e **Register**

### Passo 5: Criar Chave Privada (Private Key)

1. Vá em: https://developer.apple.com/account/resources/authkeys/list
2. Clique em **+** para criar nova chave
3. Preencha:
   - Key Name: `ImobCalc Sign in with Apple Key`
4. Marque **Sign in with Apple**
5. Clique em **Configure** e selecione o Primary App ID: `com.imobcalc.app`
6. Clique em **Save**, depois **Continue** e **Register**
7. **IMPORTANTE**: Faça download da chave (.p8 file)
   - Você só pode fazer download UMA VEZ
   - Guarde em local seguro
8. Anote o **Key ID** (ex: `ABC123DEFG`)

### Passo 6: Obter Team ID

1. Acesse: https://developer.apple.com/account/
2. No canto superior direito, você verá seu **Team ID** (ex: `XYZ987HIJK`)
3. Anote este ID

### Passo 7: Gerar Client Secret (JWT)

O Apple OAuth requer um JWT (JSON Web Token) como client secret. Este token deve ser gerado programaticamente.

**Opção 1: Usar script Python**

```python
import jwt
import time
from pathlib import Path

# Configurações
TEAM_ID = 'SEU_TEAM_ID'
KEY_ID = 'SEU_KEY_ID'
CLIENT_ID = 'com.imobcalc.service'
KEY_FILE = 'AuthKey_ABC123DEFG.p8'  # Arquivo baixado

# Ler chave privada
with open(KEY_FILE, 'r') as f:
    private_key = f.read()

# Gerar JWT
headers = {
    'kid': KEY_ID,
    'alg': 'ES256'
}

payload = {
    'iss': TEAM_ID,
    'iat': int(time.time()),
    'exp': int(time.time()) + 86400 * 180,  # 6 meses
    'aud': 'https://appleid.apple.com',
    'sub': CLIENT_ID
}

client_secret = jwt.encode(payload, private_key, algorithm='ES256', headers=headers)
print(f'Client Secret: {client_secret}')
```

**Opção 2: Deixar o django-allauth gerar automaticamente**

O django-allauth pode gerar o JWT automaticamente se você fornecer a chave privada no settings.py.

### Passo 8: Configurar no Django Admin

1. Acesse: http://127.0.0.1:8000/admin/
2. Vá em: **Social accounts > Social applications**
3. Clique em **Add Social Application**
4. Preencha:
   - Provider: **Apple**
   - Name: **Apple Sign In**
   - Client id: `com.imobcalc.service`
   - Secret key: *JWT gerado ou deixe vazio se usar certificate_key*
   - Key: *Key ID da Apple*
   - Sites: Selecione o site "ImobCalc"
5. Clique em **Save**

### Passo 9: Testar o Login

1. Acesse: http://127.0.0.1:8000/accounts/login/
2. Você deverá ver um botão "Sign in with Apple"
3. Clique e teste o fluxo de autenticação

## Diferenças entre Apple e Google OAuth

### Apple
- Requer conta Developer paga (US$ 99/ano)
- Usa JWT como client secret (mais complexo)
- Requer chave privada (.p8)
- Usuário pode ocultar email (Apple gera email proxy)
- Obrigatório para apps iOS que usam login social

### Google
- Gratuito
- Client secret estático (mais simples)
- Não requer chaves adicionais
- Email sempre visível
- Opcional para apps

## Considerações Importantes

### Email Oculto (Hide My Email)

Quando usuários escolhem "Hide My Email", a Apple gera um email proxy:
- Formato: `abc123@privaterelay.appleid.com`
- Emails enviados para este endereço são encaminhados para o email real do usuário
- Você deve aceitar e processar estes emails normalmente

### Nome do Usuário

- Apple envia nome completo apenas no **primeiro login**
- Logins subsequentes não incluem o nome
- Você deve salvar o nome no primeiro login

### Revogação de Acesso

- Usuários podem revogar acesso em: Settings > Apple ID > Password & Security > Apps Using Apple ID
- Seu app deve lidar com tokens revogados graciosamente

## URLs Importantes

- **Apple Developer**: https://developer.apple.com/
- **Identifiers**: https://developer.apple.com/account/resources/identifiers/list
- **Keys**: https://developer.apple.com/account/resources/authkeys/list
- **Sign in with Apple Docs**: https://developer.apple.com/sign-in-with-apple/
- **Django Allauth Apple**: https://django-allauth.readthedocs.io/en/latest/providers.html#apple

## Troubleshooting

### Erro: "invalid_client"
- Verifique se o Service ID está correto
- Certifique-se de que o JWT foi gerado corretamente
- Verifique se o Team ID e Key ID estão corretos

### Erro: "invalid_request"
- Verifique se a Return URL está configurada corretamente no Service ID
- Certifique-se de incluir a barra final: `/accounts/apple/login/callback/`

### JWT expirado
- JWTs para Apple OAuth expiram após 6 meses
- Você precisa gerar um novo JWT periodicamente
- Considere automatizar este processo

## Alternativa: Adiar para Fase Mobile

Como o Sign in with Apple é:
1. Mais complexo de configurar
2. Requer conta Developer paga
3. Mais relevante para apps iOS

**Sugestão**: Implementar na **Fase 7 (Encapsulamento Mobile)** quando:
- Tivermos conta Apple Developer ativa
- Estivermos preparando o app iOS
- For obrigatório para publicação na App Store

Por enquanto, focar em:
- Login tradicional (email/senha) ✅
- Google OAuth ✅
- Interface de login/registro (Fase 1.6)

## Próximos Passos Recomendados

1. **Agora**: Pular para item 1.6 (Criar telas de login/registro)
2. **Depois**: Implementar recuperação de senha (1.7)
3. **Fase Mobile**: Retornar ao OAuth Apple quando necessário
