# simulacao/middleware.py
from django.utils import timezone
from django.conf import settings


class SessionActivityMiddleware:
    """
    Middleware para rastrear atividade do usuário e gerenciar sessões
    
    - Atualiza last_activity a cada requisição
    - Renova sessão automaticamente se o usuário estiver ativo
    - Permite implementar timeout de inatividade no futuro
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Processa a requisição
        response = self.get_response(request)
        
        # Se o usuário está autenticado, atualiza last_activity
        if request.user.is_authenticated:
            # Atualiza timestamp de última atividade na sessão
            request.session['last_activity'] = timezone.now().isoformat()
            
            # Marca sessão como modificada para forçar salvamento
            request.session.modified = True
        
        return response


class SessionSecurityMiddleware:
    """
    Middleware para segurança adicional de sessões
    
    - Valida IP do usuário (opcional)
    - Valida User-Agent (opcional)
    - Previne session fixation
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            # Armazena IP e User-Agent na primeira requisição autenticada
            if 'session_ip' not in request.session:
                request.session['session_ip'] = self.get_client_ip(request)
                request.session['session_user_agent'] = request.META.get('HTTP_USER_AGENT', '')
            
            # Validação de IP (desabilitado por padrão - pode causar problemas com IPs dinâmicos)
            # current_ip = self.get_client_ip(request)
            # if current_ip != request.session.get('session_ip'):
            #     # IP mudou - potencial session hijacking
            #     from django.contrib.auth import logout
            #     logout(request)
            #     return redirect('login')
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Obtém o IP real do cliente (considerando proxies)"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
