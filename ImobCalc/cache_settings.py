# ==============================================================================
# OTIMIZAÇÃO DE PERFORMANCE - Item 5.6
# ==============================================================================
# Este arquivo contém as configurações de cache para o projeto ImobCalc.
# Para ativar, adicione ao final do settings.py:
# from .cache_settings import *

# Cache de arquivos estáticos (usar hash nos nomes para cache busting)
from .settings import DEBUG

if not DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
    
    # Cache middleware (adicionar ao MIDDLEWARE existente)
    # MIDDLEWARE.insert(1, 'django.middleware.cache.UpdateCacheMiddleware')
    # MIDDLEWARE.append('django.middleware.cache.FetchFromCacheMiddleware')
    
    # Configurações de cache
    CACHE_MIDDLEWARE_ALIAS = 'default'
    CACHE_MIDDLEWARE_SECONDS = 86400  # 24 horas
    CACHE_MIDDLEWARE_KEY_PREFIX = 'imobcalc'

# Cache backend (usar cache em memória para desenvolvimento)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutos
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}
