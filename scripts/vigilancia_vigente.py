"""
vigilancia_vigente.py
Script de Auditoria de Parâmetros Financeiros - SIMULALAR
Este script deve ser executado periodicamente para validar se as constantes 
da calculadora financeira estão alinhadas com o mercado (2024/2026).
"""
import sys
import os
import django
from decimal import Decimal

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ImobCalc.settings')
django.setup()

from simulacao.calculadora_financeira import (
    obter_taxa_mip_por_idade,
    TAXA_ADMINISTRACAO_MENSAL_PADRAO,
    LIMITE_RENDA_MCMV_FAIXA_1
)

def auditoria_parametros():
    print("[LOG] Iniciando Auditoria de Vigilancia Vigilante...")
    alerts = []

    # 1. Verificar Limite MCMV (Benchmark Mar/2024: 3.200,00)
    if LIMITE_RENDA_MCMV_FAIXA_1 < 3200:
        alerts.append(f"[!] Alerta MCMV: O limite Faixa 1 ({LIMITE_RENDA_MCMV_FAIXA_1}) esta abaixo do benchmark de R$ 3.200,00.")
    else:
        print("[OK] MCMV: Parametros de renda Faixa 1 atualizados.")

    # 2. Verificar Seguro MIP (Amostragem > 50 anos)
    taxa_55 = obter_taxa_mip_por_idade(55)
    if taxa_55 < 0.00165: # 0.165%
         alerts.append(f"⚠️ Alerta MIP: Taxa para 55 anos ({taxa_55*100:.3f}%) parece desatualizada.")
    else:
        print("✅ MIP: Tabela de seguros ativa e proporcional.")

    # 3. Verificar Taxas de Adm
    if TAXA_ADMINISTRACAO_MENSAL_PADRAO != 25:
         alerts.append(f"[!] Alerta Bancario: Taxa de adm ({TAXA_ADMINISTRACAO_MENSAL_PADRAO}) diverge do padrao SBPE (R$ 25).")
    else:
        print("[OK] Taxas de Administracao: OK.")

    # 4. Relatório Final
    print("\n--- RESUMO DA VIGILÂNCIA ---")
    if not alerts:
        print("[SUCCESS] SISTEMA SEGURO: Todos os parametros financeiros estao em conformidade com o mercado.")
    else:
        print("[ERROR] INCONSISTENCIAS ENCONTRADAS:")
        for a in alerts:
            print(a)
    print("----------------------------\n")

if __name__ == "__main__":
    auditoria_parametros()
