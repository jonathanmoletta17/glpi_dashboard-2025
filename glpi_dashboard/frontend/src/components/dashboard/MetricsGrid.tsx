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
  icon: React.ComponentType<any>;
  color: string;
  bgColor: string;
  status?: TicketStatus;
  onClick?: (status: TicketStatus) => void;
}

const StatusCard = React.memo<StatusCardProps>(
  ({ title, value, icon: Icon, color, bgColor, status, onClick }) => {
    const formattedValue = useMemo(() => value.toLocaleString(), [value]);
    const isClickable = status && onClick;

    const handleClick = useCallback(() => {
      if (isClickable) {
        onClick(status);
      }
    }, [isClickable, onClick, status]);

    // Mapear status para classes de gradiente
    const getGradientClass = (status?: TicketStatus) => {
      switch (status) {
        case 'novo': return 'metrics-card-new';
        case 'progresso': return 'metrics-card-progress';
        case 'pendente': return 'metrics-card-pending';
        case 'resolvido': return 'metrics-card-resolved';
        default: return 'bg-white';
      }
    };

    return (
      <motion.div
        className={`relative overflow-hidden rounded-xl border border-gray-200/50 p-6 transition-all duration-300 bg-white shadow-lg ${
          isClickable ? 'hover:shadow-2xl cursor-pointer hover:-translate-y-2' : ''
        }`}
        onClick={handleClick}
        whileHover={isClickable ? { scale: 1.03, y: -6 } : {}}
        whileTap={isClickable ? { scale: 0.97 } : {}}
      >
        <div className='flex items-center justify-between'>
          <div>
            <p className='text-sm font-semibold text-gray-700 mb-2'>{title}</p>
            <p className={`text-3xl font-bold ${color}`}>{formattedValue}</p>
          </div>
          <div className={`p-4 rounded-xl ${bgColor}`}>
            <Icon className={`w-7 h-7 ${color}`} />
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
    const cards = useMemo(() => {
      if (!metrics) return [];

      return [
        {
          title: 'Novos',
          value: metrics.novos || 0,
          status: 'novo' as TicketStatus,
          icon: AlertTriangle,
          color: 'text-blue-600',
          bgColor: 'bg-blue-50',
          onClick: onFilterByStatus,
        },
        {
          title: 'Em Progresso',
          value: metrics.progresso || 0,
          status: 'progresso' as TicketStatus,
          icon: Activity,
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-50',
          onClick: onFilterByStatus,
        },
        {
          title: 'Pendentes',
          value: metrics.pendentes || 0,
          status: 'pendente' as TicketStatus,
          icon: Clock,
          color: 'text-orange-600',
          bgColor: 'bg-orange-50',
          onClick: onFilterByStatus,
        },
        {
          title: 'Resolvidos',
          value: metrics.resolvidos || 0,
          status: 'resolvido' as TicketStatus,
          icon: CheckCircle,
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          onClick: onFilterByStatus,
        },
      ];
    }, [metrics, onFilterByStatus]);

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
        {cards.map((card) => (
          <motion.div key={`metrics-${card.status}`} variants={itemVariants}>
            <StatusCard
              title={card.title}
              value={card.value}
              status={card.status}
              icon={card.icon}
              color={card.color}
              bgColor={card.bgColor}
              onClick={card.onClick}
            />
          </motion.div>
        ))}
      </motion.div>
    );
  }
);

MetricsGrid.displayName = 'MetricsGrid';