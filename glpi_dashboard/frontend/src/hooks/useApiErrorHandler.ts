import { useState, useCallback, useRef } from 'react';

/**
 * Tipos de erro que podem ocorrer nas requisições de API
 */
export type ApiErrorType =
  | 'timeout'
  | 'connection'
  | 'server'
  | 'network'
  | 'abort'
  | 'unknown';

/**
 * Informações detalhadas sobre um erro de API
 */
export interface ApiErrorInfo {
  type: ApiErrorType;
  message: string;
  originalError: Error;
  timestamp: number;
  retryCount: number;
  isRetryable: boolean;
  suggestedAction?: string;
}

/**
 * Configurações para o tratamento de erros
 */
export interface ApiErrorHandlerConfig {
  /** Número máximo de tentativas automáticas */
  maxRetries?: number;
  /** Delay base entre tentativas (em ms) */
  retryDelay?: number;
  /** Se deve usar backoff exponencial */
  useExponentialBackoff?: boolean;
  /** Timeout personalizado (em ms) */
  timeout?: number;
  /** Callback chamado quando um erro ocorre */
  onError?: (errorInfo: ApiErrorInfo) => void;
  /** Callback chamado quando todas as tentativas falharam */
  onMaxRetriesReached?: (errorInfo: ApiErrorInfo) => void;
}

/**
 * Estado do tratamento de erros
 */
export interface ApiErrorState {
  /** Informações do último erro */
  lastError: ApiErrorInfo | null;
  /** Se está em processo de retry */
  isRetrying: boolean;
  /** Número de tentativas realizadas */
  retryCount: number;
  /** Se atingiu o máximo de tentativas */
  hasMaxRetriesReached: boolean;
}

/**
 * Hook para gerenciar erros de API com retry automático e classificação de erros
 */
export function useApiErrorHandler(config: ApiErrorHandlerConfig = {}) {
  const {
    maxRetries = 3,
    retryDelay = 1000,
    useExponentialBackoff = true,
    timeout = 30000,
    onError,
    onMaxRetriesReached,
  } = config;

  const [errorState, setErrorState] = useState<ApiErrorState>({
    lastError: null,
    isRetrying: false,
    retryCount: 0,
    hasMaxRetriesReached: false,
  });

  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * Classifica o tipo de erro baseado na mensagem e propriedades
   */
  const classifyError = useCallback((error: Error): ApiErrorType => {
    const message = error.message.toLowerCase();
    const errorName = error.name.toLowerCase();

    // Timeout errors
    if (
      message.includes('timeout') ||
      message.includes('timed out') ||
      errorName.includes('timeout') ||
      error.constructor.name === 'TimeoutError'
    ) {
      return 'timeout';
    }

    // Connection errors
    if (
      message.includes('network error') ||
      message.includes('connection') ||
      message.includes('econnrefused') ||
      message.includes('enotfound') ||
      message.includes('fetch')
    ) {
      return 'connection';
    }

    // Abort errors
    if (
      message.includes('abort') ||
      errorName.includes('abort') ||
      error.constructor.name === 'AbortError'
    ) {
      return 'abort';
    }

    // Server errors (HTTP 5xx)
    if (message.includes('500') || message.includes('502') || message.includes('503')) {
      return 'server';
    }

    // Network errors
    if (message.includes('network') || message.includes('net::')) {
      return 'network';
    }

    return 'unknown';
  }, []);

  /**
   * Determina se um erro é passível de retry
   */
  const isRetryableError = useCallback((errorType: ApiErrorType): boolean => {
    switch (errorType) {
      case 'timeout':
      case 'connection':
      case 'network':
      case 'server':
        return true;
      case 'abort':
      case 'unknown':
      default:
        return false;
    }
  }, []);

  /**
   * Gera sugestão de ação baseada no tipo de erro
   */
  const getSuggestedAction = useCallback((errorType: ApiErrorType): string => {
    switch (errorType) {
      case 'timeout':
        return 'Tente reduzir o período de consulta ou aguarde alguns minutos';
      case 'connection':
        return 'Verifique se o servidor está rodando e sua conexão de rede';
      case 'network':
        return 'Verifique sua conexão com a internet';
      case 'server':
        return 'Erro interno do servidor. Tente novamente em alguns minutos';
      case 'abort':
        return 'Operação cancelada pelo usuário';
      default:
        return 'Tente novamente ou contate o suporte';
    }
  }, []);

  /**
   * Cria informações detalhadas sobre o erro
   */
  const createErrorInfo = useCallback(
    (error: Error, retryCount: number): ApiErrorInfo => {
      const errorType = classifyError(error);
      return {
        type: errorType,
        message: error.message,
        originalError: error,
        timestamp: Date.now(),
        retryCount,
        isRetryable: isRetryableError(errorType),
        suggestedAction: getSuggestedAction(errorType),
      };
    },
    [classifyError, isRetryableError, getSuggestedAction]
  );

  /**
   * Calcula o delay para a próxima tentativa
   */
  const calculateRetryDelay = useCallback(
    (attempt: number): number => {
      if (!useExponentialBackoff) {
        return retryDelay;
      }
      // Exponential backoff: delay * (2 ^ attempt) com jitter
      const exponentialDelay = retryDelay * Math.pow(2, attempt);
      const jitter = Math.random() * 0.1 * exponentialDelay; // 10% jitter
      return Math.min(exponentialDelay + jitter, 30000); // Max 30 segundos
    },
    [retryDelay, useExponentialBackoff]
  );

  /**
   * Executa uma função com retry automático
   */
  const executeWithRetry = useCallback(
    async <T>(
      apiFunction: () => Promise<T>,
      customConfig?: Partial<ApiErrorHandlerConfig>
    ): Promise<T> => {
      const effectiveConfig = { ...config, ...customConfig };
      const effectiveMaxRetries = effectiveConfig.maxRetries ?? maxRetries;

      let lastError: Error;
      let attempt = 0;

      // Cancelar retry anterior se existir
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }

      // Criar novo AbortController
      abortControllerRef.current = new AbortController();

      while (attempt <= effectiveMaxRetries) {
        try {
          setErrorState(prev => ({
            ...prev,
            isRetrying: attempt > 0,
            retryCount: attempt,
            hasMaxRetriesReached: false,
          }));

          const result = await apiFunction();

          // Sucesso - resetar estado de erro
          setErrorState({
            lastError: null,
            isRetrying: false,
            retryCount: 0,
            hasMaxRetriesReached: false,
          });

          return result;
        } catch (error) {
          // Safely handle error conversion to avoid primitive conversion issues
          if (error instanceof Error) {
            lastError = error;
          } else if (typeof error === 'string') {
            lastError = new Error(error);
          } else if (error && typeof error === 'object') {
            // Handle object errors safely
            const message = (error as any).message || error.toString?.() || 'Unknown error occurred';
            lastError = new Error(message);
          } else {
            lastError = new Error('Unknown error occurred');
          }
          const errorInfo = createErrorInfo(lastError, attempt);

          // Atualizar estado com informações do erro
          setErrorState(prev => ({
            ...prev,
            lastError: errorInfo,
            retryCount: attempt,
            isRetrying: false,
            hasMaxRetriesReached: attempt >= effectiveMaxRetries,
          }));

          // Chamar callback de erro
          onError?.(errorInfo);

          // Se não é retryable ou atingiu max tentativas, lançar erro
          if (!errorInfo.isRetryable || attempt >= effectiveMaxRetries) {
            if (attempt >= effectiveMaxRetries) {
              onMaxRetriesReached?.(errorInfo);
            }
            throw lastError;
          }

          // Aguardar antes da próxima tentativa
          if (attempt < effectiveMaxRetries) {
            const delay = calculateRetryDelay(attempt);
            await new Promise((resolve) => {
              retryTimeoutRef.current = setTimeout(resolve, delay);
            });
          }

          attempt++;
        }
      }

      throw lastError!;
    },
    [config, maxRetries, onError, onMaxRetriesReached, createErrorInfo, calculateRetryDelay]
  );

  /**
   * Cancela operações em andamento
   */
  const cancel = useCallback(() => {
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  /**
   * Reseta o estado de erro
   */
  const resetError = useCallback(() => {
    setErrorState({
      lastError: null,
      isRetrying: false,
      retryCount: 0,
      hasMaxRetriesReached: false,
    });
  }, []);

  /**
   * Verifica se um erro específico deve ser tratado como crítico
   */
  const isCriticalError = useCallback((errorType: ApiErrorType): boolean => {
    return errorType === 'server' || errorType === 'unknown';
  }, []);

  return {
    errorState,
    executeWithRetry,
    cancel,
    resetError,
    classifyError,
    isRetryableError,
    isCriticalError,
    getSuggestedAction,
  };
}

export default useApiErrorHandler;
