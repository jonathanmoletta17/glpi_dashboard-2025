/**
 * Configurações centralizadas de estilo para rankings
 * Padroniza cores, tamanhos e estilos para componentes de ranking
 */

// Cores para diferentes níveis de ranking
export const RANKING_COLORS = {
  // Cores para posições no ranking
  positions: {
    first: {
      bg: 'bg-gradient-to-r from-yellow-400 to-yellow-600',
      text: 'text-yellow-900',
      border: 'border-yellow-500',
      icon: 'text-yellow-600',
    },
    second: {
      bg: 'bg-gradient-to-r from-gray-300 to-gray-500',
      text: 'text-gray-900',
      border: 'border-gray-400',
      icon: 'text-gray-600',
    },
    third: {
      bg: 'bg-gradient-to-r from-orange-400 to-orange-600',
      text: 'text-orange-900',
      border: 'border-orange-500',
      icon: 'text-orange-600',
    },
    default: {
      bg: 'bg-gradient-to-r from-blue-50 to-blue-100',
      text: 'text-blue-900',
      border: 'border-blue-200',
      icon: 'text-blue-600',
    },
  },

  // Cores para níveis de técnicos
  levels: {
    N1: {
      bg: 'bg-green-50',
      text: 'text-green-800',
      badge: 'bg-green-100 text-green-800',
      border: 'border-green-200',
    },
    N2: {
      bg: 'bg-blue-50',
      text: 'text-blue-800',
      badge: 'bg-blue-100 text-blue-800',
      border: 'border-blue-200',
    },
    N3: {
      bg: 'bg-purple-50',
      text: 'text-purple-800',
      badge: 'bg-purple-100 text-purple-800',
      border: 'border-purple-200',
    },
    N4: {
      bg: 'bg-red-50',
      text: 'text-red-800',
      badge: 'bg-red-100 text-red-800',
      border: 'border-red-200',
    },
  },

  // Cores para métricas de performance
  performance: {
    excellent: {
      bg: 'bg-green-50',
      text: 'text-green-700',
      indicator: 'bg-green-500',
    },
    good: {
      bg: 'bg-blue-50',
      text: 'text-blue-700',
      indicator: 'bg-blue-500',
    },
    average: {
      bg: 'bg-yellow-50',
      text: 'text-yellow-700',
      indicator: 'bg-yellow-500',
    },
    poor: {
      bg: 'bg-red-50',
      text: 'text-red-700',
      indicator: 'bg-red-500',
    },
  },
};

// Tamanhos e espaçamentos padronizados
export const RANKING_SIZES = {
  avatar: {
    small: 'w-8 h-8',
    medium: 'w-10 h-10',
    large: 'w-12 h-12',
  },
  badge: {
    small: 'px-2 py-1 text-xs',
    medium: 'px-3 py-1 text-sm',
    large: 'px-4 py-2 text-base',
  },
  card: {
    padding: 'p-4',
    spacing: 'space-y-3',
    rounded: 'rounded-lg',
  },
};

// Estilos para diferentes tipos de ranking
export const RANKING_VARIANTS = {
  compact: {
    container: 'space-y-2',
    item: 'flex items-center justify-between p-3 rounded-md',
    avatar: RANKING_SIZES.avatar.small,
    badge: RANKING_SIZES.badge.small,
  },
  detailed: {
    container: 'space-y-4',
    item: 'flex items-center justify-between p-4 rounded-lg border',
    avatar: RANKING_SIZES.avatar.medium,
    badge: RANKING_SIZES.badge.medium,
  },
  card: {
    container: 'grid gap-4',
    item: 'p-6 rounded-xl border shadow-sm',
    avatar: RANKING_SIZES.avatar.large,
    badge: RANKING_SIZES.badge.large,
  },
};

// Funções utilitárias para aplicar estilos
export const getRankingPositionStyle = (position: number) => {
  switch (position) {
    case 1:
      return RANKING_COLORS.positions.first;
    case 2:
      return RANKING_COLORS.positions.second;
    case 3:
      return RANKING_COLORS.positions.third;
    default:
      return RANKING_COLORS.positions.default;
  }
};

export const getLevelStyle = (level: string) => {
  const normalizedLevel = level.toUpperCase() as keyof typeof RANKING_COLORS.levels;
  return RANKING_COLORS.levels[normalizedLevel] || RANKING_COLORS.levels.N1;
};

export const getPerformanceStyle = (score: number) => {
  if (score >= 90) return RANKING_COLORS.performance.excellent;
  if (score >= 75) return RANKING_COLORS.performance.good;
  if (score >= 60) return RANKING_COLORS.performance.average;
  return RANKING_COLORS.performance.poor;
};

// Configurações de animação para rankings
export const RANKING_ANIMATIONS = {
  listItem: {
    initial: { opacity: 0, x: -20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 20 },
    transition: { duration: 0.3 },
  },
  stagger: {
    container: {
      animate: {
        transition: {
          staggerChildren: 0.1,
        },
      },
    },
  },
  hover: {
    scale: 1.02,
    y: -2,
    transition: { duration: 0.2 },
  },
};

// Configurações responsivas
export const RANKING_RESPONSIVE = {
  mobile: {
    container: 'px-2',
    item: 'flex-col space-y-2',
    avatar: RANKING_SIZES.avatar.small,
    text: 'text-sm',
  },
  tablet: {
    container: 'px-4',
    item: 'flex-row items-center',
    avatar: RANKING_SIZES.avatar.medium,
    text: 'text-base',
  },
  desktop: {
    container: 'px-6',
    item: 'flex-row items-center',
    avatar: RANKING_SIZES.avatar.large,
    text: 'text-lg',
  },
};

// Configurações de tema escuro
export const RANKING_DARK_THEME = {
  positions: {
    first: {
      bg: 'dark:bg-gradient-to-r dark:from-yellow-600 dark:to-yellow-800',
      text: 'dark:text-yellow-100',
      border: 'dark:border-yellow-600',
    },
    second: {
      bg: 'dark:bg-gradient-to-r dark:from-gray-600 dark:to-gray-800',
      text: 'dark:text-gray-100',
      border: 'dark:border-gray-600',
    },
    third: {
      bg: 'dark:bg-gradient-to-r dark:from-orange-600 dark:to-orange-800',
      text: 'dark:text-orange-100',
      border: 'dark:border-orange-600',
    },
    default: {
      bg: 'dark:bg-gray-800',
      text: 'dark:text-gray-100',
      border: 'dark:border-gray-700',
    },
  },
};

export default {
  RANKING_COLORS,
  RANKING_SIZES,
  RANKING_VARIANTS,
  RANKING_ANIMATIONS,
  RANKING_RESPONSIVE,
  RANKING_DARK_THEME,
  getRankingPositionStyle,
  getLevelStyle,
  getPerformanceStyle,
};
