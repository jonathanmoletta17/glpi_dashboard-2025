/**
 * Design Tokens - Tickets System
 * Tokens específicos para o sistema de tickets com cores semânticas e ícones SVG
 */

import { AlertTriangle, Circle, Clock, CheckCircle, XCircle, Zap } from 'lucide-react';
import { LucideIcon } from 'lucide-react';

/**
 * Configuração de prioridades com ícones SVG e cores semânticas
 */
export interface PriorityConfig {
  variant: 'default' | 'secondary' | 'success' | 'warning' | 'danger';
  icon: LucideIcon;
  color: string;
  bgColor: string;
  borderColor: string;
  textColor: string;
  darkBgColor: string;
  darkTextColor: string;
  darkBorderColor: string;
}

export const priorityTokens: Record<string, PriorityConfig> = {
  'Crítica': {
    variant: 'danger',
    icon: AlertTriangle,
    color: 'rgb(239 68 68)', // red-500
    bgColor: 'rgb(254 242 242)', // red-50
    borderColor: 'rgb(252 165 165)', // red-300
    textColor: 'rgb(153 27 27)', // red-900
    darkBgColor: 'rgb(127 29 29)', // red-900
    darkTextColor: 'rgb(254 202 202)', // red-200
    darkBorderColor: 'rgb(185 28 28)', // red-700
  },
  'Muito Alta': {
    variant: 'danger',
    icon: Zap,
    color: 'rgb(239 68 68)', // red-500
    bgColor: 'rgb(254 242 242)', // red-50
    borderColor: 'rgb(252 165 165)', // red-300
    textColor: 'rgb(153 27 27)', // red-900
    darkBgColor: 'rgb(127 29 29)', // red-900
    darkTextColor: 'rgb(254 202 202)', // red-200
    darkBorderColor: 'rgb(185 28 28)', // red-700
  },
  'Alta': {
    variant: 'warning',
    icon: AlertTriangle,
    color: 'rgb(245 158 11)', // amber-500
    bgColor: 'rgb(255 251 235)', // amber-50
    borderColor: 'rgb(252 211 77)', // amber-300
    textColor: 'rgb(146 64 14)', // amber-900
    darkBgColor: 'rgb(146 64 14)', // amber-900
    darkTextColor: 'rgb(252 211 77)', // amber-300
    darkBorderColor: 'rgb(180 83 9)', // amber-700
  },
  'Média': {
    variant: 'default',
    icon: Circle,
    color: 'rgb(59 130 246)', // blue-500
    bgColor: 'rgb(239 246 255)', // blue-50
    borderColor: 'rgb(147 197 253)', // blue-300
    textColor: 'rgb(30 58 138)', // blue-900
    darkBgColor: 'rgb(30 58 138)', // blue-900
    darkTextColor: 'rgb(147 197 253)', // blue-300
    darkBorderColor: 'rgb(29 78 216)', // blue-700
  },
  'Normal': {
    variant: 'secondary',
    icon: Circle,
    color: 'rgb(107 114 128)', // gray-500
    bgColor: 'rgb(249 250 251)', // gray-50
    borderColor: 'rgb(209 213 219)', // gray-300
    textColor: 'rgb(55 65 81)', // gray-700
    darkBgColor: 'rgb(55 65 81)', // gray-700
    darkTextColor: 'rgb(209 213 219)', // gray-300
    darkBorderColor: 'rgb(75 85 99)', // gray-600
  },
  'Baixa': {
    variant: 'success',
    icon: CheckCircle,
    color: 'rgb(34 197 94)', // green-500
    bgColor: 'rgb(240 253 244)', // green-50
    borderColor: 'rgb(134 239 172)', // green-300
    textColor: 'rgb(20 83 45)', // green-900
    darkBgColor: 'rgb(20 83 45)', // green-900
    darkTextColor: 'rgb(134 239 172)', // green-300
    darkBorderColor: 'rgb(21 128 61)', // green-700
  },
  'Muito Baixa': {
    variant: 'secondary',
    icon: Circle,
    color: 'rgb(107 114 128)', // gray-500
    bgColor: 'rgb(249 250 251)', // gray-50
    borderColor: 'rgb(209 213 219)', // gray-300
    textColor: 'rgb(55 65 81)', // gray-700
    darkBgColor: 'rgb(55 65 81)', // gray-700
    darkTextColor: 'rgb(209 213 219)', // gray-300
    darkBorderColor: 'rgb(75 85 99)', // gray-600
  },
};

/**
 * Configuração de status com ícones SVG
 */
export interface StatusConfig {
  variant: 'default' | 'secondary' | 'success' | 'warning' | 'danger';
  icon: LucideIcon;
  color: string;
  bgColor: string;
  borderColor: string;
  textColor: string;
  darkBgColor: string;
  darkTextColor: string;
  darkBorderColor: string;
}

export const statusTokens: Record<string, StatusConfig> = {
  'novo': {
    variant: 'default',
    icon: Circle,
    color: 'rgb(59 130 246)', // blue-500
    bgColor: 'rgb(239 246 255)', // blue-50
    borderColor: 'rgb(147 197 253)', // blue-300
    textColor: 'rgb(30 58 138)', // blue-900
    darkBgColor: 'rgb(30 58 138)', // blue-900
    darkTextColor: 'rgb(147 197 253)', // blue-300
    darkBorderColor: 'rgb(29 78 216)', // blue-700
  },
  'em_progresso': {
    variant: 'warning',
    icon: Clock,
    color: 'rgb(245 158 11)', // amber-500
    bgColor: 'rgb(255 251 235)', // amber-50
    borderColor: 'rgb(252 211 77)', // amber-300
    textColor: 'rgb(146 64 14)', // amber-900
    darkBgColor: 'rgb(146 64 14)', // amber-900
    darkTextColor: 'rgb(252 211 77)', // amber-300
    darkBorderColor: 'rgb(180 83 9)', // amber-700
  },
  'pendente': {
    variant: 'secondary',
    icon: Clock,
    color: 'rgb(107 114 128)', // gray-500
    bgColor: 'rgb(249 250 251)', // gray-50
    borderColor: 'rgb(209 213 219)', // gray-300
    textColor: 'rgb(55 65 81)', // gray-700
    darkBgColor: 'rgb(55 65 81)', // gray-700
    darkTextColor: 'rgb(209 213 219)', // gray-300
    darkBorderColor: 'rgb(75 85 99)', // gray-600
  },
  'solucionado': {
    variant: 'success',
    icon: CheckCircle,
    color: 'rgb(34 197 94)', // green-500
    bgColor: 'rgb(240 253 244)', // green-50
    borderColor: 'rgb(134 239 172)', // green-300
    textColor: 'rgb(20 83 45)', // green-900
    darkBgColor: 'rgb(20 83 45)', // green-900
    darkTextColor: 'rgb(134 239 172)', // green-300
    darkBorderColor: 'rgb(21 128 61)', // green-700
  },
  'fechado': {
    variant: 'secondary',
    icon: XCircle,
    color: 'rgb(107 114 128)', // gray-500
    bgColor: 'rgb(249 250 251)', // gray-50
    borderColor: 'rgb(209 213 219)', // gray-300
    textColor: 'rgb(55 65 81)', // gray-700
    darkBgColor: 'rgb(55 65 81)', // gray-700
    darkTextColor: 'rgb(209 213 219)', // gray-300
    darkBorderColor: 'rgb(75 85 99)', // gray-600
  },
};

/**
 * Tokens de espaçamento específicos para tickets
 */
export const ticketSpacing = {
  card: {
    padding: 'p-4',
    gap: 'gap-4',
    margin: 'mb-4',
  },
  item: {
    padding: 'p-3',
    gap: 'gap-3',
    margin: 'mb-2',
  },
  badge: {
    padding: 'px-2.5 py-0.5',
    gap: 'gap-1',
    margin: 'mr-2',
  },
  icon: {
    size: 'h-4 w-4',
    sizeSmall: 'h-3 w-3',
    sizeLarge: 'h-5 w-5',
  },
} as const;

/**
 * Tokens de tipografia para tickets
 */
export const ticketTypography = {
  title: {
    size: 'text-sm',
    weight: 'font-medium',
    color: 'text-gray-900 dark:text-gray-100',
    lineHeight: 'leading-5',
  },
  description: {
    size: 'text-xs',
    weight: 'font-normal',
    color: 'text-gray-600 dark:text-gray-400',
    lineHeight: 'leading-4',
  },
  metadata: {
    size: 'text-xs',
    weight: 'font-medium',
    color: 'text-gray-500 dark:text-gray-400',
    lineHeight: 'leading-4',
  },
  badge: {
    size: 'text-xs',
    weight: 'font-medium',
    lineHeight: 'leading-4',
  },
} as const;

/**
 * Tokens de animação para tickets
 */
export const ticketAnimations = {
  item: {
    hidden: { opacity: 0, y: 8, scale: 0.98 },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.2,
        ease: 'easeOut'
      }
    },
    hover: {
      scale: 1.01,
      transition: { duration: 0.15 }
    },
    tap: {
      scale: 0.98,
      transition: { duration: 0.1 }
    }
  },
  container: {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
        delayChildren: 0.1
      }
    }
  },
  badge: {
    initial: { scale: 0.9, opacity: 0 },
    animate: {
      scale: 1,
      opacity: 1,
      transition: { duration: 0.2 }
    }
  }
} as const;

/**
 * Função utilitária para obter configuração de prioridade
 */
export const getPriorityConfig = (priority: string): PriorityConfig => {
  return priorityTokens[priority] || priorityTokens['Normal'];
};

/**
 * Função utilitária para obter configuração de status
 */
export const getStatusConfig = (status: string): StatusConfig => {
  return statusTokens[status] || statusTokens['novo'];
};

/**
 * Classes CSS customizadas para tickets
 */
export const ticketClasses = {
  card: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm hover:shadow-md transition-all duration-200',
  item: 'p-3 rounded-md border border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-all duration-200',
  itemActive: 'active:scale-[0.98] transition-transform',
  badge: 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium transition-all duration-200',
  icon: 'flex-shrink-0 transition-colors duration-200',
  truncate: 'truncate overflow-hidden',
  lineClamp: 'line-clamp-2 overflow-hidden',
} as const;
