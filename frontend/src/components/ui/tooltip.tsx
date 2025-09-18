import * as React from "react"
import { cn } from "@/lib/utils"
import { generateId } from "@/utils/accessibility"
import { createPortal } from "react-dom"

export interface TooltipProps {
  children: React.ReactNode
  content: React.ReactNode
  side?: "top" | "right" | "bottom" | "left"
  align?: "start" | "center" | "end"
  delayDuration?: number
  skipDelayDuration?: number
  disableHoverableContent?: boolean
  disabled?: boolean
  className?: string
  contentClassName?: string
}

export interface TooltipContextValue {
  open: boolean
  setOpen: (open: boolean) => void
  contentId: string
  triggerId: string
}

const TooltipContext = React.createContext<TooltipContextValue | null>(null)

const useTooltip = () => {
  const context = React.useContext(TooltipContext)
  if (!context) {
    throw new Error('Tooltip components must be used within a Tooltip')
  }
  return context
}

// Position calculation utilities
const getTooltipPosition = (
  triggerRect: DOMRect,
  tooltipRect: DOMRect,
  side: "top" | "right" | "bottom" | "left",
  align: "start" | "center" | "end"
) => {
  const offset = 8 // Distance from trigger
  let x = 0
  let y = 0

  // Calculate base position based on side
  switch (side) {
    case "top":
      y = triggerRect.top - tooltipRect.height - offset
      break
    case "bottom":
      y = triggerRect.bottom + offset
      break
    case "left":
      x = triggerRect.left - tooltipRect.width - offset
      break
    case "right":
      x = triggerRect.right + offset
      break
  }

  // Calculate alignment
  if (side === "top" || side === "bottom") {
    switch (align) {
      case "start":
        x = triggerRect.left
        break
      case "center":
        x = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2
        break
      case "end":
        x = triggerRect.right - tooltipRect.width
        break
    }
  } else {
    switch (align) {
      case "start":
        y = triggerRect.top
        break
      case "center":
        y = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2
        break
      case "end":
        y = triggerRect.bottom - tooltipRect.height
        break
    }
  }

  // Ensure tooltip stays within viewport
  const padding = 8
  x = Math.max(padding, Math.min(x, window.innerWidth - tooltipRect.width - padding))
  y = Math.max(padding, Math.min(y, window.innerHeight - tooltipRect.height - padding))

  return { x, y }
}

// Main Tooltip component
const Tooltip: React.FC<TooltipProps> = ({
  children,
  content,
  side = "top",
  align = "center",
  delayDuration = 700,
  skipDelayDuration = 300,
  disableHoverableContent = false,
  disabled = false,
  className,
  contentClassName
}) => {
  const [open, setOpen] = React.useState(false)
  const [position, setPosition] = React.useState({ x: 0, y: 0 })
  const triggerRef = React.useRef<HTMLElement>(null)
  const contentRef = React.useRef<HTMLDivElement>(null)
  const timeoutRef = React.useRef<NodeJS.Timeout>()
  const skipTimeoutRef = React.useRef<NodeJS.Timeout>()
  const wasOpenRef = React.useRef(false)

  const contentId = generateId('tooltip-content')
  const triggerId = generateId('tooltip-trigger')

  const contextValue: TooltipContextValue = {
    open,
    setOpen,
    contentId,
    triggerId
  }

  // Calculate position when tooltip opens
  React.useEffect(() => {
    if (open && triggerRef.current && contentRef.current) {
      const triggerRect = triggerRef.current.getBoundingClientRect()
      const contentRect = contentRef.current.getBoundingClientRect()
      const newPosition = getTooltipPosition(triggerRect, contentRect, side, align)
      setPosition(newPosition)
    }
  }, [open, side, align])

  const handleOpenChange = React.useCallback((newOpen: boolean) => {
    if (disabled) return

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    if (newOpen) {
      const delay = wasOpenRef.current ? skipDelayDuration : delayDuration
      timeoutRef.current = setTimeout(() => {
        setOpen(true)
        wasOpenRef.current = true
      }, delay)

      // Reset skip timeout
      if (skipTimeoutRef.current) {
        clearTimeout(skipTimeoutRef.current)
      }
    } else {
      setOpen(false)

      // Set skip timeout
      skipTimeoutRef.current = setTimeout(() => {
        wasOpenRef.current = false
      }, skipDelayDuration)
    }
  }, [disabled, delayDuration, skipDelayDuration])

  // Cleanup timeouts
  React.useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
      if (skipTimeoutRef.current) clearTimeout(skipTimeoutRef.current)
    }
  }, [])

  return (
    <TooltipContext.Provider value={contextValue}>
      <TooltipTrigger
        ref={triggerRef}
        onOpenChange={handleOpenChange}
        className={className}
      >
        {children}
      </TooltipTrigger>

      {open && (
        <TooltipContent
          ref={contentRef}
          position={position}
          side={side}
          onOpenChange={handleOpenChange}
          disableHoverableContent={disableHoverableContent}
          className={contentClassName}
        >
          {content}
        </TooltipContent>
      )}
    </TooltipContext.Provider>
  )
}

// Tooltip Trigger
const TooltipTrigger = React.forwardRef<
  HTMLElement,
  {
    children: React.ReactNode
    onOpenChange: (open: boolean) => void
    className?: string
  }
>(({ children, onOpenChange, className }, ref) => {
  const { contentId, triggerId } = useTooltip()

  const handleMouseEnter = React.useCallback(() => {
    onOpenChange(true)
  }, [onOpenChange])

  const handleMouseLeave = React.useCallback(() => {
    onOpenChange(false)
  }, [onOpenChange])

  const handleFocus = React.useCallback(() => {
    onOpenChange(true)
  }, [onOpenChange])

  const handleBlur = React.useCallback(() => {
    onOpenChange(false)
  }, [onOpenChange])

  const handleKeyDown = React.useCallback((event: React.KeyboardEvent) => {
    if (event.key === 'Escape') {
      onOpenChange(false)
    }
  }, [onOpenChange])

  // Clone the child element to add event handlers and ARIA attributes
  const child = React.Children.only(children) as React.ReactElement

  return React.cloneElement(child, {
    ref,
    id: triggerId,
    'aria-describedby': contentId,
    onMouseEnter: handleMouseEnter,
    onMouseLeave: handleMouseLeave,
    onFocus: handleFocus,
    onBlur: handleBlur,
    onKeyDown: handleKeyDown,
    className: cn(child.props.className, className)
  })
})
TooltipTrigger.displayName = "TooltipTrigger"

// Tooltip Content
const TooltipContent = React.forwardRef<
  HTMLDivElement,
  {
    children: React.ReactNode
    position: { x: number; y: number }
    side: "top" | "right" | "bottom" | "left"
    onOpenChange: (open: boolean) => void
    disableHoverableContent: boolean
    className?: string
  }
>(({ children, position, side, onOpenChange, disableHoverableContent, className }, ref) => {
  const { contentId } = useTooltip()

  const handleMouseEnter = React.useCallback(() => {
    if (!disableHoverableContent) {
      onOpenChange(true)
    }
  }, [disableHoverableContent, onOpenChange])

  const handleMouseLeave = React.useCallback(() => {
    if (!disableHoverableContent) {
      onOpenChange(false)
    }
  }, [disableHoverableContent, onOpenChange])

  const sideClasses = {
    top: "animate-in fade-in-0 zoom-in-95 slide-in-from-bottom-2",
    right: "animate-in fade-in-0 zoom-in-95 slide-in-from-left-2",
    bottom: "animate-in fade-in-0 zoom-in-95 slide-in-from-top-2",
    left: "animate-in fade-in-0 zoom-in-95 slide-in-from-right-2"
  }

  return createPortal(
    <div
      ref={ref}
      id={contentId}
      role="tooltip"
      className={cn(
        "absolute z-50 overflow-hidden rounded-md border border-gray-200 dark:border-gray-800",
        "bg-white dark:bg-gray-900 px-3 py-1.5 text-sm text-gray-900 dark:text-gray-100",
        "shadow-md animate-in fade-in-0 zoom-in-95 duration-200",
        sideClasses[side],
        className
      )}
      style={{
        left: position.x,
        top: position.y
      }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}

      {/* Arrow */}
      <div
        className={cn(
          "absolute h-2 w-2 rotate-45 border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900",
          side === "top" && "bottom-[-5px] left-1/2 -translate-x-1/2 border-t-0 border-l-0",
          side === "right" && "left-[-5px] top-1/2 -translate-y-1/2 border-t-0 border-r-0",
          side === "bottom" && "top-[-5px] left-1/2 -translate-x-1/2 border-b-0 border-r-0",
          side === "left" && "right-[-5px] top-1/2 -translate-y-1/2 border-b-0 border-l-0"
        )}
      />
    </div>,
    document.body
  )
})
TooltipContent.displayName = "TooltipContent"

// Provider for global tooltip configuration
export interface TooltipProviderProps {
  children: React.ReactNode
  delayDuration?: number
  skipDelayDuration?: number
  disableHoverableContent?: boolean
}

const TooltipProviderContext = React.createContext<{
  delayDuration: number
  skipDelayDuration: number
  disableHoverableContent: boolean
} | null>(null)

export const TooltipProvider: React.FC<TooltipProviderProps> = ({
  children,
  delayDuration = 700,
  skipDelayDuration = 300,
  disableHoverableContent = false
}) => {
  const contextValue = {
    delayDuration,
    skipDelayDuration,
    disableHoverableContent
  }

  return (
    <TooltipProviderContext.Provider value={contextValue}>
      {children}
    </TooltipProviderContext.Provider>
  )
}

export { Tooltip, TooltipTrigger, TooltipContent }
