import React from 'react';

interface FooterProps {
  lastUpdated?: Date;
  isOnline: boolean;
}

export const Footer: React.FC<FooterProps> = ({ lastUpdated, isOnline }) => {
  return (
    <footer className='w-full h-8 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700'>
      <div className='container mx-auto px-4 h-full'>
        <div className='flex items-center justify-between'>
          {/* Texto Institucional */}
          <div className='text-xs text-gray-600 dark:text-gray-400'>
            © 2025 Departamento de Tecnologia do Estado
          </div>

          {/* Status + Última Atualização */}
          <div className='flex items-center space-x-4'>
            {lastUpdated && (
              <span className='text-xs text-gray-600 dark:text-gray-400'>
                Última atualização: {lastUpdated.toLocaleTimeString('pt-BR')}
              </span>
            )}
            <div className='flex items-center space-x-2'>
              <div
                className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500' : 'bg-red-500'}`}
              ></div>
              <span className='text-xs text-gray-600 dark:text-gray-400'>
                {isOnline ? 'Online' : 'Offline'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};
