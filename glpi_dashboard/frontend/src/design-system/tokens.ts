/**
 * Design System - Tokens Expandidos
 * Sistema unificado de tokens de design baseado no CSS atual
 */

// ===== SPACING TOKENS =====
export const SPACING = {
  // Base scale (múltiplos de 4px)
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

// Semantic spacing para componentes
export const COMPONENT_SPACING = {
  card: {
    padding: SPACING['2xl'],     // 24px
    gap: SPACING.lg,             // 16px
    margin: SPACING['2xl'],      // 24px
  },
  section: {
    padding: SPACING['3xl'],     // 32px
    gap: SPACING['3xl'],         // 32px
    margin: SPACING['5xl'],      // 48px
  },
  grid: {
    gap: SPACING.lg,             // 16px
    columnGap: SPACING.lg,       // 16px
    rowGap: SPACING['2xl'],      // 24px
  },
  button: {
    paddingX: SPACING.lg,        // 16px
    paddingY: SPACING.sm,        // 8px
    gap: SPACING.sm,             // 8px
  },
} as const;

// ===== COLOR TOKENS =====
export const COLORS = {
  // Primary palette
  primary: {
    50: '#f0f9ff',
    100: '#e0f2fe',
    200: '#bae6fd',
    300: '#7dd3fc',
    400: '#38bdf8',
    500: '#0ea5e9',
    600: '#0284c7',
    700: '#0369a1',
    800: '#075985',
    900: '#0c4a6e',
    DEFAULT: '#0ea5e9',
  },

  // Status colors
  success: {
    50: '#f0fdf4',
    100: '#dcfce7',
    200: '#bbf7d0',
    300: '#86efac',
    400: '#4ade80',
    500: '#22c55e',
    600: '#16a34a',
    700: '#15803d',
    800: '#166534',
    900: '#14532d',
    DEFAULT: '#22c55e',
  },

  warning: {
    50: '#fffbeb',
    100: '#fef3c7',
    200: '#fde68a',
    300: '#fcd34d',
    400: '#fbbf24',
    500: '#f59e0b',
    600: '#d97706',
    700: '#b45309',
    800: '#92400e',
    900: '#78350f',
    DEFAULT: '#f59e0b',
  },

  danger: {
    50: '#fef2f2',
    100: '#fee2e2',
    200: '#fecaca',
    300: '#fca5a5',
    400: '#f87171',
    500: '#ef4444',
    600: '#dc2626',
    700: '#b91c1c',
    800: '#991b1b',
    900: '#7f1d1d',
    DEFAULT: '#ef4444',
  },

  // Neutral colors
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
    DEFAULT: '#6b7280',
  },
} as const;

// ===== TYPOGRAPHY TOKENS =====
export const TYPOGRAPHY = {
  fontFamily: {
    sans: ['Inter', 'system-ui', 'sans-serif'],
    mono: ['JetBrains Mono', 'Roboto Mono', 'monospace'],
  },

  fontSize: {
    xs: ['0.75rem', { lineHeight: '1rem' }],      // 12px
    sm: ['0.875rem', { lineHeight: '1.25rem' }],  // 14px
    base: ['1rem', { lineHeight: '1.5rem' }],     // 16px
    lg: ['1.125rem', { lineHeight: '1.75rem' }],  // 18px
    xl: ['1.25rem', { lineHeight: '1.75rem' }],   // 20px
    '2xl': ['1.5rem', { lineHeight: '2rem' }],    // 24px
    '3xl': ['1.875rem', { lineHeight: '2.25rem' }], // 30px
    '4xl': ['2.25rem', { lineHeight: '2.5rem' }],   // 36px
  },

  fontWeight: {
    light: '300',
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },

  letterSpacing: {
    tight: '-0.025em',
    normal: '0em',
    wide: '0.025em',
  },
} as const;

// ===== SHADOW TOKENS =====
export const SHADOWS = {
  // Elevation shadows
  xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',

  // Specialized shadows
  card: '0 4px 16px rgba(0, 0, 0, 0.1)',
  cardHover: '0 8px 24px rgba(0, 0, 0, 0.15)',
  cardDark: '0 8px 32px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.08)',

  // Focus shadows
  focusRing: '0 0 0 2px rgba(59, 130, 246, 0.5)',
  focusRingDanger: '0 0 0 2px rgba(239, 68, 68, 0.5)',

  // Inner shadows
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
  innerLg: 'inset 0 4px 8px 0 rgba(0, 0, 0, 0.1)',
} as const;

// ===== BORDER RADIUS TOKENS =====
export const BORDER_RADIUS = {
  none: '0',
  xs: '0.125rem',   // 2px
  sm: '0.25rem',    // 4px
  md: '0.375rem',   // 6px
  lg: '0.5rem',     // 8px
  xl: '0.75rem',    // 12px
  '2xl': '1rem',    // 16px
  '3xl': '1.5rem',  // 24px
  full: '9999px',

  // Component specific
  card: '0.75rem',     // 12px
  button: '0.5rem',    // 8px
  badge: '9999px',     // full
  input: '0.375rem',   // 6px
} as const;

// ===== ANIMATION TOKENS =====
export const ANIMATIONS = {
  // Duration
  duration: {
    fast: '150ms',
    normal: '300ms',
    slow: '500ms',
  },

  // Timing functions
  easing: {
    linear: 'linear',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
  },

  // Keyframes
  keyframes: {
    fadeIn: {
      '0%': { opacity: '0', transform: 'translateY(10px)' },
      '100%': { opacity: '1', transform: 'translateY(0)' },
    },
    slideIn: {
      '0%': { transform: 'translateX(-100%)' },
      '100%': { transform: 'translateX(0)' },
    },
    spin: {
      '0%': { transform: 'rotate(0deg)' },
      '100%': { transform: 'rotate(360deg)' },
    },
    pulse: {
      '0%, 100%': { opacity: '1' },
      '50%': { opacity: '0.5' },
    },
  },
} as const;

// ===== Z-INDEX TOKENS =====
export const Z_INDEX = {
  hide: -1,
  auto: 'auto',
  base: 0,
  docked: 10,
  dropdown: 1000,
  sticky: 1100,
  banner: 1200,
  overlay: 1300,
  modal: 1400,
  popover: 1500,
  skipLink: 1600,
  toast: 1700,
  tooltip: 1800,
} as const;

// ===== BREAKPOINTS =====
export const BREAKPOINTS = {
  xs: '475px',
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

// ===== COMPONENT VARIANTS =====
export const COMPONENT_VARIANTS = {
  // Button variants
  button: {
    primary: {
      bg: 'bg-primary-500 hover:bg-primary-600',
      text: 'text-white',
      border: 'border-transparent',
      shadow: 'shadow-sm hover:shadow-md',
    },
    secondary: {
      bg: 'bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600',
      text: 'text-gray-900 dark:text-gray-100',
      border: 'border-gray-300 dark:border-gray-600',
      shadow: 'shadow-sm hover:shadow-md',
    },
    outline: {
      bg: 'bg-transparent hover:bg-gray-50 dark:hover:bg-gray-800',
      text: 'text-gray-700 dark:text-gray-300',
      border: 'border-gray-300 dark:border-gray-600',
      shadow: 'shadow-sm hover:shadow-md',
    },
  },

  // Card variants
  card: {
    default: {
      bg: 'bg-white dark:bg-gray-800',
      border: 'border border-gray-200 dark:border-gray-700',
      shadow: 'shadow-sm hover:shadow-md',
      radius: 'rounded-lg',
    },
    glass: {
      bg: 'bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm',
      border: 'border border-white/90 dark:border-gray-700/50',
      shadow: 'shadow-lg hover:shadow-xl',
      radius: 'rounded-xl',
    },
  },

  // Badge variants
  badge: {
    default: {
      bg: 'bg-gray-100 dark:bg-gray-700',
      text: 'text-gray-800 dark:text-gray-200',
    },
    primary: {
      bg: 'bg-primary-100 dark:bg-primary-900',
      text: 'text-primary-800 dark:text-primary-200',
    },
    success: {
      bg: 'bg-success-100 dark:bg-success-900',
      text: 'text-success-800 dark:text-success-200',
    },
    warning: {
      bg: 'bg-warning-100 dark:bg-warning-900',
      text: 'text-warning-800 dark:text-warning-200',
    },
    danger: {
      bg: 'bg-danger-100 dark:bg-danger-900',
      text: 'text-danger-800 dark:text-danger-200',
    },
  },
} as const;

// ===== UTILITY FUNCTIONS =====
export const createColorScale = (baseColor: string) => {
  // Função para criar escalas de cores personalizadas
  return {
    50: `${baseColor}-50`,
    100: `${baseColor}-100`,
    200: `${baseColor}-200`,
    300: `${baseColor}-300`,
    400: `${baseColor}-400`,
    500: `${baseColor}-500`,
    600: `${baseColor}-600`,
    700: `${baseColor}-700`,
    800: `${baseColor}-800`,
    900: `${baseColor}-900`,
    DEFAULT: `${baseColor}-500`,
  };
};

export const getSpacing = (size: keyof typeof SPACING) => SPACING[size];
export const getColor = (color: string) => COLORS;
export const getShadow = (size: keyof typeof SHADOWS) => SHADOWS[size];
export const getRadius = (size: keyof typeof BORDER_RADIUS) => BORDER_RADIUS[size];

// Export all tokens as default
export default {
  SPACING,
  COMPONENT_SPACING,
  COLORS,
  TYPOGRAPHY,
  SHADOWS,
  BORDER_RADIUS,
  ANIMATIONS,
  Z_INDEX,
  BREAKPOINTS,
  COMPONENT_VARIANTS,
  createColorScale,
  getSpacing,
  getColor,
  getShadow,
  getRadius,
};
