import { renderHook, waitFor, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useApi } from '../useApi';
import { server } from '../../test/mocks/server';
import { http, HttpResponse } from 'msw';

// Mock API functions
const mockApiFunction = vi.fn();
const mockSuccessCallback = vi.fn();
const mockErrorCallback = vi.fn();

describe('useApi Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApiFunction.mockReset();
    mockSuccessCallback.mockReset();
    mockErrorCallback.mockReset();
  });

  it('should initialize with correct default state', () => {
    const { result } = renderHook(() => useApi(mockApiFunction));

    expect(result.current.data).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(typeof result.current.execute).toBe('function');
    expect(typeof result.current.reset).toBe('function');
  });

  it('should handle loading state during API call', async () => {
    const mockData = { test: 'data' };
    let resolvePromise: (value: any) => void;
    const delayedPromise = new Promise(resolve => {
      resolvePromise = resolve;
    });

    mockApiFunction.mockReturnValue(delayedPromise);

    const { result } = renderHook(() => useApi(mockApiFunction));

    act(() => {
      result.current.execute();
    });

    // Should be loading
    expect(result.current.loading).toBe(true);
    expect(result.current.error).toBeNull();
    expect(result.current.data).toBeNull();

    // Resolve the promise
    act(() => {
      resolvePromise!(mockData);
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData);
  });

  it('should handle successful API response', async () => {
    const mockData = {
      total: 100,
      novos: 10,
      pendentes: 20,
      progresso: 30,
      resolvidos: 40,
      niveis: {
        n1: { novos: 5, pendentes: 10, progresso: 15, resolvidos: 20, total: 50 },
        n2: { novos: 3, pendentes: 7, progresso: 10, resolvidos: 15, total: 35 },
        n3: { novos: 2, pendentes: 3, progresso: 5, resolvidos: 5, total: 15 },
        n4: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
      },
    };

    mockApiFunction.mockResolvedValue(mockData);

    const { result } = renderHook(() => useApi(mockApiFunction, {
      onSuccess: mockSuccessCallback
    }));

    act(() => {
      result.current.execute();
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData);
    expect(result.current.error).toBeNull();
    expect(mockSuccessCallback).toHaveBeenCalledWith(mockData);
  });

  it('should handle API error response', async () => {
    const errorMessage = 'API Error occurred';
    const error = new Error(errorMessage);

    mockApiFunction.mockRejectedValue(error);

    const { result } = renderHook(() => useApi(mockApiFunction, {
      onError: mockErrorCallback
    }));

    act(() => {
      result.current.execute();
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBeNull();
    expect(result.current.error).toBe(errorMessage);
    expect(mockErrorCallback).toHaveBeenCalledWith(errorMessage);
  });

  it('should handle network error', async () => {
    const networkError = new Error('Network Error');
    mockApiFunction.mockRejectedValue(networkError);

    const { result } = renderHook(() => useApi(mockApiFunction));

    act(() => {
      result.current.execute();
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBeNull();
    expect(result.current.error).toBe('Network Error');
  });

  it('should reset state when reset is called', async () => {
    const mockData = { test: 'data' };
    mockApiFunction.mockResolvedValue(mockData);

    const { result } = renderHook(() => useApi(mockApiFunction));

    // Execute API call first
    act(() => {
      result.current.execute();
    });

    await waitFor(() => {
      expect(result.current.data).toEqual(mockData);
    });

    // Reset state
    act(() => {
      result.current.reset();
    });

    expect(result.current.data).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should handle multiple concurrent requests correctly', async () => {
    let requestCount = 0;

    mockApiFunction.mockImplementation(async () => {
      requestCount++;
      await new Promise(resolve => setTimeout(resolve, 50));
      return { total: requestCount * 10 };
    });

    const { result } = renderHook(() => useApi(mockApiFunction));

    // Make multiple requests
    act(() => {
      result.current.execute();
      result.current.execute();
      result.current.execute();
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Should only process the last request
    expect(result.current.data).toBeDefined();
    expect(result.current.error).toBeNull();
  });

  it('should auto-execute when autoExecute is true', async () => {
    const mockData = { autoExecuted: true };
    mockApiFunction.mockResolvedValue(mockData);

    const { result } = renderHook(() => useApi(mockApiFunction, {
      autoExecute: true
    }));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData);
    expect(mockApiFunction).toHaveBeenCalledTimes(1);
  });
});
