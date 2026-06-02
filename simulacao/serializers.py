from rest_framework import serializers
from .models import CustomUser, UserProfile, SavedSimulation
from django.db import transaction

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de novos usuários via API.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name', 'telefone']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")
        
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Este e-mail já está cadastrado.")
            
        return data

    def create(self, validated_data):
        # Remove a confirmação de senha antes de criar o usuário
        validated_data.pop('password_confirm')
        
        with transaction.atomic():
            user = CustomUser.objects.create_user(
                username=validated_data['email'],
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
                telefone=validated_data.get('telefone', ''),
                aceitou_termos=True,
                aceitou_privacidade=True,
            )
            # Cria o perfil automaticamente
            UserProfile.objects.create(user=user)
            
        return user


# --- SERALIZERS PARA O WIZARD ---

class WizardStep1Serializer(serializers.Serializer):
    perfil_usuario = serializers.ChoiceField(choices=[
        ('comprador_morar', '🏠 Comprador - Quero morar no imóvel'),
        ('investidor', '💼 Investidor - Quero alugar/revender'),
        ('corretor', '🏢 Corretor de imóveis - Orientar clientes'),
        ('vendedor_consorcio', '🎲 Vendedor de consórcio - Mostrar viabilidade'),
        ('explorando', '📊 Só estou explorando possibilidades'),
    ])
    prioridade_principal = serializers.ChoiceField(choices=[
        ('pagar_menos', '💰 Pagar o menor valor total (economia máxima)'),
        ('parcelas_suaves', '📉 Prestações mais suaves (cabe no bolso)'),
        ('quitar_rapido', '⏱️ Quitar rápido (menor prazo possível)'),
        ('flexibilidade', '🔄 Flexibilidade (poder trocar/vender facilmente)'),
        ('equilibrio', '⚖️ Equilíbrio (bom custo-benefício geral)'),
    ])
    onde_mora_atualmente = serializers.ChoiceField(choices=[
        ('aluga', 'Aluga imóvel'),
        ('pais', 'Mora com pais/parentes'),
        ('proprio', 'Tem imóvel próprio'),
        ('favor', 'Mora de favor'),
    ])
    aluguel_atual = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    tempo_mora_atualmente = serializers.CharField(max_length=50, required=False)
    idade_comprador = serializers.IntegerField(min_value=18, max_value=100, default=30)

class WizardStep2Serializer(serializers.Serializer):
    renda_familiar_bruta = serializers.DecimalField(max_digits=15, decimal_places=2)
    tipo_contrato = serializers.ChoiceField(choices=[
        ('clt', 'CLT'),
        ('autonomo', 'Autônomo'),
        ('empresario', 'Empresário'),
        ('aposentado', 'Aposentado'),
        ('outro', 'Outro'),
    ])
    renda_estavel = serializers.CharField(max_length=50, required=False, default='estavel')
    recebe_13_salario = serializers.BooleanField(default=True)
    quantos_dependentes = serializers.IntegerField(min_value=0, default=1)
    tipo_trabalho = serializers.CharField(max_length=50, required=False, default='privado')
    outras_rendas = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, default=0)

class WizardStep3Serializer(serializers.Serializer):
    valor_imovel_proprio = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, default=0)
    saldo_dinheiro_guardado = serializers.DecimalField(max_digits=15, decimal_places=2)
    saldo_fgts = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, default=0)
    despesas_mensais_fixas = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, default=0)

class WizardStep4Serializer(serializers.Serializer):
    valor_imovel_desejado = serializers.DecimalField(max_digits=15, decimal_places=2)
    prazo_desejado_anos = serializers.IntegerField(min_value=5, max_value=40)
    custas_documentacao_forma = serializers.ChoiceField(choices=[('a_vista', 'À vista'), ('financiado', 'Financiado')])

class WizardStep5Serializer(serializers.Serializer):
    comparar_financiamento_price = serializers.BooleanField(default=True)
    comparar_financiamento_sac = serializers.BooleanField(default=True)
    comparar_consorcio = serializers.BooleanField(default=True)
    prazo_consorcio = serializers.ChoiceField(choices=[('120', '120'), ('150', '150'), ('180', '180'), ('200', '200')], required=False)
    estrategia_contemplacao = serializers.ChoiceField(choices=[('sorteio', 'Sorteio'), ('lance_unico', 'Lance Único'), ('lances_mensais', 'Lances')], required=False)
    valor_lance_disponivel = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, default=0)
    tempo_maximo_espera_consorcio = serializers.IntegerField(required=False, default=36)
    comparar_mcmv = serializers.BooleanField(default=False)
    comparar_aluguel_investimento = serializers.BooleanField(default=True)
    comparar_compra_a_vista = serializers.BooleanField(default=False)
    comparar_guardar_dinheiro = serializers.BooleanField(default=True)
    pagar_aluguel_com_rendimentos = serializers.BooleanField(default=False)
    usar_fgts = serializers.BooleanField(default=True)
    taxa_investimento_esperada = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, default=9.5)

class WizardSimulationSerializer(serializers.Serializer):
    """
    Serializer mestre que contém todas as etapas.
    """
    perfil_objetivos = WizardStep1Serializer()
    trabalho_renda = WizardStep2Serializer()
    financas_atuais = WizardStep3Serializer()
    imovel_desejado = WizardStep4Serializer()
    cenarios = WizardStep5Serializer()


# --- SERALIZERS PARA DASHBOARD E PERFIL ---

class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    is_premium = serializers.BooleanField(source='user.is_premium', read_only=True)
    tipo_conta = serializers.CharField(source='user.tipo_conta', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'first_name', 'email', 'is_premium', 'tipo_conta',
            'creci', 'nome_empresa', 'logo_empresa', 'avatar'
        ]

class SavedSimulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedSimulation
        fields = ['id', 'titulo', 'dados_wizard', 'resultados', 'criado_em', 'is_favorito', 'notas']
        read_only_fields = ['criado_em']

class DashboardDataSerializer(serializers.Serializer):
    profile = UserProfileSerializer()
    recent_simulations = SavedSimulationSerializer(many=True)
    total_simulations = serializers.IntegerField()
    premium_until = serializers.DateTimeField(source='user.premium_expira_em', read_only=True)
