"""
Motor de cálculo financeiro imobiliário — ImobCalc
Regras do mercado brasileiro 2025/2026.

Referências:
  - SFH/SFI: Lei 4.380/64, Resolução CMN 4.676/2018
  - MCMV: Lei 14.118/2021, Portaria MDR vigente
  - FGTS: Lei 8.036/90, Circular CEF 820/2017
  - Seguros MIP/DFI: Circular SUSEP 399/2009
"""
from __future__ import annotations

import math
from decimal import ROUND_HALF_UP, Decimal, getcontext
from typing import Any, Dict, List, Optional, Tuple

getcontext().prec = 28

_ZERO = Decimal("0")
_CENT = Decimal("0.01")


# ─── índices de mercado (fallback + carregamento do DB) ───────────────────────

def _carregar_taxas() -> Dict[str, Decimal]:
    """
    Carrega taxas do ParametroMercado (DB) com fallback para constantes.
    Django ORM só é importado aqui para evitar import circular no nível do módulo.
    """
    _defaults: Dict[str, Decimal] = {
        "selic":               Decimal("14.75"),
        "ipca":                Decimal("5.53"),
        "tr":                  Decimal("0.0832"),
        "taxa_sbpe_cef":       Decimal("10.49"),
        "taxa_sbpe_bb":        Decimal("10.99"),
        "taxa_sbpe_bradesco":  Decimal("11.19"),
        "taxa_sbpe_itau":      Decimal("10.99"),
        "taxa_sbpe_santander": Decimal("11.49"),
        "mcmv_faixa1_taxa":    Decimal("4.75"),
        "mcmv_faixa2_taxa":    Decimal("6.50"),
        "mcmv_faixa3_taxa":    Decimal("7.66"),
        "mcmv_faixa1_renda_max": Decimal("2850"),
        "mcmv_faixa2_renda_max": Decimal("4400"),
        "mcmv_faixa3_renda_max": Decimal("8000"),
        "sfh_valor_max":       Decimal("1500000"),
    }
    try:
        from simulacao.models import ParametroMercado  # noqa: PLC0415
        qs = ParametroMercado.objects.filter(ativo=True).values("chave", "valor")
        for row in qs:
            if row["chave"] in _defaults:
                _defaults[row["chave"]] = Decimal(str(row["valor"]))
    except Exception:
        pass
    return _defaults


# ─── helpers ──────────────────────────────────────────────────────────────────

def _d(x) -> Decimal:
    if isinstance(x, Decimal):
        return x
    if x is None:
        return _ZERO
    try:
        return Decimal(str(x))
    except Exception:
        return _ZERO


def _q(x, places: int = 2) -> Decimal:
    fmt = Decimal("0." + "0" * places)
    return _d(x).quantize(fmt, rounding=ROUND_HALF_UP)


def _fmt_brl(v) -> str:
    f = float(_d(v))
    s = f"{f:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def _fmt_pct(v, decimals: int = 2) -> str:
    return f"{float(_d(v)):.{decimals}f}%".replace(".", ",")


def _pmt(pv: Decimal, r: Decimal, n: int) -> Decimal:
    """Parcela PRICE (sistema francês de amortização)."""
    if r == _ZERO:
        return _q(pv / n) if n > 0 else _ZERO
    factor = (1 + r) ** n
    return _q(pv * (r * factor) / (factor - 1))


# ─── tabelas de mercado ────────────────────────────────────────────────────────

# MIP: seguro de vida mensal (% sobre saldo devedor)
_MIP_TABELA: List[Tuple[int, Decimal]] = [
    (25, Decimal("0.009")),
    (30, Decimal("0.011")),
    (35, Decimal("0.018")),
    (40, Decimal("0.022")),
    (45, Decimal("0.032")),
    (50, Decimal("0.056")),
    (55, Decimal("0.082")),
    (60, Decimal("0.135")),
    (70, Decimal("0.165")),
    (999, Decimal("0.280")),
]

# ITBI por estado (alíquotas municipais típicas de capitais)
_ITBI_ESTADO: Dict[str, Decimal] = {
    "SP": Decimal("3.0"),  "RJ": Decimal("2.0"),  "MG": Decimal("3.0"),
    "RS": Decimal("3.0"),  "PR": Decimal("2.7"),  "SC": Decimal("2.0"),
    "BA": Decimal("2.0"),  "PE": Decimal("3.0"),  "CE": Decimal("2.0"),
    "GO": Decimal("2.0"),  "DF": Decimal("3.0"),  "AM": Decimal("2.0"),
    "PA": Decimal("2.0"),  "MT": Decimal("2.0"),  "MS": Decimal("2.0"),
    "ES": Decimal("2.0"),  "MA": Decimal("2.0"),  "PI": Decimal("2.0"),
    "RN": Decimal("3.0"),  "PB": Decimal("2.0"),  "AL": Decimal("2.0"),
    "SE": Decimal("2.0"),  "RO": Decimal("2.0"),  "TO": Decimal("2.0"),
    "AC": Decimal("2.0"),  "RR": Decimal("2.0"),  "AP": Decimal("2.0"),
}

# MCMV 2025/2026 — Portaria MDR vigente
_MCMV_FAIXAS = [
    {
        "faixa": 1,
        "nome": "Faixa 1",
        "renda_max": Decimal("2850"),
        "taxa_aa": Decimal("4.75"),
        "entrada_min_pct": Decimal("5"),
        "teto_capital": Decimal("190000"),
        "teto_interior": Decimal("130000"),
        "descricao": "Subsídio máximo do governo. Taxa a partir de 4,75% a.a.",
    },
    {
        "faixa": 2,
        "nome": "Faixa 2",
        "renda_max": Decimal("4400"),
        "taxa_aa": Decimal("6.5"),
        "entrada_min_pct": Decimal("10"),
        "teto_capital": Decimal("264000"),
        "teto_interior": Decimal("264000"),
        "descricao": "Subsídio parcial. Taxa a partir de 6,5% a.a.",
    },
    {
        "faixa": 3,
        "nome": "Faixa 3",
        "renda_max": Decimal("8000"),
        "taxa_aa": Decimal("7.66"),
        "entrada_min_pct": Decimal("10"),
        "teto_capital": Decimal("350000"),
        "teto_interior": Decimal("264000"),
        "descricao": "Taxa subsidiada CEF. Capitais SP, RJ, DF e ES têm teto maior.",
    },
]

TAXA_SBPE_AA = Decimal("10.49")      # CEF SBPE referência 2025
SFH_VALOR_MAX = Decimal("1500000")   # teto do imóvel no SFH
DFI_TAXA_ANUAL_PCT = Decimal("0.025")  # 0,025% a.a. do valor do imóvel


# ─── seguros ──────────────────────────────────────────────────────────────────

def calcular_mip_taxa(idade: int) -> Decimal:
    """Taxa mensal MIP (% sobre saldo devedor) pela faixa etária."""
    for limite, taxa in _MIP_TABELA:
        if int(idade) <= limite:
            return taxa
    return Decimal("0.280")


def calcular_dfi_mensal(valor_imovel: Decimal) -> Decimal:
    """DFI: 0,025% a.a. sobre o valor do imóvel, cobrado mensalmente."""
    return _q(valor_imovel * DFI_TAXA_ANUAL_PCT / Decimal("100") / Decimal("12"))


# ─── custas de aquisição ──────────────────────────────────────────────────────

def calcular_custas_iniciais(
    valor_imovel,
    estado: str = "SP",
    cidade_tipo: str = "capital",
    financiar: bool = False,
) -> Dict[str, Any]:
    """Estima ITBI, cartório, escritura e avaliação bancária."""
    V = _d(valor_imovel)
    itbi_pct = _ITBI_ESTADO.get(estado.upper(), Decimal("2.5")) / Decimal("100")
    itbi = _q(V * itbi_pct)
    cartorio = _q(V * Decimal("0.01"))
    escritura = _q(V * Decimal("0.005"))
    avaliacao = _q(Decimal("1000"))
    total = itbi + cartorio + escritura + avaliacao

    return {
        "itbi": float(itbi),
        "itbi_pct": float(itbi_pct * 100),
        "itbi_fmt": _fmt_brl(itbi),
        "cartorio_registro": float(cartorio),
        "cartorio_fmt": _fmt_brl(cartorio),
        "escritura": float(escritura),
        "escritura_fmt": _fmt_brl(escritura),
        "avaliacao_bancaria": float(avaliacao),
        "total": float(total),
        "total_fmt": _fmt_brl(total),
        "financiado": financiar,
        "nota": (
            "Custas pagas separadamente — não reduzem sua entrada."
            if financiar
            else "Custas pagas à vista — descontadas do seu capital disponível."
        ),
    }


# ─── MCMV ────────────────────────────────────────────────────────────────────

def verificar_mcmv(
    renda_familiar,
    valor_imovel,
    cidade_tipo: str = "capital",
    taxas_vivas: Optional[Dict[str, Decimal]] = None,
) -> Dict[str, Any]:
    """Verifica elegibilidade ao MCMV e retorna faixa, taxa e teto."""
    renda = _d(renda_familiar)
    valor = _d(valor_imovel)

    # Permite sobrescrever taxas/rendas via DB
    faixas = _MCMV_FAIXAS
    if taxas_vivas:
        faixas = [
            {**_MCMV_FAIXAS[0], "renda_max": taxas_vivas.get("mcmv_faixa1_renda_max", _MCMV_FAIXAS[0]["renda_max"]), "taxa_aa": taxas_vivas.get("mcmv_faixa1_taxa", _MCMV_FAIXAS[0]["taxa_aa"])},
            {**_MCMV_FAIXAS[1], "renda_max": taxas_vivas.get("mcmv_faixa2_renda_max", _MCMV_FAIXAS[1]["renda_max"]), "taxa_aa": taxas_vivas.get("mcmv_faixa2_taxa", _MCMV_FAIXAS[1]["taxa_aa"])},
            {**_MCMV_FAIXAS[2], "renda_max": taxas_vivas.get("mcmv_faixa3_renda_max", _MCMV_FAIXAS[2]["renda_max"]), "taxa_aa": taxas_vivas.get("mcmv_faixa3_taxa", _MCMV_FAIXAS[2]["taxa_aa"])},
        ]

    for f in faixas:
        if renda <= f["renda_max"]:
            teto = f["teto_capital"] if cidade_tipo == "capital" else f["teto_interior"]
            if valor <= teto:
                return {
                    "elegivel": True,
                    "faixa": f["faixa"],
                    "nome_faixa": f["nome"],
                    "taxa_aa": float(f["taxa_aa"]),
                    "entrada_min_pct": float(f["entrada_min_pct"]),
                    "teto_imovel": float(teto),
                    "descricao": f["descricao"],
                    "motivo": None,
                }

    if renda > faixas[-1]["renda_max"]:
        motivo = (
            f"Renda familiar {_fmt_brl(renda)}/mês acima do limite MCMV "
            f"({_fmt_brl(faixas[-1]['renda_max'])}/mês)."
        )
    else:
        teto_ref = faixas[-1]["teto_capital"]
        motivo = (
            f"Valor do imóvel {_fmt_brl(valor)} acima do teto MCMV "
            f"({_fmt_brl(teto_ref)}) para sua faixa de renda."
        )

    return {
        "elegivel": False,
        "faixa": None,
        "nome_faixa": None,
        "taxa_aa": None,
        "entrada_min_pct": 20.0,
        "teto_imovel": None,
        "descricao": None,
        "motivo": motivo,
    }


# ─── FGTS ────────────────────────────────────────────────────────────────────

def calcular_fgts_mensal(
    renda_bruta,
    tipo_contrato: str,
    recebe_13: bool = True,
) -> Decimal:
    """Acúmulo mensal de FGTS (8% da renda CLT + proporcional do 13º)."""
    if tipo_contrato.lower() not in ("clt",):
        return _ZERO
    renda = _d(renda_bruta)
    base = renda * Decimal("0.08")
    if recebe_13:
        base = base * Decimal("13") / Decimal("12")
    return _q(base)


# ─── calculadora SAC / PRICE ─────────────────────────────────────────────────

def calcular_price_sac(
    metodo: str,
    valor_principal,
    taxa_anual,
    prazo_meses,
    seguro_mensal: float = 0.0,
    taxa_admin_mensal: float = 0.0,
    tr_mensal: float = 0.0,
    usar_fgts: bool = False,
    saldo_fgts_inicial: float = 0.0,
    acumulo_fgts_mensal: float = 0.0,
    tipo_amortizacao_fgts: str = "reduzir_prazo",
    idade: int = 30,
    valor_imovel=None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Calcula tabela de amortização SAC ou PRICE com seguros MIP/DFI e FGTS.

    FGTS é aplicado a cada 24 meses (regra CEF/SFH).
    tipo_amortizacao_fgts: 'reduzir_prazo' | 'reduzir_parcela'
    """
    PV = _d(valor_principal)
    n_orig = max(1, int(prazo_meses))
    r_aa = _d(taxa_anual) / Decimal("100")
    r_m = r_aa / Decimal("12")
    tr = _d(tr_mensal)
    taxa_admin = _d(taxa_admin_mensal)
    VI = _d(valor_imovel) if valor_imovel else PV

    mip_taxa = calcular_mip_taxa(max(18, int(idade)))
    dfi_mes = calcular_dfi_mensal(VI)
    seg_extra = _d(seguro_mensal)

    saldo = PV
    fgts_bal = _d(saldo_fgts_inicial)
    fgts_acum = _d(acumulo_fgts_mensal)

    tabela: List[Dict[str, Any]] = []
    total_juros = _ZERO
    total_seguros = _ZERO
    total_admin_sum = _ZERO

    cap = n_orig * 2 + 1

    if metodo.lower() == "price":
        pmt_base = _pmt(PV, r_m, n_orig)

        for p in range(1, cap):
            if saldo < _d("0.01"):
                break
            fgts_bal += fgts_acum

            juros = _q(saldo * r_m)
            amort = _q(pmt_base - juros)
            if amort <= _ZERO:
                amort = _q(saldo)
            amort = min(amort, saldo)

            mip = _q(saldo * mip_taxa / Decimal("100"))
            pag_total = _q(pmt_base + mip + dfi_mes + seg_extra + taxa_admin)

            saldo -= amort
            if tr > _ZERO:
                saldo = _q(saldo * (1 + tr))

            tabela.append({
                "periodo": p,
                "pagamento": float(pag_total),
                "juros": float(juros),
                "amortizacao": float(amort),
                "mip": float(mip),
                "dfi": float(dfi_mes),
                "saldo": float(max(saldo, _ZERO)),
            })
            total_juros += juros
            total_seguros += mip + dfi_mes
            total_admin_sum += taxa_admin

            if usar_fgts and p % 24 == 0 and fgts_bal > _ZERO and saldo > _d("1"):
                fgts_usado = min(fgts_bal, saldo)
                saldo -= _q(fgts_usado)
                fgts_bal = _ZERO
                meses_rest = n_orig - p
                if meses_rest > 0 and saldo > _ZERO and tipo_amortizacao_fgts == "reduzir_parcela":
                    pmt_base = _pmt(saldo, r_m, meses_rest)

    else:  # SAC
        amort_const = _q(PV / n_orig) if n_orig > 0 else PV

        for p in range(1, cap):
            if saldo < _d("0.01"):
                break
            fgts_bal += fgts_acum

            juros = _q(saldo * r_m)
            amort = min(amort_const, saldo)

            mip = _q(saldo * mip_taxa / Decimal("100"))
            pag_total = _q(amort + juros + mip + dfi_mes + seg_extra + taxa_admin)

            saldo -= amort
            if tr > _ZERO:
                saldo = _q(saldo * (1 + tr))

            tabela.append({
                "periodo": p,
                "pagamento": float(pag_total),
                "juros": float(juros),
                "amortizacao": float(amort),
                "mip": float(mip),
                "dfi": float(dfi_mes),
                "saldo": float(max(saldo, _ZERO)),
            })
            total_juros += juros
            total_seguros += mip + dfi_mes
            total_admin_sum += taxa_admin

            if usar_fgts and p % 24 == 0 and fgts_bal > _ZERO and saldo > _d("1"):
                fgts_usado = min(fgts_bal, saldo)
                saldo -= _q(fgts_usado)
                fgts_bal = _ZERO
                meses_rest = n_orig - p
                if meses_rest > 0 and saldo > _ZERO and tipo_amortizacao_fgts == "reduzir_parcela":
                    amort_const = _q(saldo / meses_rest)

    prazo_final = len(tabela)
    total_pago = float(_q(sum(r["pagamento"] for r in tabela)))
    parcela_ini = tabela[0]["pagamento"] if tabela else 0.0
    parcela_fin = tabela[-1]["pagamento"] if tabela else 0.0

    fluxos = [r["pagamento"] for r in tabela]
    cet_info = calcular_cet(float(PV), fluxos)

    return {
        "tabela": tabela,
        "parcela_inicial": float(_q(parcela_ini)),
        "parcela_final": float(_q(parcela_fin)),
        "total_juros": float(_q(total_juros)),
        "total_seguros_taxas": float(_q(total_seguros + total_admin_sum)),
        "total_pago": total_pago,
        "prazo_final_meses": prazo_final,
        "cet_anual": cet_info.get("cet_anual", 0.0),
        "saldo_final": float(_q(tabela[-1]["saldo"] if tabela else _ZERO)),
    }


# ─── consórcio ───────────────────────────────────────────────────────────────

def simular_consorcio(
    valor_imovel,
    prazo_meses,
    taxa_adm: float = 18.0,
    fundo_reserva: float = 1.0,
    fgts_saldo: float = 0.0,
    lance_percentual: float = 0.0,
    tipo_lance: str = "fixo",
    tempo_espera_meses: int = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Simula consórcio imobiliário com ou sem lance.

    taxa_adm: % total sobre o prazo (ex: 18 = 18% do valor total)
    fundo_reserva: % sobre o valor do imóvel
    lance_percentual: % do valor da carta disponível como lance
    """
    V = _d(valor_imovel)
    n = max(1, int(prazo_meses))
    taxa = _d(taxa_adm) / Decimal("100")
    fundo = _d(fundo_reserva) / Decimal("100")
    lance_pct = _d(lance_percentual) / Decimal("100")
    fgts = _d(fgts_saldo)

    total_taxa_adm = _q(V * taxa)
    total_fundo = _q(V * fundo)
    total_consorcio = V + total_taxa_adm + total_fundo

    parcela = _q(total_consorcio / n)

    lance_valor = _q(V * lance_pct) + fgts
    lance_efetivo_pct = float(lance_valor / V * 100) if V > _ZERO else 0.0

    if lance_valor > _ZERO and lance_efetivo_pct >= 20:
        meses_contemplacao = max(6, int(n * 0.15))
    else:
        meses_contemplacao = (
            int(tempo_espera_meses)
            if tempo_espera_meses and tempo_espera_meses > 0
            else int(n * 0.45)
        )

    lance_abate = min(lance_valor, V)
    total_pago = float(_q(total_consorcio + lance_abate))

    tabela = [{"periodo": i + 1, "parcela": float(parcela)} for i in range(n)]

    return {
        "tabela": tabela,
        "parcela": float(parcela),
        "total_pago": total_pago,
        "total_taxa_adm": float(total_taxa_adm),
        "total_fundo_reserva": float(total_fundo),
        "meses_contemplacao_estimado": meses_contemplacao,
        "anos_contemplacao_estimado": round(meses_contemplacao / 12, 1),
        "lance_valor": float(lance_valor),
        "lance_pct": lance_efetivo_pct,
        "carta_credito": float(V),
    }


def simular_consorcio_com_lances(*args, **kwargs) -> Dict[str, Any]:
    return simular_consorcio(*args, **kwargs)


# ─── aluguel + investimento ───────────────────────────────────────────────────

def simular_aluguel_investimento(
    valor_imovel,
    aluguel_atual,
    saldo_inicial,
    aporte_mensal,
    taxa_investimento_anual,
    prazo_anos: int = 30,
    ipca_anual: float = 4.83,
    valorizacao_imovel_anual: float = 4.0,
    recebe_13: bool = True,
    fgts_mensal: float = 0.0,
    **kwargs,
) -> Dict[str, Any]:
    """
    Compara alugar+investir versus comprar agora.
    Investe o saldo disponível e faz aportes mensais enquanto paga aluguel.
    """
    V0 = _d(valor_imovel)
    aluguel = _d(aluguel_atual)
    saldo = _d(saldo_inicial)
    aporte = _d(aporte_mensal)
    taxa_m = _d(taxa_investimento_anual) / Decimal("100") / Decimal("12")
    valorizacao_m = _d(valorizacao_imovel_anual) / Decimal("100") / Decimal("12")
    n_meses = max(1, prazo_anos * 12)

    valor_imovel_atual = V0
    total_aluguel = _ZERO
    meses_para_comprar = None

    tabela_resumo = []
    for mes in range(1, n_meses + 1):
        saldo = _q(saldo * (1 + taxa_m) + aporte)
        total_aluguel += aluguel
        valor_imovel_atual = _q(valor_imovel_atual * (1 + valorizacao_m))

        if mes % 12 == 0:
            aluguel = _q(aluguel * (1 + _d(ipca_anual) / 100))
            if recebe_13 and fgts_mensal > 0:
                saldo += _q(_d(fgts_mensal) * 12)
            if mes % 60 == 0:
                tabela_resumo.append({
                    "ano": mes // 12,
                    "saldo_investido": float(_q(saldo)),
                    "valor_imovel": float(_q(valor_imovel_atual)),
                    "diferenca": float(_q(saldo - valor_imovel_atual)),
                })

        if meses_para_comprar is None and saldo >= valor_imovel_atual:
            meses_para_comprar = mes

    saldo_final = float(_q(saldo))
    valor_imovel_final = float(_q(valor_imovel_atual))
    total_aluguel_pago = float(_q(total_aluguel))
    ganho_capital = float(_q(saldo - _d(saldo_inicial) - aporte * n_meses))
    custo_liquido = total_aluguel_pago - ganho_capital

    return {
        "saldo_final_investimento": saldo_final,
        "saldo_final_fmt": _fmt_brl(saldo_final),
        "valor_imovel_final": valor_imovel_final,
        "valor_imovel_final_fmt": _fmt_brl(valor_imovel_final),
        "total_aluguel_pago": total_aluguel_pago,
        "total_aluguel_fmt": _fmt_brl(total_aluguel_pago),
        "custo_liquido": float(_q(custo_liquido)),
        "meses_para_comprar": meses_para_comprar,
        "anos_para_comprar": (
            round(meses_para_comprar / 12, 1) if meses_para_comprar else None
        ),
        "consegue_comprar_no_prazo": meses_para_comprar is not None,
        "vantagem": "investimento" if saldo_final > valor_imovel_final else "imovel",
        "tabela_resumo": tabela_resumo,
    }


# ─── guardar dinheiro ─────────────────────────────────────────────────────────

def guardar_dinheiro(
    valor_imovel,
    custas_total,
    saldo_inicial,
    poupanca_mensal,
    taxa_investimento_anual,
    recebe_13: bool = True,
    renda_bruta: float = 0.0,
    **kwargs,
) -> Dict[str, Any]:
    """Simula acúmulo até comprar à vista (imóvel + custas)."""
    alvo = _d(valor_imovel) + _d(custas_total)
    saldo = _d(saldo_inicial)
    poupanca = _d(poupanca_mensal)
    taxa_m = _d(taxa_investimento_anual) / Decimal("100") / Decimal("12")
    bonus_13 = _q(_d(renda_bruta) * Decimal("0.9")) if recebe_13 and renda_bruta > 0 else _ZERO

    if saldo >= alvo:
        return {
            "meses": 0, "anos": 0, "viavel": True,
            "saldo_no_prazo": float(saldo), "alvo": float(alvo),
            "alvo_fmt": _fmt_brl(alvo),
            "mensagem": "Você já tem capital suficiente para comprar à vista!",
        }

    if poupanca <= _ZERO and saldo <= _ZERO:
        return {
            "meses": None, "anos": None, "viavel": False,
            "saldo_no_prazo": 0.0, "alvo": float(alvo),
            "alvo_fmt": _fmt_brl(alvo),
            "mensagem": "Sem poupança mensal não é possível acumular.",
        }

    meses = 0
    for mes in range(1, 601):
        saldo = _q(saldo * (1 + taxa_m) + poupanca)
        if recebe_13 and mes % 12 == 0 and bonus_13 > _ZERO:
            saldo += bonus_13
        if saldo >= alvo:
            meses = mes
            break

    viavel = meses > 0
    anos = round(meses / 12, 1) if viavel else None

    return {
        "meses": meses if viavel else None,
        "anos": anos,
        "viavel": viavel,
        "saldo_no_prazo": float(_q(saldo)),
        "alvo": float(alvo),
        "alvo_fmt": _fmt_brl(alvo),
        "mensagem": (
            f"Você consegue comprar à vista em {anos} anos ({meses} meses) "
            f"investindo {_fmt_brl(poupanca)}/mês a {_fmt_pct(taxa_investimento_anual)}% a.a."
            if viavel
            else "Com a poupança atual, a compra à vista em 50 anos não é viável."
        ),
    }


# ─── CET ─────────────────────────────────────────────────────────────────────

def calcular_cet(
    valor_financiado,
    parcelas_mensais,
    custos_iniciais: float = 0.0,
) -> Dict[str, float]:
    """Custo Efetivo Total via bissecção (TIR)."""
    PV = _d(valor_financiado)
    custos = _d(custos_iniciais)
    if not isinstance(parcelas_mensais, (list, tuple)) or not parcelas_mensais:
        return {"cet_mensal": 0.0, "cet_anual": 0.0}

    fluxos = [_d(p) for p in parcelas_mensais]
    pv_liquido = PV - custos

    # Taxa zero: pagamentos iguais ao principal sem juros
    if abs(sum(fluxos) - pv_liquido) < _d("1"):
        return {"cet_mensal": 0.0, "cet_anual": 0.0}

    def npv(r: Decimal) -> Decimal:
        s = _ZERO
        for i, p in enumerate(fluxos, 1):
            s += p / ((1 + r) ** i)
        return s - pv_liquido

    low, high, mid = _d("0"), _d("1"), _d("0")
    for _ in range(80):
        mid = (low + high) / 2
        val = npv(mid)
        if abs(val) < _d("0.01"):
            break
        if val > 0:
            low = mid
        else:
            high = mid

    cet_mensal = float(mid)
    cet_anual = float((1 + mid) ** 12 - 1)
    return {"cet_mensal": cet_mensal, "cet_anual": cet_anual}


# ─── orquestrador principal ───────────────────────────────────────────────────

def comparar_cenarios_e_formatar(dados_wizard: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recebe os dados do wizard (5 etapas) e retorna comparação formatada.

    Entrada: estrutura SimulationData do app mobile.
    Saída: estrutura consumida pelo ResultsScreen e SimulationCharts.
    """
    perf = dados_wizard.get("perfil_objetivos", {})
    renda_d = dados_wizard.get("trabalho_renda", {})
    fin = dados_wizard.get("financas_atuais", {})
    imovel_d = dados_wizard.get("imovel_desejado", {})
    cen = dados_wizard.get("cenarios", {})

    idade = int(perf.get("idade_comprador", 30) or 30)
    perfil_usuario = perf.get("perfil_usuario", "comprador_morar")
    prioridade = perf.get("prioridade_principal", "equilibrio")
    aluguel_atual = float(perf.get("aluguel_atual", 0) or 0)

    renda = float(renda_d.get("renda_familiar_bruta", 0) or 0)
    tipo_contrato = str(renda_d.get("tipo_contrato", "clt") or "clt")
    recebe_13 = bool(renda_d.get("recebe_13_salario", True))
    outras_rendas = float(renda_d.get("outras_rendas", 0) or 0)
    renda_total = renda + outras_rendas

    saldo_guardado = float(fin.get("saldo_dinheiro_guardado", 0) or 0)
    saldo_fgts = float(fin.get("saldo_fgts", 0) or 0)
    despesas = float(fin.get("despesas_mensais_fixas", 0) or 0)

    valor_imovel = float(imovel_d.get("valor_imovel_desejado", 0) or 0)
    prazo_anos = max(1, int(imovel_d.get("prazo_desejado_anos", 30) or 30))
    custas_forma = str(imovel_d.get("custas_documentacao_forma", "a_vista") or "a_vista")
    estado = str(imovel_d.get("estado", "SP") or "SP").upper()[:2]
    cidade_tipo = str(imovel_d.get("cidade_tipo", "capital") or "capital")

    usar_fgts = bool(cen.get("usar_fgts", False))
    comparar_price = bool(cen.get("comparar_financiamento_price", True))
    comparar_sac = bool(cen.get("comparar_financiamento_sac", True))
    comparar_consorcio_flag = bool(cen.get("comparar_consorcio", True))
    comparar_aluguel = bool(cen.get("comparar_aluguel_investimento", False))
    comparar_guardar = bool(cen.get("comparar_guardar_dinheiro", False))
    comparar_mcmv_req = bool(cen.get("comparar_mcmv", False))
    prazo_consorcio = max(12, int(cen.get("prazo_consorcio", 180) or 180))
    lance_disponivel = float(cen.get("valor_lance_disponivel", 0) or 0)

    prazo_meses = prazo_anos * 12
    prazo_max = max(12, (80 - idade) * 12)
    prazo_meses = min(prazo_meses, prazo_max)

    # Custas iniciais
    custas = calcular_custas_iniciais(valor_imovel, estado=estado, cidade_tipo=cidade_tipo, financiar=(custas_forma == "financiado"))
    custas_valor = custas["total"] if custas_forma == "a_vista" else 0.0

    # Entrada disponível
    entrada_bruta = saldo_guardado + (saldo_fgts if usar_fgts else 0.0)
    entrada_efetiva = max(0.0, entrada_bruta - custas_valor)
    entrada_pct = (entrada_efetiva / valor_imovel * 100) if valor_imovel > 0 else 0.0

    # Acúmulo mensal de FGTS
    fgts_mensal_acum = float(calcular_fgts_mensal(renda, tipo_contrato, recebe_13))

    # Carrega taxas do DB (com fallback para constantes hardcoded)
    taxas_vivas = _carregar_taxas()
    taxa_sbpe = taxas_vivas["taxa_sbpe_cef"]
    sfh_valor_max = taxas_vivas["sfh_valor_max"]
    ipca_anual = float(taxas_vivas["ipca"])
    taxa_invest = float(cen.get("taxa_investimento_esperada", None) or taxas_vivas["selic"])

    # MCMV
    mcmv = verificar_mcmv(renda_total, valor_imovel, cidade_tipo=cidade_tipo, taxas_vivas=taxas_vivas)
    taxa_financing = (
        float(mcmv["taxa_aa"])
        if mcmv["elegivel"] and comparar_mcmv_req
        else float(taxa_sbpe)
    )

    valor_financiado = max(0.0, valor_imovel - entrada_efetiva)
    alertas: List[str] = []

    if valor_imovel > float(sfh_valor_max):
        alertas.append(
            f"Imóvel acima do teto do SFH ({_fmt_brl(sfh_valor_max)}). "
            "Taxas SFI (sem teto de juros) podem ser mais altas."
        )

    if entrada_pct < 20 and not mcmv["elegivel"] and valor_financiado > 0:
        falta = max(0.0, valor_imovel * 0.20 - entrada_efetiva)
        alertas.append(
            f"Entrada de {entrada_pct:.1f}% abaixo do mínimo de 20% para SBPE. "
            f"Você precisa de mais {_fmt_brl(falta)} de entrada ou busque o MCMV."
        )

    # Estimativa de comprometimento de renda
    r_m_est = _d(taxa_financing) / Decimal("100") / Decimal("12")
    parcela_est = float(_pmt(_d(valor_financiado), r_m_est, prazo_meses)) if valor_financiado > 0 else 0.0
    comprometimento_pct = (parcela_est / renda_total * 100) if renda_total > 0 else 0.0
    renda_minima = (parcela_est / 0.30) if parcela_est > 0 else 0.0

    if comprometimento_pct > 30 and renda_total > 0 and parcela_est > 0:
        alertas.append(
            f"Parcela estimada representa {comprometimento_pct:.1f}% da renda — "
            f"acima do limite de 30% dos bancos. "
            f"Renda mínima recomendada: {_fmt_brl(renda_minima)}/mês."
        )

    # ── rodar cenários ────────────────────────────────────────────────────────
    resultados: Dict[str, Any] = {}

    def _res_fin(metodo_key: str, metodo_nome: str, taxa: float) -> Dict:
        if valor_financiado <= 0:
            return {}
        res = calcular_price_sac(
            metodo=metodo_key,
            valor_principal=valor_financiado,
            taxa_anual=taxa,
            prazo_meses=prazo_meses,
            usar_fgts=usar_fgts and tipo_contrato.lower() == "clt",
            saldo_fgts_inicial=saldo_fgts if usar_fgts else 0,
            acumulo_fgts_mensal=fgts_mensal_acum if usar_fgts else 0,
            tipo_amortizacao_fgts="reduzir_prazo",
            idade=idade,
            valor_imovel=valor_imovel,
        )
        total_custo = res["total_pago"] + entrada_efetiva + custas_valor
        fgts_label = " + FGTS" if usar_fgts and tipo_contrato.lower() == "clt" else ""
        return {
            "metodo": f"{metodo_nome}{fgts_label}",
            "parcela_inicial": _fmt_brl(res["parcela_inicial"]),
            "parcela_final": _fmt_brl(res["parcela_final"]),
            "total_custo": _fmt_brl(total_custo),
            "total_juros": _fmt_brl(res["total_juros"]),
            "total_seguros": _fmt_brl(res["total_seguros_taxas"]),
            "cet_anual": _fmt_pct(res["cet_anual"] * 100),
            "prazo_meses": res["prazo_final_meses"],
            "prazo_anos": round(res["prazo_final_meses"] / 12, 1),
            "entrada": _fmt_brl(entrada_efetiva),
            "valor_financiado": _fmt_brl(valor_financiado),
            "taxa_aa": _fmt_pct(taxa),
            "comprometimento_renda": round(
                res["parcela_inicial"] / renda_total * 100, 1
            ) if renda_total > 0 else 0,
            "_total_custo_raw": total_custo,
            "_parcela_raw": res["parcela_inicial"],
            "_prazo_raw": res["prazo_final_meses"],
        }

    if comparar_price and valor_financiado > 0:
        r = _res_fin("price", "Financiamento PRICE", taxa_financing)
        if r:
            resultados["price"] = r

    if comparar_sac and valor_financiado > 0:
        r = _res_fin("sac", "Financiamento SAC", taxa_financing)
        if r:
            resultados["sac"] = r

    if comparar_mcmv_req and mcmv["elegivel"] and valor_financiado > 0:
        r = _res_fin("sac", f"MCMV {mcmv['nome_faixa']}", float(mcmv["taxa_aa"]))
        if r:
            r["metodo"] = f"MCMV {mcmv['nome_faixa']} (SAC)"
            resultados["mcmv"] = r

    # ── comparação multi-banco (SAC) ──────────────────────────────────────────
    # Exibe as taxas dos principais bancos lado a lado para o usuário escolher.
    comparar_bancos = bool(cen.get("comparar_bancos", False))
    if comparar_bancos and valor_financiado > 0 and not mcmv["elegivel"]:
        _BANCOS = [
            ("banco_cef",       "CEF SBPE",   "taxa_sbpe_cef"),
            ("banco_bb",        "BB SBPE",    "taxa_sbpe_bb"),
            ("banco_bradesco",  "Bradesco",   "taxa_sbpe_bradesco"),
            ("banco_itau",      "Itaú",       "taxa_sbpe_itau"),
            ("banco_santander", "Santander",  "taxa_sbpe_santander"),
        ]
        for chave, nome_banco, taxa_key in _BANCOS:
            taxa_banco = float(taxas_vivas.get(taxa_key, taxa_sbpe))
            r = _res_fin("sac", f"{nome_banco} (SAC)", taxa_banco)
            if r:
                resultados[chave] = r

    if comparar_consorcio_flag:
        lance_pct = (lance_disponivel / valor_imovel * 100) if lance_disponivel > 0 and valor_imovel > 0 else 0.0
        cons = simular_consorcio(
            valor_imovel=valor_imovel,
            prazo_meses=prazo_consorcio,
            taxa_adm=18.0,
            fundo_reserva=1.0,
            fgts_saldo=saldo_fgts if usar_fgts else 0,
            lance_percentual=lance_pct,
        )
        total_cons = cons["total_pago"] + custas_valor
        resultados["consorcio"] = {
            "metodo": "Consórcio Imobiliário",
            "parcela_inicial": _fmt_brl(cons["parcela"]),
            "parcela_final": _fmt_brl(cons["parcela"]),
            "total_custo": _fmt_brl(total_cons),
            "total_juros": _fmt_brl(cons["total_taxa_adm"]),
            "total_seguros": "R$ 0,00",
            "cet_anual": "0,00%",
            "prazo_meses": prazo_consorcio,
            "prazo_anos": round(prazo_consorcio / 12, 1),
            "contemplacao_estimada": f"{cons['anos_contemplacao_estimado']} anos",
            "lance_sugerido": _fmt_brl(cons["lance_valor"]),
            "entrada": "N/A",
            "valor_financiado": _fmt_brl(valor_imovel),
            "taxa_aa": "18% (taxa adm total)",
            "comprometimento_renda": round(
                cons["parcela"] / renda_total * 100, 1
            ) if renda_total > 0 else 0,
            "_total_custo_raw": total_cons,
            "_parcela_raw": cons["parcela"],
            "_prazo_raw": prazo_consorcio,
        }

    poupanca_mensal = max(0.0, renda_total - despesas - aluguel_atual)

    if comparar_aluguel and valor_imovel > 0:
        eff_aluguel = aluguel_atual or (valor_imovel * 0.004)
        alug = simular_aluguel_investimento(
            valor_imovel=valor_imovel,
            aluguel_atual=eff_aluguel,
            saldo_inicial=saldo_guardado,
            aporte_mensal=poupanca_mensal,
            taxa_investimento_anual=taxa_invest,
            prazo_anos=prazo_anos,
            ipca_anual=ipca_anual,
            recebe_13=recebe_13,
            fgts_mensal=fgts_mensal_acum,
        )
        resultados["aluguel_investimento"] = {
            "metodo": "Aluguel + Investimento",
            "parcela_inicial": _fmt_brl(eff_aluguel + poupanca_mensal),
            "parcela_final": _fmt_brl(eff_aluguel * 1.4),
            "total_custo": _fmt_brl(alug["total_aluguel_pago"]),
            "total_juros": "N/A",
            "total_seguros": "N/A",
            "cet_anual": _fmt_pct(taxa_invest),
            "saldo_final": alug["saldo_final_fmt"],
            "valor_imovel_futuro": alug["valor_imovel_final_fmt"],
            "consegue_comprar": "Sim" if alug["consegue_comprar_no_prazo"] else "Não no prazo",
            "anos_para_comprar": alug["anos_para_comprar"],
            "prazo_meses": prazo_anos * 12,
            "prazo_anos": prazo_anos,
            "entrada": _fmt_brl(saldo_guardado),
            "valor_financiado": "N/A",
            "taxa_aa": _fmt_pct(taxa_invest),
            "comprometimento_renda": round(
                eff_aluguel / renda_total * 100, 1
            ) if renda_total > 0 else 0,
            "_total_custo_raw": alug["total_aluguel_pago"],
            "_parcela_raw": eff_aluguel + poupanca_mensal,
            "_prazo_raw": prazo_anos * 12,
        }

    if comparar_guardar and valor_imovel > 0:
        guard = guardar_dinheiro(
            valor_imovel=valor_imovel,
            custas_total=custas["total"],
            saldo_inicial=saldo_guardado,
            poupanca_mensal=poupanca_mensal,
            taxa_investimento_anual=taxa_invest,
            recebe_13=recebe_13,
            renda_bruta=renda,
        )
        total_guard = valor_imovel + custas["total"]
        resultados["guardar_dinheiro"] = {
            "metodo": "Guardar Dinheiro",
            "parcela_inicial": _fmt_brl(poupanca_mensal),
            "parcela_final": _fmt_brl(poupanca_mensal),
            "total_custo": _fmt_brl(total_guard),
            "total_juros": "R$ 0,00",
            "total_seguros": "R$ 0,00",
            "cet_anual": "0,00%",
            "prazo_meses": guard.get("meses"),
            "prazo_anos": guard.get("anos"),
            "viavel": guard["viavel"],
            "mensagem_prazo": guard["mensagem"],
            "entrada": "N/A",
            "valor_financiado": "N/A",
            "taxa_aa": _fmt_pct(taxa_invest),
            "comprometimento_renda": round(
                poupanca_mensal / renda_total * 100, 1
            ) if renda_total > 0 else 0,
            "_total_custo_raw": total_guard,
            "_parcela_raw": poupanca_mensal,
            "_prazo_raw": guard.get("meses") or (prazo_anos * 12),
        }

    # ── análise e recomendação ────────────────────────────────────────────────
    melhor_cenario, texto_principal = _gerar_analise(
        resultados=resultados,
        prioridade=prioridade,
        perfil_usuario=perfil_usuario,
        renda_total=renda_total,
        valor_imovel=valor_imovel,
        mcmv=mcmv,
        alertas=alertas,
    )

    for key in list(resultados.keys()):
        for k in ("_total_custo_raw", "_parcela_raw", "_prazo_raw"):
            resultados[key].pop(k, None)

    return {
        "valor_imovel": valor_imovel,
        "valor_imovel_fmt": _fmt_brl(valor_imovel),
        "entrada_efetiva": entrada_efetiva,
        "entrada_pct": round(entrada_pct, 1),
        "valor_financiado": valor_financiado,
        "valor_financiado_fmt": _fmt_brl(valor_financiado),
        "prazo_meses": prazo_meses,
        "prazo_anos": prazo_anos,
        "custas_iniciais": custas,
        "mcmv": mcmv,
        "sfh": {
            "enquadra": valor_imovel <= float(SFH_VALOR_MAX),
            "taxa_referencia_aa": float(TAXA_SBPE_AA),
        },
        "renda_minima_recomendada": float(_q(renda_minima)),
        "renda_minima_fmt": _fmt_brl(renda_minima),
        "comprometimento_estimado": round(comprometimento_pct, 1),
        "resultados": resultados,
        "analise": {
            "melhor_cenario": melhor_cenario,
            "texto_principal": texto_principal,
            "alertas": alertas,
        },
    }


# ─── geração de análise / recomendação ───────────────────────────────────────

def _gerar_analise(
    resultados: Dict,
    prioridade: str,
    perfil_usuario: str,
    renda_total: float,
    valor_imovel: float,
    mcmv: Dict,
    alertas: List[str],
) -> Tuple[str, str]:
    """Retorna (chave_melhor_cenario, texto_recomendacao)."""

    if not resultados:
        return (
            "",
            "Nenhum cenário foi selecionado para comparação. "
            "Volte e ative pelo menos uma opção.",
        )

    scores: Dict[str, float] = {}
    for key, res in resultados.items():
        raw_custo = float(res.get("_total_custo_raw", 0) or 0)
        raw_parcela = float(res.get("_parcela_raw", 0) or 0)
        raw_prazo = float(res.get("_prazo_raw", 0) or 0)

        if prioridade == "pagar_menos":
            scores[key] = raw_custo
        elif prioridade == "parcelas_suaves":
            scores[key] = raw_parcela
        elif prioridade == "quitar_rapido":
            scores[key] = raw_prazo
        else:
            scores[key] = (raw_custo / 1_000_000) + (raw_parcela / 10_000)

    melhor = min(scores, key=lambda k: scores[k]) if scores else ""
    if not melhor:
        return "", "Não foi possível determinar a melhor opção com os dados fornecidos."

    melhor_res = resultados[melhor]
    parcela_str = melhor_res.get("parcela_inicial", "N/A")
    custo_str = melhor_res.get("total_custo", "N/A")
    prazo_str = melhor_res.get("prazo_anos", "N/A")
    metodo_str = melhor_res.get("metodo", melhor)

    intro = ""
    if mcmv["elegivel"] and "mcmv" in resultados:
        intro = (
            f"Boa notícia: você se enquadra no {mcmv['nome_faixa']} do MCMV "
            f"com taxa de {_fmt_pct(mcmv['taxa_aa'])} a.a. — muito abaixo do mercado. "
        )

    if prioridade == "pagar_menos":
        texto = (
            f"{intro}Para pagar menos juros no total, o melhor caminho é "
            f"{metodo_str}: custo total de {custo_str} em {prazo_str} anos."
        )
    elif prioridade == "parcelas_suaves":
        texto = (
            f"{intro}Para ter as parcelas mais baixas possíveis, recomendamos "
            f"{metodo_str}: sua primeira parcela seria de {parcela_str}/mês."
        )
    elif prioridade == "quitar_rapido":
        texto = (
            f"{intro}Para quitar no menor tempo, a melhor opção é "
            f"{metodo_str}: você finaliza em {prazo_str} anos."
        )
    else:
        texto = (
            f"{intro}Para o melhor custo-benefício, recomendamos "
            f"{metodo_str}: parcela inicial de {parcela_str} e custo total de {custo_str}."
        )

    if alertas:
        texto += f" Atenção: {alertas[0]}"

    return melhor, texto
