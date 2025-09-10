import { useState, useEffect, Suspense } from 'react';
import { Header } from './components/Header';
import { NotificationSystem } from './components/NotificationSystem';
import CacheNotification from './components/CacheNotification';
import { ModernDashboard } from './components/dashboard/ModernDashboard';
import { TicketDetailModal } from './components/TicketDetailModal';
import SkipLink from './components/SkipLink';

import { Ticket } from './types/ticket';
import { UnifiedLoading } from './components/UnifiedLoading';

// Componentes lazy centralizados
import { DashboardSkeleton } from './components/LazyComponents';

import { useDashboard } from './hooks/useDashboard';

import { useCacheNotifications } from './hooks/useCacheNotifications';

import { TicketStatus, Theme } from './types';

function App() {
  const {
    metrics,
    levelMetrics,
    systemStatus,
    technicianRanking,
    isLoading,
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

    updateFilters,
    updateFilterType,
    search,
    addNotification,
    removeNotification,
    changeTheme,
    updateDateRange,
  } = useDashboard();

  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [isTicketModalOpen, setIsTicketModalOpen] = useState(false);
  const [isLoadingTicketDetails, setIsLoadingTicketDetails] = useState(false);

  // Ticket modal handlers
  const handleTicketClick = async (ticket: Ticket) => {
    setIsLoadingTicketDetails(true);

    try {
      // Import the API function dynamically to avoid circular dependencies
      const { getTicketById } = await import('./services/api');

      // Fetch detailed ticket information
      const detailedTicket = await getTicketById(ticket.id.toString());

      // Merge the detailed data with the original ticket data
      const enrichedTicket = {
        ...ticket,
        ...detailedTicket,
        // Ensure we keep the original ID format
        id: ticket.id,
      };

      setSelectedTicket(enrichedTicket);
      setIsTicketModalOpen(true);
    } catch (error) {
      console.error('Erro ao buscar detalhes do ticket:', error);
      // Fallback to original ticket data if API fails
      setSelectedTicket(ticket);
      setIsTicketModalOpen(true);
    } finally {
      setIsLoadingTicketDetails(false);
    }
  };

  const handleCloseTicketModal = () => {
    setIsTicketModalOpen(false);
    setSelectedTicket(null);
  };

  // Cache notifications
  const { notifications: cacheNotifications, removeNotification: removeCacheNotification } =
    useCacheNotifications();

  // Execute cache migration on mount

  // Load data on mount
  useEffect(() => {
    loadData();
  }, [loadData]);

  // Apply theme to body element
  useEffect(() => {
    document.body.className = theme === 'dark' ? 'dark' : '';
  }, [theme]);

  // Handle filter by status
  const handleFilterByStatus = async (status: TicketStatus) => {
    updateFilters({ status: [status] });

    addNotification({
      id: Date.now().toString(),
      title: 'Filtro Aplicado',
      message: `Exibindo apenas chamados com status: ${getStatusLabel(status)}`,
      type: 'info',
      timestamp: new Date(),
      duration: 3000,
    });
  };

  // Get status label in Portuguese
  const getStatusLabel = (status: TicketStatus): string => {
    const labels = {
      new: 'Novos',
      progress: 'Em Progresso',
      pending: 'Pendentes',
      resolved: 'Resolvidos',
    };
    return labels[status] || status;
  };

  // Show loading state on initial load
  if (isLoading && !levelMetrics) {
    return (
      <UnifiedLoading isLoading={true} type='skeleton' text='Carregando dashboard...' fullScreen />
    );
  }

  // Show error state
  if (error && !levelMetrics) {
    return (
      <div className='min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50 flex items-center justify-center'>
        <UnifiedLoading
          isLoading={true}
          type='spinner'
          text={error}
          title='Erro ao Carregar Dashboard'
          fullScreen
        />
      </div>
    );
  }

  return (
    <div className={`h-screen overflow-hidden transition-all duration-300 ${theme}`}>
      {/* Skip Links for Accessibility */}
      <SkipLink href='#main-content'>Pular para o conteúdo principal</SkipLink>
      <SkipLink href='#dashboard-metrics'>Pular para métricas do dashboard</SkipLink>

      {/* Header */}
      <Header
        currentTime={new Date().toLocaleTimeString('pt-BR')}
        systemActive={true}
        searchQuery={searchQuery}
        searchResults={[]}
        dateRange={
          filters?.dateRange || { startDate: '', endDate: '', label: 'Selecionar período' }
        }
        filterType={filterType}
        availableFilterTypes={availableFilterTypes}
        onSearch={search}
        theme={theme as Theme}
        onThemeChange={(newTheme: Theme) => changeTheme(newTheme)}
        onNotification={(title, message, type) =>
          addNotification({
            id: Date.now().toString(),
            title,
            message,
            type,
            timestamp: new Date(),
            duration: 3000,
          })
        }
        onDateRangeChange={updateDateRange}
        onFilterTypeChange={updateFilterType}
      />

      {/* Dashboard Principal */}
      <main id='main-content' className='flex-1 overflow-hidden' tabIndex={-1}>
        {levelMetrics ? (
          (() => {
            const dashboardMetrics = {
              novos: metrics?.novos || 0,
              pendentes: metrics?.pendentes || 0,
              progresso: metrics?.progresso || 0,
              resolvidos: metrics?.resolvidos || 0,
              total:
                (metrics?.novos || 0) +
                (metrics?.pendentes || 0) +
                (metrics?.progresso || 0) +
                (metrics?.resolvidos || 0),
              niveis: metrics?.niveis || {
                n1: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
                n2: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
                n3: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
                n4: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
              },
            };
            // Debug logs removidos para produção
            // console.log(
            //   '🎯 App.tsx - Métricas sendo passadas para ModernDashboard:',
            //   dashboardMetrics
            // );
            // console.log('🔍 App.tsx - Objeto metrics completo:', metrics);
            // console.log('🔍 App.tsx - technicianRanking sendo passado:', technicianRanking);
            // console.log('🔍 App.tsx - technicianRanking length:', technicianRanking?.length);
            // console.log('🔍 App.tsx - technicianRanking tipo:', typeof technicianRanking);
            // console.log(
            //   '🔍 App.tsx - technicianRanking é array?',
            //   Array.isArray(technicianRanking)
            // );
            return (
              <ModernDashboard
                metrics={dashboardMetrics}
                levelMetrics={levelMetrics}
                systemStatus={systemStatus}
                technicianRanking={technicianRanking}
                onFilterByStatus={handleFilterByStatus}
                onTicketClick={handleTicketClick}
                onRefresh={loadData}
                isLoading={isLoading}
                filters={filters}
              />
            );
          })()
        ) : (
          // Fallback para quando não há dados
          <div className='h-full bg-gradient-to-br from-gray-50 via-white to-gray-100 flex items-center justify-center'>
            <div className='text-center py-12'>
              <div className='w-24 h-24 bg-gray-200 rounded-full mx-auto mb-4 flex items-center justify-center'>
                <svg
                  className='w-12 h-12 text-gray-400'
                  fill='none'
                  stroke='currentColor'
                  viewBox='0 0 24 24'
                >
                  <path
                    strokeLinecap='round'
                    strokeLinejoin='round'
                    strokeWidth={2}
                    d='M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z'
                  />
                </svg>
              </div>
              <h3 className='text-lg font-semibold text-gray-900 mb-2'>Nenhum dado disponível</h3>
              <p className='text-gray-600 mb-4'>Não foi possível carregar os dados do dashboard.</p>
              <button
                onClick={() => loadData()}
                className='px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors'
              >
                Tentar Novamente
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Loading overlay for refresh */}
      {isLoading && levelMetrics && (
        <div className='fixed top-20 right-6 z-50'>
          <div className='bg-white/90 backdrop-blur-sm rounded-xl shadow-lg p-4'>
            <UnifiedLoading isLoading={true} type='spinner' size='sm' text='Atualizando...' />
          </div>
        </div>
      )}

      {/* Pending overlay for transitions */}
      {isPending && (
        <div className='fixed top-20 left-1/2 transform -translate-x-1/2 z-50'>
          <div className='bg-blue-500/90 backdrop-blur-sm rounded-xl shadow-lg p-3 text-white'>
            <div className='flex items-center space-x-2'>
              <div className='animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent'></div>
              <span className='text-sm font-medium'>Processando...</span>
            </div>
          </div>
        </div>
      )}

      {/* Notification System */}
      <NotificationSystem notifications={notifications} onRemoveNotification={removeNotification} />

      {/* Cache Notifications */}
      {cacheNotifications.map((notification, index) => (
        <div
          key={notification.id}
          style={{ top: `${4 + index * 80}px` }}
          className='fixed right-4 z-50'
        >
          <CacheNotification
            message={notification.message}
            isVisible={true}
            onClose={() => removeCacheNotification(notification.id)}
          />
        </div>
      ))}

      {/* Ticket Detail Modal */}
      {selectedTicket && (
        <TicketDetailModal
          ticket={selectedTicket}
          isOpen={isTicketModalOpen}
          onClose={handleCloseTicketModal}
        />
      )}
    </div>
  );
}

export default App;
