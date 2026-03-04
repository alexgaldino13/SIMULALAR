# 🦞 Guia de Uso do Moltbot no Projeto Django

## O que é o Moltbot?

O Moltbot é um assistente de IA pessoal que roda no seu PC e pode ser controlado via WhatsApp, Telegram ou Discord. Ele pode executar tarefas reais no seu computador, incluindo:

- Executar scripts e comandos
- Gerenciar arquivos
- Fazer chamadas de API
- Controlar aplicações
- Automatizar fluxos de trabalho

## 📍 Localização da Instalação

O Moltbot foi instalado em: `D:\PROJETOS\FI\moltbot\`

## 🚀 Como Iniciar o Moltbot

### 1. Primeira Configuração (Onboarding)

```powershell
cd D:\PROJETOS\FI\moltbot
pnpm moltbot onboard --install-daemon
```

Este comando irá:
- Configurar o Moltbot
- Criar o arquivo de configuração em `~/.clawdbot/moltbot.json`
- Instalar como serviço do Windows (opcional)

### 2. Conectar ao WhatsApp/Telegram

#### WhatsApp
```powershell
pnpm moltbot channels login
```
- Um QR Code aparecerá no terminal
- Escaneie com o WhatsApp Web
- Aguarde a conexão

#### Telegram
1. Crie um bot via [@BotFather](https://t.me/botfather)
2. Obtenha o token
3. Configure em `~/.clawdbot/moltbot.json`:

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "SEU_TOKEN_AQUI"
    }
  }
}
```

### 3. Iniciar o Gateway (Servidor)

```powershell
cd D:\PROJETOS\FI\moltbot
pnpm moltbot gateway
```

O gateway ficará rodando em:
- WebSocket: `ws://127.0.0.1:18789`
- Dashboard: `http://127.0.0.1:18789/`

## 🎯 Casos de Uso para o Projeto de Simulação Financeira

### 1. Executar Simulações via Chat

**Exemplo de conversa:**
```
Você: Faça uma simulação SAC de R$ 300.000 em 360 meses com taxa de 0,8% ao mês
Moltbot: [executa o script Python e retorna os resultados]
```

### 2. Verificar Status do Servidor Django

```
Você: Verifique se o servidor Django está rodando
Moltbot: [verifica processos e retorna status]
```

### 3. Fazer Backup do Banco de Dados

```
Você: Faça backup do banco de dados
Moltbot: [executa comando de backup e confirma]
```

### 4. Executar Testes

```
Você: Rode os testes do Django
Moltbot: [executa pytest ou manage.py test e mostra resultados]
```

### 5. Gerar Relatórios

```
Você: Gere um relatório Excel da última simulação
Moltbot: [executa script e envia o arquivo]
```

## 🛠️ Criar Skills Personalizados

Skills são plugins que estendem as capacidades do Moltbot. Vou criar alguns exemplos para o seu projeto:

### Estrutura de um Skill

```typescript
// D:\PROJETOS\FI\moltbot\skills\simulacao-sac.js
export default {
  name: 'simulacao_sac',
  description: 'Executa uma simulação SAC no projeto Django',
  
  async execute({ valor, prazo, taxa }) {
    // Lógica para chamar sua API Django
    const resultado = await fetch('http://localhost:8000/api/simulacao/sac/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ valor, prazo, taxa })
    });
    
    return await resultado.json();
  }
};
```

### Skill para Backup

```typescript
// D:\PROJETOS\FI\moltbot\skills\backup-db.js
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export default {
  name: 'backup_database',
  description: 'Faz backup do banco de dados SQLite',
  
  async execute() {
    const timestamp = new Date().toISOString().replace(/:/g, '-');
    const backupPath = `D:\\PROJETOS\\FI\\backups\\db_${timestamp}.sqlite3`;
    
    await execAsync(`copy D:\\PROJETOS\\FI\\db.sqlite3 ${backupPath}`);
    
    return `Backup criado em: ${backupPath}`;
  }
};
```

## 📝 Configuração Avançada

### Arquivo de Configuração (~/.clawdbot/moltbot.json)

```json
{
  "channels": {
    "whatsapp": {
      "enabled": true,
      "allowFrom": ["+5511999999999"]
    },
    "telegram": {
      "enabled": false
    }
  },
  "agent": {
    "name": "AssistenteFinanceiro",
    "model": "claude-3-sonnet"
  },
  "skills": {
    "autoload": true,
    "paths": [
      "D:\\PROJETOS\\FI\\moltbot\\skills"
    ]
  }
}
```

## 🔒 Segurança

### Restringir Acesso por Número

```json
{
  "channels": {
    "whatsapp": {
      "allowFrom": ["+5511999999999"],
      "groups": {
        "*": {
          "requireMention": true
        }
      }
    }
  }
}
```

### Comandos Seguros

Use slash commands para operações sensíveis:
```
/exec python manage.py migrate
/backup database
/restart server
```

## 📱 Comandos Úteis

### Comandos do Moltbot

```powershell
# Ver status
pnpm moltbot status

# Ver logs
pnpm moltbot logs

# Parar o gateway
pnpm moltbot gateway --stop

# Ver sessões ativas
pnpm moltbot sessions

# Limpar memória
pnpm moltbot memory clear

# Atualizar Moltbot
pnpm moltbot update
```

## 🎓 Exemplos de Automação

### 1. Relatório Diário Automático

Configure um cron job no Moltbot:

```javascript
// skills/relatorio-diario.js
export default {
  name: 'relatorio_diario',
  schedule: '0 9 * * *', // Todos os dias às 9h
  
  async execute() {
    // Buscar dados do dia anterior
    const dados = await buscarDadosDia();
    
    // Gerar resumo
    return `📊 Relatório Diário:
    - Simulações realizadas: ${dados.total}
    - Valor médio: R$ ${dados.media}
    - Prazo médio: ${dados.prazoMedio} meses`;
  }
};
```

### 2. Monitoramento de Erros

```javascript
// skills/monitor-erros.js
export default {
  name: 'monitor_erros',
  schedule: '*/15 * * * *', // A cada 15 minutos
  
  async execute() {
    const logs = await lerLogsErro();
    
    if (logs.length > 0) {
      return `⚠️ ${logs.length} erros detectados nos últimos 15 minutos`;
    }
  }
};
```

## 🔗 Integração com Django

### Criar Endpoints API no Django

```python
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def moltbot_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        comando = data.get('comando')
        
        if comando == 'simulacao':
            resultado = executar_simulacao(data)
            return JsonResponse(resultado)
    
    return JsonResponse({'status': 'ok'})
```

### Configurar URLs

```python
# urls.py
urlpatterns = [
    path('api/moltbot/', moltbot_webhook, name='moltbot-webhook'),
]
```

## 📚 Recursos Adicionais

- **Documentação Oficial**: https://docs.molt.bot/
- **GitHub**: https://github.com/moltbot/moltbot
- **Discord da Comunidade**: [Link no site]
- **Exemplos de Skills**: https://github.com/moltbot/moltbot/tree/main/skills

## 🆘 Troubleshooting

### Moltbot não conecta ao WhatsApp
1. Verifique se o WhatsApp Web está funcionando no navegador
2. Delete a pasta `~/.clawdbot/auth_info_baileys/` e tente novamente
3. Verifique os logs: `pnpm moltbot logs`

### Gateway não inicia
1. Verifique se a porta 18789 está livre
2. Verifique logs de erro
3. Tente: `pnpm moltbot doctor`

### Skills não carregam
1. Verifique o caminho em moltbot.json
2. Verifique sintaxe dos arquivos .js
3. Reinicie o gateway

## 🎯 Próximos Passos

1. ✅ Instalação concluída
2. ⏳ Aguardar finalização do `pnpm install`
3. 📱 Conectar ao WhatsApp/Telegram
4. 🛠️ Criar skills personalizados para o projeto
5. 🚀 Começar a automatizar tarefas!

---

**Dúvidas?** Consulte a documentação oficial ou me pergunte! 🦞
