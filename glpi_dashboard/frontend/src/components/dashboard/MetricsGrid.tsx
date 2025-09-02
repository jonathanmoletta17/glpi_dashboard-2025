import React, { useEffect, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import { StatusCard } from './StatusCard';
import { MetricsData, TicketStatus } from '@/types';
import { Ticket, Clock, AlertTriangle, CheckCircle } from 'lucide-react';


import { useThrottledCallback } from '../../hooks/useDebounce';

interface MetricsGridProps {
  metrics: MetricsData;
  onFilterByStatus?: (status: TicketStatus) => void;
  className?: string;
}



// Variantes de animação movidas para fora do componente
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.02,
      delayChildren: 0,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.1,
      ease: 'easeOut' as const,
    },
  },
} as const;

export const MetricsGrid = React.memo<MetricsGridProps>(function MetricsGrid({
  metrics,
  onFilterByStatus,
  className,
}) {


  // Componente renderizado com métricas válidas

  // Verificação de segurança
  if (!metrics) {
    // console.log('⚠️ MetricsGrid - Metrics é null/undefined, mostrando skeleton')
    return (
      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4'>
        {[...Array(4)].map((_, i) => (
          <div key={i} className='h-32 figma-glass-card animate-pulse rounded-lg' />
        ))}
      </div>
    );
  }

  // Callbacks memoizados para os cliques com throttle
  const handleNewClickImmediate = useCallback(() => {
    onFilterByStatus?.('new');
  }, [onFilterByStatus]);

  const handleProgressClickImmediate = useCallback(() => {
    onFilterByStatus?.('progress');
  }, [onFilterByStatus]);

  const handlePendingClickImmediate = useCallback(() => {
    onFilterByStatus?.('pending');
  }, [onFilterByStatus]);

  const handleResolvedClickImmediate = useCallback(() => {
    onFilterByStatus?.('resolved');
  }, [onFilterByStatus]);

  // Throttled versions to prevent rapid clicks
  const handleNewClick = useThrottledCallback(handleNewClickImmediate, 500);
  const handleProgressClick = useThrottledCallback(handleProgressClickImmediate, 500);
  const handlePendingClick = useThrottledCallback(handlePendingClickImmediate, 500);
  const handleResolvedClick = useThrottledCallback(handleResolvedClickImmediate, 500);

  // Configuração dos cards de métricas memoizada
  const metricCards = useMemo(() => {
    const cards = [
      {
        title: 'Novos',
        value: metrics.novos || 0,
        status: 'new' as const,
        icon: Ticket,

        onClick: handleNewClick,
      },
      {
        title: 'Em Progresso',
        value: metrics.progresso || 0,
        status: 'progress' as const,
        icon: Clock,

        onClick: handleProgressClick,
      },
      {
        title: 'Pendentes',
        value: metrics.pendentes || 0,
        status: 'pending' as const,
        icon: AlertTriangle,

        onClick: handlePendingClick,
      },
      {
        title: 'Resolvidos',
        value: metrics.resolvidos || 0,
        status: 'resolved' as const,
        icon: CheckCircle,

        onClick: handleResolvedClick,
      },
    ];

    return cards;
  }, [metrics, handleNewClick, handleProgressClick, handlePendingClick, handleResolvedClick]);

  return (
    <motion.div
      variants={containerVariants}
      initial='hidden'
      animate='visible'
      className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 ${className || ''}`}
    >
      {metricCards.map(card => (
        <motion.div key={`metrics-${card.status}`} variants={itemVariants}>
          <StatusCard
            title={card.title}
            value={card.value}
            status={card.status}
            icon={card.icon}
            className='h-full cursor-pointer'
            onClick={card.onClick}
          />
        </motion.div>
      ))}
    </motion.div>
  );
});
