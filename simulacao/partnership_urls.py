# simulacao/partnership_urls.py
"""
URLs para API de Parcerias
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .partnership_api import (
    PartnershipViewSet,
    LeadViewSet,
    api_health,
    webhook_receiver
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'partnerships', PartnershipViewSet, basename='partnership')
router.register(r'leads', LeadViewSet, basename='lead')

app_name = 'partnership_api'

urlpatterns = [
    # Health check
    path('health/', api_health, name='health'),
    
    # Webhook
    path('webhook/', webhook_receiver, name='webhook'),
    
    # Router URLs
    path('', include(router.urls)),
]
