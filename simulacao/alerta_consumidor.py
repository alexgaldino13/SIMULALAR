"""
Módulo de Alertas Educativos sobre Direitos do Consumidor (CDC)

Este módulo gera alertas contextualizados para informar usuários sobre:
- Seguros opcionais inclusos em financiamentos
- Direitos garantidos pela Lei nº 12.490/2011
- Potencial de economia em custos de seguros
"""

from decimal import Decimal
from typing import Dict, List


class AlertConsumidor:
    """Gerador de alertas de proteção ao consumidor"""

    ALERTA_SEGURO_OPCIONAL = {
        "tipo": "info",
        "nivel": "alto",
        "icone": "shield-alert",
        "titulo": "💰 Você Sabia? Seu Seguro Pode Ser Mais Barato!",
        "mensagem": (
            "O seguro de Morte e Invalidez Permanente (MIP) incluído no seu financiamento "
            "é <strong>opcional</strong>. Você tem direito de contratar em qualquer seguradora "
            "e economizar até <strong>R$ 50/mês</strong>."
        ),
        "opcoes": [
            {
                "label": "Saiba mais sobre seus direitos",
                "acao": "link",
                "url": "#educacao-seguros",
                "classe": "btn-info"
            },
            {
                "label": "Simular com seguro mais barato",
                "acao": "simular",
                "parametro": "seguro_externo",
                "classe": "btn-success"
            }
        ],
        "rodape": "Conforme Lei nº 12.490/2011 e Código de Defesa do Consumidor (CDC)"
    }

    ALERTA_DIREITOS_CONSUMIDOR = {
        "tipo": "warning",
        "nivel": "critico",
        "icone": "gavel",
        "titulo": "⚖️ Direitos Garantidos por Lei",
        "mensagem": (
            "<strong>Você tem direito a:</strong><br/>"
            "✅ Contratar seguro de Morte/Invalidez em qualquer seguradora<br/>"
            "✅ Cancelar o seguro do banco a qualquer momento<br/>"
            "✅ Reduzir o valor da parcela após cancelar<br/>"
            "✅ Economizar até R$ 600/ano em custos de seguro<br/><br/>"
            "<strong>Baseado em:</strong> Lei nº 12.490/2011, artigo 4º"
        ),
        "rodape": None
    }

    ALERTA_ECONOMIA = {
        "tipo": "success",
        "nivel": "medio",
        "icone": "trending-down",
        "titulo": "💚 Simulação: Economia com Seguro Externo",
        "mensagem_template": (
            "Contratando seguro em mercado livre, você poderia economizar:<br/>"
            "<strong>R$ {economia_mensal:.2f}/mês</strong> "
            "(R$ {economia_anual:.2f}/ano)<br/>"
            "Economia total no período: <strong>R$ {economia_total:.2f}</strong>"
        ),
        "rodape": "Estimativa baseada em cotações de mercado"
    }

    ALERTA_FGTS = {
        "tipo": "info",
        "nivel": "medio",
        "icone": "info-circle",
        "titulo": "📋 Informação: FGTS Pode Amortizar Sua Dívida",
        "mensagem": (
            "Você pode usar seu saldo do FGTS (Fundo de Garantia do Tempo de Serviço) "
            "para <strong>reduzir o saldo devedor</strong> a cada 24 meses. "
            "Isso diminui os juros futuros automaticamente."
        ),
        "opcoes": [
            {
                "label": "Entender como funciona FGTS",
                "acao": "link",
                "url": "#educacao-fgts",
                "classe": "btn-info"
            }
        ],
        "rodape": None
    }

    @staticmethod
    def gerar_alerta_seguros(
        saldo_devedor: Decimal,
        prazo_meses: int,
        custo_mip_banco: Decimal = Decimal("112.22"),
        custo_mip_mercado: Decimal = Decimal("75.00"),
        custo_dfi_banco: Decimal = Decimal("22.16"),
        custo_dfi_mercado: Decimal = Decimal("12.50")
    ) -> Dict:
        """
        Gera alerta sobre economia potencial em seguros

        Args:
            saldo_devedor: Saldo devedor atual
            prazo_meses: Meses restantes
            custo_mip_banco: Custo MIP no banco (mensal)
            custo_mip_mercado: Custo MIP no mercado (mensal)
            custo_dfi_banco: Custo DFI no banco (mensal)
            custo_dfi_mercado: Custo DFI no mercado (mensal)

        Returns:
            Dict com dados de alerta e economia
        """
        economia_mensal = (
            (custo_mip_banco - custo_mip_mercado) +
            (custo_dfi_banco - custo_dfi_mercado)
        )
        economia_anual = economia_mensal * 12
        economia_total = economia_mensal * prazo_meses

        alerta = AlertConsumidor.ALERTA_ECONOMIA.copy()
        alerta["mensagem"] = alerta["mensagem_template"].format(
            economia_mensal=float(economia_mensal),
            economia_anual=float(economia_anual),
            economia_total=float(economia_total)
        )

        alerta["dados_economia"] = {
            "economia_mensal": float(economia_mensal),
            "economia_anual": float(economia_anual),
            "economia_total": float(economia_total),
            "custo_mip_banco_mes": float(custo_mip_banco),
            "custo_mip_mercado_mes": float(custo_mip_mercado),
            "economia_mip": float(custo_mip_banco - custo_mip_mercado),
            "custo_dfi_banco_mes": float(custo_dfi_banco),
            "custo_dfi_mercado_mes": float(custo_dfi_mercado),
            "economia_dfi": float(custo_dfi_banco - custo_dfi_mercado),
            "prazo_meses": prazo_meses
        }

        return alerta

    @staticmethod
    def listar_todos_alertas() -> List[Dict]:
        """Retorna lista de todos os alertas disponíveis"""
        return [
            AlertConsumidor.ALERTA_SEGURO_OPCIONAL,
            AlertConsumidor.ALERTA_DIREITOS_CONSUMIDOR,
            AlertConsumidor.ALERTA_FGTS
        ]

    @staticmethod
    def gerar_contexto_educativo() -> Dict:
        """Gera contexto completo para página educativa"""
        return {
            "alertas": AlertConsumidor.listar_todos_alertas(),
            "lei_referencia": "Lei nº 12.490/2011",
            "cdc_artigos": [39, 51],
            "direitos": [
                {
                    "titulo": "Contrate Seguro Externamente",
                    "descricao": "Você pode escolher qualquer seguradora autorizada",
                    "economia": "até R$ 50/mês"
                },
                {
                    "titulo": "Cancele o Seguro do Banco",
                    "descricao": "A qualquer momento, sem penalidades",
                    "economia": "redução imediata da parcela"
                },
                {
                    "titulo": "Compare Preços",
                    "descricao": "Solicite cotações em corretoras independentes",
                    "economia": "até R$ 600/ano"
                },
                {
                    "titulo": "Use FGTS",
                    "descricao": "Amortize dívida a cada 24 meses",
                    "economia": "redução exponencial de juros"
                }
            ],
            "passos_acao": [
                {
                    "numero": 1,
                    "titulo": "Colete Informações",
                    "descricao": "Anote o saldo devedor, prazo e cobertura necessária"
                },
                {
                    "numero": 2,
                    "titulo": "Solicite Cotações",
                    "descricao": "Contate 2-3 seguradoras competidoras"
                },
                {
                    "numero": 3,
                    "titulo": "Contrate Seguro Novo",
                    "descricao": "Escolha o mais barato com cobertura adequada"
                },
                {
                    "numero": 4,
                    "titulo": "Comunique ao Banco",
                    "descricao": "Envie cópia da apólice (formato: email ou registro)"
                },
                {
                    "numero": 5,
                    "titulo": "Cancele o Antigo",
                    "descricao": "Solicite baixa do seguro do banco por escrito"
                }
            ]
        }


def integrar_alertas_ao_contexto(contexto: Dict, financiamento_data: Dict) -> Dict:
    """
    Adiciona alertas de consumidor ao contexto de resultado do simulador

    Args:
        contexto: Contexto atual do resultado
        financiamento_data: Dados do financiamento (saldo, prazo, etc)

    Returns:
        Contexto atualizado com alertas integrados
    """
    saldo_devedor = Decimal(str(financiamento_data.get("saldo_devedor_atual", 0)))
    prazo_meses = financiamento_data.get("prazo_restante", 1)

    alertas = {
        "seguro_opcional": AlertConsumidor.ALERTA_SEGURO_OPCIONAL,
        "economia": AlertConsumidor.gerar_alerta_seguros(
            saldo_devedor, prazo_meses
        ),
        "direitos": AlertConsumidor.ALERTA_DIREITOS_CONSUMIDOR,
        "fgts": AlertConsumidor.ALERTA_FGTS
    }

    # Decidir quais alertas mostrar baseado no contexto
    mostrar_alertas = []

    # Sempre mostrar alerta de seguro opcional (primeiro)
    mostrar_alertas.append(alertas["seguro_opcional"])

    # Mostrar economia se for significativa (> R$ 20/mês)
    if alertas["economia"]["dados_economia"]["economia_mensal"] > 20:
        mostrar_alertas.append(alertas["economia"])

    # Mostrar direitos (segundo)
    mostrar_alertas.append(alertas["direitos"])

    # Mostrar FGTS se prazo > 24 meses
    if prazo_meses > 24:
        mostrar_alertas.append(alertas["fgts"])

    contexto["alertas_consumidor"] = mostrar_alertas
    contexto["total_alertas"] = len(mostrar_alertas)

    return contexto
