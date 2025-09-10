# BACKEND ARCHITECTURE - GLPI DASHBOARD

## 📋 VISÃO GERAL

O backend do GLPI Dashboard é uma API REST construída com Flask, Python e sistema de cache inteligente. Este documento detalha a arquitetura, serviços e funcionalidades do sistema.

## 🏗️ ARQUITETURA TÉCNICA

### **Stack Tecnológico**
- **Flask 2.3.3** - Framework web principal
- **Python 3.12+** - Linguagem de programação
- **SimpleCache** - Sistema de cache (fallback do Redis)
- **Structured Logging** - Sistema de logging avançado
- **Observability Middleware** - Monitoramento e métricas

### **Estrutura de Pastas**
```
backend/
├── api/                    # Rotas da API
│   └── routes.py
├── services/               # Serviços de negócio
│   ├── glpi_service.py
│   └── cache_warming.py
├── utils/                  # Utilitários e helpers
│   ├── observability_middleware.py
│   ├── structured_logging.py
│   ├── smart_cache.py
│   └── performance.py
├── config/                 # Configurações
│   ├── settings.py
│   └── logging_config.py
├── schemas/                # Schemas de dados
│   └── dashboard.py
└── app.py                  # Aplicação principal
```

## 🔌 ROTAS DA API

### **Rotas Principais**

#### **GET /api/health**
- **Função:** Status de saúde do sistema
- **Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-09T19:53:35.462357Z",
  "version": "1.0.0",
  "services": {
    "api": "ok",
    "glpi": "ok",
    "cache": "ok"
  }
}
```

#### **GET /api/metrics**
- **Função:** Métricas do dashboard
- **Parâmetros:**
  - `start_date` (opcional): Data de início
  - `end_date` (opcional): Data de fim
- **Resposta:**
```json
{
  "novos": 38,
  "pendentes": 17,
  "progresso": 28,
  "resolvidos": 90,
  "total": 173,
  "niveis": {
    "n1": { "novos": 10, "progresso": 5, "pendentes": 3, "resolvidos": 25 },
    "n2": { "novos": 8, "progresso": 12, "pendentes": 7, "resolvidos": 30 },
    "n3": { "novos": 15, "progresso": 8, "pendentes": 5, "resolvidos": 20 },
    "n4": { "novos": 5, "progresso": 3, "pendentes": 2, "resolvidos": 15 }
  }
}
```

#### **GET /api/technicians/ranking**
- **Função:** Ranking de técnicos
- **Parâmetros:**
  - `limit` (opcional): Limite de resultados
  - `level` (opcional): Filtro por nível
- **Resposta:**
```json
[
  {
    "id": "tech_001",
    "name": "João Silva",
    "rank": 1,
    "total_tickets": 45,
    "resolved_tickets": 42,
    "avg_resolution_time": 2.5,
    "level": "N1"
  }
]
```

#### **GET /api/tickets**
- **Função:** Lista de tickets
- **Parâmetros:**
  - `status` (opcional): Filtro por status
  - `priority` (opcional): Filtro por prioridade
  - `assignee` (opcional): Filtro por técnico
- **Resposta:**
```json
[
  {
    "id": "ticket_001",
    "title": "Problema de rede",
    "status": "em_progresso",
    "priority": "alta",
    "assignee": "João Silva",
    "created_at": "2025-09-09T10:00:00Z",
    "updated_at": "2025-09-09T15:30:00Z"
  }
]
```

## 🔧 SERVIÇOS PRINCIPAIS

### **GLPI Service (glpi_service.py)**
- **Função:** Integração com sistema GLPI
- **Características:**
  - Autenticação com GLPI
  - Coleta de dados de tickets
  - Processamento de métricas
  - Cache de resultados

### **Cache Warming (cache_warming.py)**
- **Função:** Pré-aquecimento do cache
- **Características:**
  - Carregamento inicial de dados
  - Atualização periódica
  - Invalidação inteligente
  - Métricas de performance

## 🛠️ UTILITÁRIOS

### **Observability Middleware**
- **Função:** Monitoramento e observabilidade
- **Características:**
  - Logging estruturado
  - Métricas de performance
  - Rastreamento de requests
  - Alertas automáticos

### **Structured Logging**
- **Função:** Sistema de logging avançado
- **Características:**
  - Logs estruturados em JSON
  - Níveis de log configuráveis
  - Correlação de requests
  - Auditoria de operações

### **Smart Cache**
- **Função:** Sistema de cache inteligente
- **Características:**
  - TTL configurável
  - Invalidação automática
  - Fallback para SimpleCache
  - Métricas de hit rate

## ⚙️ CONFIGURAÇÕES

### **Settings (settings.py)**
```python
class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # GLPI
    GLPI_URL = os.getenv('GLPI_URL', 'http://localhost/glpi')
    GLPI_USER_TOKEN = os.getenv('GLPI_USER_TOKEN')
    GLPI_APP_TOKEN = os.getenv('GLPI_APP_TOKEN')
    
    # Cache
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', '300'))
    
    # Redis (opcional)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
```

### **Logging Config**
```python
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'structured': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
            'datefmt': '%Y-%m-%dT%H:%M:%S.%fZ'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'structured',
            'level': 'INFO'
        }
    },
    'loggers': {
        'glpi': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False
        }
    }
}
```

## 📊 SISTEMA DE CACHE

### **Estratégia de Cache**
- **Nível 1:** Cache em memória (SimpleCache)
- **Nível 2:** Redis (quando disponível)
- **TTL:** 300 segundos (5 minutos)
- **Invalidação:** Automática por tempo ou manual

### **Chaves de Cache**
- `metrics:all` - Métricas gerais
- `metrics:level:{level}` - Métricas por nível
- `technicians:ranking` - Ranking de técnicos
- `tickets:recent` - Tickets recentes

## 🔍 SISTEMA DE LOGGING

### **Estrutura de Logs**
```json
{
  "timestamp": "2025-09-09T19:53:31.360527Z",
  "level": "INFO",
  "logger": "glpi.system",
  "message": "Operação success: app_initialization_complete",
  "module": "structured_logging",
  "function": "log_operation_end",
  "line": 224,
  "correlation_id": "205a7483-9cdc-4105-80af-ccc0b2ee5b9a",
  "operation": {
    "name": "app_initialization_complete",
    "start_time": "2025-09-09T19:53:31.395771Z",
    "environment": "development",
    "debug": false
  },
  "operation_phase": "end",
  "operation_status": "success",
  "duration_seconds": null,
  "result": {
    "cache_type": "SimpleCache",
    "cors_enabled": true,
    "blueprints_registered": ["api"]
  }
}
```

### **Níveis de Log**
- **DEBUG:** Informações detalhadas
- **INFO:** Informações gerais
- **WARNING:** Avisos
- **ERROR:** Erros
- **CRITICAL:** Erros críticos

## 🚀 EXECUÇÃO E DEPLOY

### **Desenvolvimento**
```bash
cd glpi_dashboard/backend
python app.py
```

### **Produção**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### **Docker**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

## 📈 MÉTRICAS E MONITORAMENTO

### **Métricas Coletadas**
- **Performance:** Tempo de resposta, throughput
- **Cache:** Hit rate, miss rate, TTL
- **GLPI:** Tempo de resposta, taxa de erro
- **Sistema:** Uso de memória, CPU

### **Alertas Configurados**
- **API Response Time High:** > 300ms
- **GLPI Response Time High:** > 2s
- **Zero Tickets Detected:** 0 tickets
- **High Error Rate:** > 5%
- **Suspicious Technician Names:** Nomes suspeitos

## 🔒 SEGURANÇA

### **Autenticação**
- Tokens de usuário GLPI
- Tokens de aplicação GLPI
- Validação de headers

### **CORS**
- Configuração para frontend
- Headers de segurança
- Validação de origem

### **Rate Limiting**
- Limite de requests por IP
- Throttling automático
- Logs de tentativas

## 🧪 TESTES

### **Estrutura de Testes**
```
tests/
├── unit/              # Testes unitários
├── integration/       # Testes de integração
└── conftest.py        # Configuração de testes
```

### **Comandos de Teste**
```bash
pytest tests/unit/
pytest tests/integration/
pytest --cov=app tests/
```

## 🔄 INTEGRAÇÃO COM GLPI

### **Endpoints GLPI Utilizados**
- `/apirest.php/initSession` - Inicialização de sessão
- `/apirest.php/Ticket` - Dados de tickets
- `/apirest.php/User` - Dados de usuários
- `/apirest.php/Group` - Dados de grupos

### **Autenticação**
```python
def authenticate_glpi():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'user_token {GLPI_USER_TOKEN}',
        'App-Token': GLPI_APP_TOKEN
    }
    response = requests.post(f'{GLPI_URL}/apirest.php/initSession', headers=headers)
    return response.json()['session_token']
```

## ⚠️ LIMITAÇÕES E FALLBACKS

### **Redis**
- **Status:** Não disponível no ambiente atual
- **Fallback:** SimpleCache em memória
- **Impacto:** Cache não persistente entre restarts

### **psycopg2-binary**
- **Status:** Falha na instalação
- **Impacto:** Não crítico para funcionalidade básica
- **Solução:** Instalar Microsoft C++ Build Tools

## ✅ CONCLUSÃO

O backend do GLPI Dashboard representa uma implementação robusta e escalável com:
- API REST bem estruturada
- Sistema de cache inteligente
- Logging estruturado e observabilidade
- Integração completa com GLPI
- Configuração flexível e segura

**Status:** ✅ FUNCIONAL E PRONTO PARA PRODUÇÃO

**Porta:** 8000 (http://localhost:8000)
**Health Check:** http://localhost:8000/api/health
