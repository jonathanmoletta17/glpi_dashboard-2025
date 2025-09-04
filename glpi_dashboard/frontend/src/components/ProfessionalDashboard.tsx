import React, { useState, useEffect, useMemo, Suspense } from 'react';
import {
  MetricsData,
  TechnicianRanking,
  NewTicket,
  TicketStatus,
  SystemStatus,
  DateRange,
  LevelMetrics,
} from '../types';
import { Ticket } from '../types/ticket';
import { apiService } from '../services/api';
import { useThrottledCallback } from '../hooks/useDebounce';
import { useSmartRefresh } from '../hooks/useSmartRefresh';
// Performance monitoring removido temporariamente
import {
  BarChart3,
  Clock,
  Users,
  AlertTriangle,
  CheckCircle,
  Settings,
  Activity,
  RefreshCw,
  TrendingUp,
} from 'lucide-react';

// Interface atualizada para compatibilidade com ModernDashboard
interface ProfessionalDashboardProps {
  metrics: MetricsData;
  levelMetrics?: any;
  systemStatus?: SystemStatus | null;
  technicianRanking?: TechnicianRanking[];
  onFilterByStatus?: (status: TicketStatus) => void;
  onTicketClick?: (ticket: Ticket) => void;
  onRefresh?: () => void;
  isLoading?: boolean;
  className?: string;
  filters?: {
    start_date?: string;
    end_date?: string;
    level?: string;
    limit?: number;
    status?: TicketStatus[];
    dateRange?: DateRange;
  };
}

interface StatusCardProps {
  title: string;
  value: number;
  icon: React.ComponentType<any>;
  color: string;
  bgColor: string;
  status?: TicketStatus;
  onClick?: (status: TicketStatus) => void;
}

const StatusCard = React.memo<StatusCardProps>(
  ({ title, value, icon: Icon, color, bgColor, status, onClick }) => {
    const formattedValue = useMemo(() => value.toLocaleString(), [value]);
    const isClickable = status && onClick;

    const handleClick = () => {
      if (isClickable) {
        onClick(status);
      }
    };

    return (
      <div 
        className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 transition-all duration-200 ${
          isClickable ? 'hover:shadow-md hover:scale-105 cursor-pointer' : 'hover:shadow-md'
        }`}
        onClick={handleClick}
      >
        <div className='flex items-center justify-between'>
          <div>
            <p className='text-sm font-medium text-gray-600 mb-1'>{title}</p>
            <p className={`text-3xl font-bold ${color}`}>{formattedValue}</p>
            {isClickable && (
              <p className='text-xs text-gray-500 mt-1'>Clique para filtrar</p>
            )}
          </div>
          <div className={`p-3 rounded-lg ${bgColor}`}>
            <Icon className={`w-6 h-6 ${color}`} />
          </div>
        </div>
      </div>
    );
  }
);

interface LevelSectionProps {
  level: string;
  data: {
    novos: number;
    progresso: number;
    pendentes: number;
    resolvidos: number;
  };
}

const LevelSection = React.memo<LevelSectionProps>(({ level, data }) => {
  const total = useMemo(
    () => data.novos + data.progresso + data.pendentes + data.resolvidos,
    [data]
  );
  const resolvedPercentage = useMemo(
    () => (total > 0 ? ((data.resolvidos / total) * 100).toFixed(1) : '0'),
    [total, data.resolvidos]
  );

  return (
    <div className='bg-white rounded-xl shadow-sm border border-gray-200 p-6'>
      <div className='flex items-center justify-between mb-6'>
        <h3 className='text-lg font-semibold text-gray-900'>Nível {level}</h3>
        <div className='flex items-center space-x-2'>
          <span className='text-sm text-gray-500'>Taxa de Resolução:</span>
          <span className='text-sm font-semibold text-green-600'>{resolvedPercentage}%</span>
        </div>
      </div>

      <div className='grid grid-cols-2 lg:grid-cols-4 gap-4'>
        <div className='text-center p-4 metrics-card-new rounded-lg'>
          <div className='text-2xl font-bold mb-1'>{data.novos}</div>
          <div className='text-sm font-medium'>Novos</div>
        </div>
        <div className='text-center p-4 metrics-card-progress rounded-lg'>
          <div className='text-2xl font-bold mb-1'>{data.progresso}</div>
          <div className='text-sm font-medium'>Em Progresso</div>
        </div>
        <div className='text-center p-4 metrics-card-pending rounded-lg'>
          <div className='text-2xl font-bold mb-1'>{data.pendentes}</div>
          <div className='text-sm font-medium'>Pendentes</div>
        </div>
        <div className='text-center p-4 metrics-card-resolved rounded-lg'>
          <div className='text-2xl font-bold mb-1'>{data.resolvidos}</div>
          <div className='text-sm font-medium'>Resolvidos</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className='mt-4'>
        <div className='flex justify-between text-xs text-gray-500 mb-1'>
          <span>Progresso de Resolução</span>
          <span>{resolvedPercentage}%</span>
        </div>
        <div className='w-full bg-gray-200 rounded-full h-2'>
          <div
            className='bg-green-500 h-2 rounded-full transition-all duration-300'
            style={{ width: `${resolvedPercentage}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
});

export const ProfessionalDashboard: React.FC<ProfessionalDashboardProps> = ({
  metrics,
  levelMetrics,
  systemStatus,
  technicianRanking = [],
  onFilterByStatus,
  onTicketClick,
  onRefresh,
  isLoading = false,
  className,
  filters,
}) => {
  // Performance monitoring removido temporariamente
  const [newTickets, setNewTickets] = useState<NewTicket[]>([]);
  const [ticketsLoading, setTicketsLoading] = useState(false);
  const [currentTime, setCurrentTime] = useState('');

  // Update current time
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(
        now.toLocaleString('pt-BR', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        })
      );
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  // Throttled function to prevent excessive API calls
  const throttledFetchNewTickets = useThrottledCallback(async () => {
    setTicketsLoading(true);
    try {
      const tickets = await apiService.getNewTickets(8);
      setNewTickets(tickets);
      setTicketsLoading(false);
    } catch (error) {
      console.error('Erro ao buscar tickets novos:', error);
      setTicketsLoading(false);
    }
  }, 2000); // 2 second throttle

  // Fetch initial tickets
  useEffect(() => {
    throttledFetchNewTickets();
  }, []);

  // Smart refresh para tickets
  useSmartRefresh({
    refreshKey: 'professional-dashboard-tickets',
    refreshFn: throttledFetchNewTickets,
    intervalMs: 300000, // 5 minutos
    immediate: false,
    enabled: true,
  });

  if (isLoading && !metrics) {
    return (
      <div className='min-h-screen bg-gray-50 flex items-center justify-center'>
        <div className='text-center'>
          <div className='animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4'></div>
          <div className='text-gray-600 text-lg font-medium'>Carregando Dashboard...</div>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className='min-h-screen bg-gray-50 flex items-center justify-center'>
        <div className='text-center'>
          <AlertTriangle className='w-16 h-16 text-red-500 mx-auto mb-4' />
          <div className='text-gray-900 text-xl font-semibold mb-2'>Erro ao Carregar Dados</div>
          <div className='text-gray-600 mb-4'>Não foi possível conectar ao sistema GLPI</div>
          <button
            onClick={() => onRefresh?.()}
            className='bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors'
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    );
  }

  const totalActive = useMemo(
    () => metrics.novos + metrics.progresso + metrics.pendentes,
    [metrics.novos, metrics.progresso, metrics.pendentes]
  );
  const totalTickets = useMemo(
    () => totalActive + metrics.resolvidos,
    [totalActive, metrics.resolvidos]
  );
  const resolutionRate = useMemo(
    () => (totalTickets > 0 ? ((metrics.resolvidos / totalTickets) * 100).toFixed(1) : '0'),
    [metrics.resolvidos, totalTickets]
  );

  return (
    <div className='min-h-screen bg-gray-50'>
      {/* Header */}
      <header className='bg-white shadow-sm border-b border-gray-200'>
        <div className='max-w-7xl mx-auto px-6 py-4'>
          <div className='flex items-center justify-between'>
            <div>
              <h1 className='text-2xl font-bold text-gray-900'>Dashboard GLPI</h1>
              <p className='text-sm text-gray-600 mt-1'>Sistema de Monitoramento de Chamados</p>
            </div>
            <div className='flex items-center space-x-6'>
              <div className='text-right'>
                <div className='text-sm font-medium text-gray-900'>{currentTime}</div>
                <div className='text-xs text-gray-500'>Atualização Automática</div>
              </div>
              <button
                onClick={onRefresh}
                disabled={isLoading}
                className='bg-slate-700 text-white px-4 py-2 rounded-lg hover:bg-slate-800 disabled:opacity-50 transition-colors flex items-center space-x-2'
              >
                <Settings className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                <span>Atualizar</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className='max-w-7xl mx-auto px-6 py-8'>
        {/* Summary Cards */}
        <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-8 mb-8'>
          <StatusCard
            title='Novos'
            value={metrics.novos}
            icon={AlertTriangle}
            color=''
            bgColor='metrics-card-new'
            status='novo'
            onClick={onFilterByStatus}
          />
          <StatusCard
            title='Em Progresso'
            value={metrics.progresso}
            icon={Activity}
            color=''
            bgColor='metrics-card-progress'
            status='progresso'
            onClick={onFilterByStatus}
          />
          <StatusCard
            title='Pendentes'
            value={metrics.pendentes}
            icon={Clock}
            color=''
            bgColor='metrics-card-pending'
            status='pendente'
            onClick={onFilterByStatus}
          />
          <StatusCard
            title='Resolvidos'
            value={metrics.resolvidos}
            icon={CheckCircle}
            color=''
            bgColor='metrics-card-resolved'
            status='resolvido'
            onClick={onFilterByStatus}
          />
        </div>

        {/* Levels Grid */}
        <div className='grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8'>
          {levelMetrics && (
            <>
              <LevelSection level='N1' data={levelMetrics.n1 || metrics.niveis?.n1 || { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0 }} />
              <LevelSection level='N2' data={levelMetrics.n2 || metrics.niveis?.n2 || { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0 }} />
              <LevelSection level='N3' data={levelMetrics.n3 || metrics.niveis?.n3 || { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0 }} />
              <LevelSection level='N4' data={levelMetrics.n4 || metrics.niveis?.n4 || { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0 }} />
            </>
          )}
        </div>

        {/* Bottom Section */}
        <div className='grid grid-cols-1 lg:grid-cols-3 gap-6'>
          {/* Technician Ranking */}
          <div className='lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6'>
            <h3 className='text-lg font-semibold text-gray-900 mb-6'>Ranking de Técnicos</h3>
            <div className='space-y-4 max-h-96 overflow-y-auto'>
              {technicianRanking.map((tech, index) => {
                const rankBadgeColor = useMemo(() => {
                  switch (index) {
                    case 0:
                      return 'bg-slate-600';
                    case 1:
                      return 'bg-slate-500';
                    case 2:
                      return 'bg-slate-700';
                    default:
                      return 'bg-slate-800';
                  }
                }, [index]);

                return (
                  <div
                    key={tech.id}
                    className='flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors'
                  >
                    <div className='flex items-center space-x-4'>
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold text-white ${rankBadgeColor}`}
                      >
                        {index + 1}
                      </div>
                      <div>
                        <div className='font-medium text-gray-900'>{tech.nome || tech.name}</div>
                        <div className='text-sm text-gray-500'>Técnico de Suporte</div>
                      </div>
                    </div>
                    <div className='text-right'>
                      <div className='text-lg font-semibold text-gray-900'>
                        {tech.total_tickets || 0}
                      </div>
                      <div className='text-sm text-gray-500'>chamados</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Recent Tickets */}
          <div className='bg-white rounded-xl shadow-sm border border-gray-200 p-6'>
            <h3 className='text-lg font-semibold text-gray-900 mb-6'>Chamados Recentes</h3>
            {ticketsLoading ? (
              <div className='text-center py-8'>
                <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-slate-600 mx-auto mb-2'></div>
                <div className='text-sm text-gray-500'>Carregando...</div>
              </div>
            ) : (
              <div className='space-y-3 max-h-96 overflow-y-auto'>
                {newTickets.length > 0 ? (
                  newTickets.map(ticket => {
                    const formattedDate = useMemo(
                      () => new Date(ticket.date).toLocaleDateString('pt-BR'),
                      [ticket.date]
                    );

                    return (
                      <div
                        key={ticket.id}
                        className='p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer'
                        onClick={() => onTicketClick && onTicketClick({
                          id: ticket.id.toString(),
                          title: ticket.title,
                          description: ticket.description || '',
                          status: 'novo',
                          priority: ticket.priority.toLowerCase() as any,
                          requester: {
                            id: '1',
                            name: ticket.requester,
                            email: '',
                          },
                          technician: undefined,
                          createdAt: ticket.date,
                          updatedAt: ticket.date,
                          category: 'Geral',
                          urgency: 2,
                          impact: 2,
                          tags: [],
                          attachments: [],
                          comments: [],
                          timeTracking: {
                            totalTime: 0,
                            entries: [],
                          },
                        })}
                      >
                        <div className='flex justify-between items-start mb-2'>
                          <div className='text-sm font-medium text-gray-900 truncate flex-1 mr-2'>
                            #{ticket.id}
                          </div>
                          <span className='inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'>
                            {ticket.priority}
                          </span>
                        </div>
                        <div className='text-sm text-gray-600 mb-2 line-clamp-2'>
                          {ticket.title}
                        </div>
                        <div className='flex items-center justify-between text-xs text-gray-500'>
                          <span>{ticket.requester}</span>
                          <span>{formattedDate}</span>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className='text-center py-8 text-gray-500'>
                    <Clock className='w-8 h-8 mx-auto mb-2 text-gray-400' />
                    <div className='text-sm'>Nenhum chamado recente</div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className='bg-white border-t border-gray-200 mt-8'>
        <div className='max-w-7xl mx-auto px-6 py-4'>
          <div className='flex items-center justify-between text-sm text-gray-500'>
            <div>© 2024 Departamento de Tecnologia do Estado</div>
            <div className='flex items-center space-x-4'>
              <span>Última atualização: {currentTime}</span>
              <div className='flex items-center space-x-1'>
                <div className='w-2 h-2 bg-slate-500 rounded-full animate-pulse'></div>
                <span>Sistema Online</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default ProfessionalDashboard;
