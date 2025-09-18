import React, { useState, useRef, useEffect, createContext, useContext } from 'react';
import { cn } from '../../lib/utils';
import { generateId, handleArrowNavigation, handleTypeAheadNavigation, announceToScreenReader } from '../../utils/accessibility';

// Context para gerenciar estado do Select
interface SelectContextType {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  value: string;
  onValueChange: (value: string) => void;
  triggerId: string;
  contentId: string;
  labelId?: string;
  disabled?: boolean;
}

const SelectContext = createContext<SelectContextType | null>(null);

const useSelectContext = () => {
  const context = useContext(SelectContext);
  if (!context) {
    throw new Error('Select components must be used within a Select');
  }
  return context;
};

// Componente principal Select
interface SelectProps {
  children: React.ReactNode;
  value?: string;
  defaultValue?: string;
  onValueChange?: (value: string) => void;
  disabled?: boolean;
  name?: string;
  required?: boolean;
}

export const Select: React.FC<SelectProps> = ({
  children,
  value,
  defaultValue = '',
  onValueChange,
  disabled = false,
  name,
  required = false
}) => {
  const [internalValue, setInternalValue] = useState(defaultValue);
  const [isOpen, setIsOpen] = useState(false);
  const triggerId = useRef(generateId('select-trigger')).current;
  const contentId = useRef(generateId('select-content')).current;
  const labelId = useRef(generateId('select-label')).current;

  const currentValue = value !== undefined ? value : internalValue;

  const handleValueChange = (newValue: string) => {
    if (value === undefined) {
      setInternalValue(newValue);
    }
    onValueChange?.(newValue);
    setIsOpen(false);
    announceToScreenReader(`Selecionado: ${newValue}`);
  };

  const contextValue: SelectContextType = {
    isOpen,
    setIsOpen,
    value: currentValue,
    onValueChange: handleValueChange,
    triggerId,
    contentId,
    labelId,
    disabled
  };

  return (
    <SelectContext.Provider value={contextValue}>
      <div className="relative">
        {children}
        {/* Hidden input for form submission */}
        {name && (
          <input
            type="hidden"
            name={name}
            value={currentValue}
            required={required}
          />
        )}
      </div>
    </SelectContext.Provider>
  );
};

// Componente SelectTrigger
interface SelectTriggerProps {
  children: React.ReactNode;
  className?: string;
  placeholder?: string;
}

export const SelectTrigger: React.FC<SelectTriggerProps> = ({
  children,
  className,
  placeholder = 'Selecione uma opção'
}) => {
  const { isOpen, setIsOpen, value, triggerId, contentId, labelId, disabled } = useSelectContext();
  const triggerRef = useRef<HTMLButtonElement>(null);

  const handleClick = () => {
    if (!disabled) {
      setIsOpen(!isOpen);
    }
  };

  const handleKeyDown = (event: KeyboardEvent) => {
    if (disabled) return;

    switch (event.key) {
      case 'Enter':
      case ' ':
      case 'ArrowDown':
      case 'ArrowUp':
        event.preventDefault();
        setIsOpen(true);
        break;
      case 'Escape':
        if (isOpen) {
          event.preventDefault();
          setIsOpen(false);
          triggerRef.current?.focus();
        }
        break;
    }
  };

  useEffect(() => {
    const trigger = triggerRef.current;
    if (trigger) {
      trigger.addEventListener('keydown', handleKeyDown);
      return () => trigger.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, disabled]);

  return (
    <button
      ref={triggerRef}
      id={triggerId}
      type="button"
      role="combobox"
      aria-expanded={isOpen}
      aria-haspopup="listbox"
      aria-controls={contentId}
      aria-labelledby={labelId}
      aria-describedby={disabled ? undefined : `${triggerId}-description`}
      disabled={disabled}
      onClick={handleClick}
      className={cn(
        'flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background',
        'placeholder:text-muted-foreground',
        'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
        'disabled:cursor-not-allowed disabled:opacity-50',
        'hover:bg-accent hover:text-accent-foreground',
        'transition-colors duration-200',
        className
      )}
    >
      <span className={cn('block truncate', !value && 'text-muted-foreground')}>
        {children || placeholder}
      </span>
      <svg
        className={cn(
          'h-4 w-4 opacity-50 transition-transform duration-200',
          isOpen && 'rotate-180'
        )}
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>

      {/* Screen reader description */}
      <span id={`${triggerId}-description`} className="sr-only">
        Use as setas para navegar pelas opções. Pressione Enter ou Espaço para abrir.
      </span>
    </button>
  );
};

// Componente SelectContent
interface SelectContentProps {
  children: React.ReactNode;
  className?: string;
  position?: 'top' | 'bottom' | 'auto';
  maxHeight?: string;
}

export const SelectContent: React.FC<SelectContentProps> = ({
  children,
  className,
  position = 'auto',
  maxHeight = '200px'
}) => {
  const { isOpen, setIsOpen, contentId, triggerId } = useSelectContext();
  const contentRef = useRef<HTMLDivElement>(null);
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const optionsRef = useRef<HTMLElement[]>([]);

  // Gerenciar navegação por teclado
  const handleKeyDown = (event: KeyboardEvent) => {
    const options = optionsRef.current.filter(Boolean);
    if (options.length === 0) return;

    switch (event.key) {
      case 'Escape':
        event.preventDefault();
        setIsOpen(false);
        document.getElementById(triggerId)?.focus();
        break;
      case 'Tab':
        setIsOpen(false);
        break;
      case 'ArrowDown':
      case 'ArrowUp':
        event.preventDefault();
        const newIndex = handleArrowNavigation(
          event,
          options,
          focusedIndex,
          {
            orientation: 'vertical',
            loop: true,
            onIndexChange: setFocusedIndex
          }
        );
        setFocusedIndex(newIndex);
        break;
      case 'Home':
        event.preventDefault();
        setFocusedIndex(0);
        options[0]?.focus();
        break;
      case 'End':
        event.preventDefault();
        const lastIndex = options.length - 1;
        setFocusedIndex(lastIndex);
        options[lastIndex]?.focus();
        break;
      default:
        // Type-ahead navigation
        handleTypeAheadNavigation(
          event,
          options,
          focusedIndex,
          {
            getItemText: (item) => item.textContent || '',
            onIndexChange: setFocusedIndex
          }
        );
        break;
    }
  };

  // Configurar event listeners quando aberto
  useEffect(() => {
    if (isOpen && contentRef.current) {
      const content = contentRef.current;
      content.addEventListener('keydown', handleKeyDown);

      // Focar primeiro item quando abrir
      const firstOption = optionsRef.current[0];
      if (firstOption) {
        firstOption.focus();
        setFocusedIndex(0);
      }

      return () => {
        content.removeEventListener('keydown', handleKeyDown);
      };
    }
  }, [isOpen, focusedIndex]);

  // Fechar ao clicar fora
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      const trigger = document.getElementById(triggerId);
      const content = contentRef.current;

      if (content && !content.contains(target) && trigger && !trigger.contains(target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, triggerId, setIsOpen]);

  if (!isOpen) return null;

  return (
    <div
      ref={contentRef}
      id={contentId}
      role="listbox"
      aria-labelledby={triggerId}
      className={cn(
        'absolute z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md',
        'animate-in fade-in-0 zoom-in-95',
        'data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2',
        'data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2',
        position === 'top' && 'bottom-full mb-1',
        position === 'bottom' && 'top-full mt-1',
        className
      )}
      style={{ maxHeight }}
    >
      <div className="overflow-auto" style={{ maxHeight }}>
        {React.Children.map(children, (child, index) => {
          if (React.isValidElement(child)) {
            return React.cloneElement(child, {
              ...child.props,
              ref: (el: HTMLElement) => {
                optionsRef.current[index] = el;
              },
              'data-index': index
            });
          }
          return child;
        })}
      </div>
    </div>
  );
};

// Componente SelectItem
interface SelectItemProps {
  children: React.ReactNode;
  value: string;
  disabled?: boolean;
  className?: string;
}

export const SelectItem = React.forwardRef<HTMLDivElement, SelectItemProps>(({
  children,
  value,
  disabled = false,
  className,
  ...props
}, ref) => {
  const { value: selectedValue, onValueChange, setIsOpen } = useSelectContext();
  const isSelected = selectedValue === value;

  const handleClick = () => {
    if (!disabled) {
      onValueChange(value);
      setIsOpen(false);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      if (!disabled) {
        onValueChange(value);
        setIsOpen(false);
      }
    }
  };

  return (
    <div
      ref={ref}
      role="option"
      aria-selected={isSelected}
      aria-disabled={disabled}
      tabIndex={disabled ? -1 : 0}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      className={cn(
        'relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none',
        'focus:bg-accent focus:text-accent-foreground',
        'data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
        disabled && 'pointer-events-none opacity-50',
        isSelected && 'bg-accent text-accent-foreground',
        className
      )}
      {...props}
    >
      {isSelected && (
        <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
          <svg
            className="h-4 w-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </span>
      )}
      <span className="block truncate">{children}</span>
    </div>
  );
});

SelectItem.displayName = 'SelectItem';

// Componente SelectLabel
interface SelectLabelProps {
  children: React.ReactNode;
  className?: string;
}

export const SelectLabel: React.FC<SelectLabelProps> = ({ children, className }) => {
  const { labelId } = useSelectContext();

  return (
    <label
      id={labelId}
      className={cn('px-2 py-1.5 text-sm font-semibold', className)}
    >
      {children}
    </label>
  );
};

// Componente SelectSeparator
interface SelectSeparatorProps {
  className?: string;
}

export const SelectSeparator: React.FC<SelectSeparatorProps> = ({ className }) => {
  return (
    <div
      role="separator"
      aria-orientation="horizontal"
      className={cn('-mx-1 my-1 h-px bg-muted', className)}
    />
  );
};

// Componente SelectValue (para mostrar valor selecionado)
interface SelectValueProps {
  placeholder?: string;
  className?: string;
}

export const SelectValue: React.FC<SelectValueProps> = ({
  placeholder = 'Selecione uma opção',
  className
}) => {
  const { value } = useSelectContext();

  return (
    <span className={cn('block truncate', !value && 'text-muted-foreground', className)}>
      {value || placeholder}
    </span>
  );
};

// Export do componente composto
export default {
  Root: Select,
  Trigger: SelectTrigger,
  Content: SelectContent,
  Item: SelectItem,
  Label: SelectLabel,
  Separator: SelectSeparator,
  Value: SelectValue
};
