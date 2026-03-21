# API do Wizard - ImobCalc

## Endpoints

### POST /simulacao/wizard/

Inicia ou continua o wizard.

**Parâmetros:**
- `wizard_step`: Step atual (0-3)
- Dados do formulário do step atual

**Resposta:**
- HTML do próximo step ou resultado final

### GET /simulacao/wizard/

Retorna o step atual do wizard.

**Resposta:**
- HTML do step atual

## Estrutura de Dados

### Step 1: Dados Básicos

```json
{
  "valor_imovel": "300000.00",
  "valor_entrada": "60000.00",
  "prazo_meses": "240",
  "taxa_juros_anual": "10.00"
}
```

### Step 2: Sistema de Amortização

```json
{
  "sistema": "SAC"  // ou "PRICE"
}
```

### Step 3: Dados Pessoais

```json
{
  "nome_completo": "João Silva",
  "email": "joao@email.com",
  "telefone": "(11) 91234-5678",
  "renda_mensal": "8000.00"
}
```

### Step 4: Resultado

```json
{
  "valor_financiado": "240000.00",
  "sistema": "SAC",
  "parcelas": [
    {
      "mes": 1,
      "parcela": "2500.00",
      "juros": "1500.00",
      "amortizacao": "1000.00",
      "saldo": "239000.00"
    },
    // ... mais parcelas
  ],
  "total_pago": "360000.00",
  "total_juros": "120000.00"
}
```

## Sessão

O wizard usa sessões Django para armazenar dados entre steps.

**Chaves de sessão:**
- `wizard_simulacao_wizard_view`: Dados do wizard
- `wizard_simulacao_wizard_view_step`: Step atual

## Validações

### Dados Básicos
- `valor_imovel`: > 0, max 12 dígitos
- `valor_entrada`: >= 0, < valor_imovel
- `prazo_meses`: 12-420
- `taxa_juros_anual`: 0.1-30.0

### Dados Pessoais
- `nome_completo`: min 3 caracteres
- `email`: formato válido
- `telefone`: formato (XX) XXXXX-XXXX
- `renda_mensal`: > 0

## Exemplos de Uso

### cURL

```bash
# Step 1
curl -X POST http://localhost:8000/simulacao/wizard/ \
  -d "wizard_step=0" \
  -d "0-valor_imovel=300000" \
  -d "0-valor_entrada=60000" \
  -d "0-prazo_meses=240" \
  -d "0-taxa_juros_anual=10"

# Step 2
curl -X POST http://localhost:8000/simulacao/wizard/ \
  -d "wizard_step=1" \
  -d "1-sistema=SAC"
```

### JavaScript (Fetch)

```javascript
// Step 1
const formData = new FormData();
formData.append('wizard_step', '0');
formData.append('0-valor_imovel', '300000');
formData.append('0-valor_entrada', '60000');
formData.append('0-prazo_meses', '240');
formData.append('0-taxa_juros_anual', '10');

fetch('/simulacao/wizard/', {
  method: 'POST',
  body: formData,
  headers: {
    'X-CSRFToken': getCookie('csrftoken')
  }
})
.then(response => response.text())
.then(html => {
  document.getElementById('wizard-container').innerHTML = html;
});
```

### Python (Requests)

```python
import requests

session = requests.Session()

# Step 1
response = session.post('http://localhost:8000/simulacao/wizard/', data={
    'wizard_step': '0',
    '0-valor_imovel': '300000',
    '0-valor_entrada': '60000',
    '0-prazo_meses': '240',
    '0-taxa_juros_anual': '10'
})

print(response.text)
```

---

**Última atualização:** 18/03/2026
