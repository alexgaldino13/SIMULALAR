# simulacao/partnership_admin.py
"""
Admin customizado para Sistema de Parcerias
Interface administrativa para gerenciar parceiros e leads
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
import json

from .partnership_models import Partnership, Lead


class LeadInline(admin.TabularInline):
    """Inline para visualizar leads de um parceiro."""
    model = Lead
    extra = 0
    fields = ('nome_completo', 'email', 'telefone', 'valor_imovel', 'status', 'criado_em')
    readonly_fields = ('nome_completo', 'email', 'telefone', 'valor_imovel', 'status', 'criado_em')
    can_delete = False
    max_num = 5
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Partnership)
class PartnershipAdmin(admin.ModelAdmin):
    """Admin customizado para Parceiros."""
    
    list_display = (
        'nome_badge',
        'tipo',
        'status_badge',
        'total_leads_badge',
        'taxa_conversao_badge',
        'valor_gerado_badge',
        'criado_em',
        'acoes'
    )
    
    list_filter = (
        'tipo',
        'status',
        'criado_em',
        'webhook_ativo',
    )
    
    search_fields = (
        'nome',
        'nome_fantasia',
        'cnpj',
        'email_contato',
    )
    
    readonly_fields = (
        'id',
        'api_key',
        'total_leads_recebidos',
        'total_leads_convertidos',
        'taxa_conversao',
        'criado_em',
        'atualizado_em',
        'estatisticas_detalhadas',
        'grafico_conversao',
    )
    
    fieldsets = (
        ('Identificação', {
            'fields': (
                'id',
                'nome',
                'nome_fantasia',
                'cnpj',
                'tipo',
                'status',
            )
        }),
        ('Contato', {
            'fields': (
                'email_contato',
                'telefone',
                'site',
            )
        }),
        ('Endereço', {
            'fields': (
                'endereco',
                'cidade',
                'estado',
                'cep',
            ),
            'classes': ('collapse',)
        }),
        ('Integração', {
            'fields': (
                'api_key',
                'webhook_url',
                'webhook_ativo',
            )
        }),
        ('Valores e Comissões', {
            'fields': (
                'valor_por_lead',
                'comissao_conversao',
            )
        }),
        ('Filtros de Leads', {
            'fields': (
                'valor_minimo_imovel',
                'valor_maximo_imovel',
                'estados_atendidos',
            ),
            'classes': ('collapse',)
        }),
        ('Estatísticas', {
            'fields': (
                'total_leads_recebidos',
                'total_leads_convertidos',
                'taxa_conversao',
                'estatisticas_detalhadas',
                'grafico_conversao',
            )
        }),
        ('Observações', {
            'fields': (
                'observacoes',
            ),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': (
                'criado_em',
                'atualizado_em',
                'criado_por',
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [LeadInline]
    
    def nome_badge(self, obj):
        """Nome com badge do tipo."""
        return format_html(
            '<strong>{}</strong><br><small style="color: #666;">{}</small>',
            obj.nome,
            obj.cnpj
        )
    nome_badge.short_description = 'Parceiro'
    
    def status_badge(self, obj):
        """Badge colorido para status."""
        colors = {
            'ATIVO': '#28a745',
            'INATIVO': '#6c757d',
            'SUSPENSO': '#dc3545',
            'EM_ANALISE': '#ffc107',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def total_leads_badge(self, obj):
        """Badge com total de leads."""
        return format_html(
            '<span style="font-size: 18px; font-weight: bold; color: #007bff;">{}</span><br><small style="color: #666;">{} convertidos</small>',
            obj.total_leads_recebidos,
            obj.total_leads_convertidos
        )
    total_leads_badge.short_description = 'Leads'
    
    def taxa_conversao_badge(self, obj):
        """Badge com taxa de conversão."""
        taxa = float(obj.taxa_conversao)
        color = '#28a745' if taxa >= 10 else '#ffc107' if taxa >= 5 else '#dc3545'
        return format_html(
            '<span style="font-size: 18px; font-weight: bold; color: {};">{:.1f}%</span>',
            color,
            taxa
        )
    taxa_conversao_badge.short_description = 'Conversão'
    
    def valor_gerado_badge(self, obj):
        """Badge com valor total gerado."""
        leads_convertidos = obj.leads.filter(status='CONVERTIDO')
        valor_total = leads_convertidos.aggregate(Sum('comissao_gerada'))['comissao_gerada__sum'] or 0
        return format_html(
            '<span style="font-size: 16px; font-weight: bold; color: #28a745;">R$ {:.2f}</span><br><small style="color: #666;">em comissões</small>',
            valor_total
        )
    valor_gerado_badge.short_description = 'Valor Gerado'
    
    def acoes(self, obj):
        """Botões de ação."""
        return format_html(
            '<a class="button" href="{}">Ver Leads</a> '
            '<a class="button" href="{}">Relatório</a>',
            reverse('admin:simulacao_lead_changelist') + f'?parceiro__id__exact={obj.id}',
            reverse('admin:simulacao_partnership_change', args=[obj.id]) + '#estatisticas'
        )
    acoes.short_description = 'Ações'
    
    def estatisticas_detalhadas(self, obj):
        """Estatísticas detalhadas do parceiro."""
        if not obj.id:
            return '-'
        
        # Últimos 30 dias
        data_inicio = timezone.now() - timedelta(days=30)
        leads_30d = obj.leads.filter(criado_em__gte=data_inicio)
        
        # Estatísticas por status
        stats_status = obj.leads.values('status').annotate(total=Count('id')).order_by('-total')
        
        # Tempo médio de conversão
        leads_convertidos = obj.leads.filter(status='CONVERTIDO', convertido_em__isnull=False)
        tempo_medio = None
        if leads_convertidos.exists():
            tempos = [(lead.convertido_em - lead.criado_em).days for lead in leads_convertidos]
            tempo_medio = sum(tempos) / len(tempos)
        
        # Valor médio de negócio
        valor_medio = leads_convertidos.aggregate(Avg('valor_negocio'))['valor_negocio__avg'] or 0
        
        html = f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
            <h3 style="margin-top: 0;">📊 Estatísticas Detalhadas</h3>
            
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px;">
                <div style="background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff;">
                    <div style="font-size: 24px; font-weight: bold; color: #007bff;">{leads_30d.count()}</div>
                    <div style="color: #666; font-size: 12px;">Leads (últimos 30 dias)</div>
                </div>
                <div style="background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745;">
                    <div style="font-size: 24px; font-weight: bold; color: #28a745;">R$ {valor_medio:,.2f}</div>
                    <div style="color: #666; font-size: 12px;">Valor Médio de Negócio</div>
                </div>
                <div style="background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
                    <div style="font-size: 24px; font-weight: bold; color: #ffc107;">{tempo_medio:.1f if tempo_medio else 0} dias</div>
                    <div style="color: #666; font-size: 12px;">Tempo Médio de Conversão</div>
                </div>
            </div>
            
            <h4>Leads por Status:</h4>
            <table style="width: 100%; background: white; border-collapse: collapse;">
                <thead>
                    <tr style="background: #e9ecef;">
                        <th style="padding: 8px; text-align: left;">Status</th>
                        <th style="padding: 8px; text-align: right;">Quantidade</th>
                        <th style="padding: 8px; text-align: right;">Percentual</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        total = obj.total_leads_recebidos or 1
        for stat in stats_status:
            percentual = (stat['total'] / total) * 100
            status_display = dict(Lead.STATUS_CHOICES).get(stat['status'], stat['status'])
            html += f"""
                    <tr>
                        <td style="padding: 8px;">{status_display}</td>
                        <td style="padding: 8px; text-align: right; font-weight: bold;">{stat['total']}</td>
                        <td style="padding: 8px; text-align: right;">{percentual:.1f}%</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        return mark_safe(html)
    estatisticas_detalhadas.short_description = 'Estatísticas Detalhadas'
    
    def grafico_conversao(self, obj):
        """Gráfico de conversão dos últimos 12 meses."""
        if not obj.id:
            return '-'
        
        # Dados dos últimos 12 meses
        meses = []
        leads_por_mes = []
        conversoes_por_mes = []
        
        for i in range(11, -1, -1):
            data_inicio = timezone.now() - timedelta(days=30*i)
            data_fim = timezone.now() - timedelta(days=30*(i-1)) if i > 0 else timezone.now()
            
            leads = obj.leads.filter(criado_em__gte=data_inicio, criado_em__lt=data_fim)
            conversoes = leads.filter(status='CONVERTIDO')
            
            meses.append(data_inicio.strftime('%b/%y'))
            leads_por_mes.append(leads.count())
            conversoes_por_mes.append(conversoes.count())
        
        html = f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
            <h3 style="margin-top: 0;">📈 Evolução (Últimos 12 Meses)</h3>
            <div style="background: white; padding: 20px; border-radius: 5px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #e9ecef;">
                            <th style="padding: 8px; text-align: left;">Mês</th>
                            <th style="padding: 8px; text-align: right;">Leads</th>
                            <th style="padding: 8px; text-align: right;">Conversões</th>
                            <th style="padding: 8px; text-align: right;">Taxa</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for i, mes in enumerate(meses):
            leads = leads_por_mes[i]
            conversoes = conversoes_por_mes[i]
            taxa = (conversoes / leads * 100) if leads > 0 else 0
            
            html += f"""
                        <tr>
                            <td style="padding: 8px;">{mes}</td>
                            <td style="padding: 8px; text-align: right;">{leads}</td>
                            <td style="padding: 8px; text-align: right; font-weight: bold; color: #28a745;">{conversoes}</td>
                            <td style="padding: 8px; text-align: right;">{taxa:.1f}%</td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
        </div>
        """
        
        return mark_safe(html)
    grafico_conversao.short_description = 'Gráfico de Evolução'
    
    def save_model(self, request, obj, form, change):
        """Salva o modelo e define o criador."""
        if not change:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['ativar_parceiros', 'desativar_parceiros', 'atualizar_estatisticas']
    
    def ativar_parceiros(self, request, queryset):
        """Ativa parceiros selecionados."""
        updated = queryset.update(status='ATIVO')
        self.message_user(request, f'{updated} parceiro(s) ativado(s) com sucesso.')
    ativar_parceiros.short_description = 'Ativar parceiros selecionados'
    
    def desativar_parceiros(self, request, queryset):
        """Desativa parceiros selecionados."""
        updated = queryset.update(status='INATIVO')
        self.message_user(request, f'{updated} parceiro(s) desativado(s) com sucesso.')
    desativar_parceiros.short_description = 'Desativar parceiros selecionados'
    
    def atualizar_estatisticas(self, request, queryset):
        """Atualiza estatísticas dos parceiros selecionados."""
        for parceiro in queryset:
            parceiro.atualizar_estatisticas()
        self.message_user(request, f'Estatísticas de {queryset.count()} parceiro(s) atualizadas.')
    atualizar_estatisticas.short_description = 'Atualizar estatísticas'


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    """Admin customizado para Leads."""
    
    list_display = (
        'nome_completo',
        'parceiro',
        'status_badge',
        'origem',
        'valor_imovel_badge',
        'cidade_estado',
        'criado_em',
        'tempo_conversao',
        'acoes'
    )
    
    list_filter = (
        'status',
        'origem',
        'parceiro',
        'criado_em',
        'estado_interesse',
    )
    
    search_fields = (
        'nome_completo',
        'email',
        'telefone',
        'cidade_interesse',
    )
    
    readonly_fields = (
        'id',
        'usuario',
        'criado_em',
        'atualizado_em',
        'enviado_em',
        'visualizado_em',
        'primeiro_contato_em',
        'convertido_em',
        'tempo_conversao',
        'dados_simulacao_formatados',
    )
    
    fieldsets = (
        ('Identificação', {
            'fields': (
                'id',
                'usuario',
                'parceiro',
                'status',
                'origem',
            )
        }),
        ('Dados do Lead', {
            'fields': (
                'nome_completo',
                'email',
                'telefone',
                'cpf_criptografado',
            )
        }),
        ('Dados do Imóvel', {
            'fields': (
                'valor_imovel',
                'valor_entrada',
                'cidade_interesse',
                'estado_interesse',
            )
        }),
        ('Dados Financeiros', {
            'fields': (
                'renda_mensal',
                'fgts_disponivel',
            ),
            'classes': ('collapse',)
        }),
        ('Preferências', {
            'fields': (
                'cenario_preferido',
                'observacoes_usuario',
            ),
            'classes': ('collapse',)
        }),
        ('Dados da Simulação', {
            'fields': (
                'dados_simulacao_formatados',
            ),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': (
                'enviado_em',
                'visualizado_em',
                'primeiro_contato_em',
                'convertido_em',
                'tempo_conversao',
            )
        }),
        ('Conversão', {
            'fields': (
                'valor_negocio',
                'comissao_gerada',
            ),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': (
                'ip_origem',
                'user_agent',
                'criado_em',
                'atualizado_em',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Badge colorido para status."""
        colors = {
            'NOVO': '#17a2b8',
            'ENVIADO': '#007bff',
            'EM_CONTATO': '#ffc107',
            'QUALIFICADO': '#20c997',
            'NEGOCIACAO': '#fd7e14',
            'CONVERTIDO': '#28a745',
            'PERDIDO': '#dc3545',
            'INVALIDO': '#6c757d',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def valor_imovel_badge(self, obj):
        """Badge com valor do imóvel."""
        return format_html(
            '<span style="font-weight: bold; color: #28a745;">R$ {:.2f}</span>',
            obj.valor_imovel
        )
    valor_imovel_badge.short_description = 'Valor do Imóvel'
    
    def cidade_estado(self, obj):
        """Cidade e estado."""
        if obj.cidade_interesse and obj.estado_interesse:
            return f"{obj.cidade_interesse}/{obj.estado_interesse}"
        return '-'
    cidade_estado.short_description = 'Localização'
    
    def tempo_conversao(self, obj):
        """Tempo até conversão."""
        tempo = obj.tempo_ate_conversao()
        if tempo is not None:
            return format_html(
                '<span style="font-weight: bold; color: #28a745;">{} dias</span>',
                tempo
            )
        return '-'
    tempo_conversao.short_description = 'Tempo de Conversão'
    
    def acoes(self, obj):
        """Botões de ação."""
        return format_html(
            '<a class="button" href="mailto:{}">Email</a> '
            '<a class="button" href="tel:{}">Ligar</a>',
            obj.email,
            obj.telefone
        )
    acoes.short_description = 'Ações'
    
    def dados_simulacao_formatados(self, obj):
        """Dados da simulação formatados."""
        if not obj.dados_simulacao:
            return '-'
        
        try:
            dados = obj.dados_simulacao if isinstance(obj.dados_simulacao, dict) else json.loads(obj.dados_simulacao)
            html = '<div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">'
            html += '<h4 style="margin-top: 0;">Dados da Simulação:</h4>'
            html += '<table style="width: 100%; background: white;">'
            
            for key, value in dados.items():
                html += f'<tr><td style="padding: 5px; font-weight: bold;">{key}:</td><td style="padding: 5px;">{value}</td></tr>'
            
            html += '</table></div>'
            return mark_safe(html)
        except:
            return str(obj.dados_simulacao)
    dados_simulacao_formatados.short_description = 'Dados da Simulação'
    
    actions = ['marcar_como_enviado', 'marcar_como_qualificado', 'marcar_como_perdido']
    
    def marcar_como_enviado(self, request, queryset):
        """Marca leads como enviados."""
        for lead in queryset:
            lead.marcar_como_enviado()
        self.message_user(request, f'{queryset.count()} lead(s) marcado(s) como enviado(s).')
    marcar_como_enviado.short_description = 'Marcar como enviado'
    
    def marcar_como_qualificado(self, request, queryset):
        """Marca leads como qualificados."""
        updated = queryset.update(status='QUALIFICADO')
        self.message_user(request, f'{updated} lead(s) marcado(s) como qualificado(s).')
    marcar_como_qualificado.short_description = 'Marcar como qualificado'
    
    def marcar_como_perdido(self, request, queryset):
        """Marca leads como perdidos."""
        updated = queryset.update(status='PERDIDO')
        self.message_user(request, f'{updated} lead(s) marcado(s) como perdido(s).')
    marcar_como_perdido.short_description = 'Marcar como perdido'
