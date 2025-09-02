import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { toHaveNoViolations } from 'jest-axe';

// Extend Vitest matchers
expect.extend(toHaveNoViolations);

// Mock das variáveis de ambiente para testes
Object.defineProperty(globalThis, 'import', {
  value: {
    meta: {
      env: {
        VITE_API_BASE_URL: 'http://localhost:5000/api',
        VITE_API_TIMEOUT: '10000',
        VITE_API_RETRY_ATTEMPTS: '3',
        VITE_API_RETRY_DELAY: '1000',
        VITE_LOG_LEVEL: 'info',
        VITE_SHOW_PERFORMANCE: 'true',
        VITE_SHOW_API_CALLS: 'true',
        VITE_SHOW_CACHE_HITS: 'true',
        VITE_API_TOKEN: 'test-api-token',
        VITE_APP_TOKEN: 'test-app-token',
        VITE_USER_TOKEN: 'test-user-token',
        MODE: 'test',
        DEV: false,
        PROD: false,
        SSR: false,
      },
    },
  },
  writable: true,
});

// Mock do console para evitar logs desnecessários durante os testes
global.console = {
  ...console,
  log: vi.fn(),
  debug: vi.fn(),
  info: vi.fn(),
  warn: vi.fn(),
  error: vi.fn(),
};

// Mock do localStorage com comportamento funcional
const createStorageMock = () => {
  let store: Record<string, string> = {};

  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
    get length() {
      return Object.keys(store).length;
    },
    key: vi.fn((index: number) => {
      const keys = Object.keys(store);
      return keys[index] || null;
    }),
  };
};

const localStorageMock = createStorageMock();
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock do sessionStorage
const sessionStorageMock = createStorageMock();
Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
});

// Mock do fetch para testes
global.fetch = vi.fn();

// Mock do axios para evitar problemas de serialização
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      patch: vi.fn(),
      head: vi.fn(),
      interceptors: {
        request: { use: vi.fn(), eject: vi.fn() },
        response: { use: vi.fn(), eject: vi.fn() },
      },
    })),
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    patch: vi.fn(),
    head: vi.fn(),
  },
  AxiosError: class AxiosError extends Error {
    constructor(message: string, code?: string, config?: any, request?: any, response?: any) {
      super(message);
      this.name = 'AxiosError';
      this.code = code;
      this.config = config;
      this.request = request;
      this.response = response;
    }
  },
}));

// Mock do performance.now para testes de performance
Object.defineProperty(window, 'performance', {
  value: {
    now: vi.fn(() => Date.now()),
    mark: vi.fn(),
    measure: vi.fn(),
    getEntriesByName: vi.fn(() => []),
    getEntriesByType: vi.fn(() => []),
  },
});

// Limpar todos os mocks antes de cada teste
beforeEach(() => {
  vi.clearAllMocks();
  localStorageMock.getItem.mockClear();
  localStorageMock.setItem.mockClear();
  localStorageMock.removeItem.mockClear();
  localStorageMock.clear.mockClear();
  sessionStorageMock.getItem.mockClear();
  sessionStorageMock.setItem.mockClear();
  sessionStorageMock.removeItem.mockClear();
  sessionStorageMock.clear.mockClear();
});
