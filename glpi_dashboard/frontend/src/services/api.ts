import { httpClient, apiUtils, API_CONFIG, updateAuthTokens } from './httpClient';
import { SystemStatus, DateRange } from '../types';
import type { ApiResult, DashboardMetrics, FilterParams, PerformanceMetrics } from '../types/api';
import { isApiError, isApiResponse, transformLegacyData } from '../types/api';
import { metricsCache, systemStatusCache, technicianRankingCache, newTicketsCache } from './cache';
import { requestCoordinator } from './requestCoordinator';
import { smartCacheManager } from './smartCache';


// Base URL for API (mantido para compatibilidade)
const API_BASE_URL = API_CONFIG.BASE_URL;

// Cliente HTTP (alias para compatibilidade)
const api = httpClient;

// Os interceptadores agora estão centralizados no httpClient.ts

// API Response wrapper interface
interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: string;
}

export const apiService = {
  // Get metrics data with optional date filter
  async getMetrics(dateRange?: DateRange): Promise<DashboardMetrics> {
    const cacheParams = {
      endpoint: 'metrics',
      dateRange: dateRange || null,
    };

    // Usar coordenador de requisições para evitar chamadas duplicadas
    const cacheKey = `metrics-${JSON.stringify(cacheParams)}`;
    const metricsCache = smartCacheManager.getCache('metrics');

    return requestCoordinator.coordinateRequest(
      cacheKey,
      async () => {
        const startTime = Date.now();
        let url = '/api/metrics';
        if (dateRange && dateRange.startDate && dateRange.endDate) {
          const params = new URLSearchParams({
            start_date: dateRange.startDate,
            end_date: dateRange.endDate,
          });
          url += `?${params.toString()}`;
        }

        const response = await api.get(url);

        // Monitora performance
        const responseTime = Date.now() - startTime;
        const cacheKey = JSON.stringify(cacheParams);
        metricsCache.recordRequestTime(cacheKey, responseTime);

        if (response.data && response.data.success && response.data.data) {
          const rawData = response.data.data;

          // Verificar se há filtros aplicados (estrutura diferente)
          let processedNiveis: import('../types/api').NiveisMetrics;

          if (rawData.general || rawData.by_level) {
            // Estrutura com filtros aplicados
            processedNiveis = {
              n1: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
              n2: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
              n3: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
              n4: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
            };

            // Processar dados da estrutura by_level
            if (rawData.by_level) {
              Object.entries(rawData.by_level).forEach(([level, data]: [string, any]) => {
                const levelKey = level.toLowerCase() as keyof typeof processedNiveis;
                if (processedNiveis[levelKey]) {
                  const novos = data['Novo'] || 0;
                  const progresso =
                    (data['Processando (atribuído)'] || 0) + (data['Processando (planejado)'] || 0);
                  const pendentes = data['Pendente'] || 0;
                  const resolvidos = (data['Solucionado'] || 0) + (data['Fechado'] || 0);
                  processedNiveis[levelKey] = {
                    novos,
                    progresso,
                    pendentes,
                    resolvidos,
                    total: novos + progresso + pendentes + resolvidos,
                  };
                }
              });
            }

            // Calcular totais gerais dos níveis específicos (excluindo geral)
            const levelValues = Object.entries(processedNiveis)
              .filter(([key]) => key !== 'geral')
              .map(([, value]) => value);

            const geralTotals = {
              novos: levelValues.reduce((sum, nivel) => sum + nivel.novos, 0),
              pendentes: levelValues.reduce((sum, nivel) => sum + nivel.pendentes, 0),
              progresso: levelValues.reduce((sum, nivel) => sum + nivel.progresso, 0),
              resolvidos: levelValues.reduce((sum, nivel) => sum + nivel.resolvidos, 0),
            };

            // Removido processedNiveis.geral: não existe nos dados do backend

            // processedNiveis já está definido
          } else {
            // Estrutura normal

            // Processar dados dos níveis
            if (rawData.niveis) {
              processedNiveis = rawData.niveis;
            } else if (rawData.levels) {
              // Caso os dados venham como 'levels' ao invés de 'niveis'
              processedNiveis = rawData.levels;
            } else {
              // Fallback com zeros
              processedNiveis = {
                n1: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
                n2: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
                n3: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
                n4: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
              };
            }
          }

          // Garantir que todos os campos necessários existam
          const data: DashboardMetrics = {
            niveis: processedNiveis,

          };

          // Armazenar no cache
          metricsCache.set(cacheParams, data);
          return data;
        } else {
          console.error('API returned unsuccessful response:', response.data);
          // Return fallback data
          const fallbackData: import('../types/api').DashboardMetrics = {
            niveis: {
              n1: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
              n2: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
              n3: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
              n4: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
            },

          };
          // Não cachear dados de fallback
          return fallbackData;
        }
      },
      {
        debounceMs: 500,
        throttleMs: 2000,
        cacheMs: 60000, // 1 minuto de cache para métricas
      }
    );
  },

  // Get system status
  async getSystemStatus(): Promise<SystemStatus> {
    const cacheParams = { endpoint: 'status' };
    const cacheKey = `system-status-${JSON.stringify(cacheParams)}`;
    const systemCache = smartCacheManager.getCache('systemStatus');

    return requestCoordinator.coordinateRequest(
      cacheKey,
      async () => {
        const startTime = Date.now();
        console.log('🔍 Buscando status do sistema');

        const response = await api.get<ApiResponse<SystemStatus>>('/api/status');

        // Monitora performance
        const responseTime = Date.now() - startTime;
        console.log(`⏱️ Status do sistema obtido em ${responseTime}ms`);
        const cacheKeyInternal = JSON.stringify(cacheParams);
        systemStatusCache.recordRequestTime(cacheKeyInternal, responseTime);

        if (response.data.success && response.data.data) {
          const data = response.data.data;
          // Armazenar no cache
          systemStatusCache.set(cacheParams, data);
          return data;
        } else {
          console.error('API returned unsuccessful response:', response.data);
          // Return fallback data (não cachear)
          return {
            api: 'offline',
            glpi: 'offline',
            glpi_message: 'Sistema indisponível',
            glpi_response_time: 0,
            last_update: new Date().toISOString(),
            version: 'unknown',
            status: 'offline',
            sistema_ativo: false,
            ultima_atualizacao: new Date().toISOString(),
          };
        }
      },
      {
        debounceMs: 300,
        throttleMs: 5000,
        cacheMs: 30000, // 30 segundos de cache para status
      }
    );
  },

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      await api.head('/api/status');
      return true;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  },

  // Get technician ranking with optional filters
  async getTechnicianRanking(filters?: {
    start_date?: string;
    end_date?: string;
    level?: string;
    limit?: number;
  }): Promise<any[]> {
    const startTime = Date.now();

    // Criar parâmetros para o cache incluindo filtros
    const cacheParams = {
      endpoint: 'technicians/ranking',
      start_date: filters?.start_date || 'none',
      end_date: filters?.end_date || 'none',
      level: filters?.level || 'none',
      limit: filters?.limit?.toString() || '10',
    };

    // Verificar cache primeiro
    const cachedData = technicianRankingCache.get(cacheParams);
    if (cachedData) {
      console.log('📦 Retornando dados do cache para ranking de técnicos');
      return cachedData;
    }

    try {
      let url = '/api/technicians/ranking';

      // Construir query parameters se filtros foram fornecidos
      if (filters && Object.keys(filters).length > 0) {
        const params = new URLSearchParams();

        if (filters.start_date) params.append('start_date', filters.start_date);
        if (filters.end_date) params.append('end_date', filters.end_date);
        if (filters.level) params.append('level', filters.level);
        if (filters.limit) params.append('limit', filters.limit.toString());

        if (params.toString()) {
          url += `?${params.toString()}`;
        }
      }

      console.log('🔍 Buscando ranking de técnicos:', url);

      // Usar timeout maior para ranking (sempre 3 minutos pois demora ~44s)
      const timeoutConfig = { timeout: 180000 }; // 3 minutos para ranking

      console.log(
        `⏱️ Usando timeout de 180 segundos para ranking de técnicos`
      );
      const response = await api.get<ApiResponse<any[]>>(url, {
        timeout: 180000, // 3 minutos para ranking
      });

      // Monitora performance
      const responseTime = Date.now() - startTime;
      const cacheKey = JSON.stringify(cacheParams);
      technicianRankingCache.recordRequestTime(cacheKey, responseTime);

      // Debug logs para investigar o problema do ranking
      console.log('🔍 getTechnicianRanking - response completo:', response);
      console.log('🔍 getTechnicianRanking - response.data:', response.data);
      console.log('🔍 getTechnicianRanking - response.data.success:', response.data.success);
      console.log('🔍 getTechnicianRanking - response.data.data:', response.data.data);
      console.log('🔍 getTechnicianRanking - response.data.data length:', response.data.data?.length);
      
      if (response.data.success && response.data.data) {
        const data = response.data.data;
        // Armazenar no cache
        technicianRankingCache.set(cacheParams, data);
        console.log('✅ Ranking de técnicos obtido com sucesso:', data.length, 'técnicos');
        console.log('🔍 getTechnicianRanking - primeiro técnico dos dados:', data[0]);
        return data;
      } else {
        console.error('API returned unsuccessful response:', response.data);
        return [];
      }
    } catch (error) {
      console.error('Error fetching technician ranking:', error);
      return [];
    }
  },

  // Get new tickets
  async getNewTickets(limit: number = 5): Promise<any[]> {
    const startTime = Date.now();
    const cacheParams = { endpoint: 'tickets/new', limit: limit.toString() };

    // Verificar cache primeiro
    const cachedData = newTicketsCache.get(cacheParams);
    if (cachedData) {
      console.log('📦 Retornando dados do cache para novos tickets');
      return cachedData;
    }

    try {
      const response = await api.get<ApiResponse<any[]>>(`/api/tickets/new?limit=${limit}`);

      // Monitora performance
      const responseTime = Date.now() - startTime;
      const cacheKey = JSON.stringify(cacheParams);
      newTicketsCache.recordRequestTime(cacheKey, responseTime);

      if (response.data.success && response.data.data) {
        const data = response.data.data;
        // Armazenar no cache
        newTicketsCache.set(cacheParams, data);
        return data;
      } else {
        console.error('API returned unsuccessful response:', response.data);
        // Return mock data as fallback (não cachear)
        return [
          {
            id: '12345',
            title: 'Problema com impressora',
            requester: 'João Silva',
            date: new Date().toISOString(),
            priority: 'Alta',
          },
          {
            id: '12346',
            title: 'Erro no sistema',
            requester: 'Maria Santos',
            date: new Date(Date.now() - 3600000).toISOString(),
            priority: 'Média',
          },
          {
            id: '12347',
            title: 'Solicitação de acesso',
            requester: 'Pedro Costa',
            date: new Date(Date.now() - 7200000).toISOString(),
            priority: 'Baixa',
          },
        ];
      }
    } catch (error) {
      console.error('Error fetching new tickets:', error);
      // Return mock data instead of throwing error (não cachear)
      return [
        {
          id: '12345',
          title: 'Problema com impressora',
          requester: 'João Silva',
          date: new Date().toISOString(),
          priority: 'Alta',
        },
        {
          id: '12346',
          title: 'Erro no sistema',
          requester: 'Maria Santos',
          date: new Date(Date.now() - 3600000).toISOString(),
          priority: 'Média',
        },
        {
          id: '12347',
          title: 'Solicitação de acesso',
          requester: 'Pedro Costa',
          date: new Date(Date.now() - 7200000).toISOString(),
          priority: 'Baixa',
        },
      ];
    }
  },

  // Search functionality (mock implementation)
  async search(query: string): Promise<any[]> {
    const startTime = Date.now();
    const cacheParams = { endpoint: 'search', query };

    // Verificar cache primeiro
    const cachedData = metricsCache.get(cacheParams);
    if (cachedData) {
      console.log('📦 Retornando dados do cache para busca');
      return cachedData;
    }

    try {
      // This would be a real API call in production
      // For now, return mock data based on query
      const mockResults = [
        {
          id: '1',
          type: 'ticket',
          title: `Chamado relacionado a: ${query}`,
          description: 'Descrição do chamado...',
          status: 'new',
        },
        {
          id: '2',
          type: 'technician',
          title: `Técnico: ${query}`,
          description: 'Informações do técnico...',
        },
      ];

      const data = mockResults.filter(
        result => result.title.toLowerCase().indexOf(query.toLowerCase()) !== -1
      );

      // Monitora performance
      const responseTime = Date.now() - startTime;
      const cacheKey = JSON.stringify(cacheParams);
      metricsCache.recordRequestTime(cacheKey, responseTime);

      // Armazenar no cache
      metricsCache.set(cacheParams, data);
      return data;
    } catch (error) {
      console.error('Error searching:', error);
      throw new Error('Falha na busca');
    }
  },

  // Get ticket details by ID
  async getTicketById(ticketId: string): Promise<any> {
    const startTime = Date.now();
    const cacheParams = { endpoint: 'tickets/detail', ticketId };

    try {
      const response = await api.get<ApiResponse<any>>(`/api/tickets/${ticketId}`);

      if (response.data.success && response.data.data) {
        const data = response.data.data;
        console.log('✅ Detalhes do ticket obtidos com sucesso:', ticketId);
        return data;
      } else {
        console.error('API returned unsuccessful response for ticket:', ticketId, response.data);
        // Return mock data as fallback
        return {
          id: ticketId,
          title: `Ticket #${ticketId}`,
          description: 'Descrição detalhada do ticket não disponível no momento.',
          status: 'novo',
          priority: 'normal',
          category: 'Suporte Técnico',
          requester: {
            id: '1',
            name: 'Usuário Exemplo',
            email: 'usuario@exemplo.com',
          },
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
      }
    } catch (error) {
      console.error('Error fetching ticket details:', error);
      // Return mock data instead of throwing error
      return {
        id: ticketId,
        title: `Ticket #${ticketId}`,
        description: 'Erro ao carregar detalhes do ticket. Tente novamente mais tarde.',
        status: 'novo',
        priority: 'normal',
        category: 'Suporte Técnico',
        requester: {
          id: '1',
          name: 'Usuário Exemplo',
          email: 'usuario@exemplo.com',
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
    }
  },

  // Get filter types
  async getFilterTypes(): Promise<ApiResponse<any>> {
    const startTime = Date.now();
    const cacheParams = { endpoint: 'filter-types' };
    const cacheKey = `filter-types-${JSON.stringify(cacheParams)}`;
    
    return requestCoordinator.coordinateRequest(
      cacheKey,
      async () => {
        const response = await api.get('/api/filter-types');
        const responseTime = Date.now() - startTime;
        
        console.log(`📋 Filter types fetched in ${responseTime}ms`);
        return response.data;
      }
    );
  },

  // Clear all caches
  clearAllCaches(): void {
    console.log('🧹 Limpando todos os caches...');
    metricsCache.clear();
    systemStatusCache.clear();
    technicianRankingCache.clear();
    newTicketsCache.clear();
    console.log('✅ Todos os caches foram limpos');
  },
};

export default api;

// Named exports for individual functions
export const getMetrics = async (dateRange?: DateRange) => {
  return apiService.getMetrics(dateRange);
};
export const getSystemStatus = async () => {
  return apiService.getSystemStatus();
};
export const getTechnicianRanking = async (filters?: {
  start_date?: string;
  end_date?: string;
  level?: string;
  limit?: number;
}) => {
  return apiService.getTechnicianRanking(filters);
};

export const getNewTickets = async (limit?: number) => {
  return apiService.getNewTickets(limit);
};

export const search = async (query: string) => {
  return apiService.search(query);
};

export const healthCheck = async () => {
  return apiService.healthCheck();
};

export const getTicketById = async (ticketId: string) => {
  return apiService.getTicketById(ticketId);
};

export const getFilterTypes = async () => {
  return apiService.getFilterTypes();
};

export const clearAllCaches = apiService.clearAllCaches;

// Export utilities from httpClient
export { updateAuthTokens, apiUtils, API_CONFIG } from './httpClient';

// Export the centralized HTTP client
export { httpClient } from './httpClient';

// Função para buscar métricas do dashboard com tipagem forte
export const fetchDashboardMetrics = async (
  filters: FilterParams = {}
): Promise<DashboardMetrics | null> => {
  let url = '';

  try {
    const queryParams = new URLSearchParams();

    // Mapear filtros para os nomes esperados pela API
    const filterMapping: Record<string, string> = {
      startDate: 'start_date',
      endDate: 'end_date',
      status: 'status',
      priority: 'priority',
      level: 'level',
      filterType: 'filter_type',
    };

    // Processar dateRange se presente
    if (filters.dateRange && filters.dateRange.startDate && filters.dateRange.endDate) {
      console.log('📅 Processando dateRange:', filters.dateRange);
      console.log('📅 Start date:', filters.dateRange.startDate);
      console.log('📅 End date:', filters.dateRange.endDate);
      queryParams.append('start_date', filters.dateRange.startDate);
      queryParams.append('end_date', filters.dateRange.endDate);
    } else {
      console.log('⚠️ dateRange não encontrado ou incompleto:', filters.dateRange);
      console.log('⚠️ Filtros completos recebidos:', JSON.stringify(filters, null, 2));
    }

    // Adicionar filtros como parâmetros de query com validação de tipos
    for (const key in filters) {
      if (Object.prototype.hasOwnProperty.call(filters, key)) {
        const value = filters[key];
        if (key === 'dateRange') continue; // Já processado acima
        if (value !== null && value !== undefined && value !== '') {
          const apiKey = filterMapping[key] || key;
          queryParams.append(apiKey, value.toString());
        }
      }
    }

    url = queryParams.toString()
      ? `/api/metrics?${queryParams.toString()}`
      : `/api/metrics`;

    console.log('🔍 Filtros originais:', filters);
    console.log('🔍 Query params construídos:', queryParams.toString());
    console.log('🔍 Fazendo requisição para:', url);
    console.log('🌐 URL final da requisição:', url);

    const startTime = performance.now();

    const response = await httpClient.get(url, {
      timeout: 60000, // 60 segundos
    });

    const endTime = performance.now();
    const responseTime = endTime - startTime;

    const result: ApiResult<DashboardMetrics> = response.data;
    console.log('Resposta da API recebida:', result);

    // Log de performance
    const perfMetrics: PerformanceMetrics = {
      responseTime,
      cacheHit: false,
      timestamp: new Date(),
      endpoint: '/api/metrics',
    };
    console.log('Métricas de performance:', perfMetrics);

    // Verificar se a resposta é um erro
    if (isApiError(result)) {
      console.error('API retornou erro:', result.error);
      return null;
    }

    // Verificar se é uma resposta de sucesso
    if (isApiResponse(result)) {
      console.log('🔍 API - result.data antes da transformação:', result.data);
      console.log('🔍 API - result.data.niveis:', result.data?.niveis);

      // Processar dados para garantir estrutura consistente
      const processedData = transformLegacyData(result.data);
      console.log('🔍 API - Dados processados após transformação:', processedData);
      console.log('🔍 API - processedData.niveis:', processedData?.niveis);

      return processedData;
    }

    console.error('Resposta da API em formato inesperado:', result);
    return null;
  } catch (error) {
    console.error('Erro ao buscar métricas:', error);
    console.error('Tipo do erro:', typeof error);
    console.error('Stack trace:', error instanceof Error ? error.stack : 'N/A');
    console.error('URL tentada:', url);
    return null;
  }
};
