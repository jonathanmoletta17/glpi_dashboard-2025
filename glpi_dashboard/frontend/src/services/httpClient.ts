import axios from 'axios';
import type {
  AxiosInstance,
  AxiosError,
  AxiosRequestConfig,
  AxiosResponse,
} from 'axios';

// Função auxiliar para acessar variáveis de ambiente
const getEnvVar = (key: string, defaultValue: string = '') => {
  return import.meta.env[key] || defaultValue;
};

// Configuração dinâmica baseada no ambiente
const getApiBaseUrl = () => {
  // Em desenvolvimento, usar URL relativa para funcionar com proxy do Vite
  if (import.meta.env.DEV) {
    return '/api';
  }

  // Em produção, usar variável de ambiente ou fallback
  return getEnvVar('VITE_API_BASE_URL', 'http://localhost:5500/api');
};

// Configuração da API usando variáveis de ambiente
export const API_CONFIG = {
  BASE_URL: getApiBaseUrl(),
  TIMEOUT: parseInt(getEnvVar('VITE_API_TIMEOUT', '120000')),
  RETRY_ATTEMPTS: parseInt(getEnvVar('VITE_API_RETRY_ATTEMPTS', '3')),
  RETRY_DELAY: parseInt(getEnvVar('VITE_API_RETRY_DELAY', '1000')),
};

// Interface para configuração de autenticação
export interface AuthConfig {
  apiToken?: string;
  appToken?: string;
  userToken?: string;
}

// Configuração de autenticação (pode ser definida via variáveis de ambiente)
export const authConfig = {
  apiToken: getEnvVar('VITE_API_TOKEN'),
  appToken: getEnvVar('VITE_APP_TOKEN'),
  userToken: getEnvVar('VITE_USER_TOKEN'),
};

// Função para atualizar tokens de autenticação
export const updateAuthTokens = (newAuthConfig: Partial<AuthConfig>) => {
  Object.assign(authConfig, newAuthConfig);
};

// Cliente HTTP centralizado
export const httpClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Log da configuração inicial (apenas em desenvolvimento)
if (import.meta.env.DEV) {
  console.log('🌐 HTTP Client configurado:', {
    baseURL: API_CONFIG.BASE_URL,
    timeout: API_CONFIG.TIMEOUT,
    environment: import.meta.env.MODE,
    isDev: import.meta.env.DEV,
  });
}

// Interceptador de requisição para autenticação e logging
httpClient.interceptors.request.use(
  (config: any) => {
    // Garantir que headers existe
    config.headers = config.headers || {};

    if (authConfig.apiToken) {
      config.headers['Authorization'] = `Bearer ${authConfig.apiToken}`;
    }

    if (authConfig.appToken) {
      config.headers['App-Token'] = authConfig.appToken;
    }

    if (authConfig.userToken) {
      config.headers['Session-Token'] = authConfig.userToken;
    }

    // Log da requisição (apenas em desenvolvimento com debug habilitado)
    if (import.meta.env.DEV && getEnvVar('VITE_SHOW_API_CALLS') === 'true') {
      console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`, {
        headers: config.headers,
        params: config.params,
        data: config.data,
      });
    }

    return config;
  },
  (error: AxiosError) => {
    console.error('❌ Request error:', error);
    return Promise.reject(error);
  }
);

// Interceptador de resposta para tratamento de erros e logging
httpClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log da resposta (apenas em desenvolvimento com debug habilitado)
    if (import.meta.env.DEV && getEnvVar('VITE_SHOW_API_CALLS') === 'true') {
      console.log(
        `✅ ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`,
        {
          status: response.status,
          statusText: response.statusText,
          data: response.data,
        }
      );
    }

    return response;
  },
  async (error: AxiosError) => {
    const errorInfo = {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      message: error.message,
      code: error.code,
      data: error.response?.data,
    };

    // Tratamento específico por tipo de erro
    if (error.code === 'ECONNABORTED') {
      console.warn('⏱️ Request timeout:', errorInfo.url);
    } else if (error.response?.status === 401) {
      console.warn('🔐 Authentication error:', errorInfo.url);
      // Aqui poderia disparar um evento para renovar token ou redirecionar para login
      dispatchAuthError();
    } else if (error.response?.status === 403) {
      console.warn('🚫 Authorization error:', errorInfo.url);
    } else if (error.response?.status === 404) {
      console.warn('🔍 Endpoint not found:', errorInfo.url);
    } else if (error.response?.status === 429) {
      console.warn('🚦 Rate limit exceeded:', errorInfo.url);
    } else if (error.response?.status && error.response.status >= 500) {
      console.error('🚨 Server error:', errorInfo);
    } else if (error.response?.status && error.response.status >= 400) {
      console.warn('⚠️ Client error:', errorInfo);
    } else {
      console.error('🔌 Network/Connection error:', errorInfo);
    }

    // Implementar retry automático para erros temporários
    if (shouldRetry(error) && !error.config?.__retryCount) {
      return retryRequest(error);
    }

    return Promise.reject(error);
  }
);

// Função para determinar se deve tentar novamente
function shouldRetry(error: AxiosError): boolean {
  const retryableStatuses = [408, 429, 500, 502, 503, 504];
  const retryableCodes = ['ECONNABORTED', 'ENOTFOUND', 'ECONNRESET', 'ETIMEDOUT'];

  return (
    (error.response?.status && retryableStatuses.includes(error.response.status)) ||
    (error.code && retryableCodes.includes(error.code as string)) ||
    false
  );
}

// Função para retry com backoff exponencial
async function retryRequest(error: AxiosError): Promise<AxiosResponse> {
  const config = error.config!;
  config.__retryCount = (config.__retryCount || 0) + 1;

  if (config.__retryCount > API_CONFIG.RETRY_ATTEMPTS) {
    return Promise.reject(error);
  }

  const delay = API_CONFIG.RETRY_DELAY * Math.pow(2, config.__retryCount - 1);

  // Debug logs removidos para produção
  // console.log(
  //   `🔄 Retrying request (${config.__retryCount}/${API_CONFIG.RETRY_ATTEMPTS}) in ${delay}ms:`,
  //   config.url
  // );

  await new Promise(resolve => setTimeout(resolve, delay));

  return httpClient.request(config);
}

// Função para disparar evento de erro de autenticação
function dispatchAuthError() {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(
      new CustomEvent('auth-error', {
        detail: { message: 'Authentication failed' },
      })
    );
  }
}

// Estender a interface AxiosRequestConfig para incluir propriedades personalizadas
declare module 'axios' {
  interface AxiosRequestConfig {
    __retryCount?: number;
    cache?: boolean;
    retry?: number;
  }

  // Extensões customizadas para AxiosInstance são adicionadas via métodos dinâmicos abaixo
}

// Adicionar métodos para interceptadores (para compatibilidade com testes)
(httpClient as any).addRequestInterceptor = (interceptor: any) => {
  return httpClient.interceptors.request.use(interceptor);
};

(httpClient as any).addResponseInterceptor = (interceptor: any) => {
  return httpClient.interceptors.response.use(interceptor);
};

(httpClient as any).setBaseURL = (baseURL: string) => {
  httpClient.defaults.baseURL = baseURL;
};

(httpClient as any).removeRequestInterceptor = (interceptor: any) => {
  httpClient.interceptors.request.eject(interceptor);
};

(httpClient as any).removeResponseInterceptor = (interceptor: any) => {
  httpClient.interceptors.response.eject(interceptor);
};

// Funções utilitárias para requisições comuns
export const apiUtils = {
  // GET request
  get: <T = any>(url: string, config?: AxiosRequestConfig) => httpClient.get<T>(url, config),

  // POST request
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    httpClient.post<T>(url, data, config),

  // PUT request
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    httpClient.put<T>(url, data, config),

  // DELETE request
  delete: <T = any>(url: string, config?: AxiosRequestConfig) => httpClient.delete<T>(url, config),

  // PATCH request
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    httpClient.patch<T>(url, data, config),

  // HEAD request
  head: (url: string, config?: AxiosRequestConfig) => httpClient.head(url, config),
};

export default httpClient;
