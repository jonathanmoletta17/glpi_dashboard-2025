import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';

interface ModuleStatus {
  name: string;
  loaded: boolean;
  error?: string;
  loadTime?: number;
}

interface ModuleHealthCheckProps {
  onStatusChange?: (status: { healthy: boolean; modules: ModuleStatus[] }) => void;
  showIndicator?: boolean;
  interval?: number;
}

const ModuleHealthCheck: React.FC<ModuleHealthCheckProps> = ({
  onStatusChange,
  showIndicator = false,
  interval = 10000 // 10 segundos
}) => {
  const [moduleStatuses, setModuleStatuses] = useState<ModuleStatus[]>([]);
  const [isHealthy, setIsHealthy] = useState(true);

  // Lista expandida de módulos para verificar
  const modulesToCheck = [
    // Componentes principais do dashboard

    { name: 'ProfessionalDashboard', path: './ProfessionalDashboard' },

    // Componentes de dashboard
    { name: 'TicketChart', path: './dashboard/TicketChart' },
    { name: 'NewTicketsList', path: './dashboard/NewTicketsList' },
    { name: 'RankingTable', path: './dashboard/RankingTable' },
    { name: 'RankingTableWithLoading', path: './dashboard/RankingTableWithLoading' },
    { name: 'StatusCard', path: './dashboard/StatusCard' },
    { name: 'ModernDashboard', path: './dashboard/ModernDashboard' },

    // Componentes de carregamento e UI
    { name: 'UnifiedLoading', path: './UnifiedLoading' },
    { name: 'LazyComponents', path: './LazyComponents' },

    // Componentes de fallback e erro
    { name: 'TimeoutFallback', path: './fallback/TimeoutFallback' },
    { name: 'ErrorBoundary', path: './ErrorBoundary' }
  ];

  const checkModuleHealth = async (moduleName: string, modulePath: string): Promise<ModuleStatus> => {
    const startTime = performance.now();

    try {
      // Tentar importar o módulo dinamicamente
      await import(/* @vite-ignore */ modulePath);
      const loadTime = performance.now() - startTime;

      return {
        name: moduleName,
        loaded: true,
        loadTime: Math.round(loadTime)
      };
    } catch (error) {
      return {
        name: moduleName,
        loaded: false,
        error: error instanceof Error ? error.message : 'Erro desconhecido'
      };
    }
  };

  const runHealthCheck = async () => {
    try {
      const results = await Promise.all(
        modulesToCheck.map(module =>
          checkModuleHealth(module.name, module.path)
        )
      );

      setModuleStatuses(results);

      const healthy = results.every(result => result.loaded);
      setIsHealthy(healthy);

      // Notificar mudança de status
      if (onStatusChange) {
        onStatusChange({ healthy, modules: results });
      }

      // Log para desenvolvimento
      if (import.meta.env.MODE === 'development') {
        console.log('🔍 Module Health Check:', {
          healthy,
          modules: results
        });
      }
    } catch (error) {
      console.error('Erro durante health check de módulos:', error);
      setIsHealthy(false);
    }
  };

  // Executar health check periodicamente
  useEffect(() => {
    // Executar imediatamente
    runHealthCheck();

    // Configurar intervalo
    const intervalId = setInterval(runHealthCheck, interval);

    return () => clearInterval(intervalId);
  }, [interval]);

  // Não renderizar nada se o indicador estiver desabilitado
  if (!showIndicator) {
    return null;
  }

  return (
    <div className="fixed bottom-4 left-4 z-50">
      <div className={`
        px-3 py-2 rounded-lg shadow-lg text-sm font-medium transition-all duration-300
        ${isHealthy
          ? 'bg-green-100 text-green-800 border border-green-200'
          : 'bg-red-100 text-red-800 border border-red-200'
        }
      `}>
        <div className="flex items-center space-x-2">
          <div className={`
            w-2 h-2 rounded-full
            ${isHealthy ? 'bg-green-500' : 'bg-red-500'}
          `} />
          <span>
            Módulos: {moduleStatuses.filter(m => m.loaded).length}/{moduleStatuses.length}
          </span>
        </div>

        {/* Detalhes expandidos em desenvolvimento */}
        {import.meta.env.MODE === 'development' && (
          <details className="mt-2">
            <summary className="cursor-pointer text-xs opacity-75 hover:opacity-100">
              Detalhes dos módulos
            </summary>
            <div className="mt-2 space-y-1">
              {moduleStatuses.map((module, index) => (
                <div key={index} className="text-xs flex items-center justify-between">
                  <span className={module.loaded ? 'text-green-700' : 'text-red-700'}>
                    {module.name}
                  </span>
                  <span className="opacity-75 flex items-center">
                    {module.loaded
                      ? `${module.loadTime}ms`
                      : <X className="w-4 h-4 text-red-500" />
                    }
                  </span>
                </div>
              ))}
            </div>
          </details>
        )}
      </div>
    </div>
  );
};

export default ModuleHealthCheck;
