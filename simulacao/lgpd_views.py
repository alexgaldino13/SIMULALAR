# simulacao/lgpd_views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .lgpd_models import ConsentManagement, DataAccessLog, DataDeletionRequest
import json
from functools import wraps


def get_client_ip(request):
    """Obtém o IP do cliente da requisição."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Obtém o User-Agent da requisição."""
    return request.META.get('HTTP_USER_AGENT', '')


@login_required
def consent_view(request):
    """
    Tela de consentimento LGPD.
    Permite ao usuário gerenciar seus consentimentos.
    """
    if request.method == 'POST':
        # Obter informações da requisição
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        # Processar consentimentos obrigatórios
        consent_terms = request.POST.get('consent_terms') == '1'
        consent_privacy = request.POST.get('consent_privacy') == '1'
        
        # Verificar se os obrigatórios foram aceitos
        if not consent_terms or not consent_privacy:
            messages.error(request, '⚠️ Você precisa aceitar os Termos de Uso e a Política de Privacidade para continuar.')
            return render(request, 'simulacao/lgpd/consent.html')
        
        # Processar consentimentos opcionais
        consent_analytics = request.POST.get('consent_analytics') == '1'
        consent_marketing = request.POST.get('consent_marketing') == '1'
        consent_data_sharing = request.POST.get('consent_data_sharing') == '1'
        consent_partnership_consorcio = request.POST.get('consent_partnership_consorcio') == '1'
        consent_partnership_corretora = request.POST.get('consent_partnership_corretora') == '1'
        consent_partnership_banco = request.POST.get('consent_partnership_banco') == '1'
        
        # Mapear consentimentos
        consents = {
            'TERMS': consent_terms,
            'PRIVACY': consent_privacy,
            'ANALYTICS': consent_analytics,
            'MARKETING': consent_marketing,
            'DATA_SHARING': consent_data_sharing,
            'PARTNERSHIP_CONSORCIO': consent_partnership_consorcio,
            'PARTNERSHIP_CORRETORA': consent_partnership_corretora,
            'PARTNERSHIP_BANCO': consent_partnership_banco,
        }
        
        # Salvar ou atualizar consentimentos
        for consent_type, granted in consents.items():
            # Buscar consentimento existente
            existing_consent = ConsentManagement.objects.filter(
                user=request.user,
                consent_type=consent_type
            ).first()
            
            if existing_consent:
                # Atualizar consentimento existente
                if granted and not existing_consent.granted:
                    # Conceder consentimento
                    existing_consent.grant_consent(
                        ip_address=ip_address,
                        user_agent=user_agent
                    )
                elif not granted and existing_consent.granted:
                    # Revogar consentimento
                    existing_consent.revoke_consent()
            else:
                # Criar novo consentimento
                if granted:
                    ConsentManagement.objects.create(
                        user=request.user,
                        consent_type=consent_type,
                        granted=True,
                        granted_at=timezone.now(),
                        ip_address=ip_address,
                        user_agent=user_agent,
                        consent_version='1.0',
                        consent_text=f'Consentimento para {consent_type}'
                    )
        
        # Registrar log de acesso
        DataAccessLog.log_access(
            user=request.user,
            accessed_by=request.user,
            access_type='UPDATE',
            data_type='CONSENT',
            description='Usuário atualizou preferências de consentimento',
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Atualizar flags no modelo de usuário
        request.user.aceitou_termos = consent_terms
        request.user.aceitou_privacidade = consent_privacy
        request.user.save()
        
        messages.success(request, '✓ Suas preferências de privacidade foram salvas com sucesso!')
        
        # Redirecionar para o dashboard
        return redirect('dashboard')
    
    # GET - Carregar consentimentos existentes
    user_consents = {}
    for consent in ConsentManagement.objects.filter(user=request.user, granted=True):
        user_consents[consent.consent_type] = True
    
    context = {
        'user_consents': user_consents,
    }
    
    return render(request, 'simulacao/lgpd/consent.html', context)


@login_required
def privacy_settings_view(request):
    """
    Tela de configurações de privacidade.
    Permite ao usuário visualizar e gerenciar todos os seus consentimentos.
    """
    # Buscar todos os consentimentos do usuário
    consents = ConsentManagement.objects.filter(user=request.user).order_by('-granted_at')
    
    # Buscar logs de acesso recentes
    access_logs = DataAccessLog.objects.filter(user=request.user).order_by('-accessed_at')[:20]
    
    # Buscar solicitações de exclusão
    deletion_requests = DataDeletionRequest.objects.filter(user=request.user).order_by('-requested_at')
    
    context = {
        'consents': consents,
        'access_logs': access_logs,
        'deletion_requests': deletion_requests,
    }
    
    return render(request, 'simulacao/lgpd/privacy_settings.html', context)


@login_required
def revoke_consent_view(request, consent_type):
    """
    Revogar um consentimento específico.
    """
    if request.method == 'POST':
        try:
            consent = ConsentManagement.objects.get(
                user=request.user,
                consent_type=consent_type,
                granted=True
            )
            consent.revoke_consent()
            
            # Registrar log
            DataAccessLog.log_access(
                user=request.user,
                accessed_by=request.user,
                access_type='UPDATE',
                data_type='CONSENT',
                description=f'Usuário revogou consentimento: {consent_type}',
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request)
            )
            
            messages.success(request, f'✓ Consentimento "{consent.get_consent_type_display()}" revogado com sucesso.')
        except ConsentManagement.DoesNotExist:
            messages.error(request, '⚠️ Consentimento não encontrado.')
    
    return redirect('privacy_settings')


@login_required
def request_data_deletion_view(request):
    """
    Solicitar exclusão de dados (Direito ao Esquecimento - LGPD).
    """
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        # Verificar se já existe uma solicitação pendente
        existing_request = DataDeletionRequest.objects.filter(
            user=request.user,
            status__in=['PENDING', 'IN_PROGRESS']
        ).first()
        
        if existing_request:
            messages.warning(request, '⚠️ Você já possui uma solicitação de exclusão em andamento.')
        else:
            # Criar nova solicitação
            DataDeletionRequest.objects.create(
                user=request.user,
                reason=reason,
                status='PENDING'
            )
            
            # Registrar log
            DataAccessLog.log_access(
                user=request.user,
                accessed_by=request.user,
                access_type='DELETE',
                data_type='USER_DATA',
                description='Usuário solicitou exclusão de dados',
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request)
            )
            
            messages.success(request, '✓ Sua solicitação de exclusão foi registrada. Entraremos em contato em até 30 dias.')
        
        return redirect('privacy_settings')
    
    return render(request, 'simulacao/lgpd/request_deletion.html')


@login_required
def export_data_view(request):
    """
    Exportar dados do usuário (Direito de Portabilidade - LGPD).
    """
    # Coletar todos os dados do usuário
    user_data = {
        'usuario': {
            'nome': request.user.get_full_name(),
            'email': request.user.email,
            'username': request.user.username,
            'telefone': request.user.telefone,
            'data_nascimento': str(request.user.data_nascimento) if request.user.data_nascimento else None,
            'tipo_conta': request.user.tipo_conta,
            'data_cadastro': str(request.user.date_joined),
        },
        'perfil': {},
        'consentimentos': [],
        'simulacoes': [],
        'logs_acesso': [],
    }
    
    # Adicionar perfil se existir
    if hasattr(request.user, 'profile'):
        profile = request.user.profile
        user_data['perfil'] = {
            'cpf': profile.cpf if profile.cpf else None,
            'renda_mensal': str(profile.renda_mensal) if profile.renda_mensal else None,
        }
    
    # Adicionar consentimentos
    for consent in ConsentManagement.objects.filter(user=request.user):
        user_data['consentimentos'].append({
            'tipo': consent.get_consent_type_display(),
            'concedido': consent.granted,
            'data_concessao': str(consent.granted_at) if consent.granted_at else None,
            'data_revogacao': str(consent.revoked_at) if consent.revoked_at else None,
        })
    
    # Adicionar simulações salvas
    from .models import SavedSimulation
    for simulation in SavedSimulation.objects.filter(user=request.user):
        user_data['simulacoes'].append({
            'nome': simulation.nome,
            'criado_em': str(simulation.created_at),
            'atualizado_em': str(simulation.updated_at),
        })
    
    # Adicionar logs de acesso (apenas os últimos 100)
    for log in DataAccessLog.objects.filter(user=request.user).order_by('-accessed_at')[:100]:
        user_data['logs_acesso'].append({
            'tipo_acesso': log.get_access_type_display(),
            'tipo_dado': log.data_type,
            'descricao': log.description,
            'data': str(log.accessed_at),
        })
    
    # Registrar log de exportação
    DataAccessLog.log_access(
        user=request.user,
        accessed_by=request.user,
        access_type='EXPORT',
        data_type='USER_DATA',
        description='Usuário exportou seus dados',
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    # Retornar JSON
    return JsonResponse(user_data, json_dumps_params={'indent': 2, 'ensure_ascii': False})


def terms_of_service_view(request):
    """
    Exibir Termos de Uso.
    """
    return render(request, 'simulacao/lgpd/terms_of_service.html')


def privacy_policy_view(request):
    """
    Exibir Política de Privacidade.
    """
    return render(request, 'simulacao/lgpd/privacy_policy.html')


def audit_log(action_type, data_type, description=None):
    """
    Decorator para registrar automaticamente logs de auditoria.
    
    Uso:
    @audit_log('READ', 'USER_DATA', 'Usuário acessou dashboard')
    def minha_view(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Executar view
            response = view_func(request, *args, **kwargs)
            
            # Registrar log se usuário autenticado
            if request.user.is_authenticated:
                desc = description or f'Acesso via {view_func.__name__}'
                DataAccessLog.log_access(
                    user=request.user,
                    accessed_by=request.user,
                    access_type=action_type,
                    data_type=data_type,
                    description=desc,
                    ip_address=get_client_ip(request),
                    user_agent=get_user_agent(request)
                )
            
            return response
        return wrapper
    return decorator


@login_required
def audit_logs_view(request):
    """
    Exibe logs de auditoria do usuário.
    """
    # Buscar logs do usuário
    logs = DataAccessLog.objects.filter(user=request.user).order_by('-accessed_at')
    
    # Filtros
    access_type = request.GET.get('type')
    if access_type:
        logs = logs.filter(access_type=access_type)
    
    # Paginação (20 por página)
    from django.core.paginator import Paginator
    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'access_types': DataAccessLog.ACCESS_TYPES,
    }
    
    return render(request, 'simulacao/lgpd/audit_logs.html', context)
