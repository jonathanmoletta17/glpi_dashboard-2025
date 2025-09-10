import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { Minus, AlertCircle, CheckCircle, Clock, XCircle, type LucideIcon } from 'lucide-react';
import type { LevelMetrics, PerformanceMetrics } from '../types/api';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Formatação de números para padrão brasileiro
export function formatNumber(value: number, options?: Intl.NumberFormatOptions): string {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
    ...options,
  }).format(value);
}

// Formatação de porcentagem
export function formatPercentage(value: number, decimals: number = 1): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value / 100);
}

// Formatação de moeda
export function formatCurrency(value: number, currency: string = 'BRL'): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency,
  }).format(value);
}

// Formatação de data
export function formatDate(
  date: Date | string,
  format: 'short' | 'long' | 'time' = 'short'
): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;

  if (isNaN(dateObj.getTime())) {
    return 'Data inválida';
  }

  switch (format) {
    case 'short':
      return dateObj.toLocaleDateString('pt-BR');
    case 'long':
      return dateObj.toLocaleDateString('pt-BR', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    case 'time':
      return dateObj.toLocaleString('pt-BR');
    default:
      return dateObj.toLocaleDateString('pt-BR');
  }
}

// Cores baseadas no status - Sistema de Cores GLPI Dashboard
export function getStatusColor(status: string): string {
  const s = (status || '').toString().toLowerCase();
  const colors: Record<string, string> = {
    // Tickets com melhor contraste para modo escuro
    new: 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-200 border-blue-200 dark:border-blue-700',
    novo: 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-200 border-blue-200 dark:border-blue-700',
    progress:
      'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-200 border-yellow-200 dark:border-yellow-700',
    progresso:
      'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-200 border-yellow-200 dark:border-yellow-700',
    pending:
      'bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-200 border-orange-200 dark:border-orange-700',
    pendente:
      'bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-200 border-orange-200 dark:border-orange-700',
    resolved:
      'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-200 border-green-200 dark:border-green-700',
    resolvido:
      'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-200 border-green-200 dark:border-green-700',
    fechado:
      'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-200 border-green-200 dark:border-green-700',

    // Estados operacionais com melhor contraste
    online:
      'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-200 border-green-200 dark:border-green-700',
    offline:
      'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-200 border-red-200 dark:border-red-700',
    maintenance:
      'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-200 border-yellow-200 dark:border-yellow-700',
  };
  return (
    colors[s] ||
    'bg-gray-100 text-gray-800 dark:bg-gray-900/40 dark:text-gray-200 border-gray-200 dark:border-gray-700'
  );
}

// Ícones baseados no status
export function getStatusIcon(status: string): LucideIcon {
  const icons = {
    new: AlertCircle,
    progress: Clock,
    pending: Clock,
    resolved: CheckCircle,
    online: CheckCircle,
    offline: XCircle,
    maintenance: AlertCircle,
  };
  return icons[status as keyof typeof icons] || AlertCircle;
}

// Formatação de data relativa
export function formatRelativeTime(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);

  if (diffInSeconds < 60) {
    return 'Agora mesmo';
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes} minuto${diffInMinutes > 1 ? 's' : ''} atrás`;
  }

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours} hora${diffInHours > 1 ? 's' : ''} atrás`;
  }

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) {
    return `${diffInDays} dia${diffInDays > 1 ? 's' : ''} atrás`;
  }

  return formatDate(dateObj);
}

// Formatação de duração em milissegundos
export function formatDuration(milliseconds: number): string {
  if (milliseconds < 1000) {
    return `${Math.round(milliseconds)}ms`;
  }

  const seconds = milliseconds / 1000;
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`;
  }

  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);

  if (minutes < 60) {
    return `${minutes}m ${remainingSeconds}s`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  return `${hours}h ${remainingMinutes}m`;
}

// Formatação de status com cores
export function formatStatus(status: string): { text: string; color: string; bgColor: string } {
  const statusMap: Record<string, { text: string; color: string; bgColor: string }> = {
    aberto: { text: 'Aberto', color: 'text-blue-700', bgColor: 'bg-blue-100' },
    fechado: { text: 'Fechado', color: 'text-green-700', bgColor: 'bg-green-100' },
    pendente: { text: 'Pendente', color: 'text-yellow-700', bgColor: 'bg-yellow-100' },
    atrasado: { text: 'Atrasado', color: 'text-red-700', bgColor: 'bg-red-100' },
  };

  return (
    statusMap[status.toLowerCase()] || {
      text: status,
      color: 'text-gray-700',
      bgColor: 'bg-gray-100',
    }
  );
}

// Formatação de tendência
export function getTrendIcon(direction: 'up' | 'down' | 'stable'): LucideIcon {
  const icons = {
    up: CheckCircle,
    down: XCircle,
    stable: Minus,
  };
  return icons[direction] || Minus;
}

export function getTrendColor(direction: 'up' | 'down' | 'stable'): string {
  const colors = {
    up: 'text-green-600 dark:text-green-400',
    down: 'text-red-600 dark:text-red-400',
    stable: 'text-gray-600 dark:text-gray-400',
  };
  return colors[direction] || 'text-gray-600 dark:text-gray-400';
}

// Formatação de texto truncado
export function truncateText(text: string, maxLength: number = 50): string {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength - 3) + '...';
}
