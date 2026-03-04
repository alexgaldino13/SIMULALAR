# D:\projetos\fi\simulacao\urls.py
from django.urls import path
from . import views 
from . import wizard_views
from . import wizard_views_novo
from . import wizard_views_v2
from . import auth_views
from . import lgpd_views

urlpatterns = [
    # URLs de Autenticação
    path('login/', auth_views.login_view, name='login'),
    path('register/', auth_views.register_view, name='register'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', auth_views.profile_view, name='profile'),
    
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
    #python manage.py runserver
    # path('', wizard_views_v2.wizard_v2, name='simulacao_principal'),
    
    # URLs do Wizard V2 (versão reorganizada com IA)
    path('wizard-v2/', wizard_views_v2.wizard_v2, name='wizard_v2'),
    path('wizard-v2/<int:step>/', wizard_views_v2.wizard_v2, name='wizard_v2_step'),
    path('wizard-v2/resultados/', wizard_views_v2.wizard_v2_resultados, name='wizard_v2_resultados'),
    path('wizard-v2/reset/', wizard_views_v2.wizard_v2_reset, name='wizard_v2_reset'),
    
    # URLs do Wizard NOVO (refatorado)
    path('wizard-novo/', wizard_views_novo.wizard_novo, name='wizard_novo'),
    path('wizard-novo/<int:step>/', wizard_views_novo.wizard_novo, name='wizard_novo_step'),
    path('wizard-novo/resultados/', wizard_views_novo.wizard_novo_resultados, name='wizard_novo_resultados'),
    path('wizard-novo/reset/', wizard_views_novo.wizard_novo_reset, name='wizard_novo_reset'),
    path('wizard-novo/salvar/', wizard_views_novo.salvar_simulacao, name='wizard_novo_salvar'),
    path('wizard-novo/exportar-pdf/', wizard_views_novo.exportar_pdf_simulacao, name='wizard_novo_exportar_pdf'),
    path('intro/', wizard_views_novo.wizard_onboarding, name='wizard_onboarding'),
    
    # URLs do Wizard (original)
    path('wizard/', wizard_views.wizard_view, name='wizard_inicio'),
    path('wizard/step/<int:step>/', wizard_views.wizard_view, name='wizard_step'),
    path('wizard/back/<int:step>/', wizard_views.wizard_back, name='wizard_back'),
    path('wizard/reset/', wizard_views.wizard_reset, name='wizard_reset'),
    path('wizard/resultados/', wizard_views.wizard_resultados, name='wizard_resultados'),
    # Dynamic wizard (client-driven)
    path('wizard/dynamic/', wizard_views.wizard_dynamic_view, name='wizard_dynamic'),
    path('wizard/api/questions/', wizard_views.wizard_api_questions, name='wizard_api_questions'),
    path('wizard/api/submit/', wizard_views.wizard_api_submit, name='wizard_api_submit'),
    
    # Rota para acesso direto ao dashboard
    path('direct-dashboard/', auth_views.direct_dashboard_view, name='direct_dashboard'),
    
    # API para autocomplete de cidades
    path('api/cidades/', wizard_views.api_cidades, name='api_cidades'),

    # Cenário 6: Investidor Imobiliário
    path('investidor-imobiliario/', views.investidor_imobiliario_view, name='investidor_imobiliario'),
        path('comparador-investimentos/', views.comparador_investimentos_view, name='comparador_investimentos'),
]