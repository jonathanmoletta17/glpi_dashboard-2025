import React, { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';

interface HealthCheckProps {
  interval?: number; // Intervalo em ms para verificar a saúde da API
  onStatusChange?: (isHealthy: boolean, details?: any) => void;
  showIndicator?: boolean;
}

interface HealthStatus {
  isHealthy: boolean;
  lastCheck: Date;
  responseTime: number;
  error?: string;
  details?: any;
}

export const HealthCheck: React.FC<HealthCheckProps> = ({
  interval = 30000, // 30 segundos por padrão
  onStatusChange,
  showIndicator = true
}) => {
  const [healthStatus, setHealthStatus] = useState<HealthStatus>({
    isHealthy: false,
    lastCheck: new Date(),
    responseTime: 0
  });
  const [isChecking, setIsChecking] = useState(false);

  const performHealthCheck = useCallback(async () => {
    if (isChecking) return; // Evitar múltiplas verificações simultâneas
    
    setIsChecking(true);
    const startTime = performance.now();
    
    try {
      console.log('🏥 HealthCheck - Verificando saúde da API...');
      
      const response = await apiService.healthCheck();
      const responseTime = performance.now() - startTime;
      
      const newStatus: HealthStatus = {
        isHealthy: true,
        lastCheck: new Date(),
        responseTime,
        details: response
      };
      
      console.log(`✅ HealthCheck - API saudável (${responseTime.toFixed(2)}ms)`, response);
      setHealthStatus(newStatus);
      onStatusChange?.(true, response);
      
    } catch (error) {
      const responseTime = performance.now() - startTime;
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      
      const newStatus: HealthStatus = {
        isHealthy: false,
        lastCheck: new Date(),
        responseTime,
        error: errorMessage,
        details: error
      };
      
      console.error(`❌ HealthCheck - API não saudável (${responseTime.toFixed(2)}ms):`, error);
      setHealthStatus(newStatus);
      onStatusChange?.(false, error);
    } finally {
      setIsChecking(false);
    }
  }, [isChecking, onStatusChange]);

  // Verificação inicial e periódica
  useEffect(() => {
    // Verificação inicial
    performHealthCheck();
    
    // Configurar verificação periódica
    const intervalId = setInterval(() => {
      performHealthCheck();
    }, interval);
    
    return () => {
      clearInterval(intervalId);
    };
  }, [interval]); // Removido performHealthCheck das dependências para evitar loop

  // Verificar quando a aba volta ao foco
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        console.log('🔄 HealthCheck - Aba voltou ao foco, verificando saúde da API...');
        performHealthCheck();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []); // Removido performHealthCheck das dependências para evitar loop

  if (!showIndicator) {
    return null;
  }

  const getStatusColor = () => {
    if (isChecking) return 'bg-yellow-500';
    return healthStatus.isHealthy ? 'bg-green-500' : 'bg-red-500';
  };

  const getStatusText = () => {
    if (isChecking) return 'Verificando...';
    if (healthStatus.isHealthy) {
      return `API Online (${healthStatus.responseTime.toFixed(0)}ms)`;
    }
    return `API Offline - ${healthStatus.error}`;
  };

  const getStatusIcon = () => {
    if (isChecking) {
      return (
        <div className="animate-spin rounded-full h-3 w-3 border-2 border-white border-t-transparent"></div>
      );
    }
    return (
      <div className={`w-3 h-3 rounded-full ${getStatusColor()}`}></div>
    );
  };

  return (
    <div className="fixed top-4 right-4 z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-3 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {getStatusText()}
          </span>
        </div>
        
        {healthStatus.lastCheck && (
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Última verificação: {healthStatus.lastCheck.toLocaleTimeString()}
          </div>
        )}
        
        {!healthStatus.isHealthy && healthStatus.error && (
          <div className="text-xs text-red-600 dark:text-red-400 mt-1 max-w-xs truncate" title={healthStatus.error}>
            {healthStatus.error}
          </div>
        )}
      </div>
    </div>
  );
};

export default HealthCheck;