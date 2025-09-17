import * as React from "react"
import { cn } from "@/lib/utils"
import { useKeyboardNavigation, useListNavigation } from "@/hooks/useKeyboardNavigation"
import { ariaUtils, generateId } from "@/utils/accessibility"
import { ChevronDown, ChevronRight } from "lucide-react"

export interface NavigationItem {
  id: string
  label: string
  href?: string
  icon?: React.ComponentType<{ className?: string }>
  children?: NavigationItem[]
  current?: boolean
  disabled?: boolean
  badge?: string | number
}

export interface NavigationProps {
  items: NavigationItem[]
  orientation?: 'horizontal' | 'vertical'
  className?: string
  onItemSelect?: (item: NavigationItem) => void
  ariaLabel?: string
  collapsible?: boolean
}

const NavigationContext = React.createContext<{
  onItemSelect?: (item: NavigationItem) => void
  orientation: 'horizontal' | 'vertical'
}>({ orientation: 'vertical' })

const NavigationItem = React.forwardRef<
  HTMLElement,
  {
    item: NavigationItem
    level?: number
    index: number
    totalItems: number
  }
>(({ item, level = 0, index, totalItems }, ref) => {
  const { onItemSelect, orientation } = React.useContext(NavigationContext)
  const [isExpanded, setIsExpanded] = React.useState(false)
  const hasChildren = item.children && item.children.length > 0
  const itemId = generateId(`nav-item-${item.id}`)
  const submenuId = hasChildren ? generateId(`submenu-${item.id}`) : undefined

  const handleClick = React.useCallback(() => {
    if (item.disabled) return

    if (hasChildren) {
      setIsExpanded(!isExpanded)
    } else {
      onItemSelect?.(item)
    }
  }, [item, hasChildren, isExpanded, onItemSelect])

  const { handleKeyDown: handleNativeKeyDown } = useKeyboardNavigation({
    onEnter: handleClick,
    onSpace: handleClick,
    onArrowRight: hasChildren && orientation === 'horizontal' ? () => setIsExpanded(true) : undefined,
    onArrowLeft: hasChildren && orientation === 'horizontal' ? () => setIsExpanded(false) : undefined,
    onArrowDown: hasChildren && orientation === 'vertical' ? () => setIsExpanded(true) : undefined,
    onArrowUp: hasChildren && orientation === 'vertical' ? () => setIsExpanded(false) : undefined,
    disabled: item.disabled
  })

  const handleKeyDown = React.useCallback((event: React.KeyboardEvent) => {
    handleNativeKeyDown(event.nativeEvent)
  }, [handleNativeKeyDown])

  const linkProps = item.href ? {
    as: 'a' as const,
    href: item.href
  } : {
    as: 'button' as const,
    type: 'button' as const
  }

  const ariaProps = {
    ...ariaUtils.listItem({
      position: index + 1,
      total: totalItems,
      selected: item.current
    }),
    id: itemId,
    'aria-expanded': hasChildren ? isExpanded : undefined,
    'aria-controls': submenuId,
    'aria-disabled': item.disabled,
    'aria-current': item.current ? ('page' as const) : undefined,
    tabIndex: item.disabled ? -1 : 0
  }

  const Component = linkProps.as

  return (
    <li className={cn("relative", level > 0 && "ml-4")}>
      <Component
        ref={ref as any}
        className={cn(
          "flex items-center justify-between w-full px-3 py-2 text-sm font-medium rounded-md transition-colors",
          "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
          "hover:bg-gray-100 dark:hover:bg-gray-800",
          item.current && "bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300",
          item.disabled && "opacity-50 cursor-not-allowed",
          !item.disabled && "cursor-pointer"
        )}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        {...linkProps}
        {...ariaProps}
      >
        <div className="flex items-center space-x-3">
          {item.icon && (
            <item.icon
              className={cn(
                "w-4 h-4",
                item.current ? "text-blue-700 dark:text-blue-300" : "text-gray-500 dark:text-gray-400"
              )}
              aria-hidden="true"
            />
          )}
          <span>{item.label}</span>
          {item.badge && (
            <span
              className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200"
              aria-label={`${item.badge} itens`}
            >
              {item.badge}
            </span>
          )}
        </div>

        {hasChildren && (
          <div className="flex items-center">
            {orientation === 'vertical' ? (
              <ChevronDown
                className={cn(
                  "w-4 h-4 transition-transform",
                  isExpanded && "rotate-180"
                )}
                aria-hidden="true"
              />
            ) : (
              <ChevronRight
                className={cn(
                  "w-4 h-4 transition-transform",
                  isExpanded && "rotate-90"
                )}
                aria-hidden="true"
              />
            )}
          </div>
        )}
      </Component>

      {hasChildren && isExpanded && (
        <ul
          id={submenuId}
          className={cn(
            "mt-1 space-y-1",
            orientation === 'horizontal' && "absolute top-full left-0 min-w-48 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg z-50 p-2"
          )}
          role="group"
          aria-labelledby={itemId}
        >
          {item.children?.map((child, childIndex) => (
            <NavigationItem
              key={child.id}
              item={child}
              level={level + 1}
              index={childIndex}
              totalItems={item.children?.length || 0}
            />
          ))}
        </ul>
      )}
    </li>
  )
})

NavigationItem.displayName = "NavigationItem"

const Navigation = React.forwardRef<HTMLElement, NavigationProps>(
  ({ items, orientation = 'vertical', className, onItemSelect, ariaLabel, collapsible = false }, ref) => {
    const navigationId = generateId('navigation')
    const [isCollapsed, setIsCollapsed] = React.useState(false)

    const {
      containerRef,
      focusedIndex,
      handleKeyDown,
      resetFocus
    } = useListNavigation({
      itemCount: items.length,
      onSelect: (index) => {
        const item = items[index]
        if (item && !item.disabled) {
          onItemSelect?.(item)
        }
      },
      loop: true
    })

    const contextValue = React.useMemo(() => ({
      onItemSelect,
      orientation
    }), [onItemSelect, orientation])

    return (
      <NavigationContext.Provider value={contextValue}>
        <nav
          ref={ref as any}
          className={cn(
            "navigation-container",
            orientation === 'horizontal' && "flex items-center space-x-1",
            orientation === 'vertical' && "space-y-1",
            className
          )}
          aria-label={ariaLabel || "Navegação principal"}
          role="navigation"
          id={navigationId}
        >
          {collapsible && (
            <button
              className="mb-2 p-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              onClick={() => setIsCollapsed(!isCollapsed)}
              aria-expanded={!isCollapsed}
              aria-controls={`${navigationId}-items`}
              aria-label={isCollapsed ? "Expandir navegação" : "Recolher navegação"}
            >
              {isCollapsed ? "Expandir" : "Recolher"}
            </button>
          )}

          <ul
            ref={containerRef}
            id={`${navigationId}-items`}
            className={cn(
              "navigation-list",
              orientation === 'horizontal' && "flex items-center space-x-1",
              orientation === 'vertical' && "space-y-1",
              isCollapsed && "hidden"
            )}
            role="list"
            aria-label={`Lista de navegação com ${items.length} itens`}
            onKeyDown={handleKeyDown}
            tabIndex={-1}
          >
            {items.map((item, index) => (
              <NavigationItem
                key={item.id}
                item={item}
                index={index}
                totalItems={items.length}
              />
            ))}
          </ul>

          {/* Screen reader instructions */}
          <div className="sr-only" aria-live="polite">
            Use as setas para navegar entre os itens. Pressione Enter ou Espaço para selecionar.
            {orientation === 'vertical' && " Use seta para baixo para expandir submenus."}
            {orientation === 'horizontal' && " Use seta para direita para expandir submenus."}
          </div>
        </nav>
      </NavigationContext.Provider>
    )
  }
)

Navigation.displayName = "Navigation"

export { Navigation, NavigationItem }
