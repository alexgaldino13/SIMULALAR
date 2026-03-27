from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .monetizacao_models import AdView, PerfilUsuario, Transacao
from .monetizacao import PremiumManager, _validate_google_purchase
import json


class SubscriptionStatusView(APIView):
    """
    Endpoint para verificar se o usuário atual é assinante Premium.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        is_premium = False
        if request.user.is_authenticated and request.user.is_active:
            pm = PremiumManager(request.user)
            is_premium = pm.eh_premium()
        
        
        return Response({"is_premium": is_premium})

class AdViewTrackingView(APIView):
    """
    Endpoint para registrar visualizações de anúncios para tracking e estatísticas.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        ad_type = request.data.get('ad_type')
        page = request.data.get('page')
        
        if not ad_type or not page:
            return Response({"error": "ad_type e page são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)
            
        AdView.objects.create(
            user=request.user if request.user.is_authenticated else None,
            ad_type=ad_type,
            page=page
        )
        
        return Response({"status": "success"}, status=status.HTTP_201_CREATED)


class GooglePlayBillingWebhookView(APIView):
    """
    Endpoint para receber e validar notificações de compra do Google Play Billing.
    """
    permission_classes = [AllowAny] # Google Play não autentica com usuário do app

    def post(self, request):
        # Google Play envia dados em um formato específico, geralmente JSON
        # Exemplo de dados esperados (simplificado):
        # {
        #   "packageName": "com.ficalc.app",
        #   "productId": "com.ficalc.premium.mensal",
        #   "purchaseToken": "some_purchase_token_from_google",
        #   "userId": "user_id_from_your_app_if_available"
        # }
        
        package_name = request.data.get('packageName')
        product_id = request.data.get('productId')
        purchase_token = request.data.get('purchaseToken')
        user_id = request.data.get('userId') # Pode ser o ID do usuário do seu app

        if not all([package_name, product_id, purchase_token]):
            return Response({"error": "Dados de compra incompletos."}, status=status.HTTP_400_BAD_REQUEST)

        # Tentar encontrar o usuário pelo ID (se enviado pelo app)
        user = None
        if user_id:
            try:
                user = settings.AUTH_USER_MODEL.objects.get(id=user_id)
            except settings.AUTH_USER_MODEL.DoesNotExist:
                pass # Usuário não encontrado, pode ser um erro ou notificação sem user_id

        # Validação com a API do Google Play (simulada por enquanto)
        if _validate_google_purchase(purchase_token, product_id, package_name):
            if user:
                pm = PremiumManager(user)
                pm.ativar_premium(product_id, purchase_token)
            return Response({"status": "success", "message": "Compra validada e premium ativado."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Falha na validação da compra com o Google Play."}, status=status.HTTP_400_BAD_REQUEST)