from django.urls import path
from . import views

urlpatterns = [
    # Wizard — endpoint principal do app mobile
    path('wizard/calculate/', views.wizard_calculate_api, name='api_wizard_calculate'),

    # Calculadoras avulsas
    path('calcular-price-sac/', views.calcular_price_sac_api, name='api_calcular_price_sac'),
    path('simular-consorcio/', views.simular_consorcio_api, name='api_simular_consorcio'),
    path('calcular-cet/', views.calcular_cet_api, name='api_calcular_cet'),
    path('comparar-cenarios/', views.comparar_cenarios_api, name='api_comparar_cenarios'),
    path('parametros/', views.parametros_mercado_api, name='api_parametros_mercado'),

    # Atualização automática de índices BCB (Railway cron)
    path('admin/atualizar-indices/', views.atualizar_indices_bcb_api, name='api_atualizar_indices'),

    # Simulações salvas (requer autenticação)
    path('simulacoes/', views.saved_simulations_api, name='api_saved_simulations'),
    path('simulacoes/<int:pk>/', views.saved_simulation_detail_api, name='api_saved_simulation_detail'),
]
