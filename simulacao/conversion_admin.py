# simulacao/conversion_admin.py
"""
Admin para Sistema de Tracking de Conversão
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .conversion_tracking import ConversionEvent, LeadAlert


@admin.register(ConversionEvent)
class ConversionEventAdmin(admin.ModelAdmin):
    """
    Admin para visualizar eventos de conversão.
    """
    
    list_display = [
        'tipo_evento_badge',
        'lead_link',
        'parceiro_link',
        'usuario_responsavel',
        'criado_em_formatado',
    ]
    
    list_filter = [
        'tipo_evento',
        'parceiro',
        'criado_em',
    ]
    
    search_fields = [
        'lead__nome_completo',
        'lead__email',
        'parceiro__nome',
        'descricao',
    ]
    
    readonly_fields = [
        'id',
        'lead',
        'parceiro',
        'tipo_evento',
        'descricao',
        'dados_adicionais',
        'usuario_responsavel',
        'ip_origem',
        'criado_em',
    ]
    
    fieldsets = [
        ('Informações do Evento', {
            'fields': ['id', 'tipo_evento', 'descricao']
        }),
        ('Relacionamentos', {
            'fields': ['lead', 'parceiro', 'usuario_responsavel']
        }),
        ('Dados Adicionais', {
            'fields': ['dados_adicionais', 'ip_origem'],
            'classes': ['collapse']
        }),
        ('Metadados', {
            'fields': ['criado_em'],
            'classes': ['collapse']
        }),
    ]
    
    date_hierarchy = 'criado_em'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def tipo_evento_badge(self, obj):
        """Badge colorido para o tipo de evento."""
        cores = {
            'LEAD_CRIADO': '#3498db',
            'LEAD_ENVIADO': '#9b59b6',
            'LEAD_VISUALIZADO': '#1abc9c',
            'PRIMEIRO_CONTATO': '#f39c12',
            'LEAD_QUALIFICADO': '#2ecc71',
            'PROPOSTA_ENVIADA': '#e67e22',
            'PROPOSTA_ACEITA': '#27ae60',
            'CONVERTIDO': '#27ae60',
            'PERDIDO': '#e74c3c',
            'INVALIDO': '#95a5a6',
        }
        cor = cores.get(obj.tipo_evento, '#34495e')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 3px; font-weight: bold; font-size: 11px;">{}</span>',
            cor,
            obj.get_tipo_evento_display()
        )
    tipo_evento_badge.short_description = 'Tipo de Evento'
    
    def lead_link(self, obj):
        """Link para o lead."""
        url = reverse('admin:simulacao_lead_change', args=[obj.lead.id])
        return format_html('<a href="{}">{}</a>', url, obj.lead.nome_completo)
    lead_link.short_description = 'Lead'
    
    def parceiro_link(self, obj):
        """Link para o parceiro."""
        url = reverse('admin:simulacao_partnership_change', args=[obj.parceiro.id])
        return format_html('<a href="{}">{}</a>', url, obj.parceiro.nome)
    parceiro_link.short_description = 'Parceiro'
    
    def criado_em_formatado(self, obj):
        """Data formatada."""
        return obj.criado_em.strftime('%d/%m/%Y %H:%M')
    criado_em_formatado.short_description = 'Data/Hora'


@admin.register(LeadAlert)
class LeadAlertAdmin(admin.ModelAdmin):
    """
    Admin para gerenciar alertas de leads.
    """
    
    list_display = [
        'tipo_alerta_badge',
        'prioridade_badge',
        'lead_link',
        'parceiro_link',
        'dias_sem_atividade',
        'status_badge',
        'notificacao_enviada_icon',
        'criado_em_formatado',
        'acoes',
    ]
    
    list_filter = [
        'tipo_alerta',
        'prioridade',
        'status',
        'notificacao_enviada',
        'parceiro',
        'criado_em',
    ]
    
    search_fields = [
        'lead__nome_completo',
        'lead__email',
        'parceiro__nome',
        'mensagem',
    ]
    
    readonly_fields = [
        'id',
        'lead',
        'parceiro',
        'tipo_alerta',
        'mensagem',
        'dias_sem_atividade',
        'notificacao_enviada',
        'notificacao_enviada_em',
        'criado_em',
        'atualizado_em',
    ]
    
    fieldsets = [
        ('Informações do Alerta', {
            'fields': ['id', 'tipo_alerta', 'prioridade', 'status', 'mensagem', 'recomendacao']
        }),
        ('Relacionamentos', {
            'fields': ['lead', 'parceiro']
        }),
        ('Tracking', {
            'fields': ['dias_sem_atividade', 'notificacao_enviada', 'notificacao_enviada_em']
        }),
        ('Resolução', {
            'fields': ['resolvido_por', 'resolvido_em', 'observacoes_resolucao'],
            'classes': ['collapse']
        }),
        ('Metadados', {
            'fields': ['criado_em', 'atualizado_em'],
            'classes': ['collapse']
        }),
    ]
    
    actions = [
        'marcar_como_resolvido',
        'marcar_como_ignorado',
        'enviar_notificacoes',
    ]
    
    date_hierarchy = 'criado_em'
    
    def has_add_permission(self, request):
        return False
    
    def tipo_alerta_badge(self, obj):
        """Badge colorido para o tipo de alerta."""
        cores = {
            'LEAD_PARADO': '#e67e22',
            'SEM_CONTATO': '#e74c3c',
            'SEM_FOLLOWUP': '#f39c12',
            'DOCUMENTOS_PENDENTES': '#3498db',
            'PROPOSTA_SEM_RESPOSTA': '#9b59b6',
            'RISCO_PERDA': '#c0392b',
            'OPORTUNIDADE': '#27ae60',
        }
        cor = cores.get(obj.tipo_alerta, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 3px; font-weight: bold; font-size: 11px;">{}</span>',
            cor,
            obj.get_tipo_alerta_display()
        )
    tipo_alerta_badge.short_description = 'Tipo'
    
    def prioridade_badge(self, obj):
        """Badge colorido para a prioridade."""
        cores = {
            'BAIXA': '#95a5a6',
            'MEDIA': '#3498db',
            'ALTA': '#e67e22',
            'URGENTE': '#e74c3c',
        }
        cor = cores.get(obj.prioridade, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-weight: bold; font-size: 10px;">{}</span>',
            cor,
            obj.get_prioridade_display()
        )
    prioridade_badge.short_description = 'Prioridade'
    
    def status_badge(self, obj):
        """Badge colorido para o status."""
        cores = {
            'ATIVO': '#e74c3c',
            'RESOLVIDO': '#27ae60',
            'IGNORADO': '#95a5a6',
        }
        cor = cores.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-weight: bold; font-size: 10px;">{}</span>',
            cor,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def notificacao_enviada_icon(self, obj):
        """Ícone indicando se a notificação foi enviada."""
        if obj.notificacao_enviada:
            return format_html(
                '<span style="color: #27ae60; font-size: 16px;" title="Notificação enviada em {}">✔</span>',
                obj.notificacao_enviada_em.strftime('%d/%m/%Y %H:%M') if obj.notificacao_enviada_em else 'N/A'
            )
        return format_html('<span style="color: #e74c3c; font-size: 16px;" title="Notificação não enviada">✘</span>')
    notificacao_enviada_icon.short_description = 'Notif.'
    
    def lead_link(self, obj):
        """Link para o lead."""
        url = reverse('admin:simulacao_lead_change', args=[obj.lead.id])
        return format_html('<a href="{}">{}</a>', url, obj.lead.nome_completo)
    lead_link.short_description = 'Lead'
    
    def parceiro_link(self, obj):
        """Link para o parceiro."""
        url = reverse('admin:simulacao_partnership_change', args=[obj.parceiro.id])
        return format_html('<a href="{}">{}</a>', url, obj.parceiro.nome)
    parceiro_link.short_description = 'Parceiro'
    
    def criado_em_formatado(self, obj):
        """Data formatada."""
        return obj.criado_em.strftime('%d/%m/%Y %H:%M')
    criado_em_formatado.short_description = 'Criado em'
    
    def acoes(self, obj):
        """Botões de ação."""
        if obj.status == 'ATIVO':
            return format_html(
                '<a class="button" href="#" onclick="return confirm(\'Marcar como resolvido?\');">Resolver</a> '
                '<a class="button" href="#" onclick="return confirm(\'Ignorar alerta?\');">Ignorar</a>'
            )
        return '-'
    acoes.short_description = 'Ações'
    
    def marcar_como_resolvido(self, request, queryset):
        """Marca alertas selecionados como resolvidos."""
        count = 0
        for alerta in queryset.filter(status='ATIVO'):
            alerta.marcar_como_resolvido(request.user, "Resolvido via ação em massa")
            count += 1
        self.message_user(request, f"{count} alerta(s) marcado(s) como resolvido(s).")
    marcar_como_resolvido.short_description = "Marcar como resolvido"
    
    def marcar_como_ignorado(self, request, queryset):
        """Marca alertas selecionados como ignorados."""
        count = queryset.filter(status='ATIVO').update(status='IGNORADO')
        self.message_user(request, f"{count} alerta(s) marcado(s) como ignorado(s).")
    marcar_como_ignorado.short_description = "Marcar como ignorado"
    
    def enviar_notificacoes(self, request, queryset):
        """Envia notificações para os alertas selecionados."""
        count = 0
        for alerta in queryset.filter(notificacao_enviada=False, status='ATIVO'):
            if alerta.enviar_notificacao():
                count += 1
        self.message_user(request, f"{count} notificação(ões) enviada(s).")
    enviar_notificacoes.short_description = "Enviar notificações"
