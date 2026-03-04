# API de Parcerias - ImobCalc

## Visão Geral

A API de Parcerias do ImobCalc permite que parceiros (consórcios, corretoras, bancos) acessem e gerenciem seus leads de forma programada.

**Base URL:** `https://imobcalc.com/api/v1/partnerships/`

## Autenticação

Todos os endpoints (exceto `/health/`) requerem autenticação via API Key.

### Como Autenticar

Incluir o header `Authorization` em todas as requisições:

```
Authorization: Api-Key SEU_API_KEY_AQUI
```

### Obter sua API Key

1. Acesse o dashboard administrativo do ImobCalc
2. Vá em "Parceiros" > Seu cadastro
3. Copie a API Key exibida

**IMPORTANTE:** Mantenha sua API Key em segredo. Não compartilhe ou exponha em código público.

---

## Endpoints

### 1. Health Check

Verifica se a API está operacional.

**Endpoint:** `GET /health/`

**Autenticação:** Não requerida

**Resposta:**
```json
{
  "status": "ok",
  "timestamp": "2026-02-01T16:30:00Z"
}
```

---

### 2. Dados do Parceiro

Retorna informações do parceiro autenticado.

**Endpoint:** `GET /me/`

**Resposta:**
```json
{
  "id": "uuid-do-parceiro",
  "nome": "Consórcio XYZ",
  "tipo": "CONSORCIO",
  "status": "ATIVO",
  "email_contato": "contato@consorcio.com",
  "telefone": "11999999999",
  "total_leads_recebidos": 150,
  "total_leads_convertidos": 45,
  "taxa_conversao": 30.0
}
```

---

### 3. Estatísticas

Retorna estatísticas detalhadas do parceiro.

**Endpoint:** `GET /stats/`

**Parâmetros de Query (opcionais):**
- `data_inicio` (YYYY-MM-DD): Data de início do período
- `data_fim` (YYYY-MM-DD): Data de fim do período

**Exemplo:** `GET /stats/?data_inicio=2026-01-01&data_fim=2026-01-31`

**Resposta:**
```json
{
  "periodo": {
    "inicio": "01/01/2026",
    "fim": "31/01/2026"
  },
  "total_leads": 50,
  "leads_convertidos": 15,
  "leads_perdidos": 10,
  "leads_em_andamento": 25,
  "taxa_conversao": 30.0,
  "taxa_perda": 20.0,
  "valor_total_negocios": 4500000.0,
  "comissao_total": 112500.0,
  "ticket_medio": 300000.0,
  "tempo_medio_conversao_dias": 15.5
}
```

---

### 4. Listar Leads

Retorna lista de leads do parceiro.

**Endpoint:** `GET /leads/`

**Parâmetros de Query (opcionais):**
- `status`: Filtrar por status (NOVO, ENVIADO, EM_CONTATO, QUALIFICADO, NEGOCIACAO, CONVERTIDO, PERDIDO, INVALIDO)
- `origem`: Filtrar por origem (SIMULACAO, FORMULARIO, DASHBOARD, MANUAL)
- `data_inicio` (YYYY-MM-DD): Leads criados após esta data
- `data_fim` (YYYY-MM-DD): Leads criados antes desta data
- `valor_min`: Valor mínimo do imóvel
- `valor_max`: Valor máximo do imóvel
- `estado`: Filtrar por estado (UF)
- `page`: Número da página (padrão: 1)
- `page_size`: Itens por página (padrão: 20, máx: 100)

**Exemplo:** `GET /leads/?status=NOVO&estado=SP&page=1&page_size=10`

**Resposta:**
```json
{
  "count": 150,
  "next": "https://imobcalc.com/api/v1/partnerships/leads/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid-do-lead",
      "nome_completo": "João Silva",
      "email": "joao@email.com",
      "telefone": "11988887777",
      "valor_imovel": 350000.0,
      "valor_entrada": 70000.0,
      "cidade_interesse": "São Paulo",
      "estado_interesse": "SP",
      "renda_mensal": 8000.0,
      "fgts_disponivel": 15000.0,
      "status": "NOVO",
      "origem": "SIMULACAO",
      "criado_em": "2026-01-15T10:30:00Z",
      "enviado_em": "2026-01-15T10:35:00Z",
      "observacoes_usuario": "Interessado em financiamento SAC"
    }
  ]
}
```

---

### 5. Detalhes do Lead

Retorna detalhes completos de um lead específico.

**Endpoint:** `GET /leads/{lead_id}/`

**Resposta:**
```json
{
  "id": "uuid-do-lead",
  "nome_completo": "João Silva",
  "email": "joao@email.com",
  "telefone": "11988887777",
  "valor_imovel": 350000.0,
  "valor_entrada": 70000.0,
  "cidade_interesse": "São Paulo",
  "estado_interesse": "SP",
  "renda_mensal": 8000.0,
  "fgts_disponivel": 15000.0,
  "cenario_preferido": "Financiamento SAC",
  "status": "NOVO",
  "origem": "SIMULACAO",
  "dados_simulacao": {
    "valor_imovel": 350000.0,
    "entrada": 70000.0,
    "prazo": 240,
    "taxa_juros": 10.5
  },
  "criado_em": "2026-01-15T10:30:00Z",
  "enviado_em": "2026-01-15T10:35:00Z",
  "visualizado_em": null,
  "primeiro_contato_em": null,
  "convertido_em": null,
  "observacoes_usuario": "Interessado em financiamento SAC"
}
```

---

### 6. Atualizar Status do Lead

Atualiza o status de um lead.

**Endpoint:** `POST /leads/{lead_id}/update_status/`

**Body:**
```json
{
  "status": "QUALIFICADO",
  "observacoes": "Lead qualificado após análise de crédito"
}
```

**Status Possíveis:**
- `NOVO`
- `ENVIADO`
- `EM_CONTATO`
- `QUALIFICADO`
- `NEGOCIACAO`
- `CONVERTIDO`
- `PERDIDO`
- `INVALIDO`

**Resposta:**
```json
{
  "success": true,
  "message": "Status atualizado com sucesso",
  "lead": {
    "id": "uuid-do-lead",
    "status": "QUALIFICADO"
  }
}
```

---

### 7. Marcar Lead como Convertido

Marca um lead como convertido e registra o valor do negócio.

**Endpoint:** `POST /leads/{lead_id}/convert/`

**Body:**
```json
{
  "valor_negocio": 350000.0,
  "observacoes": "Contrato assinado em 01/02/2026"
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Lead marcado como convertido",
  "lead": {
    "id": "uuid-do-lead",
    "status": "CONVERTIDO",
    "valor_negocio": 350000.0,
    "comissao_gerada": 8750.0,
    "convertido_em": "2026-02-01T14:30:00Z"
  }
}
```

---

### 8. Marcar Lead como Perdido

Marca um lead como perdido.

**Endpoint:** `POST /leads/{lead_id}/mark_lost/`

**Body:**
```json
{
  "motivo": "Cliente desistiu da compra",
  "observacoes": "Optou por alugar ao invés de comprar"
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Lead marcado como perdido",
  "lead": {
    "id": "uuid-do-lead",
    "status": "PERDIDO"
  }
}
```

---

### 9. Webhook (Receber Leads Automaticamente)

Se você configurou uma URL de webhook no seu cadastro, o ImobCalc enviará automaticamente novos leads para sua aplicação.

**Método:** `POST` para sua URL configurada

**Headers:**
```
Content-Type: application/json
X-ImobCalc-Signature: assinatura-hmac-sha256
```

**Body:**
```json
{
  "event": "lead.created",
  "timestamp": "2026-02-01T14:30:00Z",
  "lead": {
    "id": "uuid-do-lead",
    "nome_completo": "Maria Santos",
    "email": "maria@email.com",
    "telefone": "11977776666",
    "valor_imovel": 400000.0,
    "cidade_interesse": "Rio de Janeiro",
    "estado_interesse": "RJ",
    "status": "NOVO",
    "criado_em": "2026-02-01T14:30:00Z"
  }
}
```

**Sua aplicação deve:**
1. Responder com status `200 OK` em até 5 segundos
2. Validar a assinatura HMAC (opcional, mas recomendado)
3. Processar o lead de forma assíncrona se necessário

---

## Códigos de Status HTTP

- `200 OK`: Requisição bem-sucedida
- `201 Created`: Recurso criado com sucesso
- `400 Bad Request`: Dados inválidos na requisição
- `401 Unauthorized`: API Key inválida ou ausente
- `403 Forbidden`: Sem permissão para acessar o recurso
- `404 Not Found`: Recurso não encontrado
- `429 Too Many Requests`: Limite de taxa excedido
- `500 Internal Server Error`: Erro no servidor

---

## Rate Limiting

A API possui limites de taxa para garantir disponibilidade:

- **Tier Gratuito:** 100 requisições/hora
- **Tier Premium:** 1000 requisições/hora
- **Tier Enterprise:** Sem limites

Headers de resposta incluem:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1643731200
```

---

## Exemplos de Integração

### Python

```python
import requests

API_KEY = 'sua-api-key-aqui'
BASE_URL = 'https://imobcalc.com/api/v1/partnerships'

headers = {
    'Authorization': f'Api-Key {API_KEY}',
    'Content-Type': 'application/json'
}

# Listar leads novos
response = requests.get(
    f'{BASE_URL}/leads/',
    headers=headers,
    params={'status': 'NOVO'}
)

leads = response.json()['results']
for lead in leads:
    print(f"Novo lead: {lead['nome_completo']} - {lead['email']}")

# Atualizar status
lead_id = leads[0]['id']
response = requests.post(
    f'{BASE_URL}/leads/{lead_id}/update_status/',
    headers=headers,
    json={'status': 'EM_CONTATO', 'observacoes': 'Primeiro contato realizado'}
)

print(response.json())
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

const API_KEY = 'sua-api-key-aqui';
const BASE_URL = 'https://imobcalc.com/api/v1/partnerships';

const headers = {
  'Authorization': `Api-Key ${API_KEY}`,
  'Content-Type': 'application/json'
};

// Listar leads
async function listarLeads() {
  try {
    const response = await axios.get(`${BASE_URL}/leads/`, {
      headers,
      params: { status: 'NOVO' }
    });
    
    console.log('Leads:', response.data.results);
  } catch (error) {
    console.error('Erro:', error.response.data);
  }
}

// Marcar como convertido
async function marcarConvertido(leadId, valorNegocio) {
  try {
    const response = await axios.post(
      `${BASE_URL}/leads/${leadId}/convert/`,
      { valor_negocio: valorNegocio },
      { headers }
    );
    
    console.log('Convertido:', response.data);
  } catch (error) {
    console.error('Erro:', error.response.data);
  }
}

listarLeads();
```

### PHP

```php
<?php

$apiKey = 'sua-api-key-aqui';
$baseUrl = 'https://imobcalc.com/api/v1/partnerships';

$headers = [
    'Authorization: Api-Key ' . $apiKey,
    'Content-Type: application/json'
];

// Listar leads
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $baseUrl . '/leads/?status=NOVO');
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
$leads = json_decode($response, true);

foreach ($leads['results'] as $lead) {
    echo "Lead: " . $lead['nome_completo'] . "\n";
}

curl_close($ch);

?>
```

---

## Suporte

Para dúvidas ou problemas com a API:

- **Email:** api@imobcalc.com
- **Documentação:** https://docs.imobcalc.com
- **Status da API:** https://status.imobcalc.com

---

## Changelog

### v1.0.0 (01/02/2026)
- Lançamento inicial da API
- Endpoints de listagem e gerenciamento de leads
- Sistema de webhook
- Autenticação via API Key
