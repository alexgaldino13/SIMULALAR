# simulacao/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import json

# ======================================================================
# MODELOS DE AUTENTICAÇÃO E USUÁRIO
# ======================================================================

class CustomUser(AbstractUser):
    """
    Modelo de usuário customizado que estende o User padrão do Django.
    Permite adicionar campos extras conforme necessário.
    """
    # Campos adicionais além dos padrões (username, email, password, etc.)
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    data_nascimento = models.DateField(blank=True, null=True, verbose_name="Data de Nascimento")
    
    # Tipo de conta
    TIPO_CONTA_CHOICES = [
        ('FREE', 'Gratuita'),
        ('PREMIUM', 'Premium'),
    ]
    tipo_conta = models.CharField(
        max_length=10,
        choices=TIPO_CONTA_CHOICES,
        default='FREE',
        verbose_name="Tipo de Conta"
    )
    
    # Data de expiração da assinatura premium (se aplicável)
    premium_expira_em = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Premium Expira em"
    )
    
    # Aceite de termos e políticas
    aceitou_termos = models.BooleanField(default=False, verbose_name="Aceitou Termos de Uso")
    aceitou_privacidade = models.BooleanField(default=False, verbose_name="Aceitou Política de Privacidade")
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
    
    def __str__(self):
        return self.email or self.username
    
    @property
    def is_premium(self):
        """Verifica se o usuário tem conta premium ativa."""
        if self.tipo_conta != 'PREMIUM':
            return False
        
        if self.premium_expira_em is None:
            return True  # Premium vitalicio
        
        from django.utils import timezone
        return self.premium_expira_em > timezone.now()


class UserProfile(models.Model):
    """
    Perfil estendido do usuário com informações adicionais.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Informações pessoais
    cpf = models.CharField(max_length=14, blank=True, null=True, verbose_name="CPF")
    renda_mensal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Renda Mensal"
    )
    
    # Preferências
    receber_notificacoes = models.BooleanField(default=True, verbose_name="Receber Notificações")
    receber_emails_marketing = models.BooleanField(default=False, verbose_name="Receber E-mails de Marketing")
    
    # Avatar
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Avatar"
    )
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"
    
    def __str__(self):
        return f"Perfil de {self.user.username}"


# ======================================================================
# MODELOS DE SIMULAÇÕES SALVAS
# ======================================================================

class SavedSimulation(models.Model):
    """
    Armazena simulações completas realizadas pelos usuários.
    Permite que usuários salvem e recuperem suas simulações.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='simulacoes_salvas'
    )
    
    # Identificação
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título da Simulação",
        help_text="Ex: 'Apartamento Centro - 300k'"
    )
    
    # Dados da simulação (armazenados como JSON)
    dados_wizard = models.JSONField(
        verbose_name="Dados do Wizard",
        help_text="Todos os dados coletados nas 5 etapas do wizard"
    )
    
    # Resultados calculados (também em JSON para flexibilidade)
    resultados = models.JSONField(
        verbose_name="Resultados da Simulação",
        help_text="Resultados calculados para todos os cenários"
    )
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    # Favorito
    is_favorito = models.BooleanField(default=False, verbose_name="Favorito")
    
    # Notas do usuário
    notas = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notas",
        help_text="Anotações pessoais sobre esta simulação"
    )
    
    class Meta:
        verbose_name = "Simulação Salva"
        verbose_name_plural = "Simulações Salvas"
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"{self.titulo} - {self.user.username}"


class SimulationShare(models.Model):
    """
    Permite que usuários compartilhem suas simulações via link.
    """
    simulacao = models.ForeignKey(
        SavedSimulation,
        on_delete=models.CASCADE,
        related_name='compartilhamentos'
    )
    
    # Token único para compartilhamento
    token = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Token de Compartilhamento"
    )
    
    # Controle de acesso
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    expira_em = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Expira em"
    )
    
    # Estatísticas
    visualizacoes = models.IntegerField(default=0, verbose_name="Visualizações")
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Compartilhamento de Simulação"
        verbose_name_plural = "Compartilhamentos de Simulações"
    
    def __str__(self):
        return f"Compartilhamento: {self.simulacao.titulo}"


# ======================================================================
# 1. MODELOS DE USUÁRIO E SIMULAÇÃO (Versão Simples) - MANTIDOS
# ======================================================================

class Usuario(models.Model):
    """
    Representa o usuário do aplicativo (usado atualmente na view de teste).
    """
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class Simulacao(models.Model):
    """
    Armazena os parâmetros e resultados principais de uma simulação (Estrutura Antiga).
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    valor_imovel = models.DecimalField(max_digits=15, decimal_places=2)
    entrada = models.DecimalField(max_digits=15, decimal_places=2)
    taxa_anual = models.DecimalField(max_digits=5, decimal_places=2)
    prazo_meses = models.IntegerField()
    parcela_fixa = models.DecimalField(max_digits=15, decimal_places=2)
    total_juros = models.DecimalField(max_digits=15, decimal_places=2)
    data_simulacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Simulação de {self.valor_imovel} por {self.usuario.nome}"


# ======================================================================
# 2. NOVOS CAMPOS PARA DESPESAS DE TRANSAÇÃO
# ======================================================================

class Financiamento(models.Model):
    """
    Modelo para armazenar dados de financiamento com suporte a despesas.
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Dados do imóvel
    valor_imovel = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor do Imóvel")
    entrada = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Entrada (Recursos Próprios + FGTS)")
    
    # Dados do financiamento
    taxa_juros_anual = models.DecimalField(max_digits=5, decimal_places=3, verbose_name="Taxa de Juros Anual (%)")
    prazo_meses = models.IntegerField(verbose_name="Prazo Total em Meses")
    
    # Campos para despesas de transação
    valor_despesas = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Total de Despesas de Transação"
    )
    
    incorporar_despesas = models.BooleanField(
        default=True,
        verbose_name="Incorporar Despesas no Financiamento?"
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True)

    @property
    def principal_financiado(self):
        """
        Calcula o Principal Financiado (Base de cálculo do SAC/PRICE).
        """
        principal_base = self.valor_imovel - self.entrada
        
        if self.incorporar_despesas:
            return principal_base + self.valor_despesas
        else:
            return principal_base

    def __str__(self):
        return f"Financiamento de R$ {self.valor_imovel:,.2f} - Prazo {self.prazo_meses} meses"

    class Meta:
        verbose_name = "Financiamento"
        verbose_name_plural = "Financiamentos"


# ======================================================================
# 3. MODELOS PARA COMPARAÇÃO DE MÚLTIPLOS CENÁRIOS
# ======================================================================

class CenarioComparativo(models.Model):
    """
    Armazena o conjunto de dados iniciais para uma rodada de comparação.
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    
    valor_imovel = models.DecimalField(max_digits=15, decimal_places=2)
    entrada = models.DecimalField(max_digits=15, decimal_places=2)
    prazo_anos = models.IntegerField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cenário: R${self.valor_imovel} - {self.prazo_anos} anos"


class ResultadoComparacao(models.Model):
    """
    Armazena o resultado final de um método específico.
    """
    METODO_CHOICES = [
        ('PRICE', 'Tabela Price'),
        ('SAC', 'Tabela SAC'),
        ('CONS', 'Consórcio'),
        ('RENDA', 'Aluguel + Investimento')
    ]
    
    cenario = models.ForeignKey(CenarioComparativo, on_delete=models.CASCADE)
    metodo = models.CharField(max_length=5, choices=METODO_CHOICES)
    
    # Resultados Chave para a Comparação
    parcela_inicial = models.DecimalField(max_digits=15, decimal_places=2)
    total_pago = models.DecimalField(max_digits=15, decimal_places=2)
    total_juros_ou_custo = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Detalhes adicionais
    taxa_juros_anual = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_metodo_display()} para o Cenário #{self.cenario.id}"


class LinkAfiliado(models.Model):
    nome = models.CharField(max_length=100)  # Ex: "Caixa Economica", "Itau"
    tipo = models.CharField(max_length=50, choices=[
        ('banco', 'Banco'),
        ('consorcio', 'Consorcio'),
        ('corretora', 'Corretora'),
        ('seguradora', 'Seguradora'),
    ])
    url_afiliado = models.URLField()  # Link com parametro de afiliado
    codigo_afiliado = models.CharField(max_length=50, blank=True)
    logo = models.ImageField(upload_to='afiliados/', blank=True, null=True)
    ativo = models.BooleanField(default=True)
    comissao_percentual = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    descricao = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Link Afiliado'
        verbose_name_plural = 'Links Afiliados'

    def __str__(self):
        return f"{self.nome} ({self.tipo})"

class CliqueAfiliado(models.Model):
    link = models.ForeignKey(LinkAfiliado, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    pagina_origem = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Clique em Afiliado'
        verbose_name_plural = 'Cliques em Afiliados'
