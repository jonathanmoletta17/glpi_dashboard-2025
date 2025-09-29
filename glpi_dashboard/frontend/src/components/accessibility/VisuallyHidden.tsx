import React, { JSX } from 'react';
import { cn } from '@/lib/utils';

interface VisuallyHiddenProps {
  children: React.ReactNode;
  className?: string;
  as?: keyof JSX.IntrinsicElements;
}

/**
 * Componente para conteúdo visualmente oculto mas acessível para leitores de tela
 * Segue as melhores práticas de acessibilidade para texto off-screen
 */
export const VisuallyHidden: React.FC<VisuallyHiddenProps> = ({
  children,
  className,
  as: Component = 'span',
}) => {
  return (
    <Component
      className={cn(
        // Posicionamento absoluto para remover do fluxo visual
        'absolute',
        // Dimensões mínimas para manter acessibilidade
        'w-px h-px',
        // Overflow hidden para garantir que não apareça
        'overflow-hidden',
        // Clip path para navegadores mais antigos
        'clip-path-[inset(50%)]',
        // Margin negativo para posicionamento
        '-m-px',
        // Border zero
        'border-0',
        // Padding zero
        'p-0',
        // White space nowrap para evitar quebras
        'whitespace-nowrap',
        className
      )}
      style={{
        // Fallback para navegadores que não suportam clip-path
        clip: 'rect(0, 0, 0, 0)',
      }}
    >
      {children}
    </Component>
  );
};

/**
 * Hook para alternar visibilidade de conteúdo para leitores de tela
 */
export const useScreenReaderAnnouncement = () => {
  const [announcement, setAnnouncement] = React.useState<string>('');
  const [isVisible, setIsVisible] = React.useState(false);

  const announce = React.useCallback((message: string, duration = 3000) => {
    setAnnouncement(message);
    setIsVisible(true);

    // Remove o anúncio após o tempo especificado
    setTimeout(() => {
      setIsVisible(false);
      setTimeout(() => setAnnouncement(''), 150); // Pequeno delay para transição
    }, duration);
  }, []);

  const AnnouncementComponent = React.useMemo(
    () => (
      <div
        role='status'
        aria-live='polite'
        aria-atomic='true'
        className={cn('fixed top-0 left-0 z-[9999]', isVisible ? 'sr-only' : 'hidden')}
      >
        {announcement}
      </div>
    ),
    [announcement, isVisible]
  );

  return {
    announce,
    AnnouncementComponent,
  };
};

/**
 * Componente para skip links (pular para conteúdo principal)
 */
interface SkipLinkProps {
  href: string;
  children: React.ReactNode;
  className?: string;
}

export const SkipLink: React.FC<SkipLinkProps> = ({ href, children, className }) => {
  return (
    <a
      href={href}
      className={cn(
        // Inicialmente oculto
        'absolute top-0 left-0 z-[9999]',
        'bg-blue-600 text-white px-4 py-2 rounded-md',
        'transform -translate-y-full',
        'transition-transform duration-200',
        // Visível quando focado
        'focus:translate-y-0',
        'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
        className
      )}
      onFocus={e => {
        // Garante que o link seja visível quando focado
        e.currentTarget.style.transform = 'translateY(0)';
      }}
      onBlur={e => {
        // Oculta o link quando perde o foco
        e.currentTarget.style.transform = 'translateY(-100%)';
      }}
    >
      {children}
    </a>
  );
};
