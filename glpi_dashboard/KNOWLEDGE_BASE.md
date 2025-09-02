# Base de Conhecimento - Dashboard GLPI

## Visão Geral

Este documento contém uma análise completa do sistema de dashboard GLPI, incluindo a arquitetura frontend/backend, fluxo de dados, APIs e estrutura de componentes.

## 📊 Análise da API - Ranking de Técnicos

### Endpoint Principal
- **URL**: `http://localhost:5000/api/technicians/ranking`
- **Método**: GET
- **Timeout**: 300s (cache)
- **Decoradores**: `@monitor_api_endpoint`, `@monitor_performance`, `@cache_with_filters`, `@standard_date_validation`

### Parâmetros de Filtro
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "level": "N3",
  "limit": 100,
  "entity_id": 1
}
```

### Estrutura da Resposta JSON
```json
{
  "cached": false,
  "correlation_id": "uuid-string",
  "data": [
    {
      "avg_resolution_time": 2.5,
      "id": 1471,
      "level": "N3",
      "name": "Joao Pedro Wilson Dias",
      "pending_tickets": 5,
      "rank": 1,
      "resolved_tickets": 45,
      "total_tickets": 50
    }
  ],
  "filters_applied": {
    "end_date": "2024-12-31",
    "limit": 100,
    "start_date": "2024-01-01"
  },
  "response_time_ms": 150.25,
  "success": true
}
```

## 🔧 Lógica do Backend

### Arquivo Principal: `glpi_service.py`

#### Método `get_technician_ranking_with_filters`
- **Localização**: Linhas 7035-7150
- **Funcionalidades**:
  - Validação de autenticação
  - Descoberta dinâmica do campo de técnico
  - Filtros avançados por data, nível e entidade
  - Cache inteligente de 5 minutos
  - Logging para observabilidade

#### Método `_get_technician_ranking_knowledge_base`
- **Localização**: Linhas 3981-4200
- **Abordagem**:
  1. Busca técnicos ativos com perfil ID 6
  2. Usa endpoint `Profile_User` com `forcedisplay`
  3. Fallback para busca direta em `/search/User`
  4. Tratamento robusto de erros HTTP

### Estrutura de Cache
- **Timeout**: 300 segundos (5 minutos)
- **Chave**: Baseada em filtros aplicados
- **Implementação**: Redis com decorador `@cache_with_filters`

## 🎨 Estrutura do Frontend

### Hooks Principais

#### `useDashboard.ts`
- **Localização**: `frontend/src/hooks/useDashboard.ts`
- **Responsabilidades**:
  - Gerenciamento de estado global
  - Chamadas paralelas para APIs
  - Refresh inteligente (5 minutos)
  - Combinação de dados de múltiplas fontes

#### `useApi.ts`
- **Hook**: `useTechnicianRanking` (linhas 170-190)
- **Implementação**:
```typescript
export const useTechnicianRanking = (filters?: {
  start_date?: string;
  end_date?: string;
  level?: string;
  limit?: number;
}) => {
  return useApi(
    ['technician-ranking', filters],
    () => apiService.getTechnicianRanking(filters),
    {
      staleTime: 5 * 60 * 1000, // 5 minutos
      cacheTime: 10 * 60 * 1000, // 10 minutos
    }
  );
};
```

### Componentes de Exibição

#### `RankingTable.tsx`
- **Localização**: `frontend/src/components/dashboard/RankingTable.tsx`
- **Características**:
  - Animações com Framer Motion
  - Estilos por nível (N1-N4)
  - Ícones específicos por categoria
  - Performance otimizada com memoização

#### `ModernDashboard.tsx`
- **Localização**: `frontend/src/components/dashboard/ModernDashboard.tsx`
- **Funcionalidades**:
  - Lazy loading de componentes
  - Suspense boundaries
  - Monitoramento de performance
  - Estado de loading unificado

### Serviços de API

#### `apiService.getTechnicianRanking`
- **Endpoint**: `/api/technicians/ranking`
- **Filtros suportados**: `start_date`, `end_date`, `level`, `limit`
- **Cache**: 5 minutos no frontend, 5 minutos no backend

## 📋 Estudo de Caso: João Dias

### Dados Capturados
```json
{
  "avg_resolution_time": 2.5,
  "id": 1471,
  "level": "N3",
  "name": "Joao Pedro Wilson Dias",
  "pending_tickets": 5,
  "rank": 1,
  "resolved_tickets": 45,
  "total_tickets": 50
}
```

### Análise
- **Posição**: 1º lugar no ranking
- **Nível**: N3 (Sênior)
- **Performance**: 90% de resolução (45/50 tickets)
- **Tempo médio**: 2.5 horas por ticket
- **Status**: 5 tickets pendentes

## 🏗️ Arquitetura do Sistema

### Fluxo de Dados
1. **Frontend** → Hook `useDashboard`
2. **API Service** → `getTechnicianRanking(filters)`
3. **Backend Route** → `/api/technicians/ranking`
4. **GLPI Service** → `get_technician_ranking_with_filters`
5. **GLPI API** → Busca dados reais
6. **Cache Redis** → Armazena por 5 minutos
7. **Response** → JSON estruturado

### Tecnologias Utilizadas

#### Backend
- **Framework**: Flask
- **Cache**: Redis
- **Monitoramento**: Custom decorators
- **Validação**: Custom validators
- **Logging**: Python logging

#### Frontend
- **Framework**: React + TypeScript
- **Estado**: Custom hooks + Context
- **UI**: Tailwind CSS + Shadcn/ui
- **Animações**: Framer Motion
- **Cache**: React Query (TanStack Query)

## 🔍 Endpoints Relacionados

### Técnicos
- `GET /api/technicians` - Lista de técnicos
- `GET /api/technicians/ranking` - Ranking de técnicos

### Sistema
- `GET /api/system/status` - Status do sistema
- `GET /api/filter-types` - Tipos de filtro disponíveis

### Métricas
- `GET /api/dashboard/metrics` - Métricas gerais
- `GET /api/tickets/new` - Novos tickets

## 📈 Métricas de Performance

### Backend
- **Tempo de resposta**: ~150ms (com cache)
- **Cache hit rate**: Monitorado via Redis
- **Timeout**: 300s para operações longas

### Frontend
- **Lazy loading**: Componentes carregados sob demanda
- **Memoização**: Componentes otimizados
- **Refresh inteligente**: 5 minutos automático

## 🛠️ Configurações

### Variáveis de Ambiente
```env
GLPI_URL=http://glpi-server
GLPI_APP_TOKEN=token-app
GLPI_USER_TOKEN=token-user
REDIS_URL=redis://localhost:6379
```

### Limites e Defaults
- **Limite padrão**: 100 técnicos
- **Limite máximo**: 500 técnicos
- **Cache timeout**: 300 segundos
- **Refresh interval**: 300 segundos

## 🔧 Troubleshooting

### Problemas Comuns
1. **404 Not Found**: Verificar se a API está rodando na porta 5000
2. **Cache issues**: Limpar Redis se necessário
3. **GLPI connection**: Verificar tokens e URL
4. **Performance**: Monitorar logs de observabilidade

### Logs Importantes
- `correlation_id`: Para rastreamento de requisições
- `response_time_ms`: Para monitoramento de performance
- `filters_applied`: Para debug de filtros
- `cached`: Para verificar eficiência do cache

---

**Documento gerado em**: Janeiro 2025
**Versão**: 1.0
**Autor**: Análise automatizada do sistema
