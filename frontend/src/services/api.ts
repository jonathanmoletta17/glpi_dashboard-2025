import { httpClient, API_CONFIG } from './httpClient';
import { SystemStatus, DateRange } from '../types';
import type { ApiResult, DashboardMetrics, FilterParams, PerformanceMetrics } from '../types/api';
import { isApiError, isApiResponse, transformLegacyData } from '../types/api';
import { unifiedCache } from './unifiedCache';

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

    // Verificar cache primeiro
    const cachedData = unifiedCache.get('metrics', cacheParams);
    if (cachedData) {
      return cachedData;
    }

    // Usar coordenador de requisições para evitar chamadas duplicadas
    const cacheKey = `metrics-${JSON.stringify(cacheParams)}`;

    return unifiedCache.coordinateRequest(
      'metrics',
      cacheKey,
      async () => {
        const startTime = Date.now();
        let url = '/metrics';
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
        unifiedCache.recordRequestTime('metrics', cacheKey, responseTime);

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
          } else {
            // Estrutura normal

            // Processar dados dos níveis
            if (rawData.niveis) {
              // Calcular total para cada nível
              processedNiveis = {
                n1: {
                  ...rawData.niveis.n1,
                  total:
                    (rawData.niveis.n1.novos || 0) +
                    (rawData.niveis.n1.pendentes || 0) +
                    (rawData.niveis.n1.progresso || 0) +
                    (rawData.niveis.n1.resolvidos || 0),
                },
                n2: {
                  ...rawData.niveis.n2,
                  total:
                    (rawData.niveis.n2.novos || 0) +
                    (rawData.niveis.n2.pendentes || 0) +
                    (rawData.niveis.n2.progresso || 0) +
                    (rawData.niveis.n2.resolvidos || 0),
                },
                n3: {
                  ...rawData.niveis.n3,
                  total:
                    (rawData.niveis.n3.novos || 0) +
                    (rawData.niveis.n3.pendentes || 0) +
                    (rawData.niveis.n3.progresso || 0) +
                    (rawData.niveis.n3.resolvidos || 0),
                },
                n4: {
                  ...rawData.niveis.n4,
                  total:
                    (rawData.niveis.n4.novos || 0) +
                    (rawData.niveis.n4.pendentes || 0) +
                    (rawData.niveis.n4.progresso || 0) +
                    (rawData.niveis.n4.resolvidos || 0),
                },
              };
            } else if (rawData.levels) {
              // Caso os dados venham como 'levels' ao invés de 'niveis'
              processedNiveis = {
                n1: {
                  ...rawData.levels.n1,
                  total:
                    (rawData.levels.n1.novos || 0) +
                    (rawData.levels.n1.pendentes || 0) +
                    (rawData.levels.n1.progresso || 0) +
                    (rawData.levels.n1.resolvidos || 0),
                },
                n2: {
                  ...rawData.levels.n2,
                  total:
                    (rawData.levels.n2.novos || 0) +
                    (rawData.levels.n2.pendentes || 0) +
                    (rawData.levels.n2.progresso || 0) +
                    (rawData.levels.n2.resolvidos || 0),
                },
                n3: {
                  ...rawData.levels.n3,
                  total:
                    (rawData.levels.n3.novos || 0) +
                    (rawData.levels.n3.pendentes || 0) +
                    (rawData.levels.n3.progresso || 0) +
                    (rawData.levels.n3.resolvidos || 0),
                },
                n4: {
                  ...rawData.levels.n4,
                  total:
                    (rawData.levels.n4.novos || 0) +
                    (rawData.levels.n4.pendentes || 0) +
                    (rawData.levels.n4.progresso || 0) +
                    (rawData.levels.n4.resolvidos || 0),
                },
              };
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

          // Usar totais gerais diretamente da API (mais confiável)
          const data: DashboardMetrics = {
            // Totais gerais da API
            novos: rawData.novos || 0,
            pendentes: rawData.pendentes || 0,
            progresso: rawData.progresso || 0,
            resolvidos: rawData.resolvidos || 0,
            total: rawData.total || 0,
            // Estrutura por níveis
            niveis: processedNiveis,
          };

          // Armazenar no cache
          unifiedCache.set('metrics', cacheParams, data);
          return data;
        } else {
          console.error('API returned unsuccessful response:', response.data);
          // Return fallback data
          const fallbackData: import('../types/api').DashboardMetrics = {
            novos: 0,
            pendentes: 0,
            progresso: 0,
            resolvidos: 0,
            total: 0,
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

  // Get system status - usando endpoint /health/glpi disponível
  async getSystemStatus(): Promise<SystemStatus> {
    const cacheParams = { endpoint: 'systemStatus' };

    // Verificar cache primeiro
    const cachedData = unifiedCache.get('systemStatus', cacheParams);
    if (cachedData) {
      return cachedData;
    }

    const cacheKey = `systemStatus-${JSON.stringify(cacheParams)}`;

    return unifiedCache.coordinateRequest(
      'systemStatus',
      cacheKey,
      async () => {
        try {
          const startTime = Date.now();

          // Usar endpoint /health/glpi que existe no backend
          const response = await api.get<ApiResponse<any>>('/health/glpi');

          // Monitora performance
          const responseTime = Date.now() - startTime;
          unifiedCache.recordRequestTime('systemStatus', cacheKey, responseTime);

          if (response.data.success) {
            // Mapear resposta do health para formato SystemStatus
            const healthData = response.data.data || {};
            const data: SystemStatus = {
              api: 'online',
              glpi: healthData.glpi_status || 'online',
              glpi_message: healthData.message || 'Sistema operacional',
              glpi_response_time: responseTime,
              last_update: new Date().toISOString(),
              version: healthData.version || '1.0.0',
              status: 'online',
              sistema_ativo: true,
              ultima_atualizacao: new Date().toISOString(),
            };
            
            // Armazenar no cache
            unifiedCache.set('systemStatus', cacheParams, data);
            return data;
          } else {
            throw new Error('Health check failed');
          }
        } catch (error) {
          console.warn('System status check failed, using fallback data:', error);
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

  // Health check - usando endpoint /health disponível
  async healthCheck(): Promise<boolean> {
    try {
      await api.get('/health');
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
    const cachedData = unifiedCache.get('technicianRanking', cacheParams);
    if (cachedData) {
      // console.log('📦 Retornando dados do cache para ranking de técnicos');
      return cachedData;
    }

    try {
      let url = '/technicians/ranking';

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

      // console.log('🔍 Buscando ranking de técnicos:', url);

      // Usar timeout maior para ranking (5 minutos para casos complexos)
      const timeoutConfig = { timeout: 300000 }; // 5 minutos para ranking

      console.log(`⏱️ Usando timeout de 300 segundos para ranking de técnicos`);
      const response = await api.get<ApiResponse<any[]>>(url, {
        timeout: 300000, // 5 minutos para ranking
      });

      // Monitora performance
      const responseTime = Date.now() - startTime;
      const cacheKey = JSON.stringify(cacheParams);
      unifiedCache.recordRequestTime('technicianRanking', cacheKey, responseTime);

      // Debug logs para investigar o problema do ranking
      // console.log('🔍 getTechnicianRanking - response completo:', response);
      // console.log('🔍 getTechnicianRanking - response.data:', response.data);
      // console.log('🔍 getTechnicianRanking - response.data.success:', response.data.success);
      // console.log('🔍 getTechnicianRanking - response.data.data:', response.data.data);
      console.log(
        '🔍 getTechnicianRanking - response.data.data length:',
        response.data.data?.length
      );

      if (response.data.success && response.data.data) {
        const data = response.data.data;
        // Armazenar no cache
        unifiedCache.set('technicianRanking', cacheParams, data);
        // console.log('✅ Ranking de técnicos obtido com sucesso:', data.length, 'técnicos');
        // console.log('🔍 getTechnicianRanking - primeiro técnico dos dados:', data[0]);
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
    const cacheParams = { endpoint: 'tickets/recent', limit: limit.toString() };

    // Verificar cache primeiro
    const cachedData = unifiedCache.get('newTickets', cacheParams);
    if (cachedData) {
      // console.log('📦 Retornando dados do cache para novos tickets');
      return cachedData;
    }

    try {
      const response = await api.get<ApiResponse<any[]>>(`/tickets/recent?limit=${limit}`);

      // Monitora performance
      const responseTime = Date.now() - startTime;
      const cacheKey = JSON.stringify(cacheParams);
      unifiedCache.recordRequestTime('newTickets', cacheKey, responseTime);

      if (response.data.success && response.data.data) {
        const data = response.data.data;
        // Armazenar no cache
        unifiedCache.set('newTickets', cacheParams, data);
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
    const cachedData = unifiedCache.get('search', cacheParams);
    if (cachedData) {
      // console.log('📦 Retornando dados do cache para busca');
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
      const cacheKey = `search-${JSON.stringify(cacheParams)}`;
      unifiedCache.recordRequestTime('search', cacheKey, responseTime);

      // Armazenar no cache
      unifiedCache.set('search', cacheParams, data);
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
      const response = await api.get<ApiResponse<any>>(`/tickets/${ticketId}`);

      if (response.data.success && response.data.data) {
        const data = response.data.data;
        // console.log('✅ Detalhes do ticket obtidos com sucesso:', ticketId);
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

  // Get filter types - REMOVIDO: endpoint não existe no backend
  // Esta função foi desabilitada pois o endpoint /filter-types foi removido
  async getFilterTypes(): Promise<ApiResponse<any>> {
    console.warn('getFilterTypes: Endpoint /filter-types foi removido do backend');
    
    // Retornar dados mock ou vazios para manter compatibilidade
    return {
      success: true,
      data: [],
      message: 'Filter types endpoint não disponível',
      timestamp: new Date().toISOString()
    };
  },

  // Clear all caches
  clearAllCaches(): void {
    unifiedCache.clearAll();
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
      // console.log('📅 Processando dateRange:', filters.dateRange);
      // console.log('📅 Start date:', filters.dateRange.startDate);
      // console.log('📅 End date:', filters.dateRange.endDate);
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

    url = queryParams.toString() ? `/metrics?${queryParams.toString()}` : `/metrics`;

    // console.log('🔍 Filtros originais:', filters);
    // console.log('🔍 Query params construídos:', queryParams.toString());
    // console.log('🔍 Fazendo requisição para:', url);
    console.log('🌐 URL final da requisição:', url);

    const startTime = performance.now();

    const response = await httpClient.get(url, {
      timeout: 60000, // 60 segundos
    });

    const endTime = performance.now();
    const responseTime = endTime - startTime;

    const result: ApiResult<DashboardMetrics> = response.data;
    // Debug: console.log('Resposta da API recebida:', result);

    // Log de performance
    const perfMetrics: PerformanceMetrics = {
      responseTime,
      cacheHit: false,
      timestamp: new Date(),
      endpoint: '/metrics',
    };
    // Debug: console.log('Métricas de performance:', perfMetrics);

    // Verificar se a resposta é um erro
    if (isApiError(result)) {
      console.error('API retornou erro:', result.error);
      return null;
    }

    // Verificar se é uma resposta de sucesso
    if (isApiResponse(result)) {
      // console.log('🔍 API - result.data antes da transformação:', result.data);
      // console.log('🔍 API - result.data.niveis:', result.data?.niveis);

      // Processar dados para garantir estrutura consistente
      const processedData = transformLegacyData(result.data);
      // console.log('🔍 API - Dados processados após transformação:', processedData);
      // console.log('🔍 API - processedData.niveis:', processedData?.niveis);

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
