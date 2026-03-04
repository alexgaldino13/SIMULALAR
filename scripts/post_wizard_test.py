import os
import sys
import json
from pathlib import Path

# Ensure project root is on sys.path so Django settings can be imported
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ImobCalc.settings')
import django
django.setup()

from django.test import Client

client = Client()

payload = {
    "objetivo": "Comprar imóvel",
    "valor_imovel": 300000,
    "entrada": 60000,
    "fgts_saldo": 0,
    "paga_aluguel": True,
    "aluguel_inicial": 0,
    "renda_familiar_bruta": 8000,
    "prazo_anos": 30,
    "taxa_anual": 8.5
}

resp = client.post('/wizard/api/submit/', data=json.dumps(payload), content_type='application/json', HTTP_HOST='127.0.0.1')
print('STATUS:', resp.status_code)
text = resp.content.decode('utf-8', errors='replace')
print('RESPONSE (truncated to 2000 chars):')
print(text[:2000])
if len(text) > 2000:
    print('\n... (truncated, see full response in debug server page)')
