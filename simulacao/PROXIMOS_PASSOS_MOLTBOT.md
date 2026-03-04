# 🚀 Próximos Passos - Configuração do Moltbot

## ✅ O que já foi feito

1. ✅ Node.js v24.12.0 instalado
2. ✅ pnpm instalado
3. ✅ Repositório Moltbot clonado em `D:\PROJETOS\FI\moltbot`
4. ⏳ Instalação de dependências em andamento (pnpm install)
5. ✅ Skills personalizados criados:
   - `django-server.js` - Gerenciamento do servidor
   - `simulacao-financeira.js` - Simulações SAC e PRICE
   - `backup-database.js` - Backup e restauração do banco
6. ✅ Guias de uso criados no projeto

## 📋 Próximos Passos (em ordem)

### 1. Aguardar Conclusão da Instalação

A instalação do `pnpm install` está em andamento. Aguarde até aparecer a mensagem:
```
dependencies:
+ ...
done in Xs
```

**Status Atual:** ~76% concluído (782/1032 pacotes)

---

### 2. Verificar Instalação

Após a instalação terminar, execute:

```powershell
cd D:\PROJETOS\FI\moltbot
pnpm moltbot --version
```

**Resultado esperado:** Versão do Moltbot (ex: `2026.1.27`)

---

### 3. Configuração Inicial (Onboarding)

Execute o assistente de configuração:

```powershell
pnpm moltbot onboard
```

**O que vai acontecer:**
1. Perguntas sobre configuração inicial
2. Criação do arquivo `~/.clawdbot/moltbot.json`
3. Configuração de API keys (opcional agora, pode fazer depois)
4. Opção de instalar como serviço do Windows

**Dica:** Pode pular a parte das API keys por enquanto pressionando Enter

---

### 4. Conectar ao WhatsApp

#### Opção A: WhatsApp (Recomendado para testes)

```powershell
pnpm moltbot channels login
```

**Passos:**
1. Um QR Code aparecerá no terminal
2. Abra o WhatsApp no celular
3. Vá em: **Configurações > Aparelhos Conectados > Conectar um aparelho**
4. Escaneie o QR Code
5. Aguarde a mensagem: ✅ **WhatsApp conectado com sucesso**

#### Opção B: Telegram (Alternativa)

1. Abra o Telegram e fale com [@BotFather](https://t.me/botfather)
2. Digite: `/newbot`
3. Siga as instruções e copie o **token**
4. Edite o arquivo de configuração:

```powershell
notepad ~\.clawdbot\moltbot.json
```

5. Adicione:

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

---

### 5. Iniciar o Gateway

O Gateway é o servidor principal do Moltbot:

```powershell
cd D:\PROJETOS\FI\moltbot
pnpm moltbot gateway
```

**Mensagens esperadas:**
```
✓ Gateway starting...
✓ WhatsApp connected
✓ Skills loaded (3)
✓ Gateway running on ws://127.0.0.1:18789
✓ Dashboard available at http://127.0.0.1:18789
```

**Dashboard Web:** Abra no navegador: [http://localhost:18789](http://localhost:18789)

---

### 6. Testar Skills Personalizados

#### Teste 1: Verificar Status do Servidor Django

**No WhatsApp/Telegram, envie:**
```
Verifique o status do servidor Django
```

**Resposta esperada:**
```
❌ Servidor Django não está respondendo
```
ou
```
✅ Servidor Django está rodando em http://localhost:8000
```

---

#### Teste 2: Fazer Backup

**Envie:**
```
Faça um backup do banco de dados
```

**Resposta esperada:**
```
✅ Backup criado com sucesso!
📁 Arquivo: db_backup_2026-01-28_XX-XX-XX.sqlite3
📍 Local: D:\PROJETOS\FI\backups
💾 Tamanho: X.XX MB
```

---

#### Teste 3: Executar Simulação

**Envie:**
```
Faça uma simulação SAC de R$ 100.000 em 120 meses com taxa de 0,8%
```

**Nota:** O servidor Django precisa estar rodando para esta funcionar

---

### 7. Configurar API do Django (Se necessário)

Se os skills de simulação não funcionarem, pode ser necessário criar endpoints na API:

```python
# No Django, crie endpoints REST em views.py:

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def simulacao_sac_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Processar simulação
        resultado = {
            'primeira_parcela': 1234.56,
            'ultima_parcela': 890.12,
            'total_juros': 45000.00,
            'valor_total': 145000.00,
            'cet': 9.6,
            'id': 123
        }
        return JsonResponse(resultado)
```

E adicionar nas URLs:
```python
# urls.py
urlpatterns = [
    path('api/simulacao/sac/', simulacao_sac_api),
    path('api/simulacao/price/', simulacao_price_api),
]
```

---

### 8. Instalar como Serviço (Opcional)

Para o Moltbot iniciar automaticamente com o Windows:

```powershell
pnpm moltbot onboard --install-daemon
```

**Benefícios:**
- Inicia automaticamente ao ligar o PC
- Roda em segundo plano
- Não precisa manter terminal aberto

---

### 9. Configurar Segurança

Edite `~\.clawdbot\moltbot.json` para restringir acesso:

```json
{
  "channels": {
    "whatsapp": {
      "enabled": true,
      "allowFrom": [
        "+5511999999999"  // SEU NÚMERO AQUI
      ],
      "groups": {
        "*": {
          "requireMention": true
        }
      }
    }
  }
}
```

**Depois de editar, reinicie o gateway:**
```powershell
pnpm moltbot gateway --restart
```

---

## 🎯 Automações Futuras

### 1. Backup Automático Diário

Adicione no skill `backup-database.js`:

```javascript
export default {
  // ... código existente
  
  schedule: '0 2 * * *', // Todo dia às 2h da manhã
  
  // O método execute será chamado automaticamente
}
```

### 2. Monitoramento de Servidor

Crie um novo skill `monitor-server.js`:

```javascript
export default {
  name: 'monitor_server',
  schedule: '*/5 * * * *', // A cada 5 minutos
  
  async execute() {
    const response = await fetch('http://localhost:8000/').catch(() => null);
    
    if (!response || !response.ok) {
      // Enviar alerta
      await this.sendMessage('⚠️ Servidor Django caiu!');
    }
  }
}
```

### 3. Relatórios Automáticos

Criar skill para enviar relatório diário:

```javascript
export default {
  name: 'relatorio_diario',
  schedule: '0 9 * * *', // Todo dia às 9h
  
  async execute() {
    // Buscar dados do dia anterior
    // Gerar relatório
    // Enviar via WhatsApp
  }
}
```

---

## 📚 Documentação de Referência

### Documentos Criados

1. **MOLTBOT_GUIA_USO.md** - Guia completo de uso
2. **EXEMPLOS_USO_SKILLS.md** - Exemplos práticos dos skills
3. **Este arquivo** - Próximos passos da configuração

### Localização dos Arquivos

```
D:\PROJETOS\FI\
├── simulacao\              # Seu projeto Django
│   ├── MOLTBOT_GUIA_USO.md
│   ├── EXEMPLOS_USO_SKILLS.md
│   └── PROXIMOS_PASSOS_MOLTBOT.md
│
└── moltbot\                # Instalação do Moltbot
    ├── skills\
    │   ├── django-server.js
    │   ├── simulacao-financeira.js
    │   └── backup-database.js
    └── ...
```

---

## 🆘 Solução de Problemas

### Gateway não inicia

```powershell
# Verificar se a porta está em uso
netstat -ano | findstr 18789

# Se estiver em uso, matar o processo
taskkill /F /PID <PID>

# Ou usar porta diferente
pnpm moltbot gateway --port 18790
```

### WhatsApp não conecta

1. Desconectar todos os dispositivos do WhatsApp Web
2. Deletar pasta de autenticação:
```powershell
Remove-Item -Recurse -Force ~\.clawdbot\auth_info_baileys\
```
3. Tentar conectar novamente

### Skills não carregam

```powershell
# Ver skills carregados
pnpm moltbot skills

# Ver logs de erro
pnpm moltbot logs

# Verificar sintaxe dos arquivos .js
pnpm oxlint skills/*.js
```

### Erro de permissão no Windows

Execute o PowerShell como Administrador para:
- Instalar como serviço
- Modificar configurações do sistema
- Acessar portas privilegiadas (<1024)

---

## 📞 Suporte

### Recursos Oficiais

- **Documentação:** https://docs.molt.bot/
- **GitHub:** https://github.com/moltbot/moltbot
- **Discord:** Link no site oficial
- **Troubleshooting:** https://docs.molt.bot/help/troubleshooting

### Comandos Úteis

```powershell
# Verificar versão
pnpm moltbot --version

# Status do gateway
pnpm moltbot status

# Ver logs
pnpm moltbot logs

# Diagnosticar problemas
pnpm moltbot doctor

# Listar skills
pnpm moltbot skills

# Parar gateway
pnpm moltbot gateway --stop

# Atualizar Moltbot
pnpm moltbot update
```

---

## ✨ Conclusão

Após seguir todos os passos:

1. ✅ Moltbot estará rodando 24/7
2. ✅ WhatsApp/Telegram conectado
3. ✅ Skills personalizados funcionando
4. ✅ Automações configuradas
5. ✅ Backup e segurança implementados

**Resultado:** Você terá um assistente de IA completo que pode:
- Gerenciar seu servidor Django
- Executar simulações financeiras
- Fazer backups automáticos
- Responder via WhatsApp/Telegram
- Automatizar tarefas rotineiras
- Monitorar seu sistema 24/7

---

**Bom trabalho! 🦞** 

Em caso de dúvidas, consulte os guias criados ou a documentação oficial.
