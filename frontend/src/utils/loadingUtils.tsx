import React from 'react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import {
  LoadingSize,
  LoadingVariant,
  SkeletonType,
  LOADING_SIZES,
  LOADING_VARIANTS,
  LOADING_ANIMATIONS,
} from './loadingConstants';

/* eslint-disable react-refresh/only-export-components */
// Função para renderizar diferentes tipos de skeleton
const renderSkeletonByType = (
  type: SkeletonType,
  size: LoadingSize = 'md',
  variant: LoadingVariant = 'default',
  count: number = 1
) => {
  const sizeConfig = LOADING_SIZES[size];
  const variantConfig = LOADING_VARIANTS[variant];

  switch (type) {
    case 'card':
      return Array.from({ length: count }, (_, i) => (
        <Card key={i} className={cn(variantConfig.bg, variantConfig.border, variantConfig.shadow)}>
          <CardHeader className={sizeConfig.container}>
            <div
              className={cn(
                sizeConfig.skeleton,
                variantConfig.skeleton,
                LOADING_ANIMATIONS.pulse,
                'rounded mb-2'
              )}
            />
            <div
              className={cn(
                sizeConfig.skeleton,
                variantConfig.skeleton,
                LOADING_ANIMATIONS.pulse,
                'rounded w-3/4'
              )}
            />
          </CardHeader>
          <CardContent className={sizeConfig.container}>
            <div
              className={cn(
                sizeConfig.skeleton,
                variantConfig.skeleton,
                LOADING_ANIMATIONS.pulse,
                'rounded mb-2'
              )}
            />
            <div
              className={cn(
                sizeConfig.skeleton,
                variantConfig.skeleton,
                LOADING_ANIMATIONS.pulse,
                'rounded w-1/2'
              )}
            />
          </CardContent>
        </Card>
      ));

    case 'dashboard':
      return (
        <div
          className={cn(
            'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
            sizeConfig.gap
          )}
        >
          {Array.from({ length: count }, (_, i) => (
            <Card
              key={i}
              className={cn(variantConfig.bg, variantConfig.border, variantConfig.shadow)}
            >
              <CardContent className={sizeConfig.container}>
                <div
                  className={cn(
                    sizeConfig.skeleton,
                    variantConfig.skeleton,
                    LOADING_ANIMATIONS.pulse,
                    'rounded-full w-12 h-12 mb-4'
                  )}
                />
                <div
                  className={cn(
                    sizeConfig.skeleton,
                    variantConfig.skeleton,
                    LOADING_ANIMATIONS.pulse,
                    'rounded mb-2'
                  )}
                />
                <div
                  className={cn(
                    sizeConfig.skeleton,
                    variantConfig.skeleton,
                    LOADING_ANIMATIONS.pulse,
                    'rounded w-2/3'
                  )}
                />
              </CardContent>
            </Card>
          ))}
        </div>
      );

    case 'tickets':
      return Array.from({ length: count }, (_, i) => (
        <div
          key={i}
          className={cn(
            'flex items-center space-x-4',
            sizeConfig.container,
            variantConfig.bg,
            variantConfig.border,
            'rounded-lg'
          )}
        >
          <div
            className={cn(
              sizeConfig.skeleton,
              variantConfig.skeleton,
              LOADING_ANIMATIONS.pulse,
              'rounded-full w-10 h-10'
            )}
          />
          <div className='flex-1 space-y-2'>
            <div
              className={cn(
                sizeConfig.skeleton,
                variantConfig.skeleton,
                LOADING_ANIMATIONS.pulse,
                'rounded'
              )}
            />
            <div
              className={cn(
                sizeConfig.skeleton,
                variantConfig.skeleton,
                LOADING_ANIMATIONS.pulse,
                'rounded w-3/4'
              )}
            />
          </div>
          <div
            className={cn(
              sizeConfig.skeleton,
              variantConfig.skeleton,
              LOADING_ANIMATIONS.pulse,
              'rounded w-16'
            )}
          />
        </div>
      ));

    case 'list':
      return Array.from({ length: count }, (_, i) => (
        <div
          key={i}
          className={cn(
            'flex items-center justify-between',
            sizeConfig.container,
            variantConfig.bg,
            variantConfig.border,
            'rounded-lg'
          )}
        >
          <div className='flex items-center space-x-3'>
            <div
              className={cn(
                sizeConfig.skeleton,
                variantConfig.skeleton,
                LOADING_ANIMATIONS.pulse,
                'rounded-full w-8 h-8'
              )}
            />
            <div
              className={cn(
                sizeConfig.skeleton,
                variantConfig.skeleton,
                LOADING_ANIMATIONS.pulse,
                'rounded w-32'
              )}
            />
          </div>
          <div
            className={cn(
              sizeConfig.skeleton,
              variantConfig.skeleton,
              LOADING_ANIMATIONS.pulse,
              'rounded w-20'
            )}
          />
        </div>
      ));

    case 'table':
      return (
        <div className={cn(variantConfig.bg, variantConfig.border, 'rounded-lg overflow-hidden')}>
          <div
            className={cn(
              'grid grid-cols-4',
              sizeConfig.gap,
              sizeConfig.container,
              'bg-gray-50 dark:bg-gray-800'
            )}
          >
            {Array.from({ length: 4 }, (_, i) => (
              <div
                key={i}
                className={cn(
                  sizeConfig.skeleton,
                  variantConfig.skeleton,
                  LOADING_ANIMATIONS.pulse,
                  'rounded'
                )}
              />
            ))}
          </div>
          {Array.from({ length: count }, (_, i) => (
            <div
              key={i}
              className={cn(
                'grid grid-cols-4',
                sizeConfig.gap,
                sizeConfig.container,
                'border-t border-gray-200 dark:border-gray-700'
              )}
            >
              {Array.from({ length: 4 }, (_, j) => (
                <div
                  key={j}
                  className={cn(
                    sizeConfig.skeleton,
                    variantConfig.skeleton,
                    LOADING_ANIMATIONS.pulse,
                    'rounded'
                  )}
                />
              ))}
            </div>
          ))}
        </div>
      );

    case 'metrics':
      return (
        <div className={cn('grid grid-cols-2 md:grid-cols-4', sizeConfig.gap)}>
          {Array.from({ length: count }, (_, i) => (
            <Card
              key={i}
              className={cn(variantConfig.bg, variantConfig.border, variantConfig.shadow)}
            >
              <CardContent className={cn(sizeConfig.container, 'text-center')}>
                <div
                  className={cn(
                    sizeConfig.skeleton,
                    variantConfig.skeleton,
                    LOADING_ANIMATIONS.pulse,
                    'rounded w-16 h-8 mx-auto mb-2'
                  )}
                />
                <div
                  className={cn(
                    sizeConfig.skeleton,
                    variantConfig.skeleton,
                    LOADING_ANIMATIONS.pulse,
                    'rounded w-20 h-4 mx-auto'
                  )}
                />
              </CardContent>
            </Card>
          ))}
        </div>
      );

    case 'levels':
      return Array.from({ length: count }, (_, i) => (
        <Card
          key={i}
          className={cn(variantConfig.bg, variantConfig.border, variantConfig.shadow, 'mb-4')}
        >
          <CardHeader className={sizeConfig.container}>
            <div className='flex items-center justify-between'>
              <div
                className={cn(
                  sizeConfig.skeleton,
                  variantConfig.skeleton,
                  LOADING_ANIMATIONS.pulse,
                  'rounded w-24'
                )}
              />
              <div
                className={cn(
                  sizeConfig.skeleton,
                  variantConfig.skeleton,
                  LOADING_ANIMATIONS.pulse,
                  'rounded w-16'
                )}
              />
            </div>
          </CardHeader>
          <CardContent className={sizeConfig.container}>
            <div className={cn('grid grid-cols-3', sizeConfig.gap)}>
              {Array.from({ length: 3 }, (_, j) => (
                <div key={j} className='text-center'>
                  <div
                    className={cn(
                      sizeConfig.skeleton,
                      variantConfig.skeleton,
                      LOADING_ANIMATIONS.pulse,
                      'rounded w-12 h-6 mx-auto mb-1'
                    )}
                  />
                  <div
                    className={cn(
                      sizeConfig.skeleton,
                      variantConfig.skeleton,
                      LOADING_ANIMATIONS.pulse,
                      'rounded w-16 h-4 mx-auto'
                    )}
                  />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ));

    case 'custom':
    default:
      return Array.from({ length: count }, (_, i) => (
        <div
          key={i}
          className={cn(
            sizeConfig.skeleton,
            variantConfig.skeleton,
            LOADING_ANIMATIONS.pulse,
            'rounded',
            sizeConfig.container
          )}
        />
      ));
  }
};

// Componentes de conveniência
export const SkeletonCard = ({
  size = 'md',
  variant = 'default',
}: {
  size?: LoadingSize;
  variant?: LoadingVariant;
}) => renderSkeletonByType('card', size, variant, 1);

export const SkeletonDashboard = ({
  count = 4,
  size = 'md',
  variant = 'default',
}: {
  count?: number;
  size?: LoadingSize;
  variant?: LoadingVariant;
}) => renderSkeletonByType('dashboard', size, variant, count);

export const SkeletonTickets = ({
  count = 5,
  size = 'md',
  variant = 'default',
}: {
  count?: number;
  size?: LoadingSize;
  variant?: LoadingVariant;
}) => renderSkeletonByType('tickets', size, variant, count);

export const SkeletonList = ({
  count = 5,
  size = 'md',
  variant = 'default',
}: {
  count?: number;
  size?: LoadingSize;
  variant?: LoadingVariant;
}) => renderSkeletonByType('list', size, variant, count);

export const SkeletonTable = ({
  rows = 5,
  size = 'md',
  variant = 'default',
}: {
  rows?: number;
  size?: LoadingSize;
  variant?: LoadingVariant;
}) => renderSkeletonByType('table', size, variant, rows);

export const SkeletonMetrics = ({
  count = 4,
  size = 'md',
  variant = 'default',
}: {
  count?: number;
  size?: LoadingSize;
  variant?: LoadingVariant;
}) => renderSkeletonByType('metrics', size, variant, count);

export const SkeletonLevels = ({
  count = 3,
  size = 'md',
  variant = 'default',
}: {
  count?: number;
  size?: LoadingSize;
  variant?: LoadingVariant;
}) => renderSkeletonByType('levels', size, variant, count);

// Export da função principal
export { renderSkeletonByType };
