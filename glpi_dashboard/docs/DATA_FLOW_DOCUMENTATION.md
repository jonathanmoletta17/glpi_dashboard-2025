# Documentação do Fluxo de Dados - GLPI Dashboard

## Visão Geral

Este documento descreve o fluxo padronizado de dados no sistema GLPI Dashboard, desde o backend até os componentes do frontend, incluindo as otimizações implementadas para evitar inconsistências e duplicações.

## Arquitetura do Fluxo de Dados

```
Backend (Python/FastAPI) → API Layer → Request Coordinator → Frontend Services → React Components
```

## 1. Backend (Python/FastAPI)

### Estrutura de Dados Padronizada

#### Convenções de Nomenclatura
- **Backend**: `snake_case` (Python padrão)
- **Frontend**: `camelCase` (JavaScript padrão)

#### DTOs e Enums Consolidados

**Localização**: `backend/core/application/dto/metrics_dto.py`

```python
class TicketStatus(str, Enum):
    NOVO = "novo"
    PENDENTE = "pendente"
    PROGRESSO = "progresso"
    RESOLVIDO = "resolvido"
    FECHADO = "fechado"
    CANCELADO = "cancelado"

class TechnicianLevel(str, Enum):
    N1 = "N1"
    N2 = "N2"
    N3 = "N3"
    N4 = "N4"
```

#### Estrutura Real da API

**IMPORTANTE**: A API retorna arrays simples de objetos, não estruturas aninhadas.

```json
{
    "data": [
        {
            "id": "696",
            "level": "N3",
            "name": "Anderson da Silva Morim de Oliveira",
            "nome": "Anderson da Silva Morim de Oliveira",
            "rank": 1,
            "total": 2624
        },
        {
            "id": "32",
            "level": "N3",
            "name": "Silvio Godinho Valim",
            "nome": "Silvio Godinho Valim",
            "rank": 2,
            "total": 1726
        },
        {
            "id": "252",
            "level": "N2",
            "name": "Alessandro Carbonera Vieira",
            "nome": "Alessandro Carbonera Vieira",
            "rank": 6,
            "total": 548
        }
    ],
    "success": true,
    "message": "Ranking de técnicos obtido com sucesso",
    "metadata": {
        "total_technicians": 45,
        "levels": ["N1", "N2", "N3", "N4"],
        "period": "últimos 90 dias",
        "last_update": "2025-01-30T10:30:00Z"
    }
}
```

#### Níveis de Técnicos Reais

- **N1**: Técnico Nível 1 (Iniciante)
- **N2**: Técnico Nível 2 (Intermediário)
- **N3**: Técnico Nível 3 (Avançado)
- **N4**: Técnico Nível 4 (Especialista)

**Nota**: Não existem níveis "junior", "pleno" ou "senior" na estrutura real dos dados.

#### Dados de Teste Disponíveis

Os dados reais de teste estão disponíveis em:
- `backend/glpi_data/test_results/frontend_api_test_sem_filtros_(chamada_padrão_do_frontend).json`
- `backend/glpi_data/test_results/frontend_api_test_com_filtro_de_nível_n1.json`
- `backend/glpi_data/test_results/frontend_api_test_com_filtro_de_nível_n2.json`
- `backend/glpi_data/test_results/frontend_api_test_com_filtro_de_nível_n3.json`
- `backend/glpi_data/test_results/frontend_api_test_com_filtro_de_nível_n4.json`

Estes arquivos contêm a estrutura real retornada pela API e devem ser usados como referência para desenvolvimento e testes.

## 2. Request Coordinator (Frontend)

### Funcionalidades Implementadas

**Localização**: `frontend/src/services/requestCoordinator.ts`

#### Sistema de Coordenação Inteligente

```typescript
interface RequestConfig {
  debounceMs?: number;        // Debouncing para evitar chamadas excessivas
  throttleMs?: number;        // Throttling baseado em prioridade
  cacheMs?: number;          // Cache inteligente (60s padrão)
  maxConcurrent?: number;    // Limite de requisições simultâneas (5)
  priority?: 'high' | 'normal' | 'low'; // Sistema de prioridades
  retryAttempts?: number;    // Retry com exponential backoff
}
```

#### Normalização de Chaves

```typescript
private normalizeKey(key: string): string {
  // Remove duplicatas similares:
  // "metrics-data" e "metric_data" → "metrics-data"
  // "system-status" e "systemStatus" → "system-status"
}
```

#### Sistema de Fila com Prioridade

```typescript
private readonly priorityLevels = {
  high: 1,    // Requisições críticas (50% do throttle normal)
  normal: 2,  // Requisições padrão
  low: 3,     // Requisições em background (150% do throttle)
};
```

## 3. Frontend Services

### API Service

**Localização**: `frontend/src/services/api.ts`

```typescript
// Exemplo de uso do Request Coordinator
export const getMetrics = async (filters: MetricsFilters) => {
  return requestCoordinator.coordinateRequest(
    `metrics-${JSON.stringify(filters)}`,
    () => httpClient.get('/api/metrics', { params: filters }),
    {
      cacheMs: 30000,      // Cache de 30s para métricas
      priority: 'high',    // Alta prioridade
      debounceMs: 500,     // Debounce de 500ms
      retryAttempts: 2     // 2 tentativas em caso de erro
    }
  );
};
```

### Transformação de Dados

**Localização**: `frontend/src/utils/dataTransform.ts`

```typescript
// Interfaces para a estrutura real da API
interface TechnicianData {
  id: string;
  level: 'N1' | 'N2' | 'N3' | 'N4';
  name: string;
  nome: string; // Campo duplicado retornado pela API
  rank: number;
  total: number;
}

interface ApiResponse {
  data: TechnicianData[];
  success: boolean;
  message: string;
  metadata?: {
    total_technicians: number;
    levels: string[];
    period: string;
    last_update: string;
  };
}

// Função para processar dados da API
export const processApiData = (apiResponse: ApiResponse): ProcessedData => {
  // Validação de estrutura
  if (!apiResponse?.data || !Array.isArray(apiResponse.data)) {
    throw new Error('Estrutura de dados inválida: esperado array em data');
  }

  return {
    technicians: apiResponse.data.map(tech => ({
      id: tech.id,
      name: tech.name,
      level: tech.level, // N1, N2, N3, N4
      rank: tech.rank,
      total: tech.total
    })),
    metadata: apiResponse.metadata || {}
  };
};
```

## 4. React Components

### Hook de Auto-Refresh Inteligente

**Localização**: `frontend/src/hooks/useSmartRefresh.ts`

```typescript
export const useSmartRefresh = (refreshFn: () => Promise<void>, interval = 30000) => {
  // Utiliza o Request Coordinator para evitar duplicações
  const refresh = useCallback(() => {
    return requestCoordinator.coordinateRequest(
      `auto-refresh-${Date.now()}`,
      refreshFn,
      {
        debounceMs: 1000,
        throttleMs: 5000,
        cacheMs: 0, // Sem cache para auto-refresh
        priority: 'low'
      }
    );
  }, [refreshFn]);
};
```

### Componentes de Métricas

```typescript
// Exemplo de componente otimizado
const MetricsCard: React.FC<MetricsCardProps> = ({ filters }) => {
  const [data, setData] = useState<ProcessedData | null>(null);
  const [loading, setLoading] = useState(false);

  const loadMetrics = useCallback(async () => {
    setLoading(true);
    try {
      const apiResponse = await getMetrics(filters);
      const processedData = processApiData(apiResponse);
      setData(processedData);
    } catch (error) {
      console.error('Erro ao carregar métricas:', error);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Auto-refresh inteligente
  useSmartRefresh(loadMetrics, 30000);
};
```

## 5. Sistema de Cache Consolidado

### Estratégias de Cache

1. **Métricas Gerais**: 60 segundos
2. **Status do Sistema**: 30 segundos
3. **Rankings**: 120 segundos
4. **Auto-refresh**: Sem cache

### Invalidação Inteligente

```typescript
// Invalidação baseada em padrões
requestCoordinator.invalidateCache('metrics-*'); // Invalida todas as métricas
requestCoordinator.invalidateCache('system-status'); // Invalida status específico
```

## 6. Monitoramento e Debug

### Logs Estruturados

```typescript
// Logs do Request Coordinator
🔄 Coordenando requisição: metrics-data (normalizada: metrics-data)
💾 Cache hit para metrics-data
🚦 Throttling metrics-data: aguardando 500ms (prioridade: high)
📋 Requisição metrics-data adicionada à fila (prioridade: high)
✅ Requisição metrics-data concluída em 245ms
```

### Estatísticas de Performance

```typescript
const stats = requestCoordinator.getStats();
// {
//   totalRequests: 150,
//   cacheHits: 45,
//   averageResponseTime: 320,
//   queuedRequests: 2,
//   failedRequests: 3
// }
```

## 7. Boas Práticas

### Para Desenvolvedores Backend

1. **Sempre usar DTOs consolidados** de `metrics_dto.py`
2. **Manter convenção snake_case** em Python
3. **Estrutura de resposta padronizada** com array `data` e `metadata`
4. **Validação de dados** antes de enviar para o frontend

### Para Desenvolvedores Frontend

1. **Sempre usar Request Coordinator** para chamadas de API
2. **Configurar prioridades adequadas** (high/normal/low)
3. **Implementar transformação de dados** para normalizar snake_case → camelCase
4. **Usar hooks de auto-refresh** para componentes que precisam de atualização

### Para Otimização de Performance

1. **Cache inteligente** baseado no tipo de dados
2. **Debouncing** para inputs de usuário
3. **Throttling** baseado em prioridade
4. **Retry com exponential backoff** para requisições falhadas
5. **Normalização de chaves** para evitar duplicatas

## 8. Troubleshooting

### Problemas Comuns

#### Cache não funcionando
```typescript
// Verificar se a chave está sendo normalizada corretamente
console.log(requestCoordinator.normalizeKey('metrics-data'));
```

#### Requisições duplicadas
```typescript
// Verificar se está usando o Request Coordinator
const data = await requestCoordinator.coordinateRequest(key, requestFn, config);
```

#### Dados inconsistentes
```typescript
// Verificar processamento de dados
const processed = processApiData(apiResponse);
console.log('Dados processados:', processed);
```

## 9. Roadmap de Melhorias

- [ ] Implementar WebSocket para atualizações em tempo real
- [ ] Adicionar métricas de performance no dashboard
- [ ] Implementar cache persistente (localStorage/IndexedDB)
- [ ] Adicionar compressão de dados para requisições grandes
- [ ] Implementar sistema de notificações para erros críticos

---

**Última atualização**: Janeiro 2025
**Versão**: 1.0
**Responsável**: Sistema de Otimização GLPI Dashboard
