import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import React from 'react';
import { server } from '../../test/mocks/server';
import { http, HttpResponse } from 'msw';
import { apiService } from '../../services/api';
import { useApi } from '../../hooks/useApi';

// Integration test component that combines multiple API calls
const DashboardIntegration = () => {
  const [metrics, setMetrics] = React.useState(null);
  const [status, setStatus] = React.useState(null);
  const [ranking, setRanking] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Simulate loading multiple API endpoints
      const [metricsResponse, statusResponse, rankingResponse] = await Promise.all([
        fetch('/api/metrics'),
        fetch('/api/status'),
        fetch('/api/technicians/ranking')
      ]);

      const metricsData = await metricsResponse.json();
      const statusData = await statusResponse.json();
      const rankingData = await rankingResponse.json();

      if (metricsData.success) setMetrics(metricsData.data);
      if (statusData.success) setStatus(statusData.data);
      if (rankingData.success) setRanking(rankingData.data);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div data-testid="dashboard">
      <button onClick={loadDashboardData} data-testid="load-dashboard">
        Load Dashboard
      </button>

      {loading && <div data-testid="dashboard-loading">Loading dashboard...</div>}
      {error && <div data-testid="dashboard-error">{error}</div>}

      {metrics && (
        <div data-testid="metrics-section">
          <h2>Metrics</h2>
          <div>Total: {metrics.total}</div>
          <div>Novos: {metrics.novos}</div>
          <div>Pendentes: {metrics.pendentes}</div>
        </div>
      )}

      {status && (
        <div data-testid="status-section">
          <h2>System Status</h2>
          <div>Status: {status.status}</div>
          <div>Uptime: {status.uptime}</div>
        </div>
      )}

      {ranking && (
        <div data-testid="ranking-section">
          <h2>Technician Ranking</h2>
          {ranking.map((tech, index) => (
            <div key={tech.id} data-testid={`technician-${index}`}>
              {tech.name}: {tech.resolved} tickets
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Component using the useApi hook for integration testing
const ApiHookIntegration = () => {
  const metricsApi = useApi(async () => {
    const response = await fetch('/api/metrics');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API Error');
    return data.data;
  });

  const statusApi = useApi(async () => {
    const response = await fetch('/api/status');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API Error');
    return data.data;
  });

  return (
    <div data-testid="hook-integration">
      <div>
        <button onClick={metricsApi.execute} data-testid="fetch-metrics">
          Fetch Metrics
        </button>
        <button onClick={statusApi.execute} data-testid="fetch-status">
          Fetch Status
        </button>
        <button
          onClick={() => {
            metricsApi.reset();
            statusApi.reset();
          }}
          data-testid="reset-all"
        >
          Reset All
        </button>
      </div>

      {(metricsApi.loading || statusApi.loading) && (
        <div data-testid="any-loading">Loading...</div>
      )}

      {metricsApi.error && (
        <div data-testid="metrics-error">Metrics Error: {metricsApi.error}</div>
      )}

      {statusApi.error && (
        <div data-testid="status-error">Status Error: {statusApi.error}</div>
      )}

      {metricsApi.data && (
        <div data-testid="metrics-data">
          Metrics loaded: {metricsApi.data.total} total
        </div>
      )}

      {statusApi.data && (
        <div data-testid="status-data">
          Status: {statusApi.data.status}
        </div>
      )}
    </div>
  );
};

describe('API Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Dashboard Integration', () => {
    it('should load all dashboard data successfully', async () => {
      // Mock all API endpoints
      server.use(
        http.get('/api/metrics', () => {
          return HttpResponse.json({
            success: true,
            data: { total: 100, novos: 25, pendentes: 30 },
          });
        }),
        http.get('/api/status', () => {
          return HttpResponse.json({
            success: true,
            data: { status: 'online', uptime: '99.9%' },
          });
        }),
        http.get('/api/technicians/ranking', () => {
          return HttpResponse.json({
            success: true,
            data: [
              { id: 1, name: 'João Silva', resolved: 45 },
              { id: 2, name: 'Maria Santos', resolved: 38 },
            ],
          });
        })
      );

      render(<DashboardIntegration />);

      const loadButton = screen.getByTestId('load-dashboard');
      fireEvent.click(loadButton);

      // Should show loading
      expect(screen.getByTestId('dashboard-loading')).toBeInTheDocument();

      // Wait for all data to load
      await waitFor(() => {
        expect(screen.queryByTestId('dashboard-loading')).not.toBeInTheDocument();
      });

      // Check all sections are rendered
      expect(screen.getByTestId('metrics-section')).toBeInTheDocument();
      expect(screen.getByTestId('status-section')).toBeInTheDocument();
      expect(screen.getByTestId('ranking-section')).toBeInTheDocument();

      // Check specific data
      expect(screen.getByText('Total: 100')).toBeInTheDocument();
      expect(screen.getByText('Status: online')).toBeInTheDocument();
      expect(screen.getByText('João Silva: 45 tickets')).toBeInTheDocument();
      expect(screen.getByText('Maria Santos: 38 tickets')).toBeInTheDocument();
    });

    it('should handle partial API failures gracefully', async () => {
      // Mock mixed success/failure responses
      server.use(
        http.get('/api/metrics', () => {
          return HttpResponse.json({
            success: true,
            data: { total: 100, novos: 25, pendentes: 30 },
          });
        }),
        http.get('/api/status', () => {
          return HttpResponse.json(
            { success: false, error: 'Status service unavailable' },
            { status: 500 }
          );
        }),
        http.get('/api/technicians/ranking', () => {
          return HttpResponse.json({
            success: true,
            data: [{ id: 1, name: 'João Silva', resolved: 45 }],
          });
        })
      );

      render(<DashboardIntegration />);

      const loadButton = screen.getByTestId('load-dashboard');
      fireEvent.click(loadButton);

      await waitFor(() => {
        expect(screen.queryByTestId('dashboard-loading')).not.toBeInTheDocument();
      });

      // Should show successful sections
      expect(screen.getByTestId('metrics-section')).toBeInTheDocument();
      expect(screen.getByTestId('ranking-section')).toBeInTheDocument();

      // Should not show failed section
      expect(screen.queryByTestId('status-section')).not.toBeInTheDocument();

      // Should not show error (since some requests succeeded)
      expect(screen.queryByTestId('dashboard-error')).not.toBeInTheDocument();
    });

    it('should handle complete API failure', async () => {
      // Mock all endpoints to fail
      server.use(
        http.get('/api/metrics', () => HttpResponse.error()),
        http.get('/api/status', () => HttpResponse.error()),
        http.get('/api/technicians/ranking', () => HttpResponse.error())
      );

      render(<DashboardIntegration />);

      const loadButton = screen.getByTestId('load-dashboard');
      fireEvent.click(loadButton);

      await waitFor(() => {
        expect(screen.getByTestId('dashboard-error')).toBeInTheDocument();
      });

      expect(screen.queryByTestId('metrics-section')).not.toBeInTheDocument();
      expect(screen.queryByTestId('status-section')).not.toBeInTheDocument();
      expect(screen.queryByTestId('ranking-section')).not.toBeInTheDocument();
    });
  });

  describe('useApi Hook Integration', () => {
    it('should handle multiple independent API calls', async () => {
      server.use(
        http.get('/api/metrics', () => {
          return HttpResponse.json({
            success: true,
            data: { total: 150 },
          });
        }),
        http.get('/api/status', () => {
          return HttpResponse.json({
            success: true,
            data: { status: 'healthy' },
          });
        })
      );

      render(<ApiHookIntegration />);

      const metricsButton = screen.getByTestId('fetch-metrics');
      const statusButton = screen.getByTestId('fetch-status');

      // Fetch metrics
      fireEvent.click(metricsButton);
      await waitFor(() => {
        expect(screen.getByTestId('metrics-data')).toBeInTheDocument();
      });
      expect(screen.getByText('Metrics loaded: 150 total')).toBeInTheDocument();

      // Fetch status
      fireEvent.click(statusButton);
      await waitFor(() => {
        expect(screen.getByTestId('status-data')).toBeInTheDocument();
      });
      expect(screen.getByText('Status: healthy')).toBeInTheDocument();
    });

    it('should handle independent error states', async () => {
      server.use(
        http.get('/api/metrics', () => {
          return HttpResponse.json(
            { success: false, error: 'Metrics unavailable' },
            { status: 500 }
          );
        }),
        http.get('/api/status', () => {
          return HttpResponse.json({
            success: true,
            data: { status: 'healthy' },
          });
        })
      );

      render(<ApiHookIntegration />);

      const metricsButton = screen.getByTestId('fetch-metrics');
      const statusButton = screen.getByTestId('fetch-status');

      // Fetch metrics (should fail)
      fireEvent.click(metricsButton);
      await waitFor(() => {
        expect(screen.getByTestId('metrics-error')).toBeInTheDocument();
      });
      expect(screen.getByText('Metrics Error: Metrics unavailable')).toBeInTheDocument();

      // Fetch status (should succeed)
      fireEvent.click(statusButton);
      await waitFor(() => {
        expect(screen.getByTestId('status-data')).toBeInTheDocument();
      });
      expect(screen.getByText('Status: healthy')).toBeInTheDocument();

      // Metrics error should still be visible
      expect(screen.getByTestId('metrics-error')).toBeInTheDocument();
    });

    it('should reset all states correctly', async () => {
      server.use(
        http.get('/api/metrics', () => {
          return HttpResponse.json({
            success: true,
            data: { total: 150 },
          });
        })
      );

      render(<ApiHookIntegration />);

      const metricsButton = screen.getByTestId('fetch-metrics');
      const resetButton = screen.getByTestId('reset-all');

      // Fetch data first
      fireEvent.click(metricsButton);
      await waitFor(() => {
        expect(screen.getByTestId('metrics-data')).toBeInTheDocument();
      });

      // Reset all
      fireEvent.click(resetButton);

      // Data should be cleared
      expect(screen.queryByTestId('metrics-data')).not.toBeInTheDocument();
      expect(screen.queryByTestId('status-data')).not.toBeInTheDocument();
      expect(screen.queryByTestId('metrics-error')).not.toBeInTheDocument();
      expect(screen.queryByTestId('status-error')).not.toBeInTheDocument();
    });
  });
});
