import { useCallback, useEffect, useState } from 'react';
import { unifiedCache } from '../services/unifiedCache';

export interface CacheStats {
  metrics: {
    size: number;
    hitRate: number;
    missRate: number;
    totalRequests: number;
  };
  systemStatus: {
    size: number;
    hitRate: number;
    missRate: number;
    totalRequests: number;
  };
  technicianRanking: {
    size: number;
    hitRate: number;
    missRate: number;
    totalRequests: number;
  };
  newTickets: {
    size: number;
    hitRate: number;
    missRate: number;
    totalRequests: number;
  };
}

export interface UseCacheReturn {
  stats: Record<string, any>;
  isLoading: boolean;
  error: string | null;
  refreshAll: () => Promise<void>;
  clearAll: () => void;
  getStats: () => Record<string, any>;
  refreshMetrics: () => Promise<void>;
  refreshSystemStatus: () => Promise<void>;
  refreshTechnicianRanking: () => Promise<void>;
  refreshNewTickets: () => Promise<void>;
}

export const useCache = (): UseCacheReturn => {
  const [stats, setStats] = useState<Record<string, any>>(() => {
    try {
      return unifiedCache.getAllStats();
    } catch (error) {
      console.error('Erro ao obter estatísticas do cache:', error);
      return {
        metrics: { size: 0, hitRate: 0, missRate: 0, totalRequests: 0 },
        systemStatus: { size: 0, hitRate: 0, missRate: 0, totalRequests: 0 },
        technicianRanking: { size: 0, hitRate: 0, missRate: 0, totalRequests: 0 },
        newTickets: { size: 0, hitRate: 0, missRate: 0, totalRequests: 0 },
      };
    }
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshAll = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Limpar todos os caches
      unifiedCache.clearAll();
      
      // Aguardar um pouco para garantir que a limpeza foi processada
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Atualizar estatísticas
      setStats(unifiedCache.getAllStats());
      
      console.log('✅ Todos os caches foram atualizados');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMessage);
      console.error('❌ Erro ao atualizar caches:', errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearAll = useCallback(() => {
    try {
      unifiedCache.clearAll();
      setStats(unifiedCache.getAllStats());
      console.log('✅ Todos os caches foram limpos');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMessage);
      console.error('❌ Erro ao limpar caches:', errorMessage);
    }
  }, []);

  const getStats = useCallback((): Record<string, any> => {
    try {
      return unifiedCache.getAllStats();
    } catch (error) {
      console.error('Erro ao obter estatísticas do cache:', error);
      return {
        metrics: { size: 0, hitRate: 0, missRate: 0, totalRequests: 0 },
        systemStatus: { size: 0, hitRate: 0, missRate: 0, totalRequests: 0 },
        technicianRanking: { size: 0, hitRate: 0, missRate: 0, totalRequests: 0 },
        newTickets: { size: 0, hitRate: 0, missRate: 0, totalRequests: 0 },
      };
    }
  }, []);

  const refreshMetrics = useCallback(async () => {
    try {
      // Invalidar cache de métricas
      unifiedCache.invalidatePattern('metrics', '.*');
      setStats(unifiedCache.getAllStats());
      console.log('✅ Cache de métricas atualizado');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMessage);
      console.error('❌ Erro ao atualizar cache de métricas:', errorMessage);
    }
  }, []);

  const refreshSystemStatus = useCallback(async () => {
    try {
      // Invalidar cache de status do sistema
      unifiedCache.invalidatePattern('systemStatus', '.*');
      setStats(unifiedCache.getAllStats());
      console.log('✅ Cache de status do sistema atualizado');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMessage);
      console.error('❌ Erro ao atualizar cache de status do sistema:', errorMessage);
    }
  }, []);

  const refreshTechnicianRanking = useCallback(async () => {
    try {
      // Invalidar cache de ranking de técnicos
      unifiedCache.invalidatePattern('technicianRanking', '.*');
      setStats(unifiedCache.getAllStats());
      console.log('✅ Cache de ranking de técnicos atualizado');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMessage);
      console.error('❌ Erro ao atualizar cache de ranking de técnicos:', errorMessage);
    }
  }, []);

  const refreshNewTickets = useCallback(async () => {
    try {
      // Invalidar cache de tickets novos
      unifiedCache.invalidatePattern('newTickets', '.*');
      setStats(unifiedCache.getAllStats());
      console.log('✅ Cache de tickets novos atualizado');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMessage);
      console.error('❌ Erro ao atualizar cache de tickets novos:', errorMessage);
    }
  }, []);

  // Atualizar estatísticas periodicamente
  useEffect(() => {
    const interval = setInterval(() => {
      setStats(unifiedCache.getAllStats());
    }, 5000); // A cada 5 segundos

    return () => clearInterval(interval);
  }, []);

  return {
    stats,
    isLoading,
    error,
    refreshAll,
    clearAll,
    getStats,
    refreshMetrics,
    refreshSystemStatus,
    refreshTechnicianRanking,
    refreshNewTickets,
  };
};