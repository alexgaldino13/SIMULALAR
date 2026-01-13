# D:\projetos\fi\simulacao\urls.py
from django.urls import path
from . import views 
from . import wizard_views

urlpatterns = [
    path('', views.simulacao_view, name='simulacao_principal'),
    
    # URLs do Wizard
    path('wizard/', wizard_views.wizard_view, name='wizard_inicio'),
    path('wizard/step/<int:step>/', wizard_views.wizard_view, name='wizard_step'),
    path('wizard/back/<int:step>/', wizard_views.wizard_back, name='wizard_back'),
    path('wizard/reset/', wizard_views.wizard_reset, name='wizard_reset'),
    path('wizard/resultados/', wizard_views.wizard_resultados, name='wizard_resultados'),
    # Dynamic wizard (client-driven)
    path('wizard/dynamic/', wizard_views.wizard_dynamic_view, name='wizard_dynamic'),
    path('wizard/api/questions/', wizard_views.wizard_api_questions, name='wizard_api_questions'),
    path('wizard/api/submit/', wizard_views.wizard_api_submit, name='wizard_api_submit'),
]