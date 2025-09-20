/**
 * Serviço de Invalidação Inteligente de Cache
 *
 * Implementa invalidação baseada em eventos e padrões de uso
 * para manter os dados sempre atualizados sem comprometer a performance.
 */

import { unifiedCache } from './unifiedCache';

interface InvalidationRule {
  pattern: string;
  cacheTypes: string[];
  priority: 'high' | 'medium' | 'low';
  debounceMs?: number;
}

interface InvalidationEvent {
  type: string;
  data?: unknown;
  timestamp: number;
  source: string;
}

class CacheInvalidationService {
  private rules: Map<string, InvalidationRule> = new Map();
  private eventQueue: InvalidationEvent[] = [];
  private debounceTimers: Map<string, NodeJS.Timeout> = new Map();
  private isProcessing = false;

  constructor() {
    this.setupDefaultRules();
    this.startEventProcessor();
  }

  /**
   * Configura regras padrão de invalidação
   */
  private setupDefaultRules(): void {
    // Invalidação para mudanças em tickets
    this.addRule('ticket_update', {
      pattern: '.*tickets.*',
      cacheTypes: ['metrics', 'newTickets', 'technicianRanking'],
      priority: 'high',
      debounceMs: 1000,
    });

    // Invalidação para mudanças no sistema
    this.addRule('system_status_change', {
      pattern: '.*status.*',
      cacheTypes: ['systemStatus', 'metrics'],
      priority: 'high',
      debounceMs: 500,
    });

    // Invalidação para atualizações de métricas
    this.addRule('metrics_update', {
      pattern: '.*metrics.*',
      cacheTypes: ['metrics'],
      priority: 'medium',
      debounceMs: 2000,
    });

    // Invalidação para mudanças de ranking
    this.addRule('ranking_update', {
      pattern: '.*ranking.*',
      cacheTypes: ['technicianRanking', 'metrics'],
      priority: 'medium',
      debounceMs: 3000,
    });
  }

  /**
   * Adiciona uma nova regra de invalidação
   */
  addRule(eventType: string, rule: InvalidationRule): void {
    this.rules.set(eventType, rule);
  }

  /**
   * Remove uma regra de invalidação
   */
  removeRule(eventType: string): void {
    this.rules.delete(eventType);
  }

  /**
   * Dispara um evento de invalidação
   */
  triggerInvalidation(eventType: string, data?: unknown, source: string = 'manual'): void {
    const event: InvalidationEvent = {
      type: eventType,
      data,
      timestamp: Date.now(),
      source,
    };

    this.eventQueue.push(event);
    this.processEventQueue();
  }

  /**
   * Invalida cache baseado em padrão
   */
  invalidateByPattern(pattern: string, cacheTypes?: string[]): void {
    const types = cacheTypes || ['metrics', 'systemStatus', 'technicianRanking', 'newTickets'];

    types.forEach(type => {
      try {
        unifiedCache.invalidatePattern(type, pattern);
        console.log(`🔄 Cache invalidado: ${type} (padrão: ${pattern})`);
      } catch (error) {
        console.error(`❌ Erro ao invalidar cache ${type}:`, error);
      }
    });
  }

  /**
   * Invalida cache de métricas críticas
   */
  invalidateCriticalMetrics(): void {
    this.triggerInvalidation('metrics_update', null, 'critical_update');
  }

  /**
   * Invalida cache quando há mudanças em tickets
   */
  invalidateOnTicketChange(ticketId?: string): void {
    this.triggerInvalidation('ticket_update', { ticketId }, 'ticket_service');
  }

  /**
   * Invalida cache quando há mudanças no status do sistema
   */
  invalidateOnSystemStatusChange(): void {
    this.triggerInvalidation('system_status_change', null, 'system_monitor');
  }

  /**
   * Processa a fila de eventos de invalidação
   */
  private processEventQueue(): void {
    if (this.isProcessing || this.eventQueue.length === 0) {
      return;
    }

    this.isProcessing = true;

    // Processar eventos por prioridade
    const sortedEvents = this.eventQueue.sort((a, b) => {
      const ruleA = this.rules.get(a.type);
      const ruleB = this.rules.get(b.type);

      if (!ruleA || !ruleB) return 0;

      const priorityOrder = { high: 3, medium: 2, low: 1 };
      return priorityOrder[ruleB.priority] - priorityOrder[ruleA.priority];
    });

    sortedEvents.forEach(event => {
      this.processEvent(event);
    });

    this.eventQueue = [];
    this.isProcessing = false;
  }

  /**
   * Processa um evento individual
   */
  private processEvent(event: InvalidationEvent): void {
    const rule = this.rules.get(event.type);
    if (!rule) {
      console.warn(`⚠️ Regra não encontrada para evento: ${event.type}`);
      return;
    }

    const debounceKey = `${event.type}_${rule.pattern}`;

    // Aplicar debounce se configurado
    if (rule.debounceMs && rule.debounceMs > 0) {
      if (this.debounceTimers.has(debounceKey)) {
        clearTimeout(this.debounceTimers.get(debounceKey)!);
      }

      const timer = setTimeout(() => {
        this.executeInvalidation(rule, event);
        this.debounceTimers.delete(debounceKey);
      }, rule.debounceMs);

      this.debounceTimers.set(debounceKey, timer);
    } else {
      this.executeInvalidation(rule, event);
    }
  }

  /**
   * Executa a invalidação baseada na regra
   */
  private executeInvalidation(rule: InvalidationRule, event: InvalidationEvent): void {
    rule.cacheTypes.forEach(cacheType => {
      try {
        unifiedCache.invalidatePattern(cacheType, rule.pattern);
        console.log(`🔄 Cache invalidado por evento: ${cacheType} (${event.type})`);
      } catch (error) {
        console.error(`❌ Erro na invalidação por evento ${event.type}:`, error);
      }
    });
  }

  /**
   * Inicia o processador de eventos
   */
  private startEventProcessor(): void {
    // Processar eventos a cada 100ms
    setInterval(() => {
      if (this.eventQueue.length > 0) {
        this.processEventQueue();
      }
    }, 100);
  }

  /**
   * Obtém estatísticas do serviço
   */
  getStats(): {
    rulesCount: number;
    queueSize: number;
    activeTimers: number;
  } {
    return {
      rulesCount: this.rules.size,
      queueSize: this.eventQueue.length,
      activeTimers: this.debounceTimers.size,
    };
  }

  /**
   * Limpa todos os timers e eventos pendentes
   */
  cleanup(): void {
    this.debounceTimers.forEach(timer => clearTimeout(timer));
    this.debounceTimers.clear();
    this.eventQueue = [];
  }
}

// Instância singleton do serviço
export const cacheInvalidationService = new CacheInvalidationService();

// Exportar para uso em outros módulos
export default cacheInvalidationService;
