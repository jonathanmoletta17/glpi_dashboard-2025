/**
 * Hook personalizado para formatações complexas
 * Centraliza lógicas de formatação que dependem de estado ou contexto
 */

import { useMemo } from 'react';
import {
  formatNumber,
  formatPercentage,
  formatCurrency,
  formatDate,
  formatRelativeTime,
  formatDuration,
  formatResponseTime,
  formatLargeNumber,
  truncateText,
  getInitials,
  formatPriority,
} from '@/lib/utils';

export interface FormatterOptions {
  locale?: string;
  currency?: string;
  timezone?: string;
  dateFormat?: 'short' | 'medium' | 'long' | 'full';
  numberFormat?: 'decimal' | 'compact' | 'scientific';
}

export const useFormatters = (options: FormatterOptions = {}) => {
  const {
    locale = 'pt-BR',
    currency = 'BRL',
    timezone = 'America/Sao_Paulo',
    dateFormat = 'medium',
    numberFormat = 'decimal',
  } = options;

  // Formatadores memoizados para performance
  const formatters = useMemo(() => {
    return {
      // Formatadores básicos
      number: (value: number) => formatNumber(value),
      percentage: (value: number) => formatPercentage(value),
      currency: (value: number) => formatCurrency(value),

      // Formatadores de data com opções
      date: (date: Date | string) => {
        const dateObj = typeof date === 'string' ? new Date(date) : date;
        return formatDate(dateObj, dateFormat as 'short' | 'long' | 'time');
      },

      relativeTime: (date: Date | string) => {
        const dateObj = typeof date === 'string' ? new Date(date) : date;
        return formatRelativeTime(dateObj);
      },

      // Formatadores específicos do domínio
      duration: (ms: number) => formatDuration(ms),
      responseTime: (ms: number) => formatResponseTime(ms),

      // Formatadores com contexto
      priorityWithColor: (priority: string) => formatPriority(priority),
      nameInitials: (name: string) => getInitials(name),
      largeNumber: (value: number) => formatLargeNumber(value),

      // Formatadores de texto
      truncate: (text: string, maxLength: number = 50) => truncateText(text, maxLength),

      // Formatadores compostos
      ticketSummary: (ticket: {
        id: number;
        title: string;
        priority: string;
        createdAt: Date | string;
        responseTime?: number;
      }) => ({
        id: `#${ticket.id}`,
        title: truncateText(ticket.title, 60),
        priority: formatPriority(ticket.priority),
        createdAt: formatRelativeTime(
          typeof ticket.createdAt === 'string' ? new Date(ticket.createdAt) : ticket.createdAt
        ),
        responseTime: ticket.responseTime ? formatResponseTime(ticket.responseTime) : 'N/A',
      }),

      // Formatador para métricas de dashboard
      dashboardMetric: (metric: {
        value: number;
        change?: number;
        format?: 'number' | 'percentage' | 'currency' | 'duration';
      }) => {
        const { value, change, format: metricFormat = 'number' } = metric;

        let formattedValue: string;
        switch (metricFormat) {
          case 'percentage':
            formattedValue = formatPercentage(value);
            break;
          case 'currency':
            formattedValue = formatCurrency(value);
            break;
          case 'duration':
            formattedValue = formatDuration(value);
            break;
          default:
            formattedValue = formatLargeNumber(value);
        }

        return {
          value: formattedValue,
          change: change !== undefined ? formatPercentage(change) : undefined,
          changeColor:
            change !== undefined
              ? change > 0
                ? 'text-green-600'
                : change < 0
                  ? 'text-red-600'
                  : 'text-gray-600'
              : undefined,
        };
      },

      // Formatador para ranking de técnicos
      technicianRanking: (technician: {
        name: string;
        ticketsResolved: number;
        avgResponseTime: number;
        satisfactionRate: number;
      }) => ({
        name: technician.name,
        initials: getInitials(technician.name),
        ticketsResolved: formatLargeNumber(technician.ticketsResolved),
        avgResponseTime: formatResponseTime(technician.avgResponseTime),
        satisfactionRate: formatPercentage(technician.satisfactionRate),
        satisfactionColor:
          technician.satisfactionRate >= 0.9
            ? 'text-green-600'
            : technician.satisfactionRate >= 0.7
              ? 'text-yellow-600'
              : 'text-red-600',
      }),
    };
  }, [locale, currency, timezone, dateFormat, numberFormat]);

  return formatters;
};

// Hook especializado para formatação de dados de dashboard
export const useDashboardFormatters = () => {
  return useFormatters({
    locale: 'pt-BR',
    currency: 'BRL',
    dateFormat: 'medium',
    numberFormat: 'compact',
  });
};

// Hook especializado para formatação de relatórios
export const useReportFormatters = () => {
  return useFormatters({
    locale: 'pt-BR',
    currency: 'BRL',
    dateFormat: 'full',
    numberFormat: 'decimal',
  });
};

export default useFormatters;
