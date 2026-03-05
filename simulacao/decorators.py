from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .subscription_models import Subscription

def premium_required(view_func):
    """
    Decorator para views que requerem assinatura Premium ativa.
    Verifica se o usuário tem uma assinatura com status 'ATIVA' e se a data de expiração é válida.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Por favor, faça login para acessar recursos Premium.")
            return redirect('account_login')
        
        # Verifica se existe alguma assinatura ativa
        has_active_subscription = False
        subscriptions = Subscription.objects.filter(usuario=request.user, status='ATIVA')
        
        for sub in subscriptions:
            if sub.esta_ativa():
                has_active_subscription = True
                break
        
        if not has_active_subscription:
            messages.warning(request, "Este recurso é exclusivo para assinantes Premium.")
            # Redireciona para o dashboard (futuramente para a página de upgrade)
            return redirect('dashboard')
            
        return view_func(request, *args, **kwargs)
        
    return _wrapped_view