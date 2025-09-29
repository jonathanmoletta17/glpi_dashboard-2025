import * as React from "react"
import { cn } from "@/lib/utils"
import { generateId } from "@/utils/accessibility"
import { Input, InputProps } from "./input"
import { AlertCircle, CheckCircle, Info } from "lucide-react"

export interface FormFieldProps {
  children: React.ReactNode
  className?: string
}

export interface FormItemProps {
  children: React.ReactNode
  className?: string
}

export interface FormLabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  required?: boolean
  optional?: boolean
}

export interface FormControlProps {
  children: React.ReactNode
  className?: string
}

export interface FormDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode
}

export interface FormMessageProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children?: React.ReactNode
  type?: 'error' | 'success' | 'info'
}

// Context for form field state
interface FormFieldContextValue {
  id: string
  name?: string
  error?: string
  success?: string
  description?: string
  required?: boolean
  disabled?: boolean
}

const FormFieldContext = React.createContext<FormFieldContextValue | null>(null)

const useFormField = () => {
  const context = React.useContext(FormFieldContext)
  if (!context) {
    throw new Error('useFormField must be used within a FormField')
  }
  return context
}

// Form Field Provider
const FormField = React.forwardRef<HTMLDivElement, FormFieldProps>(
  ({ className, children, ...props }, ref) => {
    const id = generateId('form-field')

    const contextValue: FormFieldContextValue = {
      id,
    }

    return (
      <FormFieldContext.Provider value={contextValue}>
        <div
          ref={ref}
          className={cn("space-y-2", className)}
          {...props}
        >
          {children}
        </div>
      </FormFieldContext.Provider>
    )
  }
)
FormField.displayName = "FormField"

// Form Item
const FormItem = React.forwardRef<HTMLDivElement, FormItemProps>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("space-y-2", className)}
        {...props}
      />
    )
  }
)
FormItem.displayName = "FormItem"

// Form Label
const FormLabel = React.forwardRef<HTMLLabelElement, FormLabelProps>(
  ({ className, required, optional, children, ...props }, ref) => {
    const { id } = useFormField()

    return (
      <label
        ref={ref}
        htmlFor={id}
        className={cn(
          "block text-sm font-medium text-gray-700 dark:text-gray-300",
          "transition-colors duration-200",
          className
        )}
        {...props}
      >
        {children}
        {required && (
          <span
            className="text-red-500 ml-1"
            aria-label="campo obrigatório"
          >
            *
          </span>
        )}
        {optional && (
          <span
            className="text-gray-400 ml-1 text-xs font-normal"
            aria-label="campo opcional"
          >
            (opcional)
          </span>
        )}
      </label>
    )
  }
)
FormLabel.displayName = "FormLabel"

// Form Control
const FormControl = React.forwardRef<HTMLDivElement, FormControlProps>(
  ({ className, ...props }, ref) => {
    const { id, error, success, description } = useFormField()

    const ariaDescribedBy = React.useMemo(() => {
      const ids = []
      if (description) ids.push(`${id}-description`)
      if (error) ids.push(`${id}-error`)
      if (success) ids.push(`${id}-success`)
      return ids.length > 0 ? ids.join(' ') : undefined
    }, [id, description, error, success])

    return (
      <div
        ref={ref}
        className={className}
        {...props}
        aria-describedby={ariaDescribedBy}
      />
    )
  }
)
FormControl.displayName = "FormControl"

// Form Description
const FormDescription = React.forwardRef<HTMLParagraphElement, FormDescriptionProps>(
  ({ className, children, ...props }, ref) => {
    const { id } = useFormField()

    return (
      <p
        ref={ref}
        id={`${id}-description`}
        className={cn(
          "text-sm text-gray-600 dark:text-gray-400",
          className
        )}
        {...props}
      >
        {children}
      </p>
    )
  }
)
FormDescription.displayName = "FormDescription"

// Form Message
const FormMessage = React.forwardRef<HTMLParagraphElement, FormMessageProps>(
  ({ className, children, type = 'error', ...props }, ref) => {
    const { id } = useFormField()

    if (!children) return null

    const Icon = type === 'error' ? AlertCircle : type === 'success' ? CheckCircle : Info

    const colorClasses = {
      error: "text-red-600 dark:text-red-400",
      success: "text-green-600 dark:text-green-400",
      info: "text-blue-600 dark:text-blue-400"
    }

    const iconColorClasses = {
      error: "text-red-500",
      success: "text-green-500",
      info: "text-blue-500"
    }

    return (
      <p
        ref={ref}
        id={`${id}-${type}`}
        className={cn(
          "text-sm flex items-center space-x-1",
          colorClasses[type],
          className
        )}
        role={type === 'error' ? 'alert' : 'status'}
        aria-live="polite"
        {...props}
      >
        <Icon
          className={cn("w-4 h-4 flex-shrink-0", iconColorClasses[type])}
          aria-hidden="true"
        />
        <span>{children}</span>
      </p>
    )
  }
)
FormMessage.displayName = "FormMessage"

// Enhanced Form Input that integrates with form context
export interface FormInputProps extends Omit<InputProps, 'id' | 'aria-describedby'> {
  name?: string
}

const FormInput = React.forwardRef<HTMLInputElement, FormInputProps>(
  ({ name, ...props }, ref) => {
    const { id } = useFormField()

    return (
      <Input
        ref={ref}
        id={id}
        name={name}
        {...props}
      />
    )
  }
)
FormInput.displayName = "FormInput"

// Form Group - for grouping related form elements
export interface FormGroupProps {
  children: React.ReactNode
  className?: string
  legend?: string
  description?: string
  required?: boolean
}

const FormGroup = React.forwardRef<HTMLFieldSetElement, FormGroupProps>(
  ({ className, children, legend, description, required, ...props }, ref) => {
    const groupId = generateId('form-group')
    const descriptionId = description ? `${groupId}-description` : undefined

    return (
      <fieldset
        ref={ref}
        className={cn(
          "border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-4",
          className
        )}
        aria-describedby={descriptionId}
        {...props}
      >
        {legend && (
          <legend className="text-sm font-medium text-gray-900 dark:text-gray-100 px-2 -ml-2">
            {legend}
            {required && (
              <span
                className="text-red-500 ml-1"
                aria-label="grupo obrigatório"
              >
                *
              </span>
            )}
          </legend>
        )}

        {description && (
          <p
            id={descriptionId}
            className="text-sm text-gray-600 dark:text-gray-400 -mt-2"
          >
            {description}
          </p>
        )}

        {children}
      </fieldset>
    )
  }
)
FormGroup.displayName = "FormGroup"

export {
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
  FormInput,
  FormGroup,
  useFormField
}
