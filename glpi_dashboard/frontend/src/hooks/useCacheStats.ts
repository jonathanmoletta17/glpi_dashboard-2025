import { useState, useEffect } from 'react';
import { unifiedCache } from '../services/unifiedCache';

/**
 * Hook para monitorar estatísticas do cache unificado
 */
export const useCacheStats = (refreshInterval: number = 5000) => {
  const [stats, setStats] = useState(() => unifiedCache.getAllStats());
  const [isLoading, setIsLoading] = useState(false);

  const refreshStats = () => {
    setIsLoading(true);
    try {
      const newStats = unifiedCache.getAllStats();
      setStats(newStats);
    } catch (error) {
      console.error('Erro ao obter estatísticas do cache:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshStats();

    const interval = setInterval(refreshStats, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  const clearAllCaches = () => {
    unifiedCache.clearAll();
    refreshStats();
  };

  const invalidateTicketCache = () => {
    unifiedCache.invalidatePattern('newTickets', '.*');
    unifiedCache.invalidatePattern('tickets', '.*');
    refreshStats();
  };

  const invalidateMetricsCache = () => {
    unifiedCache.invalidatePattern('metrics', '.*');
    refreshStats();
  };

  const optimizeCaches = () => {
    // O unifiedCache não tem método optimize específico
    // Mas podemos limpar todos os caches
    unifiedCache.clearAll();
    refreshStats();
  };

  return {
    stats,
    isLoading,
    refreshStats,
    clearAllCaches,
    invalidateTicketCache,
    invalidateMetricsCache,
    optimizeCaches,
  };
};

/**
 * Hook simplificado para verificar se o cache está funcionando bem
 */
export const useCacheHealth = () => {
  const { stats } = useCacheStats(10000); // Atualiza a cada 10 segundos

  // Calcular hit rate geral
  const totalHits = Object.values(stats).reduce((sum, cacheStats: any) => sum + (cacheStats.hitRate || 0), 0);
  const totalRequests = Object.values(stats).reduce((sum, cacheStats: any) => sum + (cacheStats.totalRequests || 0), 0);
  const overallHitRate = totalRequests > 0 ? totalHits / Object.keys(stats).length : 0;

  const health = {
    isHealthy: overallHitRate > 0.5, // Hit rate acima de 50%
    hitRate: overallHitRate,
    memoryUsage: Object.values(stats).reduce((sum, cacheStats: any) => sum + (cacheStats.memoryUsage || 0), 0),
    totalEntries: Object.values(stats).reduce((sum, cacheStats: any) => sum + (cacheStats.size || 0), 0),
    status:
      overallHitRate > 0.7
        ? 'excellent'
        : overallHitRate > 0.5
          ? 'good'
          : overallHitRate > 0.3
            ? 'fair'
            : 'poor',
  };

  return health;
};