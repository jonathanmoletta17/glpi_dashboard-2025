/**
 * Utilitários para acessibilidade
 */

/**
 * Gera IDs únicos para elementos ARIA
 */
let idCounter = 0;
export const generateId = (prefix = 'accessible') => {
  idCounter += 1;
  return `${prefix}-${idCounter}-${Date.now()}`;
};

/**
 * Gerencia foco em elementos
 */
export const focusManager = {
  /**
   * Move o foco para o próximo elemento focável
   */
  focusNext: (container: HTMLElement) => {
    const focusableElements = getFocusableElements(container);
    const currentIndex = focusableElements.indexOf(document.activeElement as HTMLElement);
    const nextIndex = (currentIndex + 1) % focusableElements.length;
    focusableElements[nextIndex]?.focus();
  },

  /**
   * Move o foco para o elemento anterior focável
   */
  focusPrevious: (container: HTMLElement) => {
    const focusableElements = getFocusableElements(container);
    const currentIndex = focusableElements.indexOf(document.activeElement as HTMLElement);
    const prevIndex = currentIndex <= 0 ? focusableElements.length - 1 : currentIndex - 1;
    focusableElements[prevIndex]?.focus();
  },

  /**
   * Move o foco para o primeiro elemento focável
   */
  focusFirst: (container: HTMLElement) => {
    const focusableElements = getFocusableElements(container);
    focusableElements[0]?.focus();
  },

  /**
   * Move o foco para o último elemento focável
   */
  focusLast: (container: HTMLElement) => {
    const focusableElements = getFocusableElements(container);
    focusableElements[focusableElements.length - 1]?.focus();
  },

  /**
   * Captura o foco dentro de um container (focus trap)
   */
  trapFocus: (container: HTMLElement) => {
    const focusableElements = getFocusableElements(container);
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key !== 'Tab') return;

      if (event.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          event.preventDefault();
          lastElement?.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          event.preventDefault();
          firstElement?.focus();
        }
      }
    };

    container.addEventListener('keydown', handleKeyDown);
    firstElement?.focus();

    return () => {
      container.removeEventListener('keydown', handleKeyDown);
    };
  },
};

/**
 * Obtém todos os elementos focáveis dentro de um container
 */
export const getFocusableElements = (container: HTMLElement): HTMLElement[] => {
  const focusableSelectors = [
    'button:not([disabled])',
    '[href]',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
    '[contenteditable="true"]',
  ].join(', ');

  return Array.from(container.querySelectorAll(focusableSelectors)) as HTMLElement[];
};

/**
 * Utilitários para ARIA
 */
export const ariaUtils = {
  /**
   * Cria atributos ARIA para um botão
   */
  button: ({
    label,
    description,
    pressed,
    expanded,
    disabled,
  }: {
    label: string;
    description?: string;
    pressed?: boolean;
    expanded?: boolean;
    disabled?: boolean;
  }) => ({
    'aria-label': label,
    'aria-describedby': description ? generateId('description') : undefined,
    'aria-pressed': pressed !== undefined ? pressed : undefined,
    'aria-expanded': expanded !== undefined ? expanded : undefined,
    'aria-disabled': disabled,
    role: 'button',
    tabIndex: disabled ? -1 : 0,
  }),

  /**
   * Cria atributos ARIA para um link
   */
  link: ({
    label,
    description,
    current,
  }: {
    label: string;
    description?: string;
    current?: boolean;
  }) => ({
    'aria-label': label,
    'aria-describedby': description ? generateId('description') : undefined,
    'aria-current': current ? 'page' : undefined,
  }),

  /**
   * Cria atributos ARIA para uma região/landmark
   */
  region: ({
    label,
    description,
    role = 'region',
  }: {
    label: string;
    description?: string;
    role?: string;
  }) => ({
    role,
    'aria-label': label,
    'aria-describedby': description ? generateId('description') : undefined,
  }),

  /**
   * Cria atributos ARIA para uma lista
   */
  list: ({
    label,
    description,
    itemCount,
  }: {
    label: string;
    description?: string;
    itemCount?: number;
  }) => ({
    role: 'list',
    'aria-label': label,
    'aria-describedby': description ? generateId('description') : undefined,
    'aria-setsize': itemCount,
  }),

  /**
   * Cria atributos ARIA para um item de lista
   */
  listItem: ({
    position,
    total,
    selected,
  }: {
    position?: number;
    total?: number;
    selected?: boolean;
  }) => ({
    role: 'listitem',
    'aria-posinset': position,
    'aria-setsize': total,
    'aria-selected': selected,
  }),

  /**
   * Cria atributos ARIA para status/live regions
   */
  liveRegion: ({
    level = 'polite',
    atomic = true,
  }: {
    level?: 'off' | 'polite' | 'assertive';
    atomic?: boolean;
  }) => ({
    'aria-live': level,
    'aria-atomic': atomic,
    role: 'status',
  }),
};

/**
 * Utilitários para contraste de cores
 */
export const contrastUtils = {
  /**
   * Calcula a luminância relativa de uma cor
   */
  getLuminance: (r: number, g: number, b: number): number => {
    const [rs, gs, bs] = [r, g, b].map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  },

  /**
   * Calcula a razão de contraste entre duas cores
   */
  getContrastRatio: (
    color1: [number, number, number],
    color2: [number, number, number]
  ): number => {
    const lum1 = contrastUtils.getLuminance(...color1);
    const lum2 = contrastUtils.getLuminance(...color2);
    const brightest = Math.max(lum1, lum2);
    const darkest = Math.min(lum1, lum2);
    return (brightest + 0.05) / (darkest + 0.05);
  },

  /**
   * Verifica se o contraste atende aos padrões WCAG
   */
  meetsWCAG: (
    color1: [number, number, number],
    color2: [number, number, number],
    level: 'AA' | 'AAA' = 'AA'
  ): boolean => {
    const ratio = contrastUtils.getContrastRatio(color1, color2);
    return level === 'AA' ? ratio >= 4.5 : ratio >= 7;
  },
};

/**
 * Detecta preferências de acessibilidade do usuário
 */
export const accessibilityPreferences = {
  /**
   * Verifica se o usuário prefere movimento reduzido
   */
  prefersReducedMotion: (): boolean => {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  },

  /**
   * Verifica se o usuário prefere alto contraste
   */
  prefersHighContrast: (): boolean => {
    return window.matchMedia('(prefers-contrast: high)').matches;
  },

  /**
   * Verifica se o usuário prefere tema escuro
   */
  prefersDarkTheme: (): boolean => {
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  },

  /**
   * Verifica se o usuário está usando um leitor de tela
   */
  isUsingScreenReader: (): boolean => {
    // Detecta alguns leitores de tela comuns
    return (
      'speechSynthesis' in window ||
      navigator.userAgent.includes('NVDA') ||
      navigator.userAgent.includes('JAWS') ||
      navigator.userAgent.includes('VoiceOver')
    );
  },
};
