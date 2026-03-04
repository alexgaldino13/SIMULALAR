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
