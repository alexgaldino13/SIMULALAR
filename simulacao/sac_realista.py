# simulacao/sac_realista.py
"""
Cálculo de SAC (Sistema de Amortização Constante) baseado em contrato real Itaú
Implementação realista com taxas, seguros, admin fees e amortizações extras (FGTS)

Referência: Contrato Itaú 10166338005 - ALEX GALDINO
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta


class SAC_Realista:
    """
    Cálculo de amortização SAC com parâmetros realistas de banco.
    
    Atributos:
        saldo_devedor_inicial: Valor do financiamento em R$
        taxa_juros_mensal: Taxa mensal de juros (em decimal, ex: 0.00557579)
        prazo_meses: Prazo total em meses
        taxa_adm_mensal: Taxa de administração mensal (fixa ou percentual)
        seguro_mip_mensal: Morte e Invalidez Permanente (inicial)
        seguro_dfi_mensal: Danos Físicos ao Imóvel (fixo)
        indice_correcao: TR ou outro índice (aplicado mensalmente)
        data_inicio: Data de início do contrato
    """
    
    def __init__(
        self,
        saldo_devedor_inicial: float,
        taxa_juros_mensal: float,
        prazo_meses: int,
        taxa_adm_mensal: float = 25.0,
        seguro_mip_mensal: float = 112.22,
        seguro_dfi_mensal: float = 22.16,
        indice_correcao_mensal: float = 1.0,
        data_inicio: datetime = None,
    ):
        self.saldo_devedor_inicial = Decimal(str(saldo_devedor_inicial))
        self.taxa_juros_mensal = Decimal(str(taxa_juros_mensal))
        self.prazo_total_meses = prazo_meses
        self.taxa_adm_mensal = Decimal(str(taxa_adm_mensal))
        self.seguro_mip_mensal_inicial = Decimal(str(seguro_mip_mensal))
        self.seguro_dfi_mensal = Decimal(str(seguro_dfi_mensal))
        self.indice_correcao_mensal = Decimal(str(indice_correcao_mensal))
        self.data_inicio = data_inicio or datetime.now()
        
        # Calcula amortização fixa (SAC)
        self.amortizacao_mensal = self.saldo_devedor_inicial / Decimal(prazo_meses)
    
    def calcular_parcela_mes(
        self,
        mes: int,
        saldo_devedor_anterior: Decimal,
        seguro_mip_atual: Optional[Decimal] = None,
    ) -> Dict:
        """
        Calcula os componentes da parcela para um mês específico.
        
        Retorna dict com:
            - mes: número do mês
            - saldo_devedor_corrigido: saldo após correção monetária
            - amortizacao: valor da amortização (SAC)
            - juros: valor dos juros
            - taxa_adm: taxa de administração
            - seguro_mip: seguro de morte
            - seguro_dfi: seguro do imóvel
            - parcela_total: soma de todos os componentes
            - saldo_devedor_novo: saldo após amortização
        """
        
        # Usa seguro MIP fornecido ou usa o inicial
        if seguro_mip_atual is None:
            seguro_mip_atual = self.seguro_mip_mensal_inicial
        else:
            seguro_mip_atual = Decimal(str(seguro_mip_atual))
        
        # 1. Corrige o saldo anterior pela TR/índice
        saldo_corrigido = saldo_devedor_anterior * self.indice_correcao_mensal
        
        # 2. Calcula amortização (SAC = fixa)
        amortizacao = self.amortizacao_mensal
        
        # 3. Calcula juros sobre o saldo corrigido
        juros = saldo_corrigido * self.taxa_juros_mensal
        
        # 4. Componentes fixos
        taxa_adm = self.taxa_adm_mensal
        seguro_dfi = self.seguro_dfi_mensal
        
        # 5. Parcela total
        parcela_total = amortizacao + juros + taxa_adm + seguro_mip_atual + seguro_dfi
        
        # 6. Novo saldo devedor (após amortização)
        saldo_novo = saldo_corrigido - amortizacao
        
        # Garante que não fique negativo por arredondamentos
        if saldo_novo < 0:
            saldo_novo = Decimal('0')
        
        return {
            'mes': mes,
            'data_vencimento': self.data_inicio + timedelta(days=30 * mes),
            'saldo_devedor_corrigido': float(saldo_corrigido.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'amortizacao': float(amortizacao.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'juros': float(juros.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'taxa_adm': float(taxa_adm.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'seguro_mip': float(seguro_mip_atual.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'seguro_dfi': float(seguro_dfi.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'parcela_total': float(parcela_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'saldo_devedor_novo': float(saldo_novo.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        }
    
    def gerar_tabela_amortizacao(
        self,
        meses: Optional[int] = None,
        fgts_amortizacoes: Optional[List[Tuple[int, float]]] = None,
    ) -> List[Dict]:
        """
        Gera a tabela de amortização completa para todos os meses.
        
        Args:
            meses: número de meses a calcular (default: prazo_total)
            fgts_amortizacoes: list de (mes, valor) para amortizações extras via FGTS
        
        Retorna:
            Lista com os dados de cada parcela
        """
        if meses is None:
            meses = self.prazo_total_meses
        
        fgts_amortizacoes = fgts_amortizacoes or []
        fgts_dict = {int(m): float(v) for m, v in fgts_amortizacoes}
        
        tabela = []
        saldo_atual = self.saldo_devedor_inicial
        
        for mes_num in range(1, meses + 1):
            # Calcula parcela normal
            parcela_info = self.calcular_parcela_mes(mes_num, saldo_atual)
            saldo_atual = Decimal(str(parcela_info['saldo_devedor_novo']))
            
            # Verifica se há amortização extra (FGTS) neste mês
            amortizacao_extra = fgts_dict.get(mes_num, 0.0)
            if amortizacao_extra > 0:
                amortizacao_extra_dec = Decimal(str(amortizacao_extra))
                saldo_atual = saldo_atual - amortizacao_extra_dec
                if saldo_atual < 0:
                    saldo_atual = Decimal('0')
                parcela_info['amortizacao_extra_fgts'] = amortizacao_extra
                parcela_info['saldo_devedor_novo'] = float(saldo_atual.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            
            tabela.append(parcela_info)
            
            # Se saldo zerou, interrompe
            if saldo_atual <= 0:
                break
        
        return tabela
    
    def resumo_contrato(self) -> Dict:
        """
        Retorna um resumo geral do contrato.
        """
        tabela = self.gerar_tabela_amortizacao()
        
        total_amortizacoes = sum(Decimal(str(p['amortizacao'])) for p in tabela)
        total_juros = sum(Decimal(str(p['juros'])) for p in tabela)
        total_adm = sum(Decimal(str(p['taxa_adm'])) for p in tabela)
        total_mip = sum(Decimal(str(p['seguro_mip'])) for p in tabela)
        total_dfi = sum(Decimal(str(p['seguro_dfi'])) for p in tabela)
        total_pago = sum(Decimal(str(p['parcela_total'])) for p in tabela)
        
        return {
            'saldo_inicial': float(self.saldo_devedor_inicial),
            'prazo_meses': self.prazo_total_meses,
            'taxa_juros_mensal_pct': float(self.taxa_juros_mensal * 100),
            'taxa_juros_anual_pct': float(self.taxa_juros_mensal * 12 * 100),
            'parcelas_geradas': len(tabela),
            'saldo_final': float(tabela[-1]['saldo_devedor_novo']) if tabela else 0.0,
            'total_amortizacoes': float(total_amortizacoes),
            'total_juros': float(total_juros),
            'total_adm': float(total_adm),
            'total_seguros_mip': float(total_mip),
            'total_seguros_dfi': float(total_dfi),
            'total_pago': float(total_pago),
        }


# ==============================================================================
# Exemplo de uso com dados do contrato Itaú real
# ==============================================================================

def exemplo_itau_tf224():
    """
    Simula o contrato real: TF224 - ALEX GALDINO (Itaú)
    """
    
    # Parâmetros do contrato em 26/09/2025 (data do DDC)
    sac = SAC_Realista(
        saldo_devedor_inicial=327650.72,
        taxa_juros_mensal=0.00557579,  # 6,690948% / 12
        prazo_meses=360,
        taxa_adm_mensal=25.0,
        seguro_mip_mensal=112.22,
        seguro_dfi_mensal=22.16,
        indice_correcao_mensal=1.0007,  # TR mensal típica
        data_inicio=datetime(2021, 9, 24),
    )
    
    # Gera tabela dos próximos 12 meses
    tabela_12m = sac.gerar_tabela_amortizacao(meses=12)
    
    # Amortização extra via FGTS (exemplo)
    fgts_amortizacoes = [
        (6, 16433.87),  # Fevereiro 2024 - conforme demonstrativo
    ]
    
    tabela_com_fgts = sac.gerar_tabela_amortizacao(
        meses=12,
        fgts_amortizacoes=fgts_amortizacoes
    )
    
    resumo = sac.resumo_contrato()
    
    return {
        'tabela_12_meses': tabela_12m,
        'tabela_com_fgts': tabela_com_fgts,
        'resumo_geral': resumo,
    }


if __name__ == '__main__':
    resultado = exemplo_itau_tf224()
    print("=== TABELA SAC - PRIMEIROS 12 MESES ===")
    for parcela in resultado['tabela_12_meses']:
        print(
            f"Mês {parcela['mes']:3d} | "
            f"Saldo: R$ {parcela['saldo_devedor_novo']:>12,.2f} | "
            f"Parcela: R$ {parcela['parcela_total']:>10,.2f} | "
            f"Juros: R$ {parcela['juros']:>8,.2f}"
        )
    
    print("\n=== RESUMO GERAL ===")
    for chave, valor in resultado['resumo_geral'].items():
        print(f"{chave}: {valor}")
