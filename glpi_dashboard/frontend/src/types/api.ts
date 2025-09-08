// Tipos para a API do Dashboard GLPI

// Métricas por nível
export interface LevelMetrics {
  novos: number;
  pendentes: number;
  progresso: number;
  resolvidos: number;
  total: number;
  abertos?: number;
  fechados?: number;
  atrasados?: number;
}

// Métricas de níveis
export interface NiveisMetrics {
  n1: LevelMetrics;
  n2: LevelMetrics;
  n3: LevelMetrics;
  n4: LevelMetrics;
  // Removido geral: LevelMetrics; pois não existe nos dados do backend
}

// Métricas do dashboard
export interface DashboardMetrics {
  // Totais gerais
  novos?: number;
  pendentes?: number;
  progresso?: number;
  resolvidos?: number;
  total?: number;
  // Estrutura por níveis
  niveis: NiveisMetrics;

  filtros_aplicados?: any;
  tempo_execucao?: number;
  timestamp?: string;
  systemStatus?: any;
  technicianRanking?: any[];
}

// Status do sistema
export interface SystemStatus {
  status: 'online' | 'offline' | 'maintenance';
  sistema_ativo: boolean;
  ultima_atualizacao: string;
}

// Ranking de técnicos
export interface TechnicianRanking {
  id: string;
  name: string;
  nome?: string;
  level: string;
  rank: number;
  total: number;
  score?: number;
  ticketsResolved?: number;
  ticketsInProgress?: number;
  averageResolutionTime?: number;
}

// Parâmetros de filtro
export interface FilterParams {
  period?: 'today' | 'week' | 'month';
  levels?: string[];
  status?: string[];
  priority?: string[];
  dateRange?: {
    startDate: string;
    endDate: string;
    label?: string;
  };
  level?: string;
  technician?: string;
  category?: string;
  startDate?: string;
  endDate?: string;
  filterType?: string; // Novo: tipo de filtro de data (creation, modification, current_status)
}

// Resposta da API
export interface ApiResponse<T = any> {
  success: true;
  data: T;
  message?: string;
  timestamp?: string;
  performance?: PerformanceMetrics;
}

// Erro da API
export interface ApiError {
  success: false;
  error: string;
  details?: any;
  timestamp?: string;
  code?: string | number;
}

// Resultado da API (união de sucesso e erro)
export type ApiResult<T = any> = ApiResponse<T> | ApiError;

export interface LoadingState {
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

// Configuração de cache
export interface CacheConfig {
  enabled: boolean;
  ttl: number; // Time to live em milissegundos
  maxSize: number; // Número máximo de entradas no cache
  strategy: string;
}

// Entrada do cache
export interface CacheEntry<T> {
  data: T;
  timestamp: number;
  key: string;
}

// Métricas de performance
export interface PerformanceMetrics {
  responseTime: number;
  cacheHit: boolean;
  timestamp: Date;
  endpoint: string;
}

// Configuração da aplicação
export interface AppConfig {
  theme: string;
  language: string;
  autoRefresh: boolean;
  refreshInterval: number;
  showPerformanceMetrics: boolean;
  enableNotifications: boolean;
  dateFormat: string;
  timeFormat: string;
  timezone: string;
}

// Contexto do usuário
export interface UserContext {
  id?: string;
  name?: string;
  role?: string;
  permissions?: string[];
}

// Notificação
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  autoClose?: boolean;
  duration?: number;
}

// Tema da aplicação
export interface Theme {
  name: string;
  displayName: string;
  colors: {
    primary: string;
    secondary: string;
    success: string;
    warning: string;
    error: string;
    info: string;
    background: string;
    surface: string;
    text: string;
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  borderRadius: {
    sm: string;
    md: string;
    lg: string;
  };
}

// Preferências do usuário
export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: 'pt-BR' | 'en-US';
  dateFormat: string;
  timeFormat: string;
  autoRefresh: boolean;
  refreshInterval: number;
  showPerformanceMetrics: boolean;
  enableNotifications: boolean;
  dashboardLayout: string;
  chartsEnabled: boolean;
  soundEnabled: boolean;
  emailNotifications: boolean;
  notifications: {
    enabled: boolean;
    types: ('success' | 'error' | 'warning' | 'info')[];
  };
  dashboard: {
    defaultView: 'cards' | 'table' | 'chart';
    autoRefresh: boolean;
  };
}

// Validação de formulário
export interface ValidationResult<T = any> {
  isValid: boolean;
  errors: string[];
  data?: T;
}

// Opções de exportação
export interface ExportOptions {
  format: 'csv' | 'xlsx' | 'pdf' | 'json';
  includeFilters: boolean;
  includeTimestamp: boolean;
  filename?: string;
}

// Histórico de ações
export interface ActionHistory {
  id: string;
  action: string;
  timestamp: Date;
  user?: string;
  details?: Record<string, any>;
}

// Type guards para verificação de tipos em runtime
export const isApiError = (response: ApiResult): response is ApiError => {
  return response.success === false;
};

export const isApiResponse = (response: any): response is ApiResponse<any> => {
  const isValid =
    typeof response === 'object' && response !== null && typeof response.success === 'boolean';

  // Debug logs removidos para produção
  // if (!isValid) {
  //   console.error('🔍 [isApiResponse] VALIDATION FAILED:', {
  //     response,
  //     isObject: typeof response === 'object',
  //     isNotNull: response !== null,
  //     hasSuccess: 'success' in response,
  //     successType: typeof response?.success,
  //     successValue: response?.success,
  //   });
  // } else {
  //   console.log('🔍 [isApiResponse] VALIDATION PASSED:', {
  //     success: response.success,
  //     hasData: 'data' in response,
  //   });
  // }

  return isValid;
};

export const isValidLevelMetrics = (data: any): data is LevelMetrics => {
  return (
    typeof data === 'object' &&
    typeof data.novos === 'number' &&
    typeof data.pendentes === 'number' &&
    typeof data.progresso === 'number' &&
    typeof data.resolvidos === 'number' &&
    typeof data.total === 'number'
  );
};

export const isValidNiveisMetrics = (data: any): data is NiveisMetrics => {
  // Debug logs removidos para produção
  // console.log('🔍 [isValidNiveisMetrics] Validating data:', data);
  // console.log('🔍 [isValidNiveisMetrics] data.n1:', data?.n1);
  // console.log('🔍 [isValidNiveisMetrics] data.n2:', data?.n2);
  // console.log('🔍 [isValidNiveisMetrics] data.n3:', data?.n3);
  // console.log('🔍 [isValidNiveisMetrics] data.n4:', data?.n4);

  const isValid =
    typeof data === 'object' &&
    data !== null &&
    isValidLevelMetrics(data.n1) &&
    isValidLevelMetrics(data.n2) &&
    isValidLevelMetrics(data.n3) &&
    isValidLevelMetrics(data.n4);
  // Removido data.geral pois não existe nos dados do backend

  // console.log('🔍 [isValidNiveisMetrics] Validation result:', isValid);
  return isValid;
};

// Utilitários de transformação
export const transformLegacyData = (legacyData: any): DashboardMetrics => {
  // Debug logs removidos para produção
  // console.log('🔍 [transformLegacyData] Input data:', legacyData);
  // console.log('🔍 [transformLegacyData] legacyData?.niveis:', legacyData?.niveis);

  // Função para transformar dados legados em formato atual
  const defaultLevel: LevelMetrics = {
    novos: 0,
    pendentes: 0,
    progresso: 0,
    resolvidos: 0,
    total: 0,
  };

  // Se os dados já vêm na estrutura correta da API
  if (legacyData?.niveis) {
    // console.log('🔍 [transformLegacyData] Using niveis structure');
    const result = {
      // Incluir os valores totais diretamente dos dados da API
      novos: legacyData.novos || 0,
      pendentes: legacyData.pendentes || 0,
      progresso: legacyData.progresso || 0,
      resolvidos: legacyData.resolvidos || 0,
      total: legacyData.total || 0,
      niveis: {
        n1: legacyData.niveis.n1 || defaultLevel,
        n2: legacyData.niveis.n2 || defaultLevel,
        n3: legacyData.niveis.n3 || defaultLevel,
        n4: legacyData.niveis.n4 || defaultLevel,
        // Removido geral: não existe nos dados do backend
      },

      filtros_aplicados: legacyData?.filtros_aplicados,
      tempo_execucao: legacyData?.tempo_execucao,
      timestamp: legacyData?.timestamp,
      systemStatus: legacyData?.systemStatus,
      technicianRanking: legacyData?.technicianRanking,
    };
    // console.log('🔍 [transformLegacyData] Result with niveis:', result);
    return result;
  }

  // Fallback para dados legados
  // console.log('🔍 [transformLegacyData] Using fallback structure');
  const fallbackResult = {
    // Incluir os valores totais diretamente dos dados da API
    novos: legacyData?.novos || 0,
    pendentes: legacyData?.pendentes || 0,
    progresso: legacyData?.progresso || 0,
    resolvidos: legacyData?.resolvidos || 0,
    total: legacyData?.total || 0,
    niveis: {
      n1: legacyData?.n1 || defaultLevel,
      n2: legacyData?.n2 || defaultLevel,
      n3: legacyData?.n3 || defaultLevel,
      n4: legacyData?.n4 || defaultLevel,
      // Removido geral: não existe nos dados do backend
    },

    filtros_aplicados: legacyData?.filtros_aplicados,
    tempo_execucao: legacyData?.tempo_execucao,
    timestamp: legacyData?.timestamp,
    systemStatus: legacyData?.systemStatus,
    technicianRanking: legacyData?.technicianRanking,
  };
  // console.log('🔍 [transformLegacyData] Fallback result:', fallbackResult);
  return fallbackResult;
};
