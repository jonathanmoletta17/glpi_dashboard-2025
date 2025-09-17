import * as React from "react"
import { cn } from "@/lib/utils"
import { generateId } from "@/utils/accessibility"
import { Eye, EyeOff, AlertCircle, CheckCircle } from "lucide-react"

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  description?: string
  error?: string
  success?: string
  showPasswordToggle?: boolean
  loading?: boolean
  leftIcon?: React.ComponentType<{ className?: string }>
  rightIcon?: React.ComponentType<{ className?: string }>
  onClear?: () => void
  clearable?: boolean
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({
    className,
    type = "text",
    label,
    description,
    error,
    success,
    showPasswordToggle = false,
    loading = false,
    leftIcon: LeftIcon,
    rightIcon: RightIcon,
    onClear,
    clearable = false,
    disabled,
    required,
    value,
    id,
    ...props
  }, ref) => {
    const [showPassword, setShowPassword] = React.useState(false)
    const [isFocused, setIsFocused] = React.useState(false)

    const inputId = id || generateId('input')
    const descriptionId = description ? generateId('input-description') : undefined
    const errorId = error ? generateId('input-error') : undefined
    const successId = success ? generateId('input-success') : undefined

    const isPassword = type === 'password'
    const actualType = isPassword && showPassword ? 'text' : type
    const hasValue = value !== undefined && value !== ''
    const canClear = clearable && hasValue && !disabled && !loading

    const handlePasswordToggle = React.useCallback(() => {
      setShowPassword(!showPassword)
    }, [showPassword])

    const handleClear = React.useCallback(() => {
      onClear?.()
    }, [onClear])

    const handleFocus = React.useCallback((e: React.FocusEvent<HTMLInputElement>) => {
      setIsFocused(true)
      props.onFocus?.(e)
    }, [props.onFocus])

    const handleBlur = React.useCallback((e: React.FocusEvent<HTMLInputElement>) => {
      setIsFocused(false)
      props.onBlur?.(e)
    }, [props.onBlur])

    const ariaDescribedBy = React.useMemo(() => {
      const ids: string[] = []
      if (descriptionId) ids.push(descriptionId)
      if (errorId) ids.push(errorId)
      if (successId) ids.push(successId)
      return ids.length > 0 ? ids.join(' ') : undefined
    }, [descriptionId, errorId, successId])

    return (
      <div className="space-y-2">
        {label && (
          <label
            htmlFor={inputId}
            className={cn(
              "block text-sm font-medium transition-colors",
              error ? "text-red-700 dark:text-red-400" : "text-gray-700 dark:text-gray-300",
              disabled && "opacity-50"
            )}
          >
            {label}
            {required && (
              <span className="text-red-500 ml-1" aria-label="obrigatório">
                *
              </span>
            )}
          </label>
        )}

        <div className="relative">
          {/* Left Icon */}
          {LeftIcon && (
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
              <LeftIcon
                className={cn(
                  "w-4 h-4",
                  error ? "text-red-500" : "text-gray-400 dark:text-gray-500",
                  isFocused && !error && "text-blue-500"
                )}
                aria-hidden="true"
              />
            </div>
          )}

          <input
            ref={ref}
            type={actualType}
            id={inputId}
            className={cn(
              "flex h-10 w-full rounded-md border px-3 py-2 text-sm transition-colors",
              "file:border-0 file:bg-transparent file:text-sm file:font-medium",
              "placeholder:text-gray-500 dark:placeholder:text-gray-400",
              "focus:outline-none focus:ring-2 focus:ring-offset-2",
              "disabled:cursor-not-allowed disabled:opacity-50",
              // Base styles
              "bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100",
              // Border and focus states
              error
                ? "border-red-300 dark:border-red-700 focus:border-red-500 focus:ring-red-500/20"
                : success
                ? "border-green-300 dark:border-green-700 focus:border-green-500 focus:ring-green-500/20"
                : "border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-blue-500/20",
              // Icon padding
              LeftIcon && "pl-10",
              (RightIcon || isPassword || canClear || loading) && "pr-10",
              className
            )}
            disabled={disabled || loading}
            required={required}
            value={value}
            onFocus={handleFocus}
            onBlur={handleBlur}
            aria-describedby={ariaDescribedBy}
            aria-invalid={error ? 'true' : 'false'}
            aria-required={required}
            {...props}
          />

          {/* Right Side Icons */}
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-1">
            {loading && (
              <div className="animate-spin w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full" aria-hidden="true" />
            )}

            {canClear && (
              <button
                type="button"
                onClick={handleClear}
                className="p-0.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-500 rounded"
                aria-label="Limpar campo"
                tabIndex={-1}
              >
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            )}

            {isPassword && showPasswordToggle && (
              <button
                type="button"
                onClick={handlePasswordToggle}
                className="p-0.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-500 rounded"
                aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
                tabIndex={-1}
              >
                {showPassword ? (
                  <EyeOff className="w-4 h-4" aria-hidden="true" />
                ) : (
                  <Eye className="w-4 h-4" aria-hidden="true" />
                )}
              </button>
            )}

            {RightIcon && !loading && !canClear && !(isPassword && showPasswordToggle) && (
              <RightIcon
                className={cn(
                  "w-4 h-4",
                  error ? "text-red-500" : "text-gray-400 dark:text-gray-500",
                  isFocused && !error && "text-blue-500"
                )}
                aria-hidden="true"
              />
            )}

            {/* Status Icons */}
            {error && (
              <AlertCircle className="w-4 h-4 text-red-500" aria-hidden="true" />
            )}

            {success && !error && (
              <CheckCircle className="w-4 h-4 text-green-500" aria-hidden="true" />
            )}
          </div>
        </div>

        {/* Description */}
        {description && (
          <p
            id={descriptionId}
            className="text-sm text-gray-600 dark:text-gray-400"
          >
            {description}
          </p>
        )}

        {/* Error Message */}
        {error && (
          <p
            id={errorId}
            className="text-sm text-red-600 dark:text-red-400 flex items-center space-x-1"
            role="alert"
            aria-live="polite"
          >
            <AlertCircle className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
            <span>{error}</span>
          </p>
        )}

        {/* Success Message */}
        {success && !error && (
          <p
            id={successId}
            className="text-sm text-green-600 dark:text-green-400 flex items-center space-x-1"
            role="status"
            aria-live="polite"
          >
            <CheckCircle className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
            <span>{success}</span>
          </p>
        )}
      </div>
    )
  }
)

Input.displayName = "Input"

export { Input }
