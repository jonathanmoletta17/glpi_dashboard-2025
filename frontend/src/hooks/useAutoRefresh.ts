/**
 * Hook para Auto-Refresh de Métricas Críticas
 *
 * Implementa sistema de atualização automática baseado em prioridade
 * e padrões de uso para manter dados sempre atualizados.
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import { cacheInvalidationService } from '../services/CacheInvalidationService';

interface AutoRefreshConfig {
  interval: number; // Intervalo em milissegundos
  priority: 'high' | 'medium' | 'low';
  enabled: boolean;
  onRefresh?: () => Promise<void>;
  onError?: (error: Error) => void;
}

interface RefreshStats {
  lastRefresh: number;
  refreshCount: number;
  errorCount: number;
  avgDuration: number;
}

const DEFAULT_INTERVALS = {
  high: 30000, // 30 segundos
  medium: 60000, // 1 minuto
  low: 300000, // 5 minutos
};

export const useAutoRefresh = (
  key: string,
  refreshFunction: () => Promise<void>,
  config: Partial<AutoRefreshConfig> = {}
) => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [stats, setStats] = useState<RefreshStats>({
    lastRefresh: 0,
    refreshCount: 0,
    errorCount: 0,
    avgDuration: 0,
  });
  const [error, setError] = useState<Error | null>(null);

  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const durations = useRef<number[]>([]);

  const finalConfig: AutoRefreshConfig = {
    interval: config.interval || DEFAULT_INTERVALS[config.priority || 'medium'],
    priority: config.priority || 'medium',
    enabled: config.enabled !== false,
    onRefresh: config.onRefresh,
    onError: config.onError,
  };

  /**
   * Executa o refresh com métricas e tratamento de erro
   */
  const executeRefresh = useCallback(async () => {
    if (isRefreshing) return;

    setIsRefreshing(true);
    setError(null);

    const startTime = Date.now();

    try {
      await refreshFunction();

      const duration = Date.now() - startTime;
      durations.current.push(duration);

      // Manter apenas as últimas 10 durações para calcular média
      if (durations.current.length > 10) {
        durations.current = durations.current.slice(-10);
      }

      const avgDuration = durations.current.reduce((a, b) => a + b, 0) / durations.current.length;

      setStats(prev => ({
        lastRefresh: Date.now(),
        refreshCount: prev.refreshCount + 1,
        errorCount: prev.errorCount,
        avgDuration: Math.round(avgDuration),
      }));

      // Executar callback de sucesso se fornecido
      if (finalConfig.onRefresh) {
        await finalConfig.onRefresh();
      }

      console.log(`✅ Auto-refresh executado: ${key} (${duration}ms)`);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Erro desconhecido no auto-refresh');

      setError(error);
      setStats(prev => ({
        ...prev,
        errorCount: prev.errorCount + 1,
      }));

      // Executar callback de erro se fornecido
      if (finalConfig.onError) {
        finalConfig.onError(error);
      }

      console.error(`❌ Erro no auto-refresh ${key}:`, error);
    } finally {
      setIsRefreshing(false);
    }
  }, [key, refreshFunction, finalConfig, isRefreshing]);

  /**
   * Inicia o auto-refresh
   */
  const start = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    if (finalConfig.enabled) {
      intervalRef.current = setInterval(executeRefresh, finalConfig.interval);
      console.log(`🔄 Auto-refresh iniciado: ${key} (${finalConfig.interval}ms)`);
    }
  }, [key, executeRefresh, finalConfig.enabled, finalConfig.interval]);

  /**
   * Para o auto-refresh
   */
  const stop = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
      console.log(`⏹️ Auto-refresh parado: ${key}`);
    }
  }, [key]);

  /**
   * Força um refresh imediato
   */
  const forceRefresh = useCallback(async () => {
    await executeRefresh();
  }, [executeRefresh]);

  /**
   * Reseta as estatísticas
   */
  const resetStats = useCallback(() => {
    setStats({
      lastRefresh: 0,
      refreshCount: 0,
      errorCount: 0,
      avgDuration: 0,
    });
    durations.current = [];
    setError(null);
  }, []);

  // Efeito para gerenciar o ciclo de vida do auto-refresh
  useEffect(() => {
    if (finalConfig.enabled) {
      start();
    } else {
      stop();
    }

    return () => {
      stop();
    };
  }, [finalConfig.enabled, start, stop]);

  // Cleanup ao desmontar o componente
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return {
    isRefreshing,
    stats,
    error,
    start,
    stop,
    forceRefresh,
    resetStats,
    config: finalConfig,
  };
};

/**
 * Hook especializado para métricas críticas
 */
export const useMetricsAutoRefresh = (refreshFunction: () => Promise<void>) => {
  return useAutoRefresh('metrics', refreshFunction, {
    priority: 'high',
    interval: 30000, // 30 segundos
    enabled: true,
    onRefresh: async () => {
      // Invalidar cache de métricas após refresh bem-sucedido
      cacheInvalidationService.invalidateCriticalMetrics();
    },
  });
};

/**
 * Hook especializado para status do sistema
 */
export const useSystemStatusAutoRefresh = (refreshFunction: () => Promise<void>) => {
  return useAutoRefresh('systemStatus', refreshFunction, {
    priority: 'high',
    interval: 60000, // 1 minuto
    enabled: true,
    onRefresh: async () => {
      // Invalidar cache de status após refresh
      cacheInvalidationService.invalidateOnSystemStatusChange();
    },
  });
};

/**
 * Hook especializado para ranking de técnicos
 */
export const useTechnicianRankingAutoRefresh = (refreshFunction: () => Promise<void>) => {
  return useAutoRefresh('technicianRanking', refreshFunction, {
    priority: 'medium',
    interval: 300000, // 5 minutos
    enabled: true,
  });
};

/**
 * Hook especializado para novos tickets
 */
export const useNewTicketsAutoRefresh = (refreshFunction: () => Promise<void>) => {
  return useAutoRefresh('newTickets', refreshFunction, {
    priority: 'high',
    interval: 60000, // 1 minuto
    enabled: true,
    onRefresh: async () => {
      // Invalidar cache relacionado a tickets
      cacheInvalidationService.invalidateOnTicketChange();
    },
  });
};
