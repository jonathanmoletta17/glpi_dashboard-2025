import {
  LoadingSize,
  LoadingVariant,
  SkeletonType,
  LOADING_SIZES,
  LOADING_VARIANTS,
} from './loadingConstants';

// Função para renderizar diferentes tipos de skeleton
export const renderSkeletonByType = (
  type: SkeletonType,
  size: LoadingSize = 'md',
  variant: LoadingVariant = 'default',
  count: number = 1
) => {
  const sizeConfig = LOADING_SIZES[size];
  const variantConfig = LOADING_VARIANTS[variant];

  // Esta função será implementada nos componentes que a utilizam
  // Movida para arquivo separado para resolver problema de react-refresh
  return { type, size, variant, count, sizeConfig, variantConfig };
};