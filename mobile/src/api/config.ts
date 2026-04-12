/**
 * Configurações globais de API para o ambiente mobile.
 */

// Domínio de produção (placeholder - configure quando comprar o domínio)
const PROD_URL = 'https://simulalar-production.up.railway.app';

// IP Local para desenvolvimento
const DEV_URL = 'http://192.168.0.11:8000';

// Alterna automaticamente: No simulador/expo usa DEV, no build final usa PROD
export const BASE_URL = __DEV__ ? DEV_URL : PROD_URL;

// Tempo limite das requisições (ms)
export const TIMEOUT = 15000; // Aumentado para 15s em produção

export const API_CONFIG = {
  BASE_URL,
  TIMEOUT,
  ENDPOINTS: {
    LOGIN: '/api/v1/auth/login/',
    DASHBOARD: '/api/v1/dashboard/',
    SIMULATIONS: '/api/v1/simulations/',
    SAVE_SIMULATION: '/api/v1/simulation/save/',
    CALCULATE: '/api/v1/wizard/calculate/',
    EXPORT_PDF: (id: number) => `/exportar/pdf/${id}/`,
  }
};
