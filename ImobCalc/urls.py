# D:\projetos\fi\ImobCalc\urls.py
from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')), 
    path('', include('simulacao.urls')), # <--- Esta linha é a raiz
]