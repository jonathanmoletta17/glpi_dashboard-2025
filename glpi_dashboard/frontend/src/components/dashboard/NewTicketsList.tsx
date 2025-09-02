import React, { useState, useEffect, useMemo, useTransition } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AlertCircle, Clock, User, Calendar, RefreshCw, ExternalLink } from 'lucide-react';
import { NewTicket, Ticket } from '@/types';
import { cn, formatRelativeTime, formatDate } from '@/lib/utils';
import { apiService } from '@/services/api';
import { useThrottledCallback } from '@/hooks/useDebounce';
import { useSmartRefresh } from '@/hooks/useSmartRefresh';

interface NewTicketsListProps {
  className?: string;
  limit?: number;
  onTicketClick?: (ticket: Ticket) => void;
}

// Configuração de prioridades movida para fora do componente
const priorityConfig = {
  Crítica: {
    color: 'figma-status-badge-red',
    icon: '🔴',
  },
  'Muito Alta': {
    color: 'figma-status-badge-red',
    icon: '🔴',
  },
  Alta: {
    color: 'figma-priority-badge text-orange-700 dark:text-orange-300',
    icon: '🟠',
  },
  Média: {
    color: 'figma-status-badge-yellow',
    icon: '🟡',
  },
  Baixa: {
    color: 'figma-status-badge-green',
    icon: '🟢',
  },
  'Muito Baixa': {
    color: 'figma-status-badge-blue',
    icon: '🔵',
  },
  Normal: {
    color: 'figma-status-badge-blue',
    icon: '🔵',
  },
};

// Variantes de animação movidas para fora do componente
const itemVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.3,
      ease: 'easeOut' as const,
    },
  },
} as const;

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
} as const;

// Função auxiliar para obter configuração de prioridade
const getPriorityConfig = (priority: string) => {
  return priorityConfig[priority as keyof typeof priorityConfig] || priorityConfig['Normal'];
};



// Componente TicketItem memoizado
const TicketItem = React.memo<{ ticket: NewTicket; index: number; onTicketClick?: (ticket: Ticket) => void }>(({ ticket, onTicketClick }) => {
  const priorityConf = useMemo(() => getPriorityConfig(ticket.priority), [ticket.priority]);
  const formattedDate = useMemo(() => formatDate(ticket.date), [ticket.date]);

  // Função para converter NewTicket para Ticket
  const handleTicketClick = () => {
    if (onTicketClick) {
      const convertedTicket: Ticket = {
        id: ticket.id.toString(),
        title: ticket.title,
        description: ticket.description || '',
        status: 'new',
        priority: ticket.priority.toLowerCase() as any,
        requester: {
          id: '1',
          name: ticket.requester,
          email: '',
        },
        technician: null,
        createdAt: ticket.date,
        updatedAt: ticket.date,
        category: 'Geral',
        subcategory: '',
        location: '',
        urgency: 'medium',
        impact: 'medium',
        source: 'web',
        tags: [],
        attachments: [],
        comments: [],
        timeTracking: {
          timeToResolve: null,
          timeToClose: null,
          businessHours: 0,
          totalHours: 0,
        },
        sla: {
          dueDate: null,
          breached: false,
          timeRemaining: null,
        },
      };
      onTicketClick(convertedTicket);
    }
  };

  return (
    <motion.div
      key={ticket.id}
      variants={itemVariants}
      className='group p-5 figma-glass-card rounded-lg transition-all duration-200 border border-transparent shadow-none cursor-pointer hover:shadow-md hover:border-blue-200'
      onClick={handleTicketClick}
    >
      <div className='flex items-start gap-4'>
        {/* Ícone de prioridade */}
        <div className='flex-shrink-0 mt-0.5'>
          <div
            className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${priorityConf.color}`}
          >
            <span className='mr-1'>{priorityConf.icon}</span>
            {ticket.priority}
          </div>
        </div>

        {/* Conteúdo do ticket */}
        <div className='flex-1 min-w-0'>
          <div className='flex items-start justify-between gap-2 mb-2'>
            <div className='flex items-center gap-2'>
              <span className='figma-subheading'>#{ticket.id}</span>
              <Badge variant='secondary' className='text-xs'>
                NOVO
              </Badge>
            </div>
            <Button
              variant='ghost'
              size='sm'
              className='opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6 p-0'
            >
              <ExternalLink className='h-3 w-3' />
            </Button>
          </div>

          <h4 className='figma-body mb-2 line-clamp-2 leading-tight'>{ticket.title}</h4>

          {ticket.description && (
            <p className='figma-body mb-2 line-clamp-2 leading-relaxed opacity-75'>
              {ticket.description}
            </p>
          )}

          <div className='flex items-center justify-between figma-body'>
            <div className='flex items-center gap-1'>
              <User className='h-3 w-3' />
              <span className='truncate max-w-24'>{ticket.requester}</span>
            </div>
            <div className='flex items-center gap-1'>
              <Calendar className='h-3 w-3' />
              <span>{formattedDate}</span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
});

TicketItem.displayName = 'TicketItem';

export const NewTicketsList = React.memo<NewTicketsListProps>(({ className, limit = 8, onTicketClick }) => {
  const [tickets, setTickets] = useState<NewTicket[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const fetchTickets = useThrottledCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const newTickets = await apiService.getNewTickets(limit);
      startTransition(() => {
        setTickets(newTickets);
        setLastUpdate(new Date());
        setIsLoading(false);
      });
    } catch (err) {
      console.error('Erro ao buscar tickets novos:', err);
      setError('Erro ao carregar tickets');
      setIsLoading(false);
    }
  }, 2000); // 2 second throttle

  // Fetch initial tickets
  useEffect(() => {
    fetchTickets();
  }, [fetchTickets]);

  // Smart refresh para lista de tickets
  useSmartRefresh({
    refreshKey: 'new-tickets-list',
    refreshFn: fetchTickets,
    intervalMs: 300000, // 5 minutos
    immediate: false,
    enabled: true,
  });

  // Memoizar valores derivados
  const ticketsCount = useMemo(() => tickets.length, [tickets.length]);
  const hasTickets = useMemo(() => tickets.length > 0, [tickets.length]);
  const formattedLastUpdate = useMemo(
    () => (lastUpdate ? formatRelativeTime(lastUpdate) : null),
    [lastUpdate]
  );

  return (
    <Card className={cn('figma-tickets-recentes h-full flex flex-col shadow-none', className)}>
      <CardHeader className='px-5 pt-5 pb-3'>
        <div className='flex items-center justify-between'>
          <CardTitle className='figma-heading-large flex items-center gap-2'>
            <div className='p-2 rounded-xl bg-gradient-to-br shadow-lg from-slate-600 to-slate-700'>
              <AlertCircle className='h-5 w-5 text-white' />
            </div>
            Tickets Novos
          </CardTitle>

          <div className='flex items-center gap-2'>
            <Badge variant='outline' className='figma-badge-subtle'>
              {ticketsCount} tickets
            </Badge>
            <Button
              variant='outline'
              size='sm'
              onClick={fetchTickets}
              disabled={isLoading}
              className='h-8 w-8 p-0'
            >
              <RefreshCw className={cn('h-4 w-4', isLoading && 'animate-spin')} />
            </Button>
          </div>
        </div>

        {formattedLastUpdate && (
          <div className='flex items-center gap-1 figma-body'>
            <Clock className='h-3 w-3' />
            Atualizado {formattedLastUpdate}
          </div>
        )}
      </CardHeader>

      <CardContent className='px-5 pb-5 pt-0 flex-1 flex flex-col overflow-hidden'>
        {isLoading ? (
          <div className='space-y-3 flex-1 overflow-y-auto'>
            {[...Array(4)].map((_, i) => (
              <div key={i} className='animate-pulse'>
                <div className='flex items-start gap-3 p-3 figma-glass-card rounded-lg'>
                  <div className='w-8 h-8 bg-gray-200 rounded-full' />
                  <div className='flex-1 space-y-2'>
                    <div className='h-4 bg-gray-200 rounded w-3/4' />
                    <div className='h-3 bg-gray-200 rounded w-1/2' />
                    <div className='h-3 bg-gray-200 rounded w-1/4' />
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className='text-center py-8 flex-1 flex items-center justify-center'>
            <div>
              <AlertCircle className='w-12 h-12 mx-auto mb-4 text-red-400' />
              <div className='text-sm text-red-600 font-medium'>{error}</div>
              <Button variant='outline' size='sm' onClick={fetchTickets} className='mt-3'>
                Tentar novamente
              </Button>
            </div>
          </div>
        ) : !hasTickets ? (
          <div className='text-center py-8 flex-1 flex items-center justify-center'>
            <div>
              <AlertCircle className='w-12 h-12 mx-auto mb-4 figma-body' />
              <div className='figma-body font-medium'>Nenhum ticket novo encontrado</div>
              <div className='figma-body mt-1'>Todos os tickets foram processados</div>
            </div>
          </div>
        ) : (
          <motion.div
            variants={containerVariants}
            initial='hidden'
            animate='visible'
            className='space-y-3 flex-1 overflow-y-auto pr-2'
          >
            {tickets.map((ticket, index) => (
              <TicketItem key={ticket.id} ticket={ticket} index={index} onTicketClick={onTicketClick} />
            ))}
          </motion.div>
        )}
      </CardContent>
    </Card>
  );
});

NewTicketsList.displayName = 'NewTicketsList';

export default NewTicketsList;
