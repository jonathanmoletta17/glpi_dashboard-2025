// Tipos centralizados para loading
export type LoadingSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';
export type LoadingVariant = 'default' | 'minimal' | 'detailed' | 'professional';
export type SkeletonType =
  | 'card'
  | 'list'
  | 'table'
  | 'metrics'
  | 'levels'
  | 'tickets'
  | 'dashboard'
  | 'custom';

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

// Configurações de variantes otimizadas
export const LOADING_VARIANTS = {
  default: {
    bg: 'bg-white dark:bg-gray-800',
    border: 'border border-gray-200 dark:border-gray-700',
    shadow: 'shadow-sm',
    skeleton: 'bg-gray-200 dark:bg-gray-700',
    text: 'text-gray-600 dark:text-gray-400',
  },
  minimal: {
    bg: 'bg-transparent',
    border: 'border-0',
    shadow: 'shadow-none',
    skeleton: 'bg-gray-100 dark:bg-gray-800',
    text: 'text-gray-500 dark:text-gray-500',
  },
  detailed: {
    bg: 'bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900',
    border: 'border border-gray-200 dark:border-gray-700',
    shadow: 'shadow-lg',
    skeleton: 'bg-gradient-to-r from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600',
    text: 'text-gray-700 dark:text-gray-300',
  },
  professional: {
    bg: 'bg-white dark:bg-gray-900',
    border: 'border border-gray-100 dark:border-gray-800',
    shadow: 'shadow-xl',
    skeleton: 'bg-gray-100 dark:bg-gray-800',
    text: 'text-gray-800 dark:text-gray-200',
  },
} as const;

// Animações otimizadas
export const LOADING_ANIMATIONS = {
  pulse: 'animate-pulse',
  spin: 'animate-spin',
  bounce: 'animate-bounce',
  ping: 'animate-ping',
} as const;
