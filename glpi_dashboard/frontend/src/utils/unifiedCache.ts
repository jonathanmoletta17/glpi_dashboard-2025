/**
 * Sistema de cache unificado para consolidar múltiplos sistemas de cache.
 * 
 * Este módulo centraliza o gerenciamento de cache, substituindo os sistemas
 * fragmentados (metricsCache, systemStatusCache, smartCacheManager) por
 * uma interface única e consistente.
 */

import { DashboardMetrics, SystemStatus } from '../types';

/**
 * Interface para configuração de cache
 */
interface CacheConfig {
  ttl: number; // Time to live em milissegundos
  maxSize: number; // Tamanho máximo do cache
  enableMetrics: boolean; // Habilitar métricas de performance
}

/**
 * Interface para entrada do cache
 */
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
  hits: number;
  lastAccessed: number;
}

/**
 * Interface para métricas do cache
 */
interface CacheMetrics {
  hits: number;
  misses: number;
  hitRate: number;
  size: number;
  maxSize: number;
  averageResponseTime: number;
  lastCleanup: number;
}

/**
 * Classe principal do sistema de cache unificado
 */
export class UnifiedCache {
  private cache = new Map<string, CacheEntry<any>>();
  private config: CacheConfig;
  private metrics: CacheMetrics;
  private cleanupInterval: NodeJS.Timeout | null = null;

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = {
      ttl: 5 * 60 * 1000, // 5 minutos padrão
      maxSize: 100,
      enableMetrics: true,
      ...config
    };

    this.metrics = {
      hits: 0,
      misses: 0,
      hitRate: 0,
      size: 0,
      maxSize: this.config.maxSize,
      averageResponseTime: 0,
      lastCleanup: Date.now()
    };

    // Iniciar limpeza automática
    this.startCleanupInterval();
  }

  /**
   * Armazena um item no cache
   */
  set<T>(key: string, data: T, customTtl?: number): void {
    const now = Date.now();
    const ttl = customTtl || this.config.ttl;

    // Verificar se precisa fazer limpeza por tamanho
    if (this.cache.size >= this.config.maxSize) {
      this.evictOldest();
    }

    const entry: CacheEntry<T> = {
      data,
      timestamp: now,
      ttl,
      hits: 0,
      lastAccessed: now
    };

    this.cache.set(key, entry);
    this.updateMetrics();
  }

  /**
   * Recupera um item do cache
   */
  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    const now = Date.now();

    if (!entry) {
      this.recordMiss();
      return null;
    }

    // Verificar se expirou
    if (now - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      this.recordMiss();
      return null;
    }

    // Atualizar estatísticas de acesso
    entry.hits++;
    entry.lastAccessed = now;
    this.recordHit();

    return entry.data as T;
  }

  /**
   * Verifica se uma chave existe no cache e não expirou
   */
  has(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) return false;

    const now = Date.now();
    if (now - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return false;
    }

    return true;
  }

  /**
   * Remove um item específico do cache
   */
  delete(key: string): boolean {
    const result = this.cache.delete(key);
    this.updateMetrics();
    return result;
  }

  /**
   * Limpa todo o cache
   */
  clear(): void {
    this.cache.clear();
    this.resetMetrics();
  }

  /**
   * Remove entradas expiradas
   */
  cleanup(): number {
    const now = Date.now();
    let removedCount = 0;

    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > entry.ttl) {
        this.cache.delete(key);
        removedCount++;
      }
    }

    this.metrics.lastCleanup = now;
    this.updateMetrics();
    return removedCount;
  }

  /**
   * Remove a entrada mais antiga (LRU)
   */
  private evictOldest(): void {
    let oldestKey: string | null = null;
    let oldestTime = Date.now();

    for (const [key, entry] of this.cache.entries()) {
      if (entry.lastAccessed < oldestTime) {
        oldestTime = entry.lastAccessed;
        oldestKey = key;
      }
    }

    if (oldestKey) {
      this.cache.delete(oldestKey);
    }
  }

  /**
   * Registra um cache hit
   */
  private recordHit(): void {
    if (this.config.enableMetrics) {
      this.metrics.hits++;
      this.updateHitRate();
    }
  }

  /**
   * Registra um cache miss
   */
  private recordMiss(): void {
    if (this.config.enableMetrics) {
      this.metrics.misses++;
      this.updateHitRate();
    }
  }

  /**
   * Atualiza a taxa de acerto
   */
  private updateHitRate(): void {
    const total = this.metrics.hits + this.metrics.misses;
    this.metrics.hitRate = total > 0 ? (this.metrics.hits / total) * 100 : 0;
  }

  /**
   * Atualiza métricas gerais
   */
  private updateMetrics(): void {
    this.metrics.size = this.cache.size;
  }

  /**
   * Reseta as métricas
   */
  private resetMetrics(): void {
    this.metrics = {
      hits: 0,
      misses: 0,
      hitRate: 0,
      size: 0,
      maxSize: this.config.maxSize,
      averageResponseTime: 0,
      lastCleanup: Date.now()
    };
  }

  /**
   * Inicia o intervalo de limpeza automática
   */
  private startCleanupInterval(): void {
    // Limpeza a cada 5 minutos
    this.cleanupInterval = setInterval(() => {
      this.cleanup();
    }, 5 * 60 * 1000);
  }

  /**
   * Para o intervalo de limpeza
   */
  private stopCleanupInterval(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
    }
  }

  /**
   * Obtém métricas do cache
   */
  getMetrics(): CacheMetrics {
    return { ...this.metrics };
  }

  /**
   * Obtém informações de uma entrada específica
   */
  getEntryInfo(key: string): Partial<CacheEntry<any>> | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    return {
      timestamp: entry.timestamp,
      ttl: entry.ttl,
      hits: entry.hits,
      lastAccessed: entry.lastAccessed
    };
  }

  /**
   * Lista todas as chaves no cache
   */
  keys(): string[] {
    return Array.from(this.cache.keys());
  }

  /**
   * Obtém o tamanho atual do cache
   */
  size(): number {
    return this.cache.size;
  }

  /**
   * Destrói o cache e limpa recursos
   */
  destroy(): void {
    this.stopCleanupInterval();
    this.clear();
  }
}

/**
 * Instância global do cache unificado
 */
const globalCache = new UnifiedCache({
  ttl: 5 * 60 * 1000, // 5 minutos
  maxSize: 200,
  enableMetrics: true
});

/**
 * Cache especializado para métricas
 */
const metricsCache = new UnifiedCache({
  ttl: 2 * 60 * 1000, // 2 minutos para métricas
  maxSize: 50,
  enableMetrics: true
});

/**
 * Cache especializado para status do sistema
 */
const systemStatusCache = new UnifiedCache({
  ttl: 30 * 1000, // 30 segundos para status
  maxSize: 10,
  enableMetrics: true
});

/**
 * Cache especializado para ranking de técnicos
 */
const technicianRankingCache = new UnifiedCache({
  ttl: 10 * 60 * 1000, // 10 minutos para ranking
  maxSize: 20,
  enableMetrics: true
});

/**
 * Cache especializado para tickets novos
 */
const newTicketsCache = new UnifiedCache({
  ttl: 1 * 60 * 1000, // 1 minuto para tickets novos
  maxSize: 30,
  enableMetrics: true
});

/**
 * Interface unificada para gerenciamento de cache
 */
export const cacheManager = {
  // Cache global
  global: globalCache,
  
  // Caches especializados
  metrics: metricsCache,
  systemStatus: systemStatusCache,
  technicianRanking: technicianRankingCache,
  newTickets: newTicketsCache,

  // Métodos de conveniência
  clearAll(): void {
    globalCache.clear();
    metricsCache.clear();
    systemStatusCache.clear();
    technicianRankingCache.clear();
    newTicketsCache.clear();
  },

  getAllMetrics(): Record<string, CacheMetrics> {
    return {
      global: globalCache.getMetrics(),
      metrics: metricsCache.getMetrics(),
      systemStatus: systemStatusCache.getMetrics(),
      technicianRanking: technicianRankingCache.getMetrics(),
      newTickets: newTicketsCache.getMetrics()
    };
  },

  cleanupAll(): Record<string, number> {
    return {
      global: globalCache.cleanup(),
      metrics: metricsCache.cleanup(),
      systemStatus: systemStatusCache.cleanup(),
      technicianRanking: technicianRankingCache.cleanup(),
      newTickets: newTicketsCache.cleanup()
    };
  },

  destroyAll(): void {
    globalCache.destroy();
    metricsCache.destroy();
    systemStatusCache.destroy();
    technicianRankingCache.destroy();
    newTicketsCache.destroy();
  }
};

// Exportações para compatibilidade com código existente
export { metricsCache, systemStatusCache, technicianRankingCache, newTicketsCache };
export default cacheManager;