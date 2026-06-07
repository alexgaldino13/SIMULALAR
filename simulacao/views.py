import os

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .calculadora_financeira import (
    calcular_price_sac,
    calcular_cet,
    simular_consorcio,
    comparar_cenarios_e_formatar,
)
from .models import ParametroMercado, SavedSimulation

# Token secreto para o endpoint de atualização de índices (Railway cron)
_BCB_UPDATE_TOKEN = os.environ.get("BCB_UPDATE_TOKEN", "")

PARAMETROS_MERCADO_FALLBACK = {
    "selic": {"nome": "SELIC", "valor": 13.75, "unidade": "percentual", "descricao": "Taxa básica de juros do Brasil."},
    "ipca": {"nome": "IPCA", "valor": 4.83, "unidade": "percentual", "descricao": "Inflação oficial (IPCA) projetada."},
    "tr": {"nome": "TR", "valor": 0.0832, "unidade": "mensal", "descricao": "Taxa Referencial mensal."},
    "iof": {"nome": "IOF", "valor": 0.000938, "unidade": "mensal", "descricao": "Imposto sobre operações financeiras."},
    "itbi": {"nome": "ITBI", "valor": 2.5, "unidade": "percentual", "descricao": "ITBI médio nacional."},
    "taxa_sbpe": {"nome": "Taxa SBPE (CEF)", "valor": 10.49, "unidade": "percentual_aa", "descricao": "Taxa SBPE CEF de referência."},
}


def _payload(request):
    try:
        return request.data if hasattr(request, "data") else request.POST.dict()
    except Exception:
        return {}


# ─── endpoints simples ────────────────────────────────────────────────────────

@require_http_methods(["GET", "POST"])
def api_assinatura_status(request):
    return JsonResponse({"status": "free"})


@require_http_methods(["POST"])
def api_capturar_lead(request):
    return JsonResponse({"captured": True})


@require_http_methods(["POST"])
def api_registrar_ad_view(request):
    return JsonResponse({"registered": True})


# ─── parâmetros de mercado ────────────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([AllowAny])
def parametros_mercado_api(request):
    params = ParametroMercado.get_current_values(fallback=PARAMETROS_MERCADO_FALLBACK)
    return Response(params)


# ─── calculadoras avulsas ─────────────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([AllowAny])
def calcular_price_sac_api(request):
    p = _payload(request)
    resultado = calcular_price_sac(
        p.get("metodo", "price"),
        p.get("valor_principal", 0),
        p.get("taxa_anual", 0),
        p.get("prazo_meses", 1),
        seguro_mensal=p.get("seguro_mensal", 0.0),
        taxa_admin_mensal=p.get("taxa_admin_mensal", 0.0),
        tr_mensal=p.get("tr_mensal", 0.0),
        usar_fgts=p.get("usar_fgts", False),
        saldo_fgts_inicial=p.get("saldo_fgts_inicial", 0.0),
        acumulo_fgts_mensal=p.get("acumulo_fgts_mensal", 0.0),
        tipo_amortizacao_fgts=p.get("tipo_amortizacao_fgts", "reduzir_prazo"),
        idade=p.get("idade", 30),
        valor_imovel=p.get("valor_imovel"),
    )
    return Response(resultado)


@api_view(["POST"])
@permission_classes([AllowAny])
def simular_consorcio_api(request):
    p = _payload(request)
    resultado = simular_consorcio(
        p.get("valor_imovel", 0),
        p.get("prazo_meses", 1),
        p.get("taxa_adm", 18.0),
        p.get("fundo_reserva", 1.0),
        p.get("fgts_saldo", 0.0),
        lance_percentual=p.get("lance_percentual", 0.0),
    )
    return Response(resultado)


@api_view(["POST"])
@permission_classes([AllowAny])
def calcular_cet_api(request):
    p = _payload(request)
    resultado = calcular_cet(
        p.get("valor_financiado", 0),
        p.get("parcelas_mensais", []),
        p.get("custos_iniciais", 0.0),
    )
    return Response(resultado)


@api_view(["POST"])
@permission_classes([AllowAny])
def comparar_cenarios_api(request):
    p = _payload(request)
    resultado = comparar_cenarios_e_formatar(p)
    return Response(resultado)


# ─── endpoint principal do wizard ─────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([AllowAny])
def wizard_calculate_api(request):
    """
    Recebe os dados das 5 etapas do wizard e retorna comparação
    formatada para o ResultsScreen do app mobile.
    """
    dados = _payload(request)

    if not dados:
        return Response({"erro": "Nenhum dado recebido."}, status=400)

    valor_imovel = float(
        (dados.get("imovel_desejado") or {}).get("valor_imovel_desejado", 0) or 0
    )
    if valor_imovel <= 0:
        return Response(
            {"erro": "Informe o valor do imóvel (imovel_desejado.valor_imovel_desejado)."},
            status=400,
        )

    try:
        resultado = comparar_cenarios_e_formatar(dados)
        for cenario in resultado.get("resultados", {}).values():
            cenario.pop("tabela", None)
        return Response(resultado)
    except Exception as exc:
        return Response({"erro": f"Erro no cálculo: {str(exc)}"}, status=500)


# ─── atualização de índices BCB (cron Railway) ───────────────────────────────

@api_view(["POST"])
@permission_classes([AllowAny])
def atualizar_indices_bcb_api(request):
    """
    Endpoint para o cron do Railway chamar e manter os índices atualizados.
    Autenticado via header X-BCB-Token ou query param token.
    Chama o management command atualizar_indices_bcb internamente.
    """
    token_recebido = (
        request.headers.get("X-BCB-Token", "")
        or request.query_params.get("token", "")
    )

    if _BCB_UPDATE_TOKEN and token_recebido != _BCB_UPDATE_TOKEN:
        return Response({"erro": "Token inválido."}, status=403)

    try:
        from django.core.management import call_command
        from io import StringIO
        out = StringIO()
        call_command("atualizar_indices_bcb", stdout=out, stderr=out)
        return Response({"status": "ok", "log": out.getvalue()})
    except Exception as exc:
        return Response({"erro": str(exc)}, status=500)


# ─── simulações salvas ────────────────────────────────────────────────────────

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def saved_simulations_api(request):
    if request.method == "GET":
        sims = SavedSimulation.objects.filter(user=request.user).order_by("-criado_em")[:20]
        data = [
            {
                "id": s.id,
                "titulo": s.titulo,
                "criado_em": s.criado_em.isoformat(),
                "is_favorito": s.is_favorito,
                "valor_imovel": (s.dados_wizard.get("imovel_desejado") or {}).get(
                    "valor_imovel_desejado", 0
                ),
            }
            for s in sims
        ]
        return Response(data)

    p = _payload(request)
    titulo = p.get("titulo", "Minha Simulação")
    dados_wizard = p.get("dados_wizard", {})
    resultados = p.get("resultados", {})

    if not dados_wizard:
        return Response({"erro": "dados_wizard é obrigatório."}, status=400)

    sim = SavedSimulation.objects.create(
        user=request.user,
        titulo=titulo,
        dados_wizard=dados_wizard,
        resultados=resultados,
    )
    return Response(
        {"id": sim.id, "titulo": sim.titulo, "criado_em": sim.criado_em.isoformat()},
        status=201,
    )


@api_view(["GET", "DELETE"])
@permission_classes([IsAuthenticated])
def saved_simulation_detail_api(request, pk):
    try:
        sim = SavedSimulation.objects.get(pk=pk, user=request.user)
    except SavedSimulation.DoesNotExist:
        return Response({"erro": "Simulação não encontrada."}, status=404)

    if request.method == "DELETE":
        sim.delete()
        return Response(status=204)

    return Response({
        "id": sim.id,
        "titulo": sim.titulo,
        "criado_em": sim.criado_em.isoformat(),
        "dados_wizard": sim.dados_wizard,
        "resultados": sim.resultados,
        "is_favorito": sim.is_favorito,
        "notas": sim.notas,
    })
