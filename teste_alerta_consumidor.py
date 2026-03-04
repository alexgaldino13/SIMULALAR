#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste do módulo alerta_consumidor.py
"""

from simulacao.alerta_consumidor import AlertConsumidor, integrar_alertas_ao_contexto
from decimal import Decimal
import json


def teste_alerta_seguro():
    """Testa geração de alerta de seguro"""
    print("=" * 80)
    print("TESTE 1: Alerta Seguro Opcional")
    print("=" * 80)
    
    alerta = AlertConsumidor.ALERTA_SEGURO_OPCIONAL
    print(f"\nTítulo: {alerta['titulo']}")
    print(f"Tipo: {alerta['tipo']}")
    print(f"Nível: {alerta['nivel']}")
    print(f"Mensagem: {alerta['mensagem'][:100]}...")
    print(f"Opções: {len(alerta['opcoes'])} botões")
    print(f"Rodapé: {alerta['rodape']}")
    
    return True


def teste_alerta_economia():
    """Testa geração de alerta de economia"""
    print("\n" + "=" * 80)
    print("TESTE 2: Alerta de Economia em Seguros")
    print("=" * 80)
    
    alerta = AlertConsumidor.gerar_alerta_seguros(
        saldo_devedor=Decimal("327650.72"),
        prazo_meses=267,
        custo_mip_banco=Decimal("112.22"),
        custo_mip_mercado=Decimal("75.00"),
        custo_dfi_banco=Decimal("22.16"),
        custo_dfi_mercado=Decimal("12.50")
    )
    
    print(f"\nTítulo: {alerta['titulo']}")
    print(f"Tipo: {alerta['tipo']}")
    print(f"\nMensagem:")
    print(alerta['mensagem'])
    
    print(f"\nDados de Economia:")
    for chave, valor in alerta['dados_economia'].items():
        print(f"  {chave}: R$ {valor:.2f}" if isinstance(valor, float) else f"  {chave}: {valor}")
    
    return True


def teste_contexto_educativo():
    """Testa geração de contexto educativo"""
    print("\n" + "=" * 80)
    print("TESTE 3: Contexto Educativo Completo")
    print("=" * 80)
    
    contexto = AlertConsumidor.gerar_contexto_educativo()
    
    print(f"\nLei de Referência: {contexto['lei_referencia']}")
    print(f"Artigos CDC: {contexto['cdc_artigos']}")
    print(f"Total de Alertas Disponíveis: {len(contexto['alertas'])}")
    print(f"Direitos Listados: {len(contexto['direitos'])}")
    print(f"Passos de Ação: {len(contexto['passos_acao'])}")
    
    print(f"\n📋 Direitos do Consumidor:")
    for direito in contexto['direitos']:
        print(f"  ✓ {direito['titulo']}: {direito['economia']}")
    
    print(f"\n📝 Passos de Ação:")
    for passo in contexto['passos_acao']:
        print(f"  {passo['numero']}. {passo['titulo']}: {passo['descricao']}")
    
    return True


def teste_integracao_contexto():
    """Testa integração de alertas ao contexto"""
    print("\n" + "=" * 80)
    print("TESTE 4: Integração ao Contexto do Simulator")
    print("=" * 80)
    
    contexto_inicial = {
        'resultados': {'price': {}, 'sac': {}},
        'wizard_data': {},
    }
    
    contexto_atualizado = integrar_alertas_ao_contexto(
        contexto_inicial,
        financiamento_data={
            'saldo_devedor_atual': 327650.72,
            'prazo_restante': 267
        }
    )
    
    print(f"\nTotal de Alertas Integrados: {contexto_atualizado['total_alertas']}")
    print(f"Alertas para Exibição: {len(contexto_atualizado['alertas_consumidor'])}")
    
    print(f"\nAlertas a Exibir:")
    for i, alerta in enumerate(contexto_atualizado['alertas_consumidor'], 1):
        print(f"  {i}. {alerta['titulo']} ({alerta['tipo']})")
    
    return True


def teste_todos_alertas():
    """Testa listagem de todos os alertas"""
    print("\n" + "=" * 80)
    print("TESTE 5: Listagem de Todos os Alertas Disponíveis")
    print("=" * 80)
    
    alertas = AlertConsumidor.listar_todos_alertas()
    
    print(f"\nTotal de Alertas: {len(alertas)}\n")
    
    for i, alerta in enumerate(alertas, 1):
        print(f"{i}. {alerta['titulo']}")
        print(f"   Tipo: {alerta['tipo']}")
        print(f"   Nível: {alerta['nivel']}")
        print(f"   Mensagem: {alerta['mensagem'][:60]}...")
        print()
    
    return True


if __name__ == '__main__':
    testes = [
        ("Alerta Seguro Opcional", teste_alerta_seguro),
        ("Alerta de Economia", teste_alerta_economia),
        ("Contexto Educativo", teste_contexto_educativo),
        ("Integração ao Contexto", teste_integracao_contexto),
        ("Todos os Alertas", teste_todos_alertas),
    ]
    
    resultados = []
    
    for nome, funcao_teste in testes:
        try:
            resultado = funcao_teste()
            resultados.append((nome, "✅ PASSOU"))
        except Exception as e:
            resultados.append((nome, f"❌ FALHOU: {str(e)}"))
    
    print("\n" + "=" * 80)
    print("RESUMO DOS TESTES")
    print("=" * 80)
    
    for teste_nome, resultado_status in resultados:
        print(f"{resultado_status:<20} - {teste_nome}")
    
    print("\n✅ Todos os testes do módulo AlertConsumidor completados!")
