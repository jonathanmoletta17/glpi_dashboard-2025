# BYTEROVER - GLPI Dashboard Project Handbook

*Generated: 2025-01-15*
*Project: GLPI Dashboard - Performance Monitoring & Analytics*

## Layer 1: System Overview

### Purpose
GLPI Dashboard é um sistema de monitoramento e análise de performance para o sistema GLPI (Gestionnaire Libre de Parc Informatique). O projeto fornece dashboards interativos para visualização de métricas de técnicos, tickets, e performance operacional, com foco em otimização de processos de suporte técnico.

### Tech Stack
**Frontend:**
- React 18.2.0 + TypeScript
- Vite (build tool)
- TailwindCSS + Radix UI components
- Chart.js + Recharts (visualizações)
- TanStack Query (state management)
- Framer Motion (animações)
- Axios (HTTP client)

**Backend:**
- Python Flask (API REST)
- GLPI REST API integration
- Redis (caching layer)
- MySQL (database)
- Prometheus (monitoring)
- Docker + Docker Compose

### Architecture
**Pattern:** Microservices com Frontend/Backend separados

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React SPA     │───▶│   Flask API      │───▶│   GLPI System   │
│   (Port 3001)   │    │   (Port 5000)    │    │   (External)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │  Redis Cache    │              │
         │              │  (Port 6379)    │              │
         │              └─────────────────┘              │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                        ┌─────────────────┐
                        │ MySQL Database  │
                        │ (Port 3306)     │
                        └─────────────────┘
```

### Key Technical Decisions
- **Caching Strategy:** Multi-layer caching (Redis + in-memory) para otimizar performance
- **API Design:** RESTful com decorators para monitoring, caching e validação
- **Error Handling:** Structured logging com Prometheus metrics
- **Authentication:** Token-based via GLPI API
- **Deployment:** Docker containers com docker-compose

## Layer 2: Module Map

### Core Modules

#### Backend Core (`backend/`)
- **`app.py`** - Flask application factory e configuração principal
- **`api/routes.py`** - Endpoints REST com decorators de performance
- **`services/glpi_service.py`** - Integração com GLPI API (7019 linhas)
- **`services/cache_warming.py`** - Pre-aquecimento de cache
- **`config/settings.py`** - Configurações centralizadas

#### Frontend Core (`frontend/src/`)
- **`components/`** - Componentes React reutilizáveis
- **`services/httpClient.ts`** - Cliente HTTP configurado
- **`config/environment.ts`** - Configuração de ambiente
- **`pages/`** - Páginas principais do dashboard

#### Data Layer
- **`services/glpi_service.py`** - Camada de acesso aos dados GLPI
- **`services/smart_cache.py`** - Sistema de cache inteligente
- **`database/`** - Inicialização e migrações

#### Utilities
- **`utils/structured_logger.py`** - Sistema de logging estruturado
- **`utils/performance.py`** - Métricas de performance
- **`utils/prometheus_metrics.py`** - Integração com Prometheus
- **`utils/date_validator.py`** - Validação de datas

### Module Responsibilities

| Module | Responsibility | Key Files |
|--------|----------------|----------|
| API Layer | REST endpoints, validation, monitoring | `api/routes.py`, `api/hybrid_routes.py` |
| Service Layer | Business logic, GLPI integration | `services/glpi_service.py`, `services/api_service.py` |
| Cache Layer | Performance optimization | `services/smart_cache.py`, `cache_warming.py` |
| Config Layer | Settings, logging, performance | `config/settings.py`, `config/logging_config.py` |
| Utils Layer | Cross-cutting concerns | `utils/`, `schemas/` |

## Layer 3: Integration Guide

### API Endpoints

#### Core Endpoints
```
GET /api/technicians/ranking?limit=50    # Ranking de técnicos
GET /api/metrics                         # Métricas gerais
GET /api/tickets/stats                   # Estatísticas de tickets
GET /api/performance/dashboard           # Dashboard de performance
```

#### Authentication
```python
# Headers necessários
headers = {
    'App-Token': 'your_app_token',
    'Session-Token': 'session_token',
    'Content-Type': 'application/json'
}
```

### Configuration Files

#### Environment Configuration
- **`docker.env`** - Configurações Docker (produção)
- **`frontend/.env`** - Configurações frontend (desenvolvimento)
- **`.env.example`** - Template de configurações

#### Key Configuration Sections
```yaml
# GLPI Integration
GLPI_URL: "https://glpi.example.com/apirest.php"
GLPI_APP_TOKEN: "your_app_token"
GLPI_USER_TOKEN: "your_user_token"

# Cache Configuration
REDIS_URL: "redis://localhost:6379/0"
CACHE_DEFAULT_TIMEOUT: 300

# Performance
API_TIMEOUT: 30
MAX_WORKERS: 5
```

### Integration Points

#### External Dependencies
- **GLPI REST API** - Sistema principal de dados
- **Redis** - Cache distribuído
- **MySQL** - Persistência de dados
- **Prometheus** - Métricas e monitoring

#### Internal Interfaces
- **Frontend ↔ Backend** - REST API via Axios
- **Backend ↔ GLPI** - REST API com autenticação
- **Backend ↔ Redis** - Cache layer
- **Backend ↔ MySQL** - Data persistence

## Layer 4: Extension Points

### Design Patterns

#### Decorator Pattern
```python
# Performance monitoring decorator
@monitor_performance
@cache_response(timeout=300)
@validate_date_range
def get_technician_ranking():
    # Implementation
```

#### Factory Pattern
```python
# Flask app factory
def create_app(config_name='default'):
    app = Flask(__name__)
    # Configuration and setup
    return app
```

#### Service Layer Pattern
```python
# Service abstraction
class GLPIService:
    def get_technician_ranking(self) -> List[Dict]
    def get_ticket_metrics(self) -> Dict
    def get_performance_data(self) -> Dict
```

### Customization Areas

#### 1. Cache Strategy
**Location:** `services/smart_cache.py`
**Extension Point:** Custom cache backends
```python
class CustomCacheBackend(CacheBackend):
    def get(self, key: str) -> Any
    def set(self, key: str, value: Any, ttl: int) -> None
```

#### 2. Metrics Collection
**Location:** `utils/prometheus_metrics.py`
**Extension Point:** Custom metrics
```python
# Add custom metrics
custom_metric = Counter('custom_operations_total', 'Custom operations')
```

#### 3. Data Processing
**Location:** `services/glpi_service.py`
**Extension Point:** Custom data processors
```python
def process_technician_data(raw_data: List[Dict]) -> List[Dict]:
    # Custom processing logic
    return processed_data
```

#### 4. Frontend Components
**Location:** `frontend/src/components/`
**Extension Point:** Custom dashboard widgets
```typescript
interface DashboardWidget {
  id: string;
  title: string;
  component: React.ComponentType;
  config: WidgetConfig;
}
```

### Performance Optimization Points

#### 1. Concurrent Processing
```python
# ThreadPoolExecutor for parallel API calls
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(process_technician, tech_id) for tech_id in tech_ids]
```

#### 2. Cache Warming
```python
# Pre-populate cache with frequently accessed data
def warm_cache():
    endpoints = ['/api/technicians/ranking', '/api/metrics']
    for endpoint in endpoints:
        # Warm cache logic
```

#### 3. Database Optimization
```python
# Batch processing for large datasets
def process_in_batches(data: List, batch_size: int = 100):
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]
```

### Recent Changes & Evolution
- **Performance Issues:** Endpoint `/api/technicians/ranking` com timeouts frequentes
- **Cache Strategy:** Implementação de multi-layer caching
- **Error Handling:** Structured logging com Prometheus integration
- **Concurrent Processing:** ThreadPoolExecutor para otimização
- **Docker Integration:** Containerização completa do ambiente

---

*This handbook serves as a navigation guide for AI agents and human developers working on the GLPI Dashboard project. It provides essential context for understanding the system architecture, identifying key components, and extending functionality.*
