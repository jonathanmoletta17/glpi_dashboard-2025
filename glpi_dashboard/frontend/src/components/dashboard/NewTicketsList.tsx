import React, { useState, useEffect, useMemo, useTransition } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AlertCircle, Clock, User, Calendar, RefreshCw, ExternalLink, XCircle } from 'lucide-react';
import { NewTicket, Ticket } from '@/types';
import { cn, formatRelativeTime, formatDate } from '@/lib/utils';
import { createFlexClasses, TAILWIND_CLASSES } from '@/design-system/utils';
import { apiService } from '@/services/api';
import { useThrottledCallback } from '@/hooks/useDebounce';
import { useSmartRefresh } from '@/hooks/useSmartRefresh';
import {
  createCardClasses,
  createListItemClasses,
  createBadgeClasses,
  createButtonClasses,
} from '@/design-system/component-patterns';
import { componentSpacing } from '@/design-system/spacing';
import { PriorityBadge, StatusBadge } from '@/components/ui/TicketBadge';
import {
  getPriorityConfig,
  getStatusConfig,
  ticketAnimations,
  ticketSpacing,
  ticketTypography,
  ticketClasses,
} from '@/design-system/ticket-tokens';

interface NewTicketsListProps {
  className?: string;
  limit?: number;
  onTicketClick?: (ticket: Ticket) => void;
}

// Removido - usando design tokens agora

// Variantes de animação otimizadas
const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.2 } },
} as const;

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.05 },
  },
} as const;

// Componente TicketItem refatorado
const TicketItem = React.memo<{
  ticket: NewTicket;
  onTicketClick?: (ticket: Ticket) => void;
}>(({ ticket, onTicketClick }) => {
  const formattedDate = useMemo(() => formatDate(ticket.date), [ticket.date]);

  const handleTicketClick = () => {
    if (onTicketClick) {
      const convertedTicket: Ticket = {
        id: ticket.id.toString(),
        title: ticket.title,
        description: ticket.description || '',
        status: 'novo',
        priority: ticket.priority.toLowerCase() as any,
        requester: {
          id: '1',
          name: ticket.requester,
          email: '',
        },
        technician: undefined,
        createdAt: ticket.date,
        updatedAt: ticket.date,
        category: ticket.category || 'Não categorizado',
        location: '',
        urgency: 2,
        impact: 2,
        tags: [],
        attachments: [],
        comments: [],
        timeTracking: {
          totalTime: 0,
          entries: [],
        },
      };
      onTicketClick(convertedTicket);
    }
  };

  return (
    <motion.div
      key={ticket.id}
      variants={ticketAnimations.item}
      whileHover={ticketAnimations.item.hover}
      whileTap={ticketAnimations.item.tap}
      className={cn(ticketClasses.item, ticketClasses.itemActive, 'group')}
      onClick={handleTicketClick}
    >
      <div className={cn('flex items-start justify-between gap-3')}>
        {/* Conteúdo do ticket */}
        <div className='flex-1 min-w-0 space-y-2'>
          <div className='flex items-start justify-between gap-2'>
            <div className='flex items-center gap-2'>
              <span
                className={cn(
                  ticketTypography.metadata.size,
                  ticketTypography.metadata.weight,
                  ticketTypography.metadata.color
                )}
              >
                #{ticket.id}
              </span>
              <StatusBadge value='novo' size='sm' />
            </div>
            <div className='flex items-center gap-2'>
              <Button
                variant='ghost'
                size='icon'
                className='h-6 w-6 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity'
              >
                <ExternalLink className='h-3 w-3' />
              </Button>
              {/* Badge de prioridade movido para a direita */}
              <div className='flex-shrink-0'>
                <PriorityBadge
                  value={ticket.priority}
                  size='sm'
                  className={ticketSpacing.badge.margin}
                />
              </div>
            </div>
          </div>

          <h4
            className={cn(
              ticketTypography.title.size,
              ticketTypography.title.weight,
              ticketTypography.title.color,
              ticketTypography.title.lineHeight,
              ticketClasses.lineClamp
            )}
          >
            {ticket.title}
          </h4>

          {ticket.description && (
            <p
              className={cn(
                ticketTypography.description.size,
                ticketTypography.description.weight,
                ticketTypography.description.color,
                ticketTypography.description.lineHeight,
                ticketClasses.lineClamp
              )}
            >
              {ticket.description}
            </p>
          )}

          <div className='flex items-center justify-between gap-2'>
            <div className='flex items-center gap-1 min-w-0'>
              <User className={cn(ticketSpacing.icon.sizeSmall, 'flex-shrink-0')} />
              <span
                className={cn(
                  ticketTypography.metadata.size,
                  ticketTypography.metadata.color,
                  ticketClasses.truncate
                )}
              >
                {ticket.requester}
              </span>
            </div>
            <div className='flex items-center gap-1 flex-shrink-0'>
              <Calendar className={ticketSpacing.icon.sizeSmall} />
              <span className={cn(ticketTypography.metadata.size, ticketTypography.metadata.color)}>
                {formattedDate}
              </span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
});

TicketItem.displayName = 'TicketItem';

// Componente de loading skeleton
const LoadingSkeleton = () => (
  <div className={TAILWIND_CLASSES.spaceY.card}>
    {[...Array(4)].map((_, i) => (
      <div key={i} className='animate-pulse'>
        <div className={createCardClasses()}>
          <div className={createFlexClasses('row', 'start', 'start', 'normal')}>
            <div className='h-6 w-16 bg-gray-200 dark:bg-gray-700 rounded-full flex-shrink-0' />
            <div className={cn('flex-1', TAILWIND_CLASSES.spaceY.list)}>
              <div className='h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4' />
              <div className='h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2' />
              <div className='h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/3' />
            </div>
          </div>
        </div>
      </div>
    ))}
  </div>
);

// Componente de estado vazio
const EmptyState = ({ error }: { error?: string }) => (
  <div className='text-center py-8'>
    <AlertCircle className='h-12 w-12 text-gray-400 mx-auto mb-4' />
    <h3 className='text-lg font-medium text-gray-900 dark:text-gray-100 mb-2'>
      {error ? 'Erro ao carregar' : 'Nenhum ticket novo'}
    </h3>
    <p className='text-sm text-gray-500 dark:text-gray-400'>
      {error || 'Não há tickets novos no momento.'}
    </p>
  </div>
);

export const NewTicketsList = React.memo<NewTicketsListProps>(
  ({ className, limit = 8, onTicketClick }) => {
    const [tickets, setTickets] = useState<NewTicket[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
    const [isPending, startTransition] = useTransition();

    const fetchTickets = useThrottledCallback(async () => {
      try {
        setError(null);
        const response = await apiService.getNewTickets(limit);

        startTransition(() => {
          setTickets(response || []);
          setLastUpdate(new Date());
          markRefreshed();
        });
      } catch (err) {
        console.error('Erro ao buscar tickets novos:', err);
        setError('Erro ao carregar tickets novos');
      } finally {
        setIsLoading(false);
      }
    }, 1000);

    useEffect(() => {
      fetchTickets();
    }, [fetchTickets]);

    const { shouldRefresh, markRefreshed } = useSmartRefresh({
      intervalMs: 30000,
      refreshKey: 'new-tickets',
      refreshFn: fetchTickets,
      enabled: true,
    });

    useEffect(() => {
      if (shouldRefresh() && !isLoading) {
        fetchTickets();
      }
    }, [shouldRefresh, fetchTickets, isLoading]);

    const ticketsCount = useMemo(() => tickets.length, [tickets.length]);
    const hasTickets = useMemo(() => tickets.length > 0, [tickets.length]);
    const formattedLastUpdate = useMemo(
      () => (lastUpdate ? formatRelativeTime(lastUpdate) : null),
      [lastUpdate]
    );

    return (
      <Card className={cn(createCardClasses(), className)}>
        <CardHeader className='pb-3'>
          <div className='flex items-center justify-between'>
            <CardTitle className='flex items-center gap-2'>
              <div className='h-8 w-8 bg-blue-500 rounded-lg flex items-center justify-center'>
                <AlertCircle className='h-4 w-4 text-white' />
              </div>
              Tickets Novos
            </CardTitle>

            <div className='flex items-center gap-2'>
              <Badge variant='outline' className='text-xs'>
                {ticketsCount} tickets
              </Badge>
              <Button
                variant='outline'
                size='icon'
                onClick={fetchTickets}
                disabled={isLoading}
                className='h-8 w-8'
              >
                <RefreshCw className={cn('h-4 w-4', isLoading && 'animate-spin')} />
              </Button>
            </div>
          </div>

          {formattedLastUpdate && (
            <div className='flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400'>
              <Clock className='h-3 w-3' />
              Atualizado {formattedLastUpdate}
            </div>
          )}
        </CardHeader>

        <CardContent className='pt-0'>
          {isLoading ? (
            <LoadingSkeleton />
          ) : error ? (
            <EmptyState error={error} />
          ) : hasTickets ? (
            <motion.div
              className={ticketSpacing.card.gap}
              variants={ticketAnimations.container}
              initial='hidden'
              animate='visible'
            >
              {tickets.map(ticket => (
                <TicketItem key={ticket.id} ticket={ticket} onTicketClick={onTicketClick} />
              ))}
            </motion.div>
          ) : (
            <EmptyState />
          )}
        </CardContent>
      </Card>
    );
  }
);

NewTicketsList.displayName = 'NewTicketsList';

export default NewTicketsList;
