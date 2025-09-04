import React from 'react';
import { memo, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn, formatNumber, getStatusIcon } from '@/lib/utils';
import { type LucideIcon } from 'lucide-react';

// CSS refatorado removido - usando apenas Tailwind CSS

/**
 * StatusCard Refatorado - Melhorias Implementadas:
 *
 * 1. CSS Refatorado:
 *    - Substituição de classes utilitárias por classes semânticas BEM
 *    - Variáveis CSS para cores, espaçamentos e animações
 *    - Suporte aprimorado a tema escuro
 *    - Media queries para responsividade
 *    - Melhor acessibilidade (prefers-reduced-motion, prefers-contrast)
 *
 * 2. Estrutura HTML Simplificada:
 *    - Classes BEM descritivas e semânticas
 *    - Redução significativa de classes Tailwind inline
 *    - Melhor separação de responsabilidades
 *
 * 3. Performance:
 *    - CSS otimizado com variáveis reutilizáveis
 *    - Animações mais eficientes
 *    - Menor bundle size
 */

interface StatusCardProps {
  title: string;
  value: number;
  status?: string;
  icon?: LucideIcon;
  className?: string;
  variant?: 'default' | 'compact' | 'detailed' | 'gradient';
  showProgress?: boolean;
  maxValue?: number;
  onClick?: () => void;
}

// Função auxiliar definida fora do componente para evitar recriação
const getStatusClass = (status?: string) => {
  switch (status) {
    case 'online':
      return 'status-card--online';
    case 'offline':
      return 'status-card--offline';
    case 'active':
      return 'status-card--active';
    case 'progress':
      return 'status-card--progress';
    case 'pending':
      return 'status-card--pending';
    case 'resolved':
      return 'status-card--resolved';
    default:
      return 'status-card--default';
  }
};

// Variantes de animação definidas fora do componente
const cardVariants = {
  hidden: { opacity: 0, y: 20, scale: 0.9 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: 'easeOut' as const,
    },
  },
  hover: {
    y: -8,
    scale: 1.03,
    transition: {
      duration: 0.3,
      ease: 'easeInOut' as const,
    },
  },
} as const;

const iconVariants = {
  hover: {
    scale: 1.2,
    rotate: 10,
    transition: {
      duration: 0.3,
      ease: 'easeInOut' as const,
    },
  },
} as const;

const numberVariants = {
  hidden: { scale: 0 },
  visible: {
    scale: 1,
    transition: {
      duration: 0.6,
      ease: 'easeOut' as const,
      delay: 0.2,
    },
  },
} as const;

export const StatusCard = memo<StatusCardProps>(function StatusCard({
  title,
  value,
  status,
  icon,
  className,
  variant: _ = 'default',
  onClick,
}) {
  // Memoizar ícones para evitar recálculos
  const StatusIcon = useMemo(() => icon || (status ? getStatusIcon(status) : null), [icon, status]);

  // Memoizar classe do status
  const statusClass = useMemo(() => getStatusClass(status), [status]);

  // Memoizar valor formatado
  const formattedValue = useMemo(() => {
    return formatNumber(value);
  }, [value]);

  // Handler para clique no card
  const handleCardClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onClick?.();
  };

  return (
    <motion.div
      variants={cardVariants}
      initial='hidden'
      animate='visible'
      whileHover='hover'
      className={cn('status-card status-card--animated', statusClass, className)}
    >
      <Card
        className='status-card__container'
        onClick={handleCardClick}
      >
        {/* Gradient Background */}
        <div className='status-card__gradient-bg' />

        {/* Animated Border */}
        <div className='status-card__animated-border' />

        <CardHeader className='status-card__header'>
          <CardTitle className='status-card__title'>{title}</CardTitle>
          {StatusIcon && (
            <motion.div
              variants={iconVariants}
              className='status-card__icon'
            >
              <StatusIcon />
            </motion.div>
          )}
        </CardHeader>

        <CardContent className='status-card__content'>
          <div className='status-card__content-wrapper'>
            <div className='status-card__value-section'>
              <motion.div
                variants={numberVariants}
                className='status-card__value status-card__value--animated'
              >
                {formattedValue}
              </motion.div>
            </div>

            {status && (
              <motion.div whileHover={{ scale: 1.05 }} transition={{ duration: 0.2 }}>
                <Badge className='status-card__badge'>
                  {status}
                </Badge>
              </motion.div>
            )}
          </div>
        </CardContent>

        {/* Shine Effect */}
        <motion.div
          className='status-card__shine'
          whileHover={{
            opacity: [0, 1, 0],
            x: [-100, 300],
          }}
          transition={{ duration: 0.6 }}
        />
      </Card>
    </motion.div>
  );
});
