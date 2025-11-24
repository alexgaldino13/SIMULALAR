# simulacao/urls.py

from django.urls import path
from . import views 

urlpatterns = [
    # Mapeia a URL vazia (rota principal) para a nossa função
    path('', views.simular_financiamento, name='simulacao_principal'),
]