import type { LevelMetrics, SystemStatus } from './api';

export interface MetricsData {
  novos: number;
  pendentes: number;
  progresso: number;
  resolvidos: number;
  total: number;
  niveis: {
    n1: LevelMetrics;
    n2: LevelMetrics;
    n3: LevelMetrics;
    n4: LevelMetrics;
  };
}

export interface SearchResult {
  id: string;
  type: 'ticket' | 'technician' | 'system';
  title: string;
  description?: string;
  status?: TicketStatus;
}

export type TicketStatus = 'novo' | 'progresso' | 'pendente' | 'resolvido' | 'fechado';

export type Theme = 'light' | 'dark';

export interface FilterState {
  period: 'today' | 'week' | 'month';
  levels: string[];
  status: TicketStatus[];
  priority: ('high' | 'medium' | 'low')[];
  dateRange?: DateRange;
}

export interface DateRange {
  startDate: string;
  endDate: string;
  label: string;
  start?: Date;
  end?: Date;
}

export interface NotificationData {
  id: string;
  title: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  timestamp: Date;
  duration?: number;
}

export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

export interface TechnicianRanking {
  id: string;
  name: string;
  nome?: string; // Campo alternativo da API
  level: string;
  rank: number;
  total_tickets: number; // Total de tickets do técnico
  resolved_tickets: number; // Tickets resolvidos
  pending_tickets: number; // Tickets pendentes
  avg_resolution_time: number; // Tempo médio de resolução
  score?: number; // Campo opcional para compatibilidade
  ticketsResolved?: number; // Campo opcional para compatibilidade
  ticketsInProgress?: number; // Campo opcional para compatibilidade
  averageResolutionTime?: number; // Campo opcional para compatibilidade
}

export interface NewTicket {
  id: string;
  title: string;
  description: string;
  date: string;
  requester: string;
  priority: string;
  status: string;
  category: string;
}

export interface DashboardState {
  metrics: MetricsData | null;
  systemStatus: SystemStatus | null;
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  filters: FilterState;
  searchQuery: string;
  searchResults: SearchResult[];
  notifications: NotificationData[];
  theme: Theme;
  dateRange?: DateRange;

  technicianRanking: TechnicianRanking[];
  dataIntegrityReport: any | null; // Será tipado adequadamente quando importado
  monitoringAlerts: any[];
}

// Export all types
export * from './api';
export * from './contract';
export * from './ticket';
