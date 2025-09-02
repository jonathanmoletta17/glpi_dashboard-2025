/**
 * Design System - Spacing Tokens
 * Sistema unificado de espaçamento para garantir consistência visual
 */

export const spacing = {
  // Base spacing scale (baseado em múltiplos de 4px)
  xs: '0.25rem',    // 4px
  sm: '0.5rem',     // 8px
  md: '0.75rem',    // 12px
  lg: '1rem',       // 16px
  xl: '1.25rem',    // 20px
  '2xl': '1.5rem',  // 24px
  '3xl': '2rem',    // 32px
  '4xl': '2.5rem',  // 40px
  '5xl': '3rem',    // 48px
  '6xl': '4rem',    // 64px
} as const;

export const componentSpacing = {
  // Espaçamentos específicos para componentes
  cardPadding: spacing.lg,           // 16px
  cardGap: spacing.md,               // 12px
  sectionGap: spacing['2xl'],        // 24px
  itemGap: spacing.sm,               // 8px
  headerPadding: spacing.lg,         // 16px
  contentPadding: spacing.lg,        // 16px
  buttonPadding: spacing.md,         // 12px
  inputPadding: spacing.md,          // 12px
} as const;

export const layoutSpacing = {
  // Espaçamentos para layout
  containerPadding: spacing.lg,      // 16px
  gridGap: spacing.lg,               // 16px
  stackGap: spacing.md,              // 12px
  flexGap: spacing.sm,               // 8px
} as const;

export type SpacingKey = keyof typeof spacing;
export type ComponentSpacingKey = keyof typeof componentSpacing;
export type LayoutSpacingKey = keyof typeof layoutSpacing;
