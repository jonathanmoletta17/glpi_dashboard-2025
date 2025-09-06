/**
 * Configuração Centralizada da Aplicação
 *
 * Este arquivo centraliza todas as configurações da aplicação,
 * eliminando configurações hardcoded espalhadas pelos componentes.
 */

// Tipos de configuração
export interface EnvironmentConfig {
  development: {
    minimumScore: number;
    checkInterval: number;
    enabledChecks: string[];
    alertThresholds: {
      responseTime: number;
      errorRate: number;
      memoryUsage: number;
    };
    autoRecovery: boolean;
    notifications: {
      enabled: boolean;
      duration: number;
      maxVisible: number;
    };
    logging: {
      level: 'debug' | 'info' | 'warn' | 'error';
      enableConsole: boolean;
    };
  };
  production: {
    minimumScore: number;
    checkInterval: number;
    enabledChecks: string[];
    alertThresholds: {
      responseTime: number;
      errorRate: number;
      memoryUsage: number;
    };
    autoRecovery: boolean;
    notifications: {
      enabled: boolean;
      duration: number;
      maxVisible: number;
    };
    logging: {
      level: 'debug' | 'info' | 'warn' | 'error';
      enableConsole: boolean;
    };
  };
}

export interface LoadingConfig {
  skeletonAnimationDuration: number;
  minimumLoadingTime: number;
  timeoutDuration: number;
  showProgressAfter: number;
  states: {
    initial: string;
    pending: string;
    success: string;
    error: string;
  };
}

export interface NotificationConfig {
  defaultDuration: number;
  maxVisible: number;
  position: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
  priorities: {
    critical: {
      duration: number;
      persistent: boolean;
      sound: boolean;
    };
    high: {
      duration: number;
      persistent: boolean;
      sound: boolean;
    };
    medium: {
      duration: number;
      persistent: boolean;
      sound: boolean;
    };
    low: {
      duration: number;
      persistent: boolean;
      sound: boolean;
    };
  };
  types: {
    cache: {
      enabled: boolean;
      duration: number;
      showIcon: boolean;
    };
    system: {
      enabled: boolean;
      duration: number;
      showIcon: boolean;
    };
    user: {
      enabled: boolean;
      duration: number;
      showIcon: boolean;
    };
  };
}

export interface APIConfig {
  baseURL: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
  endpoints: {
    dashboard: string;
    ranking: string;
    metrics: string;
    health: string;
  };
}

export interface CacheConfig {
  defaultTTL: number;
  maxSize: number;
  cleanupInterval: number;
  strategies: {
    dashboard: {
      ttl: number;
      maxAge: number;
    };
    ranking: {
      ttl: number;
      maxAge: number;
    };
    metrics: {
      ttl: number;
      maxAge: number;
    };
  };
}

// Configurações por ambiente
const environmentConfigs: EnvironmentConfig = {
  development: {
    minimumScore: 75,
    checkInterval: 15000,
    enabledChecks: ['api-health', 'data-integrity', 'visual-validation', 'performance-monitoring'],
    alertThresholds: {
      responseTime: 2000,
      errorRate: 0.1,
      memoryUsage: 80,
    },
    autoRecovery: true,
    notifications: {
      enabled: true,
      duration: 5000,
      maxVisible: 5,
    },
    logging: {
      level: 'debug',
      enableConsole: true,
    },
  },
  production: {
    minimumScore: 90,
    checkInterval: 60000,
    enabledChecks: ['api-health', 'data-integrity', 'performance-monitoring'],
    alertThresholds: {
      responseTime: 1000,
      errorRate: 0.05,
      memoryUsage: 70,
    },
    autoRecovery: false,
    notifications: {
      enabled: true,
      duration: 8000,
      maxVisible: 3,
    },
    logging: {
      level: 'warn',
      enableConsole: false,
    },
  },
};

// Configuração de loading states
const loadingConfig: LoadingConfig = {
  skeletonAnimationDuration: 1500,
  minimumLoadingTime: 500,
  timeoutDuration: 30000,
  showProgressAfter: 2000,
  states: {
    initial: 'Carregando...',
    pending: 'Processando...',
    success: 'Concluído',
    error: 'Erro ao carregar',
  },
};

// Configuração do sistema de notificações
const notificationConfig: NotificationConfig = {
  defaultDuration: 5000,
  maxVisible: 3,
  position: 'top-right',
  priorities: {
    critical: {
      duration: 0, // Persistente
      persistent: true,
      sound: true,
    },
    high: {
      duration: 10000,
      persistent: false,
      sound: true,
    },
    medium: {
      duration: 5000,
      persistent: false,
      sound: false,
    },
    low: {
      duration: 3000,
      persistent: false,
      sound: false,
    },
  },
  types: {
    cache: {
      enabled: true,
      duration: 3000,
      showIcon: true,
    },
    system: {
      enabled: true,
      duration: 5000,
      showIcon: true,
    },
    user: {
      enabled: true,
      duration: 4000,
      showIcon: false,
    },
  },
};

// Configuração da API
const apiConfig: APIConfig = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  timeout: 10000,
  retryAttempts: 3,
  retryDelay: 1000,
  endpoints: {
    dashboard: '/api/dashboard',
    ranking: '/api/ranking',
    metrics: '/api/metrics',
    health: '/api/health',
  },
};

// Configuração do cache
const cacheConfig: CacheConfig = {
  defaultTTL: 300000, // 5 minutos
  maxSize: 100,
  cleanupInterval: 60000, // 1 minuto
  strategies: {
    dashboard: {
      ttl: 180000, // 3 minutos
      maxAge: 600000, // 10 minutos
    },
    ranking: {
      ttl: 300000, // 5 minutos
      maxAge: 900000, // 15 minutos
    },
    metrics: {
      ttl: 120000, // 2 minutos
      maxAge: 300000, // 5 minutos
    },
  },
};

// Função para obter configuração do ambiente atual
function getCurrentEnvironment(): 'development' | 'production' {
  return (import.meta.env.MODE as 'development' | 'production') || 'development';
}

// Exportações principais
export const appConfig = {
  environment: environmentConfigs[getCurrentEnvironment()],
  loading: loadingConfig,
  notifications: notificationConfig,
  api: apiConfig,
  cache: cacheConfig,

  // Helpers
  isDevelopment: getCurrentEnvironment() === 'development',
  isProduction: getCurrentEnvironment() === 'production',

  // Getters para configurações específicas
  getNotificationDuration: (priority: keyof NotificationConfig['priorities'] = 'medium') => {
    return notificationConfig.priorities[priority].duration || notificationConfig.defaultDuration;
  },

  getLoadingTimeout: () => {
    return loadingConfig.timeoutDuration;
  },

  getAPITimeout: () => {
    return apiConfig.timeout;
  },

  getCacheTTL: (strategy: keyof CacheConfig['strategies'] = 'dashboard') => {
    return cacheConfig.strategies[strategy].ttl;
  },
};

// Configurações específicas para componentes
export const componentConfigs = {
  unifiedMonitor: {
    enabled: appConfig.environment.enabledChecks.includes('performance-monitoring'),
    minimumScore: appConfig.environment.minimumScore,
    checkInterval: appConfig.environment.checkInterval,
    enabledChecks: appConfig.environment.enabledChecks,
    alertThresholds: appConfig.environment.alertThresholds,
    autoRecovery: appConfig.environment.autoRecovery,
    notifications: appConfig.environment.notifications,
  },

  unifiedLoading: {
    animationDuration: appConfig.loading.skeletonAnimationDuration,
    minimumTime: appConfig.loading.minimumLoadingTime,
    timeout: appConfig.loading.timeoutDuration,
    messages: appConfig.loading.states,
    defaultType: 'spinner',
    defaultSize: 'md',
    defaultVariant: 'default',
  },

  notificationSystem: {
    maxVisible: appConfig.notifications.maxVisible,
    position: appConfig.notifications.position,
    defaultDuration: appConfig.notifications.defaultDuration,
    priorities: appConfig.notifications.priorities,
  },

  cacheNotification: {
    enabled: appConfig.notifications.types.cache.enabled,
    autoCloseDelay: appConfig.notifications.types.cache.duration,
    showIcon: appConfig.notifications.types.cache.showIcon,
  },
};

export default appConfig;
