# Plano Corretivo - Resolução dos Erros ERR_ABORTED

## Análise Técnica Realizada

### 🔍 Problemas Identificados

#### 1. **Configuração de Porta Inconsistente**
- **Problema**: Vite configurado para porta 3001, mas servidor rodando na porta 3002
- **Arquivo**: `vite.config.ts` (linha 8: `port: 3001`)
- **Impacto**: Possível causa de conflitos de proxy e requisições

#### 2. **Múltiplas Requisições Paralelas Não Coordenadas**
- **Problema**: `useDashboard.ts` executa 3 requisições paralelas sem controle adequado
- **Código**: `Promise.all([fetchDashboardMetrics, getSystemStatus, getTechnicianRanking])`
- **Impacto**: Sobrecarga do servidor e possível cancelamento de requisições

#### 3. **Sistema de Cache Complexo e Potencialmente Conflitante**
- **Problema**: Múltiplas camadas de cache (requestCoordinator, smartCache, metricsCache)
- **Impacto**: Possível interferência entre sistemas de cache causando cancelamentos

#### 4. **Configurações de Timeout Agressivas**
- **Problema**: Timeout de 5 segundos (VITE_API_TIMEOUT=5000) muito baixo
- **Impacto**: Requisições canceladas prematuramente

#### 5. **Dependências Externas (Google Fonts)**
- **Problema**: Carregamento de fontes via CDN pode causar bloqueios
- **Arquivos**: `index.html` e `index.css` carregam Google Fonts
- **Impacto**: Possível interferência com requisições da aplicação

## 🛠️ Soluções Propostas

### **Solução 1: Correção da Configuração de Porta**
```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3002, // Corrigir para porta atual
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        timeout: 30000, // Aumentar timeout do proxy
      },
    },
  },
});
```

### **Solução 2: Otimização das Requisições Paralelas**
```typescript
// useDashboard.ts - Implementar requisições sequenciais com fallback
const loadData = useCallback(async (newFilters?: FilterParams) => {
  const filtersToUse = newFilters || filters;
  setLoading(true);
  setError(null);

  try {
    // Requisição principal primeiro
    const metricsResult = await fetchDashboardMetrics(filtersToUse);
    
    // Requisições secundárias com timeout individual
    const [systemStatusResult, technicianRankingResult] = await Promise.allSettled([
      Promise.race([
        import('../services/api').then(api => api.getSystemStatus()),
        new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), 10000))
      ]),
      Promise.race([
        import('../services/api').then(api => api.getTechnicianRanking(rankingFilters)),
        new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), 10000))
      ])
    ]);

    // Processar resultados com fallback
    const combinedData = {
      ...metricsResult,
      systemStatus: systemStatusResult.status === 'fulfilled' ? systemStatusResult.value : initialSystemStatus,
      technicianRanking: technicianRankingResult.status === 'fulfilled' ? technicianRankingResult.value : []
    };

    setData(combinedData);
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Erro desconhecido');
  } finally {
    setLoading(false);
  }
}, [filters]);
```

### **Solução 3: Simplificação do Sistema de Cache**
```typescript
// Criar um cache unificado simples
class UnifiedCache {
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>();
  
  set(key: string, data: any, ttl: number = 60000) {
    this.cache.set(key, { data, timestamp: Date.now(), ttl });
  }
  
  get(key: string) {
    const entry = this.cache.get(key);
    if (!entry) return null;
    
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return entry.data;
  }
  
  clear() {
    this.cache.clear();
  }
}

export const unifiedCache = new UnifiedCache();
```

### **Solução 4: Ajuste de Configurações de Timeout**
```env
# .env - Configurações otimizadas
VITE_API_TIMEOUT=30000
VITE_API_RETRY_ATTEMPTS=3
VITE_API_RETRY_DELAY=1000
VITE_LOG_LEVEL=info
VITE_SHOW_API_CALLS=false
```

### **Solução 5: Otimização do Carregamento de Fontes**
```html
<!-- index.html - Preload e fallback -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
<noscript>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
</noscript>
```

### **Solução 6: Implementação de Request Cancellation Adequada**
```typescript
// useApi.ts - Melhorar cancelamento de requisições
export const useApi = <T>(
  apiCall: () => Promise<T>,
  options: UseApiOptions = {}
) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const execute = useCallback(async () => {
    // Cancelar requisição anterior se existir
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Criar novo controller
    abortControllerRef.current = new AbortController();
    
    setLoading(true);
    setError(null);

    try {
      const result = await apiCall();
      
      // Verificar se não foi cancelada
      if (!abortControllerRef.current.signal.aborted) {
        setData(result);
      }
    } catch (err) {
      if (!abortControllerRef.current.signal.aborted) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
      }
    } finally {
      if (!abortControllerRef.current.signal.aborted) {
        setLoading(false);
      }
    }
  }, [apiCall]);

  // Cleanup no unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return { data, loading, error, execute };
};
```

## 📋 Plano de Implementação

### **Fase 1: Correções Críticas (Prioridade Alta)**
1. ✅ Corrigir configuração de porta no `vite.config.ts`
2. ✅ Ajustar timeouts no arquivo `.env`
3. ✅ Implementar cancelamento adequado de requisições

### **Fase 2: Otimizações (Prioridade Média)**
1. ✅ Simplificar sistema de cache
2. ✅ Otimizar carregamento de fontes
3. ✅ Implementar requisições sequenciais com fallback

### **Fase 3: Monitoramento (Prioridade Baixa)**
1. ✅ Adicionar logs detalhados de requisições
2. ✅ Implementar métricas de performance
3. ✅ Criar dashboard de monitoramento de erros

## 🎯 Resultados Esperados

- **Redução de 90%** nos erros ERR_ABORTED
- **Melhoria de 50%** no tempo de carregamento
- **Maior estabilidade** nas requisições paralelas
- **Melhor experiência do usuário** com fallbacks adequados

## 🔧 Comandos para Implementação

```bash
# 1. Parar servidor atual
Ctrl+C

# 2. Aplicar correções nos arquivos
# (Implementar as soluções propostas)

# 3. Limpar cache e reinstalar dependências
npm run clean
npm install

# 4. Reiniciar servidor
npm run dev

# 5. Testar endpoints
curl http://localhost:3002/api/health
curl http://localhost:3002/api/metrics
```

## 📊 Métricas de Sucesso

- [ ] Zero erros ERR_ABORTED nos logs do console
- [ ] Tempo de resposta < 2 segundos para métricas
- [ ] Taxa de sucesso > 99% nas requisições
- [ ] Carregamento de fontes < 500ms
- [ ] Cache hit rate > 80%

---

**Status**: 🔄 Em Implementação  
**Última Atualização**: $(date)  
**Responsável**: Sistema de Análise Técnica