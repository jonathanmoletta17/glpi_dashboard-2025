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
import { 
  createCardClasses, 
  createListItemClasses, 
  createBadgeClasses,
  createButtonClasses 
} from '@/design-system/component-patterns';
import { componentSpacing } from '@/design-system/spacing';

interface NewTicketsListProps {
  className?: string;
  limit?: number;
  onTicketClick?: (ticket: Ticket) => void;
}

// Configuração de prioridades simplificada
const priorityConfig = {
  'Crítica': { variant: 'danger' as const, icon: '🔴' },
  'Muito Alta': { variant: 'danger' as const, icon: '🔴' },
  'Alta': { variant: 'warning' as const, icon: '🟠' },
  'Média': { variant: 'default' as const, icon: '🟡' },
  'Baixa': { variant: 'success' as const, icon: '🟢' },
  'Muito Baixa': { variant: 'default' as const, icon: '🔵' },
  'Normal': { variant: 'default' as const, icon: '🔵' },
} as const;

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
  onTicketClick?: (ticket: Ticket) => void 
}>(({ ticket, onTicketClick }) => {
  const priorityConf = useMemo(() => 
    priorityConfig[ticket.priority as keyof typeof priorityConfig] || priorityConfig['Normal'], 
    [ticket.priority]
  );
  
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
        category: 'Geral',
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
      variants={itemVariants}
      className={createListItemClasses()}
      onClick={handleTicketClick}
    >
      <div className="flex items-start justify-between gap-3">
        {/* Badge de prioridade */}
        <div className="flex-shrink-0">
          <Badge 
            variant={priorityConf.variant}
            className="flex items-center gap-1"
          >
            <span>{priorityConf.icon}</span>
            {ticket.priority}
          </Badge>
        </div>

        {/* Conteúdo do ticket */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-2">
            <div className="flex items-center gap-2 min-w-0">
              <span className="text-sm font-medium text-gray-500">#{ticket.id}</span>
              <Badge variant="secondary" className="text-xs">
                NOVO
              </Badge>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 flex-shrink-0"
            >
              <ExternalLink className="h-3 w-3" />
            </Button>
          </div>

          <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-1 line-clamp-2">
            {ticket.title}
          </h4>

          {ticket.description && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
              {ticket.description}
            </p>
          )}

          <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            <div className="flex items-center gap-1">
              <User className="h-3 w-3" />
              <span className="truncate">{ticket.requester}</span>
            </div>
            <div className="flex items-center gap-1 flex-shrink-0">
              <Calendar className="h-3 w-3" />
              <span>{formattedDate}</span>
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
  <div className="space-y-3">
    {[...Array(4)].map((_, i) => (
      <div key={i} className="animate-pulse">
        <div className="p-3 rounded-md border border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800">
          <div className="flex items-start gap-3">
            <div className="h-6 w-16 bg-gray-200 dark:bg-gray-700 rounded-full flex-shrink-0" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2" />
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/3" />
            </div>
          </div>
        </div>
      </div>
    ))}
  </div>
);

// Componente de estado vazio
const EmptyState = ({ error }: { error?: string }) => (
  <div className="text-center py-8">
    <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
    <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
      {error ? 'Erro ao carregar' : 'Nenhum ticket novo'}
    </h3>
    <p className="text-sm text-gray-500 dark:text-gray-400">
      {error || 'Não há tickets novos no momento.'}
    </p>
  </div>
);

export const NewTicketsListRefactored = React.memo<NewTicketsListProps>(({ 
  className, 
  limit = 8, 
  onTicketClick 
}) => {
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
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <div className="h-8 w-8 bg-blue-500 rounded-lg flex items-center justify-center">
              <AlertCircle className="h-4 w-4 text-white" />
            </div>
            Tickets Novos
          </CardTitle>

          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              {ticketsCount} tickets
            </Badge>
            <Button
              variant="outline"
              size="icon"
              onClick={fetchTickets}
              disabled={isLoading}
              className="h-8 w-8"
            >
              <RefreshCw className={cn('h-4 w-4', isLoading && 'animate-spin')} />
            </Button>
          </div>
        </div>

        {formattedLastUpdate && (
          <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
            <Clock className="h-3 w-3" />
            Atualizado {formattedLastUpdate}
          </div>
        )}
      </CardHeader>

      <CardContent className="pt-0">
        {isLoading ? (
          <LoadingSkeleton />
        ) : error ? (
          <EmptyState error={error} />
        ) : hasTickets ? (
          <motion.div
            className="space-y-2"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {tickets.map((ticket) => (
              <TicketItem
                key={ticket.id}
                ticket={ticket}
                onTicketClick={onTicketClick}
              />
            ))}
          </motion.div>
        ) : (
          <EmptyState />
        )}
      </CardContent>
    </Card>
  );
});

NewTicketsListRefactored.displayName = 'NewTicketsListRefactored';

export default NewTicketsListRefactored;
