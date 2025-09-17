import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { BarChart3, AlertCircle, Clock, Users, CheckCircle } from 'lucide-react';
import { VisuallyHidden } from '@/components/accessibility/VisuallyHidden';

interface LevelCardProps {
  title: string;
  totalTickets: number;
  stats: Array<{
    label: string;
    value: number;
    color: string;
    bgColor: string;
  }>;
}

const statusIcons = {
  Novos: AlertCircle,
  'Em Progresso': Clock,
  Pendentes: Users,
  Resolvidos: CheckCircle,
};

const getStatusConfig = (label: string) => {
  switch (label) {
    case 'Novos':
      return {
        iconColor: 'text-blue-500 dark:text-blue-400',
        textColor: 'text-gray-900 dark:text-white',
        bgClass: 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700',
      };
    case 'Em Progresso':
      return {
        iconColor: 'text-amber-500 dark:text-amber-400',
        textColor: 'text-gray-900 dark:text-white',
        bgClass: 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700',
      };
    case 'Pendentes':
      return {
        iconColor: 'text-orange-500 dark:text-orange-400',
        textColor: 'text-gray-900 dark:text-white',
        bgClass: 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700',
      };
    case 'Resolvidos':
      return {
        iconColor: 'text-emerald-500 dark:text-emerald-400',
        textColor: 'text-gray-900 dark:text-white',
        bgClass: 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700',
      };
    default:
      return {
        iconColor: 'text-gray-500 dark:text-gray-400',
        textColor: 'text-gray-900 dark:text-white',
        bgClass: 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700',
      };
  }
};

export const PremiumLevelCard: React.FC<LevelCardProps> = ({ title, totalTickets, stats }) => {
  const getLevelConfig = (title: string) => {
    // Cores neutras para todos os níveis
    return {
      bgClass: 'bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900',
      textClass: 'text-gray-900 dark:text-white',
      accentColor: 'text-gray-600 dark:text-gray-400',
    };
  };

  const levelConfig = getLevelConfig(title);
  const cardId = `level-card-${title.toLowerCase().replace(/\s+/g, '-')}`;
  const totalStatsValue = stats.reduce((sum, stat) => sum + stat.value, 0);

  return (
    <Card
      className={`h-full bg-transparent border border-gray-200 dark:border-gray-700 shadow-sm ${levelConfig.bgClass}`}
      role="region"
      aria-labelledby={`${cardId}-title`}
      aria-describedby={`${cardId}-description`}
    >
      <CardHeader className='pb-3 px-5 pt-5'>
        <div className='flex items-center justify-between'>
          <CardTitle
            id={`${cardId}-title`}
            className={`text-lg font-semibold flex items-center gap-3 ${levelConfig.textClass}`}
          >
            <div
              className='p-2 rounded-lg bg-white dark:bg-gray-800 shadow-sm border border-gray-200 dark:border-gray-600'
              aria-hidden="true"
            >
              <BarChart3 className={`h-5 w-5 ${levelConfig.accentColor}`} />
            </div>
            <span className='whitespace-nowrap'>{title}</span>
          </CardTitle>
          <Badge
            variant='outline'
            className={`bg-white dark:bg-gray-800 ${levelConfig.textClass} border-gray-300 dark:border-gray-600 text-sm px-3 py-1.5 font-bold shadow-sm`}
            aria-label={`Total de tickets: ${totalTickets.toLocaleString()}`}
          >
            {totalTickets.toLocaleString()}
          </Badge>
        </div>
        <VisuallyHidden>
          <div id={`${cardId}-description`}>
            Cartão de métricas para {title} com {totalTickets} tickets totais distribuídos em {stats.length} categorias de status
          </div>
        </VisuallyHidden>
      </CardHeader>

      <CardContent className='px-5 pb-5'>
        <div
          className='grid grid-cols-1 sm:grid-cols-2 gap-3'
          role="list"
          aria-label={`Estatísticas detalhadas para ${title}`}
        >
          {stats.map((stat, index) => {
            const Icon = statusIcons[stat.label as keyof typeof statusIcons] || AlertCircle;
            const statusConfig = getStatusConfig(stat.label);
            const percentage = totalStatsValue > 0 ? ((stat.value / totalStatsValue) * 100).toFixed(1) : '0';

            return (
              <div
                key={index}
                className={`flex items-center justify-between p-4 rounded-lg ${statusConfig.bgClass} min-h-[56px] border transition-all duration-200 hover:shadow-md hover:scale-[1.02] focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-offset-2`}
                role="listitem"
                tabIndex={0}
                aria-label={`${stat.label}: ${stat.value.toLocaleString()} tickets (${percentage}% do total)`}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    // Pode adicionar ação de clique aqui se necessário
                  }
                }}
              >
                <div className='flex items-center gap-3'>
                  <div
                    className='p-2 rounded-lg bg-white dark:bg-gray-800 shadow-sm border border-gray-200 dark:border-gray-600'
                    aria-hidden="true"
                  >
                    <Icon className={`h-4 w-4 ${statusConfig.iconColor}`} />
                  </div>
                  <span className='text-sm font-medium text-gray-600 dark:text-gray-400'>
                    {stat.label}
                  </span>
                </div>
                <div className='text-right'>
                  <span className={`text-lg font-bold ${statusConfig.textColor} tabular-nums block`}>
                    {stat.value.toLocaleString()}
                  </span>
                  <VisuallyHidden>
                    <span aria-label={`${percentage} por cento do total`}>
                      ({percentage}%)
                    </span>
                  </VisuallyHidden>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};
