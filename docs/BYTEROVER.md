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
│   React SPA     │───▶│ Flask/FastAPI    │───▶│   GLPI System   │
│   (Port 3001)   │    │ Hybrid API       │    │   (External)    │
│                 │    │ (Port 5000)      │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │ Redis Cache +   │              │
         │              │ Prometheus      │              │
         │              │ (Port 6379)     │              │
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
- **API Design:** RESTful híbrido (Flask principal + FastAPI para métricas simples) com decorators para monitoring, caching e validação
- **Error Handling:** Structured logging com Prometheus metrics e correlação de requests
- **Authentication:** Token-based via GLPI API
- **Deployment:** Docker containers com docker-compose
- **Concurrency:** ThreadPoolExecutor para processamento paralelo
- **Resilience:** Circuit breaker pattern para falhas de API
- **Performance:** Sistema de monitoramento com métricas estruturadas

## Layer 2: Module Map

### Core Modules

#### Backend Services
- **`app.py`** - Flask application factory and main entry point
- **`glpi_service.py`** - GLPI API integration (⚠️ 7,039 lines - URGENT refactoring needed)
- **`cache_service.py`** - Multi-layer caching (Redis + Memory + App-level)
- **`routes.py`** - Main Flask API endpoints (11 endpoints)
- **`hybrid_routes.py`** - Hybrid pagination endpoints (3 endpoints)
- **`simple_metrics_api.py`** - FastAPI simple metrics service (2 endpoints)
- **`asgi.py`** - ASGI application wrapper for FastAPI integration

#### Utilities & Infrastructure
- **`utils/performance_monitor.py`** - Performance monitoring decorators
- **`utils/concurrent_processor.py`** - ThreadPoolExecutor utilities (max_workers: 10)
- **`utils/resilience.py`** - Circuit breaker pattern implementation
- **`utils/logging_config.py`** - Structured logging with correlation IDs
- **`utils/alert_manager.py`** - Alert system with observer pattern
- **`monitoring/prometheus_config.py`** - Metrics collection and monitoring
- **`monitoring/connectivity_monitor.py`** - GLPI connectivity monitoring

#### Frontend Components
- **`frontend/src/components/Dashboard/`** - Main dashboard components
- **`frontend/src/components/Metrics/`** - Metrics visualization widgets
- **`frontend/src/services/api.js`** - API client with retry logic
- **`frontend/src/hooks/useMetrics.js`** - Custom hooks for data fetching
- **`frontend/src/utils/performance.js`** - Frontend performance tracking

#### Configuration & Deployment
- **`docker-compose.yml`** - Complete containerization stack
- **`requirements.txt`** - Python dependencies
- **`frontend/package.json`** - Node.js dependencies
- **`.env.example`** - Environment configuration template

### Module Responsibilities

- **API Layer:** HTTP request handling, validation, response formatting (Flask + FastAPI)
- **Service Layer:** Business logic, data processing, GLPI integrations
- **Cache Layer:** Multi-level caching (Redis + Memory + App-level) with TTL management
- **Data Layer:** GLPI API communication, data transformation, batch processing
- **Utils Layer:** Cross-cutting concerns (logging, monitoring, resilience, concurrency)
- **Monitoring Layer:** Performance tracking, alerting, metrics collection
- **Infrastructure Layer:** Docker containerization, environment configuration

| Module | Responsibility | Key Files |
|--------|----------------|----------|
| API Layer | REST endpoints, validation, monitoring | `api/routes.py`, `api/hybrid_routes.py` |
| Service Layer | Business logic, GLPI integration | `services/glpi_service.py`, `services/api_service.py` |
| Cache Layer | Performance optimization | `services/smart_cache.py`, `cache_warming.py` |
| Config Layer | Settings, logging, performance | `config/settings.py`, `config/logging_config.py` |
| Utils Layer | Cross-cutting concerns | `utils/`, `schemas/` |

## Layer 3: Integration Guide

### API Architecture Overview

#### Dual API Strategy
- **Flask API:** Main application endpoints (11 endpoints)
- **FastAPI Integration:** High-performance metrics service (2 endpoints)
- **ASGI Wrapper:** Unified deployment via `asgi.py`

### API Endpoints
**Base URL:** `http://localhost:5000/api`

#### Core Flask Endpoints (routes.py):
```http
# Health & Status
GET  /health              # Health check com diagnósticos detalhados (cache: 30s)
GET  /status              # Status do sistema com monitoramento (cache: 60s)

# Métricas com Performance Monitoring
GET  /metrics             # Dashboard metrics com structured logging (cache: 300s)
GET  /metrics/filtered    # Métricas com filtros avançados e correlation IDs

# Técnicos com Concurrent Processing
GET  /technicians         # Lista com ThreadPoolExecutor (cache: 600s, Redis+Memory+App)
GET  /technicians/ranking # Performance ranking com circuit breaker (cache: 300s)

# Tickets com Batch Processing
GET  /tickets/new         # Tickets com processamento paralelo (cache: 120s)
GET  /tickets/<id>        # Detalhes com correlation ID tracking (cache: 180s)

# Sistema com Resilience Patterns
GET  /alerts              # Alertas com observer pattern (cache: 60s)
GET  /cache/stats         # Estatísticas multi-layer cache (cache: 30s)
POST /cache/invalidate    # Invalidação inteligente de cache
GET  /filter-types        # Tipos de filtros com connectivity monitoring (cache: 3600s)
```

#### Hybrid Pagination Endpoints (hybrid_routes.py):
```http
GET  /hybrid-pagination/stats              # Estatísticas com cursor-based pagination (cache: 180s)
GET  /hybrid-pagination/technician-info    # Info detalhada com batch loading (cache: 300s)
POST /hybrid-pagination/cleanup           # Limpeza otimizada de cache híbrido
```

#### FastAPI Simple Metrics (simple_metrics_api.py):
```http
GET  /simple/health                        # Health check de alta performance
GET  /simple/metrics/operational           # Métricas operacionais com minimal overhead
```

#### Authentication & Headers

##### Required Headers
```python
# Headers necessários
headers = {
    'App-Token': 'your_app_token',
    'Session-Token': 'session_token',
    'Content-Type': 'application/json',
    'X-Correlation-ID': 'uuid4-correlation-id',  # For request tracking
    'X-Request-Source': 'dashboard|api|monitoring'  # Request source identification
}
```

##### Performance Headers
```python
# Headers opcionais para performance
performance_headers = {
    'X-Cache-Control': 'max-age=300',  # Override default cache TTL
    'X-Enable-Metrics': 'true',        # Enable performance tracking
    'X-Circuit-Breaker': 'enabled'     # Circuit breaker protection
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

# Performance & Monitoring
API_TIMEOUT: 30
MAX_WORKERS: 5
PROMETHEUS_ENABLED: true
PERFORMANCE_MONITORING: true
STRUCTURED_LOGGING: true
CORRELATION_ID_ENABLED: true

# Threading Configuration
THREAD_POOL_MAX_WORKERS: 10
CIRCUIT_BREAKER_ENABLED: true

# API Configuration
FLASK_API_PORT: 5000
FASTAPI_ENABLED: true
HYBRID_PAGINATION_ENABLED: true
```

### Integration Points

#### External Dependencies
- **GLPI REST API** - Sistema principal de dados com circuit breaker protection
- **Redis** - Multi-layer caching (L1: Memory, L2: Redis, L3: App-level)
- **MySQL** - Persistência de dados
- **Prometheus** - Comprehensive metrics collection and alerting
- **Docker** - Containerized deployment with health checks

#### Internal Interfaces
- **Frontend ↔ Backend** - REST API via Axios
- **Backend ↔ GLPI** - REST API com autenticação
- **Backend ↔ Redis** - Cache layer
- **Backend ↔ MySQL** - Data persistence
- **Cache Service** - Intelligent caching with TTL management and warming
- **Performance Monitor** - Request timing, correlation tracking, and bottleneck detection
- **Logger** - Structured logging with correlation IDs and alert integration
- **Thread Pool** - Concurrent processing with configurable worker limits
- **Circuit Breaker** - Resilience patterns for external API calls
- **Alert Manager** - Observer pattern for system notifications

## Layer 4: Extension Points

### Design Patterns

#### 1. Decorator Pattern
```python
# Performance monitoring decorator
@monitor_performance
@cache_result(ttl=300)
@structured_logging
def get_technician_metrics():
    return glpi_service.fetch_metrics()

# Circuit breaker decorator
@circuit_breaker(failure_threshold=5, timeout=60)
def external_api_call():
    return glpi_service.make_request()
```

#### 2. Factory Pattern
```python
# GLPIService factory
class GLPIServiceFactory:
    @staticmethod
    def create_service(config):
        return GLPIService(config)

# Logger factory for structured logging
class StructuredLoggerFactory:
    @staticmethod
    def create_logger(name, correlation_id=None):
        return StructuredLogger(name, correlation_id)
```

#### 3. Service Layer Pattern
```python
# Service abstraction
class MetricsService:
    def __init__(self, glpi_service, cache_service, performance_monitor):
        self.glpi = glpi_service
        self.cache = cache_service
        self.monitor = performance_monitor
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
```

#### 4. Observer Pattern
```python
# Alert system with observers
class AlertManager:
    def __init__(self):
        self.observers = []
        self.connectivity_monitor = ConnectivityMonitor()
    
    def notify_observers(self, alert):
        for observer in self.observers:
            observer.handle_alert(alert)
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
# Add custom metric collectors
class CustomMetricCollector:
    def __init__(self, performance_monitor):
        self.monitor = performance_monitor
    
    @monitor_performance
    def collect_custom_data(self):
        # Your custom logic here with monitoring
        pass

# Register in app.py
app.register_metric_collector(CustomMetricCollector(performance_monitor))
```

#### 3. Data Processing
**Location:** `services/glpi_service.py`
**Extension Point:** Custom data processors
```python
# Custom data processing with threading
class CustomDataProcessor:
    def __init__(self, thread_pool):
        self.thread_pool = thread_pool
    
    @circuit_breaker(failure_threshold=3)
    def process_technician_data(self, raw_data: List[Dict]) -> List[Dict]:
        # Custom processing logic with resilience
        return processed_data
    
    def process_batch_data(self, data_list):
        # Concurrent processing
        futures = [self.thread_pool.submit(self.process_item, item) 
                  for item in data_list]
        return [f.result() for f in futures]
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

// Custom dashboard widgets with performance tracking
class CustomWidget extends DashboardWidget {
    constructor() {
        super();
        this.performanceObserver = new PerformanceObserver();
    }
    
    render() {
        const startTime = performance.now();
        // Custom widget implementation
        this.trackRenderTime(performance.now() - startTime);
    }
}
```

#### 5. Alert Handlers
**Location:** `services/alert_manager.py`
**Extension Point:** Custom alert handlers
```python
# Custom alert handlers
class CustomAlertHandler:
    def handle_connectivity_alert(self, alert):
        # Custom alert processing
        pass
    
    def handle_performance_alert(self, alert):
        # Performance degradation handling
        pass
```

### Performance Optimization Points

#### 1. Concurrent Processing
**Location:** `services/glpi_service.py`
**Implementation:** ThreadPoolExecutor for parallel API calls
```python
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(fetch_data, endpoint) for endpoint in endpoints]
    results = [future.result() for future in futures]
```

#### 2. Multi-Layer Caching Strategy
**Location:** `services/cache_service.py`
**Strategy:** Redis + In-memory + Application-level caching
```python
class MultiLayerCache:
    def __init__(self):
        self.redis_cache = RedisCache()
        self.memory_cache = MemoryCache()
        self.app_cache = ApplicationCache()
    
    def get(self, key):
        # Try memory first, then Redis, then source
        return self.memory_cache.get(key) or \
               self.redis_cache.get(key) or \
               self.fetch_from_source(key)
```

#### 3. Circuit Breaker Pattern
**Location:** `utils/resilience.py`
**Implementation:** Prevent cascade failures
```python
@circuit_breaker(failure_threshold=5, timeout=60)
def external_api_call():
    # Protected external calls
    return make_request()
```

#### 4. Database Batch Processing
**Location:** `services/data_processor.py`
**Optimization:** Bulk operations with connection pooling
```python
def batch_update_metrics(metrics_list):
    # Batch database operations with connection reuse
    with db.get_connection() as conn:
        conn.bulk_insert(metrics_list)
```

#### 5. Structured Logging with Correlation IDs
**Location:** `utils/logging_config.py`
**Implementation:** Request tracing and performance monitoring
```python
class StructuredLogger:
    def __init__(self, correlation_id):
        self.correlation_id = correlation_id
    
    def log_performance(self, operation, duration):
        logger.info({
            'correlation_id': self.correlation_id,
            'operation': operation,
            'duration_ms': duration,
            'timestamp': datetime.utcnow()
        })
```

### Recent Changes & Issues

#### Critical Issues Identified in Audit

##### 1. Monolithic Service File
- **Issue:** `glpi_service.py` has 7,039 lines - severely violates SRP
- **Impact:** Maintenance nightmare, testing difficulties, performance bottlenecks
- **Recommended Action:** Urgent refactoring into specialized services
- **Priority:** HIGH

##### 2. API Redundancy
- **Issue:** 16 endpoints with 2 redundant APIs identified
- **Impact:** Increased maintenance overhead, potential inconsistencies
- **Solution:** Consolidate to proposed 5-endpoint simplified API
- **Files Affected:** `routes.py`, `hybrid_routes.py`, `simple_metrics_api.py`

##### 3. Duplicated Utilities
- **Issue:** Multiple utility functions scattered across modules
- **Impact:** Code duplication, inconsistent behavior
- **Solution:** Centralize in `utils/` directory with proper organization

#### Performance Improvements Implemented

##### Multi-Layer Caching Strategy
- **Layer 1:** Redis for shared data across instances (TTL: 300-3600s)
- **Layer 2:** In-memory cache for frequently accessed data
- **Layer 3:** Application-level caching for computed results
- **Monitoring:** Cache hit/miss ratios tracked via `/cache/stats`

##### Concurrent Processing Enhancement
- **Implementation:** ThreadPoolExecutor with configurable workers (default: 10)
- **Benefits:** 3x improvement in API response times for bulk operations
- **Location:** `services/glpi_service.py`, `utils/concurrent_processor.py`

##### Circuit Breaker Pattern
- **Purpose:** Prevent cascade failures from GLPI API issues
- **Configuration:** 5 failure threshold, 60s timeout
- **Monitoring:** Failure rates tracked and alerted

#### Structured Logging & Monitoring
- **Implementation:** Correlation IDs for request tracing
- **Benefits:** Better debugging, performance monitoring, audit trails
- **Integration:** Prometheus metrics, structured JSON logs
- **Location:** `utils/logging_config.py`, `monitoring/prometheus_config.py`

#### Docker & Infrastructure
- **Added:** Complete Docker Compose stack
- **Services:** Flask app, FastAPI, Redis, Prometheus, Grafana
- **Benefits:** Consistent development environment, easy deployment
- **Monitoring:** Health checks, resource usage tracking

---

*This handbook serves as a navigation guide for AI agents and human developers working on the GLPI Dashboard project. It provides essential context for understanding the system architecture, identifying key components, and extending functionality.*