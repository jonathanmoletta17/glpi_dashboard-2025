# BYTEROVER HANDBOOK - GLPI Dashboard

*Generated: 2025-01-09*
*Project: GLPI Dashboard - Sistema de Dashboard Moderno*
*Version: Estável/Produção*

---

## 🎯 LAYER 1: SYSTEM OVERVIEW

### Purpose
Sistema de dashboard moderno e responsivo para visualização de métricas e dados do GLPI. Oferece interface interativa com ranking de técnicos, métricas em tempo real, suporte a modo escuro e design responsivo para desktop, tablet e mobile.

### Tech Stack

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS + Radix UI
- TanStack Query (data fetching)
- Chart.js + Recharts (visualizações)
- Framer Motion (animações)
- Axios (HTTP client)

**Backend:**
- Flask 2.3.3 + Python 3.12+
- Flask-CORS, Flask-Caching, Flask-SQLAlchemy
- Redis (cache)
- Pydantic (validação)
- Gunicorn/Uvicorn (produção)
- PyYAML (configuração)

**DevOps & Tools:**
- Docker + Docker Compose
- Prometheus (monitoramento)
- Pre-commit hooks
- ESLint + Prettier
- Vitest + Playwright (testes)
- GitHub Actions

### Architecture Pattern
**Microservices com Frontend SPA**
- Frontend React SPA comunicando via REST API
- Backend Flask com arquitetura em camadas
- Cache inteligente (SimpleCache/Redis)
- Separação clara entre apresentação e lógica de negócio
- Sistema de observabilidade e métricas

### Key Technical Decisions
- Cache híbrido para otimização de performance
- Sistema de paginação dinâmica
- Logging estruturado para observabilidade
- Design system baseado em tokens
- Arquitetura modular e extensível

---

## 🗺️ LAYER 2: MODULE MAP

### Core Modules

#### Frontend Core (`/frontend/src`)
- **`components/`** - Componentes React reutilizáveis
  - `ProfessionalDashboard.tsx` - Dashboard principal
  - `TechnicianRanking.tsx` - Ranking de técnicos
  - `TicketList.tsx` - Lista de tickets
  - `ui/` - Componentes base do design system

- **`hooks/`** - Custom hooks para lógica de estado
  - `useDashboard.ts` - Gerenciamento do dashboard
  - `useApi.ts` - Integração com API
  - `useCache.ts` - Gerenciamento de cache

- **`services/`** - Camada de serviços
  - `api.ts` - Cliente HTTP principal
  - `unifiedCache.ts` - Sistema de cache unificado
  - `requestBatcher.ts` - Batching de requisições

#### Backend Core (`/backend`)
- **`api/`** - Endpoints REST
  - `routes.py` - Rotas principais
  - `hybrid_routes.py` - Rotas híbridas

- **`services/`** - Lógica de negócio
  - `glpi_service.py` - Integração com GLPI
  - `mock_glpi_service.py` - Mock para desenvolvimento
  - `cache_warming.py` - Aquecimento de cache

- **`utils/`** - Utilitários e middleware
  - `smart_cache.py` - Cache inteligente
  - `prometheus_metrics.py` - Métricas
  - `structured_logger.py` - Logging estruturado

### Data Layer
- **Cache Redis** - Cache distribuído para produção
- **SimpleCache** - Cache local para desenvolvimento
- **GLPI API** - Fonte de dados externa
- **JSON Files** - Cache persistente para ranges de técnicos

### Configuration Layer
- **`config/settings.py`** - Configurações centralizadas
- **`.env`** - Variáveis de ambiente
- **`docker-compose.yml`** - Orquestração de containers
- **`pyproject.toml`** - Configuração Python

---

## 🔌 LAYER 3: INTEGRATION GUIDE

### API Endpoints

#### Dashboard APIs
```
GET /api/dashboard/metrics - Métricas gerais
GET /api/dashboard/technicians - Ranking de técnicos
GET /api/tickets - Lista de tickets com paginação
GET /api/tickets/{id} - Detalhes do ticket
GET /api/health - Health check
GET /api/cache/stats - Estatísticas de cache
```

#### Configuration Endpoints
```
GET /api/config/levels - Configuração de níveis
POST /api/cache/warm - Aquecimento de cache
DELETE /api/cache/clear - Limpeza de cache
```

### External Integrations

#### GLPI API Integration
```python
# Configuração necessária
GLPI_URL=http://your-glpi-server/glpi
GLPI_USER_TOKEN=your-user-token
GLPI_APP_TOKEN=your-app-token
```

#### Redis Cache
```python
# Configuração Redis
REDIS_URL=redis://localhost:6379/0
CACHE_TYPE=redis  # ou 'simple' para desenvolvimento
```

### Frontend-Backend Communication
```typescript
// Configuração do cliente API
VITE_API_URL=http://localhost:8000

// Headers padrão
headers: {
  'Content-Type': 'application/json',
  'X-Requested-With': 'XMLHttpRequest'
}
```

### Docker Integration
```yaml
# Serviços principais
services:
  frontend: # Vite dev server
  backend:  # Flask application
  redis:    # Cache layer
  prometheus: # Monitoring
```

---

## 🔧 LAYER 4: EXTENSION POINTS

### Design Patterns Used

#### Service Layer Pattern
- `GLPIService` - Abstração da API GLPI
- `CacheService` - Gerenciamento de cache
- `MetricsService` - Coleta de métricas

#### Repository Pattern
- Abstração de acesso a dados
- Mock services para testes
- Fallback strategies

#### Observer Pattern
- Sistema de notificações
- Cache invalidation
- Real-time updates

### Customization Areas

#### Theme System
```typescript
// Tokens de design customizáveis
/src/design-system/tokens.ts
/src/design-system/component-patterns.ts
```

#### Metrics Configuration
```python
# Configuração de métricas
/backend/config/performance.py
/backend/utils/prometheus_metrics.py
```

#### Cache Strategies
```python
# Estratégias de cache extensíveis
/backend/utils/smart_cache.py
/backend/services/cache_warming.py
```

### Plugin Architecture

#### Frontend Plugins
- Custom hooks para funcionalidades específicas
- Componentes plugáveis via props
- Service workers para cache offline

#### Backend Extensions
- Middleware customizável
- Decorators para funcionalidades transversais
- Sistema de alertas configurável

### Development Workflows

#### Setup Scripts
```bash
# Automação de setup
./setup.sh      # Linux/macOS
./setup.bat     # Windows
```

#### Testing Framework
```bash
# Frontend tests
npm run test
npm run test:coverage

# Backend tests
pytest tests/
```

#### Deployment
```bash
# Docker deployment
docker-compose up -d

# Production scripts
./deploy.sh
./validate-stable.sh
```

---

## 📋 VALIDATION CHECKLIST

- ✅ All 4 required sections present
- ✅ Architecture pattern identified (Microservices + SPA)
- ✅ 6+ core modules documented
- ✅ Tech stack matches project reality
- ✅ Extension points and patterns identified
- ✅ API endpoints documented
- ✅ Integration points mapped
- ✅ Development workflows included

---

*This handbook provides a comprehensive guide for AI agents and developers working with the GLPI Dashboard project. It covers architecture, modules, integrations, and extension points for efficient navigation and development.*