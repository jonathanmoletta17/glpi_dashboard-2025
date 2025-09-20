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
 * Reseta o contador de IDs (útil para testes)
 */
export const resetIdCounter = (): void => {
  idCounter = 0;
};

/**
 * Anuncia mensagens para leitores de tela
 */
export const announceToScreenReader = (
  message: string,
  priority: 'polite' | 'assertive' = 'polite'
) => {
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;

  document.body.appendChild(announcement);

  // Remove o elemento após um tempo para evitar acúmulo
  setTimeout(() => {
    if (document.body.contains(announcement)) {
      document.body.removeChild(announcement);
    }
  }, 1000);
};

/**
 * Cria uma região live persistente para anúncios
 */
let liveRegion: HTMLElement | null = null;

export const createLiveRegion = (): HTMLElement => {
  if (!liveRegion) {
    liveRegion = document.createElement('div');
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'false');
    liveRegion.className = 'sr-only';
    liveRegion.id = 'live-region';
    document.body.appendChild(liveRegion);
  }
  return liveRegion;
};

export const announceToPersistentRegion = (message: string): void => {
  const region = createLiveRegion();
  region.textContent = message;

  // Limpa após um delay
  setTimeout(() => {
    if (region.textContent === message) {
      region.textContent = '';
    }
  }, 1000);
};

/**
 * Gerencia foco em elementos
 */
export const focusManager = {
  /**
   * Armazena o último elemento focado antes de abrir um modal/dialog
   */
  storeFocus: (): HTMLElement | null => {
    return document.activeElement as HTMLElement;
  },

  /**
   * Restaura o foco para um elemento previamente armazenado
   */
  restoreFocus: (element: HTMLElement | null): void => {
    if (element && typeof element.focus === 'function') {
      element.focus();
    }
  },

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
   * Move o foco para próximo/anterior elemento focável
   */
  moveFocus: (container: HTMLElement, direction: 'next' | 'previous'): void => {
    const focusableElements = getFocusableElements(container);
    const currentIndex = focusableElements.indexOf(document.activeElement as HTMLElement);

    let nextIndex: number;
    if (direction === 'next') {
      nextIndex = currentIndex + 1 >= focusableElements.length ? 0 : currentIndex + 1;
    } else {
      nextIndex = currentIndex - 1 < 0 ? focusableElements.length - 1 : currentIndex - 1;
    }

    focusableElements[nextIndex]?.focus();
  },

  /**
   * Captura o foco dentro de um container (focus trap)
   */
  trapFocus: (container: HTMLElement) => {
    const focusableElements = getFocusableElements(container);
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleTabKey = (event: KeyboardEvent) => {
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

    const handleEscapeKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        // Permite que componentes lidem com a tecla escape
        const escapeEvent = new CustomEvent('modal-escape', { bubbles: true });
        container.dispatchEvent(escapeEvent);
      }
    };

    container.addEventListener('keydown', handleTabKey);
    container.addEventListener('keydown', handleEscapeKey);
    firstElement?.focus();

    return () => {
      container.removeEventListener('keydown', handleTabKey);
      container.removeEventListener('keydown', handleEscapeKey);
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
 * Helpers para navegação por teclado
 */
export const handleArrowNavigation = (
  event: KeyboardEvent,
  items: HTMLElement[],
  currentIndex: number,
  options: {
    orientation?: 'horizontal' | 'vertical' | 'both';
    loop?: boolean;
    onIndexChange?: (newIndex: number) => void;
  } = {}
): number => {
  const { orientation = 'vertical', loop = true, onIndexChange } = options;
  let newIndex = currentIndex;

  switch (event.key) {
    case 'ArrowDown':
      if (orientation === 'vertical' || orientation === 'both') {
        event.preventDefault();
        newIndex = currentIndex + 1;
        if (newIndex >= items.length) {
          newIndex = loop ? 0 : items.length - 1;
        }
      }
      break;
    case 'ArrowUp':
      if (orientation === 'vertical' || orientation === 'both') {
        event.preventDefault();
        newIndex = currentIndex - 1;
        if (newIndex < 0) {
          newIndex = loop ? items.length - 1 : 0;
        }
      }
      break;
    case 'ArrowRight':
      if (orientation === 'horizontal' || orientation === 'both') {
        event.preventDefault();
        newIndex = currentIndex + 1;
        if (newIndex >= items.length) {
          newIndex = loop ? 0 : items.length - 1;
        }
      }
      break;
    case 'ArrowLeft':
      if (orientation === 'horizontal' || orientation === 'both') {
        event.preventDefault();
        newIndex = currentIndex - 1;
        if (newIndex < 0) {
          newIndex = loop ? items.length - 1 : 0;
        }
      }
      break;
    case 'Home':
      event.preventDefault();
      newIndex = 0;
      break;
    case 'End':
      event.preventDefault();
      newIndex = items.length - 1;
      break;
  }

  if (newIndex !== currentIndex && items[newIndex]) {
    items[newIndex].focus();
    onIndexChange?.(newIndex);
  }

  return newIndex;
};

/**
 * Navegação por teclado com suporte a type-ahead
 */
export const handleTypeAheadNavigation = (
  event: KeyboardEvent,
  items: HTMLElement[],
  currentIndex: number,
  options: {
    getItemText?: (item: HTMLElement) => string;
    onIndexChange?: (newIndex: number) => void;
  } = {}
): number => {
  const { getItemText = item => item.textContent || '', onIndexChange } = options;

  // Apenas lida com caracteres imprimíveis
  if (event.key.length === 1 && !event.ctrlKey && !event.altKey && !event.metaKey) {
    event.preventDefault();

    const searchChar = event.key.toLowerCase();
    const startIndex = (currentIndex + 1) % items.length;

    // Busca a partir da posição atual para frente
    for (let i = 0; i < items.length; i++) {
      const index = (startIndex + i) % items.length;
      const item = items[index];
      const itemText = getItemText(item).toLowerCase();

      if (itemText.startsWith(searchChar)) {
        item.focus();
        onIndexChange?.(index);
        return index;
      }
    }
  }

  return currentIndex;
};

/**
 * Utilitários de validação para acessibilidade
 */
export const validateAriaLabel = (element: HTMLElement): boolean => {
  return !!(element.getAttribute('aria-label') || element.getAttribute('aria-labelledby'));
};

export const validateFormField = (
  field: HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
): {
  isValid: boolean;
  issues: string[];
} => {
  const issues: string[] = [];

  // Verifica associação de label
  const hasLabel = field.labels && field.labels.length > 0;
  const hasAriaLabel = validateAriaLabel(field);

  if (!hasLabel && !hasAriaLabel) {
    issues.push('Campo não possui rotulação adequada');
  }

  // Verifica indicação de campo obrigatório
  if (field.required && !field.getAttribute('aria-required')) {
    issues.push('Campo obrigatório deve ter aria-required="true"');
  }

  // Verifica estados de erro
  if (field.getAttribute('aria-invalid') === 'true' && !field.getAttribute('aria-describedby')) {
    issues.push('Campo inválido deve referenciar mensagem de erro com aria-describedby');
  }

  return {
    isValid: issues.length === 0,
    issues,
  };
};

/**
 * Valida hierarquia de cabeçalhos
 */
export const validateHeadingHierarchy = (
  container: HTMLElement = document.body
): {
  isValid: boolean;
  issues: string[];
} => {
  const headings = Array.from(container.querySelectorAll('h1, h2, h3, h4, h5, h6'));
  const issues: string[] = [];
  let previousLevel = 0;

  headings.forEach((heading, index) => {
    const level = parseInt(heading.tagName.charAt(1));

    if (index === 0 && level !== 1) {
      issues.push('Primeiro cabeçalho deve ser h1');
    }

    if (level > previousLevel + 1) {
      issues.push(
        `Nível de cabeçalho pula de h${previousLevel} para h${level} - deve ser sequencial`
      );
    }

    previousLevel = level;
  });

  return {
    isValid: issues.length === 0,
    issues,
  };
};

/**
 * Auditoria de acessibilidade em um container
 */
export const auditAccessibility = (
  container: HTMLElement
): {
  isValid: boolean;
  issues: string[];
} => {
  const issues: string[] = [];

  // Verifica imagens sem texto alternativo
  const images = container.querySelectorAll('img');
  images.forEach(img => {
    if (!img.alt && !img.getAttribute('aria-hidden')) {
      issues.push('Imagem sem texto alternativo ou aria-hidden');
    }
  });

  // Verifica botões sem nomes acessíveis
  const buttons = container.querySelectorAll('button');
  buttons.forEach(button => {
    if (!button.textContent?.trim() && !validateAriaLabel(button)) {
      issues.push('Botão sem nome acessível');
    }
  });

  // Verifica links sem nomes acessíveis
  const links = container.querySelectorAll('a');
  links.forEach(link => {
    if (!link.textContent?.trim() && !validateAriaLabel(link)) {
      issues.push('Link sem nome acessível');
    }
  });

  // Verifica campos de formulário
  const formFields = container.querySelectorAll('input, select, textarea');
  formFields.forEach(field => {
    const validation = validateFormField(field as HTMLInputElement);
    issues.push(...validation.issues);
  });

  // Verifica hierarquia de cabeçalhos
  const headingValidation = validateHeadingHierarchy(container);
  issues.push(...headingValidation.issues);

  return {
    isValid: issues.length === 0,
    issues,
  };
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
const hexToRgb = (hex: string): { r: number; g: number; b: number } | null => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
};

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
   * Calcula a razão de contraste entre duas cores hex
   */
  getContrastRatioFromHex: (color1: string, color2: string): number => {
    const rgb1 = hexToRgb(color1);
    const rgb2 = hexToRgb(color2);

    if (!rgb1 || !rgb2) return 1;

    return contrastUtils.getContrastRatio([rgb1.r, rgb1.g, rgb1.b], [rgb2.r, rgb2.g, rgb2.b]);
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

  /**
   * Verifica se o contraste de cores hex atende aos padrões WCAG
   */
  meetsWCAGFromHex: (color1: string, color2: string, level: 'AA' | 'AAA' = 'AA'): boolean => {
    const ratio = contrastUtils.getContrastRatioFromHex(color1, color2);
    return level === 'AA' ? ratio >= 4.5 : ratio >= 7;
  },

  /**
   * Obtém cor acessível alternativa
   */
  getAccessibleColor: (
    backgroundColor: string,
    textColor: string,
    level: 'AA' | 'AAA' = 'AA'
  ): string => {
    if (contrastUtils.meetsWCAGFromHex(backgroundColor, textColor, level)) {
      return textColor;
    }

    // Retorna alternativas de alto contraste
    const bgRgb = hexToRgb(backgroundColor);
    if (!bgRgb) return textColor;

    const bgLuminance = contrastUtils.getLuminance(bgRgb.r, bgRgb.g, bgRgb.b);

    // Se o fundo é claro, retorna texto escuro; se escuro, retorna texto claro
    return bgLuminance > 0.5 ? '#000000' : '#ffffff';
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

  /**
   * Obtém todas as preferências de acessibilidade
   */
  getAll: () => {
    return {
      reducedMotion: accessibilityPreferences.prefersReducedMotion(),
      highContrast: accessibilityPreferences.prefersHighContrast(),
      darkTheme: accessibilityPreferences.prefersDarkTheme(),
      reducedTransparency: window.matchMedia('(prefers-reduced-transparency: reduce)').matches,
      forcedColors: window.matchMedia('(forced-colors: active)').matches,
      screenReader: accessibilityPreferences.isUsingScreenReader(),
    };
  },

  /**
   * Aplica preferências de acessibilidade a um elemento
   */
  applyToElement: (element: HTMLElement): void => {
    const prefs = accessibilityPreferences.getAll();

    element.classList.toggle('reduce-motion', prefs.reducedMotion);
    element.classList.toggle('high-contrast', prefs.highContrast);
    element.classList.toggle('dark-theme', prefs.darkTheme);
    element.classList.toggle('reduce-transparency', prefs.reducedTransparency);
    element.classList.toggle('forced-colors', prefs.forcedColors);
  },

  /**
   * Cria listener para mudanças em media queries
   */
  createMediaQueryListener: (query: string, callback: (matches: boolean) => void): (() => void) => {
    const mediaQuery = window.matchMedia(query);
    const handler = (e: MediaQueryListEvent) => callback(e.matches);

    mediaQuery.addEventListener('change', handler);

    // Chama imediatamente com o estado atual
    callback(mediaQuery.matches);

    // Retorna função de limpeza
    return () => mediaQuery.removeEventListener('change', handler);
  },
};
