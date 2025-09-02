import React, { useEffect, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import { StatusCard } from './StatusCard';
import { MetricsData, TicketStatus } from '@/types';
import { Ticket, Clock, AlertTriangle, CheckCircle } from 'lucide-react';
import { useThrottledCallback } from '../../hooks/useDebounce';

/**
 * MetricsGrid Refatorado - Melhorias Implementadas:
 * 
 * 1. CSS Refatorado:
 *    - Substituição de classes utilitárias por classes semânticas BEM
 *    - Variáveis CSS para cores, espaçamentos e animações
 *    - Skeleton loading com estilos próprios (sem figma-glass-card)
 *    - Suporte aprimorado a tema escuro
 *    - Media queries para responsividade
 *    - Melhor acessibilidade (prefers-reduced-motion, prefers-contrast)
 * 
 * 2. Estrutura HTML Simplificada:
 *    - Classes BEM descritivas e semânticas
 *    - Redução significativa de classes Tailwind inline
 *    - Melhor separação de responsabilidades
 * 
 * 3. Performance:
 *    - CSS otimizado com variáveis reutilizáveis
 *    - Animações mais eficientes
 *    - Menor bundle size
 */

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
  // Verificação de segurança - Skeleton loading com classes BEM
  if (!metrics) {
    return (
      <div className={`metrics-grid__skeleton ${className || ''}`}>
        {[...Array(4)].map((_, i) => (
          <div key={`skeleton-${i}`} className='metrics-grid__skeleton-item' />
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
      className={`metrics-grid ${className || ''}`}
    >
      {metricCards.map(card => (
        <motion.div 
          key={`metrics-${card.status}`} 
          variants={itemVariants}
          className='metrics-grid__item'
        >
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