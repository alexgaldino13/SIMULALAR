from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import SavedSimulation, UserProfile
from .serializers import UserProfileSerializer, SavedSimulationSerializer, WizardSimulationSerializer

class APIDashboardView(APIView):
    """
    Retorna os dados principais para o dashboard do aplicativo móvel.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = getattr(user, 'profile', None)
        if not profile:
            profile = UserProfile.objects.create(user=user)

        recent_simulations = SavedSimulation.objects.filter(user=user).order_by('-criado_em')[:5]
        total_simulations = SavedSimulation.objects.filter(user=user).count()

        data = {
            'profile': UserProfileSerializer(profile).data,
            'recent_simulations': SavedSimulationSerializer(recent_simulations, many=True).data,
            'total_simulations': total_simulations,
        }

        return Response(data, status=status.HTTP_200_OK)


class APISaveSimulationView(APIView):
    """
    Salva uma nova simulação enviada pelo mobile.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        
        # O mobile envia dados_wizard e resultados
        titulo = request.data.get('titulo', f"Simulalar - {user.first_name}")
        dados_wizard = request.data.get('dados_wizard')
        resultados = request.data.get('resultados')

        if not dados_wizard or not resultados:
            return Response(
                {'error': 'Dados incompletos para salvar a simulação.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        simulacao = SavedSimulation.objects.create(
            user=user,
            titulo=titulo,
            dados_wizard=dados_wizard,
            resultados=resultados
        )

        return Response(
            {'message': 'Simulação salva com sucesso!', 'id': simulacao.id},
            status=status.HTTP_201_CREATED
        )


class APIDeleteSimulationView(APIView):
    """
    Exclui uma simulação salva pelo usuário.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            simulacao = SavedSimulation.objects.get(pk=pk, user=request.user)
            simulacao.delete()
            return Response({'message': 'Simulação excluída com sucesso!'}, status=status.HTTP_204_NO_CONTENT)
        except SavedSimulation.DoesNotExist:
            return Response({'error': 'Simulação não encontrada ou você não tem permissão.'}, status=status.HTTP_404_NOT_FOUND)
class APISimulationListView(APIView):
    """
    Retorna a lista completa de todas as simulações salvas pelo usuário.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        simulations = SavedSimulation.objects.filter(user=user).order_by('-criado_em')
        serializer = SavedSimulationSerializer(simulations, many=True)
        return Response({'simulations': serializer.data}, status=status.HTTP_200_OK)
