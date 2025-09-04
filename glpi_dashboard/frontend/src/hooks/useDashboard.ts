import { useState, useEffect, useCallback } from 'react';
import { fetchDashboardMetrics, apiService } from '../services/api';
import type { DashboardMetrics, FilterParams } from '../types/api';
import { SystemStatus, NotificationData } from '../types';
import { useSmartRefresh } from './useSmartRefresh';
// Removed unused imports

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

// Removed unused initialFilterState

// Removed unused initialMetrics

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

// Removed unused getDefaultDateRange

// Removed unused initialState

// Removed unused performConsistencyChecks function

export const useDashboard = (initialFilters: FilterParams = {}): UseDashboardReturn => {
  const [data, setData] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  // Removed unused state variables
  const [filters, setFilters] = useState<FilterParams>(initialFilters);
  // Derivar dados dos resultados da API
  const levelMetrics = data?.niveis || null;

  // Debug logs temporários
  console.log('🔍 useDashboard - data completo:', data);
  console.log('🔍 useDashboard - data.niveis:', data?.niveis);
  console.log('🔍 useDashboard - levelMetrics derivado:', levelMetrics);
  const systemStatus = data?.systemStatus || initialSystemStatus;
  const technicianRanking = data?.technicianRanking || [];

  // Debug logs para investigar o problema do ranking
  console.log('🔍 useDashboard - data?.technicianRanking:', data?.technicianRanking);
  console.log('🔍 useDashboard - technicianRanking final:', technicianRanking);
  console.log('🔍 useDashboard - technicianRanking length:', technicianRanking?.length);
  console.log('🔍 useDashboard - technicianRanking é array?', Array.isArray(technicianRanking));
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
        // Fazer chamadas paralelas para todos os endpoints
        console.log('🚀 useDashboard - Iniciando chamadas paralelas...');

        const [metricsResult, systemStatusResult, technicianRankingResult] = await Promise.all([
          fetchDashboardMetrics(filtersToUse),
          (async () => {
            console.log('🔄 useDashboard - Chamando getSystemStatus...');
            return await apiService.getSystemStatus();
          })(),
          (async () => {
            console.log('🔄 useDashboard - Iniciando getTechnicianRanking...');
            // Preparar filtros para o ranking de técnicos
            const rankingFilters: any = {};

            if (filtersToUse.dateRange?.startDate) {
              rankingFilters.start_date = filtersToUse.dateRange.startDate;
            }
            if (filtersToUse.dateRange?.endDate) {
              rankingFilters.end_date = filtersToUse.dateRange.endDate;
            }

            console.log('🔍 useDashboard - Filtros para ranking:', rankingFilters);

            try {
              const result = await apiService.getTechnicianRanking(
                Object.keys(rankingFilters).length > 0 ? rankingFilters : undefined
              );
              console.log('✅ useDashboard - getTechnicianRanking sucesso:', result);
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

  // Removed unused forceRefresh function

  // Load data on mount
  useEffect(() => {
    loadData();
  }, [loadData]);

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
