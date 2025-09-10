import { useCallback, useEffect, useRef, useState, useMemo } from 'react';

/**
 * Hook para gerenciar navegação por teclado em componentes
 */
export const useKeyboardNavigation = ({
  onEnter,
  onSpace,
  onEscape,
  onArrowUp,
  onArrowDown,
  onArrowLeft,
  onArrowRight,
  disabled = false,
}: {
  onEnter?: () => void;
  onSpace?: () => void;
  onEscape?: () => void;
  onArrowUp?: () => void;
  onArrowDown?: () => void;
  onArrowLeft?: () => void;
  onArrowRight?: () => void;
  disabled?: boolean;
}) => {
  const elementRef = useRef<HTMLElement>(null);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (disabled) return;

      switch (event.key) {
        case 'Enter':
          event.preventDefault();
          onEnter?.();
          break;
        case ' ':
        case 'Space':
          event.preventDefault();
          onSpace?.();
          break;
        case 'Escape':
          event.preventDefault();
          onEscape?.();
          break;
        case 'ArrowUp':
          event.preventDefault();
          onArrowUp?.();
          break;
        case 'ArrowDown':
          event.preventDefault();
          onArrowDown?.();
          break;
        case 'ArrowLeft':
          event.preventDefault();
          onArrowLeft?.();
          break;
        case 'ArrowRight':
          event.preventDefault();
          onArrowRight?.();
          break;
      }
    },
    [disabled, onEnter, onSpace, onEscape, onArrowUp, onArrowDown, onArrowLeft, onArrowRight]
  );

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    element.addEventListener('keydown', handleKeyDown);
    return () => element.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return {
    elementRef,
    handleKeyDown,
  };
};

/**
 * Hook para gerenciar foco em listas navegáveis
 */
export const useListNavigation = ({
  items,
  itemCount,
  onSelect,
  loop = true,
  isEnabled = true,
}: {
  items?: any[];
  itemCount?: number;
  onSelect?: (index: number, item?: any) => void;
  loop?: boolean;
  isEnabled?: boolean;
}) => {
  const containerRef = useRef<HTMLElement>(null);
  const currentIndexRef = useRef<number>(-1);
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);

  // Calculate the actual item count
  const actualItemCount = useMemo(() => {
    if (typeof itemCount === 'number') return itemCount;
    if (Array.isArray(items)) return items.length;
    return 0;
  }, [items, itemCount]);

  const focusItem = useCallback(
    (index: number) => {
      if (!isEnabled || index < 0 || index >= actualItemCount) return;

      const container = containerRef.current;
      if (!container) return;

      const focusableElements = container.querySelectorAll(
        '[tabindex="0"], button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );

      const element = focusableElements[index] as HTMLElement;
      if (element) {
        element.focus();
        currentIndexRef.current = index;
        setFocusedIndex(index);
      }
    },
    [isEnabled, actualItemCount]
  );

  const moveToNext = useCallback(() => {
    if (!isEnabled || actualItemCount === 0) return;

    const nextIndex = currentIndexRef.current + 1;
    if (nextIndex >= actualItemCount) {
      if (loop) {
        focusItem(0);
      }
    } else {
      focusItem(nextIndex);
    }
  }, [actualItemCount, loop, focusItem, isEnabled]);

  const moveToPrevious = useCallback(() => {
    if (!isEnabled || actualItemCount === 0) return;

    const prevIndex = currentIndexRef.current - 1;
    if (prevIndex < 0) {
      if (loop) {
        focusItem(actualItemCount - 1);
      }
    } else {
      focusItem(prevIndex);
    }
  }, [actualItemCount, loop, focusItem, isEnabled]);

  const selectCurrent = useCallback(() => {
    if (!isEnabled) return;

    const currentIndex = currentIndexRef.current;
    if (currentIndex >= 0 && currentIndex < actualItemCount) {
      const item = Array.isArray(items) ? items[currentIndex] : undefined;
      onSelect?.(currentIndex, item);
    }
  }, [items, onSelect, actualItemCount, isEnabled]);

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      if (!isEnabled) return;

      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault();
          moveToNext();
          break;
        case 'ArrowUp':
          event.preventDefault();
          moveToPrevious();
          break;
        case 'Enter':
        case ' ':
          event.preventDefault();
          selectCurrent();
          break;
        case 'Escape':
          event.preventDefault();
          resetFocus();
          break;
      }
    },
    [isEnabled, moveToNext, moveToPrevious, selectCurrent]
  );

  const resetFocus = useCallback(() => {
    currentIndexRef.current = -1;
    setFocusedIndex(-1);
  }, []);

  return {
    containerRef,
    focusedIndex,
    handleKeyDown,
    resetFocus,
    focusItem,
    moveToNext,
    moveToPrevious,
    selectCurrent,
  };
};
