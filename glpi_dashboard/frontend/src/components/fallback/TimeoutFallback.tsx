import React, { useState, useEffect } from 'react';
import { AlertTriangle, RefreshCw, Clock, Wifi, Server, Settings } from 'lucide-react';
import { ApiErrorType, ApiErrorInfo } from '../../hooks/useApiErrorHandler';

export interface TimeoutFallbackProps {
  /** Informações do erro */
  errorInfo?: ApiErrorInfo;
  /** Tipo de erro (se não fornecido via errorInfo) */
  errorType?: ApiErrorType;
  /** Mensagem personalizada */
  message?: string;
  /** Se deve mostrar botão de retry */
  showRetry?: boolean;
  /** Callback para tentar novamente */
  onRetry?: () => void;
  /** Se está em processo de retry */
  isRetrying?: boolean;
  /** Número de tentativas realizadas */
  retryCount?: number;
  /** Máximo de tentativas permitidas */
  maxRetries?: number;
  /** Se deve mostrar detalhes técnicos */
  showTechnicalDetails?: boolean;
  /** Callback para ativar modo offline */
  onEnableOfflineMode?: () => void;
  /** Se o modo offline está disponível */
  offlineModeAvailable?: boolean;
  /** Tamanho do componente */
  size?: 'small' | 'medium' | 'large';
  /** Se deve ocupar toda a altura disponível */
  fullHeight?: boolean;
}

/**
 * Componente de fallback especializado para erros de timeout e conectividade
 */
export const TimeoutFallback: React.FC<TimeoutFallbackProps> = ({
  errorInfo,
  errorType,
  message,
  showRetry = true,
  onRetry,
  isRetrying = false,
  retryCount = 0,
  maxRetries = 3,
  showTechnicalDetails = false,
  onEnableOfflineMode,
  offlineModeAvailable = false,
  size = 'medium',
  fullHeight = false,
}) => {
  const [showDetails, setShowDetails] = useState(false);
  const [countdown, setCountdown] = useState(0);

  // Determinar tipo de erro
  const effectiveErrorType = errorInfo?.type || errorType || 'timeout';

  // Determinar mensagem baseada no tipo de erro
  const getErrorMessage = () => {
    if (message) return message;
    if (errorInfo?.message) return errorInfo.message;

    switch (effectiveErrorType) {
      case 'timeout':
        return 'A requisição demorou mais que o esperado para responder';
      case 'connection':
        return 'Não foi possível conectar ao servidor';
      case 'network':
        return 'Problema de conectividade de rede';
      case 'server':
        return 'Erro interno do servidor';
      default:
        return 'Ocorreu um erro inesperado';
    }
  };

  // Determinar ícone baseado no tipo de erro
  const getErrorIcon = () => {
    switch (effectiveErrorType) {
      case 'timeout':
        return <Clock className="w-8 h-8 text-orange-500" />;
      case 'connection':
        return <Wifi className="w-8 h-8 text-red-500" />;
      case 'network':
        return <Wifi className="w-8 h-8 text-red-500" />;
      case 'server':
        return <Server className="w-8 h-8 text-red-600" />;
      default:
        return <AlertTriangle className="w-8 h-8 text-yellow-500" />;
    }
  };

  // Determinar cor do tema baseado no tipo de erro
  const getThemeColors = () => {
    switch (effectiveErrorType) {
      case 'timeout':
        return {
          bg: 'bg-orange-50',
          border: 'border-orange-200',
          text: 'text-orange-800',
          button: 'bg-orange-600 hover:bg-orange-700',
        };
      case 'connection':
      case 'network':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          text: 'text-red-800',
          button: 'bg-red-600 hover:bg-red-700',
        };
      case 'server':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          text: 'text-red-800',
          button: 'bg-red-600 hover:bg-red-700',
        };
      default:
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          text: 'text-yellow-800',
          button: 'bg-yellow-600 hover:bg-yellow-700',
        };
    }
  };

  // Determinar tamanhos baseado na prop size
  const getSizeClasses = () => {
    switch (size) {
      case 'small':
        return {
          container: 'p-4',
          icon: 'w-6 h-6',
          title: 'text-lg',
          text: 'text-sm',
          button: 'px-3 py-1.5 text-sm',
        };
      case 'large':
        return {
          container: 'p-8',
          icon: 'w-12 h-12',
          title: 'text-2xl',
          text: 'text-base',
          button: 'px-6 py-3 text-base',
        };
      default: // medium
        return {
          container: 'p-6',
          icon: 'w-8 h-8',
          title: 'text-xl',
          text: 'text-sm',
          button: 'px-4 py-2 text-sm',
        };
    }
  };

  const colors = getThemeColors();
  const sizes = getSizeClasses();

  // Countdown para próxima tentativa automática
  useEffect(() => {
    if (isRetrying && countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [isRetrying, countdown]);

  // Determinar se deve mostrar progresso de retry
  const showRetryProgress = retryCount > 0 && maxRetries > 0;
  const retryPercentage = (retryCount / maxRetries) * 100;

  return (
    <div
      className={`
        ${colors.bg} ${colors.border} ${colors.text}
        ${sizes.container}
        border rounded-lg
        ${fullHeight ? 'min-h-full flex flex-col justify-center' : ''}
      `}
    >
      <div className="flex flex-col items-center text-center space-y-4">
        {/* Ícone do erro */}
        <div className="flex-shrink-0">
          {getErrorIcon()}
        </div>

        {/* Título */}
        <div>
          <h3 className={`font-semibold ${sizes.title} mb-2`}>
            {effectiveErrorType === 'timeout' && 'Tempo Limite Excedido'}
            {effectiveErrorType === 'connection' && 'Falha de Conexão'}
            {effectiveErrorType === 'network' && 'Problema de Rede'}
            {effectiveErrorType === 'server' && 'Erro do Servidor'}
            {!['timeout', 'connection', 'network', 'server'].includes(effectiveErrorType) && 'Erro Inesperado'}
          </h3>
          <p className={`${colors.text} ${sizes.text} opacity-80`}>
            {getErrorMessage()}
          </p>
        </div>

        {/* Sugestão de ação */}
        {errorInfo?.suggestedAction && (
          <div className={`${colors.text} ${sizes.text} opacity-70 italic`}>
            💡 {errorInfo.suggestedAction}
          </div>
        )}

        {/* Progresso de retry */}
        {showRetryProgress && (
          <div className="w-full max-w-xs">
            <div className="flex justify-between text-xs mb-1">
              <span>Tentativa {retryCount} de {maxRetries}</span>
              <span>{Math.round(retryPercentage)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-300 ${
                  effectiveErrorType === 'timeout' ? 'bg-orange-500' : 'bg-red-500'
                }`}
                style={{ width: `${retryPercentage}%` }}
              />
            </div>
          </div>
        )}

        {/* Botões de ação */}
        <div className="flex flex-col sm:flex-row gap-3 w-full max-w-sm">
          {/* Botão de retry */}
          {showRetry && onRetry && (
            <button
              onClick={onRetry}
              disabled={isRetrying}
              className={`
                ${colors.button} text-white
                ${sizes.button}
                rounded-md font-medium
                flex items-center justify-center gap-2
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-colors duration-200
                flex-1
              `}
            >
              <RefreshCw className={`${isRetrying ? 'animate-spin' : ''} w-4 h-4`} />
              {isRetrying ? 'Tentando...' : 'Tentar Novamente'}
            </button>
          )}

          {/* Botão de modo offline */}
          {offlineModeAvailable && onEnableOfflineMode && (
            <button
              onClick={onEnableOfflineMode}
              className="
                bg-gray-600 hover:bg-gray-700 text-white
                px-4 py-2 text-sm
                rounded-md font-medium
                flex items-center justify-center gap-2
                transition-colors duration-200
                flex-1
              "
            >
              <Settings className="w-4 h-4" />
              Modo Offline
            </button>
          )}
        </div>

        {/* Detalhes técnicos */}
        {showTechnicalDetails && errorInfo && (
          <div className="w-full">
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="text-xs underline opacity-60 hover:opacity-80"
            >
              {showDetails ? 'Ocultar' : 'Mostrar'} detalhes técnicos
            </button>

            {showDetails && (
              <div className="mt-3 p-3 bg-gray-100 rounded text-xs font-mono text-left overflow-auto">
                <div><strong>Tipo:</strong> {errorInfo.type}</div>
                <div><strong>Timestamp:</strong> {new Date(errorInfo.timestamp).toLocaleString()}</div>
                <div><strong>Tentativas:</strong> {errorInfo.retryCount}</div>
                <div><strong>Retryable:</strong> {errorInfo.isRetryable ? 'Sim' : 'Não'}</div>
                {errorInfo.originalError && (
                  <div className="mt-2">
                    <strong>Erro original:</strong>
                    <pre className="mt-1 text-xs">{errorInfo.originalError.stack || errorInfo.originalError.message}</pre>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TimeoutFallback;
