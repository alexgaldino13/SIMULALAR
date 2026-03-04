# simulacao/partnership_models.py
"""
Models para Sistema de Parcerias
Gerencia parceiros (consórcios, corretoras, bancos) e leads gerados
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Partnership(models.Model):
    """
    Modelo para gerenciar parceiros comerciais.
    Representa empresas que recebem leads do ImobCalc.
    """
    
    TIPO_PARCEIRO_CHOICES = [
        ('CONSORCIO', 'Consórcio'),
        ('CORRETORA', 'Corretora de Imóveis'),
        ('BANCO', 'Banco/Instituição Financeira'),
        ('CONSTRUTORA', 'Construtora'),
        ('OUTRO', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('INATIVO', 'Inativo'),
        ('SUSPENSO', 'Suspenso'),
        ('EM_ANALISE', 'Em Análise'),
    ]
    
    # Identificação
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=200, verbose_name="Nome do Parceiro")
    nome_fantasia = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nome Fantasia")
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ")
    
    # Tipo e Status
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_PARCEIRO_CHOICES,
        verbose_name="Tipo de Parceiro"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='EM_ANALISE',
        verbose_name="Status"
    )
    
    # Contato
    email_contato = models.EmailField(verbose_name="Email de Contato")
    telefone = models.CharField(max_length=20, verbose_name="Telefone")
    site = models.URLField(blank=True, null=True, verbose_name="Website")
    
    # Endereço
    endereco = models.CharField(max_length=300, blank=True, null=True, verbose_name="Endereço")
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado")
    cep = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")
    
    # Configurações de Integração
    api_key = models.CharField(
        max_length=100,
        unique=True,
        default=uuid.uuid4,
        verbose_name="API Key",
        help_text="Chave para autenticação na API"
    )
    webhook_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL do Webhook",
        help_text="URL para envio automático de leads"
    )
    webhook_ativo = models.BooleanField(
        default=False,
        verbose_name="Webhook Ativo"
    )
    
    # Valores e Comissões
    valor_por_lead = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor por Lead (R$)",
        help_text="Quanto o parceiro paga por lead qualificado"
    )
    comissao_conversao = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Comissão por Conversão (%)",
        help_text="Percentual sobre o valor do negócio fechado"
    )
    
    # Filtros de Leads
    valor_minimo_imovel = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Valor Mínimo do Imóvel",
        help_text="Recebe apenas leads de imóveis acima deste valor"
    )
    valor_maximo_imovel = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Valor Máximo do Imóvel",
        help_text="Recebe apenas leads de imóveis abaixo deste valor"
    )
    estados_atendidos = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Estados Atendidos",
        help_text="Lista de UFs que o parceiro atende. Ex: ['SP', 'RJ', 'MG']"
    )
    
    # Estatísticas
    total_leads_recebidos = models.IntegerField(
        default=0,
        verbose_name="Total de Leads Recebidos"
    )
    total_leads_convertidos = models.IntegerField(
        default=0,
        verbose_name="Total de Leads Convertidos"
    )
    taxa_conversao = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Taxa de Conversão (%)"
    )
    
    # Metadados
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partnerships_criadas',
        verbose_name="Criado por"
    )
    
    class Meta:
        verbose_name = "Parceiro"
        verbose_name_plural = "Parceiros"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['tipo', 'status']),
            models.Index(fields=['cnpj']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"
    
    def atualizar_estatisticas(self):
        """
        Atualiza estatísticas do parceiro baseado nos leads.
        """
        from django.db.models import Count, Q
        
        leads = self.leads.all()
        self.total_leads_recebidos = leads.count()
        self.total_leads_convertidos = leads.filter(status='CONVERTIDO').count()
        
        if self.total_leads_recebidos > 0:
            self.taxa_conversao = (self.total_leads_convertidos / self.total_leads_recebidos) * 100
        else:
            self.taxa_conversao = 0
        
        self.save()
    
    def pode_receber_lead(self, valor_imovel, estado):
        """
        Verifica se o parceiro pode receber um lead baseado nos filtros.
        """
        # Verifica status
        if self.status != 'ATIVO':
            return False
        
        # Verifica valor mínimo
        if self.valor_minimo_imovel and valor_imovel < self.valor_minimo_imovel:
            return False
        
        # Verifica valor máximo
        if self.valor_maximo_imovel and valor_imovel > self.valor_maximo_imovel:
            return False
        
        # Verifica estado
        if self.estados_atendidos and estado not in self.estados_atendidos:
            return False
        
        return True


class Lead(models.Model):
    """
    Modelo para gerenciar leads enviados aos parceiros.
    Representa um usuário interessado que foi compartilhado com um parceiro.
    """
    
    STATUS_CHOICES = [
        ('NOVO', 'Novo'),
        ('ENVIADO', 'Enviado ao Parceiro'),
        ('EM_CONTATO', 'Em Contato'),
        ('QUALIFICADO', 'Qualificado'),
        ('NEGOCIACAO', 'Em Negociação'),
        ('CONVERTIDO', 'Convertido'),
        ('PERDIDO', 'Perdido'),
        ('INVALIDO', 'Inválido'),
    ]
    
    ORIGEM_CHOICES = [
        ('SIMULACAO', 'Simulação Completa'),
        ('FORMULARIO', 'Formulário de Contato'),
        ('DASHBOARD', 'Dashboard do Usuário'),
        ('MANUAL', 'Cadastro Manual'),
    ]
    
    # Identificação
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relacionamentos
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leads',
        verbose_name="Usuário"
    )
    parceiro = models.ForeignKey(
        Partnership,
        on_delete=models.CASCADE,
        related_name='leads',
        verbose_name="Parceiro"
    )
    
    # Status e Origem
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NOVO',
        verbose_name="Status"
    )
    origem = models.CharField(
        max_length=20,
        choices=ORIGEM_CHOICES,
        default='SIMULACAO',
        verbose_name="Origem"
    )
    
    # Dados do Lead (criptografados quando necessário)
    nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    email = models.EmailField(verbose_name="Email")
    telefone = models.CharField(max_length=20, verbose_name="Telefone")
    cpf_criptografado = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="CPF (Criptografado)"
    )
    
    # Dados do Imóvel de Interesse
    valor_imovel = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Valor do Imóvel"
    )
    valor_entrada = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Valor da Entrada"
    )
    cidade_interesse = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Cidade de Interesse"
    )
    estado_interesse = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        verbose_name="Estado de Interesse"
    )
    
    # Dados Financeiros
    renda_mensal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Renda Mensal"
    )
    fgts_disponivel = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="FGTS Disponível"
    )
    
    # Preferências
    cenario_preferido = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Cenário Preferido",
        help_text="Ex: Financiamento SAC, Consórcio, etc."
    )
    observacoes_usuario = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações do Usuário"
    )
    
    # Dados da Simulação (JSON)
    dados_simulacao = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Dados da Simulação",
        help_text="Dados completos da simulação realizada"
    )
    
    # Tracking
    enviado_em = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Enviado em"
    )
    visualizado_em = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Visualizado em"
    )
    primeiro_contato_em = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Primeiro Contato em"
    )
    convertido_em = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Convertido em"
    )
    
    # Valor da Conversão
    valor_negocio = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Valor do Negócio",
        help_text="Valor final do negócio fechado"
    )
    comissao_gerada = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Comissão Gerada",
        help_text="Valor da comissão para o ImobCalc"
    )
    
    # Metadados
    ip_origem = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="IP de Origem"
    )
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="User Agent"
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Lead"
        verbose_name_plural = "Leads"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['parceiro', 'status']),
            models.Index(fields=['usuario']),
            models.Index(fields=['status']),
            models.Index(fields=['criado_em']),
        ]
    
    def __str__(self):
        return f"Lead {self.nome_completo} - {self.parceiro.nome}"
    
    def marcar_como_enviado(self):
        """Marca o lead como enviado ao parceiro."""
        self.status = 'ENVIADO'
        self.enviado_em = timezone.now()
        self.save()
    
    def marcar_como_convertido(self, valor_negocio):
        """Marca o lead como convertido e calcula comissão."""
        self.status = 'CONVERTIDO'
        self.convertido_em = timezone.now()
        self.valor_negocio = valor_negocio
        
        # Calcula comissão
        if self.parceiro.comissao_conversao > 0:
            self.comissao_gerada = (valor_negocio * self.parceiro.comissao_conversao) / 100
        
        self.save()
        
        # Atualiza estatísticas do parceiro
        self.parceiro.atualizar_estatisticas()
    
    def tempo_ate_conversao(self):
        """Retorna o tempo em dias até a conversão."""
        if self.convertido_em and self.criado_em:
            delta = self.convertido_em - self.criado_em
            return delta.days
        return None
    
    def get_cpf_descriptografado(self):
        """Retorna o CPF descriptografado."""
        if self.cpf_criptografado:
            from .encryption import decrypt_cpf
            return decrypt_cpf(self.cpf_criptografado, formatted=True)
        return None
