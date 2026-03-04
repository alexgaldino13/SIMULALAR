from django.db import models
from django.conf import settings
from django.utils import timezone
import json


class ConsentManagement(models.Model):
    """
    Model para gerenciar consentimentos LGPD dos usuários.
    Registra todos os consentimentos dados pelo usuário para diferentes finalidades.
    """
    
    # Tipos de consentimento
    CONSENT_TYPES = [
        ('TERMS', 'Termos de Uso'),
        ('PRIVACY', 'Política de Privacidade'),
        ('DATA_SHARING', 'Compartilhamento de Dados'),
        ('MARKETING', 'Comunicações de Marketing'),
        ('ANALYTICS', 'Análise de Dados'),
        ('PARTNERSHIP_CONSORCIO', 'Parceria - Consórcio'),
        ('PARTNERSHIP_CORRETORA', 'Parceria - Corretora'),
        ('PARTNERSHIP_BANCO', 'Parceria - Banco'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='consents',
        verbose_name='Usuário'
    )
    
    consent_type = models.CharField(
        max_length=50,
        choices=CONSENT_TYPES,
        verbose_name='Tipo de Consentimento'
    )
    
    granted = models.BooleanField(
        default=False,
        verbose_name='Consentimento Concedido'
    )
    
    granted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Concessão'
    )
    
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Revogação'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Endereço IP'
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    
    consent_text = models.TextField(
        verbose_name='Texto do Consentimento',
        help_text='Versão exata do texto apresentado ao usuário'
    )
    
    consent_version = models.CharField(
        max_length=20,
        verbose_name='Versão do Consentimento',
        help_text='Ex: 1.0, 1.1, 2.0'
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Metadados',
        help_text='Informações adicionais sobre o consentimento'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )
    
    class Meta:
        verbose_name = 'Consentimento'
        verbose_name_plural = 'Consentimentos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'consent_type']),
            models.Index(fields=['granted', 'consent_type']),
        ]
    
    def __str__(self):
        status = 'Concedido' if self.granted else 'Revogado'
        return f"{self.user.email} - {self.get_consent_type_display()} - {status}"
    
    def grant_consent(self, ip_address=None, user_agent=None):
        """Concede o consentimento"""
        self.granted = True
        self.granted_at = timezone.now()
        self.revoked_at = None
        if ip_address:
            self.ip_address = ip_address
        if user_agent:
            self.user_agent = user_agent
        self.save()
    
    def revoke_consent(self):
        """Revoga o consentimento"""
        self.granted = False
        self.revoked_at = timezone.now()
        self.save()
    
    @classmethod
    def has_consent(cls, user, consent_type):
        """Verifica se o usuário tem um consentimento ativo"""
        return cls.objects.filter(
            user=user,
            consent_type=consent_type,
            granted=True,
            revoked_at__isnull=True
        ).exists()
    
    @classmethod
    def get_active_consents(cls, user):
        """Retorna todos os consentimentos ativos do usuário"""
        return cls.objects.filter(
            user=user,
            granted=True,
            revoked_at__isnull=True
        )


class DataAccessLog(models.Model):
    """
    Model para registrar todos os acessos a dados sensíveis.
    Fundamental para auditoria LGPD.
    """
    
    ACCESS_TYPES = [
        ('READ', 'Leitura'),
        ('CREATE', 'Criação'),
        ('UPDATE', 'Atualização'),
        ('DELETE', 'Exclusão'),
        ('EXPORT', 'Exportação'),
        ('SHARE', 'Compartilhamento'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='data_access_logs',
        verbose_name='Usuário'
    )
    
    accessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='data_accesses_made',
        verbose_name='Acessado por',
        help_text='Quem acessou os dados (pode ser o próprio usuário ou admin)'
    )
    
    access_type = models.CharField(
        max_length=20,
        choices=ACCESS_TYPES,
        verbose_name='Tipo de Acesso'
    )
    
    data_type = models.CharField(
        max_length=100,
        verbose_name='Tipo de Dado',
        help_text='Ex: CPF, Renda, Simulação, Perfil'
    )
    
    description = models.TextField(
        verbose_name='Descrição',
        help_text='Descrição detalhada da operação'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Endereço IP'
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Metadados',
        help_text='Informações adicionais sobre o acesso'
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data/Hora'
    )
    
    class Meta:
        verbose_name = 'Log de Acesso a Dados'
        verbose_name_plural = 'Logs de Acesso a Dados'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['accessed_by', 'timestamp']),
            models.Index(fields=['access_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_access_type_display()} - {self.data_type} - {self.timestamp}"
    
    @classmethod
    def log_access(cls, user, accessed_by, access_type, data_type, description, 
                   ip_address=None, user_agent=None, metadata=None):
        """Método helper para criar logs de acesso"""
        return cls.objects.create(
            user=user,
            accessed_by=accessed_by,
            access_type=access_type,
            data_type=data_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {}
        )


class DataDeletionRequest(models.Model):
    """
    Model para gerenciar solicitações de exclusão de dados (direito ao esquecimento).
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('IN_PROGRESS', 'Em Andamento'),
        ('COMPLETED', 'Concluída'),
        ('CANCELLED', 'Cancelada'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deletion_requests',
        verbose_name='Usuário'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name='Status'
    )
    
    reason = models.TextField(
        blank=True,
        verbose_name='Motivo',
        help_text='Motivo da solicitação de exclusão'
    )
    
    requested_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Solicitado em'
    )
    
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Processado em'
    )
    
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deletion_requests_processed',
        verbose_name='Processado por'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Observações',
        help_text='Observações sobre o processamento'
    )
    
    class Meta:
        verbose_name = 'Solicitação de Exclusão'
        verbose_name_plural = 'Solicitações de Exclusão'
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_status_display()} - {self.requested_at}"
    
    def mark_completed(self, processed_by, notes=''):
        """Marca a solicitação como concluída"""
        self.status = 'COMPLETED'
        self.processed_at = timezone.now()
        self.processed_by = processed_by
        self.notes = notes
        self.save()
