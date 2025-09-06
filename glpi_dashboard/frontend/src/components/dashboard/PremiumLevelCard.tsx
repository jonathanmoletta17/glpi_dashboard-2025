import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { BarChart3, AlertCircle, Clock, Users, CheckCircle } from 'lucide-react';

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
  'Novos': AlertCircle,
  'Em Progresso': Clock,
  'Pendentes': Users,
  'Resolvidos': CheckCircle,
};

const getStatusConfig = (label: string) => {
  switch (label) {
    case 'Novos':
      return { 
        iconColor: 'text-blue-500 dark:text-blue-400', 
        textColor: 'text-gray-900 dark:text-white',
        bgClass: 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700'
      };
    case 'Em Progresso':
      return { 
        iconColor: 'text-amber-500 dark:text-amber-400', 
        textColor: 'text-gray-900 dark:text-white',
        bgClass: 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700'
      };
    case 'Pendentes':
      return { 
        iconColor: 'text-orange-500 dark:text-orange-400', 
        textColor: 'text-gray-900 dark:text-white',
        bgClass: 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700'
      };
    case 'Resolvidos':
      return { 
        iconColor: 'text-emerald-500 dark:text-emerald-400', 
        textColor: 'text-gray-900 dark:text-white',
        bgClass: 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700'
      };
    default:
      return { 
        iconColor: 'text-gray-500 dark:text-gray-400', 
        textColor: 'text-gray-900 dark:text-white',
        bgClass: 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700'
      };
  }
};

export const PremiumLevelCard: React.FC<LevelCardProps> = ({
  title,
  totalTickets,
  stats,
}) => {
  const getLevelConfig = (title: string) => {
    switch (title) {
      case 'Nível N1':
        return { 
          bgClass: 'bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900', 
          textClass: 'text-gray-900 dark:text-white',
          accentColor: 'text-emerald-600 dark:text-emerald-400'
        };
      case 'Nível N2':
        return { 
          bgClass: 'bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900', 
          textClass: 'text-gray-900 dark:text-white',
          accentColor: 'text-blue-600 dark:text-blue-400'
        };
      case 'Nível N3':
        return { 
          bgClass: 'bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900', 
          textClass: 'text-gray-900 dark:text-white',
          accentColor: 'text-purple-600 dark:text-purple-400'
        };
      case 'Nível N4':
        return { 
          bgClass: 'bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900', 
          textClass: 'text-gray-900 dark:text-white',
          accentColor: 'text-orange-600 dark:text-orange-400'
        };
      default:
        return { 
          bgClass: 'bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900', 
          textClass: 'text-gray-900 dark:text-white',
          accentColor: 'text-gray-600 dark:text-gray-400'
        };
    }
  };

  const levelConfig = getLevelConfig(title);

  return (
    <Card className={`h-full bg-transparent border border-gray-200 dark:border-gray-700 shadow-sm ${levelConfig.bgClass}`}>
      <CardHeader className="pb-3 px-5 pt-5">
        <div className="flex items-center justify-between">
          <CardTitle className={`text-lg font-semibold flex items-center gap-3 ${levelConfig.textClass}`}>
            <div className="p-2 rounded-lg bg-white dark:bg-gray-800 shadow-sm border border-gray-200 dark:border-gray-600">
              <BarChart3 className={`h-5 w-5 ${levelConfig.accentColor}`} />
            </div>
            <span className="whitespace-nowrap">{title}</span>
          </CardTitle>
          <Badge
            variant="outline"
            className={`bg-white dark:bg-gray-800 ${levelConfig.textClass} border-gray-300 dark:border-gray-600 text-sm px-3 py-1.5 font-bold shadow-sm`}
          >
            {totalTickets.toLocaleString()}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="px-5 pb-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {stats.map((stat, index) => {
            const Icon = statusIcons[stat.label as keyof typeof statusIcons] || AlertCircle;
            const statusConfig = getStatusConfig(stat.label);
            
            return (
              <div
                key={index}
                className={`flex items-center justify-between p-4 rounded-lg ${statusConfig.bgClass} min-h-[56px] border transition-all duration-200 hover:shadow-md hover:scale-[1.02]`}
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-white dark:bg-gray-800 shadow-sm border border-gray-200 dark:border-gray-600">
                    <Icon className={`h-4 w-4 ${statusConfig.iconColor}`} />
                  </div>
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    {stat.label}
                  </span>
                </div>
                <span className={`text-lg font-bold ${statusConfig.textColor} tabular-nums`}>
                  {stat.value.toLocaleString()}
                </span>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};
