/**
 * TicketBadge Component
 * Badge aprimorado para tickets com ícones SVG e design tokens
 */

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';
import {
  getPriorityConfig,
  getStatusConfig,
  ticketAnimations,
  ticketSpacing,
  ticketTypography,
} from '../../design-system/ticket-tokens';

export interface TicketBadgeProps {
  type: 'priority' | 'status';
  value: string;
  className?: string;
  showIcon?: boolean;
  size?: 'sm' | 'md' | 'lg';
  animated?: boolean;
}

const TicketBadge: React.FC<TicketBadgeProps> = ({
  type,
  value,
  className,
  showIcon = true,
  size = 'md',
  animated = true,
}) => {
  const config = type === 'priority' ? getPriorityConfig(value) : getStatusConfig(value);
  const IconComponent = config.icon;

  // Tamanhos baseados no design token
  const sizeClasses = {
    sm: {
      badge: 'px-2 py-0.5 text-xs',
      icon: ticketSpacing.icon.sizeSmall,
      gap: 'gap-1',
    },
    md: {
      badge: ticketSpacing.badge.padding + ' ' + ticketTypography.badge.size,
      icon: ticketSpacing.icon.size,
      gap: ticketSpacing.badge.gap,
    },
    lg: {
      badge: 'px-3 py-1 text-sm',
      icon: ticketSpacing.icon.sizeLarge,
      gap: 'gap-1.5',
    },
  };

  const currentSize = sizeClasses[size];

  // Classes CSS dinâmicas baseadas no tema
  const badgeClasses = cn(
    'inline-flex items-center rounded-full font-medium transition-all duration-200',
    currentSize.badge,
    currentSize.gap,
    // Cores para tema claro
    `bg-[${config.bgColor}] text-[${config.textColor}] border border-[${config.borderColor || 'transparent'}]`,
    // Cores para tema escuro
    `dark:bg-[${config.darkBgColor}] dark:text-[${config.darkTextColor}] dark:border-[${config.darkBorderColor || 'transparent'}]`,
    // Hover effects
    'hover:shadow-sm hover:scale-105',
    className
  );

  const iconClasses = cn('flex-shrink-0', currentSize.icon, `text-[${config.color}]`);

  const BadgeContent = () => (
    <>
      {showIcon && <IconComponent className={iconClasses} aria-hidden='true' />}
      <span className='truncate'>{value}</span>
    </>
  );

  if (animated) {
    return (
      <motion.span
        className={badgeClasses}
        initial={ticketAnimations.badge.initial}
        animate={ticketAnimations.badge.animate}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        role='status'
        aria-label={`${type}: ${value}`}
      >
        <BadgeContent />
      </motion.span>
    );
  }

  return (
    <span className={badgeClasses} role='status' aria-label={`${type}: ${value}`}>
      <BadgeContent />
    </span>
  );
};

// Componentes especializados para facilitar o uso
export const PriorityBadge: React.FC<Omit<TicketBadgeProps, 'type'>> = props => (
  <TicketBadge type='priority' {...props} />
);

export const StatusBadge: React.FC<Omit<TicketBadgeProps, 'type'>> = props => (
  <TicketBadge type='status' {...props} />
);

// Componente de exemplo para demonstração
export const TicketBadgeShowcase: React.FC = () => {
  const priorities = ['Crítica', 'Muito Alta', 'Alta', 'Média', 'Normal', 'Baixa', 'Muito Baixa'];
  const statuses = ['novo', 'em_progresso', 'pendente', 'solucionado', 'fechado'];

  return (
    <div className='p-6 space-y-6'>
      <div>
        <h3 className='text-lg font-semibold mb-3'>Prioridades</h3>
        <div className='flex flex-wrap gap-2'>
          {priorities.map(priority => (
            <PriorityBadge key={priority} value={priority} />
          ))}
        </div>
      </div>

      <div>
        <h3 className='text-lg font-semibold mb-3'>Status</h3>
        <div className='flex flex-wrap gap-2'>
          {statuses.map(status => (
            <StatusBadge key={status} value={status} />
          ))}
        </div>
      </div>

      <div>
        <h3 className='text-lg font-semibold mb-3'>Tamanhos</h3>
        <div className='flex items-center gap-4'>
          <PriorityBadge value='Alta' size='sm' />
          <PriorityBadge value='Alta' size='md' />
          <PriorityBadge value='Alta' size='lg' />
        </div>
      </div>
    </div>
  );
};

export default TicketBadge;
