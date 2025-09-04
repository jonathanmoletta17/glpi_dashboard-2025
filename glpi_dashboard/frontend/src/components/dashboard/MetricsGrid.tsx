import React, { useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Activity, Clock, CheckCircle } from 'lucide-react';
import { MetricsData, TicketStatus } from '../../types';

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
    const formattedValue = useMemo(() => value.toLocaleString(), [value]);
    const isClickable = onClick;

    const handleClick = useCallback(() => {
      if (isClickable) {
        onClick();
      }
    }, [isClickable, onClick]);

    return (
      <motion.div
        className={`relative overflow-hidden rounded-xl border border-gray-200/50 p-6 transition-all duration-300 shadow-lg ${className} ${
          isClickable ? 'hover:shadow-2xl cursor-pointer hover:-translate-y-2' : ''
        }`}
        onClick={handleClick}
        whileHover={isClickable ? { scale: 1.03, y: -6 } : {}}
        whileTap={isClickable ? { scale: 0.97 } : {}}
      >
        <div className='flex items-center justify-between'>
          <div>
            <p className='text-sm font-semibold text-gray-700 mb-2'>{title}</p>
            <p className='text-3xl font-bold'>{formattedValue}</p>
          </div>
          <div className='p-4 rounded-xl'>
            <Icon className='w-7 h-7' />
          </div>
        </div>
      </motion.div>
    );
  }
);

StatusCard.displayName = 'StatusCard';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3,
    },
  },
};

export const MetricsGrid = React.memo<MetricsGridProps>(
  ({ metrics, onFilterByStatus, isLoading = false, className = '' }) => {
    const cardsData = useMemo(() => [
       {
         title: 'Novos',
         value: metrics?.novos || 0,
         status: 'novo' as TicketStatus,
         icon: AlertTriangle,
         className: 'metrics-card-new status-new',
         onClick: () => onFilterByStatus?.('novo')
       },
       {
         title: 'Em Progresso',
         value: metrics?.progresso || 0,
         status: 'progresso' as TicketStatus,
         icon: Activity,
         className: 'metrics-card-progress status-progress',
         onClick: () => onFilterByStatus?.('progresso')
       },
       {
         title: 'Pendentes',
         value: metrics?.pendentes || 0,
         status: 'pendente' as TicketStatus,
         icon: Clock,
         className: 'metrics-card-pending status-pending',
         onClick: () => onFilterByStatus?.('pendente')
       },
       {
         title: 'Resolvidos',
         value: metrics?.resolvidos || 0,
         status: 'resolvido' as TicketStatus,
         icon: CheckCircle,
         className: 'metrics-card-resolved status-resolved',
         onClick: () => onFilterByStatus?.('resolvido')
       }
     ], [metrics, onFilterByStatus]);

    if (isLoading) {
      return (
        <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 ${className}`}>
          {Array.from({ length: 4 }).map((_, index) => (
            <div
              key={index}
              className='bg-white rounded-xl shadow-sm border border-gray-200 p-6 animate-pulse'
            >
              <div className='flex items-center justify-between'>
                <div>
                  <div className='h-4 bg-gray-200 rounded w-16 mb-2'></div>
                  <div className='h-8 bg-gray-200 rounded w-12'></div>
                </div>
                <div className='p-3 rounded-lg bg-gray-100'>
                  <div className='w-6 h-6 bg-gray-200 rounded'></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      );
    }

    return (
      <motion.div
        className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 ${className}`}
        variants={containerVariants}
        initial='hidden'
        animate='visible'
      >
        {cardsData.map((card) => (
          <motion.div key={`metrics-${card.status}`} variants={itemVariants}>
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
