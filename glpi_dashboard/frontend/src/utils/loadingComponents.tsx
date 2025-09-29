import React from 'react';
import { motion } from 'framer-motion';
import { Loader2, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader } from '@/components/ui/card';

// Tipos centralizados para loading
export type LoadingSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';
export type LoadingVariant = 'default' | 'minimal' | 'detailed' | 'professional';
export type SkeletonType = 'card' | 'list' | 'table' | 'metrics' | 'levels' | 'tickets' | 'dashboard' | 'custom';

// Configurações de tamanhos otimizadas
export const LOADING_SIZES = {
  xs: {
    spinner: 'w-3 h-3',
    text: 'text-xs',
    container: 'p-1',
    skeleton: 'h-2',
    gap: 'gap-1',
  },
  sm: {
    spinner: 'w-4 h-4',
    text: 'text-xs',
    container: 'p-2',
    skeleton: 'h-3',
    gap: 'gap-2',
  },
  md: {
    spinner: 'w-6 h-6',
    text: 'text-sm',
    container: 'p-4',
    skeleton: 'h-4',
    gap: 'gap-3',
  },
  lg: {
    spinner: 'w-8 h-8',
    text: 'text-base',
    container: 'p-6',
    skeleton: 'h-5',
    gap: 'gap-4',
  },
  xl: {
    spinner: 'w-12 h-12',
    text: 'text-lg',
    container: 'p-8',
    skeleton: 'h-6',
    gap: 'gap-6',
  },
} as const;

// Configurações de variantes
export const LOADING_VARIANTS = {
  default: {
    bg: 'bg-white dark:bg-gray-800',
    border: 'border border-gray-200 dark:border-gray-700',
    shadow: 'shadow-sm',
    skeleton: 'bg-gray-200 dark:bg-gray-700',
  },
  minimal: {
    bg: 'bg-transparent',
    border: '',
    shadow: '',
    skeleton: 'bg-gray-100 dark:bg-gray-800',
  },
  detailed: {
    bg: 'bg-white/80 backdrop-blur-sm dark:bg-white/5',
    border: 'border border-white/90 dark:border-white/10',
    shadow: 'shadow-lg',
    skeleton: 'bg-gray-200 dark:bg-gray-700',
  },
  professional: {
    bg: 'bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900',
    border: 'border border-gray-200/50 dark:border-gray-700/50',
    shadow: 'shadow-md hover:shadow-lg transition-shadow',
    skeleton: 'bg-gradient-to-r from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600',
  },
} as const;

// Animações otimizadas
export const LOADING_ANIMATIONS = {
  pulse: 'animate-pulse',
  spin: 'animate-spin',
  bounce: 'animate-bounce',
  shimmer: 'animate-pulse bg-gradient-to-r from-transparent via-white/20 to-transparent',
  wave: 'animate-pulse duration-1000',
} as const;

// Interface para props de skeleton
interface SkeletonProps {
  type: SkeletonType;
  count?: number;
  size?: LoadingSize;
  variant?: LoadingVariant;
  className?: string;
  animate?: boolean;
}

// Componente base de skeleton otimizado
export const OptimizedSkeleton: React.FC<SkeletonProps> = ({
  type,
  count = 1,
  size = 'md',
  variant = 'default',
  className = '',
  animate = true,
}) => {
  const sizeConfig = LOADING_SIZES[size];
  const variantConfig = LOADING_VARIANTS[variant];
  const animationClass = animate ? LOADING_ANIMATIONS.pulse : '';

  const baseSkeletonClass = cn(
    variantConfig.skeleton,
    'rounded',
    animationClass,
    className
  );

  const renderSkeletonByType = () => {
    switch (type) {
      case 'card':
        return (
          <Card className={cn(variantConfig.bg, variantConfig.border, variantConfig.shadow)}>
            <CardHeader className='pb-2'>
              <div className='flex items-center justify-between'>
                <div className={cn(baseSkeletonClass, 'w-20', sizeConfig.skeleton)} />
                <div className={cn(baseSkeletonClass, 'w-8 h-8 rounded-full')} />
              </div>
            </CardHeader>
            <CardContent>
              <div className={cn('space-y-3', sizeConfig.gap)}>
                <div className={cn(baseSkeletonClass, 'w-16 h-8')} />
                <div className={cn(baseSkeletonClass, 'w-24', sizeConfig.skeleton)} />
              </div>
            </CardContent>
          </Card>
        );

      case 'dashboard':
        return (
          <Card className={cn(variantConfig.bg, variantConfig.border, variantConfig.shadow)}>
            <CardHeader className='pb-2'>
              <div className='flex items-center justify-between'>
                <div className={cn(baseSkeletonClass, 'w-20 h-4')} />
                <div className={cn(baseSkeletonClass, 'w-8 h-8 rounded-full')} />
              </div>
            </CardHeader>
            <CardContent>
              <div className='space-y-3'>
                <div className={cn(baseSkeletonClass, 'w-16 h-8')} />
                <div className={cn(baseSkeletonClass, 'w-24 h-3')} />
              </div>
            </CardContent>
          </Card>
        );

      case 'tickets':
        return (
          <div className='space-y-3'>
            {Array.from({ length: count }).map((_, i) => (
              <div key={i} className={cn('p-4 rounded-lg', variantConfig.bg, variantConfig.border)}>
                <div className='flex items-start justify-between gap-3'>
                  <div className={cn(baseSkeletonClass, 'h-6 w-16 rounded-full flex-shrink-0')} />
                  <div className='flex-1 space-y-2'>
                    <div className='flex items-start justify-between gap-2'>
                      <div className='flex items-center gap-2'>
                        <div className={cn(baseSkeletonClass, 'h-4 w-12')} />
                        <div className={cn(baseSkeletonClass, 'h-4 w-12')} />
                      </div>
                      <div className={cn(baseSkeletonClass, 'h-4 w-4')} />
                    </div>
                    <div className={cn(baseSkeletonClass, 'h-4 w-3/4')} />
                    <div className={cn(baseSkeletonClass, 'h-3 w-1/2')} />
                    <div className='flex items-center justify-between gap-2'>
                      <div className={cn(baseSkeletonClass, 'h-3 w-24')} />
                      <div className={cn(baseSkeletonClass, 'h-3 w-16')} />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        );

      case 'list':
        return (
          <div className='space-y-3'>
            {Array.from({ length: count }).map((_, i) => (
              <div key={i} className={cn('flex items-center space-x-3 p-3 rounded', variantConfig.border)}>
                <div className={cn(baseSkeletonClass, sizeConfig.skeleton, 'w-8')} />
                <div className={cn(baseSkeletonClass, sizeConfig.skeleton, 'flex-1')} />
                <div className={cn(baseSkeletonClass, sizeConfig.skeleton, 'w-16')} />
              </div>
            ))}
          </div>
        );

      case 'table':
        return (
          <div className='space-y-4'>
            <div className={cn(baseSkeletonClass, sizeConfig.skeleton, 'w-1/4')} />
            {Array.from({ length: count }).map((_, i) => (
              <div key={i} className='flex space-x-4'>
                <div className={cn(baseSkeletonClass, 'h-10 w-10 rounded-full')} />
                <div className='flex-1 space-y-2'>
                  <div className={cn(baseSkeletonClass, sizeConfig.skeleton, 'w-3/4')} />
                  <div className={cn(baseSkeletonClass, 'h-3 w-1/2')} />
                </div>
              </div>
            ))}
          </div>
        );

      case 'metrics':
        return (
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6'>
            {Array.from({ length: count || 4 }).map((_, i) => (
              <Card key={i} className={cn(variantConfig.bg, variantConfig.border, variantConfig.shadow)}>
                <CardContent className={sizeConfig.container}>
                  <div className='flex items-center justify-between mb-4'>
                    <div className={cn(baseSkeletonClass, 'w-10 h-10 rounded-lg')} />
                    <div className={cn(baseSkeletonClass, 'w-16 h-4')} />
                  </div>
                  <div className='space-y-3'>
                    <div className={cn(baseSkeletonClass, 'w-24 h-4')} />
                    <div className={cn(baseSkeletonClass, 'w-16 h-8')} />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        );

      case 'levels':
        return (
          <div className='space-y-6'>
            <div className='flex items-center justify-between'>
              <div className='space-y-2'>
                <div className={cn(baseSkeletonClass, 'w-48 h-6')} />
                <div className={cn(baseSkeletonClass, 'w-64 h-4')} />
              </div>
              <div className={cn(baseSkeletonClass, 'w-24 h-16 rounded-lg')} />
            </div>
            <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6'>
              {Array.from({ length: 4 }).map((_, i) => (
                <Card key={i} className={cn(variantConfig.bg, variantConfig.border, variantConfig.shadow)}>
                  <CardContent className={sizeConfig.container}>
                    <div className='flex items-center justify-between mb-4'>
                      <div className={cn(baseSkeletonClass, 'w-10 h-10 rounded-lg')} />
                      <div className={cn(baseSkeletonClass, 'w-16 h-4')} />
                    </div>
                    <div className='space-y-3'>
                      <div className={cn(baseSkeletonClass, 'w-24 h-4')} />
                      <div className={cn(baseSkeletonClass, 'w-16 h-8')} />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            <Card className={cn(variantConfig.bg, variantConfig.border, variantConfig.shadow, 'h-48')}>
              <CardContent className={cn(sizeConfig.container, 'h-full')}>
                <div className={cn(baseSkeletonClass, 'h-full rounded')} />
              </CardContent>
            </Card>
          </div>
        );

      default:
        return <div className={cn(baseSkeletonClass, sizeConfig.skeleton, 'w-full')} />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
      className={className}
    >
      {renderSkeletonByType()}
    </motion.div>
  );
};

// Componentes de conveniência específicos
export const SkeletonCard: React.FC<Omit<SkeletonProps, 'type'>> = (props) => (
  <OptimizedSkeleton {...props} type="card" />
);

export const SkeletonDashboard: React.FC<Omit<SkeletonProps, 'type'>> = (props) => (
  <OptimizedSkeleton {...props} type="dashboard" />
);

export const SkeletonTickets: React.FC<Omit<SkeletonProps, 'type'>> = (props) => (
  <OptimizedSkeleton {...props} type="tickets" />
);

export const SkeletonMetrics: React.FC<Omit<SkeletonProps, 'type'>> = (props) => (
  <OptimizedSkeleton {...props} type="metrics" />
);

export const SkeletonLevels: React.FC<Omit<SkeletonProps, 'type'>> = (props) => (
  <OptimizedSkeleton {...props} type="levels" />
);

// Spinner otimizado
interface SpinnerProps {
  size?: LoadingSize;
  className?: string;
  text?: string;
}

export const OptimizedSpinner: React.FC<SpinnerProps> = ({
  size = 'md',
  className = '',
  text,
}) => {
  const sizeConfig = LOADING_SIZES[size];

  return (
    <div className={cn('flex flex-col items-center justify-center gap-2', className)}>
      <Loader2 className={cn(sizeConfig.spinner, 'text-blue-600 dark:text-blue-400', LOADING_ANIMATIONS.spin)} />
      {text && (
        <span className={cn('text-gray-600 dark:text-gray-400', sizeConfig.text)}>
          {text}
        </span>
      )}
    </div>
  );
};

// Estado de erro otimizado
interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
  size?: LoadingSize;
}

export const OptimizedErrorState: React.FC<ErrorStateProps> = ({
  title = 'Erro ao carregar dados',
  message = 'Ocorreu um erro inesperado. Tente novamente.',
  onRetry,
  className = '',
  size = 'md',
}) => {
  const sizeConfig = LOADING_SIZES[size];

  return (
    <div className={cn('flex flex-col items-center justify-center text-center', sizeConfig.container, className)}>
      <div className='w-16 h-16 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center mb-4'>
        <AlertCircle className='w-8 h-8 text-red-600 dark:text-red-400' />
      </div>

      <div className='space-y-2 mb-4'>
        <h3 className={cn('font-semibold text-gray-900 dark:text-white', sizeConfig.text)}>
          {title}
        </h3>
        <p className={cn('text-gray-600 dark:text-gray-400 max-w-md', sizeConfig.text)}>
          {message}
        </p>
      </div>

      {onRetry && (
        <button
          onClick={onRetry}
          className={cn(
            'flex items-center gap-2 font-semibold rounded-xl bg-gradient-to-r from-blue-500 to-blue-700 hover:from-blue-600 hover:to-blue-800 text-white shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-300',
            sizeConfig.container
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

// Hook para gerenciar estados de loading
export const useLoadingState = (initialState = false) => {
  const [isLoading, setIsLoading] = React.useState(initialState);
  const [error, setError] = React.useState<string | null>(null);

  const startLoading = React.useCallback(() => {
    setIsLoading(true);
    setError(null);
  }, []);

  const stopLoading = React.useCallback(() => {
    setIsLoading(false);
  }, []);

  const setLoadingError = React.useCallback((errorMessage: string) => {
    setIsLoading(false);
    setError(errorMessage);
  }, []);

  const reset = React.useCallback(() => {
    setIsLoading(false);
    setError(null);
  }, []);

  return {
    isLoading,
    error,
    startLoading,
    stopLoading,
    setLoadingError,
    reset,
  };
};
