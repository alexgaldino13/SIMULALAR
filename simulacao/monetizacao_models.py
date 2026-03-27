from django.db import models
from django.conf import settings

# ============================================================================
# Modelos para Tracking de Anúncios
# ============================================================================
class AdView(models.Model):
    AD_TYPES = [
        ('banner', 'Banner'),
        ('interstitial', 'Interstitial'),
        ('rewarded', 'Rewarded'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ad_type = models.CharField(max_length=20, choices=AD_TYPES)
    page = models.CharField(max_length=100)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Visualização de Anúncio"
        verbose_name_plural = "Visualizações de Anúncios"

    def __str__(self):
        return f"{self.ad_type} em {self.page} - {self.viewed_at}"

# ============================================================================
# Modelos para Assinaturas Premium
# ============================================================================
class PerfilUsuario(models.Model):
    """Perfil do usuário - Plano (Grátis/Premium) e dados de assinatura."""
    
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='perfil_ficalc'
    )
    
    plano = models.CharField(
        max_length=20,
        choices=[
            ('gratis', 'Grátis'),
            ('premium', 'Premium')
        ],
        default='gratis'
    )
    
    premium_ativo = models.BooleanField(default=False)
    premium_expira = models.DateTimeField(null=True, blank=True)
    produto_premium = models.CharField(max_length=50, null=True, blank=True)
    data_premium = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = 'Perfis de Usuário'

    def __str__(self):
        return f"{self.usuario.username} - {self.plano}"


class Transacao(models.Model):
    """Histórico de transações (compras, cancelamentos, renovações)."""
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='transacoes'
    )
    
    tipo = models.CharField(
        max_length=50,
        choices=[
            ('premium_ativacao', 'Premium - Ativação'),
            ('premium_renovacao', 'Premium - Renovação'),
            ('premium_cancelamento', 'Premium - Cancelamento'),
            ('google_play_purchase', 'Google Play Purchase'),
            ('app_store_purchase', 'App Store Purchase'),
        ]
    )
    
    produto = models.CharField(max_length=50, null=True, blank=True)
    valor = models.CharField(max_length=50, null=True, blank=True) # Pode ser string para flexibilidade
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('sucesso', 'Sucesso'),
            ('falha', 'Falha'),
            ('pendente', 'Pendente')
        ],
        default='pendente'
    )
    
    id_transacao_externa = models.CharField(max_length=255, null=True, blank=True, unique=True)
    data = models.DateTimeField(auto_now_add=True)
    dados_adicionais = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = 'Transações'
        ordering = ['-data']

    def __str__(self):
        return f"{self.usuario.username} - {self.tipo} - {self.status}"

class UsoRecursos(models.Model):
    """Contador de uso de recursos (simulações, comparações, exportações)."""
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='uso_recursos'
    )
    tipo = models.CharField(max_length=50) # Ex: 'simulacoes_dia', 'exportacoes_mes'
    contador = models.IntegerField(default=0)
    limite_maximo = models.IntegerField()
    ultimo_reset = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Uso de Recurso"
        verbose_name_plural = "Uso de Recursos"
        unique_together = ('usuario', 'tipo')

    def __str__(self):
        return f"{self.usuario.username} - {self.tipo}: {self.contador}/{self.limite_maximo}"