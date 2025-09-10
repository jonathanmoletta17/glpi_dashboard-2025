import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';

import { cn } from '@/lib/utils';

const buttonVariants = cva(
  // Base styles com design system expandido
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0',
  {
    variants: {
      variant: {
        // Shadcn UI compatibility
        default:
          'bg-primary text-primary-foreground shadow-sm hover:bg-primary/90 focus-visible:ring-primary active:scale-[0.98]',
        destructive:
          'bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90 focus-visible:ring-destructive active:scale-[0.98]',
        outline:
          'border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground focus-visible:ring-ring active:scale-[0.98]',
        secondary:
          'bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80 focus-visible:ring-secondary active:scale-[0.98]',
        ghost:
          'hover:bg-accent hover:text-accent-foreground focus-visible:ring-ring active:scale-[0.98]',
        link: 'text-primary underline-offset-4 hover:underline focus-visible:ring-primary',

        // Design system expandido
        primary:
          'bg-primary-500 text-white shadow-sm hover:bg-primary-600 hover:shadow-md focus-visible:ring-primary-500 active:bg-primary-700 active:scale-[0.98]',
        success:
          'bg-success-500 text-white shadow-sm hover:bg-success-600 hover:shadow-md focus-visible:ring-success-500 active:bg-success-700 active:scale-[0.98]',
        warning:
          'bg-warning-500 text-white shadow-sm hover:bg-warning-600 hover:shadow-md focus-visible:ring-warning-500 active:bg-warning-700 active:scale-[0.98]',
        danger:
          'bg-danger-500 text-white shadow-sm hover:bg-danger-600 hover:shadow-md focus-visible:ring-danger-500 active:bg-danger-700 active:scale-[0.98]',
      },
      size: {
        default: 'h-9 px-4 py-2',
        xs: 'h-7 px-2 text-xs rounded-md',
        sm: 'h-8 px-3 text-xs rounded-md',
        lg: 'h-10 px-6 text-base rounded-md',
        xl: 'h-12 px-8 text-base rounded-lg',
        icon: 'h-9 w-9',
      },
      loading: {
        true: 'cursor-not-allowed',
        false: '',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
      loading: false,
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  loadingText?: string;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      asChild = false,
      loading = false,
      leftIcon,
      rightIcon,
      loadingText,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const Comp = asChild ? Slot : 'button';
    const isDisabled = disabled || loading;

    return (
      <Comp
        className={cn(buttonVariants({ variant, size, loading, className }))}
        ref={ref}
        disabled={isDisabled}
        aria-disabled={isDisabled}
        aria-busy={loading}
        aria-label={loading ? loadingText || 'Carregando...' : undefined}
        {...props}
      >
        {loading && (
          <svg
            className='animate-spin h-4 w-4'
            xmlns='http://www.w3.org/2000/svg'
            fill='none'
            viewBox='0 0 24 24'
            role='img'
            aria-label='Carregando'
          >
            <circle
              className='opacity-25'
              cx='12'
              cy='12'
              r='10'
              stroke='currentColor'
              strokeWidth='4'
            />
            <path
              className='opacity-75'
              fill='currentColor'
              d='M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z'
            />
          </svg>
        )}
        {!loading && leftIcon && leftIcon}
        {loading ? loadingText || 'Carregando...' : children}
        {!loading && rightIcon && rightIcon}
      </Comp>
    );
  }
);
Button.displayName = 'Button';

export { Button, buttonVariants };
