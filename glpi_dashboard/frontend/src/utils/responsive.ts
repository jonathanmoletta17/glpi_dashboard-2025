// Responsive utility classes and functions for the dashboard

// Grid classes for responsive layouts
export const RESPONSIVE_GRID_CLASSES = {
  // Base grid classes
  grid: 'grid gap-4',

  // Responsive columns
  cols: {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
    5: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5',
    6: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6'
  },

  // Auto-fit responsive grid
  autoFit: {
    sm: 'grid-cols-[repeat(auto-fit,minmax(200px,1fr))]',
    md: 'grid-cols-[repeat(auto-fit,minmax(250px,1fr))]',
    lg: 'grid-cols-[repeat(auto-fit,minmax(300px,1fr))]'
  },

  // Dashboard specific layouts
  dashboard: 'grid grid-cols-1 xl:grid-cols-3',
  levelMetrics: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2',

  // Metrics cards layout
  metricsCards: {
    base: 'grid gap-4 sm:gap-6',
    mobile: 'grid-cols-1',
    tablet: 'grid-cols-2',
    desktop: 'grid-cols-4'
  }
};

// Container classes for responsive layouts
export const RESPONSIVE_CONTAINER = {
  // Base container
  base: 'w-full mx-auto',

  // Responsive padding
  padding: 'px-4 sm:px-6 lg:px-8',

  // Max width containers
  maxWidth: {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
    '3xl': 'max-w-3xl',
    '4xl': 'max-w-4xl',
    '5xl': 'max-w-5xl',
    '6xl': 'max-w-6xl',
    '7xl': 'max-w-7xl',
    full: 'max-w-full'
  },

  // Full container with padding
  full: 'w-full mx-auto px-4 sm:px-6 lg:px-8'
};

// Spacing classes for responsive layouts
export const RESPONSIVE_SPACING = {
  // Responsive gaps
  gap: {
    xs: 'gap-2 sm:gap-3',
    sm: 'gap-3 sm:gap-4',
    md: 'gap-4 sm:gap-6',
    lg: 'gap-6 sm:gap-8',
    xl: 'gap-8 sm:gap-10'
  },

  // Responsive margins
  margin: {
    xs: 'm-2 sm:m-3',
    sm: 'm-3 sm:m-4',
    md: 'm-4 sm:m-6',
    lg: 'm-6 sm:m-8',
    xl: 'm-8 sm:m-10',
    // Bottom margins
    bottom: {
      xs: 'mb-2 sm:mb-3',
      sm: 'mb-3 sm:mb-4',
      md: 'mb-4 sm:mb-6',
      lg: 'mb-6 sm:mb-8',
      xl: 'mb-8 sm:mb-10'
    }
  },

  // Responsive padding
  padding: {
    xs: 'p-2 sm:p-3',
    sm: 'p-3 sm:p-4',
    md: 'p-4 sm:p-6',
    lg: 'p-6 sm:p-8',
    xl: 'p-8 sm:p-10'
  }
};

// Function to create responsive classes dynamically
export const createResponsiveClasses = ({
  cols,
  gap = 'md',
  padding = 'md',
  base,
  mobile,
  tablet,
  desktop
}: {
  cols?: 1 | 2 | 3 | 4 | 5 | 6;
  gap?: keyof typeof RESPONSIVE_SPACING.gap;
  padding?: keyof typeof RESPONSIVE_SPACING.padding;
  base?: string;
  mobile?: string;
  tablet?: string;
  desktop?: string;
}) => {
  // Se base, mobile, tablet, desktop são fornecidos, use essa abordagem
  if (base && mobile && tablet && desktop) {
    return `${base} ${mobile} md:${tablet} lg:${desktop}`;
  }

  // Caso contrário, use a abordagem original com cols
  if (cols) {
    return [
      RESPONSIVE_GRID_CLASSES.grid,
      RESPONSIVE_GRID_CLASSES.cols[cols],
      RESPONSIVE_SPACING.gap[gap],
      RESPONSIVE_SPACING.padding[padding]
    ].join(' ');
  }

  return '';
};

// Função específica para criar classes de grid responsivo simples
export const createSimpleGridClasses = ({
  base,
  mobile,
  tablet,
  desktop
}: {
  base: string;
  mobile: string;
  tablet: string;
  desktop: string;
}) => {
  return `${base} ${mobile} md:${tablet} lg:${desktop}`;
};

// Breakpoint utilities
export const BREAKPOINTS = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px'
};

// Media query helpers
export const mediaQueries = {
  sm: `@media (min-width: ${BREAKPOINTS.sm})`,
  md: `@media (min-width: ${BREAKPOINTS.md})`,
  lg: `@media (min-width: ${BREAKPOINTS.lg})`,
  xl: `@media (min-width: ${BREAKPOINTS.xl})`,
  '2xl': `@media (min-width: ${BREAKPOINTS['2xl']})`
};

// Hook for responsive behavior
export const useResponsive = () => {
  const getScreenSize = () => {
    if (typeof window === 'undefined') return 'lg';

    const width = window.innerWidth;
    if (width < 640) return 'xs';
    if (width < 768) return 'sm';
    if (width < 1024) return 'md';
    if (width < 1280) return 'lg';
    return 'xl';
  };

  return {
    screenSize: getScreenSize(),
    isMobile: getScreenSize() === 'xs' || getScreenSize() === 'sm',
    isTablet: getScreenSize() === 'md',
    isDesktop: getScreenSize() === 'lg' || getScreenSize() === 'xl'
  };
};
