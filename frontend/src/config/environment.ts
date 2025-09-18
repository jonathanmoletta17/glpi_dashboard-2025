// Configuração de ambiente para desenvolvimento e debug
// Nota: Configurações de API foram movidas para httpClient.ts para evitar duplicação
export const ENV_CONFIG = {
  // Configurações de debug e logging
  LOG_LEVEL: import.meta.env.VITE_LOG_LEVEL || 'info',
  SHOW_API_CALLS: import.meta.env.VITE_SHOW_API_CALLS === 'true',

  // Configurações de desenvolvimento
  IS_DEVELOPMENT: import.meta.env.DEV,
  IS_PRODUCTION: import.meta.env.PROD,
  MODE: import.meta.env.MODE,
};

// Importar configuração de API do httpClient
import { API_CONFIG } from '../services/httpClient';

// Log da configuração atual
console.log('🔧 Configuração de ambiente:', {
  mode: ENV_CONFIG.MODE,
  isDev: ENV_CONFIG.IS_DEVELOPMENT,
  isProd: ENV_CONFIG.IS_PRODUCTION,
  logLevel: ENV_CONFIG.LOG_LEVEL,
  showApiCalls: ENV_CONFIG.SHOW_API_CALLS,
  apiBaseUrl: API_CONFIG.BASE_URL,
});

// Exportar configuração consolidada
export const CONSOLIDATED_CONFIG = {
  ...ENV_CONFIG,
  API: API_CONFIG,
};
