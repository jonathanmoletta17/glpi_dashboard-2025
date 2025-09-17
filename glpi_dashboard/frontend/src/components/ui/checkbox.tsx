import React, { useState, useRef, forwardRef } from 'react';
import { cn } from '../../lib/utils';
import { generateId, announceToScreenReader } from '../../utils/accessibility';

// Interface para props do Checkbox
interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange' | 'size'> {
  checked?: boolean;
  defaultChecked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
  disabled?: boolean;
  required?: boolean;
  indeterminate?: boolean;
  label?: string;
  description?: string;
  error?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'destructive';
  className?: string;
  labelClassName?: string;
}

// Componente Checkbox principal
export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(({
  checked,
  defaultChecked = false,
  onCheckedChange,
  disabled = false,
  required = false,
  indeterminate = false,
  label,
  description,
  error,
  size = 'md',
  variant = 'default',
  className,
  labelClassName,
  id,
  name,
  value,
  'aria-describedby': ariaDescribedBy,
  'aria-labelledby': ariaLabelledBy,
  ...props
}, ref) => {
  const [internalChecked, setInternalChecked] = useState(defaultChecked);
  const checkboxId = useRef(id || generateId('checkbox')).current;
  const descriptionId = useRef(generateId('checkbox-description')).current;
  const errorId = useRef(generateId('checkbox-error')).current;

  const isControlled = checked !== undefined;
  const isChecked = isControlled ? checked : internalChecked;

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newChecked = event.target.checked;

    if (!isControlled) {
      setInternalChecked(newChecked);
    }

    onCheckedChange?.(newChecked);

    // Anunciar mudança para leitores de tela
    const announcement = newChecked ? 'Marcado' : 'Desmarcado';
    announceToScreenReader(`${label || 'Checkbox'} ${announcement}`);
  };

  // Configurar aria-describedby
  const describedByIds: string[] = [];
  if (description) describedByIds.push(descriptionId);
  if (error) describedByIds.push(errorId);
  if (ariaDescribedBy) describedByIds.push(ariaDescribedBy);
  const finalAriaDescribedBy = describedByIds.length > 0 ? describedByIds.join(' ') : undefined;

  // Classes de tamanho
  const sizeClasses = {
    sm: 'h-3 w-3',
    md: 'h-4 w-4',
    lg: 'h-5 w-5'
  };

  // Classes de variante
  const variantClasses = {
    default: {
      checkbox: 'border-primary data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground',
      focus: 'focus-visible:ring-ring'
    },
    destructive: {
      checkbox: 'border-destructive data-[state=checked]:bg-destructive data-[state=checked]:text-destructive-foreground',
      focus: 'focus-visible:ring-destructive'
    }
  };

  const currentVariant = variantClasses[variant];

  return (
    <div className="flex items-start space-x-2">
      <div className="relative flex items-center">
        <input
          ref={ref}
          type="checkbox"
          id={checkboxId}
          name={name}
          value={value}
          checked={isChecked}
          onChange={handleChange}
          disabled={disabled}
          required={required}
          aria-describedby={finalAriaDescribedBy}
          aria-labelledby={ariaLabelledBy}
          aria-invalid={error ? 'true' : 'false'}
          data-state={indeterminate ? 'indeterminate' : isChecked ? 'checked' : 'unchecked'}
          className={cn(
            // Base styles
            'peer shrink-0 rounded-sm border border-primary shadow',
            'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-offset-2',
            'disabled:cursor-not-allowed disabled:opacity-50',
            'transition-all duration-200',
            // Size
            sizeClasses[size],
            // Variant
            currentVariant.checkbox,
            currentVariant.focus,
            // Error state
            error && 'border-destructive focus-visible:ring-destructive',
            className
          )}
          {...props}
        />

        {/* Custom checkbox indicator */}
        <div className={cn(
          'pointer-events-none absolute inset-0 flex items-center justify-center text-current opacity-0',
          'peer-data-[state=checked]:opacity-100 peer-data-[state=indeterminate]:opacity-100',
          'transition-opacity duration-200'
        )}>
          {indeterminate ? (
            <svg
              className={cn('fill-current', sizeClasses[size])}
              viewBox="0 0 16 16"
              aria-hidden="true"
            >
              <rect x="3" y="7" width="10" height="2" rx="1" />
            </svg>
          ) : (
            <svg
              className={cn('fill-current', sizeClasses[size])}
              viewBox="0 0 16 16"
              aria-hidden="true"
            >
              <path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z" />
            </svg>
          )}
        </div>
      </div>

      {/* Label e descrições */}
      {(label || description || error) && (
        <div className="flex flex-col space-y-1">
          {label && (
            <label
              htmlFor={checkboxId}
              className={cn(
                'text-sm font-medium leading-none',
                'peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
                error && 'text-destructive',
                labelClassName
              )}
            >
              {label}
              {required && (
                <span className="ml-1 text-destructive" aria-label="obrigatório">
                  *
                </span>
              )}
            </label>
          )}

          {description && (
            <p
              id={descriptionId}
              className="text-sm text-muted-foreground"
            >
              {description}
            </p>
          )}

          {error && (
            <p
              id={errorId}
              className="text-sm text-destructive"
              role="alert"
              aria-live="polite"
            >
              {error}
            </p>
          )}
        </div>
      )}
    </div>
  );
});

Checkbox.displayName = 'Checkbox';

// Componente CheckboxGroup para múltiplas opções
interface CheckboxOption {
  value: string;
  label: string;
  description?: string;
  disabled?: boolean;
}

interface CheckboxGroupProps {
  options: CheckboxOption[];
  value?: string[];
  defaultValue?: string[];
  onValueChange?: (value: string[]) => void;
  disabled?: boolean;
  required?: boolean;
  label?: string;
  description?: string;
  error?: string;
  orientation?: 'horizontal' | 'vertical';
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'destructive';
  className?: string;
  name?: string;
}

export const CheckboxGroup: React.FC<CheckboxGroupProps> = ({
  options,
  value,
  defaultValue = [],
  onValueChange,
  disabled = false,
  required = false,
  label,
  description,
  error,
  orientation = 'vertical',
  size = 'md',
  variant = 'default',
  className,
  name
}) => {
  const [internalValue, setInternalValue] = useState<string[]>(defaultValue);
  const groupId = useRef(generateId('checkbox-group')).current;
  const descriptionId = useRef(generateId('checkbox-group-description')).current;
  const errorId = useRef(generateId('checkbox-group-error')).current;

  const isControlled = value !== undefined;
  const currentValue = isControlled ? value : internalValue;

  const handleValueChange = (optionValue: string, checked: boolean) => {
    let newValue: string[];

    if (checked) {
      newValue = [...currentValue, optionValue];
    } else {
      newValue = currentValue.filter(v => v !== optionValue);
    }

    if (!isControlled) {
      setInternalValue(newValue);
    }

    onValueChange?.(newValue);
  };

  // Configurar aria-describedby
  const describedByIds: string[] = [];
  if (description) describedByIds.push(descriptionId);
  if (error) describedByIds.push(errorId);
  const finalAriaDescribedBy = describedByIds.length > 0 ? describedByIds.join(' ') : undefined;

  return (
    <fieldset
      className={cn('space-y-3', className)}
      aria-describedby={finalAriaDescribedBy}
      aria-invalid={error ? 'true' : 'false'}
      aria-required={required}
    >
      {label && (
        <legend className="text-sm font-medium leading-none">
          {label}
          {required && (
            <span className="ml-1 text-destructive" aria-label="obrigatório">
              *
            </span>
          )}
        </legend>
      )}

      {description && (
        <p
          id={descriptionId}
          className="text-sm text-muted-foreground"
        >
          {description}
        </p>
      )}

      <div className={cn(
        'space-y-2',
        orientation === 'horizontal' && 'flex flex-wrap gap-4 space-y-0'
      )}>
        {options.map((option, index) => (
          <Checkbox
            key={option.value}
            name={name}
            value={option.value}
            checked={currentValue.includes(option.value)}
            onCheckedChange={(checked) => handleValueChange(option.value, checked)}
            disabled={disabled || option.disabled}
            label={option.label}
            description={option.description}
            size={size}
            variant={variant}
            aria-describedby={finalAriaDescribedBy}
          />
        ))}
      </div>

      {error && (
        <p
          id={errorId}
          className="text-sm text-destructive"
          role="alert"
          aria-live="polite"
        >
          {error}
        </p>
      )}
    </fieldset>
  );
};

// Hook personalizado para gerenciar estado de checkbox
export const useCheckbox = ({
  defaultChecked = false,
  onChange
}: {
  defaultChecked?: boolean;
  onChange?: (checked: boolean) => void;
} = {}) => {
  const [checked, setChecked] = useState(defaultChecked);

  const handleChange = (newChecked: boolean) => {
    setChecked(newChecked);
    onChange?.(newChecked);
  };

  const toggle = () => handleChange(!checked);
  const check = () => handleChange(true);
  const uncheck = () => handleChange(false);

  return {
    checked,
    setChecked: handleChange,
    toggle,
    check,
    uncheck
  };
};

export default Checkbox;
