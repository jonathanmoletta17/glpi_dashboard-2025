import * as React from 'react';
import { cn } from '@/lib/utils';
import { generateId, focusManager } from '@/utils/accessibility';
import { X } from 'lucide-react';
import { createPortal } from 'react-dom';

export interface DialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
}

export interface DialogContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  onEscapeKeyDown?: (event: KeyboardEvent) => void;
  onPointerDownOutside?: (event: PointerEvent) => void;
  forceMount?: boolean;
}

export interface DialogHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export interface DialogFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export interface DialogTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode;
  asChild?: boolean;
}

export interface DialogDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode;
}

export interface DialogCloseProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children?: React.ReactNode;
  asChild?: boolean;
}

// Context for dialog state
interface DialogContextValue {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  titleId: string;
  descriptionId: string;
}

const DialogContext = React.createContext<DialogContextValue | null>(null);

const useDialog = () => {
  const context = React.useContext(DialogContext);
  if (!context) {
    throw new Error('Dialog components must be used within a Dialog');
  }
  return context;
};

// Main Dialog component
const Dialog: React.FC<DialogProps> = ({ open = false, onOpenChange, children }) => {
  const titleId = generateId('dialog-title');
  const descriptionId = generateId('dialog-description');

  const contextValue: DialogContextValue = {
    open,
    onOpenChange: onOpenChange || (() => {}),
    titleId,
    descriptionId,
  };

  return <DialogContext.Provider value={contextValue}>{children}</DialogContext.Provider>;
};

// Dialog Trigger
const DialogTrigger = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement>
>(({ children, onClick, ...props }, ref) => {
  const { onOpenChange } = useDialog();

  const handleClick = React.useCallback(
    (event: React.MouseEvent<HTMLButtonElement>) => {
      onClick?.(event);
      onOpenChange(true);
    },
    [onClick, onOpenChange]
  );

  return (
    <button ref={ref} onClick={handleClick} {...props}>
      {children}
    </button>
  );
});
DialogTrigger.displayName = 'DialogTrigger';

// Dialog Portal
const DialogPortal: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return createPortal(children, document.body);
};

// Dialog Overlay
const DialogOverlay = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    const { open } = useDialog();

    if (!open) return null;

    return (
      <div
        ref={ref}
        className={cn(
          'fixed inset-0 z-50 bg-background/80 backdrop-blur-sm',
          'data-[state=open]:animate-in data-[state=closed]:animate-out',
          'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
          className
        )}
        data-state={open ? 'open' : 'closed'}
        {...props}
      />
    );
  }
);
DialogOverlay.displayName = 'DialogOverlay';

// Dialog Content
const DialogContent = React.forwardRef<HTMLDivElement, DialogContentProps>(
  ({ className, children, onEscapeKeyDown, onPointerDownOutside, ...props }, ref) => {
    const { open, onOpenChange, titleId, descriptionId } = useDialog();
    const contentRef = React.useRef<HTMLDivElement>(null);
    const previousActiveElement = React.useRef<HTMLElement | null>(null);

    // Focus management
    React.useEffect(() => {
      if (open) {
        // Store the previously focused element
        previousActiveElement.current = document.activeElement as HTMLElement;

        // Focus trap
        const cleanup = focusManager.trapFocus(contentRef.current!);

        return cleanup;
      } else {
        // Restore focus to previously focused element
        if (previousActiveElement.current) {
          previousActiveElement.current.focus();
        }
      }
    }, [open]);

    // Escape key handling
    React.useEffect(() => {
      const handleKeyDown = (event: KeyboardEvent) => {
        if (event.key === 'Escape') {
          event.preventDefault();
          onEscapeKeyDown?.(event);
          onOpenChange(false);
        }
      };

      if (open) {
        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
      }
    }, [open, onEscapeKeyDown, onOpenChange]);

    // Click outside handling
    React.useEffect(() => {
      const handlePointerDown = (event: PointerEvent) => {
        if (contentRef.current && !contentRef.current.contains(event.target as Node)) {
          onPointerDownOutside?.(event);
          onOpenChange(false);
        }
      };

      if (open) {
        document.addEventListener('pointerdown', handlePointerDown);
        return () => document.removeEventListener('pointerdown', handlePointerDown);
      }
    }, [open, onPointerDownOutside, onOpenChange]);

    // Prevent body scroll when dialog is open
    React.useEffect(() => {
      if (open) {
        const originalStyle = window.getComputedStyle(document.body).overflow;
        document.body.style.overflow = 'hidden';
        return () => {
          document.body.style.overflow = originalStyle;
        };
      }
    }, [open]);

    if (!open) return null;

    return (
      <DialogPortal>
        <DialogOverlay />
        <div className='fixed inset-0 z-50 flex items-center justify-center p-4'>
          <div
            ref={node => {
              if (typeof ref === 'function') ref(node);
              else if (ref) ref.current = node;
              if (contentRef)
                (contentRef as React.MutableRefObject<HTMLDivElement | null>).current = node;
            }}
            className={cn(
              'relative z-50 grid w-full max-w-lg gap-4 border border-gray-200 dark:border-gray-800',
              'bg-white dark:bg-gray-900 p-6 shadow-lg duration-200',
              'data-[state=open]:animate-in data-[state=closed]:animate-out',
              'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
              'data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95',
              'data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%]',
              'data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%]',
              'sm:rounded-lg',
              className
            )}
            role='dialog'
            aria-modal='true'
            aria-labelledby={titleId}
            aria-describedby={descriptionId}
            data-state={open ? 'open' : 'closed'}
            {...props}
          >
            {children}
          </div>
        </div>
      </DialogPortal>
    );
  }
);
DialogContent.displayName = 'DialogContent';

// Dialog Header
const DialogHeader = React.forwardRef<HTMLDivElement, DialogHeaderProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('flex flex-col space-y-1.5 text-center sm:text-left', className)}
      {...props}
    />
  )
);
DialogHeader.displayName = 'DialogHeader';

// Dialog Footer
const DialogFooter = React.forwardRef<HTMLDivElement, DialogFooterProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2', className)}
      {...props}
    />
  )
);
DialogFooter.displayName = 'DialogFooter';

// Dialog Title
const DialogTitle = React.forwardRef<HTMLHeadingElement, DialogTitleProps>(
  ({ className, children, ...props }, ref) => {
    const { titleId } = useDialog();

    return (
      <h2
        ref={ref}
        id={titleId}
        className={cn(
          'text-lg font-semibold leading-none tracking-tight text-gray-900 dark:text-gray-100',
          className
        )}
        {...props}
      >
        {children}
      </h2>
    );
  }
);
DialogTitle.displayName = 'DialogTitle';

// Dialog Description
const DialogDescription = React.forwardRef<HTMLParagraphElement, DialogDescriptionProps>(
  ({ className, children, ...props }, ref) => {
    const { descriptionId } = useDialog();

    return (
      <p
        ref={ref}
        id={descriptionId}
        className={cn('text-sm text-gray-600 dark:text-gray-400', className)}
        {...props}
      >
        {children}
      </p>
    );
  }
);
DialogDescription.displayName = 'DialogDescription';

// Dialog Close
const DialogClose = React.forwardRef<HTMLButtonElement, DialogCloseProps>(
  ({ className, children, onClick, ...props }, ref) => {
    const { onOpenChange } = useDialog();

    const handleClick = React.useCallback(
      (event: React.MouseEvent<HTMLButtonElement>) => {
        onClick?.(event);
        onOpenChange(false);
      },
      [onClick, onOpenChange]
    );

    return (
      <button
        ref={ref}
        className={cn(
          'absolute right-4 top-4 rounded-sm opacity-70 ring-offset-white',
          'transition-opacity hover:opacity-100 focus:outline-none focus:ring-2',
          'focus:ring-blue-500 focus:ring-offset-2 disabled:pointer-events-none',
          'data-[state=open]:bg-gray-100 data-[state=open]:text-gray-500',
          'dark:ring-offset-gray-950 dark:focus:ring-gray-300',
          'dark:data-[state=open]:bg-gray-800 dark:data-[state=open]:text-gray-400',
          className
        )}
        onClick={handleClick}
        aria-label='Fechar dialog'
        {...props}
      >
        {children || <X className='h-4 w-4' />}
        <span className='sr-only'>Fechar</span>
      </button>
    );
  }
);
DialogClose.displayName = 'DialogClose';

export {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
  DialogClose,
  DialogPortal,
  DialogOverlay,
};
