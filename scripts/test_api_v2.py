import requests
import json

url = "http://127.0.0.1:8000/api/v1/wizard/calculate/"

data = {
    "perfil_objetivos": {
        "perfil_usuario": "comprador_morar",
        "prioridade_principal": "equilibrio",
        "onde_mora_atualmente": "aluga",
        "aluguel_atual": 1500,
        "tempo_mora_atualmente": "1_3",
        "idade_comprador": 30
    },
    "trabalho_renda": {
        "renda_familiar_bruta": 8000,
        "tipo_contrato": "clt",
        "renda_estavel": "estavel",
        "recebe_13_salario": True,
        "quantos_dependentes": 1,
        "outras_rendas": 0,
        "tipo_trabalho": "privado"
    },
    "financas_atuais": {
        "valor_imovel_proprio": 0,
        "saldo_dinheiro_guardado": 50000,
        "saldo_fgts": 0,
        "despesas_mensais_fixas": 2000
    },
    "imovel_desejado": {
        "valor_imovel_desejado": 500000,
        "prazo_desejado_anos": 30,
        "custas_documentacao_forma": "financiado"
    },
    "cenarios": {
        "comparar_financiamento_price": True,
        "comparar_financiamento_sac": True,
        "comparar_consorcio": True,
        "prazo_consorcio": "180",
        "estrategia_contemplacao": "sorteio",
        "valor_lance_disponivel": 0,
        "tempo_maximo_espera_consorcio": 36,
        "comparar_mcmv": False,
        "comparar_aluguel_investimento": True,
        "comparar_compra_a_vista": False,
        "comparar_guardar_dinheiro": True,
        "pagar_aluguel_com_rendimentos": False,
        "usar_fgts": True,
        "taxa_investimento_esperada": 9.5
    }
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
