# Documentação Completa dos Endpoints da API

## Visão Geral
Este documento mapeia todos os endpoints disponíveis na API do Dashboard GLPI, incluindo suas rotas backend, métodos frontend correspondentes e interfaces TypeScript.

## Estrutura da API

### Backend
- **Framework**: Flask
- **Blueprints**:
  - `api_bp` (prefixo `/api`)
  - `hybrid_bp` (prefixo `/api/hybrid-pagination`)
- **Arquivos principais**:
  - `backend/api/routes.py` - Endpoints principais
  - `backend/api/hybrid_routes.py` - Endpoints de paginação híbrida
  - `backend/app.py` - Configuração e registro de blueprints

### Frontend
- **Serviços**: `frontend/src/services/api.ts`
- **Hooks**: `frontend/src/hooks/useApi.ts`, `useDashboard.ts`
- **Tipos**: `frontend/src/types/api.ts`, `ticket.ts`

---

## 1. ENDPOINTS DE SAÚDE E STATUS

### 1.1 Health Check
**Backend**: `GET /api/health`
- **Arquivo**: `routes.py:25-45`
- **Funcionalidade**: Verificação básica de saúde da API
- **Cache**: 30 segundos
- **Resposta**: Status da API e timestamp

**Frontend**: `healthCheck()`
- **Arquivo**: `api.ts:280-285`
- **Método**: HEAD request
- **Interface**: Retorna boolean

### 1.2 System Status
**Backend**: `GET /api/status`
- **Arquivo**: `routes.py:1000-1042`
- **Funcionalidade**: Status detalhado do sistema (API, GLPI, cache)
- **Cache**: 60 segundos
- **Validação**: Pydantic models

**Frontend**: `getSystemStatus()`
- **Arquivo**: `api.ts:250-270`
- **Cache**: 60 segundos
- **Interface**: `SystemStatus`

---

## 2. ENDPOINTS DE MÉTRICAS

### 2.1 Métricas Básicas
**Backend**: `GET /api/metrics`
- **Arquivo**: `routes.py:47-150`
- **Funcionalidade**: Métricas gerais do dashboard
- **Parâmetros**: `start_date`, `end_date`, `level`, `status`, `priority`
- **Cache**: 300 segundos (5 minutos)
- **Performance**: Monitoramento de tempo de resposta

**Frontend**: `getMetrics(filters)`
- **Arquivo**: `api.ts:50-150`
- **Cache**: Unificado com TTL configurável
- **Interface**: `DashboardMetrics`
- **Filtros**: `FilterParams`

### 2.2 Métricas Filtradas
**Backend**: `GET /api/metrics/filtered`
- **Arquivo**: `routes.py:251-350`
- **Funcionalidade**: Métricas com filtros avançados
- **Validação**: Pydantic para parâmetros
- **Logging**: Detalhado para auditoria
- **Performance**: Monitoramento de queries

**Frontend**: `fetchDashboardMetrics(filters)`
- **Arquivo**: `api.ts:640-740`
- **Funcionalidade**: Função especializada com tipagem forte
- **Mapeamento**: Conversão de nomes de filtros
- **Timeout**: 60 segundos
- **Interface**: `DashboardMetrics`

---

## 3. ENDPOINTS DE TÉCNICOS

### 3.1 Lista de Técnicos
**Backend**: `GET /api/technicians`
- **Arquivo**: `routes.py:351-450`
- **Funcionalidade**: Lista todos os técnicos
- **Parâmetros**: `level`, `active`, `limit`
- **Cache**: 600 segundos (10 minutos)
- **Filtros**: Por nível e status ativo

### 3.2 Ranking de Técnicos
**Backend**: `GET /api/technicians/ranking`
- **Arquivo**: `routes.py:451-550`
- **Funcionalidade**: Ranking de performance dos técnicos
- **Parâmetros**: `start_date`, `end_date`, `level`, `limit`
- **Cache**: 300 segundos
- **Ordenação**: Por score/performance

**Frontend**: `getTechnicianRanking(filters)`
- **Arquivo**: `api.ts:300-350`
- **Cache**: Coordenado com outros requests
- **Interface**: `TechnicianRanking[]`
- **Performance**: Monitoramento de tempo de resposta

---

## 4. ENDPOINTS DE TICKETS

### 4.1 Novos Tickets
**Backend**: `GET /api/tickets/new`
- **Arquivo**: `routes.py:551-650`
- **Funcionalidade**: Lista de tickets novos
- **Parâmetros**: `limit`, `status`, `priority`, `level`
- **Cache**: 120 segundos
- **Filtros**: Múltiplos critérios

**Frontend**: `getNewTickets(limit)`
- **Arquivo**: `api.ts:350-400`
- **Cache**: 120 segundos
- **Fallback**: Mock data se API falhar
- **Interface**: `Ticket[]`

### 4.2 Detalhes do Ticket
**Backend**: `GET /api/tickets/<int:ticket_id>`
- **Arquivo**: `routes.py:651-750`
- **Funcionalidade**: Detalhes específicos de um ticket
- **Parâmetros**: `ticket_id` (path parameter)
- **Cache**: 180 segundos
- **Validação**: ID numérico obrigatório

**Frontend**: `getTicketById(ticketId)`
- **Arquivo**: `api.ts:450-500`
- **Cache**: Por ID do ticket
- **Fallback**: Mock data
- **Interface**: `Ticket`

---

## 5. ENDPOINTS DE ALERTAS

### 5.1 Alertas do Sistema
**Backend**: `GET /api/alerts`
- **Arquivo**: `routes.py:751-850`
- **Funcionalidade**: Alertas e notificações do sistema
- **Parâmetros**: `level`, `active`, `limit`
- **Cache**: 60 segundos
- **Tipos**: Error, Warning, Info

---

## 6. ENDPOINTS DE CACHE

### 6.1 Estatísticas do Cache
**Backend**: `GET /api/cache/stats`
- **Arquivo**: `routes.py:851-900`
- **Funcionalidade**: Estatísticas de uso do cache
- **Cache**: 30 segundos
- **Métricas**: Hit rate, miss rate, tamanho

### 6.2 Invalidação do Cache
**Backend**: `POST /api/cache/invalidate`
- **Arquivo**: `routes.py:901-950`
- **Funcionalidade**: Limpar cache específico ou geral
- **Parâmetros**: `key` (opcional)
- **Autenticação**: Requerida

**Frontend**: `clearAllCaches()`
- **Arquivo**: `api.ts:550-560`
- **Funcionalidade**: Limpar todos os caches locais

---

## 7. ENDPOINTS HÍBRIDOS (Paginação)

### 7.1 Estatísticas de Paginação
**Backend**: `GET /api/hybrid-pagination/stats`
- **Arquivo**: `hybrid_routes.py:15-50`
- **Funcionalidade**: Estatísticas para paginação híbrida
- **Cache**: 180 segundos
- **Resposta**: Contadores e métricas

### 7.2 Informações de Técnicos
**Backend**: `GET /api/hybrid-pagination/technician-info`
- **Arquivo**: `hybrid_routes.py:51-85`
- **Funcionalidade**: Informações detalhadas de técnicos
- **Parâmetros**: `technician_id`, `include_stats`
- **Cache**: 300 segundos

### 7.3 Limpeza de Cache
**Backend**: `POST /api/hybrid-pagination/cleanup`
- **Arquivo**: `hybrid_routes.py:86-118`
- **Funcionalidade**: Limpeza específica do cache híbrido
- **Autenticação**: Requerida
- **Logging**: Detalhado

---

## 8. ENDPOINTS UTILITÁRIOS

### 8.1 Tipos de Filtros
**Backend**: `GET /api/filter-types`
- **Arquivo**: `routes.py:951-999`
- **Funcionalidade**: Lista tipos de filtros disponíveis
- **Cache**: 3600 segundos (1 hora)
- **Resposta**: Enum de tipos de filtros

**Frontend**: `getFilterTypes()`
- **Arquivo**: `api.ts:500-520`
- **Cache**: Coordenado
- **Interface**: Array de strings

### 8.2 Busca Geral
**Frontend**: `search(query)`
- **Arquivo**: `api.ts:400-450`
- **Funcionalidade**: Busca mock (implementação futura)
- **Interface**: Array de resultados

---

## INTERFACES TYPESCRIPT

### Principais Interfaces

```typescript
// Métricas do Dashboard
interface DashboardMetrics {
  novos?: number;
  pendentes?: number;
  progresso?: number;
  resolvidos?: number;
  total?: number;
  niveis: NiveisMetrics;
  filtros_aplicados?: Record<string, unknown>;
  tempo_execucao?: number;
  timestamp?: string;
  systemStatus?: SystemStatus;
  technicianRanking?: TechnicianRanking[];
}

// Métricas por Nível
interface NiveisMetrics {
  n1: LevelMetrics;
  n2: LevelMetrics;
  n3: LevelMetrics;
  n4: LevelMetrics;
}

// Status do Sistema
interface SystemStatus {
  api: string;
  glpi: string;
  glpi_message: string;
  glpi_response_time: number;
  last_update: string;
  version: string;
}

// Ranking de Técnicos
interface TechnicianRanking {
  id: string;
  name: string;
  level: string;
  rank: number;
  total: number;
  score?: number;
}

// Parâmetros de Filtro
interface FilterParams {
  period?: 'today' | 'week' | 'month';
  levels?: string[];
  status?: string[];
  priority?: string[];
  dateRange?: {
    startDate: string;
    endDate: string;
    label?: string;
  };
  level?: string;
  technician?: string;
  category?: string;
  filterType?: string;
}
```

---

## CONFIGURAÇÕES E CACHE

### Configuração do Cache
- **Backend**: Redis com fallback para SimpleCache
- **Frontend**: Cache unificado com TTL configurável
- **Estratégias**: Por endpoint com tempos específicos

### Performance
- **Monitoramento**: Tempo de resposta em todos os endpoints
- **Logging**: Detalhado para auditoria e debug
- **Validação**: Pydantic models no backend
- **Error Handling**: Tratamento consistente de erros

### Proxy Configuration (Vite)
```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true,
      secure: false
    }
  }
}
```

---

## RESUMO DE ENDPOINTS

| Endpoint | Método | Cache (s) | Frontend Method | Interface |
|----------|--------|-----------|-----------------|----------|
| `/api/health` | GET | 30 | `healthCheck()` | boolean |
| `/api/status` | GET | 60 | `getSystemStatus()` | `SystemStatus` |
| `/api/metrics` | GET | 300 | `getMetrics()` | `DashboardMetrics` |
| `/api/metrics/filtered` | GET | - | `fetchDashboardMetrics()` | `DashboardMetrics` |
| `/api/technicians` | GET | 600 | - | - |
| `/api/technicians/ranking` | GET | 300 | `getTechnicianRanking()` | `TechnicianRanking[]` |
| `/api/tickets/new` | GET | 120 | `getNewTickets()` | `Ticket[]` |
| `/api/tickets/<id>` | GET | 180 | `getTicketById()` | `Ticket` |
| `/api/alerts` | GET | 60 | - | - |
| `/api/cache/stats` | GET | 30 | - | - |
| `/api/cache/invalidate` | POST | - | `clearAllCaches()` | - |
| `/api/filter-types` | GET | 3600 | `getFilterTypes()` | string[] |
| `/api/hybrid-pagination/stats` | GET | 180 | - | - |
| `/api/hybrid-pagination/technician-info` | GET | 300 | - | - |
| `/api/hybrid-pagination/cleanup` | POST | - | - | - |

**Total de Endpoints Mapeados**: 13 principais + 3 híbridos = **16 endpoints**