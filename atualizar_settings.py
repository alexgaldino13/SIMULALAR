# Script para atualizar settings.py com configurações de autenticação

import os

settings_path = r'd:\projetos\FI\ImobCalc\settings.py'

# Ler o arquivo atual
with open(settings_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar configurações no final do arquivo
novas_configs = '''

# Configurações de Autenticação Customizada
# ----------------------------------------------------------------------

# Define o modelo de usuário customizado
AUTH_USER_MODEL = 'simulacao.CustomUser'

# URL de login
LOGIN_URL = '/accounts/login/'

# Configurações de Email (para desenvolvimento - console backend)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Configurações de Mídia (para uploads de avatar, etc.)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configurações de Sessão
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600  # 14 dias em segundos
SESSION_SAVE_EVERY_REQUEST = False
'''

# Verificar se já existe AUTH_USER_MODEL
if 'AUTH_USER_MODEL' not in content:
    # Adicionar as novas configurações
    content += novas_configs
    
    # Salvar o arquivo atualizado
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\u2705 Settings.py atualizado com sucesso!")
else:
    print("⚠️ AUTH_USER_MODEL já existe no settings.py")

print("\nConfigurações adicionadas:")
print(novas_configs)
