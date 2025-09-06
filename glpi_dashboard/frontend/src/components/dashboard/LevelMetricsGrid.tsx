import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Users, Clock, AlertCircle, CheckCircle, TrendingUp, BarChart3 } from 'lucide-react';
import {
  RESPONSIVE_GRID_CLASSES,
  RESPONSIVE_CONTAINER,
  RESPONSIVE_SPACING,
} from '../../utils/responsive';
import { MetricsData } from '@/types';
import { cn } from '@/lib/utils';

interface LevelMetricsGridProps {
  metrics?: MetricsData;
  className?: string;
}

const levelConfig = {
  n1: {
    title: 'Nível N1',
    color: 'level-accent-n1',
    bgColor: 'level-badge level-badge-n1',
    textColor: '',
  },
  n2: {
    title: 'Nível N2',
    color: 'level-accent-n2',
    bgColor: 'level-badge level-badge-n2',
    textColor: '',
  },
  n3: {
    title: 'Nível N3',
    color: 'level-accent-n3',
    bgColor: 'level-badge level-badge-n3',
    textColor: '',
  },
  n4: {
    title: 'Nível N4',
    color: 'level-accent-n4',
    bgColor: 'level-badge level-badge-n4',
    textColor: '',
  },
};

const statusConfig = {
  novos: {
    icon: AlertCircle,
    color: 'text-gray-900 dark:text-gray-100',
    bgColor: 'status-new',
    iconColor: '',
    label: 'Novos',
  },
  progresso: {
    icon: Clock,
    color: 'text-gray-900 dark:text-gray-100',
    bgColor: 'status-progress',
    iconColor: '',
    label: 'Em Progresso',
  },
  pendentes: {
    icon: Users,
    color: 'text-gray-900 dark:text-gray-100',
    bgColor: 'status-pending',
    iconColor: '',
    label: 'Pendentes',
  },
  resolvidos: {
    icon: CheckCircle,
    color: 'text-gray-900 dark:text-gray-100',
    bgColor: 'status-resolved',
    iconColor: '',
    label: 'Resolvidos',
  },
};

// Variantes de animação movidas para fora do componente
const itemVariants = {
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

const statusVariants = {
  hover: {
    scale: 1.05,
    transition: {
      duration: 0.2,
      ease: 'easeInOut' as const,
    },
  },
} as const;

// Componente StatusItem memoizado
const StatusItem = React.memo<{
  status: string;
  statusConf: (typeof statusConfig)[keyof typeof statusConfig];
  value: number | undefined;
}>(function StatusItem({ status, statusConf, value }) {
  const Icon = statusConf.icon;

  return (
    <motion.div
      key={`status-item-${status}`}
      variants={statusVariants}
      whileHover='hover'
      className='flex items-center justify-between p-4 rounded-lg bg-white/80 backdrop-blur-sm min-h-[60px] border border-gray-100/50 dark:border-gray-800/50 dark:bg-white/5 cursor-pointer'
    >
      <div className='flex items-center gap-3'>
        <motion.div
          className={`p-2 rounded-lg ${statusConf.bgColor} shadow-sm`}
          whileHover={{ scale: 1.1 }}
          transition={{ duration: 0.2 }}
        >
          <Icon className={`h-4 w-4 ${statusConf.iconColor}`} />
        </motion.div>
        <span className='text-sm font-medium text-gray-700 dark:text-gray-300'>
          {statusConf.label}
        </span>
      </div>
      <motion.span
        className={`text-lg font-bold ${statusConf.color} tabular-nums`}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.6, ease: 'easeOut', delay: 0.2 }}
      >
        {value || 0}
      </motion.span>
    </motion.div>
  );
});

// Componente LevelCard memoizado
const LevelCard = React.memo<{
  level: string;
  levelData: any;
  config: (typeof levelConfig)[keyof typeof levelConfig];
}>(function LevelCard({ level, levelData, config }) {
  const total = useMemo(() => {
    return Object.values(levelData).reduce((sum: number, value) => sum + (Number(value) || 0), 0);
  }, [levelData]);

  return (
    <motion.div
      key={`level-motion-${level}`}
      variants={itemVariants}
      initial='hidden'
      animate='visible'
      whileHover='hover'
      className='h-full flex cursor-pointer'
    >
      <Card className='bg-white/80 backdrop-blur-sm border border-white/90 dark:bg.white/5 dark:border-white/10 border-0 shadow-none h-full w-full flex flex-col relative overflow-hidden rounded-lg'>
        <CardHeader className='pb-3 px-4 pt-4 flex-shrink-0'>
          <div className='flex items-center justify-between relative z-10'>
            <CardTitle className='text-lg font-semibold flex items-center gap-3'>
              <motion.div
                variants={iconVariants}
                className={`p-2 rounded-lg bg-gradient-to-br shadow-sm ${config.color}`}
              >
                <TrendingUp className='h-5 w-5 text-white' />
              </motion.div>
              <span className='whitespace-nowrap'>{config.title}</span>
            </CardTitle>
            <motion.div whileHover={{ scale: 1.05 }} transition={{ duration: 0.2 }}>
              <Badge
                variant='outline'
                className={`${config.bgColor} ${config.textColor} border-0 text-sm px-3 py-1.5 font-bold`}
              >
                {total}
              </Badge>
            </motion.div>
          </div>
        </CardHeader>

        <CardContent className='px-4 pb-4 flex-1 relative z-10'>
          <div className='grid grid-cols-1 sm:grid-cols-2 gap-3 w-full h-full'>
            {Object.entries(statusConfig).map(([status, statusConf]) => {
              const value = levelData[status as keyof typeof levelData];

              return (
                <StatusItem
                  key={`level-${level}-${status}`}
                  status={status}
                  statusConf={statusConf}
                  value={value}
                />
              );
            })}
          </div>
        </CardContent>

        {/* Gradient Background */}
        <div className={cn('absolute inset-0 bg-gradient-to-br opacity-5', config.color)} />

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

export const LevelMetricsGrid = React.memo<LevelMetricsGridProps>(function LevelMetricsGrid({
  metrics,
  className,
}) {
  // Verificação de segurança para evitar erros
  if (!metrics || !metrics.niveis) {
    return (
      <Card
        className={cn(
          'bg-white/80 backdrop-blur-sm border border-white/90 dark:bg-white/5 dark:border-white/10 h-full shadow-none rounded-lg',
          className
        )}
      >
        <CardContent className='flex items-center justify-center h-48'>
          <div className='text-center'>
            <div className='text-sm text-gray-600 mb-2'>
              <BarChart3 className='h-6 w-6 mx-auto' />
            </div>
            <div className='text-sm text-gray-600'>Carregando métricas por nível...</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Memoizar as entradas dos níveis
  const levelEntries = useMemo(() => {
    return Object.entries(metrics.niveis || {});
  }, [metrics.niveis]);

  return (
    <div className={cn('h-full flex flex-col overflow-hidden', className)}>
      <div
        className={`${RESPONSIVE_GRID_CLASSES.levelMetrics} ${RESPONSIVE_SPACING.gap.lg} h-full overflow-hidden p-1`}
      >
        {levelEntries.map(([levelKey, levelData]) => {
          const key = levelKey.toLowerCase() as keyof typeof levelConfig;
          const config = levelConfig[key] || levelConfig.n1;

          return (
            <LevelCard
              key={`level-card-${key}`}
              level={String(levelKey)}
              levelData={levelData}
              config={config}
            />
          );
        })}
      </div>
    </div>
  );
});
