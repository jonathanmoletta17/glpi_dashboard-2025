/**
 * Sistema de Cache Unificado
 *
 * Consolida todos os sistemas de cache em uma única interface,
 * eliminando duplicidades e inconsistências identificadas na auditoria.
 */

// Interfaces base
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
  accessCount: number;
  lastAccessed: number;
}

interface CacheConfig {
  ttl: number; // Time to live em milissegundos
  maxSize: number; // Tamanho máximo do cache
  autoActivate?: boolean;
  performanceThreshold?: number; // ms - tempo mínimo de resposta para ativar cache
  usageThreshold?: number; // número de chamadas repetidas para ativar cache
}

interface CacheStats {
  hits: number;
  misses: number;
  sets: number;
  deletes: number;
  clears: number;
  size: number;
  maxSize: number;
  ttl: number;
  hitRate: number;
  isActive: boolean;
  totalRequests: number;
  avgResponseTime: number;
  memoryUsage: number;
}

interface RequestConfig {
  debounceMs?: number;
  throttleMs?: number;
  maxConcurrent?: number;
  cacheMs?: number;
}

interface PendingRequest {
  promise: Promise<any>;
  timestamp: number;
  key: string;
}

/**
 * Cache Unificado que consolida todas as funcionalidades
 */
class UnifiedCacheManager {
  private caches = new Map<string, Map<string, CacheEntry<any>>>();
  private configs = new Map<string, CacheConfig>();
  private stats = new Map<string, any>();
  private requestTimes = new Map<string, number[]>();
  private requestCounts = new Map<string, number>();
  private pendingRequests = new Map<string, PendingRequest>();
  private lastRequestTimes = new Map<string, number>();
  private globalCache = new Map<string, { data: any; timestamp: number }>();

  private readonly defaultConfig: CacheConfig = {
    ttl: 5 * 60 * 1000, // 5 minutos
    maxSize: 100,
    autoActivate: true,
    performanceThreshold: 500,
    usageThreshold: 3,
  };

  private readonly defaultRequestConfig: RequestConfig = {
    debounceMs: 300,
    throttleMs: 1000,
    maxConcurrent: 3,
    cacheMs: 30000,
  };

  constructor() {
    this.setupCleanupIntervals();
  }

  /**
   * Registra um novo tipo de cache
   */
  registerCacheType(type: string, config: Partial<CacheConfig> = {}): void {
    const finalConfig = { ...this.defaultConfig, ...config };
    this.configs.set(type, finalConfig);
    this.caches.set(type, new Map());
    this.stats.set(type, {
      hits: 0,
      misses: 0,
      sets: 0,
      deletes: 0,
      clears: 0,
    });
    this.requestTimes.set(type, []);
    this.requestCounts.set(type, 0);
  }

  /**
   * Gera chave única baseada nos parâmetros
   */
  private generateKey(params: Record<string, any>): string {
    const sortedKeys = Object.keys(params).sort();
    const keyParts = sortedKeys.map(key => `${key}:${params[key]}`);
    return keyParts.join('|');
  }

  /**
   * Verifica se uma entrada está expirada
   */
  private isExpired(entry: CacheEntry<any>): boolean {
    return Date.now() > entry.expiresAt;
  }

  /**
   * Verifica se o cache está ativo para o tipo especificado
   */
  private isCacheActive(type: string): boolean {
    const config = this.configs.get(type);
    if (!config) return false;

    if (!config.autoActivate) return true;

    // Verificar se deve ativar baseado em performance/uso
    const requestCount = this.requestCounts.get(type) || 0;
    const avgResponseTime = this.getAverageResponseTime(type);

    return (
      avgResponseTime >= config.performanceThreshold! || requestCount >= config.usageThreshold!
    );
  }

  /**
   * Calcula tempo médio de resposta para um tipo de cache
   */
  private getAverageResponseTime(type: string): number {
    const times = this.requestTimes.get(type) || [];
    if (times.length === 0) return 0;
    return times.reduce((sum, time) => sum + time, 0) / times.length;
  }

  /**
   * Registra tempo de resposta para análise de performance
   */
  recordRequestTime(type: string, key: string, responseTime: number): void {
    const config = this.configs.get(type);
    if (!config?.autoActivate) return;

    // Registrar tempo de resposta
    if (!this.requestTimes.has(type)) {
      this.requestTimes.set(type, []);
    }
    const times = this.requestTimes.get(type)!;
    times.push(responseTime);
    if (times.length > 10) times.shift();

    // Contar requisições
    const count = (this.requestCounts.get(type) || 0) + 1;
    this.requestCounts.set(type, count);
  }

  /**
   * Remove entradas expiradas do cache
   */
  private cleanExpired(type: string): void {
    const cache = this.caches.get(type);
    if (!cache) return;

    const now = Date.now();
    for (const [key, entry] of cache.entries()) {
      if (now > entry.expiresAt) {
        cache.delete(key);
      }
    }
  }

  /**
   * Remove entrada mais antiga se cache estiver cheio
   */
  private evictOldest(type: string): void {
    const cache = this.caches.get(type);
    const config = this.configs.get(type);
    if (!cache || !config) return;

    if (cache.size >= config.maxSize) {
      const oldestKey = cache.keys().next().value;
      if (oldestKey) {
        cache.delete(oldestKey);
      }
    }
  }

  /**
   * Armazena dados no cache
   */
  set(type: string, params: Record<string, any>, data: any): void {
    if (!this.isCacheActive(type)) return;

    const cache = this.caches.get(type);
    const config = this.configs.get(type);
    if (!cache || !config) return;

    const key = this.generateKey(params);
    const now = Date.now();

    this.evictOldest(type);

    cache.set(key, {
      data,
      timestamp: now,
      expiresAt: now + config.ttl,
      accessCount: 0,
      lastAccessed: now,
    });

    const stats = this.stats.get(type);
    if (stats) {
      stats.sets++;
    }
  }

  /**
   * Recupera dados do cache
   */
  get(type: string, params: Record<string, any>): any | null {
    if (!this.isCacheActive(type)) return null;

    const cache = this.caches.get(type);
    if (!cache) return null;

    const key = this.generateKey(params);
    const entry = cache.get(key);

    if (!entry) {
      const stats = this.stats.get(type);
      if (stats) stats.misses++;
      return null;
    }

    if (this.isExpired(entry)) {
      cache.delete(key);
      const stats = this.stats.get(type);
      if (stats) stats.misses++;
      return null;
    }

    // Cache hit
    const stats = this.stats.get(type);
    if (stats) stats.hits++;

    // Atualizar estatísticas de acesso
    entry.accessCount++;
    entry.lastAccessed = Date.now();

    return entry.data;
  }

  /**
   * Verifica se existe entrada válida no cache
   */
  has(type: string, params: Record<string, any>): boolean {
    return this.get(type, params) !== null;
  }

  /**
   * Remove entrada específica do cache
   */
  delete(type: string, params: Record<string, any>): boolean {
    const cache = this.caches.get(type);
    if (!cache) return false;

    const key = this.generateKey(params);
    const deleted = cache.delete(key);

    if (deleted) {
      const stats = this.stats.get(type);
      if (stats) stats.deletes++;
    }

    return deleted;
  }

  /**
   * Limpa cache de um tipo específico
   */
  clear(type: string): void {
    const cache = this.caches.get(type);
    if (cache) {
      cache.clear();
      const stats = this.stats.get(type);
      if (stats) stats.clears++;
    }
  }

  /**
   * Limpa todos os caches
   */
  clearAll(): void {
    for (const cache of this.caches.values()) {
      cache.clear();
    }
    this.globalCache.clear();
    this.pendingRequests.clear();
  }

  /**
   * Invalida cache por padrão
   */
  invalidatePattern(type: string, pattern: string): void {
    const cache = this.caches.get(type);
    if (!cache) return;

    const regex = new RegExp(pattern);
    let deletedCount = 0;

    for (const [key] of cache.entries()) {
      if (regex.test(key)) {
        cache.delete(key);
        deletedCount++;
      }
    }
  }

  /**
   * Coordena requisição com debouncing, throttling e cache
   */
  async coordinateRequest<T>(
    type: string,
    key: string,
    requestFn: () => Promise<T>,
    config: RequestConfig = {}
  ): Promise<T> {
    const finalConfig = { ...this.defaultRequestConfig, ...config };
    const now = Date.now();

    // Verificar cache global primeiro
    const globalKey = `${type}:${key}`;
    const cached = this.globalCache.get(globalKey);
    if (cached && now - cached.timestamp < finalConfig.cacheMs!) {
      return cached.data;
    }

    // Verificar se já existe requisição pendente
    const existing = this.pendingRequests.get(globalKey);
    if (existing) {
      return existing.promise;
    }

    // Verificar throttling
    const lastRequestTime = this.lastRequestTimes.get(globalKey) || 0;
    const timeSinceLastRequest = now - lastRequestTime;
    if (timeSinceLastRequest < finalConfig.throttleMs!) {
      const waitTime = finalConfig.throttleMs! - timeSinceLastRequest;
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }

    // Verificar limite de requisições concorrentes
    const currentConcurrent = this.pendingRequests.size;
    if (currentConcurrent >= finalConfig.maxConcurrent!) {
      await Promise.race(Array.from(this.pendingRequests.values()).map(r => r.promise));
    }

    // Executar requisição
    const promise = this.executeRequest(type, globalKey, requestFn, finalConfig);

    this.pendingRequests.set(globalKey, {
      promise,
      timestamp: now,
      key: globalKey,
    });

    this.lastRequestTimes.set(globalKey, now);
    return promise;
  }

  /**
   * Executa requisição e gerencia cache
   */
  private async executeRequest<T>(
    type: string,
    key: string,
    requestFn: () => Promise<T>,
    config: RequestConfig
  ): Promise<T> {
    try {
      const startTime = Date.now();
      const result = await requestFn();
      const duration = Date.now() - startTime;

      // Registrar tempo de resposta
      this.recordRequestTime(type, key, duration);

      // Armazenar no cache global
      if (config.cacheMs! > 0) {
        this.globalCache.set(key, {
          data: result,
          timestamp: Date.now(),
        });
      }

      return result;
    } finally {
      this.pendingRequests.delete(key);
    }
  }

  /**
   * Obtém estatísticas de um tipo de cache
   */
  getStats(type: string): CacheStats | null {
    const cache = this.caches.get(type);
    const config = this.configs.get(type);
    const stats = this.stats.get(type);

    if (!cache || !config || !stats) return null;

    const entries = Array.from(cache.entries()).map(([key, entry]) => ({
      key,
      timestamp: entry.timestamp,
      expiresAt: entry.expiresAt,
    }));

    return {
      ...stats,
      size: cache.size,
      maxSize: config.maxSize,
      ttl: config.ttl,
      hitRate: stats.hits / (stats.hits + stats.misses) || 0,
      isActive: this.isCacheActive(type),
      totalRequests: this.requestCounts.get(type) || 0,
      avgResponseTime: this.getAverageResponseTime(type),
      memoryUsage: this.getMemoryUsage(type),
    };
  }

  /**
   * Obtém estatísticas consolidadas de todos os caches
   */
  getAllStats(): Record<string, CacheStats> {
    const allStats: Record<string, CacheStats> = {};

    for (const type of this.caches.keys()) {
      const stats = this.getStats(type);
      if (stats) {
        allStats[type] = stats;
      }
    }

    return allStats;
  }

  /**
   * Calcula uso de memória de um tipo de cache
   */
  private getMemoryUsage(type: string): number {
    const cache = this.caches.get(type);
    if (!cache) return 0;

    let totalSize = 0;
    for (const [key, entry] of cache.entries()) {
      totalSize += JSON.stringify({ key, entry }).length;
    }
    return totalSize;
  }

  /**
   * Configura intervalos de limpeza automática
   */
  private setupCleanupIntervals(): void {
    // Limpar caches expirados a cada minuto
    setInterval(() => {
      for (const type of this.caches.keys()) {
        this.cleanExpired(type);
      }
    }, 60000);

    // Limpar cache global a cada 5 minutos
    setInterval(() => {
      const now = Date.now();
      for (const [key, entry] of this.globalCache.entries()) {
        if (now - entry.timestamp > this.defaultRequestConfig.cacheMs!) {
          this.globalCache.delete(key);
        }
      }
    }, 300000);
  }

  /**
   * Força ativação de um tipo de cache
   */
  forceActivate(type: string): void {
    const config = this.configs.get(type);
    if (config) {
      config.autoActivate = false; // Desativa auto-ativação
    }
  }

  /**
   * Força desativação de um tipo de cache
   */
  forceDeactivate(type: string): void {
    this.clear(type);
    const config = this.configs.get(type);
    if (config) {
      config.autoActivate = false;
    }
  }
}

// Instância singleton do cache unificado
export const unifiedCache = new UnifiedCacheManager();

// Registrar tipos de cache padrão
unifiedCache.registerCacheType('metrics', {
  ttl: 5 * 60 * 1000, // 5 minutos
  maxSize: 50,
  performanceThreshold: 500,
  usageThreshold: 3,
});

unifiedCache.registerCacheType('systemStatus', {
  ttl: 2 * 60 * 1000, // 2 minutos
  maxSize: 10,
  performanceThreshold: 300,
  usageThreshold: 2,
});

unifiedCache.registerCacheType('technicianRanking', {
  ttl: 10 * 60 * 1000, // 10 minutos
  maxSize: 20,
  performanceThreshold: 800,
  usageThreshold: 2,
});

unifiedCache.registerCacheType('newTickets', {
  ttl: 1 * 60 * 1000, // 1 minuto
  maxSize: 30,
  performanceThreshold: 400,
  usageThreshold: 3,
});

unifiedCache.registerCacheType('tickets', {
  ttl: 3 * 60 * 1000, // 3 minutos
  maxSize: 200,
  performanceThreshold: 600,
  usageThreshold: 2,
});

unifiedCache.registerCacheType('filterTypes', {
  ttl: 10 * 60 * 1000, // 10 minutos
  maxSize: 10,
  performanceThreshold: 300,
  usageThreshold: 2,
});

unifiedCache.registerCacheType('search', {
  ttl: 2 * 60 * 1000, // 2 minutos
  maxSize: 50,
  performanceThreshold: 200,
  usageThreshold: 1,
});

export default unifiedCache;
