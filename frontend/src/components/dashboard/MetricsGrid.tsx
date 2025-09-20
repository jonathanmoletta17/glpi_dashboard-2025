import React, { useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Activity, Clock, CheckCircle } from 'lucide-react';
import { MetricsData, TicketStatus } from '../../types';
import { RESPONSIVE_GRID_CLASSES, createSimpleGridClasses } from '@/utils/responsive';
import { gridPresets } from '@/utils/animations';
import { useDashboardFormatters } from '@/hooks/useFormatters';
import { SkeletonMetrics } from '@/utils/loadingUtils';

import { useScreenReaderAnnouncement } from '../accessibility/VisuallyHidden';

interface MetricsGridProps {
  metrics: MetricsData;
  onFilterByStatus?: (status: TicketStatus) => void;
  isLoading?: boolean;
  className?: string;
}

interface StatusCardProps {
  title: string;
  value: number;
  icon: React.ComponentType<{ className?: string }>;
  className: string;
  onClick?: () => void;
}

const StatusCard = React.memo<StatusCardProps>(
  ({ title, value, icon: Icon, className, onClick }) => {
    const { announce } = useScreenReaderAnnouncement();
    const formatters = useDashboardFormatters();
    const formattedValue = useMemo(() => formatters.largeNumber(value), [value, formatters]);
    const isClickable = onClick;

    const handleClick = useCallback(() => {
      if (isClickable) {
        onClick();
        announce(`Filtro aplicado: ${title} com ${value} tickets`);
      }
    }, [isClickable, onClick, announce, title, value]);

    const handleKeyDown = useCallback(
      (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleClick();
        }
      },
      [handleClick]
    );

    return (
      <motion.div
        className={`relative overflow-hidden rounded-xl border border-gray-200/50 dark:border-gray-700/50 p-6 transition-all duration-300 shadow-lg dark:shadow-xl ${className} ${
          isClickable
            ? 'hover:shadow-2xl cursor-pointer hover:-translate-y-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900'
            : ''
        }`}
        onClick={handleClick}
        onKeyDown={isClickable ? handleKeyDown : undefined}
        tabIndex={isClickable ? 0 : undefined}
        role={isClickable ? 'button' : undefined}
        aria-label={isClickable ? `Filtrar por ${title}: ${value} tickets` : undefined}
        aria-describedby={
          isClickable ? `${title.toLowerCase().replace(/\s+/g, '-')}-description` : undefined
        }
        whileHover={isClickable ? { scale: 1.03, y: -6 } : {}}
        whileTap={isClickable ? { scale: 0.97 } : {}}
      >
        <div className='flex items-center justify-between'>
          <div>
            <p className='text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2'>{title}</p>
            <p className='text-3xl font-bold text-gray-900 dark:text-white'>{formattedValue}</p>
            {isClickable && (
              <div
                id={`${title.toLowerCase().replace(/\s+/g, '-')}-description`}
                className='sr-only'
              >
                Clique para filtrar tickets por status {title}
              </div>
            )}
          </div>
          <div className='p-4 rounded-xl' aria-hidden='true'>
            <Icon className='w-7 h-7 text-gray-600 dark:text-gray-400' />
          </div>
        </div>
      </motion.div>
    );
  }
);

StatusCard.displayName = 'StatusCard';

// Usando variantes de animação da biblioteca centralizada

export const MetricsGrid = React.memo<MetricsGridProps>(
  ({ metrics, onFilterByStatus, isLoading = false, className = '' }) => {
    const cardsData = useMemo(
      () => [
        {
          title: 'Novos',
          value: metrics?.novos || 0,
          status: 'novo' as TicketStatus,
          icon: AlertTriangle,
          className: 'metrics-card-new status-new',
          onClick: () => onFilterByStatus?.('novo'),
        },
        {
          title: 'Em Progresso',
          value: metrics?.progresso || 0,
          status: 'progresso' as TicketStatus,
          icon: Activity,
          className: 'metrics-card-progress status-progress',
          onClick: () => onFilterByStatus?.('progresso'),
        },
        {
          title: 'Pendentes',
          value: metrics?.pendentes || 0,
          status: 'pendente' as TicketStatus,
          icon: Clock,
          className: 'metrics-card-pending status-pending',
          onClick: () => onFilterByStatus?.('pendente'),
        },
        {
          title: 'Resolvidos',
          value: metrics?.resolvidos || 0,
          status: 'resolvido' as TicketStatus,
          icon: CheckCircle,
          className: 'metrics-card-resolved status-resolved',
          onClick: () => onFilterByStatus?.('resolvido'),
        },
      ],
      [metrics, onFilterByStatus]
    );

    if (isLoading) {
      return <SkeletonMetrics />;
    }

    const gridClasses = createSimpleGridClasses({
      base: RESPONSIVE_GRID_CLASSES.metricsCards.base,
      mobile: 'grid-cols-1',
      tablet: 'grid-cols-2',
      desktop: 'grid-cols-4',
    });

    return (
      <motion.div
        className={`${gridClasses} ${className}`}
        variants={gridPresets.container}
        initial='hidden'
        animate='visible'
        role='region'
        aria-label='Métricas de tickets por status'
        aria-describedby='metrics-grid-description'
      >
        <div id='metrics-grid-description' className='sr-only'>
          Grade de métricas mostrando contadores de tickets por status. Use as setas do teclado para
          navegar entre os cartões.
        </div>
        {cardsData.map(card => (
          <motion.div key={`metrics-${card.status}`} variants={gridPresets.item}>
            <StatusCard
              title={card.title}
              value={card.value}
              icon={card.icon}
              className={card.className}
              onClick={card.onClick}
            />
          </motion.div>
        ))}
      </motion.div>
    );
  }
);

MetricsGrid.displayName = 'MetricsGrid';
