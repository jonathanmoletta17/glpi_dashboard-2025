/**
 * Utilitário para transformação e normalização de dados entre backend e frontend.
 * 
 * Este módulo simplifica a conversão de dados legados e padroniza a estrutura
 * de dados entre as diferentes versões da API.
 */

import { DashboardMetrics, LevelMetrics } from '../types/api';

/**
 * Classe para transformação de dados da API
 */
export class DataTransformer {
  /**
   * Normaliza chaves de objeto convertendo snake_case para camelCase
   */
  static normalizeKeys(obj: any): any {
    if (obj === null || typeof obj !== 'object') {
      return obj;
    }

    if (Array.isArray(obj)) {
      return obj.map(item => this.normalizeKeys(item));
    }

    const normalized: any = {};
    for (const [key, value] of Object.entries(obj)) {
      const camelKey = this.snakeToCamel(key);
      normalized[camelKey] = this.normalizeKeys(value);
    }

    return normalized;
  }

  /**
   * Converte string de snake_case para camelCase
   */
  static snakeToCamel(str: string): string {
    return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
  }

  /**
   * Converte string de camelCase para snake_case
   */
  static camelToSnake(str: string): string {
    return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
  }

  /**
   * Transforma dados legados para a estrutura DashboardMetrics padronizada
   */
  static transformLegacyData(rawData: any): DashboardMetrics {
    // Se os dados já estão no formato correto, normaliza apenas as chaves
    if (rawData?.niveis || rawData?.levels) {
      return this.normalizeApiResponse(rawData);
    }

    // Fallback para dados diretos (estrutura antiga)
    const defaultMetrics: LevelMetrics = {
      novos: 0,
      pendentes: 0,
      progresso: 0,
      resolvidos: 0,
      total: 0
    };

    return {
      niveis: {
        n1: rawData?.n1 || defaultMetrics,
        n2: rawData?.n2 || defaultMetrics,
        n3: rawData?.n3 || defaultMetrics,
        n4: rawData?.n4 || defaultMetrics
      },
      tendencias: rawData?.tendencias || {
        novos: [],
        resolvidos: [],
        pendentes: []
      },
      sistema: rawData?.sistema || {
        ativo: true,
        ultimaAtualizacao: new Date().toISOString()
      }
    };
  }

  /**
   * Normaliza resposta da API convertendo snake_case para camelCase
   */
  static normalizeApiResponse(response: any): DashboardMetrics {
    if (!response) {
      throw new Error('Resposta da API está vazia');
    }

    // Normalizar chaves principais
    const normalized = this.normalizeKeys(response);

    // Garantir estrutura de níveis
    const niveis = normalized.niveis || normalized.levels || normalized.byLevel;
    if (!niveis) {
      throw new Error('Estrutura de níveis não encontrada na resposta');
    }

    // Normalizar cada nível
    const normalizedNiveis: any = {};
    for (const [level, metrics] of Object.entries(niveis)) {
      normalizedNiveis[level] = this.normalizeMetrics(metrics as any);
    }

    return {
      niveis: normalizedNiveis,
      tendencias: normalized.tendencias || {
        novos: [],
        resolvidos: [],
        pendentes: []
      },
      sistema: normalized.sistema || {
        ativo: true,
        ultimaAtualizacao: new Date().toISOString()
      }
    };
  }

  /**
   * Normaliza métricas de um nível específico
   */
  static normalizeMetrics(metrics: any): LevelMetrics {
    if (!metrics || typeof metrics !== 'object') {
      return {
        novos: 0,
        pendentes: 0,
        progresso: 0,
        resolvidos: 0,
        total: 0
      };
    }

    return {
      novos: metrics.novos || metrics.new || 0,
      pendentes: metrics.pendentes || metrics.pending || 0,
      progresso: metrics.progresso || metrics.progress || metrics.inProgress || 0,
      resolvidos: metrics.resolvidos || metrics.resolved || metrics.solved || 0,
      total: metrics.total || 0
    };
  }

  /**
   * Valida se os dados têm a estrutura esperada
   */
  static validateDataStructure(data: any): boolean {
    try {
      if (!data || typeof data !== 'object') {
        return false;
      }

      // Verificar se tem estrutura de níveis
      const niveis = data.niveis || data.levels || data.byLevel;
      if (!niveis || typeof niveis !== 'object') {
        return false;
      }

      // Verificar se pelo menos um nível existe
      const levels = ['n1', 'n2', 'n3', 'n4'];
      return levels.some(level => niveis[level]);
    } catch {
      return false;
    }
  }

  /**
   * Cria dados de fallback em caso de erro
   */
  static createFallbackData(): DashboardMetrics {
    const defaultMetrics: LevelMetrics = {
      novos: 0,
      pendentes: 0,
      progresso: 0,
      resolvidos: 0,
      total: 0
    };

    return {
      niveis: {
        n1: { ...defaultMetrics },
        n2: { ...defaultMetrics },
        n3: { ...defaultMetrics },
        n4: { ...defaultMetrics }
      },
      tendencias: {
        novos: [],
        resolvidos: [],
        pendentes: []
      },
      sistema: {
        ativo: false,
        ultimaAtualizacao: new Date().toISOString()
      }
    };
  }

  /**
   * Processa resposta da API com tratamento de erro robusto
   */
  static processApiResponse(response: any): DashboardMetrics {
    try {
      // Validar estrutura dos dados
      if (!this.validateDataStructure(response)) {
        console.warn('Estrutura de dados inválida, usando fallback');
        return this.createFallbackData();
      }

      // Tentar transformar dados legados
      return this.transformLegacyData(response);
    } catch (error) {
      console.error('Erro ao processar resposta da API:', error);
      return this.createFallbackData();
    }
  }
}

/**
 * Funções de conveniência para uso direto
 */
export const transformLegacyData = (data: any): DashboardMetrics => {
  return DataTransformer.transformLegacyData(data);
};

export const normalizeApiResponse = (response: any): DashboardMetrics => {
  return DataTransformer.normalizeApiResponse(response);
};

export const processApiResponse = (response: any): DashboardMetrics => {
  return DataTransformer.processApiResponse(response);
};

export const validateDataStructure = (data: any): boolean => {
  return DataTransformer.validateDataStructure(data);
};

export const createFallbackData = (): DashboardMetrics => {
  return DataTransformer.createFallbackData();
};