import { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';
import type { DashboardMetrics, FilterParams } from '../types/api';
import { SystemStatus, NotificationData } from '../types';
import { useSmartRefresh } from './useSmartRefresh';

interface UseDashboardReturn {
  metrics: DashboardMetrics | null;
  levelMetrics: any;
  systemStatus: SystemStatus;
  technicianRanking: any[];
  isLoading: boolean;
  isPending: boolean;
  error: string | null;
  notifications: any[];
  searchQuery: string;
  filters: FilterParams;
  theme: string;
  dataIntegrityReport: any;
  filterType: string;
  availableFilterTypes: Array<{
    key: string;
    name: string;
    description: string;
    default?: boolean;
  }>;
  loadData: () => Promise<void>;
  forceRefresh: () => Promise<void>;
  updateFilters: (newFilters: FilterParams) => void;
  updateFilterType: (type: string) => void;
  search: (query: string) => void;
  addNotification: (notification: any) => void;
  removeNotification: (id: string) => void;
  changeTheme: (theme: string) => void;
  updateDateRange: (dateRange: any) => void;
}

const initialSystemStatus: SystemStatus = {
  api: 'offline',
  glpi: 'offline',
  glpi_message: 'Sistema não conectado',
  glpi_response_time: 0,
  last_update: new Date().toISOString(),
  version: '1.0.0',
  status: 'offline',
  sistema_ativo: false,
  ultima_atualizacao: new Date().toISOString(),
};

export const useDashboard = (initialFilters: FilterParams = {}): UseDashboardReturn => {
  const [data, setData] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterParams>(initialFilters);
  // Derivar dados dos resultados da API
  const levelMetrics = data?.niveis || null;

  const systemStatus = data?.systemStatus || initialSystemStatus;
  const technicianRanking = data?.technicianRanking || [];
  const [isPending] = useState<boolean>(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [theme, setTheme] = useState<string>('light');
  const [dataIntegrityReport] = useState<any>(null);
  const [filterType, setFilterType] = useState<string>(initialFilters.filterType || 'creation');
  const [availableFilterTypes, setAvailableFilterTypes] = useState<
    Array<{
      key: string;
      name: string;
      description: string;
      default?: boolean;
    }>
  >([]);

  const loadData = useCallback(
    async (newFilters?: FilterParams) => {
      const filtersToUse = newFilters || filters;

      setLoading(true);
      setError(null);

      try {
        // Limpar cache quando filtros mudam para garantir dados atualizados
        const currentDateRange = filters.dateRange;
        const newDateRange = newFilters?.dateRange;
        
        // Comparar filtros de data para detectar mudanças
        const dateRangeChanged = 
          (currentDateRange?.startDate !== newDateRange?.startDate) ||
          (currentDateRange?.endDate !== newDateRange?.endDate) ||
          (currentDateRange && !newDateRange) ||
          (!currentDateRange && newDateRange);
        
        if (dateRangeChanged) {
          apiService.clearAllCaches();
        }

        // Fazer chamadas paralelas para todos os endpoints

        const [metricsResult, systemStatusResult, technicianRankingResult] = await Promise.all([
          apiService.getMetrics(filtersToUse.dateRange ? {
            startDate: filtersToUse.dateRange.startDate,
            endDate: filtersToUse.dateRange.endDate,
            label: filtersToUse.dateRange.label || 'Período personalizado'
          } : undefined),
          (async () => {
            return await apiService.getSystemStatus();
          })(),
          (async () => {
            // Preparar filtros para o ranking de técnicos
            // NOTA: Ranking de técnicos não deve ser filtrado por data pois pode não ter dados históricos
            const rankingFilters: any = {
              limit: 50 // Aumentar limite para mostrar mais técnicos
            };

            // Aplicar filtros de data apenas se especificamente solicitado
            // Por padrão, buscar ranking sem filtros de data para garantir dados
            if (filtersToUse.dateRange?.startDate && filtersToUse.dateRange?.endDate) {
              // Só aplicar filtros de data se ambos startDate e endDate estiverem definidos
              // e se não for um período muito restritivo (menos de 30 dias)
              const startDate = new Date(filtersToUse.dateRange.startDate);
              const endDate = new Date(filtersToUse.dateRange.endDate);
              const daysDiff = (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24);

              if (daysDiff >= 30) { // Só aplicar filtros se período for >= 30 dias
                rankingFilters.start_date = filtersToUse.dateRange.startDate;
                rankingFilters.end_date = filtersToUse.dateRange.endDate;
              }
            }

            try {
              const result = await apiService.getTechnicianRanking(rankingFilters);

              // Se não retornou dados com filtros, tentar sem filtros
              if (result.length === 0 && (rankingFilters.start_date || rankingFilters.end_date)) {
                const fallbackResult = await apiService.getTechnicianRanking({ limit: 50 });
                return fallbackResult;
              }

              return result;
            } catch (error) {
              console.error('❌ useDashboard - Erro em getTechnicianRanking:', error);
              throw error;
            }
          })()
        ]);

        console.log('✅ useDashboard - Todas as chamadas paralelas concluídas');

        // Performance metrics tracking removed for now

        console.log('🔍 useDashboard - metricsResult recebido:', metricsResult);
        console.log('🔍 useDashboard - metricsResult.niveis:', metricsResult?.niveis);

        if (metricsResult) {
          // Debug logs para investigar o problema do ranking
          console.log('🔍 useDashboard - technicianRankingResult da API:', technicianRankingResult);
          console.log('🔍 useDashboard - technicianRankingResult length:', technicianRankingResult?.length);
          console.log('🔍 useDashboard - technicianRankingResult é array?', Array.isArray(technicianRankingResult));

          // Combinar todos os dados em um objeto DashboardMetrics
          const combinedData: DashboardMetrics = {
            ...metricsResult,
            systemStatus: systemStatusResult || initialSystemStatus,
            technicianRanking: technicianRankingResult || [],
          };

          console.log('🔍 useDashboard - combinedData.technicianRanking:', combinedData.technicianRanking);

          console.log('✅ useDashboard - Definindo dados combinados no estado:', combinedData);
          console.log('✅ useDashboard - combinedData.niveis:', combinedData.niveis);
          setData(combinedData);
          setError(null);
        } else {
          console.error('❌ useDashboard - metricsResult é null/undefined');
          setError('Falha ao carregar dados do dashboard');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
      } finally {
        setLoading(false);
      }
    },
    [filters]
  );

  // Load data on mount
  useEffect(() => {
    loadData();
  }, []);

  // Smart refresh - coordenado e inteligente
  useSmartRefresh({
    refreshKey: 'dashboard-main',
    refreshFn: loadData,
    intervalMs: 300000, // 5 minutos
    immediate: false,
    enabled: true,
  });

  // Função para buscar tipos de filtro disponíveis
  const fetchFilterTypes = useCallback(async () => {
    try {
      const { apiService } = await import('../services/api');
      const result = await apiService.getFilterTypes();
      if (result.success && result.data) {
        const types = Object.entries(result.data).map(([key, value]: [string, any]) => ({
          key,
          name: value.name,
          description: value.description,
          default: value.default,
        }));
        setAvailableFilterTypes(types);
      }
    } catch (error) {
      console.error('Erro ao buscar tipos de filtro:', error);
      // Fallback para tipos padrão
      setAvailableFilterTypes([
        {
          key: 'creation',
          name: 'Data de Criação',
          description: 'Filtra tickets criados no período',
          default: true,
        },
        {
          key: 'modification',
          name: 'Data de Modificação',
          description: 'Filtra tickets modificados no período',
          default: false,
        },
        {
          key: 'current_status',
          name: 'Status Atual',
          description: 'Mostra snapshot atual dos tickets',
          default: false,
        },
      ]);
    }
  }, []);

  // Buscar tipos de filtro na inicialização
  useEffect(() => {
    fetchFilterTypes();
  }, [fetchFilterTypes]);

  // Função para atualizar o tipo de filtro
  const updateFilterType = useCallback(
    (type: string) => {
      setFilterType(type);
      const updatedFilters = { ...filters, filterType: type };
      setFilters(updatedFilters);
      loadData(updatedFilters);
    },
    [filters, loadData]
  );

  const returnData: UseDashboardReturn = {
    metrics: data,
    levelMetrics,
    systemStatus,
    technicianRanking,
    isLoading: loading,
    isPending,
    error,
    notifications,
    searchQuery,
    filters,
    theme,
    dataIntegrityReport,
    filterType,
    availableFilterTypes,
    loadData,
    forceRefresh: loadData,
    updateFilters: (newFilters: FilterParams) => {
      const updatedFilters = { ...filters, ...newFilters };
      setFilters(updatedFilters);
      loadData(updatedFilters);
    },
    updateFilterType,
    search: (query: string) => setSearchQuery(query),
    addNotification: (notification: Partial<NotificationData>) => {
      const completeNotification: NotificationData = {
        id: notification.id || Date.now().toString(),
        title: notification.title || 'Notificação',
        message: notification.message || '',
        type: notification.type || 'info',
        timestamp: notification.timestamp || new Date(),
        duration: notification.duration,
      };
      setNotifications(prev => [...prev, completeNotification]);
    },
    removeNotification: (id: string) => setNotifications(prev => prev.filter(n => n.id !== id)),
    changeTheme: (newTheme: string) => setTheme(newTheme),
    updateDateRange: (dateRange: any) => {
      const updatedFilters = { ...filters, dateRange };
      setFilters(updatedFilters);
      // Forçar recarregamento imediato com os novos filtros
      loadData(updatedFilters);
    },
  };

  // Debug logs comentados para evitar erros de sintaxe
  // console.log('useDashboard - Retornando dados:', returnData);

  return returnData;
};
