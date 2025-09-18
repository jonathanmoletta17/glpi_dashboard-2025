/**
 * Biblioteca de animações reutilizáveis para componentes React
 * Centraliza todas as variantes de animação do Framer Motion
 */

import { Variants } from 'framer-motion';

// ============================================================================
// VARIANTES DE CONTAINER
// ============================================================================

/**
 * Animação padrão para containers com stagger children
 */
export const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
    },
  },
};

/**
 * Animação para containers com stagger customizável
 */
export const createContainerVariants = (staggerDelay = 0.1, delayChildren = 0.1): Variants => ({
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: staggerDelay,
      delayChildren,
    },
  },
});

// ============================================================================
// VARIANTES DE ITEM/CARD
// ============================================================================

/**
 * Animação padrão para itens individuais (fade + slide up)
 */
export const itemVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: 'easeOut',
    },
  },
};

/**
 * Animação para cards com escala suave
 */
export const cardVariants: Variants = {
  hidden: { opacity: 0, scale: 0.95, y: 20 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: 'easeOut',
    },
  },
  hover: {
    scale: 1.02,
    transition: {
      duration: 0.2,
      ease: 'easeInOut',
    },
  },
};

/**
 * Animação para itens de lista/tabela
 */
export const listItemVariants: Variants = {
  hidden: { opacity: 0, x: -20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.3,
      ease: 'easeOut',
    },
  },
};

// ============================================================================
// VARIANTES ESPECIALIZADAS
// ============================================================================

/**
 * Animação para modais e overlays
 */
export const modalVariants: Variants = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.3,
      ease: 'easeOut',
    },
  },
  exit: {
    opacity: 0,
    scale: 0.9,
    transition: {
      duration: 0.2,
      ease: 'easeIn',
    },
  },
};

/**
 * Animação para backdrop de modais
 */
export const backdropVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.2,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      duration: 0.2,
    },
  },
};

/**
 * Animação para elementos de ranking/posição
 */
export const rankingVariants: Variants = {
  hidden: { opacity: 0, scale: 0.8, y: 30 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: 'easeOut',
      type: 'spring',
      stiffness: 100,
    },
  },
};

/**
 * Animação para métricas/números
 */
export const metricsVariants: Variants = {
  hidden: { opacity: 0, scale: 0.5 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.6,
      ease: 'easeOut',
      type: 'spring',
      stiffness: 120,
    },
  },
};

// ============================================================================
// VARIANTES DE LOADING/SKELETON
// ============================================================================

/**
 * Animação para skeleton loading
 */
export const skeletonVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.3,
    },
  },
};

/**
 * Animação pulsante para loading
 */
export const pulseVariants: Variants = {
  pulse: {
    opacity: [0.5, 1, 0.5],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

// ============================================================================
// TRANSIÇÕES CUSTOMIZÁVEIS
// ============================================================================

/**
 * Configurações de transição reutilizáveis
 */
export const transitions = {
  fast: {
    duration: 0.2,
    ease: 'easeOut',
  },
  normal: {
    duration: 0.4,
    ease: 'easeOut',
  },
  slow: {
    duration: 0.6,
    ease: 'easeOut',
  },
  spring: {
    type: 'spring' as const,
    stiffness: 100,
    damping: 15,
  },
  bouncy: {
    type: 'spring' as const,
    stiffness: 200,
    damping: 10,
  },
};

// ============================================================================
// FACTORY FUNCTIONS
// ============================================================================

/**
 * Cria variantes customizadas para fade in/out
 */
export const createFadeVariants = (duration = 0.4): Variants => ({
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration, ease: 'easeOut' },
  },
});

/**
 * Cria variantes customizadas para slide
 */
export const createSlideVariants = (
  direction: 'up' | 'down' | 'left' | 'right' = 'up',
  distance = 20,
  duration = 0.4
): Variants => {
  const getInitialPosition = () => {
    switch (direction) {
      case 'up':
        return { y: distance };
      case 'down':
        return { y: -distance };
      case 'left':
        return { x: distance };
      case 'right':
        return { x: -distance };
      default:
        return { y: distance };
    }
  };

  return {
    hidden: {
      opacity: 0,
      ...getInitialPosition(),
    },
    visible: {
      opacity: 1,
      x: 0,
      y: 0,
      transition: {
        duration,
        ease: 'easeOut',
      },
    },
  };
};

/**
 * Cria variantes customizadas para escala
 */
export const createScaleVariants = (initialScale = 0.9, duration = 0.4): Variants => ({
  hidden: {
    opacity: 0,
    scale: initialScale,
  },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration,
      ease: 'easeOut',
    },
  },
});

// ============================================================================
// PRESETS PARA CASOS COMUNS
// ============================================================================

/**
 * Preset para dashboard cards
 */
export const dashboardPresets = {
  container: createContainerVariants(0.1, 0.2),
  card: cardVariants,
  metrics: metricsVariants,
};

/**
 * Preset para tabelas e listas
 */
export const tablePresets = {
  container: createContainerVariants(0.05, 0.1),
  row: listItemVariants,
  ranking: rankingVariants,
};

/**
 * Preset para modais e overlays
 */
export const modalPresets = {
  backdrop: backdropVariants,
  modal: modalVariants,
  content: createSlideVariants('up', 30, 0.3),
};

/**
 * Preset para loading states
 */
export const loadingPresets = {
  skeleton: skeletonVariants,
  pulse: pulseVariants,
  fade: createFadeVariants(0.3),
};

/**
 * Preset para grids de métricas
 */
export const gridPresets = {
  container: createContainerVariants(0.1, 0.15),
  item: itemVariants,
};

/**
 * Preset para listas e rankings
 */
export const listPresets = {
  container: createContainerVariants(0.05, 0.1),
  item: listItemVariants,
};

/**
 * Preset para cards genéricos
 */
export const cardPresets = {
  hover: cardVariants,
  scale: createScaleVariants(0.95, 0.2),
  fade: createFadeVariants(0.3),
};
