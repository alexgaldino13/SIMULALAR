from django.contrib import admin

# Register your models here.

# Importa os admins de parcerias
from .partnership_admin import PartnershipAdmin, LeadAdmin

# Importa os admins de assinaturas
from .subscription_admin import (
    SubscriptionPlanAdmin,
    SubscriptionAdmin,
    PaymentAdmin,
    UsageStatsAdmin
)

# Importa os admins de tracking de conversão
from .conversion_admin import ConversionEventAdmin, LeadAlertAdmin

# Importa os modelos de afiliados
from .models import LinkAfiliado, CliqueAfiliado, SavedSimulation, SimulationShare

@admin.register(SavedSimulation)
class SavedSimulationAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'user', 'criado_em', 'is_favorito']
    list_filter = ['criado_em', 'is_favorito']
    search_fields = ['titulo', 'user__username', 'user__email']

@admin.register(SimulationShare)
class SimulationShareAdmin(admin.ModelAdmin):
    list_display = ['token', 'simulacao', 'visualizacoes', 'ativo', 'criado_em']
    list_filter = ['ativo', 'criado_em']
    search_fields = ['token', 'simulacao__titulo']

@admin.register(LinkAfiliado)
class LinkAfiliadoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'ativo', 'comissao_percentual', 'created_at']
    list_filter = ['tipo', 'ativo']
    search_fields = ['nome']

@admin.register(CliqueAfiliado)
class CliqueAfiliadoAdmin(admin.ModelAdmin):
    list_display = ['link', 'usuario', 'ip_address', 'created_at']
    list_filter = ['link', 'created_at']
    readonly_fields = ['link', 'usuario', 'ip_address', 'user_agent', 'pagina_origem', 'created_at']
