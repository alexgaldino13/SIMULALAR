# simulacao/conversion_tracking.py
"""
Sistema de Tracking de Conversão
Rastreia eventos do funil de vendas e identifica leads parados
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta
import uuid


class ConversionEvent(models.Model):
    """
    Registra eventos importantes no funil de conversão.
    Permite análise detalhada do comportamento dos leads.
    """
    
    TIPO_EVENTO_CHOICES = [
        # Eventos do Lead
        ('LEAD_CRIADO', 'Lead Criado'),
        ('LEAD_ENVIADO', 'Lead Enviado ao Parceiro'),
        ('LEAD_VISUALIZADO', 'Lead Visualizado pelo Parceiro'),
        
        # Eventos de Contato
        ('PRIMEIRO_CONTATO', 'Primeiro Contato Realizado'),
        ('CONTATO_TELEFONE', 'Contato por Telefone'),
        ('CONTATO_EMAIL', 'Contato por Email'),
        ('CONTATO_WHATSAPP', 'Contato por WhatsApp'),
        ('REUNIAO_AGENDADA', 'Reunião Agendada'),
        ('REUNIAO_REALIZADA', 'Reunião Realizada'),
        
        # Eventos de Qualificação
        ('LEAD_QUALIFICADO', 'Lead Qualificado'),
        ('DOCUMENTOS_SOLICITADOS', 'Documentos Solicitados'),
        ('DOCUMENTOS_RECEBIDOS', 'Documentos Recebidos'),
        ('ANALISE_CREDITO', 'Análise de Crédito Iniciada'),
        ('CREDITO_APROVADO', 'Crédito Aprovado'),
        ('CREDITO_NEGADO', 'Crédito Negado'),
        
        # Eventos de Negociação
        ('PROPOSTA_ENVIADA', 'Proposta Enviada'),
        ('PROPOSTA_ACEITA', 'Proposta Aceita'),
        ('PROPOSTA_RECUSADA', 'Proposta Recusada'),
        ('NEGOCIACAO_VALORES', 'Negociação de Valores'),
        ('CONTRATO_ENVIADO', 'Contrato Enviado'),
        ('CONTRATO_ASSINADO', 'Contrato Assinado'),
        
        # Eventos de Conversão
        ('CONVERTIDO', 'Lead Convertido'),
        ('PERDIDO', 'Lead Perdido'),
        ('INVALIDO', 'Lead Inválido'),
        
        # Eventos de Follow-up
        ('FOLLOWUP_AGENDADO', 'Follow-up Agendado'),
        ('FOLLOWUP_REALIZADO', 'Follow-up Realizado'),
        ('SEM_RESPOSTA', 'Sem Resposta do Lead'),
    ]
    
    # Identificação
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relacionamentos
    lead = models.ForeignKey(
        'Lead',
        on_delete=models.CASCADE,
        related_name='eventos',
        verbose_name="Lead"
    )
    parceiro = models.ForeignKey(
        'Partnership',
        on_delete=models.CASCADE,
        related_name='eventos',
        verbose_name="Parceiro"
    )
    usuario_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos_conversao',
        verbose_name="Usuário Responsável",
        help_text="Usuário do parceiro que registrou o evento"
    )
    
    # Dados do Evento
    tipo_evento = models.CharField(
        max_length=30,
        choices=TIPO_EVENTO_CHOICES,
        verbose_name="Tipo de Evento"
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição",
        help_text="Detalhes adicionais sobre o evento"
    )
    
    # Metadados
    dados_adicionais = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Dados Adicionais",
        help_text="Informações extras em formato JSON"
    )
    ip_origem = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="IP de Origem"
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Evento de Conversão"
        verbose_name_plural = "Eventos de Conversão"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['lead', 'tipo_evento']),
            models.Index(fields=['parceiro', 'criado_em']),
            models.Index(fields=['tipo_evento', 'criado_em']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_evento_display()} - {self.lead.nome_completo}"
    
    @classmethod
    def registrar_evento(cls, lead, tipo_evento, descricao=None, dados_adicionais=None, usuario=None, ip=None):
        """
        Método helper para registrar um evento de conversão.
        """
        evento = cls.objects.create(
            lead=lead,
            parceiro=lead.parceiro,
            tipo_evento=tipo_evento,
            descricao=descricao,
            dados_adicionais=dados_adicionais,
            usuario_responsavel=usuario,
            ip_origem=ip
        )
        return evento


class LeadAlert(models.Model):
    """
    Alertas automáticos para leads que precisam de atenção.
    Identifica leads parados ou com problemas.
    """
    
    TIPO_ALERTA_CHOICES = [
        ('LEAD_PARADO', 'Lead Parado (sem atividade)'),
        ('SEM_CONTATO', 'Sem Contato Inicial'),
        ('SEM_FOLLOWUP', 'Sem Follow-up'),
        ('DOCUMENTOS_PENDENTES', 'Documentos Pendentes'),
        ('PROPOSTA_SEM_RESPOSTA', 'Proposta sem Resposta'),
        ('RISCO_PERDA', 'Risco de Perda'),
        ('OPORTUNIDADE', 'Oportunidade de Conversão'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]
    
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('RESOLVIDO', 'Resolvido'),
        ('IGNORADO', 'Ignorado'),
    ]
    
    # Identificação
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relacionamentos
    lead = models.ForeignKey(
        'Lead',
        on_delete=models.CASCADE,
        related_name='alertas',
        verbose_name="Lead"
    )
    parceiro = models.ForeignKey(
        'Partnership',
        on_delete=models.CASCADE,
        related_name='alertas',
        verbose_name="Parceiro"
    )
    
    # Dados do Alerta
    tipo_alerta = models.CharField(
        max_length=30,
        choices=TIPO_ALERTA_CHOICES,
        verbose_name="Tipo de Alerta"
    )
    prioridade = models.CharField(
        max_length=10,
        choices=PRIORIDADE_CHOICES,
        default='MEDIA',
        verbose_name="Prioridade"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ATIVO',
        verbose_name="Status"
    )
    
    mensagem = models.TextField(verbose_name="Mensagem")
    recomendacao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Recomendação",
        help_text="Ação recomendada para resolver o alerta"
    )
    
    # Tracking
    dias_sem_atividade = models.IntegerField(
        default=0,
        verbose_name="Dias sem Atividade"
    )
    notificacao_enviada = models.BooleanField(
        default=False,
        verbose_name="Notificação Enviada"
    )
    notificacao_enviada_em = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Notificação Enviada em"
    )
    
    # Resolução
    resolvido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertas_resolvidos',
        verbose_name="Resolvido por"
    )
    resolvido_em = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Resolvido em"
    )
    observacoes_resolucao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações da Resolução"
    )
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Alerta de Lead"
        verbose_name_plural = "Alertas de Leads"
        ordering = ['-prioridade', '-criado_em']
        indexes = [
            models.Index(fields=['parceiro', 'status']),
            models.Index(fields=['lead', 'status']),
            models.Index(fields=['prioridade', 'status']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_alerta_display()} - {self.lead.nome_completo}"
    
    def marcar_como_resolvido(self, usuario, observacoes=None):
        """Marca o alerta como resolvido."""
        self.status = 'RESOLVIDO'
        self.resolvido_por = usuario
        self.resolvido_em = timezone.now()
        self.observacoes_resolucao = observacoes
        self.save()
    
    def enviar_notificacao(self):
        """Envia notificação por email sobre o alerta."""
        if not self.notificacao_enviada and self.parceiro.email_contato:
            assunto = f"[ImobCalc] Alerta: {self.get_tipo_alerta_display()}"
            mensagem = f"""
            Olá {self.parceiro.nome},
            
            Identificamos um alerta importante sobre o lead {self.lead.nome_completo}:
            
            Tipo: {self.get_tipo_alerta_display()}
            Prioridade: {self.get_prioridade_display()}
            
            {self.mensagem}
            
            {f'Recomendação: {self.recomendacao}' if self.recomendacao else ''}
            
            Acesse o dashboard para mais detalhes.
            
            Atenciosamente,
            Equipe ImobCalc
            """
            
            try:
                send_mail(
                    assunto,
                    mensagem,
                    settings.DEFAULT_FROM_EMAIL,
                    [self.parceiro.email_contato],
                    fail_silently=False,
                )
                self.notificacao_enviada = True
                self.notificacao_enviada_em = timezone.now()
                self.save()
                return True
            except Exception as e:
                print(f"Erro ao enviar notificação: {e}")
                return False
        return False
    
    @classmethod
    def verificar_leads_parados(cls):
        """
        Verifica todos os leads e cria alertas para os que estão parados.
        Deve ser executado periodicamente (ex: diariamente via cron).
        """
        from .partnership_models import Lead
        from django.db.models import Max
        
        agora = timezone.now()
        alertas_criados = 0
        
        # Busca leads ativos (não convertidos, não perdidos, não inválidos)
        leads_ativos = Lead.objects.exclude(
            status__in=['CONVERTIDO', 'PERDIDO', 'INVALIDO']
        )
        
        for lead in leads_ativos:
            # Pega o último evento do lead
            ultimo_evento = lead.eventos.aggregate(Max('criado_em'))['criado_em__max']
            
            if ultimo_evento:
                dias_sem_atividade = (agora - ultimo_evento).days
            else:
                # Se não tem eventos, usa a data de criação do lead
                dias_sem_atividade = (agora - lead.criado_em).days
            
            # Verifica se já existe um alerta ativo para este lead
            alerta_existente = cls.objects.filter(
                lead=lead,
                tipo_alerta='LEAD_PARADO',
                status='ATIVO'
            ).exists()
            
            # Cria alerta se o lead está parado há mais de 3 dias
            if dias_sem_atividade >= 3 and not alerta_existente:
                if dias_sem_atividade >= 7:
                    prioridade = 'URGENTE'
                    mensagem = f"Lead sem atividade há {dias_sem_atividade} dias! Risco alto de perda."
                elif dias_sem_atividade >= 5:
                    prioridade = 'ALTA'
                    mensagem = f"Lead sem atividade há {dias_sem_atividade} dias. Ação necessária."
                else:
                    prioridade = 'MEDIA'
                    mensagem = f"Lead sem atividade há {dias_sem_atividade} dias."
                
                alerta = cls.objects.create(
                    lead=lead,
                    parceiro=lead.parceiro,
                    tipo_alerta='LEAD_PARADO',
                    prioridade=prioridade,
                    mensagem=mensagem,
                    recomendacao="Entre em contato com o lead o mais rápido possível.",
                    dias_sem_atividade=dias_sem_atividade
                )
                
                # Envia notificação para alertas de alta prioridade
                if prioridade in ['ALTA', 'URGENTE']:
                    alerta.enviar_notificacao()
                
                alertas_criados += 1
        
        return alertas_criados
    
    @classmethod
    def verificar_sem_contato_inicial(cls):
        """
        Verifica leads que foram enviados mas ainda não tiveram contato inicial.
        """
        from .partnership_models import Lead
        
        agora = timezone.now()
        limite = agora - timedelta(hours=24)  # 24 horas sem contato
        alertas_criados = 0
        
        # Busca leads enviados sem primeiro contato
        leads_sem_contato = Lead.objects.filter(
            status='ENVIADO',
            enviado_em__lte=limite,
            primeiro_contato_em__isnull=True
        )
        
        for lead in leads_sem_contato:
            # Verifica se já existe alerta
            alerta_existente = cls.objects.filter(
                lead=lead,
                tipo_alerta='SEM_CONTATO',
                status='ATIVO'
            ).exists()
            
            if not alerta_existente:
                horas_sem_contato = (agora - lead.enviado_em).total_seconds() / 3600
                
                alerta = cls.objects.create(
                    lead=lead,
                    parceiro=lead.parceiro,
                    tipo_alerta='SEM_CONTATO',
                    prioridade='ALTA',
                    mensagem=f"Lead enviado há {int(horas_sem_contato)} horas sem contato inicial.",
                    recomendacao="Realize o primeiro contato imediatamente para não perder o lead.",
                    dias_sem_atividade=int(horas_sem_contato / 24)
                )
                alerta.enviar_notificacao()
                alertas_criados += 1
        
        return alertas_criados
