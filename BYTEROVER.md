# BYTEROVER HANDBOOK - GLPI Dashboard

*Generated: 2025-01-06*
*Project: GLPI Dashboard - Sistema de Monitoramento e Análise*
*Version: 1.0.0*

---

## Layer 1: System Overview

### Purpose
Sistema completo de dashboard para monitoramento e análise de tickets do GLPI, com interface moderna e responsiva. O projeto oferece métricas em tempo real, ranking de técnicos, sistema de performance e estatísticas com design responsivo otimizado para desktop, tablet e mobile.

### Tech Stack

**Frontend:**
- React 18 com TypeScript
- Vite 5.4.19 para build e desenvolvimento
- Tailwind CSS para estilização
- Axios para requisições HTTP
- Chart.js e Recharts para visualizações
- Radix UI para componentes base
- Framer Motion para animações
- TanStack React Query para gerenciamento de estado

**Backend:**
- Flask 2.3.3 com Python 3.11+
- Flask-CORS para CORS
- Flask-Caching para sistema de cache
- Requests para integração com GLPI API
- Redis para cache (com fallback SimpleCache)
- Pydantic para validação de dados
- Gunicorn para produção

**DevOps:**
- Docker para containerização
- Scripts automatizados de deploy
- GitHub Actions para CI/CD

### Architecture Pattern
**Microservices + SPA**: Backend API REST separado + Frontend React SPA
- **Cache Híbrido**: Sistema inteligente de cache com fallback
- **Logging Estruturado**: Observabilidade completa do sistema
- **Proxy Development**: Vite proxy para desenvolvimento local

### Key Technical Decisions
- Separação completa entre frontend e backend
- Sistema de cache inteligente com warming automático
- Middleware de observabilidade para monitoramento
- Design system baseado em tokens para consistência
- Hooks customizados para reutilização de lógica

---

## Layer 2: Module Map

### Core Modules

#### Frontend Core (`frontend/src/`)
- **components/**: Componentes React organizados por funcionalidade
  - `dashboard/`: Componentes específicos do dashboard (MetricsGrid, ModernDashboard, ProfessionalRankingTable)
  - `ui/`: Componentes de UI reutilizáveis (badge, button, card)
  - `accessibility/`: Componentes de acessibilidade (VisuallyHidden)
- **hooks/**: Hooks customizados para lógica reutilizável
  - `useApi.ts`: Hook para requisições API
  - `useDashboard.ts`: Hook para dados do dashboard
  - `useCache.ts`: Hook para gerenciamento de cache
- **services/**: Serviços de integração
  - `api.ts`: Funções de API
  - `httpClient.ts`: Cliente HTTP configurado
  - `unifiedCache.ts`: Sistema de cache unificado

#### Backend Core (`backend/`)
- **api/**: Endpoints da API REST
  - `routes.py`: Rotas principais da API
  - `hybrid_routes.py`: Rotas híbridas
- **services/**: Serviços de negócio
  - `glpi_service.py`: Integração com GLPI
  - `api_service.py`: Serviços de API
  - `smart_cache.py`: Sistema de cache inteligente
- **utils/**: Utilitários e middleware
  - `observability_middleware.py`: Middleware de monitoramento
  - `structured_logging.py`: Sistema de logging
  - `performance.py`: Utilitários de performance

### Data Layer
- **GLPI Integration**: Integração direta com API do GLPI
- **Cache Layer**: Sistema híbrido Redis/SimpleCache
- **Configuration**: Gerenciamento centralizado de configurações

### Utilities
- **Frontend Utils**: Formatadores, animações, responsividade
- **Backend Utils**: Logging, performance, validação de dados
- **Shared Types**: Definições TypeScript compartilhadas

---

## Layer 3: Integration Guide

### API Endpoints

#### Core Endpoints
- `GET /api/health` - Status de saúde do sistema
- `GET /api/metrics` - Métricas do sistema
- `GET /api/dashboard` - Dados do dashboard
- `GET /api/technicians/ranking` - Ranking de técnicos
- `GET /api/tickets` - Lista de tickets

#### Configuration Endpoints
- `GET /api/config` - Configurações do sistema
- `GET /api/cache/status` - Status do cache

### External Integrations

#### GLPI API Integration
- **Authentication**: User Token + App Token
- **Base URL**: Configurável via `GLPI_URL`
- **Timeout**: Configurável via `API_TIMEOUT`
- **Cache Strategy**: Cache inteligente com warming

#### Environment Configuration

**Development:**
```typescript
// Frontend (Vite proxy)
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, '')
  }
}
```

**Production:**
```typescript
// Frontend
const API_BASE_URL = process.env.VITE_API_BASE_URL || 'http://localhost:5000'
```

**Backend Configuration:**
```python
# Key environment variables
GLPI_URL=https://your-glpi-instance.com/apirest.php
GLPI_USER_TOKEN=your_user_token
GLPI_APP_TOKEN=your_app_token
FLASK_ENV=development|production
REDIS_URL=redis://localhost:6379/0
```

### Data Flow
1. **Frontend Request** → HTTP Client (Axios)
2. **Vite Proxy** (dev) → Backend Flask
3. **Backend Processing** → GLPI API Integration
4. **Cache Layer** → Redis/SimpleCache
5. **Response** → Frontend Components

---

## Layer 4: Extension Points

### Design Patterns

#### Frontend Patterns
- **Custom Hooks Pattern**: Lógica reutilizável encapsulada
- **Compound Components**: Componentes compostos para flexibilidade
- **Provider Pattern**: Context para estado global
- **Observer Pattern**: React Query para cache e sincronização

#### Backend Patterns
- **Middleware Pattern**: Observabilidade e logging
- **Service Layer Pattern**: Separação de responsabilidades
- **Cache-Aside Pattern**: Sistema de cache inteligente
- **Factory Pattern**: Criação de serviços configuráveis

### Customization Areas

#### Theme and Styling
- **Design Tokens**: `design-system/ticket-tokens.ts`
- **Tailwind Config**: Customização de cores e espaçamentos
- **CSS Variables**: Modo escuro/claro

#### API Extensions
- **New Endpoints**: Adicionar em `backend/api/routes.py`
- **Custom Services**: Criar em `backend/services/`
- **Middleware**: Adicionar em `backend/utils/`

#### Component Extensions
- **New Components**: Seguir estrutura em `components/`
- **Custom Hooks**: Adicionar em `hooks/`
- **Utilities**: Expandir em `utils/`

### Configuration Points

#### Frontend Configuration
- **Environment**: `config/environment.ts`
- **App Config**: `config/appConfig.ts`
- **API Client**: `services/httpClient.ts`

#### Backend Configuration
- **Settings**: `config/settings.py`
- **Logging**: `config/logging_config.py`
- **Performance**: `config/performance.py`

### Extension Guidelines

1. **Follow Existing Patterns**: Manter consistência com padrões estabelecidos
2. **Type Safety**: Usar TypeScript para tipagem forte
3. **Error Handling**: Implementar tratamento de erros robusto
4. **Testing**: Adicionar testes para novas funcionalidades
5. **Documentation**: Documentar mudanças e extensões
6. **Performance**: Considerar impacto no cache e performance
7. **Accessibility**: Manter padrões de acessibilidade

### Common Extension Scenarios

- **New Dashboard Widgets**: Criar componentes em `components/dashboard/`
- **Additional GLPI Endpoints**: Estender `services/glpi_service.py`
- **Custom Metrics**: Adicionar em `utils/prometheus_metrics.py`
- **New Cache Strategies**: Implementar em `services/smart_cache.py`
- **UI Components**: Adicionar em `components/ui/`
- **Data Transformations**: Criar utilitários em `utils/`

---

*This handbook provides a comprehensive guide for AI agents and developers working with the GLPI Dashboard project. For specific implementation details, refer to the individual module documentation and code comments.*
