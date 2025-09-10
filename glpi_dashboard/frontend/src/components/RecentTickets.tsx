import React, { memo, useMemo, useCallback } from 'react';
import { Clock } from 'lucide-react';
import { Ticket } from '../types';

interface NewTicket {
  id: string;
  title: string;
  description?: string;
  priority: string;
  requester: string;
  date: string;
}

interface RecentTicketsProps {
  newTickets: NewTicket[];
  ticketsLoading: boolean;
  onTicketClick?: (ticket: Ticket) => void;
}

const RecentTickets = memo(({ newTickets, ticketsLoading, onTicketClick }: RecentTicketsProps) => {
  const memoizedTickets = useMemo(() => {
    return newTickets.map(ticket => ({
      ...ticket,
      formattedDate: new Date(ticket.date).toLocaleDateString('pt-BR'),
      ticketObject: {
        id: ticket.id.toString(),
        title: ticket.title,
        description: ticket.description || '',
        status: 'novo' as const,
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
        urgency: 2,
        impact: 2,
        tags: [],
        attachments: [],
        comments: [],
        timeTracking: {
          totalTime: 0,
          entries: [],
        },
      },
    }));
  }, [newTickets]);

  const handleTicketClick = useCallback(
    (ticketObject: Ticket) => {
      if (onTicketClick) {
        onTicketClick(ticketObject);
      }
    },
    [onTicketClick]
  );

  if (ticketsLoading) {
    return (
      <div className='text-center py-8'>
        <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-slate-600 mx-auto mb-2'></div>
        <div className='text-sm text-gray-500'>Carregando...</div>
      </div>
    );
  }

  return (
    <div className='space-y-3 max-h-96 overflow-y-auto'>
      {memoizedTickets.length > 0 ? (
        memoizedTickets.map(ticket => (
          <div
            key={ticket.id}
            className='p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer'
            onClick={() => handleTicketClick(ticket.ticketObject)}
          >
            <div className='flex justify-between items-start mb-2'>
              <div className='text-sm font-medium text-gray-900 truncate flex-1 mr-2'>
                #{ticket.id}
              </div>
              <span className='inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'>
                {ticket.priority}
              </span>
            </div>
            <div className='text-sm text-gray-600 mb-2 line-clamp-2'>{ticket.title}</div>
            <div className='flex items-center justify-between text-xs text-gray-500'>
              <span>{ticket.requester}</span>
              <span>{ticket.formattedDate}</span>
            </div>
          </div>
        ))
      ) : (
        <div className='text-center py-8 text-gray-500'>
          <Clock className='w-8 h-8 mx-auto mb-2 text-gray-400' />
          <div className='text-sm'>Nenhum chamado recente</div>
        </div>
      )}
    </div>
  );
});

RecentTickets.displayName = 'RecentTickets';

export default RecentTickets;
