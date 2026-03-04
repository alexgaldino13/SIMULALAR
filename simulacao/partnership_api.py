# simulacao/partnership_api.py
"""
API REST para Sistema de Parcerias
Permite que parceiros acessem e gerenciem seus leads
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from datetime import timedelta
import logging

from .partnership_models import Partnership, Lead
from .partnership_serializers import (
    PartnershipSerializer,
    LeadSerializer,
    LeadListSerializer,
    LeadDetailSerializer,
    LeadStatusUpdateSerializer,
    PartnershipStatsSerializer
)

logger = logging.getLogger(__name__)


class PartnershipAPIKeyAuthentication(TokenAuthentication):
    """
    Autenticação customizada usando API Key do parceiro.
    """
    keyword = 'ApiKey'
    
    def authenticate_credentials(self, key):
        try:
            partnership = Partnership.objects.get(api_key=key, status='ATIVO')
        except Partnership.DoesNotExist:
            raise exceptions.AuthenticationFailed('API Key inválida ou parceiro inativo')
        
        return (partnership, key)


class IsPartnerAuthenticated(permissions.BasePermission):
    """
    Permissão customizada para verificar se o parceiro está autenticado.
    """
    
    def has_permission(self, request, view):
        return hasattr(request, 'user') and isinstance(request.user, Partnership)


class PartnershipViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para parceiros visualizarem seus próprios dados.
    READ-ONLY: Parceiros não podem modificar seus dados via API.
    """
    serializer_class = PartnershipSerializer
    authentication_classes = [PartnershipAPIKeyAuthentication]
    permission_classes = [IsPartnerAuthenticated]
    
    def get_queryset(self):
        # Retorna apenas o parceiro autenticado
        return Partnership.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Retorna dados do parceiro autenticado.
        GET /api/partnerships/me/
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Retorna estatísticas do parceiro.
        GET /api/partnerships/stats/
        """
        partnership = request.user
        
        # Estatísticas gerais
        total_leads = partnership.leads.count()
        leads_novos = partnership.leads.filter(status='NOVO').count()
        leads_em_contato = partnership.leads.filter(status='EM_CONTATO').count()
        leads_qualificados = partnership.leads.filter(status='QUALIFICADO').count()
        leads_negociacao = partnership.leads.filter(status='NEGOCIACAO').count()
        leads_convertidos = partnership.leads.filter(status='CONVERTIDO').count()
        leads_perdidos = partnership.leads.filter(status='PERDIDO').count()
        
        # Estatísticas dos últimos 30 dias
        data_30_dias = timezone.now() - timedelta(days=30)
        leads_30_dias = partnership.leads.filter(criado_em__gte=data_30_dias)
        
        # Valor total de negócios
        valor_total = partnership.leads.filter(
            status='CONVERTIDO'
        ).aggregate(total=Sum('valor_negocio'))['total'] or 0
        
        # Comissão total gerada
        comissao_total = partnership.leads.filter(
            status='CONVERTIDO'
        ).aggregate(total=Sum('comissao_gerada'))['total'] or 0
        
        # Tempo médio de conversão
        leads_convertidos_obj = partnership.leads.filter(
            status='CONVERTIDO',
            convertido_em__isnull=False
        )
        
        tempo_medio_conversao = None
        if leads_convertidos_obj.exists():
            tempos = []
            for lead in leads_convertidos_obj:
                tempo = lead.tempo_ate_conversao()
                if tempo:
                    tempos.append(tempo)
            
            if tempos:
                tempo_medio_conversao = sum(tempos) / len(tempos)
        
        data = {
            'total_leads': total_leads,
            'leads_por_status': {
                'novos': leads_novos,
                'em_contato': leads_em_contato,
                'qualificados': leads_qualificados,
                'negociacao': leads_negociacao,
                'convertidos': leads_convertidos,
                'perdidos': leads_perdidos,
            },
            'ultimos_30_dias': {
                'total': leads_30_dias.count(),
                'convertidos': leads_30_dias.filter(status='CONVERTIDO').count(),
            },
            'financeiro': {
                'valor_total_negocios': float(valor_total),
                'comissao_total_gerada': float(comissao_total),
            },
            'performance': {
                'taxa_conversao': float(partnership.taxa_conversao),
                'tempo_medio_conversao_dias': tempo_medio_conversao,
            }
        }
        
        return Response(data)


class LeadViewSet(viewsets.ModelViewSet):
    """
    ViewSet para parceiros gerenciarem seus leads.
    """
    serializer_class = LeadSerializer
    authentication_classes = [PartnershipAPIKeyAuthentication]
    permission_classes = [IsPartnerAuthenticated]
    
    def get_queryset(self):
        # Retorna apenas leads do parceiro autenticado
        queryset = Lead.objects.filter(parceiro=self.request.user)
        
        # Filtros opcionais
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        origem_filter = self.request.query_params.get('origem', None)
        if origem_filter:
            queryset = queryset.filter(origem=origem_filter)
        
        # Filtro por data
        data_inicio = self.request.query_params.get('data_inicio', None)
        data_fim = self.request.query_params.get('data_fim', None)
        
        if data_inicio:
            queryset = queryset.filter(criado_em__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(criado_em__lte=data_fim)
        
        # Filtro por valor do imóvel
        valor_min = self.request.query_params.get('valor_min', None)
        valor_max = self.request.query_params.get('valor_max', None)
        
        if valor_min:
            queryset = queryset.filter(valor_imovel__gte=valor_min)
        if valor_max:
            queryset = queryset.filter(valor_imovel__lte=valor_max)
        
        # Filtro por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado_interesse=estado)
        
        return queryset.order_by('-criado_em')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LeadListSerializer
        elif self.action == 'retrieve':
            return LeadDetailSerializer
        elif self.action == 'update_status':
            return LeadStatusUpdateSerializer
        return LeadSerializer
    
    def list(self, request, *args, **kwargs):
        """
        Lista todos os leads do parceiro.
        GET /api/leads/
        
        Parâmetros de query:
        - status: Filtrar por status
        - origem: Filtrar por origem
        - data_inicio: Data inicial (YYYY-MM-DD)
        - data_fim: Data final (YYYY-MM-DD)
        - valor_min: Valor mínimo do imóvel
        - valor_max: Valor máximo do imóvel
        - estado: Filtrar por estado (UF)
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retorna detalhes de um lead específico.
        GET /api/leads/{id}/
        """
        lead = self.get_object()
        
        # Marca como visualizado se ainda não foi
        if not lead.visualizado_em:
            lead.visualizado_em = timezone.now()
            lead.save()
        
        serializer = self.get_serializer(lead)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        Parceiros não podem criar leads via API.
        Leads são criados apenas pelo sistema ImobCalc.
        """
        return Response(
            {'error': 'Parceiros não podem criar leads via API'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    def destroy(self, request, *args, **kwargs):
        """
        Parceiros não podem deletar leads via API.
        """
        return Response(
            {'error': 'Parceiros não podem deletar leads via API'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Atualiza o status de um lead.
        PATCH /api/leads/{id}/update_status/
        
        Body:
        {
            "status": "EM_CONTATO",
            "observacoes": "Cliente respondeu, agendar reunião"
        }
        """
        lead = self.get_object()
        serializer = LeadStatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            novo_status = serializer.validated_data['status']
            observacoes = serializer.validated_data.get('observacoes', '')
            
            # Atualiza status
            status_anterior = lead.status
            lead.status = novo_status
            
            # Atualiza timestamps específicos
            if novo_status == 'EM_CONTATO' and not lead.primeiro_contato_em:
                lead.primeiro_contato_em = timezone.now()
            
            # Adiciona observações
            if observacoes:
                if lead.observacoes_usuario:
                    lead.observacoes_usuario += f"\n\n[{timezone.now().strftime('%d/%m/%Y %H:%M')}] {observacoes}"
                else:
                    lead.observacoes_usuario = f"[{timezone.now().strftime('%d/%m/%Y %H:%M')}] {observacoes}"
            
            lead.save()
            
            # Log da alteração
            logger.info(
                f"Lead {lead.id} - Status alterado de {status_anterior} para {novo_status} "
                f"pelo parceiro {request.user.nome}"
            )
            
            return Response({
                'success': True,
                'message': 'Status atualizado com sucesso',
                'lead': LeadDetailSerializer(lead).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def mark_converted(self, request, pk=None):
        """
        Marca um lead como convertido.
        POST /api/leads/{id}/mark_converted/
        
        Body:
        {
            "valor_negocio": 350000.00,
            "observacoes": "Contrato assinado"
        }
        """
        lead = self.get_object()
        
        if lead.status == 'CONVERTIDO':
            return Response(
                {'error': 'Lead já está marcado como convertido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valor_negocio = request.data.get('valor_negocio')
        observacoes = request.data.get('observacoes', '')
        
        if not valor_negocio:
            return Response(
                {'error': 'valor_negocio é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            valor_negocio = float(valor_negocio)
        except (ValueError, TypeError):
            return Response(
                {'error': 'valor_negocio deve ser um número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Marca como convertido
        lead.marcar_como_convertido(valor_negocio)
        
        # Adiciona observações
        if observacoes:
            if lead.observacoes_usuario:
                lead.observacoes_usuario += f"\n\n[{timezone.now().strftime('%d/%m/%Y %H:%M')}] CONVERTIDO: {observacoes}"
            else:
                lead.observacoes_usuario = f"[{timezone.now().strftime('%d/%m/%Y %H:%M')}] CONVERTIDO: {observacoes}"
            lead.save()
        
        # Log da conversão
        logger.info(
            f"Lead {lead.id} convertido pelo parceiro {request.user.nome}. "
            f"Valor: R$ {valor_negocio:,.2f} - Comissão: R$ {lead.comissao_gerada:,.2f}"
        )
        
        return Response({
            'success': True,
            'message': 'Lead marcado como convertido com sucesso',
            'lead': LeadDetailSerializer(lead).data,
            'comissao_gerada': float(lead.comissao_gerada) if lead.comissao_gerada else 0
        })
    
    @action(detail=True, methods=['post'])
    def mark_lost(self, request, pk=None):
        """
        Marca um lead como perdido.
        POST /api/leads/{id}/mark_lost/
        
        Body:
        {
            "motivo": "Cliente desistiu da compra"
        }
        """
        lead = self.get_object()
        
        if lead.status in ['CONVERTIDO', 'PERDIDO']:
            return Response(
                {'error': f'Lead já está marcado como {lead.get_status_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        motivo = request.data.get('motivo', 'Não especificado')
        
        # Atualiza status
        lead.status = 'PERDIDO'
        
        # Adiciona motivo nas observações
        if lead.observacoes_usuario:
            lead.observacoes_usuario += f"\n\n[{timezone.now().strftime('%d/%m/%Y %H:%M')}] PERDIDO: {motivo}"
        else:
            lead.observacoes_usuario = f"[{timezone.now().strftime('%d/%m/%Y %H:%M')}] PERDIDO: {motivo}"
        
        lead.save()
        
        # Atualiza estatísticas do parceiro
        request.user.atualizar_estatisticas()
        
        # Log
        logger.info(
            f"Lead {lead.id} marcado como perdido pelo parceiro {request.user.nome}. "
            f"Motivo: {motivo}"
        )
        
        return Response({
            'success': True,
            'message': 'Lead marcado como perdido',
            'lead': LeadDetailSerializer(lead).data
        })


@api_view(['GET'])
@permission_classes([IsPartnerAuthenticated])
def api_health(request):
    """
    Endpoint de health check para verificar se a API está funcionando.
    GET /api/health/
    """
    return Response({
        'status': 'ok',
        'message': 'API de Parcerias ImobCalc está funcionando',
        'parceiro': request.user.nome,
        'timestamp': timezone.now().isoformat()
    })


@api_view(['POST'])
def webhook_receiver(request):
    """
    Endpoint para receber webhooks de parceiros.
    POST /api/webhook/
    
    Parceiros podem enviar atualizações de status via webhook.
    """
    # Valida API Key
    api_key = request.headers.get('X-API-Key')
    
    if not api_key:
        return Response(
            {'error': 'API Key não fornecida'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        partnership = Partnership.objects.get(api_key=api_key, status='ATIVO')
    except Partnership.DoesNotExist:
        return Response(
            {'error': 'API Key inválida'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Processa webhook
    lead_id = request.data.get('lead_id')
    novo_status = request.data.get('status')
    
    if not lead_id or not novo_status:
        return Response(
            {'error': 'lead_id e status são obrigatórios'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        lead = Lead.objects.get(id=lead_id, parceiro=partnership)
    except Lead.DoesNotExist:
        return Response(
            {'error': 'Lead não encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Atualiza status
    lead.status = novo_status
    lead.save()
    
    logger.info(
        f"Webhook recebido: Lead {lead_id} atualizado para {novo_status} "
        f"pelo parceiro {partnership.nome}"
    )
    
    return Response({
        'success': True,
        'message': 'Webhook processado com sucesso'
    })
