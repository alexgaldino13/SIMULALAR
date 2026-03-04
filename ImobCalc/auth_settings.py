# ImobCalc/auth_settings.py
# Configurações adicionais de autenticação
# Importar este arquivo no settings.py principal

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Configurações de Autenticação Customizada
# ----------------------------------------------------------------------

# Define o modelo de usuário customizado
AUTH_USER_MODEL = 'simulacao.CustomUser'

# URL de login
LOGIN_URL = '/accounts/login/'

# Configurações de Email (para desenvolvimento - console backend)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Para produção, usar SMTP real:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'seu-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'sua-senha-de-app'
# DEFAULT_FROM_EMAIL = 'ImobCalc <noreply@imobcalc.com>'

# Configurações de Mídia (para uploads de avatar, etc.)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configurações de Sessão
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600  # 14 dias em segundos
SESSION_SAVE_EVERY_REQUEST = False

# Configurações Allauth adicionais
ACCOUNT_EMAIL_VERIFICATION = "optional"  # Mudado para optional durante desenvolvimento
