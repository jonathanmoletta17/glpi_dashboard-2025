/**
 * Design System - Component Patterns
 * Padrões unificados para construção de componentes
 */

import { cn } from '@/lib/utils';

/**
 * Padrão base para cards
 */
export const cardPattern = {
  base: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm',
  hover:
    'hover:shadow-md hover:border-gray-300 dark:hover:border-gray-600 transition-all duration-200',
  padding: 'p-4',
  spacing: 'space-y-3',
} as const;

/**
 * Padrão para listas de itens
 */
export const listPattern = {
  container: 'space-y-2',
  item: 'p-3 rounded-md border border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800',
  itemHover: 'hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors',
  itemActive: 'active:scale-[0.98] transition-transform',
} as const;

/**
 * Padrão para badges
 */
export const badgePattern = {
  base: 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
  variants: {
    default: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
    primary: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    success: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    danger: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  },
} as const;

/**
 * Padrão para botões
 */
export const buttonPattern = {
  base: 'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none',
  sizes: {
    sm: 'h-8 px-3 text-xs',
    default: 'h-9 px-4 py-2',
    lg: 'h-10 px-8',
    icon: 'h-9 w-9',
  },
  variants: {
    default: 'bg-primary text-primary-foreground hover:bg-primary/90',
    destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
    outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
    ghost: 'hover:bg-accent hover:text-accent-foreground',
    link: 'text-primary underline-offset-4 hover:underline',
  },
} as const;

/**
 * Padrão para inputs
 */
export const inputPattern = {
  base: 'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50',
} as const;

/**
 * Funções utilitárias para aplicar padrões
 */
export const createCardClasses = (className?: string) =>
  cn(cardPattern.base, cardPattern.hover, cardPattern.padding, className);

export const createListItemClasses = (className?: string) =>
  cn(listPattern.item, listPattern.itemHover, listPattern.itemActive, className);

export const createBadgeClasses = (
  variant: keyof typeof badgePattern.variants = 'default',
  className?: string
) => cn(badgePattern.base, badgePattern.variants[variant], className);

export const createButtonClasses = (
  variant: keyof typeof buttonPattern.variants = 'default',
  size: keyof typeof buttonPattern.sizes = 'default',
  className?: string
) => cn(buttonPattern.base, buttonPattern.variants[variant], buttonPattern.sizes[size], className);

export const createInputClasses = (className?: string) => cn(inputPattern.base, className);
