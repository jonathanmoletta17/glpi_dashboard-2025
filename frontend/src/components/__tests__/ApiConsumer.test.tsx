import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { server } from '../../test/mocks/server';
import { http, HttpResponse } from 'msw';

// Mock the API service
vi.mock('../../services/api', () => ({
  apiService: {
    getMetrics: vi.fn(),
    getSystemStatus: vi.fn(),
    getTechnicianRanking: vi.fn(),
  },
}));

// Simple test component that uses API
const TestApiConsumer = () => {
  const [data, setData] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/metrics');
      const result = await response.json();
      if (result.success) {
        setData(result.data);
      } else {
        setError(result.error || 'API Error');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Network Error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={fetchData} data-testid='fetch-button'>
        Fetch Data
      </button>
      {loading && <div data-testid='loading'>Loading...</div>}
      {error && <div data-testid='error'>{error}</div>}
      {data && (
        <div data-testid='data'>
          <div>Total: {data.total}</div>
          <div>Novos: {data.novos}</div>
          <div>Pendentes: {data.pendentes}</div>
        </div>
      )}
    </div>
  );
};

// Export the component for the test
const ApiConsumer = TestApiConsumer;

describe('ApiConsumer Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render initial state correctly', () => {
    render(<ApiConsumer />);

    expect(screen.getByTestId('fetch-button')).toBeInTheDocument();
    expect(screen.queryByTestId('loading')).not.toBeInTheDocument();
    expect(screen.queryByTestId('error')).not.toBeInTheDocument();
    expect(screen.queryByTestId('data')).not.toBeInTheDocument();
  });

  it('should show loading state when fetching data', async () => {
    // Mock delayed response
    server.use(
      http.get('/api/metrics', async () => {
        await new Promise(resolve => setTimeout(resolve, 100));
        return HttpResponse.json({
          success: true,
          data: { total: 100, novos: 25, pendentes: 30 },
        });
      })
    );

    render(<ApiConsumer />);

    const fetchButton = screen.getByTestId('fetch-button');
    fireEvent.click(fetchButton);

    // Should show loading
    expect(screen.getByTestId('loading')).toBeInTheDocument();
    expect(screen.queryByTestId('error')).not.toBeInTheDocument();
    expect(screen.queryByTestId('data')).not.toBeInTheDocument();

    // Wait for completion
    await waitFor(() => {
      expect(screen.queryByTestId('loading')).not.toBeInTheDocument();
    });

    // Should show data
    expect(screen.getByTestId('data')).toBeInTheDocument();
    expect(screen.getByText('Total: 100')).toBeInTheDocument();
    expect(screen.getByText('Novos: 25')).toBeInTheDocument();
    expect(screen.getByText('Pendentes: 30')).toBeInTheDocument();
  });

  it('should display data when API call succeeds', async () => {
    const mockData = {
      total: 150,
      novos: 35,
      pendentes: 45,
      progresso: 25,
      resolvidos: 45,
    };

    server.use(
      http.get('/api/metrics', () => {
        return HttpResponse.json({
          success: true,
          data: mockData,
        });
      })
    );

    render(<ApiConsumer />);

    const fetchButton = screen.getByTestId('fetch-button');
    fireEvent.click(fetchButton);

    await waitFor(() => {
      expect(screen.getByTestId('data')).toBeInTheDocument();
    });

    expect(screen.getByText('Total: 150')).toBeInTheDocument();
    expect(screen.getByText('Novos: 35')).toBeInTheDocument();
    expect(screen.getByText('Pendentes: 45')).toBeInTheDocument();
    expect(screen.queryByTestId('error')).not.toBeInTheDocument();
  });

  it('should display error when API call fails', async () => {
    const errorMessage = 'API request failed';

    server.use(
      http.get('/api/metrics', () => {
        return HttpResponse.json(
          {
            success: false,
            error: errorMessage,
          },
          { status: 500 }
        );
      })
    );

    render(<ApiConsumer />);

    const fetchButton = screen.getByTestId('fetch-button');
    fireEvent.click(fetchButton);

    await waitFor(() => {
      expect(screen.getByTestId('error')).toBeInTheDocument();
    });

    expect(screen.getByText(errorMessage)).toBeInTheDocument();
    expect(screen.queryByTestId('data')).not.toBeInTheDocument();
    expect(screen.queryByTestId('loading')).not.toBeInTheDocument();
  });

  it('should handle network errors', async () => {
    server.use(
      http.get('/api/metrics', () => {
        return HttpResponse.error();
      })
    );

    render(<ApiConsumer />);

    const fetchButton = screen.getByTestId('fetch-button');
    fireEvent.click(fetchButton);

    await waitFor(() => {
      expect(screen.getByTestId('error')).toBeInTheDocument();
    });

    expect(screen.getByText('Failed to fetch')).toBeInTheDocument();
    expect(screen.queryByTestId('data')).not.toBeInTheDocument();
  });

  it('should allow multiple API calls', async () => {
    let callCount = 0;

    server.use(
      http.get('/api/metrics', () => {
        callCount++;
        return HttpResponse.json({
          success: true,
          data: { total: callCount * 10, novos: callCount * 2, pendentes: callCount * 3 },
        });
      })
    );

    render(<ApiConsumer />);

    const fetchButton = screen.getByTestId('fetch-button');

    // First call
    fireEvent.click(fetchButton);
    await waitFor(() => {
      expect(screen.getByText('Total: 10')).toBeInTheDocument();
    });

    // Second call
    fireEvent.click(fetchButton);
    await waitFor(() => {
      expect(screen.getByText('Total: 20')).toBeInTheDocument();
    });

    expect(screen.getByText('Novos: 4')).toBeInTheDocument();
    expect(screen.getByText('Pendentes: 6')).toBeInTheDocument();
  });
});
