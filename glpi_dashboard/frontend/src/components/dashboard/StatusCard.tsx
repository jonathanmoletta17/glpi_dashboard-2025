import React from 'react';
import { memo, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn, formatNumber, getStatusIcon } from '@/lib/utils';
import { type LucideIcon } from 'lucide-react';


interface StatusCardProps {
  title: string;
  value: number;
  status?: string;

  icon?: LucideIcon;
  className?: string;
  variant?: 'default' | 'compact' | 'detailed' | 'gradient';
  showProgress?: boolean;
  maxValue?: number;
  onClick?: () => void;
}

// Função auxiliar definida fora do componente para evitar recriação
const getStatusGradient = (status?: string) => {
  switch (status) {
    case 'online':
      return 'from-green-500 to-emerald-600';
    case 'offline':
      return 'from-red-500 to-rose-600';
    case 'active':
      return 'from-blue-500 to-cyan-600';
    case 'progress':
      return 'from-yellow-500 to-orange-600';
    case 'pending':
      return 'from-orange-500 to-red-600';
    case 'resolved':
      return 'from-green-500 to-emerald-600';
    default:
      return 'from-gray-500 to-slate-600';
  }
};





// Variantes de animação definidas fora do componente
const cardVariants = {
  hidden: { opacity: 0, y: 20, scale: 0.9 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: 'easeOut' as const,
    },
  },
  hover: {
    y: -8,
    scale: 1.03,
    transition: {
      duration: 0.3,
      ease: 'easeInOut' as const,
    },
  },
} as const;

const iconVariants = {
  hover: {
    scale: 1.2,
    rotate: 10,
    transition: {
      duration: 0.3,
      ease: 'easeInOut' as const,
    },
  },
} as const;

const numberVariants = {
  hidden: { scale: 0 },
  visible: {
    scale: 1,
    transition: {
      duration: 0.6,
      ease: 'easeOut' as const,
      delay: 0.2,
    },
  },
} as const;

export const StatusCard = memo<StatusCardProps>(function StatusCard({
  title,
  value,
  status,
  icon,
  className,
  variant: _ = 'default',
  onClick,
}) {
  // Memoizar ícones para evitar recálculos
  const StatusIcon = useMemo(() => icon || (status ? getStatusIcon(status) : null), [icon, status]);

  // Memoizar gradiente do status
  const statusGradient = useMemo(() => getStatusGradient(status), [status]);

  // Memoizar valor formatado
  const formattedValue = useMemo(() => {
    return formatNumber(value);
  }, [value]);

  // Handler para clique no card
  const handleCardClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onClick?.();
  };

  return (
    <motion.div
      variants={cardVariants}
      initial='hidden'
      animate='visible'
      whileHover='hover'
      className={cn('cursor-pointer', className)}
    >
      <Card
        className='figma-glass-card border-0 shadow-none h-full w-full flex flex-col relative overflow-hidden'
        onClick={handleCardClick}
      >
        {/* Gradient Background */}
        <div className={cn('absolute inset-0 bg-gradient-to-br opacity-5', statusGradient)} />

        {/* Animated Border */}
        <div className='absolute inset-0'>
          <div
            className={cn('absolute inset-0 bg-gradient-to-r opacity-20 blur-sm', statusGradient)}
          />
        </div>

        <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-3 px-4 pt-4 flex-shrink-0 relative z-10'>
          <CardTitle className='figma-subheading uppercase tracking-wide'>{title}</CardTitle>
          {StatusIcon && (
            <motion.div
              variants={iconVariants}
              className={cn('p-2 rounded-xl bg-gradient-to-br shadow-lg', statusGradient)}
            >
              <StatusIcon className='h-5 w-5 text-white' />
            </motion.div>
          )}
        </CardHeader>

        <CardContent className='px-4 pb-4 flex-1 relative z-10'>
          <div className='flex items-center justify-between'>
            <div className='space-y-2'>
              <motion.div variants={numberVariants} className='figma-numeric'>
                {formattedValue}
              </motion.div>


            </div>

            {status && (
              <motion.div whileHover={{ scale: 1.05 }} transition={{ duration: 0.2 }}>
                <Badge
                  className={cn(
                    'capitalize text-xs font-semibold px-3 py-1 border-0 shadow-lg bg-gradient-to-r text-white',
                    statusGradient
                  )}
                >
                  {status}
                </Badge>
              </motion.div>
            )}
          </div>
        </CardContent>

        {/* Shine Effect */}
        <motion.div
          className='absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 opacity-0'
          whileHover={{
            opacity: [0, 1, 0],
            x: [-100, 300],
          }}
          transition={{ duration: 0.6 }}
        />
      </Card>
    </motion.div>
  );
});
