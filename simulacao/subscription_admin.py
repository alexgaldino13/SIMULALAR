# simulacao/subscription_admin.py
"""
Admin para Sistema de Assinaturas
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count, Sum, Q
from .subscription_models import SubscriptionPlan, Subscription, Payment, UsageStats


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = [
        'nome',
        'preco_display',
        'duracao',
        'desconto_badge',
        'features_display',
        'total_assinaturas',
        'ativo_badge',
        'destaque_badge',
    ]
    list_filter = ['ativo', 'destaque', 'duracao']
    search_fields = ['nome', 'descricao']
    ordering = ['ordem', 'preco']
    
    fieldsets = [
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'ordem')
        }),
        ('Preço e Duração', {
            'fields': ('preco', 'duracao', 'dias_duracao', 'desconto_percentual')
        }),
        ('Features Incluídas', {
            'fields': (
                'simulacoes_ilimitadas',
                'sem_anuncios',
                'exportacao_excel',
                'exportacao_pdf_premium',
                'suporte_prioritario',
            )
        }),
        ('Status', {
            'fields': ('ativo', 'destaque')
        }),
    ]
    
    def preco_display(self, obj):
        preco_original = obj.preco
        preco_final = obj.preco_com_desconto()
        
        if preco_final < preco_original:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">R$ {:.2f}</span><br>'
                '<strong style="color: #28a745;">R$ {:.2f}</strong>',
                preco_original, preco_final
            )
        return format_html('<strong>R$ {:.2f}</strong>', preco_original)
    preco_display.short_description = 'Preço'
    
    def desconto_badge(self, obj):
        if obj.desconto_percentual > 0:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-weight: bold;">-{:.0f}%</span>',
                obj.desconto_percentual
            )
        return '-'
    desconto_badge.short_description = 'Desconto'
    
    def features_display(self, obj):
        features = []
        if obj.simulacoes_ilimitadas:
            features.append('✅ Ilimitado')
        if obj.sem_anuncios:
            features.append('✅ Sem Ads')
        if obj.exportacao_excel:
            features.append('✅ Excel')
        if obj.exportacao_pdf_premium:
            features.append('✅ PDF Premium')
        if obj.suporte_prioritario:
            features.append('⭐ Suporte VIP')
        
        return format_html('<br>'.join(features))
    features_display.short_description = 'Features'
    
    def total_assinaturas(self, obj):
        total = obj.subscriptions.filter(status='ATIVA').count()
        return format_html(
            '<strong style="color: #007bff;">{}</strong> ativas',
            total
        )
    total_assinaturas.short_description = 'Assinaturas'
    
    def ativo_badge(self, obj):
        if obj.ativo:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; '
                'border-radius: 3px;">✅ Ativo</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 8px; '
            'border-radius: 3px;">❌ Inativo</span>'
        )
    ativo_badge.short_description = 'Status'
    
    def destaque_badge(self, obj):
        if obj.destaque:
            return format_html('⭐ Destaque')
        return '-'
    destaque_badge.short_description = 'Destaque'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'usuario_display',
        'plano',
        'status_badge',
        'valor_pago_display',
        'data_inicio',
        'data_expiracao',
        'dias_restantes_display',
        'renovacao_badge',
    ]
    list_filter = ['status', 'renovacao_automatica', 'plano', 'data_inicio']
    search_fields = ['usuario__email', 'usuario__first_name', 'transaction_id']
    readonly_fields = ['id', 'criado_em', 'atualizado_em']
    date_hierarchy = 'data_inicio'
    
    fieldsets = [
        ('Assinatura', {
            'fields': ('id', 'usuario', 'plano', 'status')
        }),
        ('Datas', {
            'fields': ('data_inicio', 'data_expiracao', 'data_cancelamento')
        }),
        ('Pagamento', {
            'fields': ('valor_pago', 'gateway', 'transaction_id')
        }),
        ('Configurações', {
            'fields': ('renovacao_automatica',)
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    ]
    
    actions = ['ativar_assinaturas', 'cancelar_assinaturas']
    
    def usuario_display(self, obj):
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.usuario.get_full_name() or obj.usuario.email,
            obj.usuario.email
        )
    usuario_display.short_description = 'Usuário'
    
    def status_badge(self, obj):
        colors = {
            'ATIVA': '#28a745',
            'CANCELADA': '#6c757d',
            'EXPIRADA': '#dc3545',
            'SUSPENSA': '#ffc107',
            'PENDENTE': '#17a2b8',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def valor_pago_display(self, obj):
        return format_html(
            '<strong style="color: #28a745;">R$ {:.2f}</strong>',
            obj.valor_pago
        )
    valor_pago_display.short_description = 'Valor Pago'
    
    def dias_restantes_display(self, obj):
        if obj.status != 'ATIVA':
            return '-'
        
        dias = obj.dias_restantes()
        if dias > 30:
            color = '#28a745'
        elif dias > 7:
            color = '#ffc107'
        else:
            color = '#dc3545'
        
        return format_html(
            '<strong style="color: {};">{} dias</strong>',
            color, dias
        )
    dias_restantes_display.short_description = 'Dias Restantes'
    
    def renovacao_badge(self, obj):
        if obj.renovacao_automatica:
            return format_html('✅ Sim')
        return format_html('❌ Não')
    renovacao_badge.short_description = 'Renovação Auto'
    
    def ativar_assinaturas(self, request, queryset):
        for subscription in queryset:
            if subscription.status == 'PENDENTE':
                subscription.ativar()
        self.message_user(request, f"{queryset.count()} assinatura(s) ativada(s).")
    ativar_assinaturas.short_description = "Ativar assinaturas selecionadas"
    
    def cancelar_assinaturas(self, request, queryset):
        queryset.update(status='CANCELADA', renovacao_automatica=False)
        self.message_user(request, f"{queryset.count()} assinatura(s) cancelada(s).")
    cancelar_assinaturas.short_description = "Cancelar assinaturas selecionadas"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id',
        'usuario_display',
        'valor_display',
        'metodo',
        'status_badge',
        'gateway',
        'data_pagamento',
    ]
    list_filter = ['status', 'metodo', 'gateway', 'criado_em']
    search_fields = ['transaction_id', 'usuario__email', 'usuario__first_name']
    readonly_fields = ['id', 'criado_em', 'atualizado_em', 'dados_gateway']
    date_hierarchy = 'criado_em'
    
    fieldsets = [
        ('Pagamento', {
            'fields': ('id', 'subscription', 'usuario', 'valor', 'metodo', 'status')
        }),
        ('Gateway', {
            'fields': ('gateway', 'transaction_id', 'dados_gateway')
        }),
        ('Datas', {
            'fields': ('data_pagamento', 'data_aprovacao')
        }),
        ('Metadados', {
            'fields': ('ip_origem', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    ]
    
    actions = ['aprovar_pagamentos', 'recusar_pagamentos']
    
    def usuario_display(self, obj):
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.usuario.get_full_name() or obj.usuario.email,
            obj.usuario.email
        )
    usuario_display.short_description = 'Usuário'
    
    def valor_display(self, obj):
        return format_html(
            '<strong style="color: #28a745; font-size: 14px;">R$ {:.2f}</strong>',
            obj.valor
        )
    valor_display.short_description = 'Valor'
    
    def status_badge(self, obj):
        colors = {
            'PENDENTE': '#17a2b8',
            'PROCESSANDO': '#ffc107',
            'APROVADO': '#28a745',
            'RECUSADO': '#dc3545',
            'CANCELADO': '#6c757d',
            'REEMBOLSADO': '#fd7e14',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def aprovar_pagamentos(self, request, queryset):
        count = 0
        for payment in queryset:
            if payment.status in ['PENDENTE', 'PROCESSANDO']:
                payment.aprovar()
                count += 1
        self.message_user(request, f"{count} pagamento(s) aprovado(s).")
    aprovar_pagamentos.short_description = "Aprovar pagamentos selecionados"
    
    def recusar_pagamentos(self, request, queryset):
        count = 0
        for payment in queryset:
            if payment.status in ['PENDENTE', 'PROCESSANDO']:
                payment.recusar()
                count += 1
        self.message_user(request, f"{count} pagamento(s) recusado(s).")
    recusar_pagamentos.short_description = "Recusar pagamentos selecionados"


@admin.register(UsageStats)
class UsageStatsAdmin(admin.ModelAdmin):
    list_display = [
        'usuario_display',
        'simulacoes_mes_display',
        'exportacoes_pdf_mes_display',
        'exportacoes_excel_mes_display',
        'totais_display',
        'ultimo_reset_mensal',
    ]
    search_fields = ['usuario__email', 'usuario__first_name']
    readonly_fields = ['criado_em', 'atualizado_em']
    
    fieldsets = [
        ('Usuário', {
            'fields': ('usuario',)
        }),
        ('Contadores Mensais', {
            'fields': (
                'simulacoes_mes_atual',
                'exportacoes_pdf_mes_atual',
                'exportacoes_excel_mes_atual',
                'ultimo_reset_mensal',
            )
        }),
        ('Contadores Totais', {
            'fields': (
                'total_simulacoes',
                'total_exportacoes_pdf',
                'total_exportacoes_excel',
            )
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    ]
    
    def usuario_display(self, obj):
        tipo_conta = obj.usuario.tipo_conta
        badge_color = '#28a745' if tipo_conta == 'PREMIUM' else '#6c757d'
        
        return format_html(
            '<strong>{}</strong><br>'
            '<small>{}</small><br>'
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            obj.usuario.get_full_name() or obj.usuario.email,
            obj.usuario.email,
            badge_color,
            tipo_conta
        )
    usuario_display.short_description = 'Usuário'
    
    def simulacoes_mes_display(self, obj):
        return format_html(
            '<strong style="color: #007bff; font-size: 16px;">{}</strong>',
            obj.simulacoes_mes_atual
        )
    simulacoes_mes_display.short_description = 'Simulações (Mês)'
    
    def exportacoes_pdf_mes_display(self, obj):
        return format_html(
            '<strong style="color: #dc3545; font-size: 16px;">{}</strong>',
            obj.exportacoes_pdf_mes_atual
        )
    exportacoes_pdf_mes_display.short_description = 'PDFs (Mês)'
    
    def exportacoes_excel_mes_display(self, obj):
        return format_html(
            '<strong style="color: #28a745; font-size: 16px;">{}</strong>',
            obj.exportacoes_excel_mes_atual
        )
    exportacoes_excel_mes_display.short_description = 'Excel (Mês)'
    
    def totais_display(self, obj):
        return format_html(
            'Simulações: <strong>{}</strong><br>'
            'PDFs: <strong>{}</strong><br>'
            'Excel: <strong>{}</strong>',
            obj.total_simulacoes,
            obj.total_exportacoes_pdf,
            obj.total_exportacoes_excel
        )
    totais_display.short_description = 'Totais (Histórico)'
