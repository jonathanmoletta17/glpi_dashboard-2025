import React, { useEffect, useMemo, Suspense, useState } from 'react';
import { motion } from 'framer-motion';
import { MetricsGrid } from './MetricsGrid';
import { LevelMetricsGrid } from './LevelMetricsGrid';
import { PremiumLevelCard } from './PremiumLevelCard';
import { ProfessionalTicketsList } from './ProfessionalTicketsList';
import { ProfessionalRankingTable } from './ProfessionalRankingTable';

// Componentes lazy centralizados
import {
  LazyNewTicketsList,
  LazyRankingTable,
  ListSkeleton,
  TableSkeleton,
} from '../LazyComponents';

import { RESPONSIVE_GRID_CLASSES, RESPONSIVE_SPACING } from '../../utils/responsive';

import { Card, CardContent, CardHeader } from '@/components/ui/card';

import { MetricsData, TicketStatus, SystemStatus, TechnicianRanking, Ticket } from '@/types';
import { cn } from '@/lib/utils';
import { SkipLink } from '../accessibility/VisuallyHidden';

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
  // Debug logs removidos para produção
  // console.log('🔍 ModernDashboard - technicianRanking recebido:', technicianRanking);
  // console.log('🔍 ModernDashboard - technicianRanking length:', technicianRanking?.length);
  // console.log('🔍 ModernDashboard - primeiro técnico:', technicianRanking?.[0]);

  // Memoizar dados do ranking processados
  const processedRankingData = useMemo(() => {
    if (!technicianRanking || !Array.isArray(technicianRanking)) {
      console.warn(
        '⚠️ ModernDashboard - technicianRanking não é um array válido:',
        technicianRanking
      );
      return [];
    }

    const result = technicianRanking.map(tech => {
      const processed = {
        id: tech.id || String(tech.name),
        name: tech.name || tech.nome || 'Técnico',
        level: tech.level || 'N1',
        total: tech.total_tickets || 0,
        total_tickets: tech.total_tickets || 0,
        resolved_tickets: tech.resolved_tickets || 0,
        pending_tickets: tech.pending_tickets || 0,
        avg_resolution_time: tech.avg_resolution_time || 0,
        rank: tech.rank || 0,
      };
      // console.log('🔍 ModernDashboard - processando técnico:', tech, '-> resultado:', processed);
      return processed;
    });

    // console.log('✅ ModernDashboard - processedRankingData final:', result);
    return result;
  }, [technicianRanking]);

  // Loading state
  if (isLoading) {
    return (
      <main
        className='space-y-6 p-6 min-h-screen'
        role='main'
        aria-label='Carregando dashboard GLPI'
        aria-busy='true'
      >
        <SkipLink href='#main-content'>Pular para conteúdo principal</SkipLink>

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
        <section aria-label='Carregando métricas gerais'>
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4'>
            {[...Array(4)].map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        </section>

        {/* Charts skeleton */}
        <section aria-label='Carregando gráficos e dados'>
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
        </section>
      </main>
    );
  }

  return (
    <motion.main
      variants={containerVariants}
      initial='hidden'
      animate='visible'
      className={cn('dashboard-fullscreen-container px-6', className)}
      role='main'
      aria-label='Dashboard GLPI'
      id='main-content'
    >
      <SkipLink href='#metrics-section'>Pular para métricas</SkipLink>
      <SkipLink href='#levels-section'>Pular para níveis</SkipLink>
      <SkipLink href='#ranking-section'>Pular para ranking</SkipLink>

      <h1 className='sr-only'>Dashboard de Tickets GLPI</h1>

      {/* Cards de métricas gerais no topo - OTIMIZADO */}
      <motion.section
        variants={itemVariants}
        className='w-full mt-4 mb-4'
        id='metrics-section'
        data-dashboard-section='metrics'
        aria-labelledby='metrics-heading'
      >
        <h2 id='metrics-heading' className='sr-only'>
          Métricas Gerais de Tickets
        </h2>
        <MetricsGrid metrics={metrics} onFilterByStatus={onFilterByStatus} isLoading={isLoading} />
      </motion.section>

      {/* Layout principal com métricas por nível e tickets novos - ESTRUTURA PREMIUM OTIMIZADA */}
      <section
        className='glpi-grid-levels glpi-animate-fade-up mb-4'
        id='levels-section'
        data-dashboard-section='levels'
        aria-labelledby='levels-heading'
      >
        <h2 id='levels-heading' className='sr-only'>
          Métricas por Nível de Suporte
        </h2>

        {/* Coluna 1 - N1 e N3 */}
        <div className='space-y-4 glpi-animate-slide-right' style={{ animationDelay: '100ms' }}>
          <div
            className='glpi-card-premium glpi-glass-premium glpi-hover-lift'
            role='region'
            aria-labelledby='n1-heading'
          >
            <h3 id='n1-heading' className='sr-only'>
              Métricas Nível N1
            </h3>
            <PremiumLevelCard
              title='Nível N1'
              totalTickets={levelMetrics?.n1?.total || 0}
              stats={[
                {
                  label: 'Novos',
                  value: levelMetrics?.n1?.novos || 0,
                  color: 'text-gray-900 dark:text-white',
                  bgColor: 'bg-gray-50 dark:bg-gray-800/50',
                },
                {
                  label: 'Em Progresso',
                  value: levelMetrics?.n1?.progresso || 0,
                  color: 'text-gray-900 dark:text-white',
                  bgColor: 'bg-gray-50 dark:bg-gray-800/50',
                },
                {
                  label: 'Pendentes',
                  value: levelMetrics?.n1?.pendentes || 0,
                  color: 'text-gray-900 dark:text-white',
                  bgColor: 'bg-gray-50 dark:bg-gray-800/50',
                },
                {
                  label: 'Resolvidos',
                  value: levelMetrics?.n1?.resolvidos || 0,
                  color: 'text-gray-900 dark:text-white',
                  bgColor: 'bg-gray-50 dark:bg-gray-800/50',
                },
              ]}
            />
          </div>

          <div
            className='glpi-card-premium glpi-glass-premium glpi-hover-lift'
            role='region'
            aria-labelledby='n3-heading'
          >
            <h3 id='n3-heading' className='sr-only'>
              Métricas Nível N3
            </h3>
            <PremiumLevelCard
              title='Nível N3'
              totalTickets={levelMetrics?.n3?.total || 0}
              stats={[
                {
                  label: 'Novos',
                  value: levelMetrics?.n3?.novos || 0,
                  color: 'text-gray-900 dark:text-white',
                  bgColor: 'bg-gray-50 dark:bg-gray-800/50',
                },
                {
                  label: 'Em Progresso',
                  value: levelMetrics?.n3?.progresso || 0,
                  color: 'text-gray-900 dark:text-white',
                  bgColor: 'bg-gray-50 dark:bg-gray-800/50',
                },
                {
                  label: 'Pendentes',
                  value: levelMetrics?.n3?.pendentes || 0,
                  color: 'text-gray-900 dark:text-white',
                  bgColor: 'bg-gray-50 dark:bg-gray-800/50',
                },
                {
                  label: 'Resolvidos',
                  value: levelMetrics?.n3?.resolvidos || 0,
                  color: 'text-gray-900 dark:text-white',
                  bgColor: 'bg-gray-50 dark:bg-gray-800/50',
                },
              ]}
            />
          </div>
        </div>

        {/* Coluna 2 - N2 e N4 */}
        <div className='space-y-4 glpi-animate-slide-right' style={{ animationDelay: '200ms' }}>
          <div
            className='glpi-card-premium glpi-glass-premium glpi-hover-lift'
            role='region'
            aria-labelledby='n2-heading'
          >
            <h3 id='n2-heading' className='sr-only'>
              Métricas Nível N2
            </h3>
            <PremiumLevelCard
              title='Nível N2'
              totalTickets={levelMetrics?.n2?.total || 0}
              stats={[
                {
                  label: 'Novos',
                  value: levelMetrics?.n2?.novos || 0,
                  color: 'text-gray-900 dark:text-white',
                  bgColor: 'bg-gray-50 dark:bg-gray-800/50',
                },
                {
                  label: 'Em Progresso',
                  value: levelMetrics?.n2?.progresso || 0,
                  color: 'text-gray-900 dark:text-white',
                  bgColor: 'bg-gray-50 dark:bg-gray-800/50',
                },
                {
                  label: 'Pendentes',
                  value: levelMetrics?.n2?.pendentes || 0,
                  color: 'text-gray-900 dark:text-white',
                  bgColor: 'bg-gray-50 dark:bg-gray-800/50',
                },
                {
                  label: 'Resolvidos',
                  value: levelMetrics?.n2?.resolvidos || 0,
                  color: 'text-gray-900 dark:text-white',
                  bgColor: 'bg-gray-50 dark:bg-gray-800/50',
                },
              ]}
            />
          </div>

          <div
            className='glpi-card-premium glpi-glass-premium glpi-hover-lift'
            role='region'
            aria-labelledby='n4-heading'
          >
            <h3 id='n4-heading' className='sr-only'>
              Métricas Nível N4
            </h3>
            <PremiumLevelCard
              title='Nível N4'
              totalTickets={levelMetrics?.n4?.total || 0}
              stats={[
                {
                  label: 'Novos',
                  value: levelMetrics?.n4?.novos || 0,
                  color: 'text-gray-900 dark:text-white',
                  bgColor: 'bg-gray-50 dark:bg-gray-800/50',
                },
                {
                  label: 'Em Progresso',
                  value: levelMetrics?.n4?.progresso || 0,
                  color: 'text-gray-900 dark:text-white',
                  bgColor: 'bg-gray-50 dark:bg-gray-800/50',
                },
                {
                  label: 'Pendentes',
                  value: levelMetrics?.n4?.pendentes || 0,
                  color: 'text-gray-900 dark:text-white',
                  bgColor: 'bg-gray-50 dark:bg-gray-800/50',
                },
                {
                  label: 'Resolvidos',
                  value: levelMetrics?.n4?.resolvidos || 0,
                  color: 'text-gray-900 dark:text-white',
                  bgColor: 'bg-gray-50 dark:bg-gray-800/50',
                },
              ]}
            />
          </div>
        </div>

        {/* Coluna 3 - TicketsCard */}
        <div className='glpi-animate-slide-right' style={{ animationDelay: '300ms' }}>
          <div
            className='glpi-card-premium glpi-glass-premium glpi-hover-lift h-full'
            role='region'
            aria-labelledby='tickets-heading'
          >
            <h3 id='tickets-heading' className='sr-only'>
              Lista de Tickets Recentes
            </h3>
            <ProfessionalTicketsList className='h-full' limit={6} onTicketClick={onTicketClick} />
          </div>
        </div>
      </section>

      {/* Layout inferior com ranking */}
      <section
        className='grid grid-cols-1 gap-4'
        id='ranking-section'
        data-dashboard-section='ranking'
        aria-labelledby='ranking-heading'
      >
        {/* Ranking de técnicos */}
        <motion.div variants={itemVariants} className='w-full'>
          <div
            className='glpi-card-premium glpi-glass-premium glpi-hover-lift h-full'
            role='region'
            aria-labelledby='ranking-heading'
          >
            <h2 id='ranking-heading' className='sr-only'>
              Ranking de Técnicos
            </h2>
            <ProfessionalRankingTable
              data={processedRankingData}
              title='Ranking de Técnicos'
              className='w-full h-full'
              filters={filters}
            />
          </div>
        </motion.div>
      </section>
    </motion.main>
  );
});
