/**
 * Design System - Utilities
 * Utilitários para aplicação consistente do design system
 */

import { cn } from '@/lib/utils';

/**
 * Mapeamento de classes Tailwind para tokens do design system
 */
export const TAILWIND_CLASSES = {
  // Padding padronizado
  padding: {
    xs: 'p-1', // 4px - espaçamentos muito pequenos
    small: 'p-4', // 16px - componentes pequenos
    card: 'p-6', // 24px - padrão para cards
    section: 'p-8', // 32px - padrão para seções
    button: 'px-4 py-2', // 16px/8px - padrão para botões
    modal: 'p-6', // 24px - padrão para modais
    badge: 'px-2 py-1', // 8px/4px - badges e tags
    normal: 'p-4', // 16px - padding normal
  },

  // Gaps padronizados
  gap: {
    xs: 'gap-1', // 4px - gaps muito pequenos
    card: 'gap-4', // 16px - entre elementos de card
    section: 'gap-6', // 24px - entre seções
    grid: 'gap-4', // 16px - grids padrão
    items: 'gap-2', // 8px - entre itens pequenos
    large: 'gap-8', // 32px - espaçamentos grandes
    normal: 'gap-4', // 16px - gap normal
  },

  // Margins padronizados
  margin: {
    xs: 'mb-1', // 4px - margens muito pequenas
    small: 'mb-2', // 8px - espaçamentos pequenos
    element: 'mb-4', // 16px - entre elementos
    card: 'mb-6', // 24px - entre cards
    section: 'mb-8', // 32px - entre seções
    md: 'mb-3', // 12px - margem média
    normal: 'mb-4', // 16px - margem normal
  },

  // Space-y padronizado
  spaceY: {
    xs: 'space-y-1', // 4px - espaçamentos muito pequenos
    list: 'space-y-2', // 8px - listas
    card: 'space-y-4', // 16px - dentro de cards
    section: 'space-y-6', // 24px - dentro de seções
    form: 'space-y-4', // 16px - formulários
    normal: 'space-y-4', // 16px - espaçamento normal
    md: 'space-y-3', // 12px - espaçamento médio
  },
} as const;

/**
 * Cria classes padronizadas para cards
 */
export function createCardClasses(variant: 'default' | 'elevated' | 'outlined' = 'default') {
  const baseClasses = 'rounded-lg border transition-all duration-200';

  const variants = {
    default:
      'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md',
    elevated:
      'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 shadow-lg hover:shadow-xl',
    outlined: 'bg-transparent border-2 border-gray-300 dark:border-gray-600 hover:border-gray-400',
  };

  return cn(baseClasses, variants[variant], TAILWIND_CLASSES.padding.card);
}

/**
 * Cria classes padronizadas para seções
 */
export function createSectionClasses(spacing: 'normal' | 'compact' | 'spacious' = 'normal') {
  const spacingMap = {
    compact: TAILWIND_CLASSES.spaceY.list,
    normal: TAILWIND_CLASSES.spaceY.section,
    spacious: 'space-y-8',
  };

  return cn(spacingMap[spacing], TAILWIND_CLASSES.margin.section);
}

/**
 * Cria classes padronizadas para grids
 */
export function createGridClasses(columns: number = 1, responsive = true) {
  const baseClasses = TAILWIND_CLASSES.gap.grid;

  if (!responsive) {
    return cn(`grid grid-cols-${columns}`, baseClasses);
  }

  // Grid responsivo baseado no número de colunas
  const responsiveClasses = {
    1: 'grid grid-cols-1',
    2: 'grid grid-cols-1 md:grid-cols-2',
    3: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
  };

  return cn(
    responsiveClasses[columns as keyof typeof responsiveClasses] || `grid grid-cols-${columns}`,
    baseClasses
  );
}

/**
 * Cria classes padronizadas para flex layouts
 */
export function createFlexClasses(
  direction: 'row' | 'col' = 'row',
  align: 'start' | 'center' | 'end' | 'stretch' = 'center',
  justify: 'start' | 'center' | 'end' | 'between' | 'around' = 'start',
  gap: 'small' | 'normal' | 'large' = 'normal'
) {
  const gapMap = {
    small: TAILWIND_CLASSES.gap.items,
    normal: TAILWIND_CLASSES.gap.card,
    large: TAILWIND_CLASSES.gap.large,
  };

  return cn(
    'flex',
    direction === 'col' ? 'flex-col' : 'flex-row',
    `items-${align}`,
    `justify-${justify}`,
    gapMap[gap]
  );
}

/**
 * Remove classes de espaçamento hardcoded e substitui por padrões
 */
export function normalizeSpacingClasses(className: string): string {
  // Mapeamento de classes comuns para padrões
  const replacements: Record<string, string> = {
    // Padding
    'p-3': TAILWIND_CLASSES.padding.small,
    'p-4': TAILWIND_CLASSES.padding.small,
    'p-6': TAILWIND_CLASSES.padding.card,
    'p-8': TAILWIND_CLASSES.padding.section,

    // Gaps
    'gap-2': TAILWIND_CLASSES.gap.items,
    'gap-3': TAILWIND_CLASSES.gap.card,
    'gap-4': TAILWIND_CLASSES.gap.card,
    'gap-6': TAILWIND_CLASSES.gap.section,

    // Space-y
    'space-y-2': TAILWIND_CLASSES.spaceY.list,
    'space-y-3': TAILWIND_CLASSES.spaceY.card,
    'space-y-4': TAILWIND_CLASSES.spaceY.card,
    'space-y-6': TAILWIND_CLASSES.spaceY.section,

    // Margins
    'mb-2': TAILWIND_CLASSES.margin.small,
    'mb-3': TAILWIND_CLASSES.margin.element,
    'mb-4': TAILWIND_CLASSES.margin.element,
    'mb-6': TAILWIND_CLASSES.margin.card,
    'mb-8': TAILWIND_CLASSES.margin.section,
  };

  let normalizedClassName = className;

  Object.entries(replacements).forEach(([old, replacement]) => {
    normalizedClassName = normalizedClassName.replace(new RegExp(`\\b${old}\\b`, 'g'), replacement);
  });

  return normalizedClassName;
}

/**
 * Valida se as classes seguem o design system
 */
export function validateDesignSystemClasses(className: string): {
  isValid: boolean;
  issues: string[];
  suggestions: string[];
} {
  const issues: string[] = [];
  const suggestions: string[] = [];

  // Verifica classes hardcoded comuns
  const hardcodedPatterns = [
    /\bp-[0-9]+\b/g,
    /\bm[tblr]?-[0-9]+\b/g,
    /\bgap-[0-9]+\b/g,
    /\bspace-[xy]-[0-9]+\b/g,
  ];

  hardcodedPatterns.forEach(pattern => {
    const matches = className.match(pattern);
    if (matches) {
      issues.push(`Classes hardcoded encontradas: ${matches.join(', ')}`);
      suggestions.push(
        'Use utilitários do design system como createCardClasses() ou TAILWIND_CLASSES'
      );
    }
  });

  // Verifica classes obsoletas
  const obsoletePatterns = [/\bfigma-\w+\b/g, /\btext-h[0-9]\b/g, /\bcard-base\b/g];

  obsoletePatterns.forEach(pattern => {
    const matches = className.match(pattern);
    if (matches) {
      issues.push(`Classes obsoletas encontradas: ${matches.join(', ')}`);
      suggestions.push('Substitua por classes Tailwind equivalentes ou componentes Shadcn UI');
    }
  });

  return {
    isValid: issues.length === 0,
    issues,
    suggestions,
  };
}
