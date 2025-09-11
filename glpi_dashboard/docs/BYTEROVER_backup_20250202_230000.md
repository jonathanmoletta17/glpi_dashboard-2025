# 🚀 BYTEROVER HANDBOOK - GLPI Dashboard

> **Comprehensive AI Agent Navigation Guide**
> Sistema de dashboard profissional para análise de performance de técnicos GLPI

---

## 🏗️ LAYER 1: ARCHITECTURE OVERVIEW

### System Vision
Dashboard interativo para monitoramento de performance de técnicos GLPI com foco em:
- **Análise de Performance**: Métricas detalhadas de produtividade
- **Ranking Dinâmico**: Classificação automática baseada em KPIs
- **Cache Inteligente**: Sistema híbrido para otimização de performance
- **Observabilidade**: Monitoramento completo com métricas e logs estruturados

### Architecture Pattern
**Microservices + SPA (Single Page Application)**
- Frontend React independente
- Backend Flask como API REST
- Cache distribuído (Redis/SimpleCache)
- Monitoramento com Prometheus

### Technology Stack

#### Frontend
- **React 18** - Framework principal
- **TypeScript** - Type safety
- **Vite** - Build tool e dev server
- **Tailwind CSS** - Styling framework
- **Recharts** - Visualização de dados

#### Backend
- **Flask 2.3.3** - Web framework
- **Python 3.11+** - Runtime
- **SimpleCache/Redis** - Sistema de cache
- **Prometheus** - Métricas e monitoramento
- **Structured Logging** - Observabilidade

#### DevOps
- **Docker & Docker Compose** - Containerização
- **GitHub Actions** - CI/CD
- **Prometheus** - Monitoring stack
- **Environment-based Config** - Configuração flexível

### Key Technical Decisions

#### Cache Híbrido
- **Desenvolvimento**: SimpleCache (local)
- **Produção**: Redis (distribuído)
- **Estratégia**: Cache warming proativo
- **TTL Inteligente**: Baseado em padrões de uso

#### Sistema de Paginação Híbrido
- **Frontend**: Paginação virtual para grandes datasets
- **Backend**: Paginação dinâmica com otimização de queries
- **Cache**: Pré-carregamento de páginas adjacentes

#### Logging Estruturado
- **Formato**: JSON estruturado
- **Níveis**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Contexto**: Request ID, User ID, Performance metrics
- **Integração**: Prometheus metrics automáticos

### Additional Features
- Sistema de paginação dinâmica
- Design system baseado em tokens
- Arquitetura modular e extensível
- Request batching para otimização
- Sistema de alertas configurável

---

## 🗺️ LAYER 2: MODULE MAP

### Frontend Core (`/frontend/src`)

#### Components (`/components`)
- **`dashboard/ModernDashboard.tsx`** - Dashboard principal modernizado com métricas
- **`dashboard/MetricsGrid.tsx`** - Grid de métricas responsivo
- **`dashboard/ProfessionalRankingTable.tsx`** - Tabela de ranking de técnicos
- **`dashboard/ProfessionalTicketsList.tsx`** - Lista de tickets com scroll otimizado
- **`TicketDetailModal.tsx`** - Modal de detalhes do ticket
- **`MetricCard.tsx`** - Componente de métricas reutilizável
- **`RecentTickets.tsx`** - Visualização de tickets recentes
- **`CacheManager.tsx`** - Gerenciamento de cache frontend
- **`CacheNotification.tsx`** - Notificações de cache
- **`ErrorBoundary.tsx`** - Tratamento de erros
- **`ui/`** - Componentes base do design system
- **`common/UnifiedLoading.tsx`** - Componente de loading unificado

#### Hooks (`/hooks`)
- **`useDashboard.ts`** - Gerenciamento de estado do dashboard
- **`useApi.ts`** - Integração com API e cache
- **`useCache.ts`** - Gerenciamento de cache local
- **`useSmartRefresh.ts`** - Estratégias de refresh inteligente

#### Services (`/services`)
- **`api.ts`** - Cliente HTTP principal
- **`httpClient.ts`** - Configuração do cliente HTTP
- **`unifiedCache.ts`** - Sistema de cache unificado
- **`requestBatcher.ts`** - Batching de requisições

#### Design System (`/design-system`)
- **`tokens.ts`** - Design tokens e variáveis
- **`component-patterns.ts`** - Padrões de componentes reutilizáveis
- **`spacing.ts`** - Sistema de espaçamento

### Backend Core (`/backend`)

#### API Layer (`/api`)
- **`routes.py`** - Rotas principais da API
- **`hybrid_routes.py`** - Rotas avançadas com paginação híbrida

#### Services (`/services`)
- **`glpi_service.py`** - Integração principal com GLPI API
- **`api_service.py`** - Camada de serviço interno
- **`cache_warming.py`** - Aquecimento proativo de cache

#### Configuration (`/config`)
- **`settings.py`** - Gerenciamento de configurações da aplicação
- **`logging_config.py`** - Configuração de logging estruturado
- **`performance.py`** - Configuração de monitoramento de performance

#### Utilities (`/utils`)
- **`smart_cache.py`** - Cache inteligente com TTL dinâmico
- **`prometheus_metrics.py`** - Métricas customizadas do Prometheus
- **`structured_logger.py`** - Logging estruturado centralizado
- **`observability_middleware.py`** - Middleware de métricas e monitoramento
- **`dynamic_pagination.py`** - Utilitários de paginação avançada
- **`response_formatter.py`** - Padronização de respostas da API

#### Data Layer (`/schemas`)
- **`dashboard.py`** - Schemas de validação de dados

### Infrastructure Layer

#### Cache System
- **Redis** - Cache distribuído para produção
- **SimpleCache** - Cache local para desenvolvimento
- **JSON Files** - Cache persistente para ranges de técnicos

#### External Integrations
- **GLPI API** - Fonte de dados externa
- **Prometheus** - Coleta e armazenamento de métricas
- **Docker** - Containerização e orquestração

#### Configuration Files
- **`.env`** - Variáveis de ambiente
- **`docker-compose.yml`** - Orquestração de containers
- **`pyproject.toml`** - Configuração Python
- **`vite.config.ts`** - Configuração do Vite
- **`tailwind.config.js`** - Configuração do Tailwind CSS

---

## 🔌 LAYER 3: INTEGRATION GUIDE

### API Endpoints

#### Core Dashboard APIs
```
GET /api/dashboard/metrics     # Métricas gerais do dashboard
GET /api/dashboard/technicians # Ranking de técnicos
GET /api/tickets              # Lista de tickets com paginação
GET /api/tickets/{id}         # Detalhes específicos do ticket
GET /api/technicians/ranking  # Ranking de performance de técnicos
```

#### System Management
```
GET /api/health               # Health check da aplicação
GET /api/cache/stats          # Estatísticas de cache
POST /api/cache/warm          # Aquecimento de cache
DELETE /api/cache/clear       # Limpeza de cache
```

#### Monitoring & Metrics
```
GET /metrics                  # Export de métricas Prometheus
GET /api/metrics              # Métricas da aplicação
GET /alerts                   # Gerenciamento de alertas
```

### External Integrations

#### GLPI API Integration
```python
# Configuração necessária
GLPI_URL=http://your-glpi-server/glpi
GLPI_USER_TOKEN=your-user-token
GLPI_APP_TOKEN=your-app-token

# Autenticação: Token-based
# Base path: /apirest.php/
# Rate limiting: Gerenciado por smart caching
```

#### Redis Cache Configuration
```python
# Configuração Redis
REDIS_URL=redis://localhost:6379/0
CACHE_TYPE=redis  # ou 'simple' para desenvolvimento
```

#### Frontend-Backend Communication
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
  frontend:   # Vite dev server
  backend:    # Flask application
  redis:      # Cache layer
  prometheus: # Monitoring
```

### Configuration Management

#### Backend Configuration
- **`.env`** - Variáveis de ambiente (API keys, URLs de banco)
- **`config/settings.py`** - Configurações da aplicação
- **`pyproject.toml`** - Configuração do projeto Python
- **`requirements.txt`** - Dependências Python

#### Frontend Configuration
- **`.env`** - Variáveis de ambiente (URL base da API)
- **`vite.config.ts`** - Configuração de build do Vite
- **`tailwind.config.js`** - Configuração do Tailwind CSS
- **`tsconfig.json`** - Configuração do TypeScript

#### Infrastructure Configuration
- **`docker-compose.yml`** - Orquestração multi-serviço
- **`monitoring/prometheus.yml`** - Coleta de métricas
- **`monitoring/alert_rules.yml`** - Regras de alertas

---

## 🔧 LAYER 4: EXTENSION POINTS

### Design Patterns Used

#### Backend Patterns
- **Service Layer Pattern** - Separação clara entre API e lógica de negócio
- **Repository Pattern** - Abstração de acesso a dados (GLPI service)
- **Middleware Pattern** - Concerns transversais (observabilidade, cache)
- **Factory Pattern** - Instanciação e configuração de serviços
- **Decorator Pattern** - Validação de datas e formatação

#### Frontend Patterns
- **Custom Hooks Pattern** - Lógica stateful reutilizável
- **Compound Components** - Composição de componentes UI complexos
- **Render Props** - Composição flexível de componentes
- **Provider Pattern** - Gerenciamento de estado global
- **Higher-Order Components** - Concerns transversais de UI

### Customization Areas

#### Backend Extensions
```python
# Novas fontes de dados
/backend/services/glpi_service.py

# Métricas customizadas
/backend/utils/prometheus_metrics.py

# Estratégias de cache
/backend/utils/smart_cache.py

# Regras de alerta
/backend/config/alerting_system.py

# Validação de dados
/backend/schemas/
```

#### Frontend Extensions
```typescript
// Sistema de temas
/src/design-system/tokens.ts
/src/design-system/component-patterns.ts

// Novos componentes
/src/components/

// Hooks customizados
/src/hooks/

// Tipos de gráficos
/src/components/charts/
```

### Plugin Architecture

#### Backend Plugins
- **Service Plugins** - Novas integrações de fontes de dados
- **Middleware Plugins** - Processamento customizado de request/response
- **Cache Plugins** - Estratégias alternativas de cache
- **Metric Plugins** - Monitoramento e alertas customizados

#### Frontend Plugins
- **Component Plugins** - Componentes UI reutilizáveis
- **Hook Plugins** - Padrões customizados de gerenciamento de estado
- **Service Plugins** - Clientes API alternativos
- **Theme Plugins** - Sistemas de design customizados

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

### Recent Improvements
- **Análise Crítica de Requisições GLPI** - Documentação completa de 28 tipos de consultas à API
- **Otimização de Performance** - Paginação robusta e batching de requisições
- **Qualidade de Código** - Setup abrangente de linting e testes
- **Observabilidade** - Coleta de logs estruturados e métricas
- **Cache Inteligente** - Aquecimento proativo e invalidação inteligente
- **Redução de Débito Técnico** - Limpeza sistemática e modernização
- **Limpeza de Código** - Remoção de arquivos obsoletos (mock.ts, test.ts, mock_glpi_service.py)
- **Consolidação de Tipos** - Simplificação da estrutura de tipos TypeScript
- **Documentação Atualizada** - Sincronização do handbook com mudanças recentes
- **Análise de Duplicação de Código** - Identificação e refatoração de código duplicado
- **Melhorias de UI/UX** - Componentes modernos e responsivos implementados

---

## 📋 VALIDATION CHECKLIST

- ✅ Todas as 4 seções obrigatórias presentes
- ✅ Padrão de arquitetura identificado (Microservices + SPA)
- ✅ 6+ módulos principais documentados
- ✅ Stack tecnológica corresponde à realidade do projeto
- ✅ Pontos de extensão e padrões identificados
- ✅ Endpoints da API documentados
- ✅ Pontos de integração mapeados
- ✅ Workflows de desenvolvimento incluídos
- ✅ Configurações e dependências externas documentadas
- ✅ Melhorias recentes e débito técnico abordados

---

*Este handbook fornece um guia abrangente para agentes de IA e desenvolvedores trabalhando com o projeto GLPI Dashboard. Cada camada se baseia na anterior, fornecendo informações cada vez mais detalhadas para navegação e extensão eficazes da base de código.*
