# simulacao/auth_views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser, UserProfile
from django.db import transaction


def login_view(request):
    """
    View para login de usuários
    Suporta login tradicional (email/senha) e OAuth (Google)
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        # Autentica o usuário
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            
            # Configura duração da sessão baseado em "Manter-me conectado"
            if remember_me:
                # 30 dias se marcou "Manter-me conectado"
                request.session.set_expiry(settings.SESSION_COOKIE_AGE_REMEMBER_ME)
            else:
                # 14 dias (padrão) se não marcou
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            
            messages.success(request, f'Bem-vindo de volta, {user.first_name or user.email}!')
            
            # Redireciona para a página solicitada ou dashboard
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Email ou senha incorretos. Tente novamente.')
    
    context = {
        'next': request.GET.get('next', ''),
    }
    return render(request, 'simulacao/auth/login.html', context)


def register_view(request):
    """
    View para registro de novos usuários
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        telefone = request.POST.get('telefone', '')
        aceito_termos = request.POST.get('aceito_termos')
        aceito_privacidade = request.POST.get('aceito_privacidade')
        
        # Validações
        if not email or not password:
            messages.error(request, 'Email e senha são obrigatórios.')
        elif password != password_confirm:
            messages.error(request, 'As senhas não coincidem.')
        elif len(password) < 8:
            messages.error(request, 'A senha deve ter pelo menos 8 caracteres.')
        elif not aceito_termos or not aceito_privacidade:
            messages.error(request, 'Você deve aceitar os Termos de Uso e a Política de Privacidade.')
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Este email já está cadastrado.')
        else:
            try:
                with transaction.atomic():
                    # Cria o usuário
                    user = CustomUser.objects.create_user(
                        username=email,  # Usa email como username
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        telefone=telefone,
                        aceitou_termos=True,
                        aceitou_privacidade=True,
                    )
                    
                    # Cria o perfil do usuário
                    UserProfile.objects.create(user=user)
                    
                    # Faz login automaticamente
                    login(request, user)
                    
                    messages.success(request, f'Conta criada com sucesso! Bem-vindo, {first_name}!')
                    return redirect('dashboard')
                    
            except Exception as e:
                messages.error(request, f'Erro ao criar conta: {str(e)}')
    
    return render(request, 'simulacao/auth/register.html')


def logout_view(request):
    """
    View para logout de usuários
    """
    logout(request)
    messages.success(request, 'Você saiu da sua conta com sucesso.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """
    Dashboard do usuário logado
    Mostra simulações salvas, estatísticas e acesso rápido
    """
    user = request.user
    
    # Busca simulações salvas do usuário
    simulacoes_salvas = user.saved_simulations.all().order_by('-criado_em')[:5]
    
    # Estatísticas
    total_simulacoes = user.saved_simulations.count()
    
    context = {
        'user': user,
        'simulacoes_salvas': simulacoes_salvas,
        'total_simulacoes': total_simulacoes,
        'is_premium': user.tipo_conta == 'PREMIUM',
    }
    
    return render(request, 'simulacao/auth/dashboard.html', context)


@login_required
def profile_view(request):
    """
    View para editar perfil do usuário
    """
    user = request.user
    profile = user.profile
    
    if request.method == 'POST':
        # Atualiza dados do usuário
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.telefone = request.POST.get('telefone', user.telefone)
        
        # Atualiza dados do perfil
        profile.cpf = request.POST.get('cpf', profile.cpf)
        profile.renda_mensal = request.POST.get('renda_mensal', profile.renda_mensal)
        
        # Atualiza preferências de notificação
        profile.notificacoes_email = request.POST.get('notificacoes_email') == 'on'
        profile.notificacoes_push = request.POST.get('notificacoes_push') == 'on'
        
        try:
            user.save()
            profile.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar perfil: {str(e)}')
        
        return redirect('profile')
    
    context = {
        'user': user,
        'profile': profile,
    }
    
    return render(request, 'simulacao/auth/profile.html', context)


def password_reset_request_view(request):
    """
    View para solicitar recuperação de senha
    Envia email com link para resetar senha
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = CustomUser.objects.get(email=email)
            
            # Gera token de recuperação
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Cria link de recuperação
            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            # Envia email
            subject = 'ImobCalc - Recuperação de Senha'
            message = f'''Olá {user.first_name or user.email},

Você solicitou a recuperação de senha da sua conta no ImobCalc.

Clique no link abaixo para criar uma nova senha:
{reset_link}

Este link é válido por 24 horas.

Se você não solicitou esta recuperação, ignore este email.

Atenciosamente,
Equipe ImobCalc
'''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Enviamos um email com instruções para recuperar sua senha.')
            return redirect('login')
            
        except CustomUser.DoesNotExist:
            # Por segurança, não revela se o email existe ou não
            messages.success(request, 'Se este email estiver cadastrado, você receberá instruções para recuperar sua senha.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Erro ao enviar email: {str(e)}')
    
    return render(request, 'simulacao/auth/password_reset_request.html')


def password_reset_confirm_view(request, uidb64, token):
    """
    View para confirmar e resetar a senha
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')
            
            if password != password_confirm:
                messages.error(request, 'As senhas não coincidem.')
            elif len(password) < 8:
                messages.error(request, 'A senha deve ter pelo menos 8 caracteres.')
            else:
                user.set_password(password)
                user.save()
                messages.success(request, 'Senha alterada com sucesso! Faça login com sua nova senha.')
                return redirect('login')
        
        context = {
            'validlink': True,
            'uidb64': uidb64,
            'token': token,
        }
        return render(request, 'simulacao/auth/password_reset_confirm.html', context)
    else:
        messages.error(request, 'Link de recuperação inválido ou expirado.')
        return redirect('password_reset_request')


def direct_dashboard_view(request):
    """
    View para redirecionar diretamente ao dashboard sem autenticação.
    """
    return render(request, 'simulacao/auth/dashboard.html', {})
