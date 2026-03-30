# simulacao/subscription_models.py
"""
Models para Sistema de Assinaturas Premium
Gerencia planos, assinaturas e pagamentos
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid


class SubscriptionPlan(models.Model):
    """
    Planos de assinatura disponíveis.
    """
    
    DURACAO_CHOICES = [
        ('MENSAL', 'Mensal'),
        ('TRIMESTRAL', 'Trimestral'),
        ('SEMESTRAL', 'Semestral'),
        ('ANUAL', 'Anual'),
    ]
    
    # Identificação
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=100, verbose_name="Nome do Plano")
    descricao = models.TextField(verbose_name="Descrição")
    
    # Preço e Duração
    preco = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preço (R$)"
    )
    duracao = models.CharField(
        max_length=20,
        choices=DURACAO_CHOICES,
        verbose_name="Duração"
    )
    dias_duracao = models.IntegerField(
        verbose_name="Dias de Duração",
        help_text="Número de dias que o plano dura"
    )
    
    # Features
    simulacoes_ilimitadas = models.BooleanField(
        default=True,
        verbose_name="Simulações Ilimitadas"
    )
    sem_anuncios = models.BooleanField(
        default=True,
        verbose_name="Sem Anúncios"
    )
    exportacao_excel = models.BooleanField(
        default=True,
        verbose_name="Exportação Excel"
    )
    exportacao_pdf_premium = models.BooleanField(
        default=True,
        verbose_name="PDF sem Marca d'Água"
    )
    suporte_prioritario = models.BooleanField(
        default=False,
        verbose_name="Suporte Prioritário"
    )
    pdf_white_label = models.BooleanField(
        default=False,
        verbose_name="PDF White-Label para Corretores",
        help_text="Permite ao corretor personalizar o PDF com logo e dados de contato"
    )
    
    # Desconto
    desconto_percentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Desconto (%)",
        help_text="Desconto aplicado sobre o preço base"
    )
    
    # Status
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    destaque = models.BooleanField(
        default=False,
        verbose_name="Plano em Destaque",
        help_text="Será destacado na página de upgrade"
    )
    
    # Ordem de exibição
    ordem = models.IntegerField(
        default=0,
        verbose_name="Ordem de Exibição"
    )
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Plano de Assinatura"
        verbose_name_plural = "Planos de Assinatura"
        ordering = ['ordem', 'preco']
    
    def __str__(self):
        return f"{self.nome} - R$ {self.preco}/{self.get_duracao_display()}"
    
    def preco_com_desconto(self):
        """Retorna o preço com desconto aplicado."""
        if self.desconto_percentual > 0:
            desconto = (self.preco * self.desconto_percentual) / 100
            return self.preco - desconto
        return self.preco
    
    def preco_mensal_equivalente(self):
        """Calcula o preço mensal equivalente."""
        meses = self.dias_duracao / 30
        return self.preco_com_desconto() / meses if meses > 0 else self.preco_com_desconto()


class Subscription(models.Model):
    """
    Assinatura de um usuário a um plano.
    """
    
    STATUS_CHOICES = [
        ('ATIVA', 'Ativa'),
        ('CANCELADA', 'Cancelada'),
        ('EXPIRADA', 'Expirada'),
        ('SUSPENSA', 'Suspensa'),
        ('PENDENTE', 'Pendente'),
    ]
    
    # Identificação
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relacionamentos
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name="Usuário"
    )
    plano = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name="Plano"
    )
    
    # Status e Datas
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name="Status"
    )
    data_inicio = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Início"
    )
    data_expiracao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Expiração"
    )
    data_cancelamento = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Cancelamento"
    )
    
    # Renovação Automática
    renovacao_automatica = models.BooleanField(
        default=True,
        verbose_name="Renovação Automática"
    )
    
    # Valores
    valor_pago = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Pago (R$)"
    )
    
    # Gateway de Pagamento
    gateway = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Gateway de Pagamento",
        help_text="Ex: Stripe, PagSeguro, Mercado Pago"
    )
    transaction_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="ID da Transação"
    )
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Assinatura"
        verbose_name_plural = "Assinaturas"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['usuario', 'status']),
            models.Index(fields=['status', 'data_expiracao']),
        ]
    
    def __str__(self):
        return f"{self.usuario.email} - {self.plano.nome} ({self.get_status_display()})"
    
    def ativar(self):
        """Ativa a assinatura."""
        self.status = 'ATIVA'
        self.data_inicio = timezone.now()
        self.data_expiracao = self.data_inicio + timedelta(days=self.plano.dias_duracao)
        self.save()
        
        # Atualiza o usuário para Premium
        self.usuario.tipo_conta = 'PREMIUM'
        self.usuario.premium_expira_em = self.data_expiracao
        self.usuario.save()
    
    def cancelar(self, motivo=None):
        """Cancela a assinatura."""
        self.status = 'CANCELADA'
        self.data_cancelamento = timezone.now()
        self.renovacao_automatica = False
        self.save()
    
    def esta_ativa(self):
        """Verifica se a assinatura está ativa."""
        if self.status != 'ATIVA':
            return False
        
        if self.data_expiracao and timezone.now() > self.data_expiracao:
            self.status = 'EXPIRADA'
            self.save()
            return False
        
        return True
    
    def dias_restantes(self):
        """Retorna quantos dias faltam para expirar."""
        if not self.data_expiracao:
            return 0
        
        delta = self.data_expiracao - timezone.now()
        return max(0, delta.days)


class Payment(models.Model):
    """
    Registro de pagamentos realizados.
    """
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PROCESSANDO', 'Processando'),
        ('APROVADO', 'Aprovado'),
        ('RECUSADO', 'Recusado'),
        ('CANCELADO', 'Cancelado'),
        ('REEMBOLSADO', 'Reembolsado'),
    ]
    
    METODO_CHOICES = [
        ('CARTAO_CREDITO', 'Cartão de Crédito'),
        ('CARTAO_DEBITO', 'Cartão de Débito'),
        ('PIX', 'PIX'),
        ('BOLETO', 'Boleto'),
        ('PAYPAL', 'PayPal'),
    ]
    
    # Identificação
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relacionamentos
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Assinatura"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Usuário"
    )
    
    # Dados do Pagamento
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor (R$)"
    )
    metodo = models.CharField(
        max_length=20,
        choices=METODO_CHOICES,
        verbose_name="Método de Pagamento"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name="Status"
    )
    
    # Gateway
    gateway = models.CharField(
        max_length=50,
        verbose_name="Gateway de Pagamento"
    )
    transaction_id = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="ID da Transação"
    )
    
    # Dados Adicionais
    dados_gateway = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Dados do Gateway",
        help_text="Resposta completa do gateway de pagamento"
    )
    
    # Datas
    data_pagamento = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data do Pagamento"
    )
    data_aprovacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Aprovação"
    )
    
    # Metadados
    ip_origem = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="IP de Origem"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['usuario', 'status']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['status', 'criado_em']),
        ]
    
    def __str__(self):
        return f"Pagamento {self.transaction_id} - R$ {self.valor} ({self.get_status_display()})"
    
    def aprovar(self):
        """Aprova o pagamento e ativa a assinatura."""
        self.status = 'APROVADO'
        self.data_aprovacao = timezone.now()
        self.save()
        
        # Ativa a assinatura
        if self.subscription.status == 'PENDENTE':
            self.subscription.ativar()
    
    def recusar(self, motivo=None):
        """Recusa o pagamento."""
        self.status = 'RECUSADO'
        self.save()
        
        # Cancela a assinatura se estava pendente
        if self.subscription.status == 'PENDENTE':
            self.subscription.cancelar(motivo=motivo)


class UsageStats(models.Model):
    """
    Estatísticas de uso para controle de limites.
    """
    
    # Relacionamento
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='usage_stats',
        verbose_name="Usuário"
    )
    
    # Contadores Mensais
    simulacoes_mes_atual = models.IntegerField(
        default=0,
        verbose_name="Simulações no Mês Atual"
    )
    exportacoes_pdf_mes_atual = models.IntegerField(
        default=0,
        verbose_name="Exportações PDF no Mês Atual"
    )
    exportacoes_excel_mes_atual = models.IntegerField(
        default=0,
        verbose_name="Exportações Excel no Mês Atual"
    )
    
    # Contadores Totais
    total_simulacoes = models.IntegerField(
        default=0,
        verbose_name="Total de Simulações"
    )
    total_exportacoes_pdf = models.IntegerField(
        default=0,
        verbose_name="Total de Exportações PDF"
    )
    total_exportacoes_excel = models.IntegerField(
        default=0,
        verbose_name="Total de Exportações Excel"
    )
    
    # Data do último reset
    ultimo_reset_mensal = models.DateField(
        auto_now_add=True,
        verbose_name="Último Reset Mensal"
    )
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Estatística de Uso"
        verbose_name_plural = "Estatísticas de Uso"
    
    def __str__(self):
        return f"Stats de {self.usuario.email}"
    
    def resetar_contadores_mensais(self):
        """Reseta os contadores mensais."""
        self.simulacoes_mes_atual = 0
        self.exportacoes_pdf_mes_atual = 0
        self.exportacoes_excel_mes_atual = 0
        self.ultimo_reset_mensal = timezone.now().date()
        self.save()
    
    def verificar_reset_mensal(self):
        """Verifica se precisa resetar os contadores mensais."""
        hoje = timezone.now().date()
        if self.ultimo_reset_mensal.month != hoje.month:
            self.resetar_contadores_mensais()
    
    def incrementar_simulacao(self):
        """Incrementa contador de simulações."""
        self.verificar_reset_mensal()
        self.simulacoes_mes_atual += 1
        self.total_simulacoes += 1
        self.save()
    
    def incrementar_exportacao_pdf(self):
        """Incrementa contador de exportações PDF."""
        self.verificar_reset_mensal()
        self.exportacoes_pdf_mes_atual += 1
        self.total_exportacoes_pdf += 1
        self.save()
    
    def incrementar_exportacao_excel(self):
        """Incrementa contador de exportações Excel."""
        self.verificar_reset_mensal()
        self.exportacoes_excel_mes_atual += 1
        self.total_exportacoes_excel += 1
        self.save()
