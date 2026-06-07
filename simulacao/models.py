from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Usuário customizado com campos de perfil e monetização."""
    TIPO_CONTA_CHOICES = [
        ("comprador", "Comprador"),
        ("investidor", "Investidor"),
        ("corretor", "Corretor"),
        ("explorando", "Explorando"),
    ]
    tipo_conta = models.CharField(max_length=20, choices=TIPO_CONTA_CHOICES, default="comprador", blank=True)
    aceitou_termos = models.BooleanField(default=False)
    aceitou_privacidade = models.BooleanField(default=False)
    premium_expira_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"


class SavedSimulation(models.Model):
    """Simulação salva pelo usuário."""
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="simulacoes"
    )
    titulo = models.CharField(max_length=200, default="Minha Simulação")
    dados_wizard = models.JSONField(default=dict)
    resultados = models.JSONField(default=dict)
    is_favorito = models.BooleanField(default=False)
    notas = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Simulação Salva"
        verbose_name_plural = "Simulações Salvas"

    def __str__(self):
        return f"{self.titulo} — {self.user.username}"


class ParametroMercado(models.Model):
    chave = models.SlugField(max_length=64, unique=True)
    nome = models.CharField(max_length=128)
    valor = models.DecimalField(max_digits=18, decimal_places=8)
    unidade = models.CharField(max_length=32, default='percentual')
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['chave']
        verbose_name = 'Parâmetro de Mercado'
        verbose_name_plural = 'Parâmetros de Mercado'

    def __str__(self):
        return f"{self.nome} ({self.chave})"

    def to_dict(self):
        return {
            'nome': self.nome,
            'valor': float(self.valor),
            'unidade': self.unidade,
            'descricao': self.descricao,
        }

    @classmethod
    def get_current_values(cls, fallback=None):
        queryset = cls.objects.filter(ativo=True)
        if not queryset.exists():
            return fallback or {}
        return {param.chave: param.to_dict() for param in queryset}
