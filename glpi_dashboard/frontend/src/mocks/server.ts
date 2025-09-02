import { setupServer } from 'msw/node';
import { http, HttpResponse, HttpHandler } from 'msw';
import { handlers } from './handlers';

// Configura o servidor MSW para testes Node.js
export const server = setupServer(...handlers);

// Handlers adicionais para cenários específicos de teste
export const testHandlers: Record<string, HttpHandler> = {
  // Handler para simular erro de rede
  networkError: http.get('*', () => {
    return HttpResponse.error();
  }),

  // Handler para simular timeout
  timeout: http.get('*', async () => {
    await new Promise(() => {}); // Infinite delay
    return HttpResponse.json({ message: 'This should never resolve' });
  }),

  // Handler para simular erro 500
  serverError: http.get('*', () => {
    return HttpResponse.json(
      {
        error: 'Internal Server Error',
        message: 'Something went wrong on the server',
      },
      { status: 500 }
    );
  }),

  // Handler para simular erro 404
  notFound: http.get('*', () => {
    return HttpResponse.json(
      {
        error: 'Not Found',
        message: 'The requested resource was not found',
      },
      { status: 404 }
    );
  }),

  // Handler para simular erro 401
  unauthorized: http.get('*', () => {
    return HttpResponse.json(
      {
        error: 'Unauthorized',
        message: 'Authentication required',
      },
      { status: 401 }
    );
  }),

  // Handler para simular erro 403
  forbidden: http.get('*', () => {
    return HttpResponse.json(
      {
        error: 'Forbidden',
        message: 'Access denied',
      },
      { status: 403 }
    );
  }),

  // Handler para simular resposta lenta
  slowResponse: http.get('*', async () => {
    await new Promise(resolve => setTimeout(resolve, 3000));
    return HttpResponse.json({ message: 'Slow response' });
  }),

  // Handler para simular resposta vazia
  emptyResponse: http.get('*', () => {
    return HttpResponse.json({});
  }),

  // Handler para simular resposta com dados inválidos
  invalidData: http.get('*', () => {
    return new HttpResponse('Invalid JSON response', {
      status: 200,
      headers: { 'Content-Type': 'text/plain' },
    });
  }),
};

// Utilitários para testes
export const testUtils = {
  // Usa um handler específico para o próximo request
  useHandler: (handler: HttpHandler) => {
    server.use(handler);
  },

  // Reseta todos os handlers para o estado inicial
  resetHandlers: () => {
    server.resetHandlers();
  },

  // Adiciona handlers temporários
  addHandlers: (...handlers: HttpHandler[]) => {
    server.use(...handlers);
  },

  // Simula erro de rede para todas as requisições
  simulateNetworkError: () => {
    server.use(testHandlers.networkError);
  },

  // Simula timeout para todas as requisições
  simulateTimeout: () => {
    server.use(testHandlers.timeout);
  },

  // Simula erro 500 para todas as requisições
  simulateServerError: () => {
    server.use(testHandlers.serverError);
  },

  // Simula erro 404 para todas as requisições
  simulateNotFound: () => {
    server.use(testHandlers.notFound);
  },

  // Simula erro 401 para todas as requisições
  simulateUnauthorized: () => {
    server.use(testHandlers.unauthorized);
  },

  // Simula erro 403 para todas as requisições
  simulateForbidden: () => {
    server.use(testHandlers.forbidden);
  },

  // Simula resposta lenta
  simulateSlowResponse: () => {
    server.use(testHandlers.slowResponse);
  },

  // Simula resposta vazia
  simulateEmptyResponse: () => {
    server.use(testHandlers.emptyResponse);
  },

  // Simula dados inválidos
  simulateInvalidData: () => {
    server.use(testHandlers.invalidData);
  },
};
