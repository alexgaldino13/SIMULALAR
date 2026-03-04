# 💬 Exemplos de Uso dos Skills Personalizados

## 🎯 Skills Criados

Foram criados 3 skills personalizados para automatizar tarefas do projeto Django:

1. **django-server.js** - Gerenciamento do servidor Django
2. **simulacao-financeira.js** - Execução de simulações SAC e PRICE
3. **backup-database.js** - Backup e restauração do banco de dados

## 📱 Como Usar via WhatsApp/Telegram

Após conectar o Moltbot ao WhatsApp/Telegram, você pode enviar mensagens naturais e o assistente executará os skills automaticamente.

---

## 1️⃣ Gerenciamento do Servidor Django

### Verificar Status do Servidor

**Mensagem:**
```
Verifique o status do servidor Django
```
ou
```
O servidor está rodando?
```

**Resposta esperada:**
```
✅ Servidor Django está rodando em http://localhost:8000
```

---

### Iniciar o Servidor

**Mensagem:**
```
Inicie o servidor Django
```
ou
```
Start o servidor
```

**Resposta esperada:**
```
✅ Servidor Django iniciado com sucesso em http://localhost:8000
```

---

### Parar o Servidor

**Mensagem:**
```
Pare o servidor Django
```
ou
```
Stop o servidor
```

**Resposta esperada:**
```
✅ Servidor Django parado com sucesso
```

---

### Reiniciar o Servidor

**Mensagem:**
```
Reinicie o servidor Django
```

**Resposta esperada:**
```
✅ Servidor Django parado com sucesso
✅ Servidor Django iniciado com sucesso em http://localhost:8000
```

---

## 2️⃣ Simulações Financeiras

### Executar Simulação SAC

**Mensagem:**
```
Faça uma simulação SAC de R$ 300.000 em 360 meses com taxa de 0,8% ao mês
```

**Resposta esperada:**
```
📊 **Simulação SAC Concluída**

💰 **Dados da Simulação:**
  • Valor Financiado: R$ 300.000,00
  • Prazo: 360 meses
  • Taxa de Juros: 0,8% ao mês

📈 **Resultados:**
  • Primeira Parcela: R$ 3.233,33
  • Última Parcela: R$ 840,00
  • Total de Juros: R$ 434.400,00
  • Valor Total: R$ 734.400,00
  • CET: 9,60%

✅ Simulação salva com ID: 123
```

---

### Executar Simulação PRICE

**Mensagem:**
```
Simulação PRICE de R$ 500.000 em 240 meses, taxa 0,75%
```

**Resposta esperada:**
```
📊 **Simulação PRICE Concluída**

💰 **Dados da Simulação:**
  • Valor Financiado: R$ 500.000,00
  • Prazo: 240 meses
  • Taxa de Juros: 0,75% ao mês

📈 **Resultados:**
  • Parcela Fixa: R$ 4.892,50
  • Total de Juros: R$ 674.200,00
  • Valor Total: R$ 1.174.200,00
  • CET: 9,00%

✅ Simulação salva com ID: 124
```

---

### Comparar SAC e PRICE

**Mensagem:**
```
Compare SAC e PRICE para R$ 400.000, 300 meses, taxa 0,85%
```

**Resposta esperada:**
```
🔄 **Comparação SAC vs PRICE**

[Resultados SAC]
---
[Resultados PRICE]

💡 **Dica:** 
  • SAC: Parcelas decrescentes, menos juros no total
  • PRICE: Parcelas fixas, mais fácil de planejar
```

---

### Simulação com Seguro e Taxa Administrativa

**Mensagem:**
```
Simulação SAC de R$ 250.000, 180 meses, taxa 0,9%, seguro R$ 50, taxa admin R$ 1.500
```

**Parâmetros:**
- valor: 250000
- prazo: 180
- taxa: 0.9
- seguro: 50
- taxaAdmin: 1500

---

## 3️⃣ Backup do Banco de Dados

### Criar Backup

**Mensagem:**
```
Faça um backup do banco de dados
```
ou
```
Backup do banco
```

**Resposta esperada:**
```
✅ **Backup criado com sucesso!**

📁 Arquivo: db_backup_2026-01-28_01-30-00.sqlite3
📍 Local: D:\PROJETOS\FI\backups
💾 Tamanho: 2.45 MB
🕐 Data: 28/01/2026 01:30:00
```

---

### Listar Backups

**Mensagem:**
```
Liste os backups do banco de dados
```
ou
```
Quais backups existem?
```

**Resposta esperada:**
```
📂 **Backups Disponíveis:**

  1. db_backup_2026-01-28_01-30-00.sqlite3
  2. db_backup_2026-01-27_14-20-15.sqlite3
  3. db_backup_2026-01-26_09-45-30.sqlite3

Total: 3 backup(s)
Localização: D:\PROJETOS\FI\backups
```

---

### Restaurar Backup

**Mensagem:**
```
Restaure o backup db_backup_2026-01-27_14-20-15.sqlite3
```

**Resposta esperada:**
```
✅ **Backup restaurado com sucesso!**

📁 Arquivo restaurado: db_backup_2026-01-27_14-20-15.sqlite3
💾 Banco atual salvo como: db_before_restore_1706400000000.sqlite3
🕐 Data: 28/01/2026 01:35:00

⚠️ **IMPORTANTE:** Reinicie o servidor Django para aplicar as mudanças!
```

---

### Limpar Backups Antigos

**Mensagem:**
```
Limpe backups antigos, mantendo os 5 mais recentes
```

**Resposta esperada:**
```
🗑️ **Limpeza concluída**

3 backup(s) antigo(s) removido(s)
Mantidos: 5 backup(s) mais recentes
```

---

## 🔄 Fluxos de Trabalho Comuns

### Fluxo 1: Rotina Matinal

**Sequência de mensagens:**
```
1. "Bom dia! Verifique o status do servidor"
2. "Faça um backup do banco de dados"
3. "Liste as simulações do dia anterior"
```

---

### Fluxo 2: Análise de Cenários

**Sequência de mensagens:**
```
1. "Compare SAC e PRICE para R$ 350.000, 360 meses, taxa 0,8%"
2. "Agora faça a mesma simulação com prazo de 240 meses"
3. "E com 480 meses?"
```

---

### Fluxo 3: Manutenção Semanal

**Sequência de mensagens:**
```
1. "Pare o servidor Django"
2. "Faça backup do banco de dados"
3. "Limpe backups antigos, mantendo os 10 mais recentes"
4. "Inicie o servidor Django"
```

---

## 🎨 Personalizações Avançadas

### Criar Skill Personalizado para Relatórios

Você pode criar um novo skill para gerar relatórios personalizados:

**Exemplo de mensagem:**
```
Gere um relatório Excel com todas as simulações do mês
```

**Skill necessário:** `relatorio-excel.js` (a ser criado)

---

### Integrar com Alertas

Configure alertas automáticos:

**Exemplo:**
```
Me avise todo dia às 9h sobre o status do servidor
```

**Implementação:** Usar cron jobs no Moltbot

---

### Monitoramento Contínuo

**Exemplo:**
```
Monitore o servidor e me avise se cair
```

**Implementação:** Skill de monitoramento com verificações a cada 5 minutos

---

## 📊 Comandos Rápidos

| Comando | Ação |
|---------|------|
| `status servidor` | Verifica se o servidor está rodando |
| `start servidor` | Inicia o servidor Django |
| `stop servidor` | Para o servidor Django |
| `simulação sac X Y Z` | Executa simulação SAC |
| `simulação price X Y Z` | Executa simulação PRICE |
| `comparar X Y Z` | Compara SAC e PRICE |
| `backup` | Cria backup do banco |
| `listar backups` | Lista backups disponíveis |
| `restaurar backup X` | Restaura backup específico |
| `limpar backups` | Remove backups antigos |

---

## 🔧 Configuração dos Skills

### Localização dos Skills

Os skills estão em:
```
D:\PROJETOS\FI\moltbot\skills\
  ├── django-server.js
  ├── simulacao-financeira.js
  └── backup-database.js
```

### Recarregar Skills

Após modificar um skill, reinicie o gateway:
```powershell
cd D:\PROJETOS\FI\moltbot
pnpm moltbot gateway --restart
```

---

## 🐛 Troubleshooting

### Skill não responde

1. Verifique se o gateway está rodando
2. Verifique os logs: `pnpm moltbot logs`
3. Confirme se o skill está carregado: `pnpm moltbot skills`

### Erro ao executar simulação

1. Verifique se o servidor Django está rodando
2. Confirme a URL da API: `http://localhost:8000/api/simulacao/`
3. Teste a API diretamente no navegador

### Backup não funciona

1. Verifique se os caminhos no skill estão corretos
2. Confirme permissões de escrita na pasta de backups
3. Verifique se o arquivo `db.sqlite3` existe

---

## 💡 Dicas Avançadas

### 1. Agendar Backups Automáticos

Configure no Moltbot para fazer backup diário:
```javascript
// No arquivo de configuração do skill
schedule: '0 2 * * *' // Todo dia às 2h da manhã
```

### 2. Notificações Proativas

Configure o Moltbot para enviar notificações:
```javascript
// Exemplo: notificar quando simulação é concluída
await this.notify('✅ Sua simulação foi concluída!');
```

### 3. Integração com Excel

Crie um skill para exportar simulações para Excel:
```javascript
// Usar biblioteca como 'exceljs'
const workbook = new ExcelJS.Workbook();
// ... adicionar dados da simulação
await workbook.xlsx.writeFile('simulacao.xlsx');
```

---

## 🚀 Próximas Funcionalidades

Skills futuros planejados:

- [ ] **relatorio-excel.js** - Exportar simulações para Excel
- [ ] **monitor-erros.js** - Monitorar logs de erro
- [ ] **estatisticas.js** - Gerar estatísticas de uso
- [ ] **email-sender.js** - Enviar relatórios por email
- [ ] **webhook-handler.js** - Receber webhooks de sistemas externos

---

**Dúvidas?** Envie uma mensagem no WhatsApp/Telegram conectado ao Moltbot! 🦞
