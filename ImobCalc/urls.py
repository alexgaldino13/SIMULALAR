# D:\projetos\fi\ImobCalc\urls.py
from django.contrib import admin
from django.urls import path, include 

from django.views.generic import RedirectView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
        path('', RedirectView.as_view(url='/wizard/', permanent=False)),
path('api/v1/', include('simulacao.partnership_urls')),  # API de Parcerias 
    path('', include('simulacao.urls')), # <--- Esta linha é a raiz
]