from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from .monetizacao_models import PerfilUsuario, Transacao, UsoRecursos

LIMITS_FREE = {
    'simulacoes_dia': 5,
    'comparacoes_dia': 2,
    'exportacoes_mes': 1
}

class PremiumManager:
    def __init__(self, user):
        self.user = user
        self.perfil, created = PerfilUsuario.objects.get_or_create(usuario=user)

    def eh_premium(self):
        if not self.perfil.premium_ativo:
            return False
        if self.perfil.premium_expira and self.perfil.premium_expira < timezone.now():
            self.desativar_premium()
            return False
        return True

    def ativar_premium(self, product_id, purchase_token=None):
        duration_days = 0
        if product_id == 'com.ficalc.premium.mensal':
            duration_days = 30
        elif product_id == 'com.ficalc.premium.anual':
            duration_days = 365
        else:
            return False # Produto desconhecido

        self.perfil.plano = 'premium'
        self.perfil.premium_ativo = True
        self.perfil.premium_expira = timezone.now() + timedelta(days=duration_days)
        self.perfil.produto_premium = product_id
        self.perfil.data_premium = timezone.now()
        self.perfil.save()

        Transacao.objects.create(
            usuario=self.user,
            tipo='premium_ativacao',
            produto=product_id,
            status='sucesso',
            id_transacao_externa=purchase_token
        )
        return True

    def desativar_premium(self):
        self.perfil.plano = 'gratis'
        self.perfil.premium_ativo = False
        self.perfil.premium_expira = None
        self.perfil.produto_premium = None
        self.perfil.save()

        Transacao.objects.create(
            usuario=self.user,
            tipo='premium_cancelamento',
            status='sucesso'
        )

    def _verificar_e_resetar_limite(self, tipo, reset_period='day'):
        if self.eh_premium():
            return True

        limite_max = LIMITS_FREE.get(tipo, 0)
        uso, created = UsoRecursos.objects.get_or_create(
            usuario=self.user, 
            tipo=tipo, 
            defaults={'limite_maximo': limite_max}
        )

        # Lógica de Reset (Diário ou Mensal)
        agora = timezone.now()
        if reset_period == 'day' and uso.ultimo_reset.date() < agora.date():
            uso.contador = 0
            uso.ultimo_reset = agora
            uso.save()
        elif reset_period == 'month' and (uso.ultimo_reset.year < agora.year or uso.ultimo_reset.month < agora.month):
            uso.contador = 0
            uso.ultimo_reset = agora
            uso.save()

        return uso.contador < uso.limite_maximo

    def incrementar_uso(self, tipo):
        if self.eh_premium():
            return
        uso = UsoRecursos.objects.filter(usuario=self.user, tipo=tipo).first()
        if uso:
            uso.contador += 1
            uso.save()

    def pode_fazer_simulacao(self):
        return self._verificar_e_resetar_limite('simulacoes_dia', 'day')

    def pode_exportar_excel(self):
        return self._verificar_e_resetar_limite('exportacoes_mes', 'month')

    def pode_comparar_cenarios(self):
        return self._verificar_e_resetar_limite('comparacoes_dia', 'day')

    def obter_status(self):
        return {
            'is_premium': self.eh_premium(),
            'expires_at': self.perfil.premium_expira.isoformat() if self.perfil.premium_expira else None,
            'product_id': self.perfil.produto_premium
        }

# Placeholder for Google Play Billing validation
def _validate_google_purchase(purchase_token, product_id, package_name):
    """
    Simulates Google Play purchase validation.
    In a real scenario, this would call Google Play Developer API.
    """
    # For testing purposes, always return True
    print(f"Simulating Google Play validation for token: {purchase_token}, product: {product_id}")
    return True # Assume valid for now