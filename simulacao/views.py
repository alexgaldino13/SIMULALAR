import io
import os

from django.http import HttpResponse, JsonResponse
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


# ─── tabela de amortização detalhada ─────────────────────────────────────────

@api_view(["POST"])
@permission_classes([AllowAny])
def wizard_tabela_api(request):
    """
    Retorna a tabela de amortização completa (mês a mês) para um cenário.

    Body JSON:
      dados_wizard      – mesma estrutura do /wizard/calculate/
      cenario           – "price" | "sac" | "mcmv"
      crescimento_renda – % anual de aumento de salário (ex: 5.0)
    """
    dados = _payload(request)
    if not dados:
        return Response({"erro": "Nenhum dado recebido."}, status=400)

    imovel_d = dados.get("imovel_desejado") or {}
    fin = dados.get("financas_atuais") or {}
    renda_d = dados.get("trabalho_renda") or {}
    perf = dados.get("perfil_objetivos") or {}
    cen = dados.get("cenarios") or {}

    valor_imovel = float(imovel_d.get("valor_imovel_desejado", 0) or 0)
    if valor_imovel <= 0:
        return Response({"erro": "Informe o valor do imóvel."}, status=400)

    cenario = str(dados.get("cenario", "sac")).lower()
    crescimento_renda = float(dados.get("crescimento_renda", 0) or 0)
    prazo_anos = max(1, int(imovel_d.get("prazo_desejado_anos", 30) or 30))
    idade = int(perf.get("idade_comprador", 30) or 30)
    prazo_meses = min(prazo_anos * 12, (80 - idade) * 12)

    saldo_guardado = float(fin.get("saldo_dinheiro_guardado", 0) or 0)
    saldo_fgts = float(fin.get("saldo_fgts", 0) or 0)
    usar_fgts = bool(cen.get("usar_fgts", False))
    renda = float(renda_d.get("renda_familiar_bruta", 0) or 0)
    tipo_contrato = str(renda_d.get("tipo_contrato", "clt") or "clt")
    recebe_13 = bool(renda_d.get("recebe_13_salario", True))

    # Entrada e valor financiado
    entrada = saldo_guardado + (saldo_fgts if usar_fgts else 0.0)
    valor_financiado = max(0.0, valor_imovel - entrada)
    if valor_financiado <= 0:
        return Response({"erro": "Valor financiado é zero — nada a amortizar."}, status=400)

    # FGTS mensal base (sem crescimento)
    from .calculadora_financeira import calcular_fgts_mensal, _carregar_taxas
    taxas = _carregar_taxas()
    fgts_mensal = float(calcular_fgts_mensal(renda, tipo_contrato, recebe_13)) if usar_fgts else 0.0

    # Taxa conforme cenário
    if cenario == "mcmv":
        from .calculadora_financeira import verificar_mcmv
        outras_rendas = float(renda_d.get("outras_rendas", 0) or 0)
        mcmv = verificar_mcmv(renda + outras_rendas, valor_imovel)
        taxa_aa = float(mcmv["taxa_aa"]) if mcmv["elegivel"] else float(taxas["taxa_sbpe_cef"])
    elif cenario.startswith("banco_"):
        chave = cenario.replace("banco_", "taxa_sbpe_")
        taxa_aa = float(taxas.get(chave, taxas["taxa_sbpe_cef"]))
    else:
        taxa_aa = float(taxas["taxa_sbpe_cef"])

    try:
        resultado = calcular_price_sac(
            metodo="price" if cenario == "price" else "sac",
            valor_principal=valor_financiado,
            taxa_anual=taxa_aa,
            prazo_meses=prazo_meses,
            usar_fgts=usar_fgts and tipo_contrato.lower() == "clt",
            saldo_fgts_inicial=saldo_fgts if usar_fgts else 0,
            acumulo_fgts_mensal=fgts_mensal,
            tipo_amortizacao_fgts=cen.get("tipo_amortizacao_fgts", "reduzir_prazo"),
            idade=idade,
            valor_imovel=valor_imovel,
            crescimento_renda_anual_pct=crescimento_renda,
            renda_bruta_inicial=renda,
        )
        return Response({
            "cenario": cenario,
            "taxa_aa": taxa_aa,
            "valor_financiado": valor_financiado,
            "prazo_meses": resultado["prazo_final_meses"],
            "parcela_inicial": resultado["parcela_inicial"],
            "parcela_final": resultado["parcela_final"],
            "total_pago": resultado["total_pago"],
            "total_juros": resultado["total_juros"],
            "total_seguros": resultado["total_seguros_taxas"],
            "total_fgts_usado": resultado["total_fgts_usado"],
            "cet_anual": resultado["cet_anual"],
            "fgts_schedule": resultado["fgts_schedule"],
            "tabela": resultado["tabela"],
        })
    except Exception as exc:
        return Response({"erro": str(exc)}, status=500)


# ─── exportação Excel (premium) ───────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([AllowAny])
def wizard_exportar_excel_api(request):
    """
    Gera planilha Excel com tabelas de amortização para os cenários solicitados.
    Requer conta premium (verificado via token).

    Body JSON:
      dados_wizard      – mesma estrutura do wizard
      cenarios_exportar – lista ex: ["sac", "price"]
      crescimento_renda – % anual de aumento de salário
    """
    dados = _payload(request)
    if not dados:
        return Response({"erro": "Nenhum dado recebido."}, status=400)

    cenarios_exportar = dados.get("cenarios_exportar") or ["sac", "price"]
    crescimento_renda = float(dados.get("crescimento_renda", 0) or 0)

    # Verificação premium: usuário autenticado OU token de teste
    is_premium = False
    if request.user and request.user.is_authenticated:
        is_premium = True
    test_token = request.headers.get("X-Premium-Token", "")
    if test_token == os.environ.get("PREMIUM_TEST_TOKEN", ""):
        is_premium = True

    if not is_premium:
        return Response({"erro": "Recurso exclusivo para assinantes premium.", "premium_required": True}, status=402)

    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, numbers
        from openpyxl.utils import get_column_letter
    except ImportError:
        return Response({"erro": "openpyxl não instalado no servidor."}, status=500)

    imovel_d = dados.get("dados_wizard", dados).get("imovel_desejado") or {}
    fin = (dados.get("dados_wizard", dados)).get("financas_atuais") or {}
    renda_d = (dados.get("dados_wizard", dados)).get("trabalho_renda") or {}
    perf = (dados.get("dados_wizard", dados)).get("perfil_objetivos") or {}
    cen_d = (dados.get("dados_wizard", dados)).get("cenarios") or {}

    valor_imovel = float(imovel_d.get("valor_imovel_desejado", 0) or 0)
    prazo_anos = max(1, int(imovel_d.get("prazo_desejado_anos", 30) or 30))
    idade = int(perf.get("idade_comprador", 30) or 30)
    prazo_meses_orig = min(prazo_anos * 12, (80 - idade) * 12)
    saldo_guardado = float(fin.get("saldo_dinheiro_guardado", 0) or 0)
    saldo_fgts = float(fin.get("saldo_fgts", 0) or 0)
    usar_fgts = bool(cen_d.get("usar_fgts", False))
    renda = float(renda_d.get("renda_familiar_bruta", 0) or 0)
    tipo_contrato = str(renda_d.get("tipo_contrato", "clt") or "clt")
    recebe_13 = bool(renda_d.get("recebe_13_salario", True))
    entrada = saldo_guardado + (saldo_fgts if usar_fgts else 0.0)
    valor_financiado = max(0.0, valor_imovel - entrada)

    from .calculadora_financeira import calcular_fgts_mensal, _carregar_taxas, verificar_mcmv, _fmt_brl
    taxas = _carregar_taxas()
    fgts_mensal = float(calcular_fgts_mensal(renda, tipo_contrato, recebe_13)) if usar_fgts else 0.0

    wb = openpyxl.Workbook()

    # ── estilos ────────────────────────────────────────────────────────────────
    header_fill = PatternFill("solid", fgColor="1E1B4B")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    fgts_fill   = PatternFill("solid", fgColor="D1FAE5")   # verde claro
    fgts_font   = Font(bold=True, color="065F46")
    alt_fill    = PatternFill("solid", fgColor="F8F8FF")
    money_fmt   = 'R$ #,##0.00'
    pct_fmt     = '0.00%'

    def _col_widths(ws, widths):
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w

    # ── aba Resumo ─────────────────────────────────────────────────────────────
    ws_resumo = wb.active
    ws_resumo.title = "Resumo"
    resumo_headers = ["Campo", "Valor"]
    for c, h in enumerate(resumo_headers, 1):
        cell = ws_resumo.cell(1, c, h)
        cell.font = header_font; cell.fill = header_fill
    resumo_rows = [
        ("Imóvel", valor_imovel),
        ("Entrada", entrada),
        ("Valor Financiado", valor_financiado),
        ("Prazo (meses)", prazo_meses_orig),
        ("FGTS inicial", saldo_fgts),
        ("Acúmulo FGTS/mês", fgts_mensal),
        ("Crescimento Renda/ano", f"{crescimento_renda}%"),
    ]
    for r, (campo, val) in enumerate(resumo_rows, 2):
        ws_resumo.cell(r, 1, campo)
        c = ws_resumo.cell(r, 2, val)
        if isinstance(val, float):
            c.number_format = money_fmt
    _col_widths(ws_resumo, [28, 20])

    # ── abas por cenário ───────────────────────────────────────────────────────
    NOMES_CENARIO = {
        "sac": "SAC", "price": "PRICE", "mcmv": "MCMV",
        "banco_cef": "CEF SBPE", "banco_bb": "BB SBPE",
        "banco_bradesco": "Bradesco", "banco_itau": "Itaú", "banco_santander": "Santander",
    }
    COLS = ["Mês", "Data", "Parcela Total", "Amortização", "Juros", "MIP", "DFI",
            "Saldo Devedor", "FGTS Utilizado", "FGTS Saldo", "Renda Estimada"]

    for cenario in cenarios_exportar:
        # calcular taxa
        if cenario == "mcmv":
            outras_rendas = float(renda_d.get("outras_rendas", 0) or 0)
            mcmv_r = verificar_mcmv(renda + outras_rendas, valor_imovel)
            taxa_aa = float(mcmv_r["taxa_aa"]) if mcmv_r["elegivel"] else float(taxas["taxa_sbpe_cef"])
        elif cenario.startswith("banco_"):
            chave = cenario.replace("banco_", "taxa_sbpe_")
            taxa_aa = float(taxas.get(chave, taxas["taxa_sbpe_cef"]))
        else:
            taxa_aa = float(taxas["taxa_sbpe_cef"])

        res = calcular_price_sac(
            metodo="price" if cenario == "price" else "sac",
            valor_principal=valor_financiado,
            taxa_anual=taxa_aa,
            prazo_meses=prazo_meses_orig,
            usar_fgts=usar_fgts and tipo_contrato.lower() == "clt",
            saldo_fgts_inicial=saldo_fgts if usar_fgts else 0,
            acumulo_fgts_mensal=fgts_mensal,
            tipo_amortizacao_fgts=cen_d.get("tipo_amortizacao_fgts", "reduzir_prazo"),
            idade=idade,
            valor_imovel=valor_imovel,
            crescimento_renda_anual_pct=crescimento_renda,
            renda_bruta_inicial=renda,
        )

        ws = wb.create_sheet(NOMES_CENARIO.get(cenario, cenario.upper()))

        # cabeçalho
        for c, h in enumerate(COLS, 1):
            cell = ws.cell(1, c, h)
            cell.font = header_font; cell.fill = header_fill; cell.alignment = Alignment(horizontal="center")

        for r, row in enumerate(res["tabela"], 2):
            is_fgts = row["fgts_utilizado"] > 0
            fill = fgts_fill if is_fgts else (alt_fill if r % 2 == 0 else None)
            font = fgts_font if is_fgts else None

            vals = [
                row["mes"], row["data"], row["pagamento"], row["amortizacao"],
                row["juros"], row["mip"], row["dfi"], row["saldo_devedor"],
                row["fgts_utilizado"], row["fgts_saldo"],
                row.get("renda_estimada") or "",
            ]
            fmts = [None, None, money_fmt, money_fmt, money_fmt, money_fmt, money_fmt,
                    money_fmt, money_fmt, money_fmt, money_fmt]

            for c, (v, fmt) in enumerate(zip(vals, fmts), 1):
                cell = ws.cell(r, c, v)
                if fmt and isinstance(v, (int, float)):
                    cell.number_format = fmt
                if fill:
                    cell.fill = fill
                if font:
                    cell.font = font

        # totais
        tot_row = len(res["tabela"]) + 2
        ws.cell(tot_row, 2, "TOTAL")
        ws.cell(tot_row, 2).font = Font(bold=True)
        for c, key in enumerate(["pagamento", "amortizacao", "juros", "mip", "dfi",
                                  None, "fgts_utilizado"], 3):
            if key:
                val = sum(r[key] for r in res["tabela"])
                cell = ws.cell(tot_row, c, val)
                cell.number_format = money_fmt
                cell.font = Font(bold=True)

        _col_widths(ws, [6, 9, 14, 13, 12, 10, 10, 14, 14, 13, 14])
        ws.freeze_panes = "A2"

    # ── serializar e retornar ──────────────────────────────────────────────────
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    response = HttpResponse(
        buf.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="simulalar_amortizacao.xlsx"'
    return response


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
