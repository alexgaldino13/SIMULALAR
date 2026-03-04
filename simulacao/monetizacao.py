"""
Sistema de Monetização - FI (Financiamento Imobiliário)

Gerencia:
- Versão Grátis com anúncios AdMob
- Versão Premium com compra in-app
- Acesso a recursos exclusivos
- Controle de limite de simulações

Integração com:
- Google Play (Android)
- App Store (iOS)
- AdMob (Publicidade)
"""

from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from enum import Enum
import json
import hashlib
import hmac


# ============================================================================
# CONSTANTES DE CONFIGURAÇÃO
# ============================================================================

class TipoPlano(Enum):
    """Tipos de plano disponíveis."""
    GRATIS = "gratis"
    PREMIUM = "premium"


class TipoAnuncio(Enum):
    """Tipos de anúncios AdMob."""
    BANNER = "banner"
    INTERSTICIAL = "intersticial"
    RECOMPENSA = "recompensa"


# IDs de Teste do AdMob (conforme documentação oficial do Google)
# Usar estes durante desenvolvimento
ADMOB_TEST_IDS = {
    'banner_ios': 'ca-app-pub-3940256099942544/2934735945',
    'banner_android': 'ca-app-pub-3940256099942544/6300978111',
    'intersticial_ios': 'ca-app-pub-3940256099942544/4411468910',
    'intersticial_android': 'ca-app-pub-3940256099942544/1033173712',
    'recompensa_ios': 'ca-app-pub-3940256099942544/5224354917',
    'recompensa_android': 'ca-app-pub-3940256099942544/6978759866',
    'aplicacao_ios': 'ca-app-pub-xxxxxxxxxxxxxxxx~yyyyyyyyyy',
    'aplicacao_android': 'ca-app-pub-xxxxxxxxxxxxxxxx~yyyyyyyyyy',
}

# IDs de Produtos In-App (configure com seus valores reais)
PRODUTOS_IN_APP = {
    'premium_anual': {
        'ios_id': 'com.ficalc.premium.anual',
        'android_id': 'com.ficalc.premium.anual',
        'preco': 'R$ 49,90',
        'preco_usd': 9.99,
        'descricao': 'Premium anual - Sem anúncios + Recursos ilimitados',
        'duracao': 365,  # dias
    },
    'premium_mensal': {
        'ios_id': 'com.ficalc.premium.mensal',
        'android_id': 'com.ficalc.premium.mensal',
        'preco': 'R$ 9,90',
        'preco_usd': 2.99,
        'descricao': 'Premium mensal - Sem anúncios + Recursos ilimitados',
        'duracao': 30,  # dias
    },
}

# Limites de uso (versão grátis)
LIMITES_GRATIS = {
    'simulacoes_por_dia': 5,
    'comparacoes_por_dia': 2,
    'exportacoes_por_mes': 1,
    'cenarios_simultaneos': 2,
}

# Posições de anúncios
POSICOES_ANUNCIOS = {
    'topo_pagina': 'above_fold',
    'rodape_pagina': 'bottom',
    'entre_resultados': 'middle',
    'lateral': 'sidebar',
}


# ============================================================================
# CLASSE GERENCIADOR ADMOB
# ============================================================================

class AdMobManager:
    """
    Gerencia integração com AdMob para versão grátis.
    
    Exemplo:
        ad_manager = AdMobManager(user)
        if not ad_manager.eh_premium:
            banner_id = ad_manager.obter_id_anuncio('banner')
            ad_manager.registrar_impressao('banner', 'topo_pagina')
    """
    
    def __init__(self, usuario=None, plataforma='android'):
        """
        Inicializa o gerenciador de anúncios.
        
        Args:
            usuario (User): Usuário Django
            plataforma (str): 'android' ou 'ios'
        """
        self.usuario = usuario
        self.plataforma = plataforma
        self.eh_premium = self._verificar_premium()
        self.contador_anuncios = self._obter_contador()
    
    def _verificar_premium(self):
        """Verifica se usuário é premium."""
        if not self.usuario or not self.usuario.is_authenticated:
            return False
        
        try:
            perfil = PerfilUsuario.objects.get(usuario=self.usuario)
            return perfil.plano == TipoPlano.PREMIUM and perfil.premium_ativo
        except PerfilUsuario.DoesNotExist:
            return False
    
    def _obter_contador(self):
        """Obtém contador de anúncios mostrados."""
        if not self.usuario or not self.usuario.is_authenticated:
            return {'banner': 0, 'intersticial': 0, 'recompensa': 0}
        
        try:
            contador = ContadorAnuncios.objects.get(usuario=self.usuario)
            return {
                'banner': contador.banner_hoje,
                'intersticial': contador.intersticial_hoje,
                'recompensa': contador.recompensa_hoje,
            }
        except ContadorAnuncios.DoesNotExist:
            return {'banner': 0, 'intersticial': 0, 'recompensa': 0}
    
    def obter_id_anuncio(self, tipo_anuncio):
        """
        Retorna ID do anúncio apropriado.
        
        Args:
            tipo_anuncio (str): 'banner', 'intersticial' ou 'recompensa'
        
        Returns:
            str: ID do anúncio (teste ou produção)
        
        Exemplo:
            banner_id = ad_manager.obter_id_anuncio('banner')
            # ca-app-pub-3940256099942544/6300978111 (teste Android)
        """
        if self.eh_premium:
            return None  # Premium não vê anúncios
        
        # Em produção, retornar IDs reais
        ambiente = getattr(settings, 'ADMOB_AMBIENTE', 'teste')
        
        if ambiente == 'teste':
            chave = f"{tipo_anuncio}_{self.plataforma}"
            return ADMOB_TEST_IDS.get(chave)
        else:
            # Em produção, buscar IDs do settings
            return getattr(settings, f'ADMOB_{tipo_anuncio.upper()}_{self.plataforma.upper()}', None)
    
    def mostrar_anuncio(self, tipo_anuncio, posicao, contexto=None):
        """
        Prepara e registra exibição de anúncio.
        
        Args:
            tipo_anuncio (str): 'banner', 'intersticial', 'recompensa'
            posicao (str): Posição na página
            contexto (dict): Dados adicionais
        
        Returns:
            dict: Configuração do anúncio
        
        Exemplo:
            config = ad_manager.mostrar_anuncio('banner', 'topo_pagina')
            # {'id': 'ca-app-pub-...', 'tipo': 'banner', 'visivel': True}
        """
        if self.eh_premium:
            return {'visivel': False, 'motivo': 'usuario_premium'}
        
        config = {
            'tipo': tipo_anuncio,
            'posicao': posicao,
            'id_anuncio': self.obter_id_anuncio(tipo_anuncio),
            'visivel': True,
            'plataforma': self.plataforma,
        }
        
        # Registrar impressão
        if self.usuario and self.usuario.is_authenticated:
            self.registrar_impressao(tipo_anuncio, posicao, contexto)
        
        return config
    
    def registrar_impressao(self, tipo_anuncio, posicao, contexto=None):
        """
        Registra impressão de anúncio para análise.
        
        Args:
            tipo_anuncio (str): Tipo de anúncio
            posicao (str): Posição de exibição
            contexto (dict): Dados contextuais
        """
        if not self.usuario or not self.usuario.is_authenticated:
            return
        
        try:
            contador = ContadorAnuncios.objects.get(usuario=self.usuario)
        except ContadorAnuncios.DoesNotExist:
            contador = ContadorAnuncios.objects.create(usuario=self.usuario)
        
        # Resetar contadores se é um novo dia
        se_novo_dia = contador.ultimo_reset.date() < timezone.now().date()
        if se_novo_dia:
            contador.banner_hoje = 0
            contador.intersticial_hoje = 0
            contador.recompensa_hoje = 0
            contador.ultimo_reset = timezone.now()
        
        # Incrementar contador apropriado
        if tipo_anuncio == 'banner':
            contador.banner_hoje += 1
        elif tipo_anuncio == 'intersticial':
            contador.intersticial_hoje += 1
        elif tipo_anuncio == 'recompensa':
            contador.recompensa_hoje += 1
        
        contador.total_impressoes += 1
        contador.save()
        
        # Registrar em log para análise
        AnuncioLog.objects.create(
            usuario=self.usuario,
            tipo=tipo_anuncio,
            posicao=posicao,
            plataforma=self.plataforma,
            dados_contexto=contexto or {}
        )
    
    def obter_restricoes(self):
        """
        Retorna restrições de anúncios para usuário.
        
        Returns:
            dict: Configurações de limite
        
        Exemplo:
            restricoes = ad_manager.obter_restricoes()
            # {
            #     'max_banner_dia': 10,
            #     'max_intersticial_dia': 3,
            #     'intervalo_minimo_seg': 30,
            # }
        """
        return {
            'max_banner_dia': 20,
            'max_intersticial_dia': 5,
            'max_recompensa_dia': 10,
            'intervalo_minimo_seg': 30,
            'bloqueio_apos_rejeicao': 120,  # segundos
        }


# ============================================================================
# CLASSE GERENCIADOR PREMIUM
# ============================================================================

class PremiumManager:
    """
    Gerencia assinatura Premium e acesso a recursos exclusivos.
    
    Exemplo:
        pm = PremiumManager(user)
        if pm.pode_exportar_excel():
            exportar_para_excel(dados)
        else:
            mostrar_banner_premium()
    """
    
    def __init__(self, usuario):
        """
        Inicializa gerenciador Premium.
        
        Args:
            usuario (User): Usuário Django
        """
        self.usuario = usuario
        self.perfil = self._obter_ou_criar_perfil()
    
    def _obter_ou_criar_perfil(self):
        """Obtém ou cria perfil de usuário."""
        perfil, criado = PerfilUsuario.objects.get_or_create(usuario=self.usuario)
        return perfil
    
    def eh_premium(self):
        """
        Verifica se usuário é premium e ativa.
        
        Returns:
            bool: True se premium ativo
        """
        if self.perfil.plano != TipoPlano.PREMIUM:
            return False
        
        # Verificar se expirou
        if self.perfil.premium_expira:
            if timezone.now() > self.perfil.premium_expira:
                self._desativar_premium()
                return False
        
        return self.perfil.premium_ativo
    
    def pode_exportar_excel(self):
        """
        Verifica se usuário pode exportar para Excel.
        
        Returns:
            bool: True se permitido
        """
        if self.eh_premium():
            return True  # Premium ilimitado
        
        # Verificar limite de exportações grátis
        return self._verificar_limite('exportacoes_por_mes', LIMITES_GRATIS['exportacoes_por_mes'])
    
    def pode_fazer_simulacao(self):
        """
        Verifica se usuário pode fazer nova simulação.
        
        Returns:
            bool: True se permitido
        """
        if self.eh_premium():
            return True  # Premium ilimitado
        
        return self._verificar_limite('simulacoes_por_dia', LIMITES_GRATIS['simulacoes_por_dia'])
    
    def pode_comparar_cenarios(self):
        """
        Verifica se usuário pode fazer comparação.
        
        Returns:
            bool: True se permitido
        """
        if self.eh_premium():
            return True  # Premium ilimitado
        
        return self._verificar_limite('comparacoes_por_dia', LIMITES_GRATIS['comparacoes_por_dia'])
    
    def pode_acessar_graficos_avancados(self):
        """
        Verifica se usuário acessa gráficos avançados.
        
        Returns:
            bool: True se permitido
        """
        if self.eh_premium():
            return True
        return False
    
    def pode_usar_cenarios_multiplos(self):
        """
        Verifica se usuário pode comparar múltiplos cenários.
        
        Returns:
            bool: True se permitido
        """
        if self.eh_premium():
            return True
        
        limite = LIMITES_GRATIS['cenarios_simultaneos']
        return self._verificar_limite('cenarios_simultaneos', limite)
    
    def _verificar_limite(self, tipo_limite, limite_max):
        """
        Verifica se usuário atingiu limite.
        
        Args:
            tipo_limite (str): Tipo de limite
            limite_max (int): Limite máximo
        
        Returns:
            bool: True se não atingiu limite
        """
        try:
            uso = UsoRecursos.objects.get(usuario=self.usuario, tipo=tipo_limite)
            
            # Resetar se necessário (diário ou mensal)
            agora = timezone.now()
            if tipo_limite.endswith('_dia'):
                deve_resetar = uso.ultimo_reset.date() < agora.date()
            else:
                deve_resetar = uso.ultimo_reset.month < agora.month or uso.ultimo_reset.year < agora.year
            
            if deve_resetar:
                uso.contador = 0
                uso.ultimo_reset = agora
                uso.save()
            
            # Verificar limite
            if uso.contador >= limite_max:
                return False
            
            # Incrementar contador
            uso.contador += 1
            uso.save()
            return True
            
        except UsoRecursos.DoesNotExist:
            # Criar registro novo
            UsoRecursos.objects.create(
                usuario=self.usuario,
                tipo=tipo_limite,
                contador=1,
                limite_maximo=limite_max
            )
            return True
    
    def ativar_premium(self, tipo_produto, tempo_duracao_dias=None):
        """
        Ativa Premium após verificação de compra.
        
        Args:
            tipo_produto (str): 'premium_mensal' ou 'premium_anual'
            tempo_duracao_dias (int): Dias de duração (opcional)
        
        Returns:
            bool: True se ativado com sucesso
        """
        if tipo_produto not in PRODUTOS_IN_APP:
            return False
        
        produto = PRODUTOS_IN_APP[tipo_produto]
        duracao = tempo_duracao_dias or produto['duracao']
        
        self.perfil.plano = TipoPlano.PREMIUM
        self.perfil.premium_ativo = True
        self.perfil.premium_expira = timezone.now() + timedelta(days=duracao)
        self.perfil.produto_premium = tipo_produto
        self.perfil.data_premium = timezone.now()
        self.perfil.save()
        
        # Registrar transação
        Transacao.objects.create(
            usuario=self.usuario,
            tipo='premium_ativacao',
            produto=tipo_produto,
            valor=produto['preco'],
            status='sucesso'
        )
        
        return True
    
    def _desativar_premium(self):
        """Desativa Premium após expiração."""
        self.perfil.plano = TipoPlano.GRATIS
        self.perfil.premium_ativo = False
        self.perfil.save()
    
    def renovar_premium(self, tipo_produto):
        """
        Renova assinatura Premium.
        
        Args:
            tipo_produto (str): Tipo de produto
        
        Returns:
            bool: True se renovado
        """
        return self.ativar_premium(tipo_produto)
    
    def cancelar_premium(self):
        """Cancela Premium imediatamente."""
        self.perfil.plano = TipoPlano.GRATIS
        self.perfil.premium_ativo = False
        self.perfil.premium_expira = None
        self.perfil.save()
        
        Transacao.objects.create(
            usuario=self.usuario,
            tipo='premium_cancelamento',
            status='sucesso'
        )
    
    def obter_status(self):
        """
        Retorna status detalhado do usuário.
        
        Returns:
            dict: Informações de status
        """
        status = {
            'usuario': self.usuario.username,
            'plano': self.perfil.plano.value if self.perfil.plano else 'gratis',
            'premium_ativo': self.eh_premium(),
            'data_ativacao': self.perfil.data_premium.isoformat() if self.perfil.data_premium else None,
            'data_expiracao': self.perfil.premium_expira.isoformat() if self.perfil.premium_expira else None,
            'dias_restantes': self._calcular_dias_restantes(),
        }
        
        # Adicionar limites de uso
        if not self.eh_premium():
            status['limites'] = {
                'simulacoes_hoje': self._obter_contador_uso('simulacoes_por_dia'),
                'comparacoes_hoje': self._obter_contador_uso('comparacoes_por_dia'),
                'exportacoes_mes': self._obter_contador_uso('exportacoes_por_mes'),
            }
        
        return status
    
    def _calcular_dias_restantes(self):
        """Calcula dias restantes de Premium."""
        if not self.perfil.premium_expira:
            return None
        
        dias = (self.perfil.premium_expira - timezone.now()).days
        return max(0, dias)
    
    def _obter_contador_uso(self, tipo_limite):
        """Obtém contador de uso atual."""
        try:
            uso = UsoRecursos.objects.get(usuario=self.usuario, tipo=tipo_limite)
            return {
                'usado': uso.contador,
                'limite': uso.limite_maximo,
                'disponivel': uso.limite_maximo - uso.contador,
            }
        except UsoRecursos.DoesNotExist:
            limite = LIMITES_GRATIS.get(tipo_limite, 0)
            return {
                'usado': 0,
                'limite': limite,
                'disponivel': limite,
            }


# ============================================================================
# MODELOS DJANGO (usar em models.py)
# ============================================================================

"""
Adicione estes modelos ao seu models.py:

from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_ficalc')
    plano = models.CharField(
        max_length=20,
        choices=[('gratis', 'Grátis'), ('premium', 'Premium')],
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
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='contador_anuncios')
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
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logs_anuncios')
    tipo = models.CharField(max_length=20, choices=[
        ('banner', 'Banner'),
        ('intersticial', 'Intersticial'),
        ('recompensa', 'Recompensa'),
    ])
    posicao = models.CharField(max_length=50)
    plataforma = models.CharField(max_length=20)
    dados_contexto = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Logs de Anúncios'
        ordering = ['-timestamp']


class UsoRecursos(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uso_recursos')
    tipo = models.CharField(max_length=50)  # simulacoes_por_dia, exportacoes_por_mes, etc
    contador = models.IntegerField(default=0)
    limite_maximo = models.IntegerField()
    ultimo_reset = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Uso de Recursos'
        unique_together = ('usuario', 'tipo')


class Transacao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transacoes')
    tipo = models.CharField(max_length=50)  # premium_ativacao, premium_cancelamento, etc
    produto = models.CharField(max_length=50, null=True, blank=True)
    valor = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('sucesso', 'Sucesso'), ('falha', 'Falha'), ('pendente', 'Pendente')],
        default='pendente'
    )
    id_transacao_externa = models.CharField(max_length=255, null=True, blank=True, unique=True)
    data = models.DateTimeField(auto_now_add=True)
    dados_adicionais = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name_plural = 'Transações'
        ordering = ['-data']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.tipo} - {self.status}"
"""


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def gerar_assinatura_compra(user_id, produto_id, timestamp):
    """
    Gera assinatura HMAC para validação de compra (Google Play).
    
    Args:
        user_id (str): ID do usuário
        produto_id (str): ID do produto
        timestamp (int): Timestamp Unix
    
    Returns:
        str: Hash HMAC SHA256
    """
    chave_secreta = getattr(settings, 'GOOGLE_PLAY_SECRET_KEY', '').encode()
    mensagem = f"{user_id}:{produto_id}:{timestamp}".encode()
    
    if not chave_secreta:
        raise ValueError("GOOGLE_PLAY_SECRET_KEY não configurada em settings.py")
    
    assinatura = hmac.new(chave_secreta, mensagem, hashlib.sha256).hexdigest()
    return assinatura


def validar_assinatura_compra(user_id, produto_id, timestamp, assinatura):
    """
    Valida assinatura de compra do Google Play.
    
    Args:
        user_id (str): ID do usuário
        produto_id (str): ID do produto
        timestamp (int): Timestamp Unix
        assinatura (str): Assinatura HMAC a validar
    
    Returns:
        bool: True se assinatura válida
    """
    assinatura_esperada = gerar_assinatura_compra(user_id, produto_id, timestamp)
    return hmac.compare_digest(assinatura_esperada, assinatura)


def obter_contexto_anuncios(usuario, plataforma='web'):
    """
    Retorna contexto de anúncios para template.
    
    Args:
        usuario (User): Usuário
        plataforma (str): 'web', 'android', 'ios'
    
    Returns:
        dict: Configuração de anúncios
    
    Exemplo em template:
        {% load custom_filters %}
        {% if config.ads.topo.visivel %}
            <div class="ad-banner">{{ config.ads.topo|anuncio }}</div>
        {% endif %}
    """
    ad_manager = AdMobManager(usuario, plataforma)
    
    return {
        'mostra_anuncios': not ad_manager.eh_premium,
        'topo': ad_manager.mostrar_anuncio('banner', 'topo_pagina'),
        'rodape': ad_manager.mostrar_anuncio('banner', 'rodape_pagina'),
        'entre_resultados': ad_manager.mostrar_anuncio('intersticial', 'entre_resultados'),
    }


def obter_contexto_premium(usuario):
    """
    Retorna contexto de recursos Premium para template.
    
    Args:
        usuario (User): Usuário
    
    Returns:
        dict: Status e limites
    
    Exemplo em template:
        {% if premium.pode_exportar %}
            <button>Exportar para Excel</button>
        {% else %}
            <button disabled>Upgrade para Premium</button>
        {% endif %}
    """
    pm = PremiumManager(usuario)
    
    return {
        'eh_premium': pm.eh_premium(),
        'pode_exportar': pm.pode_exportar_excel(),
        'pode_simular': pm.pode_fazer_simulacao(),
        'pode_comparar': pm.pode_comparar_cenarios(),
        'graficos_avancados': pm.pode_acessar_graficos_avancados(),
        'multiplos_cenarios': pm.pode_usar_cenarios_multiplos(),
        'status': pm.obter_status(),
    }


if __name__ == '__main__':
    print("✓ Módulo de Monetização carregado com sucesso!")
    print("\nUso básico:")
    print("  from simulacao.monetizacao import AdMobManager, PremiumManager")
    print("  ")
    print("  # AdMob (anúncios)")
    print("  ad_mgr = AdMobManager(usuario)")
    print("  config = ad_mgr.mostrar_anuncio('banner', 'topo_pagina')")
    print("  ")
    print("  # Premium")
    print("  pm = PremiumManager(usuario)")
    print("  pm.ativar_premium('premium_mensal')")
    print("  if pm.pode_exportar_excel():")
    print("      exportar_para_excel(dados)")
