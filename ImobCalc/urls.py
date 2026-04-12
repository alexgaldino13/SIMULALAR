# D:\projetos\fi\ImobCalc\urls.py
from django.contrib import admin
from django.urls import path, include 

from rest_framework.authtoken import views as auth_views
from django.views.generic import RedirectView
from simulacao import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/v1/assinatura-status/', views.api_assinatura_status, name='api_assinatura_status'),
    path('api/v1/capturar-lead/', views.api_capturar_lead, name='api_capturar_lead'),
    path('api/v1/ad-view/', views.api_registrar_ad_view, name='api_registrar_ad_view'),
    path('api/v1/', include('simulacao.partnership_urls')),  # API de Parcerias 
    path('api-token-auth/', auth_views.obtain_auth_token), # Token para Mobile
    path('', include('simulacao.urls')), # <--- Esta linha é a raiz
]