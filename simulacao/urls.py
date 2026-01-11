# D:\projetos\fi\simulacao\urls.py
from django.urls import path
from . import views 

urlpatterns = [
    path('', views.simulacao_view, name='simulacao_principal'), 
]