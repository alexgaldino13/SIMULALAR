# D:\projetos\fi\simulacao\urls.py
from django.urls import path
from . import views 
from . import wizard_views_v2
from . import auth_views
from . import lgpd_views 
from .monetizacao_views import SubscriptionStatusView, AdViewTrackingView, GooglePlayBillingWebhookView

urlpatterns = [
    # URLs de Autenticação
    path('login/', auth_views.login_view, name='login'),
    path('register/', auth_views.register_view, name='register'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', auth_views.profile_view, name='profile'),
    path('upgrade/', views.upgrade_premium_view, name='upgrade_premium'),
    
    # URLs de Recuperação de Senha
    path('password-reset/', auth_views.password_reset_request_view, name='password_reset_request'),
    path('password-reset/<uidb64>/<token>/', auth_views.password_reset_confirm_view, name='password_reset_confirm'),
    
    # URLs LGPD
    path('consent/', lgpd_views.consent_view, name='consent'),
    path('privacy-settings/', lgpd_views.privacy_settings_view, name='privacy_settings'),
    path('revoke-consent/<str:consent_type>/', lgpd_views.revoke_consent_view, name='revoke_consent'),
    path('request-deletion/', lgpd_views.request_data_deletion_view, name='request_deletion'),
    path('export-data/', lgpd_views.export_data_view, name='export_data'),
    path('terms/', lgpd_views.terms_of_service_view, name='terms_of_service'),
    path('privacy/', lgpd_views.privacy_policy_view, name='privacy_policy'),
    path('audit-logs/', lgpd_views.audit_logs_view, name='audit_logs'),
    
    # Redireciona direto para o Wizard V2 (nova versão)
    path('', wizard_views_v2.wizard_v2, name='simulacao_principal'),
    
    # URLs do Wizard V2 (versão reorganizada com IA)
    path('wizard-v2/', wizard_views_v2.wizard_v2, name='wizard_v2'),
    path('wizard-v2/<int:step>/', wizard_views_v2.wizard_v2, name='wizard_v2_step'),
    path('wizard-v2/resultados/', wizard_views_v2.wizard_v2_resultados, name='wizard_v2_resultados'),
    path('wizard-v2/reset/', wizard_views_v2.wizard_v2_reset, name='wizard_v2_reset'),
    path('wizard-v2/salvar/', wizard_views_v2.salvar_simulacao_v2, name='wizard_v2_salvar'),
    path('wizard-v2/exportar-pdf/', wizard_views_v2.exportar_pdf_simulacao_v2, name='wizard_v2_exportar_pdf'),
        
    # Rota para acesso direto ao dashboard
    path('direct-dashboard/', auth_views.direct_dashboard_view, name='direct_dashboard'),

    # Cenário 6: Investidor Imobiliário
    path('investidor-imobiliario/', views.investidor_imobiliario_view, name='investidor_imobiliario'),
        path('comparador-investimentos/', views.comparador_investimentos_view, name='comparador_investimentos'),

    # Exportação (Premium)
    path('exportar/excel/<int:sim_id>/', views.exportar_simulacao_excel, name='exportar_excel'),
    path('exportar/pdf/<int:sim_id>/', views.exportar_simulacao_pdf, name='exportar_pdf'),
            
    # APIs para AdMob/Monetizacao
    path('api/assinaturas/status/', SubscriptionStatusView.as_view(), name='api_assinatura_status'),
    path('api/monetizacao/ad-view/', AdViewTrackingView.as_view(), name='api_registrar_ad_view'),
    path('api/monetizacao/google-play-billing-webhook/', GooglePlayBillingWebhookView.as_view(), name='api_google_play_billing_webhook'),

    path('afiliado/<int:link_id>/', views.redirecionar_afiliado, name='redirecionar_afiliado'),
    path('api/afiliados/', views.api_links_afiliados, name='api_links_afiliados'),
]