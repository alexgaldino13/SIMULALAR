# 📋 CÓDIGO PARA ADICIONAR AO models.py

Copie e cole o código abaixo em `simulacao/models.py`:

```python
# simulacao/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


# ============================================================================
# MODELOS DE MONETIZAÇÃO
# ============================================================================

class PerfilUsuario(models.Model):
    """Perfil do usuário - Plano (Grátis/Premium) e dados de assinatura."""
    
    usuario = models.OneToOneField(
        User, 
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
        verbose_name_plural = 'Perfis de Usuário'
    
    def __str__(self):
        return f"{self.usuario.username} - {self.plano}"


class ContadorAnuncios(models.Model):
    """Contador de anúncios exibidos por dia."""
    
    usuario = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='contador_anuncios'
    )
    
    banner_hoje = models.IntegerField(default=0)
    intersticial_hoje = models.IntegerField(default=0)
    recompensa_hoje = models.IntegerField(default=0)
    total_impressoes = models.IntegerField(default=0)
    ultimo_reset = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Contadores de Anúncios'
    
    def __str__(self):
        return f"{self.usuario.username} - {self.total_impressoes} impressões"


class AnuncioLog(models.Model):
    """Log detalhado de cada anúncio exibido (para análise)."""
    
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='logs_anuncios'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('banner', 'Banner'),
            ('intersticial', 'Intersticial'),
            ('recompensa', 'Recompensa'),
        ]
    )
    
    posicao = models.CharField(max_length=50)  # topo, rodape, meio
    plataforma = models.CharField(max_length=20)  # web, android, ios
    dados_contexto = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Logs de Anúncios'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.tipo} - {self.timestamp}"


class UsoRecursos(models.Model):
    """Contador de uso de recursos (simulações, comparações, exportações)."""
    
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='uso_recursos'
    )
    
    tipo = models.CharField(
        max_length=50,
        help_text="Tipo: simulacoes_por_dia, comparacoes_por_dia, exportacoes_por_mes"
    )
    
    contador = models.IntegerField(default=0)
    limite_maximo = models.IntegerField()
    ultimo_reset = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Uso de Recursos'
        unique_together = ('usuario', 'tipo')
    
    def __str__(self):
        return f"{self.usuario.username} - {self.tipo}: {self.contador}/{self.limite_maximo}"


class Transacao(models.Model):
    """Histórico de transações (compras, cancelamentos, renovações)."""
    
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='transacoes'
    )
    
    tipo = models.CharField(
        max_length=50,
        choices=[
            ('premium_ativacao', 'Premium - Ativação'),
            ('premium_renovacao', 'Premium - Renovação'),
            ('premium_cancelamento', 'Premium - Cancelamento'),
        ]
    )
    
    produto = models.CharField(max_length=50, null=True, blank=True)
    valor = models.CharField(max_length=50, null=True, blank=True)
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('sucesso', 'Sucesso'),
            ('falha', 'Falha'),
            ('pendente', 'Pendente')
        ],
        default='pendente'
    )
    
    id_transacao_externa = models.CharField(
        max_length=255, 
        null=True, 
        blank=True, 
        unique=True
    )
    
    data = models.DateTimeField(auto_now_add=True)
    dados_adicionais = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name_plural = 'Transações'
        ordering = ['-data']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.tipo} - {self.status}"


# ============================================================================
# ADMIN INLINE PARA VISUALIZAR NO Django Admin
# ============================================================================

"""
Adicione também ao seu admin.py:

from django.contrib import admin
from simulacao.models import (
    PerfilUsuario, ContadorAnuncios, AnuncioLog, 
    UsoRecursos, Transacao
)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'plano', 'premium_ativo', 'premium_expira')
    list_filter = ('plano', 'premium_ativo')
    search_fields = ('usuario__username',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ContadorAnuncios)
class ContadorAnunciosAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'banner_hoje', 'intersticial_hoje', 'total_impressoes')
    search_fields = ('usuario__username',)


@admin.register(AnuncioLog)
class AnuncioLogAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'posicao', 'timestamp')
    list_filter = ('tipo', 'plataforma', 'timestamp')
    search_fields = ('usuario__username',)
    readonly_fields = ('timestamp',)


@admin.register(UsoRecursos)
class UsoRecursosAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'contador', 'limite_maximo')
    list_filter = ('tipo',)
    search_fields = ('usuario__username',)


@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'status', 'valor', 'data')
    list_filter = ('tipo', 'status', 'data')
    search_fields = ('usuario__username', 'id_transacao_externa')
    readonly_fields = ('data',)
"""
```

---

## 📝 CHECKLIST DE IMPLEMENTAÇÃO

```bash
# 1. Copiar código acima para simulacao/models.py
# 2. Executar makemigrations
python manage.py makemigrations simulacao

# 3. Verificar migration criada
# Arquivo: simulacao/migrations/000X_add_monetizacao_models.py

# 4. Executar migrate
python manage.py migrate

# 5. Testar no shell
python manage.py shell

>>> from django.contrib.auth.models import User
>>> from simulacao.models import PerfilUsuario
>>> user = User.objects.first()
>>> perfil = PerfilUsuario.objects.create(usuario=user, plano='gratis')
>>> print(perfil)
# usuario - gratis

# 6. Ver no admin
# Acesse http://localhost:8000/admin/
# Você verá: "Perfis de Usuário", "Contadores de Anúncios", etc
```

---

## ✅ PRONTO!

Agora você pode:

```python
from simulacao.models import PerfilUsuario
from simulacao.monetizacao import PremiumManager

user = User.objects.get(username='joao')
pm = PremiumManager(user)

# Ativar Premium
pm.ativar_premium('premium_mensal')

# Verificar
if pm.eh_premium():
    print("Usuário é premium!")
```
