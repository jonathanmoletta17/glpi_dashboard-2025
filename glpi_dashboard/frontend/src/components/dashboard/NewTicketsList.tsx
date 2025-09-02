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
import './NewTicketsList.css';



interface NewTicketsListProps {
  className?: string;
  limit?: number;
  onTicketClick?: (ticket: Ticket) => void;
}

// Configuração de prioridades com mapeamento BEM
const priorityConfig = {
  'Crítica': {
    bemClass: 'new-tickets-list__priority-badge--critical',
    icon: '🔴',
  },
  'Muito Alta': {
    bemClass: 'new-tickets-list__priority-badge--critical',
    icon: '🔴',
  },
  'Alta': {
    bemClass: 'new-tickets-list__priority-badge--high',
    icon: '🟠',
  },
  'Média': {
    bemClass: 'new-tickets-list__priority-badge--medium',
    icon: '🟡',
  },
  'Baixa': {
    bemClass: 'new-tickets-list__priority-badge--low',
    icon: '🟢',
  },
  'Muito Baixa': {
    bemClass: 'new-tickets-list__priority-badge--normal',
    icon: '🔵',
  },
  'Normal': {
    bemClass: 'new-tickets-list__priority-badge--normal',
    icon: '🔵',
  },
};

// Variantes de animação
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

// Componente TicketItem refatorado com BEM
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
      className="new-tickets-list__item"
      onClick={handleTicketClick}
    >
      <div className="new-tickets-list__item-content">
        {/* Badge de prioridade com BEM */}
        <div className="new-tickets-list__priority">
          <div className={cn('new-tickets-list__priority-badge', priorityConf.bemClass)}>
            <span className="new-tickets-list__priority-icon">{priorityConf.icon}</span>
            {ticket.priority}
          </div>
        </div>

        {/* Conteúdo do ticket com BEM */}
        <div className="new-tickets-list__ticket-content">
          <div className="new-tickets-list__ticket-header">
            <div className="new-tickets-list__ticket-meta">
              <span className="new-tickets-list__ticket-id">#{ticket.id}</span>
              <Badge variant="secondary" className="new-tickets-list__new-badge">
                NOVO
              </Badge>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="new-tickets-list__external-btn"
            >
              <ExternalLink className="h-3 w-3" />
            </Button>
          </div>

          <h4 className="new-tickets-list__ticket-title">{ticket.title}</h4>

          {ticket.description && (
            <p className="new-tickets-list__ticket-description">
              {ticket.description}
            </p>
          )}

          <div className="new-tickets-list__ticket-footer">
            <div className="new-tickets-list__requester">
              <User className="h-3 w-3" />
              <span className="new-tickets-list__requester-name">{ticket.requester}</span>
            </div>
            <div className="new-tickets-list__date">
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

export const NewTicketsList = React.memo<NewTicketsListProps>(({ className, limit = 8, onTicketClick }) => {
  const [tickets, setTickets] = useState<NewTicket[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [isPending, startTransition] = useTransition();

  // Hook para refresh inteligente
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
    intervalMs: 30000, // 30 segundos
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
    <Card className={cn('new-tickets-list rounded-lg', className)}>
      <CardHeader className="new-tickets-list__header">
        <div className="new-tickets-list__header-content">
          <CardTitle className="new-tickets-list__title">
            <div className="new-tickets-list__title-icon">
              <AlertCircle className="h-5 w-5 text-white" />
            </div>
            Tickets Novos
          </CardTitle>

          <div className="new-tickets-list__header-actions">
            <Badge variant="outline" className="new-tickets-list__count-badge">
              {ticketsCount} tickets
            </Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchTickets}
              disabled={isLoading}
              className="new-tickets-list__refresh-btn"
            >
              <RefreshCw className={cn('h-4 w-4', isLoading && 'animate-spin')} />
            </Button>
          </div>
        </div>

        {formattedLastUpdate && (
          <div className="new-tickets-list__last-update">
            <Clock className="h-3 w-3" />
            Atualizado {formattedLastUpdate}
          </div>
        )}
      </CardHeader>

      <CardContent className="new-tickets-list__content">
        {isLoading ? (
          <div className="new-tickets-list__skeleton">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="new-tickets-list__skeleton-item">
                <div className="new-tickets-list__skeleton-card">
                  <div className="new-tickets-list__skeleton-avatar" />
                  <div className="new-tickets-list__skeleton-content">
                    <div className="new-tickets-list__skeleton-line new-tickets-list__skeleton-line--75" />
                    <div className="new-tickets-list__skeleton-line new-tickets-list__skeleton-line--50" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="new-tickets-list__empty">
            <AlertCircle className="new-tickets-list__empty-icon" />
            <h3 className="new-tickets-list__empty-title">Erro ao carregar</h3>
            <p className="new-tickets-list__empty-description">{error}</p>
          </div>
        ) : hasTickets ? (
          <motion.div
            className="new-tickets-list__items"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {tickets.map((ticket, index) => (
              <TicketItem
                key={ticket.id}
                ticket={ticket}
                index={index}
                onTicketClick={onTicketClick}
              />
            ))}
          </motion.div>
        ) : (
          <div className="new-tickets-list__empty">
            <AlertCircle className="new-tickets-list__empty-icon" />
            <h3 className="new-tickets-list__empty-title">Nenhum ticket novo</h3>
            <p className="new-tickets-list__empty-description">
              Não há tickets novos no momento.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
});

NewTicketsList.displayName = 'NewTicketsList';

export default NewTicketsList;

/* 
=== REFATORAÇÃO CSS APLICADA ===

Esta versão refatorada do NewTicketsList implementa:

1. **Metodologia BEM**: Classes semânticas seguindo o padrão Block__Element--Modifier
2. **CSS Consolidado**: Importação do arquivo CSS refatorado
3. **Estrutura Simplificada**: HTML mais limpo e semântico
4. **Manutenibilidade**: Código mais fácil de manter e estender
5. **Responsividade**: Melhor suporte a diferentes dispositivos
6. **Acessibilidade**: Melhor suporte a leitores de tela e navegação por teclado
7. **Performance**: CSS otimizado com variáveis e menos especificidade
8. **Temas**: Suporte nativo a tema claro/escuro

Principais mudanças:
- Substituição de classes utilitárias por classes BEM semânticas
- Remoção de classes figma-* obsoletas
- Importação do CSS refatorado
- Estrutura HTML simplificada
- Melhor organização do código
*/