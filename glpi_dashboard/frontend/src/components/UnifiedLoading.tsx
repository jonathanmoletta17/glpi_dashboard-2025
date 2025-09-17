import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, AlertCircle } from 'lucide-react';
import { componentConfigs } from '../config/appConfig';
import { createFlexClasses, TAILWIND_CLASSES } from '../design-system/utils';
import { cn } from '../lib/utils';

// Tipos unificados para loading
export type LoadingType = 'spinner' | 'skeleton' | 'progress' | 'overlay';
export type LoadingSize = 'sm' | 'md' | 'lg' | 'xl';
export type LoadingVariant = 'default' | 'minimal' | 'detailed';
export type SkeletonType = 'card' | 'list' | 'table' | 'metrics' | 'levels' | 'custom';

interface UnifiedLoadingProps {
  // Estados básicos
  isLoading: boolean;
  type?: LoadingType;
  size?: LoadingSize;
  variant?: LoadingVariant;

  // Conteúdo
  text?: string;
  title?: string;

  // Configurações visuais
  fullScreen?: boolean;
  overlay?: boolean;
  className?: string;

  // Skeleton específico
  skeletonType?: SkeletonType;
  skeletonCount?: number;

  // Progress específico
  progress?: number;
  estimatedTime?: number;
  showTimeEstimate?: boolean;

  // Callbacks
  onTimeout?: () => void;
  timeoutDuration?: number;
}

const sizeClasses = {
  sm: {
    spinner: 'w-4 h-4',
    text: 'text-xs',
    container: 'p-2',
    skeleton: 'h-3',
  },
  md: {
    spinner: 'w-6 h-6',
    text: 'text-sm',
    container: 'p-4',
    skeleton: 'h-4',
  },
  lg: {
    spinner: 'w-8 h-8',
    text: 'text-base',
    container: 'p-6',
    skeleton: 'h-5',
  },
  xl: {
    spinner: 'w-12 h-12',
    text: 'text-lg',
    container: 'p-8',
    skeleton: 'h-6',
  },
};

// Componente de Skeleton unificado
const UnifiedSkeleton = React.memo<{
  type: SkeletonType;
  count?: number;
  size: LoadingSize;
  className?: string;
}>(({ type, count = 1, size, className = '' }) => {
  const skeletonClass = `bg-gray-200 dark:bg-gray-700 rounded animate-pulse ${className}`;

  const renderSkeletonByType = () => {
    switch (type) {
      case 'card':
        return (
          <div
            className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 ${sizeClasses[size].container}`}
          >
            <div className='animate-pulse'>
              <div className='flex items-center justify-between mb-4'>
                <div className='w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg' />
                <div className='w-16 h-4 bg-gray-200 dark:bg-gray-700 rounded' />
              </div>
              <div className='space-y-3'>
                <div className='w-24 h-4 bg-gray-200 dark:bg-gray-700 rounded' />
                <div className='w-16 h-8 bg-gray-200 dark:bg-gray-700 rounded' />
              </div>
              <div className='mt-4 w-full h-2 bg-gray-200 dark:bg-gray-700 rounded' />
            </div>
          </div>
        );

      case 'list':
        return (
          <div className='space-y-3'>
            {Array.from({ length: count }).map((_, i) => (
              <div key={i} className='flex items-center space-x-3 p-3 border rounded'>
                <div className={`${sizeClasses[size].skeleton} w-8 ${skeletonClass}`} />
                <div className={`${sizeClasses[size].skeleton} flex-1 ${skeletonClass}`} />
                <div className={`${sizeClasses[size].skeleton} w-16 ${skeletonClass}`} />
              </div>
            ))}
          </div>
        );

      case 'table':
        return (
          <div className='space-y-4'>
            <div className={`${sizeClasses[size].skeleton} w-1/4 ${skeletonClass}`} />
            {Array.from({ length: count }).map((_, i) => (
              <div key={i} className='flex space-x-4'>
                <div className='h-10 w-10 bg-gray-200 dark:bg-gray-700 rounded-full' />
                <div className='flex-1 space-y-2'>
                  <div className={`${sizeClasses[size].skeleton} w-3/4 ${skeletonClass}`} />
                  <div className={`h-3 w-1/2 ${skeletonClass}`} />
                </div>
              </div>
            ))}
          </div>
        );

      case 'metrics':
        return (
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6'>
            {Array.from({ length: count || 4 }).map((_, i) => (
              <div
                key={i}
                className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 ${sizeClasses[size].container}`}
              >
                <div className='animate-pulse'>
                  <div className='flex items-center justify-between mb-4'>
                    <div className='w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg' />
                    <div className='w-16 h-4 bg-gray-200 dark:bg-gray-700 rounded' />
                  </div>
                  <div className='space-y-3'>
                    <div className='w-24 h-4 bg-gray-200 dark:bg-gray-700 rounded' />
                    <div className='w-16 h-8 bg-gray-200 dark:bg-gray-700 rounded' />
                  </div>
                </div>
              </div>
            ))}
          </div>
        );

      case 'levels':
        return (
          <div className='space-y-6'>
            <div className='flex items-center justify-between'>
              <div className='space-y-2'>
                <div className='w-48 h-6 bg-gray-200 dark:bg-gray-700 rounded' />
                <div className='w-64 h-4 bg-gray-200 dark:bg-gray-700 rounded' />
              </div>
              <div className='w-24 h-16 bg-gray-200 dark:bg-gray-700 rounded-lg' />
            </div>
            <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6'>
              {Array.from({ length: 4 }).map((_, i) => (
                <div
                  key={i}
                  className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 ${sizeClasses[size].container}`}
                >
                  <div className='animate-pulse'>
                    <div className='flex items-center justify-between mb-4'>
                      <div className='w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg' />
                      <div className='w-16 h-4 bg-gray-200 dark:bg-gray-700 rounded' />
                    </div>
                    <div className='space-y-3'>
                      <div className='w-24 h-4 bg-gray-200 dark:bg-gray-700 rounded' />
                      <div className='w-16 h-8 bg-gray-200 dark:bg-gray-700 rounded' />
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div
              className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 h-48 ${sizeClasses[size].container}`}
            >
              <div className='animate-pulse h-full bg-gray-200 dark:bg-gray-700 rounded' />
            </div>
          </div>
        );

      default:
        return <div className={`${sizeClasses[size].skeleton} w-full ${skeletonClass}`} />;
    }
  };

  return <div className={className}>{renderSkeletonByType()}</div>;
});

UnifiedSkeleton.displayName = 'UnifiedSkeleton';

// Componente principal unificado
export const UnifiedLoading = React.memo<UnifiedLoadingProps>(({
  isLoading,
  type = 'spinner',
  size = 'md',
  variant = 'default',
  text,
  title,
  fullScreen = false,
  overlay = false,
  className = '',
  skeletonType = 'card',
  skeletonCount = 1,
  progress,
  estimatedTime = 30,
  showTimeEstimate = false,
  onTimeout,
  timeoutDuration = 60,
}) => {
  const [elapsedTime, setElapsedTime] = useState(0);
  const [hasTimedOut, setHasTimedOut] = useState(false);
  const [calculatedProgress, setCalculatedProgress] = useState(0);

  const config = componentConfigs.unifiedLoading;

  // Reset states when loading changes
  useEffect(() => {
    if (isLoading) {
      setElapsedTime(0);
      setHasTimedOut(false);
      setCalculatedProgress(0);
    }
  }, [isLoading]);

  // Timer para elapsed time e progress
  useEffect(() => {
    if (!isLoading || type !== 'progress') return;

    const interval = setInterval(() => {
      setElapsedTime(prev => {
        const newTime = prev + 1;

        // Calcular progresso baseado no tempo estimado se não fornecido
        if (progress === undefined) {
          const progressPercent = Math.min((newTime / estimatedTime) * 100, 95);
          setCalculatedProgress(progressPercent);
        }

        // Verificar timeout
        if (newTime >= timeoutDuration && !hasTimedOut) {
          setHasTimedOut(true);
          onTimeout?.();
        }

        return newTime;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isLoading, type, estimatedTime, timeoutDuration, hasTimedOut, onTimeout, progress]);

  const formatTime = (seconds: number) => {
    if (seconds < 60) {
      return `${seconds}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getStatusColor = () => {
    if (hasTimedOut) return 'text-red-600 dark:text-red-400';
    if (elapsedTime > estimatedTime * 0.8) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-blue-600 dark:text-blue-400';
  };

  if (!isLoading) return null;

  const renderLoadingContent = () => {
    switch (type) {
      case 'skeleton': {
        return (
          <UnifiedSkeleton
            type={skeletonType}
            count={skeletonCount}
            size={size}
            className={className}
          />
        );
      }

      case 'progress': {
        const currentProgress = progress !== undefined ? progress : calculatedProgress;
        return (
          <div
            className={`flex flex-col items-center justify-center space-y-4 ${sizeClasses[size].container} ${className}`}
          >
            {title && (
              <h3
                className={`font-semibold text-gray-900 dark:text-white ${sizeClasses[size].text}`}
              >
                {title}
              </h3>
            )}

            <div className='w-full max-w-xs'>
              <div className='flex justify-between items-center mb-2'>
                <span className={`${sizeClasses[size].text} text-gray-600 dark:text-gray-400`}>
                  {text || 'Carregando...'}
                </span>
                {showTimeEstimate && (
                  <span className={`${sizeClasses[size].text} ${getStatusColor()}`}>
                    {formatTime(elapsedTime)}
                  </span>
                )}
              </div>

              <div className='w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2'>
                <motion.div
                  className='bg-blue-600 dark:bg-blue-400 h-2 rounded-full'
                  initial={{ width: 0 }}
                  animate={{ width: `${currentProgress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>

              <div className='flex justify-between items-center mt-2'>
                <span className={`${sizeClasses[size].text} text-gray-500 dark:text-gray-400`}>
                  {Math.round(currentProgress)}%
                </span>
                {hasTimedOut && (
                  <div className='flex items-center space-x-1 text-red-600 dark:text-red-400'>
                    <AlertCircle className='w-4 h-4' />
                    <span className='text-xs'>Timeout</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      }

      case 'overlay': {
        return (
          <div className='fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center'>
            <div className='bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8 max-w-md w-full mx-4'>
              <div className='flex flex-col items-center space-y-4'>
                <Loader2
                  className={`${sizeClasses[size].spinner} text-blue-600 dark:text-blue-400 animate-spin`}
                />
                {title && (
                  <h3
                    className={`font-semibold text-gray-900 dark:text-white ${sizeClasses[size].text}`}
                  >
                    {title}
                  </h3>
                )}
                {text && (
                  <p
                    className={`text-gray-600 dark:text-gray-400 text-center ${sizeClasses[size].text}`}
                  >
                    {text}
                  </p>
                )}
              </div>
            </div>
          </div>
        );
      }

      default: {
        // spinner
        const spinnerContent = (
          <div
            className={`flex flex-col items-center justify-center space-y-3 ${sizeClasses[size].container} ${className}`}
          >
            <Loader2
              className={`${sizeClasses[size].spinner} text-blue-600 dark:text-blue-400 animate-spin`}
            />
            {text && (
              <p
                className={`text-gray-600 dark:text-gray-400 font-medium ${sizeClasses[size].text}`}
              >
                {text}
              </p>
            )}
          </div>
        );

        if (fullScreen) {
          return (
            <div className='fixed inset-0 bg-white dark:bg-gray-900 bg-opacity-80 dark:bg-opacity-80 backdrop-blur-sm z-50 flex items-center justify-center'>
              {spinnerContent}
            </div>
          );
        }

        return spinnerContent;
      }
    }
  };

  return (
    <AnimatePresence>
      {isLoading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: config.animationDuration / 1000 }}
        >
          {renderLoadingContent()}
        </motion.div>
      )}
    </AnimatePresence>
  );
}); // End of UnifiedLoading component

// Componentes de conveniência para casos específicos
export const LoadingSpinner: React.FC<Omit<UnifiedLoadingProps, 'type'>> = props => (
  <UnifiedLoading {...props} type='spinner' />
);

export const LoadingSkeleton: React.FC<Omit<UnifiedLoadingProps, 'type'>> = props => (
  <UnifiedLoading {...props} type='skeleton' />
);

export const LoadingProgress: React.FC<Omit<UnifiedLoadingProps, 'type'>> = props => (
  <UnifiedLoading {...props} type='progress' />
);

export const LoadingOverlay: React.FC<Omit<UnifiedLoadingProps, 'type'>> = props => (
  <UnifiedLoading {...props} type='overlay' />
);

// Componentes específicos para compatibilidade
export const SkeletonCard: React.FC<{ className?: string }> = ({ className }) => (
  <LoadingSkeleton skeletonType='card' className={className} isLoading={true} />
);

// SkeletonMetricsGrid removido - MetricsGrid foi removido do sistema

export const SkeletonLevelsSection: React.FC = () => (
  <LoadingSkeleton skeletonType='levels' isLoading={true} />
);

// Error state component (mantido do arquivo original)
interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Erro ao carregar dados',
  message = 'Ocorreu um erro inesperado. Tente novamente.',
  onRetry,
  className = '',
}) => {
  return (
    <div
      className={cn(
        createFlexClasses('col', 'center', 'center', 'normal'),
        TAILWIND_CLASSES.padding.section,
        className
      )}
    >
      <div
        className={cn(
          'w-16 h-16 bg-red-100 dark:bg-red-900/20 rounded-full',
          createFlexClasses('row', 'center', 'center')
        )}
      >
        <AlertCircle className='w-8 h-8 text-red-600 dark:text-red-400' />
      </div>

      <div className={cn('text-center', TAILWIND_CLASSES.spaceY.list)}>
        <h3 className='text-lg font-semibold text-gray-900 dark:text-white'>{title}</h3>
        <p className='text-gray-600 dark:text-gray-400 max-w-md'>{message}</p>
      </div>

      {onRetry && (
        <button
          onClick={onRetry}
          className={cn(
            createFlexClasses('row', 'center', 'start', 'small'),
            'font-semibold rounded-xl bg-gradient-to-r from-blue-500 to-blue-700 hover:from-blue-600 hover:to-blue-800 text-white shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-300',
            TAILWIND_CLASSES.padding.button
          )}
        >
          <svg className='w-4 h-4' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
            <path
              strokeLinecap='round'
              strokeLinejoin='round'
              strokeWidth={2}
              d='M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15'
            />
          </svg>
          <span>Tentar Novamente</span>
        </button>
      )}
    </div>
  );
};

UnifiedLoading.displayName = 'UnifiedLoading';

export default UnifiedLoading;
