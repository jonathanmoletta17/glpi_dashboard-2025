import React, { useMemo } from 'react';
// import { Users, Minus } from 'lucide-react';
import { MetricsData, LevelMetrics } from '../types';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';

interface LevelsSectionProps {
  metrics: MetricsData;
}

interface LevelCardProps {
  level: string;
  data: LevelMetrics;
  resolucaoRate: number;
}

// Função auxiliar para calcular taxa de resolução
const calculateResolutionRate = (data: LevelMetrics): number => {
  const total = data.novos + data.progresso + data.pendentes + data.resolvidos;
  return total > 0 ? Math.round((data.resolvidos / total) * 100) : 0;
};

const LevelCard = React.memo<LevelCardProps>(({ level, data, resolucaoRate }) => {
  // Memoizar o estilo da barra de progresso
  const progressBarStyle = useMemo(
    () => ({
      width: `${resolucaoRate}%`,
    }),
    [resolucaoRate]
  );

  return (
    <Card className='col-span-3 md:col-span-6 lg:col-span-3'>
      <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
        <CardTitle className='text-lg font-medium text-gray-700 dark:text-gray-300'>
          Nível {level}
        </CardTitle>
        <span className='text-xs text-green-600 dark:text-green-400'>
          {resolucaoRate}% Resolução
        </span>
      </CardHeader>
      <CardContent>
        {/* Metrics Grid */}
        <div className='grid grid-cols-2 gap-3 mb-4'>
          <div className='text-center'>
            <div className='text-2xl font-bold text-blue-600 dark:text-blue-400'>{data.novos}</div>
            <div className='text-sm text-gray-600 dark:text-gray-400'>Novos</div>
          </div>
          <div className='text-center'>
            <div className='text-2xl font-bold text-yellow-600 dark:text-yellow-400'>
              {data.progresso}
            </div>
            <div className='text-sm text-gray-600 dark:text-gray-400'>Progresso</div>
          </div>
          <div className='text-center'>
            <div className='text-2xl font-bold text-orange-600 dark:text-orange-400'>
              {data.pendentes}
            </div>
            <div className='text-sm text-gray-600 dark:text-gray-400'>Pendentes</div>
          </div>
          <div className='text-center'>
            <div className='text-2xl font-bold text-green-600 dark:text-green-400'>
              {data.resolvidos}
            </div>
            <div className='text-sm text-gray-600 dark:text-gray-400'>Resolvidos</div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className='w-full bg-gray-200 rounded-full h-1.5'>
          <div
            className='bg-green-500 h-1.5 rounded-full transition-all duration-300'
            style={progressBarStyle}
          ></div>
        </div>
      </CardContent>
    </Card>
  );
});

export const LevelsSection = React.memo<LevelsSectionProps>(({ metrics }) => {
  // Verificação de segurança para evitar erros
  if (!metrics || !metrics.niveis) {
    return (
      <div className='space-y-6'>
        <div className='text-center text-gray-500'>Carregando métricas por nível...</div>
      </div>
    );
  }

  // Memoizar as taxas de resolução calculadas
  const resolutionRates = useMemo(
    () => ({
      n1: calculateResolutionRate(metrics.niveis.n1),
      n2: calculateResolutionRate(metrics.niveis.n2),
      n3: calculateResolutionRate(metrics.niveis.n3),
      n4: calculateResolutionRate(metrics.niveis.n4),
    }),
    [metrics.niveis]
  );

  return (
    <section className='w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-8'>
      <div className='col-span-12'>
        <h2 className='text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6'>
          Níveis de Atendimento
        </h2>
        <div className='grid grid-cols-12 gap-4'>
          <LevelCard level='1' data={metrics.niveis.n1} resolucaoRate={resolutionRates.n1} />
          <LevelCard level='2' data={metrics.niveis.n2} resolucaoRate={resolutionRates.n2} />
          <LevelCard level='3' data={metrics.niveis.n3} resolucaoRate={resolutionRates.n3} />
          <LevelCard level='4' data={metrics.niveis.n4} resolucaoRate={resolutionRates.n4} />
        </div>
      </div>
    </section>
  );
});
