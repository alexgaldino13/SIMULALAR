"""
Management command: atualizar_indices_bcb

Busca índices atualizados do Banco Central do Brasil (BCB/SGS)
e atualiza a tabela ParametroMercado.

Séries utilizadas:
  432   – Meta SELIC (COPOM)
  13522 – IPCA acumulado em 12 meses
  226   – TR mensal (Taxa Referencial)

Uso:
  python manage.py atualizar_indices_bcb
  python manage.py atualizar_indices_bcb --dry-run
"""
from __future__ import annotations

import logging
from datetime import date, timedelta
from decimal import Decimal

import requests
from django.core.management.base import BaseCommand, CommandError

from simulacao.models import ParametroMercado

logger = logging.getLogger(__name__)

BCB_BASE = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie}/dados/ultimos/{n}?formato=json"

# Taxas dos bancos (atualizadas em 2025/2026 — atualizar manualmente quando portaria mudar)
# CEF SBPE TH: https://www.caixa.gov.br/voce/habitacao/financiamento-habitacional/Paginas/default.aspx
# BB: https://www.bb.com.br/site/habitacao/
# Bradesco/Itaú/Santander: tabelas de junho 2026
BANCOS_TAXA_AA = {
    "taxa_sbpe_cef":       ("10.49", "Taxa SBPE CEF (referência)"),
    "taxa_sbpe_bb":        ("10.99", "Taxa SBPE Banco do Brasil"),
    "taxa_sbpe_bradesco":  ("11.19", "Taxa SBPE Bradesco"),
    "taxa_sbpe_itau":      ("10.99", "Taxa SBPE Itaú"),
    "taxa_sbpe_santander": ("11.49", "Taxa SBPE Santander"),
    "mcmv_faixa1_taxa":   ("4.75",  "MCMV Faixa 1 — taxa mínima"),
    "mcmv_faixa2_taxa":   ("6.50",  "MCMV Faixa 2 — taxa mínima"),
    "mcmv_faixa3_taxa":   ("7.66",  "MCMV Faixa 3 — taxa mínima"),
    "mcmv_faixa1_renda_max": ("2850",  "MCMV Faixa 1 — renda máxima R$"),
    "mcmv_faixa2_renda_max": ("4400",  "MCMV Faixa 2 — renda máxima R$"),
    "mcmv_faixa3_renda_max": ("8000",  "MCMV Faixa 3 — renda máxima R$"),
    "sfh_valor_max":         ("1500000", "Valor máximo do imóvel no SFH"),
}

# ParametroMercado.unidade para cada chave
_UNIDADES = {
    "selic":              "percentual_aa",
    "ipca":               "percentual_12m",
    "tr":                 "percentual_mensal",
    "taxa_sbpe_cef":      "percentual_aa",
    "taxa_sbpe_bb":       "percentual_aa",
    "taxa_sbpe_bradesco": "percentual_aa",
    "taxa_sbpe_itau":     "percentual_aa",
    "taxa_sbpe_santander":"percentual_aa",
    "mcmv_faixa1_taxa":   "percentual_aa",
    "mcmv_faixa2_taxa":   "percentual_aa",
    "mcmv_faixa3_taxa":   "percentual_aa",
    "mcmv_faixa1_renda_max": "reais",
    "mcmv_faixa2_renda_max": "reais",
    "mcmv_faixa3_renda_max": "reais",
    "sfh_valor_max":         "reais",
}

_NOMES = {
    "selic": "Meta SELIC (COPOM)",
    "ipca":  "IPCA acumulado 12 meses",
    "tr":    "TR mensal",
}


def _bcb_fetch(serie: int, n: int = 1) -> float | None:
    """Busca o último valor de uma série SGS/BCB. Retorna None em caso de erro."""
    url = BCB_BASE.format(serie=serie, n=n)
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        dados = resp.json()
        if not dados:
            return None
        valor_str = dados[-1].get("valor", "").replace(",", ".")
        return float(valor_str) if valor_str not in ("", None) else None
    except Exception as exc:
        logger.warning("BCB série %s: %s", serie, exc)
        return None


def _upsert(chave: str, nome: str, valor: float, unidade: str, descricao: str, dry_run: bool) -> str:
    """Cria ou atualiza um ParametroMercado. Retorna 'criado' | 'atualizado' | 'dry-run'."""
    if dry_run:
        return "dry-run"
    obj, created = ParametroMercado.objects.update_or_create(
        chave=chave,
        defaults={
            "nome": nome,
            "valor": Decimal(str(valor)),
            "unidade": unidade,
            "descricao": descricao,
            "ativo": True,
        },
    )
    return "criado" if created else "atualizado"


class Command(BaseCommand):
    help = "Atualiza índices do BCB (SELIC, IPCA, TR) e taxas dos bancos no ParametroMercado."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true", default=False,
            help="Exibe o que seria atualizado sem salvar no banco.",
        )
        parser.add_argument(
            "--apenas-bcb", action="store_true", default=False,
            help="Atualiza apenas SELIC/IPCA/TR (sem taxas dos bancos).",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        apenas_bcb = options["apenas_bcb"]

        if dry_run:
            self.stdout.write(self.style.WARNING("=== DRY-RUN — nada será salvo ==="))

        erros = 0

        # ── SELIC meta (série 432) ─────────────────────────────────────────────
        selic = _bcb_fetch(432)
        if selic is not None:
            status = _upsert(
                "selic", "Meta SELIC (COPOM)", selic,
                "percentual_aa", f"Taxa básica de juros do Brasil — COPOM. Série BCB 432.",
                dry_run,
            )
            self.stdout.write(f"  SELIC: {selic}% a.a. [{status}]")
        else:
            self.stdout.write(self.style.ERROR("  SELIC: falha ao buscar BCB série 432"))
            erros += 1

        # ── IPCA acumulado 12 meses (série 13522) ─────────────────────────────
        ipca = _bcb_fetch(13522)
        if ipca is not None:
            status = _upsert(
                "ipca", "IPCA acumulado 12 meses", ipca,
                "percentual_12m", "Inflação oficial acumulada em 12 meses. Série BCB 13522.",
                dry_run,
            )
            self.stdout.write(f"  IPCA: {ipca}% (12m) [{status}]")
        else:
            self.stdout.write(self.style.ERROR("  IPCA: falha ao buscar BCB série 13522"))
            erros += 1

        # ── TR mensal (série 226) ──────────────────────────────────────────────
        tr = _bcb_fetch(226)
        if tr is not None:
            status = _upsert(
                "tr", "TR mensal", tr,
                "percentual_mensal", "Taxa Referencial mensal. Série BCB 226.",
                dry_run,
            )
            self.stdout.write(f"  TR: {tr}%/mês [{status}]")
        else:
            self.stdout.write(self.style.ERROR("  TR: falha ao buscar BCB série 226"))
            erros += 1

        # ── Taxas dos bancos (hardcoded — atualizar manualmente) ──────────────
        if not apenas_bcb:
            for chave, (valor_str, descricao) in BANCOS_TAXA_AA.items():
                nome = descricao.split("—")[0].strip() if "—" in descricao else descricao
                unidade = _UNIDADES.get(chave, "percentual_aa")
                status = _upsert(chave, nome, float(valor_str), unidade, descricao, dry_run)
                self.stdout.write(f"  {chave}: {valor_str} [{status}]")

        if erros:
            self.stdout.write(self.style.WARNING(f"\n{erros} índice(s) BCB não atualizados (usando fallback do código)."))
        else:
            self.stdout.write(self.style.SUCCESS("\nÍndices atualizados com sucesso."))
