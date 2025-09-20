/**
 * Provider para Auto-Refresh Global
 *
 * Gerencia o sistema de auto-refresh em toda a aplicação,
 * permitindo controle centralizado e coordenação entre componentes.
 */

/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useCallback, useEffect, useState } from 'react';
import { useAutoRefresh } from '../hooks/useAutoRefresh';
import { cacheInvalidationService } from '../services/CacheInvalidationService';

interface AutoRefreshContextType {
  isGlobalRefreshEnabled: boolean;
  toggleGlobalRefresh: () => void;
  forceRefreshAll: () => Promise<void>;
  refreshStats: {
    totalRefreshes: number;
    lastGlobalRefresh: number;
    activeRefreshers: number;
  };
  registerRefresher: (key: string, refreshFn: () => Promise<void>) => void;
  unregisterRefresher: (key: string) => void;
}

const AutoRefreshContext = createContext<AutoRefreshContextType | undefined>(undefined);

interface AutoRefreshProviderProps {
  children: React.ReactNode;
  defaultEnabled?: boolean;
}

interface RefresherRegistry {
  [key: string]: () => Promise<void>;
}

export const AutoRefreshProvider: React.FC<AutoRefreshProviderProps> = ({
  children,
  defaultEnabled = true,
}) => {
  const [isGlobalRefreshEnabled, setIsGlobalRefreshEnabled] = useState(defaultEnabled);
  const [refresherRegistry, setRefresherRegistry] = useState<RefresherRegistry>({});
  const [refreshStats, setRefreshStats] = useState({
    totalRefreshes: 0,
    lastGlobalRefresh: 0,
    activeRefreshers: 0,
  });

  /**
   * Função principal de refresh global
   */
  const executeGlobalRefresh = useCallback(async () => {
    if (!isGlobalRefreshEnabled) return;

    console.warn('🔄 Iniciando refresh global...');
    const startTime = Date.now();

    try {
      // Executar todos os refreshers registrados em paralelo
      const refreshPromises = Object.entries(refresherRegistry).map(async ([key, refreshFn]) => {
        try {
          await refreshFn();
          console.warn(`✅ Refresh concluído: ${key}`);
        } catch (error) {
          console.error(`❌ Erro no refresh ${key}:`, error);
        }
      });

      await Promise.allSettled(refreshPromises);

      // Invalidar caches críticos após refresh global
      cacheInvalidationService.invalidateCriticalMetrics();

      const duration = Date.now() - startTime;

      setRefreshStats(prev => ({
        totalRefreshes: prev.totalRefreshes + 1,
        lastGlobalRefresh: Date.now(),
        activeRefreshers: Object.keys(refresherRegistry).length,
      }));

      console.warn(`✅ Refresh global concluído em ${duration}ms`);
    } catch (error) {
      console.error('❌ Erro no refresh global:', error);
    }
  }, [isGlobalRefreshEnabled, refresherRegistry]);

  // Auto-refresh global a cada 5 minutos
  useAutoRefresh('global', executeGlobalRefresh, {
    priority: 'low',
    interval: 300000, // 5 minutos
    enabled: isGlobalRefreshEnabled,
  });

  /**
   * Toggle do refresh global
   */
  const toggleGlobalRefresh = useCallback(() => {
    setIsGlobalRefreshEnabled(prev => {
      const newState = !prev;
      console.warn(`🔄 Auto-refresh global ${newState ? 'ativado' : 'desativado'}`);
      return newState;
    });
  }, []);

  /**
   * Força refresh imediato de todos os componentes
   */
  const forceRefreshAll = useCallback(async () => {
    await executeGlobalRefresh();
  }, [executeGlobalRefresh]);

  /**
   * Registra um refresher no sistema global
   */
  const registerRefresher = useCallback(
    (key: string, refreshFn: () => Promise<void>) => {
      setRefresherRegistry(prev => ({
        ...prev,
        [key]: refreshFn,
      }));

      setRefreshStats(prev => ({
        ...prev,
        activeRefreshers: Object.keys(refresherRegistry).length + 1,
      }));

      console.warn(`📝 Refresher registrado: ${key}`);
    },
    [refresherRegistry]
  );

  /**
   * Remove um refresher do sistema global
   */
  const unregisterRefresher = useCallback((key: string) => {
    setRefresherRegistry(prev => {
      const newRegistry = { ...prev };
      delete newRegistry[key];
      return newRegistry;
    });

    setRefreshStats(prev => ({
      ...prev,
      activeRefreshers: Math.max(0, prev.activeRefreshers - 1),
    }));

    console.warn(`🗑️ Refresher removido: ${key}`);
  }, []);

  // Efeito para detectar mudanças de visibilidade da página
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && isGlobalRefreshEnabled) {
        // Quando a página volta a ficar visível, força um refresh
        console.warn('👁️ Página visível novamente, forçando refresh...');
        setTimeout(() => {
          forceRefreshAll();
        }, 1000); // Delay de 1 segundo para evitar múltiplos refreshes
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [isGlobalRefreshEnabled, forceRefreshAll]);

  // Efeito para detectar reconexão de rede
  useEffect(() => {
    const handleOnline = () => {
      if (isGlobalRefreshEnabled) {
        console.warn('🌐 Conexão restaurada, forçando refresh...');
        setTimeout(() => {
          forceRefreshAll();
        }, 2000); // Delay de 2 segundos para garantir estabilidade da conexão
      }
    };

    window.addEventListener('online', handleOnline);

    return () => {
      window.removeEventListener('online', handleOnline);
    };
  }, [isGlobalRefreshEnabled, forceRefreshAll]);

  const contextValue: AutoRefreshContextType = {
    isGlobalRefreshEnabled,
    toggleGlobalRefresh,
    forceRefreshAll,
    refreshStats,
    registerRefresher,
    unregisterRefresher,
  };

  return <AutoRefreshContext.Provider value={contextValue}>{children}</AutoRefreshContext.Provider>;
};

/**
 * Hook para usar o contexto de auto-refresh
 */
export const useAutoRefreshContext = (): AutoRefreshContextType => {
  const context = useContext(AutoRefreshContext);

  if (context === undefined) {
    throw new Error('useAutoRefreshContext deve ser usado dentro de um AutoRefreshProvider');
  }

  return context;
};

/**
 * Hook para registrar um componente no sistema de auto-refresh global
 */
export const useGlobalRefreshRegistration = (
  key: string,
  refreshFunction: () => Promise<void>,
  enabled: boolean = true
) => {
  const { registerRefresher, unregisterRefresher } = useAutoRefreshContext();

  useEffect(() => {
    if (enabled) {
      registerRefresher(key, refreshFunction);

      return () => {
        unregisterRefresher(key);
      };
    }
  }, [key, refreshFunction, enabled, registerRefresher, unregisterRefresher]);
};
