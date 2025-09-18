import { http, HttpResponse } from 'msw';
import type { DashboardMetrics, SystemStatus, TechnicianRanking, ApiResponse } from '../../types/api';

// Mock data
const mockMetrics: DashboardMetrics = {
  novos: 25,
  pendentes: 45,
  progresso: 30,
  resolvidos: 120,
  total: 220,
  niveis: {
    n1: {
      novos: 10,
      pendentes: 15,
      progresso: 8,
      resolvidos: 45,
      total: 78,
    },
    n2: {
      novos: 8,
      pendentes: 12,
      progresso: 10,
      resolvidos: 35,
      total: 65,
    },
    n3: {
      novos: 5,
      pendentes: 10,
      progresso: 8,
      resolvidos: 25,
      total: 48,
    },
    n4: {
      novos: 2,
      pendentes: 8,
      progresso: 4,
      resolvidos: 15,
      total: 29,
    },
  },
  timestamp: new Date().toISOString(),
  tempo_execucao: 0.5,
};

const mockSystemStatus: SystemStatus = {
  api: 'online',
  glpi: 'online',
  glpi_message: 'Sistema funcionando normalmente',
  glpi_response_time: 150,
  last_update: new Date().toISOString(),
  version: '1.0.0',
  status: 'online',
  sistema_ativo: true,
  ultima_atualizacao: new Date().toISOString(),
};

const mockTechnicianRanking: TechnicianRanking[] = [
  {
    id: '1',
    name: 'João Silva',
    level: 'N2',
    rank: 1,
    total: 45,
    score: 95,
    ticketsResolved: 40,
    ticketsInProgress: 5,
    averageResolutionTime: 2.5,
  },
  {
    id: '2',
    name: 'Maria Santos',
    level: 'N3',
    rank: 2,
    total: 38,
    score: 88,
    ticketsResolved: 35,
    ticketsInProgress: 3,
    averageResolutionTime: 3.2,
  },
  {
    id: '3',
    name: 'Pedro Costa',
    level: 'N2',
    rank: 3,
    total: 32,
    score: 82,
    ticketsResolved: 28,
    ticketsInProgress: 4,
    averageResolutionTime: 2.8,
  },
];

export const handlers = [
  // Get metrics
  http.get('/api/metrics', ({ request }) => {
    const url = new URL(request.url);
    const startDate = url.searchParams.get('start_date');
    const endDate = url.searchParams.get('end_date');

    // Simulate different data based on date range
    let responseData = { ...mockMetrics };
    if (startDate && endDate) {
      // Simulate filtered data
      responseData = {
        ...mockMetrics,
        total: mockMetrics.total! * 0.8,
        novos: Math.floor(mockMetrics.novos! * 0.8),
        pendentes: Math.floor(mockMetrics.pendentes! * 0.8),
        progresso: Math.floor(mockMetrics.progresso! * 0.8),
        resolvidos: Math.floor(mockMetrics.resolvidos! * 0.8),
        filtros_aplicados: { start_date: startDate, end_date: endDate },
      };
    }

    const response: ApiResponse<DashboardMetrics> = {
      success: true,
      data: responseData,
      timestamp: new Date().toISOString(),
    };

    return HttpResponse.json(response);
  }),

  // Get system health - mudado de /api/status para /api/health
  http.get('/api/health', () => {
    const response: ApiResponse<SystemStatus> = {
      success: true,
      data: mockSystemStatus,
      timestamp: new Date().toISOString(),
    };

    return HttpResponse.json(response);
  }),

  // Get technician ranking
  http.get('/api/technicians/ranking', ({ request }) => {
    const url = new URL(request.url);
    const level = url.searchParams.get('level');
    const limit = url.searchParams.get('limit');

    let filteredRanking = [...mockTechnicianRanking];

    if (level) {
      filteredRanking = filteredRanking.filter(tech => tech.level === level);
    }

    if (limit) {
      filteredRanking = filteredRanking.slice(0, parseInt(limit));
    }

    const response: ApiResponse<TechnicianRanking[]> = {
      success: true,
      data: filteredRanking,
      timestamp: new Date().toISOString(),
    };

    return HttpResponse.json(response);
  }),

  // Get tickets (generic endpoint)
  http.get('/api/tickets', ({ request }) => {
    const url = new URL(request.url);
    const status = url.searchParams.get('status');
    const level = url.searchParams.get('level');

    // Mock ticket data based on filters
    const mockTickets = {
      tickets: [],
      total: 50,
      page: 1,
      per_page: 20,
      filters_applied: {
        status,
        level,
      },
    };

    const response: ApiResponse<typeof mockTickets> = {
      success: true,
      data: mockTickets,
      timestamp: new Date().toISOString(),
    };

    return HttpResponse.json(response);
  }),

  // Error simulation for testing error handling
  http.get('/api/error-test', () => {
    return HttpResponse.json(
      {
        success: false,
        error: 'Simulated API error for testing',
        code: 'TEST_ERROR',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }),

  // Network error simulation
  http.get('/api/network-error-test', () => {
    return HttpResponse.error();
  }),
];
