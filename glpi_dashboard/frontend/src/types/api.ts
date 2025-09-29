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

  filtros_aplicados?: Record<string, unknown>;
  tempo_execucao?: number;
  timestamp?: string;
  systemStatus?: SystemStatus;
  technicianRanking?: TechnicianRanking[];
}

// Status do sistema
export interface SystemStatus {
  api: string;
  glpi: string;
  glpi_message: string;
  glpi_response_time: number;
  last_update: string;
  version: string;
  // Campos de compatibilidade
  status?: 'online' | 'offline' | 'maintenance';
  sistema_ativo?: boolean;
  ultima_atualizacao?: string;
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
export interface ApiResponse<T = unknown> {
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
  details?: Record<string, unknown>;
  timestamp?: string;
  code?: string | number;
}

// Resultado da API (união de sucesso e erro)
export type ApiResult<T = unknown> = ApiResponse<T> | ApiError;

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
export interface ValidationResult<T = unknown> {
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
  details?: Record<string, unknown>;
}

// Type guards para verificação de tipos em runtime
export const isApiError = (response: ApiResult): response is ApiError => {
  return response.success === false;
};

export const isApiResponse = (response: unknown): response is ApiResponse<unknown> => {
<<<<<<< Updated upstream
  const obj = response as any;
=======
  const obj = response as Record<string, unknown>;
>>>>>>> Stashed changes
  const isValid =
    typeof response === 'object' && response !== null && typeof obj.success === 'boolean';

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

export const isValidLevelMetrics = (data: unknown): data is LevelMetrics => {
<<<<<<< Updated upstream
  const obj = data as any;
=======
  const obj = data as Record<string, unknown>;
>>>>>>> Stashed changes
  return (
    typeof data === 'object' &&
    data !== null &&
    typeof obj.novos === 'number' &&
    typeof obj.pendentes === 'number' &&
    typeof obj.progresso === 'number' &&
    typeof obj.resolvidos === 'number' &&
    typeof obj.total === 'number'
  );
};

export const isDashboardMetrics = (data: unknown): data is DashboardMetrics => {
<<<<<<< Updated upstream
  const obj = data as any;
=======
  const obj = data as Record<string, unknown>;
>>>>>>> Stashed changes
  return (
    typeof data === 'object' &&
    data !== null &&
    typeof obj.novos === 'number' &&
    typeof obj.pendentes === 'number' &&
    typeof obj.progresso === 'number' &&
    typeof obj.resolvidos === 'number' &&
    typeof obj.total === 'number'
  );
};

export const isValidNiveisMetrics = (data: unknown): data is NiveisMetrics => {
  // Debug logs removidos para produção
  // console.log('🔍 [isValidNiveisMetrics] Validating data:', data);
  // console.log('🔍 [isValidNiveisMetrics] data.n1:', data?.n1);
  // console.log('🔍 [isValidNiveisMetrics] data.n2:', data?.n2);
  // console.log('🔍 [isValidNiveisMetrics] data.n3:', data?.n3);
  // console.log('🔍 [isValidNiveisMetrics] data.n4:', data?.n4);

<<<<<<< Updated upstream
  const obj = data as any;
=======
  const obj = data as Record<string, unknown>;
>>>>>>> Stashed changes
  const isValid =
    typeof data === 'object' &&
    data !== null &&
    isValidLevelMetrics(obj.n1) &&
    isValidLevelMetrics(obj.n2) &&
    isValidLevelMetrics(obj.n3) &&
    isValidLevelMetrics(obj.n4);
  // Removido data.geral pois não existe nos dados do backend

  // console.log('🔍 [isValidNiveisMetrics] Validation result:', isValid);
  return isValid;
};

// Utilitários de transformação
export const transformLegacyData = (legacyData: unknown): DashboardMetrics => {
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
<<<<<<< Updated upstream
  const apiData = legacyData as any;
=======
  const apiData = legacyData as Record<string, unknown>;
>>>>>>> Stashed changes
  if (apiData?.niveis) {
    // console.log('🔍 [transformLegacyData] Using niveis structure');
    const result = {
      // Incluir os valores totais diretamente dos dados da API
<<<<<<< Updated upstream
      novos: apiData.novos || 0,
      pendentes: apiData.pendentes || 0,
      progresso: apiData.progresso || 0,
      resolvidos: apiData.resolvidos || 0,
      total: apiData.total || 0,
      niveis: {
        n1: apiData.niveis.n1 || defaultLevel,
        n2: apiData.niveis.n2 || defaultLevel,
        n3: apiData.niveis.n3 || defaultLevel,
        n4: apiData.niveis.n4 || defaultLevel,
=======
      novos: (apiData.novos as number) || 0,
      pendentes: (apiData.pendentes as number) || 0,
      progresso: (apiData.progresso as number) || 0,
      resolvidos: (apiData.resolvidos as number) || 0,
      total: (apiData.total as number) || 0,
      niveis: {
        n1: ((apiData.niveis as Record<string, unknown>)?.n1 as LevelMetrics) || defaultLevel,
        n2: ((apiData.niveis as Record<string, unknown>)?.n2 as LevelMetrics) || defaultLevel,
        n3: ((apiData.niveis as Record<string, unknown>)?.n3 as LevelMetrics) || defaultLevel,
        n4: ((apiData.niveis as Record<string, unknown>)?.n4 as LevelMetrics) || defaultLevel,
>>>>>>> Stashed changes
        // Removido geral: não existe nos dados do backend
      },

      filtros_aplicados: apiData?.filtros_aplicados,
      tempo_execucao: apiData?.tempo_execucao,
      timestamp: apiData?.timestamp,
      systemStatus: apiData?.systemStatus,
      technicianRanking: apiData?.technicianRanking,
    };
    // console.log('🔍 [transformLegacyData] Result with niveis:', result);
<<<<<<< Updated upstream
    return result;
=======
    return result as DashboardMetrics;
>>>>>>> Stashed changes
  }

  // Fallback para dados legados
  // console.log('🔍 [transformLegacyData] Using fallback structure');
<<<<<<< Updated upstream
  const fallbackData = legacyData as any;
  const fallbackResult = {
    // Incluir os valores totais diretamente dos dados da API
    novos: fallbackData?.novos || 0,
    pendentes: fallbackData?.pendentes || 0,
    progresso: fallbackData?.progresso || 0,
    resolvidos: fallbackData?.resolvidos || 0,
    total: fallbackData?.total || 0,
    niveis: {
      n1: fallbackData?.n1 || defaultLevel,
      n2: fallbackData?.n2 || defaultLevel,
      n3: fallbackData?.n3 || defaultLevel,
      n4: fallbackData?.n4 || defaultLevel,
=======
  const fallbackData = legacyData as Record<string, unknown>;
  const fallbackResult = {
    // Incluir os valores totais diretamente dos dados da API
    novos: (fallbackData?.novos as number) || 0,
    pendentes: (fallbackData?.pendentes as number) || 0,
    progresso: (fallbackData?.progresso as number) || 0,
    resolvidos: (fallbackData?.resolvidos as number) || 0,
    total: (fallbackData?.total as number) || 0,
    niveis: {
      n1: (fallbackData?.n1 as LevelMetrics) || defaultLevel,
      n2: (fallbackData?.n2 as LevelMetrics) || defaultLevel,
      n3: (fallbackData?.n3 as LevelMetrics) || defaultLevel,
      n4: (fallbackData?.n4 as LevelMetrics) || defaultLevel,
>>>>>>> Stashed changes
      // Removido geral: não existe nos dados do backend
    },

    filtros_aplicados: fallbackData?.filtros_aplicados,
    tempo_execucao: fallbackData?.tempo_execucao,
    timestamp: fallbackData?.timestamp,
    systemStatus: fallbackData?.systemStatus,
    technicianRanking: fallbackData?.technicianRanking,
  };
  // console.log('🔍 [transformLegacyData] Fallback result:', fallbackResult);
<<<<<<< Updated upstream
  return fallbackResult;
=======
  return fallbackResult as DashboardMetrics;
>>>>>>> Stashed changes
};
