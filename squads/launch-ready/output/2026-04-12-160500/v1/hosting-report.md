# 🚀 Relatório de Hosting e Deploy
**Agente:** Dante Deploy

O backend do SIMULALAR está pronto para ser provisionado. O uso de Docker garante que o ambiente de desenvolvimento seja idêntico ao de produção.

## 1. Estratégia de Cloud
*   **Provedor Recomendado:** Railway.app (pelo suporte nativo a Docker e PostgreSQL).
*   **Runtime:** Python 3.12 (via Dockerfile).
*   **Servidor Web:** Gunicorn com 4 workers.

## 2. Configuração Docker
O arquivo `Dockerfile` na raiz do projeto já contempla:
*   Instalação de dependências de sistema (PostgreSQL, Pillow).
*   Coleta de arquivos estáticos automática no build.
*   Execução automática de migrations no startup.

## 3. Variáveis de Ambiente (MANDATÓRIO)
Configurar no painel da Cloud:
*   `DATABASE_URL`: URL do banco PostgreSQL.
*   `SECRET_KEY`: Chave única para produção.
*   `DEBUG`: `False`.
*   `ALLOWED_HOSTS`: `*` ou o domínio final.
*   `PYTHONUNBUFFERED`: `1`.

## 4. Próximos Passos
1. Conectar o repositório GitHub ao Railway.
2. Adicionar o plugin "PostgreSQL" no projeto Railway.
3. Inserir as variáveis de ambiente acima.
4. O deploy será automático a cada push.
