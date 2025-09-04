import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';

import { cn } from '@/lib/utils';

const badgeVariants = cva(
  // Base styles com design system expandido
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        // Shadcn UI compatibility
        default: 'border-transparent bg-primary text-primary-foreground shadow hover:bg-primary/80',
        secondary: 'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
        destructive: 'border-transparent bg-destructive text-destructive-foreground shadow hover:bg-destructive/80',
        outline: 'text-foreground',

        // Design system expandido - Status
        success: 'border-transparent bg-success-500 text-white hover:bg-success-600',
        warning: 'border-transparent bg-warning-500 text-white hover:bg-warning-600',
        danger: 'border-transparent bg-danger-500 text-white hover:bg-danger-600',
        info: 'border-transparent bg-blue-500 text-white hover:bg-blue-600',

        // Design system expandido - Prioridades
        'priority-urgent': 'border-transparent bg-red-600 text-white animate-pulse',
        'priority-high': 'border-transparent bg-orange-500 text-white',
        'priority-medium': 'border-transparent bg-yellow-500 text-black',
        'priority-low': 'border-transparent bg-green-500 text-white',

        // Design system expandido - Status de tickets
        'status-new': 'border-transparent bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
        'status-assigned': 'border-transparent bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
        'status-planned': 'border-transparent bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
        'status-waiting': 'border-transparent bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
        'status-solved': 'border-transparent bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
        'status-closed': 'border-transparent bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
      },
      size: {
        sm: 'px-2 py-0.5 text-xs',
        default: 'px-2.5 py-0.5 text-xs',
        lg: 'px-3 py-1 text-sm',
      },
      interactive: {
        true: 'cursor-pointer hover:scale-105 active:scale-95',
        false: '',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
      interactive: false,
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  removable?: boolean;
  onRemove?: () => void;
}

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({
    className,
    variant,
    size,
    interactive,
    leftIcon,
    rightIcon,
    removable = false,
    onRemove,
    children,
    ...props
  }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(badgeVariants({ variant, size, interactive: interactive || removable, className }))}
        {...props}
      >
        {leftIcon && (
          <span className="mr-1 flex-shrink-0">
            {leftIcon}
          </span>
        )}
        <span className="truncate">{children}</span>
        {rightIcon && (
          <span className="ml-1 flex-shrink-0">
            {rightIcon}
          </span>
        )}
        {removable && (
          <button
            type="button"
            className="ml-1 flex-shrink-0 rounded-full p-0.5 hover:bg-black/10 focus:outline-none focus:ring-1 focus:ring-white"
            onClick={onRemove}
          >
            <svg
              className="h-3 w-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>
    );
  }
);
Badge.displayName = 'Badge';

export { Badge, badgeVariants };
