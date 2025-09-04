/* ==========================================================================
   RANKING TABLE - EXEMPLO DE REFATORAÇÃO
   ========================================================================== */

/*
 * Este arquivo demonstra como aplicar a refatoração CSS no componente RankingTable.
 *
 * PRINCIPAIS MUDANÇAS:
 * 1. Substituição de classes utilitárias por classes semânticas BEM
 * 2. Importação do CSS refatorado
 * 3. Simplificação da estrutura HTML
 * 4. Melhoria na organização do código
 */

import React, { useRef, useEffect, useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn, formatNumber } from '@/lib/utils';
import { Trophy, Medal, Award, Star, Users, Zap, Shield, Wrench, Settings } from 'lucide-react';
import { TechnicianRanking } from '@/types';

// CSS refatorado removido - usando apenas Tailwind CSS

interface RankingTableProps {
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

// Variantes de animação movidas para fora do componente
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
} as const;

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
    y: -2,
    scale: 1.01,
    zIndex: 5,
    transition: {
      duration: 0.3,
      ease: 'easeOut' as const,
    },
  },
} as const;

// Componente TechnicianCard memoizado
const TechnicianCard = React.memo<{
  technician: TechnicianRanking;
  index: number;
}>(function TechnicianCard({ technician, index }) {
  const levelStyle = getLevelStyle(technician.level);
  const position = index + 1;
  const isTopThree = position <= 3;

  const formattedName = useMemo(() => {
    const nameParts = technician.name.split(' ');
    const firstName = nameParts[0] || '';
    const lastNameInitial =
      nameParts.length > 1 ? nameParts[nameParts.length - 1].charAt(0).toUpperCase() + '.' : '';
    return `${firstName} ${lastNameInitial}`.trim();
  }, [technician.name]);

  const performanceIndicators = useMemo(() => {
    return Array.from({ length: Math.min(3, Math.max(1, 4 - Math.ceil(position / 3))) });
  }, [position]);

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

  const getPositionColor = () => {
    switch (position) {
      case 1:
        return 'ranking-pos-1';
      case 2:
        return 'ranking-pos-2';
      case 3:
        return 'ranking-pos-3';
      default:
        return 'ranking-pos-default';
    }
  };

  return (
    <motion.div
      variants={cardVariants}
      whileHover='hover'
      className='flex-shrink-0 w-48 h-full'
    >
      <div className='bg-white/90 backdrop-blur-sm border border-white/90 shadow-lg rounded-xl p-4 h-full flex flex-col justify-between hover:shadow-xl transition-all duration-300 dark:bg-white/10 dark:border-white/20'>
        {/* Header com posição e nível */}
        <div className='flex items-center justify-between mb-3'>
          <div className={cn(
            'flex items-center justify-center w-6 h-6 rounded-full text-white text-xs font-bold',
            getPositionColor()
          )}>
            {getPositionIcon()}
          </div>
          <div className='flex items-center gap-1'>
            <div className={cn(
              'p-1 rounded-full',
              levelStyle.iconBg
            )}>
              {levelStyle.icon && <levelStyle.icon className={cn('h-3 w-3', levelStyle.iconColor)} />}
            </div>
            <Badge className={cn(
              'text-xs font-medium text-white border-0 px-2 py-0.5',
              levelStyle.accentColor
            )}>
              {technician.level}
            </Badge>
          </div>
        </div>

        {/* Nome do técnico */}
        <div className='text-center mb-3'>
          <h4 className='font-medium text-gray-900 dark:text-white text-sm leading-tight'>
            {formattedName}
          </h4>
        </div>

        {/* Estatísticas */}
        <div className='text-center'>
          <div className='text-2xl font-bold text-gray-900 dark:text-white mb-1'>
            {formatNumber(technician.total_tickets || 0)}
          </div>
          <div className='text-xs text-gray-600 dark:text-gray-400 mb-2'>
            tickets resolvidos
          </div>

          {/* Indicadores de performance */}
          <div className='flex justify-center gap-1'>
            {performanceIndicators.map((_, i) => (
              <div
                key={i}
                className={cn(
                  'w-1.5 h-1.5 rounded-full',
                  isTopThree ? 'ranking-dot-top' : 'ranking-dot-default'
                )}
              />
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
});

// Função getLevelStyle permanece a mesma
function getLevelStyle(level?: string) {
  const styles = {
    N1: {
      iconBg: 'bg-emerald-100',
      iconColor: 'text-emerald-600',
      textColor: 'text-emerald-600',
      accentColor: 'ranking-level-n1',
      icon: Zap,
    },
    N2: {
      iconBg: 'bg-blue-100',
      iconColor: 'text-blue-600',
      textColor: 'text-blue-600',
      accentColor: 'ranking-level-n2',
      icon: Shield,
    },
    N3: {
      iconBg: 'bg-purple-100',
      iconColor: 'text-purple-600',
      textColor: 'text-purple-600',
      accentColor: 'ranking-level-n3',
      icon: Wrench,
    },
    N4: {
      iconBg: 'bg-orange-100',
      iconColor: 'text-orange-600',
      textColor: 'text-orange-600',
      accentColor: 'ranking-level-n4',
      icon: Settings,
    },
  };

  return (
    styles[level as keyof typeof styles] || {
      iconBg: 'bg-gray-100',
      iconColor: 'text-gray-600',
      textColor: 'text-gray-600',
      accentColor: 'bg-gray-500',
      icon: Star,
    }
  );
}

// Componente principal refatorado

// Componente principal refatorado
export const RankingTable = React.memo<RankingTableProps>(function RankingTable({
  data,
  title = 'Ranking de Técnicos',
  className,
  variant = 'default',
  isLoading = false,
  filters,
}) {
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Lógica de dados permanece a mesma
  const topTechnicians = useMemo(() => {
    return [...data].sort((a, b) => (b.total_tickets || 0) - (a.total_tickets || 0));
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

  // Classes CSS refatoradas
  const cardClasses = cn(
    'ranking-card', // Classe semântica principal
    {
      'ranking-card--compact': variant === 'compact',
      'ranking-card--expanded': variant === 'expanded',
      'ranking-card--loading': isLoading,
    },
    className
  );

  return (
    <Card className={cn(
      'bg-white/80 backdrop-blur-sm border border-white/90 shadow-sm dark:bg-white/5 dark:border-white/10',
      'h-full flex flex-col',
      className
    )}>
      <CardHeader className='pb-3'>
        <div className='flex items-center justify-between'>
          <div className='flex flex-col gap-2'>
            <CardTitle className='text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2'>
              <div className='p-2 rounded-xl bg-gradient-to-br from-slate-500 to-slate-600 shadow-lg'>
                <Users className='h-5 w-5 text-white' />
              </div>
              Ranking de Técnicos
            </CardTitle>
            {filters && (filters.start_date || filters.end_date || filters.level) && (
              <div className='flex items-center gap-2 text-xs text-gray-600'>
                <span className='font-medium'>Filtros aplicados:</span>
                {filters.start_date && (
                  <Badge variant='outline' className='text-xs px-2 py-1'>
                    De: {new Date(filters.start_date).toLocaleDateString('pt-BR')}
                  </Badge>
                )}
                {filters.end_date && (
                  <Badge variant='outline' className='text-xs px-2 py-1'>
                    Até: {new Date(filters.end_date).toLocaleDateString('pt-BR')}
                  </Badge>
                )}
                {filters.level && (
                  <Badge variant='outline' className='text-xs px-2 py-1'>
                    Nível: {filters.level}
                  </Badge>
                )}
              </div>
            )}
          </div>
          <div className='flex items-center gap-2'>
            {Object.entries(levelStats).map(([level, count]) => {
              const style = getLevelStyle(level);
              return (
                <Badge
                  key={`ranking-level-${level}`}
                  className={cn(
                    'text-xs px-2 py-1 border text-white font-medium',
                    style.accentColor
                  )}
                >
                  {level}: {count}
                </Badge>
              );
            })}
          </div>
        </div>
      </CardHeader>

      <CardContent className='px-4 pb-4 pt-0 flex-1 flex flex-col'>
        <motion.div
          variants={containerVariants}
          initial='hidden'
          animate='visible'
          className='flex-1 flex flex-col'
        >
          <div
            ref={scrollContainerRef}
            className='flex w-full flex-1 overflow-x-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent px-2 space-x-3'
          >
            {topTechnicians.map((technician, index) => (
              <TechnicianCard
                key={`${technician.id}-${index}`}
                technician={technician}
                index={index}
              />
            ))}
          </div>
        </motion.div>
      </CardContent>
    </Card>
  );
});

RankingTable.displayName = 'RankingTable';

export default RankingTable;
