import React, { useEffect, useMemo, Suspense, useState } from 'react';
import { motion } from 'framer-motion';
import { MetricsGrid } from './MetricsGrid';
import { LevelMetricsGrid } from './LevelMetricsGrid';

// Componentes lazy centralizados
import {
  LazyNewTicketsList,
  LazyRankingTable,
  ListSkeleton,
  TableSkeleton,
} from '../LazyComponents';

import { Card, CardContent, CardHeader } from '@/components/ui/card';


import { MetricsData, TicketStatus, SystemStatus, TechnicianRanking, Ticket } from '@/types';
import { cn } from '@/lib/utils';



interface ModernDashboardProps {
  metrics: MetricsData;
  levelMetrics?: any;
  systemStatus?: SystemStatus | null;
  technicianRanking?: TechnicianRanking[];
  onFilterByStatus?: (status: TicketStatus) => void;
  onTicketClick?: (ticket: Ticket) => void;
  onRefresh?: () => void;
  isLoading?: boolean;
  className?: string;
  filters?: {
    start_date?: string;
    end_date?: string;
    level?: string;
    limit?: number;
  };
}

// Variantes de animação movidas para fora do componente
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.01,
      delayChildren: 0,
    },
  },
} as const;

const itemVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.05,
      ease: 'easeOut' as const,
    },
  },
} as const;

// Componente SkeletonCard memoizado
const SkeletonCard = React.memo(function SkeletonCard() {
  return (
    <Card className='bg-white/80 backdrop-blur-sm border border-white/90 shadow-sm dark:bg-white/5 dark:border-white/10 shadow-none'>
      <CardHeader className='pb-2'>
        <div className='flex items-center justify-between'>
          <div className='h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-20' />
          <div className='h-8 w-8 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse' />
        </div>
      </CardHeader>
      <CardContent>
        <div className='space-y-3'>
          <div className='h-8 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-16' />
          <div className='h-3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-24' />
        </div>
      </CardContent>
    </Card>
  );
});

export const ModernDashboard = React.memo<ModernDashboardProps>(function ModernDashboard({
  metrics,
  levelMetrics,
  systemStatus,
  technicianRanking = [],
  onFilterByStatus,
  onTicketClick,
  isLoading = false,
  className,
  filters,
}) {






  // Debug logs para investigar o problema do ranking zerado
  console.log('🔍 ModernDashboard - technicianRanking recebido:', technicianRanking);
  console.log('🔍 ModernDashboard - technicianRanking length:', technicianRanking?.length);
  console.log('🔍 ModernDashboard - primeiro técnico:', technicianRanking?.[0]);

  // Memoizar dados do ranking processados
  const processedRankingData = useMemo(() => {
    if (!technicianRanking || !Array.isArray(technicianRanking)) {
      console.warn('⚠️ ModernDashboard - technicianRanking não é um array válido:', technicianRanking);
      return [];
    }

    const result = technicianRanking.map(tech => {
      const processed = {
        id: tech.id || String(tech.name),
        name: tech.name || tech.nome || 'Técnico',
        level: tech.level || 'N1',
        total: tech.total_tickets || tech.resolved_tickets || tech.total || 0,
        total_tickets: tech.total_tickets || tech.resolved_tickets || tech.total || 0,
        resolved_tickets: tech.resolved_tickets || 0,
        pending_tickets: tech.pending_tickets || 0,
        avg_resolution_time: tech.avg_resolution_time || 0,
        rank: tech.rank || 0,
      };
      console.log('🔍 ModernDashboard - processando técnico:', tech, '-> resultado:', processed);
      return processed;
    });

    console.log('✅ ModernDashboard - processedRankingData final:', result);
    return result;
  }, [technicianRanking]);

  // Loading state
  if (isLoading) {
    return (
      <div className='space-y-6 p-6 min-h-screen'>
        {/* Header skeleton */}
        <div className='flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4'>
          <div className='space-y-2'>
            <div className='h-8 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-64' />
            <div className='h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-48' />
          </div>
          <div className='flex items-center gap-3'>
            <div className='h-10 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-32' />
            <div className='h-10 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-24' />
          </div>
        </div>

        {/* Metrics skeleton */}
        <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4'>
          {[...Array(4)].map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>

        {/* Charts skeleton */}
        <div className='grid grid-cols-1 xl:grid-cols-3 gap-6'>
          <div className='xl:col-span-2'>
            <Card className='bg-white/80 backdrop-blur-sm border border-white/90 shadow-sm dark:bg-white/5 dark:border-white/10 shadow-none'>
              <CardHeader>
                <div className='h-6 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-40' />
              </CardHeader>
              <CardContent>
                <div className='h-64 bg-gray-200 dark:bg-gray-700 rounded animate-pulse' />
              </CardContent>
            </Card>
          </div>
          <div className='space-y-4'>
            {[...Array(3)].map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      variants={containerVariants}
      initial='hidden'
      animate='visible'
      className={cn(
        'dashboard-fullscreen-container px-6',
        className
      )}
    >
      {/* Cards de métricas gerais no topo */}
      <motion.div variants={itemVariants} className='w-full mt-8 mb-6'>
        <MetricsGrid 
          metrics={metrics} 
          onFilterByStatus={onFilterByStatus}
          isLoading={isLoading}
        />
      </motion.div>

      {/* Layout principal com métricas por nível e tickets novos */}
      <div className='grid grid-cols-1 xl:grid-cols-3 gap-6 mb-6'>
        {/* Métricas por nível de atendimento - ocupando 2 colunas */}
        <motion.div variants={itemVariants} className='xl:col-span-2'>
          <LevelMetricsGrid metrics={metrics} className='h-full' />
        </motion.div>

        {/* Lista de tickets novos - ocupando 1 coluna */}
        <motion.div variants={itemVariants} className='xl:col-span-1'>
          <Suspense fallback={<ListSkeleton />}>
            <LazyNewTicketsList className='h-full' limit={6} onTicketClick={onTicketClick} />
          </Suspense>
        </motion.div>
      </div>

      {/* Layout inferior com ranking */}
      <div className='grid grid-cols-1 gap-6'>
        {/* Ranking de técnicos */}
        <motion.div variants={itemVariants} className='w-full'>
          <Suspense fallback={<TableSkeleton />}>
            <LazyRankingTable
              data={processedRankingData}
              title='Ranking de Técnicos'
              className='w-full h-full'
              filters={filters}
            />
          </Suspense>
        </motion.div>


      </div>


    </motion.div>
  );
});
