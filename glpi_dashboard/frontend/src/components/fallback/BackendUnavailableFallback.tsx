import React from 'react';
import { AlertTriangle, RefreshCw, Wifi, WifiOff, Lightbulb } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface BackendUnavailableFallbackProps {
  /** Título personalizado para o fallback */
  title?: string;
  /** Mensagem personalizada */
  message?: string;
  /** Função chamada quando o usuário clica em "Tentar novamente" */
  onRetry?: () => void;
  /** Se deve mostrar o botão de retry */
  showRetry?: boolean;
  /** Classe CSS adicional */
  className?: string;
  /** Tipo de fallback - afeta o ícone e cores */
  type?: 'timeout' | 'connection' | 'server' | 'generic';
  /** Se deve mostrar dados mockados como alternativa */
  showMockData?: boolean;
  /** Função para ativar modo offline */
  onEnableOfflineMode?: () => void;
}

const BackendUnavailableFallback: React.FC<BackendUnavailableFallbackProps> = ({
  title,
  message,
  onRetry,
  showRetry = true,
  className,
  type = 'generic',
  showMockData = false,
  onEnableOfflineMode,
}) => {
  const getConfig = () => {
    switch (type) {
      case 'timeout':
        return {
          icon: AlertTriangle,
          iconColor: 'text-yellow-600 dark:text-yellow-400',
          bgColor: 'bg-yellow-100 dark:bg-yellow-900/20',
          title: title || 'Tempo Limite Excedido',
          message:
            message ||
            'A requisição demorou mais que o esperado. O servidor pode estar sobrecarregado.',
        };
      case 'connection':
        return {
          icon: WifiOff,
          iconColor: 'text-red-600 dark:text-red-400',
          bgColor: 'bg-red-100 dark:bg-red-900/20',
          title: title || 'Sem Conexão com o Servidor',
          message:
            message || 'Não foi possível conectar ao servidor. Verifique sua conexão de rede.',
        };
      case 'server':
        return {
          icon: AlertTriangle,
          iconColor: 'text-orange-600 dark:text-orange-400',
          bgColor: 'bg-orange-100 dark:bg-orange-900/20',
          title: title || 'Erro do Servidor',
          message:
            message || 'O servidor encontrou um erro interno. Tente novamente em alguns minutos.',
        };
      default:
        return {
          icon: Wifi,
          iconColor: 'text-gray-600 dark:text-gray-400',
          bgColor: 'bg-gray-100 dark:bg-gray-900/20',
          title: title || 'Serviço Indisponível',
          message: message || 'O serviço está temporariamente indisponível.',
        };
    }
  };

  const config = getConfig();
  const IconComponent = config.icon;

  return (
    <Card className={cn('h-full', className)}>
      <CardHeader>
        <CardTitle className='flex items-center space-x-2'>
          <div
            className={cn(
              'w-10 h-10 rounded-full flex items-center justify-center',
              config.bgColor
            )}
          >
            <IconComponent className={cn('w-5 h-5', config.iconColor)} />
          </div>
          <span>{config.title}</span>
        </CardTitle>
      </CardHeader>
      <CardContent className='flex flex-col items-center justify-center space-y-6 py-8'>
        <div className='text-center space-y-3 max-w-md'>
          <p className='text-gray-600 dark:text-gray-400 leading-relaxed'>{config.message}</p>

          {type === 'timeout' && (
            <div className='text-sm text-gray-500 dark:text-gray-500 space-y-1'>
              <p className='flex items-center gap-2'>
                <Lightbulb className='w-4 h-4' /> <strong>Dicas:</strong>
              </p>
              <ul className='text-left space-y-1 ml-4'>
                <li>• Tente reduzir o período de consulta</li>
                <li>• Remova filtros complexos</li>
                <li>• Aguarde alguns minutos e tente novamente</li>
              </ul>
            </div>
          )}

          {type === 'connection' && (
            <div className='text-sm text-gray-500 dark:text-gray-500 space-y-1'>
              <p className='flex items-center gap-2'>
                <Lightbulb className='w-4 h-4' /> <strong>Possíveis causas:</strong>
              </p>
              <ul className='text-left space-y-1 ml-4'>
                <li>• Servidor backend não está rodando</li>
                <li>• Problemas de rede</li>
                <li>• Firewall bloqueando a conexão</li>
              </ul>
            </div>
          )}
        </div>

        <div className='flex flex-col sm:flex-row gap-3'>
          {showRetry && onRetry && (
            <button
              onClick={onRetry}
              className='flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
            >
              <RefreshCw className='w-4 h-4' />
              <span>Tentar Novamente</span>
            </button>
          )}

          {showMockData && onEnableOfflineMode && (
            <button
              onClick={onEnableOfflineMode}
              className='flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2'
            >
              <WifiOff className='w-4 h-4' />
              <span>Modo Offline</span>
            </button>
          )}
        </div>

        {showMockData && (
          <div className='text-xs text-gray-500 dark:text-gray-500 text-center max-w-sm'>
            <p>O modo offline mostra dados de exemplo para demonstração da interface.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default BackendUnavailableFallback;

// Componentes de conveniência para casos específicos
export const TimeoutFallback: React.FC<Omit<BackendUnavailableFallbackProps, 'type'>> = props => (
  <BackendUnavailableFallback {...props} type='timeout' />
);

export const ConnectionFallback: React.FC<
  Omit<BackendUnavailableFallbackProps, 'type'>
> = props => <BackendUnavailableFallback {...props} type='connection' />;

export const ServerErrorFallback: React.FC<
  Omit<BackendUnavailableFallbackProps, 'type'>
> = props => <BackendUnavailableFallback {...props} type='server' />;
