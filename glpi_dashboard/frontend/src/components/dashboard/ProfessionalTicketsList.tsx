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

interface ProfessionalTicketsListProps {
  className?: string;
  limit?: number;
  onTicketClick?: (ticket: Ticket) => void;
}

// Variantes de animação profissionais
const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3,
      ease: 'easeOut' as const
    }
  },
  hover: {
    y: -1,
    transition: {
      duration: 0.15,
      ease: 'easeOut' as const,
    },
  },
} as const;

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.05 },
  },
} as const;

// Componente TicketItem profissional
const ProfessionalTicketItem = React.memo<{
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

  const getPriorityConfig = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'alta':
        return {
          bgClass: 'bg-red-50 border-red-200',
          textClass: 'text-red-700',
          iconClass: 'text-red-600'
        };
      case 'média':
        return {
          bgClass: 'bg-yellow-50 border-yellow-200',
          textClass: 'text-yellow-700',
          iconClass: 'text-yellow-600'
        };
      case 'baixa':
        return {
          bgClass: 'bg-green-50 border-green-200',
          textClass: 'text-green-700',
          iconClass: 'text-green-600'
        };
      default:
        return {
          bgClass: 'bg-gray-50 border-gray-200',
          textClass: 'text-gray-700',
          iconClass: 'text-gray-600'
        };
    }
  };

  const priorityConfig = getPriorityConfig(ticket.priority);

  return (
    <motion.div
      key={ticket.id}
      variants={itemVariants}
      whileHover="hover"
      className="group cursor-pointer"
      onClick={handleTicketClick}
    >
      <div className="p-3 rounded-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-300 dark:hover:border-gray-600 transition-colors duration-150 hover:shadow-sm">
        <div className="flex items-start justify-between gap-3">
          {/* Badge de prioridade */}
          <div className="flex-shrink-0">
            <Badge
              variant="outline"
              className={`${priorityConfig.bgClass} ${priorityConfig.textClass} border text-xs px-2 py-1`}
            >
              {ticket.priority}
            </Badge>
          </div>

          {/* Conteúdo do ticket */}
          <div className="flex-1 min-w-0 space-y-2">
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-gray-500 dark:text-gray-400">#{ticket.id}</span>
                <Badge
                  variant="outline"
                  className="bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-700 text-xs px-2 py-1"
                >
                  Novo
                </Badge>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <ExternalLink className="h-3 w-3" />
              </Button>
            </div>

            <h4 className="text-sm font-semibold text-gray-900 dark:text-white line-clamp-2 leading-tight">
              {ticket.title}
            </h4>

            {ticket.description && (
              <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2 leading-relaxed">
                {ticket.description}
              </p>
            )}

            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-1 min-w-0">
                <User className="h-3 w-3 text-gray-400 dark:text-gray-500 flex-shrink-0" />
                <span className="text-xs text-gray-600 dark:text-gray-400 truncate">
                  {ticket.requester}
                </span>
              </div>
              <div className="flex items-center gap-1 flex-shrink-0">
                <Calendar className="h-3 w-3 text-gray-400 dark:text-gray-500" />
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {formattedDate}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
});

ProfessionalTicketItem.displayName = 'ProfessionalTicketItem';

// Componente de loading skeleton profissional
const ProfessionalLoadingSkeleton = () => (
  <div className="space-y-3">
    {[...Array(4)].map((_, i) => (
      <div key={i} className="animate-pulse">
        <div className="p-4 rounded-lg border border-gray-200 bg-white">
          <div className="flex items-start justify-between gap-3">
            <div className="h-6 w-16 bg-gray-200 rounded-full flex-shrink-0" />
            <div className="flex-1 space-y-2">
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                <div className="h-4 w-12 bg-gray-200 dark:bg-gray-700 rounded" />
                <div className="h-4 w-12 bg-gray-200 dark:bg-gray-700 rounded" />
                </div>
                <div className="h-4 w-4 bg-gray-200 dark:bg-gray-700 rounded" />
              </div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2" />
              <div className="flex items-center justify-between gap-2">
                <div className="h-3 w-24 bg-gray-200 dark:bg-gray-700 rounded" />
                <div className="h-3 w-16 bg-gray-200 dark:bg-gray-700 rounded" />
              </div>
            </div>
          </div>
        </div>
      </div>
    ))}
  </div>
);

// Componente de estado vazio profissional
const ProfessionalEmptyState = ({ error }: { error?: string }) => (
  <div className="flex flex-col items-center justify-center p-8 text-center">
    <div className="p-3 rounded-full bg-gray-100 dark:bg-gray-800 mb-4">
      <AlertCircle className="h-6 w-6 text-gray-400 dark:text-gray-500" />
    </div>
    <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-1">
      {error ? 'Erro ao carregar' : 'Nenhum ticket novo'}
    </h3>
    <p className="text-xs text-gray-500 dark:text-gray-400">
      {error || 'Não há tickets novos no momento.'}
    </p>
  </div>
);

export const ProfessionalTicketsList = React.memo<ProfessionalTicketsListProps>(({
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
    <Card className={cn("h-full bg-transparent border-0 shadow-none", className)}>
      <CardHeader className="pb-2 px-4 pt-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold flex items-center gap-2 text-gray-900 dark:text-white">
            <div className="p-1.5 rounded-md bg-white dark:bg-gray-700 shadow-sm border border-gray-200 dark:border-gray-600">
              <AlertCircle className="h-4 w-4 text-gray-600 dark:text-gray-300" />
            </div>
            Tickets Novos
          </CardTitle>

          <div className="flex items-center gap-2">
            <Badge
              variant="outline"
              className="bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 text-xs px-2 py-1 font-semibold shadow-sm"
            >
              {ticketsCount} tickets
            </Badge>
            <Button
              variant="outline"
              size="icon"
              onClick={fetchTickets}
              disabled={isLoading}
              className="h-6 w-6 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150"
            >
              <RefreshCw className={cn('h-3 w-3', isLoading && 'animate-spin')} />
            </Button>
          </div>
        </div>

        {formattedLastUpdate && (
          <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 mt-1">
            <Clock className="h-3 w-3" />
            Atualizado {formattedLastUpdate}
          </div>
        )}
      </CardHeader>

      <CardContent className="px-4 pb-4 pt-0">
        {isLoading ? (
          <ProfessionalLoadingSkeleton />
        ) : error ? (
          <ProfessionalEmptyState error={error} />
        ) : hasTickets ? (
          <motion.div
            className="space-y-2"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {tickets.map((ticket) => (
              <ProfessionalTicketItem
                key={ticket.id}
                ticket={ticket}
                onTicketClick={onTicketClick}
              />
            ))}
          </motion.div>
        ) : (
          <ProfessionalEmptyState />
        )}
      </CardContent>
    </Card>
  );
});

ProfessionalTicketsList.displayName = 'ProfessionalTicketsList';
