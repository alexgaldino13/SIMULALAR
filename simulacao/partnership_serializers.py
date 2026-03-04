# simulacao/partnership_serializers.py
"""
Serializers para API de Parcerias
"""

from rest_framework import serializers
from .partnership_models import Partnership, Lead


class PartnershipSerializer(serializers.ModelSerializer):
    """
    Serializer para dados do parceiro.
    """
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Partnership
        fields = [
            'id',
            'nome',
            'nome_fantasia',
            'cnpj',
            'tipo',
            'tipo_display',
            'status',
            'status_display',
            'email_contato',
            'telefone',
            'site',
            'endereco',
            'cidade',
            'estado',
            'cep',
            'valor_minimo_imovel',
            'valor_maximo_imovel',
            'estados_atendidos',
            'total_leads_recebidos',
            'total_leads_convertidos',
            'taxa_conversao',
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = [
            'id',
            'cnpj',
            'total_leads_recebidos',
            'total_leads_convertidos',
            'taxa_conversao',
            'criado_em',
            'atualizado_em',
        ]


class PartnershipStatsSerializer(serializers.Serializer):
    """
    Serializer para estatísticas do parceiro.
    """
    total_leads = serializers.IntegerField()
    leads_por_status = serializers.DictField()
    ultimos_30_dias = serializers.DictField()
    financeiro = serializers.DictField()
    performance = serializers.DictField()


class LeadListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listagem de leads.
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    origem_display = serializers.CharField(source='get_origem_display', read_only=True)
    
    class Meta:
        model = Lead
        fields = [
            'id',
            'nome_completo',
            'email',
            'telefone',
            'status',
            'status_display',
            'origem',
            'origem_display',
            'valor_imovel',
            'cidade_interesse',
            'estado_interesse',
            'criado_em',
            'enviado_em',
            'visualizado_em',
        ]
        read_only_fields = '__all__'


class LeadDetailSerializer(serializers.ModelSerializer):
    """
    Serializer completo para detalhes de um lead.
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    origem_display = serializers.CharField(source='get_origem_display', read_only=True)
    tempo_conversao_dias = serializers.SerializerMethodField()
    cpf = serializers.SerializerMethodField()
    
    class Meta:
        model = Lead
        fields = [
            'id',
            'nome_completo',
            'email',
            'telefone',
            'cpf',
            'status',
            'status_display',
            'origem',
            'origem_display',
            'valor_imovel',
            'valor_entrada',
            'cidade_interesse',
            'estado_interesse',
            'renda_mensal',
            'fgts_disponivel',
            'cenario_preferido',
            'observacoes_usuario',
            'dados_simulacao',
            'criado_em',
            'enviado_em',
            'visualizado_em',
            'primeiro_contato_em',
            'convertido_em',
            'valor_negocio',
            'tempo_conversao_dias',
        ]
        read_only_fields = '__all__'
    
    def get_tempo_conversao_dias(self, obj):
        return obj.tempo_ate_conversao()
    
    def get_cpf(self, obj):
        # Retorna CPF descriptografado apenas se existir
        return obj.get_cpf_descriptografado()


class LeadSerializer(serializers.ModelSerializer):
    """
    Serializer padrão para leads.
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    origem_display = serializers.CharField(source='get_origem_display', read_only=True)
    
    class Meta:
        model = Lead
        fields = [
            'id',
            'nome_completo',
            'email',
            'telefone',
            'status',
            'status_display',
            'origem',
            'origem_display',
            'valor_imovel',
            'valor_entrada',
            'cidade_interesse',
            'estado_interesse',
            'renda_mensal',
            'observacoes_usuario',
            'criado_em',
            'enviado_em',
            'visualizado_em',
        ]
        read_only_fields = [
            'id',
            'criado_em',
            'enviado_em',
        ]


class LeadStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer para atualização de status de lead.
    """
    status = serializers.ChoiceField(choices=Lead.STATUS_CHOICES)
    observacoes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_status(self, value):
        # Não permite mudar para NOVO
        if value == 'NOVO':
            raise serializers.ValidationError("Não é possível voltar o status para NOVO")
        return value
