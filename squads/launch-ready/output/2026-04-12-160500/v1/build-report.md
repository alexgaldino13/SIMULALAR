# 🏗️ Relatório de Configuração de Build
**Agente:** Lola Lançamento

As configurações de automação de build (EAS) foram revisadas para o lançamento.

## 1. Perfis de Compilação (eas.json)
*   **Preview:** Configurado para gerar `.apk` (instalação direta para testes).
*   **Production:** Configurado para gerar `.aab` (App Bundle exigido pela Google Play).

## 2. Metadados Técnicos
*   **API Endpoint:** Apontando para o ambiente de produção (Railway).
*   **Build Target:** Android 5.0 (API 21) até Android 15.
*   **Permissions:** Apenas Internet e Acesso ao Estado da Rede (mínimo necessário para LGPD e AdMob).

## 3. Comandos de Build
*   `npm run build:apk`: Para testes internos imediatos.
*   `npm run build:aab`: Para submissão final à loja.

---
**Status:** Pipeline de compilação operacional.
