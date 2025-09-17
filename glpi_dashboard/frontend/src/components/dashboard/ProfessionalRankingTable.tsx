import React, { useRef, useEffect, useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn, formatNumber } from '@/lib/utils';
import { Trophy, Medal, Award, Star, BarChart3 } from 'lucide-react';
import { TechnicianRanking } from '@/types';
import { listPresets, cardPresets } from '@/utils/animations';
import {
  getRankingPositionStyle,
  getLevelStyle,
  RANKING_VARIANTS,
  RANKING_ANIMATIONS
} from '@/utils/rankingStyles';

interface ProfessionalRankingTableProps {
  data: TechnicianRanking[];
  title?: string;
  className?: string;
  variant?: 'default' | 'compact' | 'expanded';
  isLoading?: boolean;
  filters?: {
    start_date?: string;
    end_date?: string;
    level?: string;
    limit?: number;
  };
}

// Usando variantes de animação da biblioteca centralizada

// Componente TechnicianCard profissional
const ProfessionalTechnicianCard = React.memo<{
  technician: TechnicianRanking;
  index: number;
}>(({ technician, index }) => {
  const position = index + 1;
  // const isTopThree = position <= 3; // Removido pois não está sendo usado

  const formattedName = useMemo(() => {
    const nameParts = technician.name.split(' ');
    const firstName = nameParts[0] || '';
    const lastNameInitial =
      nameParts.length > 1 ? nameParts[nameParts.length - 1].charAt(0).toUpperCase() + '.' : '';
    return `${firstName} ${lastNameInitial}`.trim();
  }, [technician.name]);

  const getPositionIcon = () => {
    switch (position) {
      case 1:
        return <Trophy className='h-4 w-4' />;
      case 2:
        return <Medal className='h-4 w-4' />;
      case 3:
        return <Award className='h-4 w-4' />;
      default:
        return <Star className='h-4 w-4' />;
    }
  };

  const positionStyle = getRankingPositionStyle(position);

  const levelStyle = getLevelStyle(technician.level || 'N1');

  return (
    <motion.div variants={listPresets.item} whileHover={{ scale: 1.02, y: -2 }} className='flex-shrink-0 w-48'>
      <Card
        className={cn(
          'h-full border-2 dark:border-gray-700',
          positionStyle.bg,
          positionStyle.border
        )}
      >
        <CardContent className='p-3'>
          <div className='flex items-center justify-between mb-2'>
            <div className='flex items-center gap-2'>
              <div
                className={cn(
                  'p-1.5 rounded-md bg-white dark:bg-gray-700 shadow-sm border dark:border-gray-600',
                  positionStyle.icon
                )}
              >
                {getPositionIcon()}
              </div>
              <span className={cn('text-base font-bold', positionStyle.text)}>
                #{position}
              </span>
            </div>
            <Badge
              variant='outline'
              className={cn(
                'text-xs px-2 py-1 font-semibold dark:border-gray-600',
                levelStyle.bg,
                levelStyle.text,
                levelStyle.border
              )}
            >
              {technician.level || 'N1'}
            </Badge>
          </div>

          <div className='space-y-2'>
            <div>
              <h3 className='font-semibold text-gray-900 dark:text-white text-sm mb-1'>
                {formattedName}
              </h3>
              <p className='text-xs text-gray-600 dark:text-gray-400 truncate'>{technician.name}</p>
            </div>

            <div className='grid grid-cols-2 gap-2'>
              <div className='bg-white/60 dark:bg-gray-800/60 rounded-md p-1.5 border border-white/80 dark:border-gray-700/80'>
                <div className='text-xs text-gray-600 dark:text-gray-400 mb-1'>Total</div>
                <div className='text-base font-bold text-gray-900 dark:text-white'>
                  {technician.total_tickets ? formatNumber(technician.total_tickets) : '-'}
                </div>
              </div>
              <div className='bg-white/60 dark:bg-gray-800/60 rounded-md p-1.5 border border-white/80 dark:border-gray-700/80'>
                <div className='text-xs text-gray-600 dark:text-gray-400 mb-1'>Resolvidos</div>
                <div className='text-base font-bold text-green-700 dark:text-green-400'>
                  {technician.resolved_tickets ? formatNumber(technician.resolved_tickets) : '-'}
                </div>
              </div>
            </div>

            {(() => {
              // Garantir que avg_resolution_time seja um número válido maior que 0
              const avgTime = Number(technician.avg_resolution_time);
              if (avgTime && avgTime > 0 && !isNaN(avgTime)) {
                return (
                  <div className='bg-white/60 dark:bg-gray-800/60 rounded-md p-1.5 border border-white/80 dark:border-gray-700/80'>
                    <div className='text-xs text-gray-600 dark:text-gray-400 mb-1'>Tempo Médio</div>
                    <div className='text-sm font-semibold text-gray-900 dark:text-white'>
                      {avgTime}h
                    </div>
                  </div>
                );
              }
              return null;
            })()}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
});

ProfessionalTechnicianCard.displayName = 'ProfessionalTechnicianCard';

export const ProfessionalRankingTable = React.memo<ProfessionalRankingTableProps>(
  ({
    data,
    title = 'Ranking de Técnicos',
    className,
    isLoading = false,
    filters,
  }) => {
    const scrollContainerRef = useRef<HTMLDivElement>(null);

    // Lógica de dados - incluir todos os técnicos, mesmo com dados zerados
    const topTechnicians = useMemo(() => {
      return [...data]
        .filter(tech => tech && tech.name) // Apenas verificar se existe e tem nome
        .sort((a, b) => (b.total_tickets || 0) - (a.total_tickets || 0));
    }, [data]);

    const levelStats = useMemo(() => {
      return topTechnicians.reduce(
        (acc, tech) => {
          const level = tech.level || 'Outros';
          acc[level] = (acc[level] || 0) + 1;
          return acc;
        },
        {} as Record<string, number>
      );
    }, [topTechnicians]);

    const handleWheel = useCallback((e: WheelEvent) => {
      e.preventDefault();
      const container = scrollContainerRef.current;
      if (container) {
        container.scrollLeft += e.deltaY;
      }
    }, []);

    useEffect(() => {
      const container = scrollContainerRef.current;
      if (!container) return;

      container.addEventListener('wheel', handleWheel, { passive: false });
      return () => {
        container.removeEventListener('wheel', handleWheel);
      };
    }, [handleWheel]);

    return (
      <Card className={cn('h-full bg-transparent border-0 shadow-none', className)}>
        <CardHeader className='pb-1 px-3 pt-3'>
          <div className='flex items-center justify-between'>
            <div className='flex flex-col gap-1'>
              <CardTitle className='text-base font-semibold flex items-center gap-2 text-gray-900 dark:text-white'>
                <div className='p-1.5 rounded-md bg-white dark:bg-gray-700 shadow-sm border border-gray-200 dark:border-gray-600'>
                  <BarChart3 className='h-4 w-4 text-gray-600 dark:text-gray-300' />
                </div>
                {title}
              </CardTitle>
              {filters && (filters.start_date || filters.end_date || filters.level) && (
                <div className='flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400'>
                  <span className='font-medium'>Filtros aplicados:</span>
                  {filters.start_date && (
                    <Badge
                      variant='outline'
                      className='text-xs px-2 py-1 bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300'
                    >
                      De: {new Date(filters.start_date).toLocaleDateString('pt-BR')}
                    </Badge>
                  )}
                  {filters.end_date && (
                    <Badge
                      variant='outline'
                      className='text-xs px-2 py-1 bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300'
                    >
                      Até: {new Date(filters.end_date).toLocaleDateString('pt-BR')}
                    </Badge>
                  )}
                  {filters.level && (
                    <Badge
                      variant='outline'
                      className='text-xs px-2 py-1 bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300'
                    >
                      Nível: {filters.level}
                    </Badge>
                  )}
                </div>
              )}
            </div>
            <div className='flex items-center gap-2'>
              {Object.entries(levelStats).map(([level, count]) => {
                const getLevelConfig = (level: string) => {
                  // Cores neutras para todos os níveis
                  return 'bg-gray-50 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-600';
                };

                return (
                  <Badge
                    key={`ranking-level-${level}`}
                    variant='outline'
                    className={cn('text-xs px-2 py-1 font-medium', getLevelConfig(level))}
                  >
                    {level}: {count}
                  </Badge>
                );
              })}
            </div>
          </div>
        </CardHeader>

        <CardContent className='px-3 pb-3 pt-0 flex-1 flex flex-col'>
          {isLoading ? (
            <div className='flex flex-col items-center justify-center p-8 space-y-4'>
              <div className='relative'>
                <div className='animate-spin rounded-full h-12 w-12 border-4 border-gray-200'></div>
                <div className='animate-spin rounded-full h-12 w-12 border-4 border-gray-600 border-t-transparent absolute top-0 left-0'></div>
              </div>
              <div className='text-center'>
                <h3 className='text-lg font-semibold text-gray-900 dark:text-white mb-2'>
                  Carregando Ranking
                </h3>
                <p className='text-sm text-gray-600 dark:text-gray-400 mb-2'>
                  Processando dados do GLPI...
                </p>
                <p className='text-xs text-gray-500 dark:text-gray-500'>
                  Isso pode levar até 2 minutos na primeira vez
                </p>
              </div>
              <div className='w-full max-w-xs bg-gray-200 dark:bg-gray-700 rounded-full h-2'>
                <div
                  className='bg-gray-600 dark:bg-gray-500 h-2 rounded-full animate-pulse'
                  style={{ width: '60%' }}
                ></div>
              </div>
            </div>
          ) : topTechnicians.length === 0 ? (
            <div className='flex flex-col items-center justify-center p-8 text-center'>
              <div className='p-3 rounded-full bg-gray-100 dark:bg-gray-800 mb-4'>
                <BarChart3 className='h-6 w-6 text-gray-400 dark:text-gray-500' />
              </div>
              <h3 className='text-sm font-medium text-gray-900 dark:text-white mb-1'>
                Nenhum técnico encontrado
              </h3>
              <p className='text-xs text-gray-500 dark:text-gray-400'>
                Não há dados de técnicos disponíveis no momento.
              </p>
            </div>
          ) : (
            <motion.div
              variants={listPresets.container}
              initial='hidden'
              animate='visible'
              className='flex-1 flex flex-col'
            >
              <div
                ref={scrollContainerRef}
                className='flex w-full flex-1 overflow-x-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent px-2 space-x-3'
              >
                {topTechnicians.map((technician, index) => (
                  <ProfessionalTechnicianCard
                    key={`${technician.id}-${index}`}
                    technician={technician}
                    index={index}
                  />
                ))}
              </div>
            </motion.div>
          )}
        </CardContent>
      </Card>
    );
  }
);

ProfessionalRankingTable.displayName = 'ProfessionalRankingTable';
