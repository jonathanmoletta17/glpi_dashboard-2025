import React from 'react';
import { motion } from 'framer-motion';
import { Clock, User, AlertCircle, CheckCircle, XCircle, Calendar, Tag } from 'lucide-react';
import { Ticket } from '../types/ticket';
import { cn } from '@/lib/utils';

interface TicketCardProps {
  ticket: Ticket;
  onClick?: (ticket: Ticket) => void;
  onStatusChange?: (ticketId: number, status: string) => void;
  onPriorityChange?: (ticketId: number, priority: string) => void;
  compact?: boolean;
  selected?: boolean;
  loading?: boolean;
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'open':
      return <AlertCircle className='h-4 w-4' />;
    case 'closed':
      return <CheckCircle className='h-4 w-4' />;
    case 'in_progress':
      return <Clock className='h-4 w-4' />;
    default:
      return <XCircle className='h-4 w-4' />;
  }
};

const getStatusText = (status: string) => {
  switch (status) {
    case 'open':
      return 'Aberto';
    case 'closed':
      return 'Fechado';
    case 'in_progress':
      return 'Em Progresso';
    default:
      return status;
  }
};

const getPriorityText = (priority: string) => {
  switch (priority) {
    case 'high':
      return 'Alta';
    case 'medium':
      return 'Média';
    case 'low':
      return 'Baixa';
    default:
      return priority;
  }
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('pt-BR');
};

const formatHtmlContent = (content: string): string => {
  if (!content) return '';

  let formatted = content;

  // Decodificar entidades HTML numéricas e hexadecimais
  formatted = formatted.replace(/&#(\d+);/g, (match, dec) => {
    return String.fromCharCode(parseInt(dec, 10));
  });

  formatted = formatted.replace(/&#x([0-9A-Fa-f]+);/g, (match, hex) => {
    return String.fromCharCode(parseInt(hex, 16));
  });

  // Converter entidades HTML comuns
  formatted = formatted
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");

  // Remover tags HTML e manter apenas o texto
  formatted = formatted.replace(/<[^>]*>/g, '');

  // Limpar espaços extras
  formatted = formatted.replace(/\s+/g, ' ').trim();

  return formatted;
};

export const TicketCard: React.FC<TicketCardProps> = ({
  ticket,
  onClick,
  onStatusChange,
  onPriorityChange,
  compact = false,
  selected = false,
  loading = false,
}) => {
  const handleClick = () => {
    if (onClick) {
      onClick(ticket);
    }
  };

  if (loading) {
    return (
      <div className='p-4 border rounded-lg bg-white shadow-sm'>
        <div
          data-testid='loading-spinner'
          className='animate-spin h-6 w-6 border-2 border-blue-500 border-t-transparent rounded-full mx-auto'
        ></div>
      </div>
    );
  }

  return (
    <motion.article
      className={cn(
        'p-4 border rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow cursor-pointer',
        compact && 'compact',
        selected && 'selected border-blue-500 bg-blue-50'
      )}
      onClick={handleClick}
      data-testid='ticket-card'
      role='article'
      aria-labelledby={`ticket-title-${ticket.id}`}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {/* Header */}
      <div className='flex justify-between items-start mb-3'>
        <h3 id={`ticket-title-${ticket.id}`} className='font-semibold text-lg text-gray-900'>
          {ticket.title}
        </h3>
        <div className='flex items-center gap-2'>
          <span
            className={cn(
              'inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium',
              ticket.status === 'novo' && 'bg-red-100 text-red-800',
              ticket.status === 'fechado' && 'bg-green-100 text-green-800',
              ticket.status === 'progresso' && 'bg-yellow-100 text-yellow-800'
            )}
            aria-label={`Status: ${ticket.status}`}
          >
            {getStatusIcon(ticket.status)}
            {getStatusText(ticket.status)}
          </span>
        </div>
      </div>

      {/* Description */}
      <div className='mb-3'>
        <p className={cn('text-gray-700 text-sm', compact && 'truncated')}>
          {formatHtmlContent(ticket.description)}
        </p>
      </div>

      {/* Metadata */}
      <div className='grid grid-cols-2 gap-4 text-sm text-gray-600 mb-3'>
        <div className='flex items-center gap-1'>
          <User className='h-4 w-4' />
          <span>{ticket.requester.name}</span>
        </div>
        <div className='flex items-center gap-1'>
          <User className='h-4 w-4' />
          <span>{ticket.technician?.name || 'Não atribuído'}</span>
        </div>
        <div className='flex items-center gap-1'>
          <Calendar className='h-4 w-4' />
          <span>{formatDate(ticket.createdAt)}</span>
        </div>
        {ticket.dueDate && (
          <div className='flex items-center gap-1'>
            <Clock className='h-4 w-4' />
            <span>Vence: {formatDate(ticket.dueDate)}</span>
          </div>
        )}
      </div>

      {/* Priority and Category */}
      <div className='flex justify-between items-center mb-3'>
        <span
          className={cn(
            'px-2 py-1 rounded text-xs font-medium',
            ticket.priority === 'alta' && 'bg-red-100 text-red-800',
            ticket.priority === 'normal' && 'bg-yellow-100 text-yellow-800',
            ticket.priority === 'baixa' && 'bg-green-100 text-green-800'
          )}
          data-testid='ticket-priority'
        >
          {getPriorityText(ticket.priority)}
        </span>
        <span className='text-sm text-gray-600'>{ticket.category}</span>
      </div>

      {/* Tags */}
      {ticket.tags && ticket.tags.length > 0 && (
        <div className='flex flex-wrap gap-1 mb-3'>
          {ticket.tags.map((tag, index) => (
            <span
              key={index}
              className='inline-flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs'
            >
              <Tag className='h-3 w-3' />
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Footer */}
      <div className='flex justify-between items-center text-xs text-gray-500'>
        <span>{ticket.comments?.length || 0} comentários</span>
        <span>{ticket.attachments?.length || 0} anexos</span>
      </div>
    </motion.article>
  );
};

export default TicketCard;
