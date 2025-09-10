import React, { memo, useMemo } from 'react';

interface TechnicianData {
  id: string | number;
  nome?: string;
  name?: string;
  total_tickets?: number;
  resolvidos?: number;
  pendentes?: number;
  progresso?: number;
}

interface TechnicianRankingProps {
  data: TechnicianData[];
}

const TechnicianRanking = memo(({ data }: TechnicianRankingProps) => {
  const memoizedRanking = useMemo(() => {
    return data.map((tech, index) => {
      const rankBadgeColor = (() => {
        switch (index) {
          case 0:
            return 'bg-slate-600';
          case 1:
            return 'bg-slate-500';
          case 2:
            return 'bg-slate-700';
          default:
            return 'bg-slate-800';
        }
      })();

      return {
        ...tech,
        index,
        rankBadgeColor,
        displayName: tech.nome || tech.name,
        ticketCount: tech.total_tickets || 0,
      };
    });
  }, [data]);

  return (
    <section
      className='space-y-4 max-h-96 overflow-y-auto'
      role='region'
      aria-label='Ranking de técnicos'
      tabIndex={0}
    >
      <h3 className='sr-only'>Lista de técnicos ordenados por desempenho</h3>
      {memoizedRanking.map(tech => (
        <article
          key={tech.id}
          className='flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
          role='listitem'
          tabIndex={0}
          aria-labelledby={`tech-name-${tech.id}`}
          aria-describedby={`tech-stats-${tech.id}`}
        >
          <div className='flex items-center space-x-4'>
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold text-white ${tech.rankBadgeColor}`}
              role='img'
              aria-label={`Posição ${tech.index + 1} no ranking`}
            >
              {tech.index + 1}
            </div>
            <div>
              <div id={`tech-name-${tech.id}`} className='font-medium text-gray-900'>
                {tech.displayName}
              </div>
              <div className='text-sm text-gray-500'>Técnico de Suporte</div>
              <div
                id={`tech-stats-${tech.id}`}
                className='text-xs text-gray-400 mt-1'
                aria-label={`Estatísticas: ${tech.resolvidos || 0} tickets resolvidos, ${tech.pendentes || 0} pendentes, ${tech.progresso || 0} em progresso`}
              >
                Resolvidos: {tech.resolvidos || 0} | Pendentes: {tech.pendentes || 0} | Em
                Progresso: {tech.progresso || 0}
              </div>
            </div>
          </div>
          <div className='text-right'>
            <div
              className='text-lg font-semibold text-gray-900'
              aria-label={`Total de ${tech.ticketCount} tickets`}
            >
              {tech.ticketCount}
            </div>
            <div className='text-sm text-gray-500'>total</div>
          </div>
        </article>
      ))}
    </section>
  );
});

TechnicianRanking.displayName = 'TechnicianRanking';

export default TechnicianRanking;
