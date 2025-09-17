import * as React from "react"
import { cn } from "@/lib/utils"
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from "lucide-react"
import { createPortal } from "react-dom"
import { generateId } from "@/utils/accessibility"

export type ToastVariant = "default" | "success" | "error" | "warning" | "info"

export interface ToastProps {
  id?: string
  title?: string
  description?: string
  variant?: ToastVariant
  duration?: number
  onClose?: () => void
  action?: React.ReactNode
  className?: string
}

export interface ToastContextValue {
  toasts: ToastProps[]
  addToast: (toast: Omit<ToastProps, 'id'>) => string
  removeToast: (id: string) => void
  clearToasts: () => void
}

const ToastContext = React.createContext<ToastContextValue | null>(null)

export const useToast = () => {
  const context = React.useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}

// Toast variants configuration
const toastVariants = {
  default: {
    className: "bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100",
    icon: Info,
    iconColor: "text-blue-500"
  },
  success: {
    className: "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-900 dark:text-green-100",
    icon: CheckCircle,
    iconColor: "text-green-500"
  },
  error: {
    className: "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-900 dark:text-red-100",
    icon: AlertCircle,
    iconColor: "text-red-500"
  },
  warning: {
    className: "bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800 text-yellow-900 dark:text-yellow-100",
    icon: AlertTriangle,
    iconColor: "text-yellow-500"
  },
  info: {
    className: "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-900 dark:text-blue-100",
    icon: Info,
    iconColor: "text-blue-500"
  }
}

// Individual Toast Component
const Toast = React.forwardRef<HTMLDivElement, ToastProps>(
  ({ id, title, description, variant = "default", onClose, action, className, ...props }, ref) => {
    const toastRef = React.useRef<HTMLDivElement>(null)
    const variantConfig = toastVariants[variant]
    const Icon = variantConfig.icon
    const titleId = generateId('toast-title')
    const descriptionId = generateId('toast-description')

    // Auto-focus for screen readers
    React.useEffect(() => {
      if (toastRef.current) {
        toastRef.current.focus()
      }
    }, [])

    return (
      <div
        ref={(node) => {
          if (typeof ref === 'function') ref(node)
          else if (ref) ref.current = node
          toastRef.current = node
        }}
        className={cn(
          "group pointer-events-auto relative flex w-full items-center justify-between space-x-4 overflow-hidden rounded-md border p-4 pr-8 shadow-lg transition-all",
          "data-[swipe=cancel]:translate-x-0 data-[swipe=end]:translate-x-[var(--radix-toast-swipe-end-x)] data-[swipe=move]:translate-x-[var(--radix-toast-swipe-move-x)] data-[swipe=move]:transition-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[swipe=end]:animate-out data-[state=closed]:fade-out-80 data-[state=closed]:slide-out-to-right-full data-[state=open]:slide-in-from-top-full data-[state=open]:sm:slide-in-from-bottom-full",
          variantConfig.className,
          className
        )}
        role="alert"
        aria-live={variant === "error" ? "assertive" : "polite"}
        aria-labelledby={title ? titleId : undefined}
        aria-describedby={description ? descriptionId : undefined}
        tabIndex={-1}
        {...props}
      >
        <div className="flex items-start space-x-3">
          <Icon className={cn("h-5 w-5 mt-0.5 flex-shrink-0", variantConfig.iconColor)} aria-hidden="true" />
          <div className="flex-1 space-y-1">
            {title && (
              <div id={titleId} className="text-sm font-semibold">
                {title}
              </div>
            )}
            {description && (
              <div id={descriptionId} className="text-sm opacity-90">
                {description}
              </div>
            )}
            {action && (
              <div className="mt-2">
                {action}
              </div>
            )}
          </div>
        </div>

        {onClose && (
          <button
            onClick={onClose}
            className={cn(
              "absolute right-2 top-2 rounded-md p-1 opacity-0 transition-opacity hover:opacity-100 focus:opacity-100 focus:outline-none focus:ring-2 focus:ring-offset-2",
              variant === "default" && "focus:ring-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700",
              variant === "success" && "focus:ring-green-400 hover:bg-green-100 dark:hover:bg-green-800",
              variant === "error" && "focus:ring-red-400 hover:bg-red-100 dark:hover:bg-red-800",
              variant === "warning" && "focus:ring-yellow-400 hover:bg-yellow-100 dark:hover:bg-yellow-800",
              variant === "info" && "focus:ring-blue-400 hover:bg-blue-100 dark:hover:bg-blue-800",
              "group-hover:opacity-100"
            )}
            aria-label="Fechar notificação"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    )
  }
)
Toast.displayName = "Toast"

// Toast Provider
export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = React.useState<ToastProps[]>([])

  const addToast = React.useCallback((toast: Omit<ToastProps, 'id'>) => {
    const id = generateId('toast')
    const newToast: ToastProps = {
      ...toast,
      id,
      duration: toast.duration ?? 5000
    }

    setToasts(prev => [...prev, newToast])

    // Auto-remove toast after duration
    if (newToast.duration && newToast.duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, newToast.duration)
    }

    return id
  }, [])

  const removeToast = React.useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }, [])

  const clearToasts = React.useCallback(() => {
    setToasts([])
  }, [])

  const contextValue: ToastContextValue = {
    toasts,
    addToast,
    removeToast,
    clearToasts
  }

  return (
    <ToastContext.Provider value={contextValue}>
      {children}
      <ToastViewport />
    </ToastContext.Provider>
  )
}

// Toast Viewport (renders toasts)
const ToastViewport: React.FC = () => {
  const { toasts, removeToast } = useToast()

  if (toasts.length === 0) return null

  return createPortal(
    <div
      className="fixed top-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 sm:bottom-0 sm:right-0 sm:top-auto sm:flex-col md:max-w-[420px]"
      role="region"
      aria-label="Notificações"
      aria-live="polite"
    >
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          {...toast}
          onClose={() => removeToast(toast.id!)}
        />
      ))}
    </div>,
    document.body
  )
}

// Utility functions for common toast types
export const toast = {
  success: (message: string, options?: Partial<ToastProps>) => {
    const { addToast } = React.useContext(ToastContext) || {}
    if (!addToast) throw new Error('toast.success must be used within ToastProvider')
    return addToast({ ...options, variant: 'success', description: message })
  },
  error: (message: string, options?: Partial<ToastProps>) => {
    const { addToast } = React.useContext(ToastContext) || {}
    if (!addToast) throw new Error('toast.error must be used within ToastProvider')
    return addToast({ ...options, variant: 'error', description: message })
  },
  warning: (message: string, options?: Partial<ToastProps>) => {
    const { addToast } = React.useContext(ToastContext) || {}
    if (!addToast) throw new Error('toast.warning must be used within ToastProvider')
    return addToast({ ...options, variant: 'warning', description: message })
  },
  info: (message: string, options?: Partial<ToastProps>) => {
    const { addToast } = React.useContext(ToastContext) || {}
    if (!addToast) throw new Error('toast.info must be used within ToastProvider')
    return addToast({ ...options, variant: 'info', description: message })
  },
  default: (message: string, options?: Partial<ToastProps>) => {
    const { addToast } = React.useContext(ToastContext) || {}
    if (!addToast) throw new Error('toast.default must be used within ToastProvider')
    return addToast({ ...options, variant: 'default', description: message })
  }
}

export { Toast, ToastViewport }
