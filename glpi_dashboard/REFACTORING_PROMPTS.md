# 🚀 Prompts de Refatoração - Dashboard GLPI

## 📋 Tarefas de Refatoração Organizadas

### 1. 🔧 **Refatorar backend/app.py - Consolidar Aplicação Principal**

#### **Prompt:**
```
Analise e refatore o arquivo backend/app.py para consolidar a aplicação principal Flask. 

CONTEXTO ATUAL:
- O arquivo app.py é a aplicação principal Flask do dashboard GLPI
- Deve integrar com backend/api/routes.py para as rotas da API
- Precisa usar backend/config/settings.py para configurações
- Deve inicializar backend/utils/ para utilitários essenciais
- Precisa conectar com backend/services/glpi_service.py para dados GLPI

OBJETIVOS:
1. Consolidar inicialização da aplicação Flask
2. Configurar middleware essencial (CORS, logging, observabilidade)
3. Registrar blueprints da API
4. Configurar tratamento de erros global
5. Inicializar serviços essenciais (GLPI, cache, alertas)
6. Configurar métricas Prometheus
7. Manter apenas funcionalidades essenciais

ARQUIVOS RELACIONADOS:
- backend/api/routes.py (rotas da API)
- backend/config/settings.py (configurações)
- backend/services/glpi_service.py (serviço GLPI)
- backend/utils/ (utilitários)
- config/system.yaml (configuração principal)

REQUISITOS:
- Manter compatibilidade com frontend React
- Preservar endpoints essenciais: /api/health, /api/metrics, /api/technicians/ranking
- Configurar logging estruturado
- Implementar observabilidade básica
- Manter tratamento de erros robusto
- Configurar cache Redis se disponível
- Inicializar sistema de alertas

REMOVER:
- Código duplicado
- Configurações desnecessárias
- Middleware não utilizado
- Inicializações complexas desnecessárias
```

---

### 2. 🛣️ **Limpar backend/api/routes.py - Manter Apenas Rotas Essenciais**

#### **Prompt:**
```
Analise e limpe o arquivo backend/api/routes.py mantendo apenas as rotas essenciais para o dashboard GLPI.

CONTEXTO ATUAL:
- O arquivo routes.py contém todas as rotas da API REST
- Integra com backend/services/glpi_service.py para dados
- Usa backend/utils/ para decoradores e utilitários
- Deve manter compatibilidade com frontend React
- Precisa preservar funcionalidades core do dashboard

ROTAS ESSENCIAIS A MANTER:
1. GET /api/health - Health check da aplicação
2. GET /api/health/glpi - Health check da conexão GLPI
3. GET /api/metrics - Métricas gerais do dashboard
4. GET /api/metrics/filtered - Métricas com filtros
5. GET /api/technicians - Lista de técnicos
6. GET /api/technicians/ranking - Ranking de técnicos por nível
7. GET /api/tickets/new - Tickets novos
8. GET /api/alerts - Alertas do sistema
9. GET /api/status - Status geral do sistema

DECORADORES ESSENCIAIS:
- @monitor_api_endpoint - Monitoramento de endpoints
- @monitor_performance - Monitoramento de performance
- @cache_with_filters - Cache com filtros
- @standard_date_validation - Validação de datas

INTEGRAÇÕES NECESSÁRIAS:
- backend/services/glpi_service.py (dados GLPI)
- backend/utils/response_formatter.py (formatação de resposta)
- backend/utils/date_validator.py (validação de datas)
- backend/utils/performance.py (métricas de performance)
- backend/utils/alerting_system.py (sistema de alertas)

REMOVER:
- Rotas de debug e teste
- Endpoints não utilizados pelo frontend
- Código duplicado
- Validações desnecessárias
- Logs excessivos
- Tratamento de erros redundante

MANTER:
- Tratamento de erros essencial
- Validação de parâmetros
- Formatação de resposta padronizada
- Logging estruturado
- Cache inteligente
- Monitoramento de performance
```

---

### 3. 📚 **Atualizar docs/api/openapi.yaml - Documentar API Atual**

#### **Prompt:**
```
Atualize o arquivo docs/api/openapi.yaml para documentar a API atual do dashboard GLPI após a refatoração.

CONTEXTO ATUAL:
- O arquivo openapi.yaml deve refletir as rotas essenciais do backend/api/routes.py
- Deve documentar todos os endpoints mantidos após limpeza
- Precisa incluir schemas de dados do backend/schemas/dashboard.py
- Deve ser compatível com frontend React
- Serve como documentação oficial da API

ENDPOINTS A DOCUMENTAR:
1. GET /api/health
   - Descrição: Health check da aplicação
   - Resposta: Status da aplicação e dependências

2. GET /api/health/glpi
   - Descrição: Health check da conexão GLPI
   - Resposta: Status da conexão GLPI

3. GET /api/metrics
   - Descrição: Métricas gerais do dashboard
   - Parâmetros: start_date, end_date (opcionais)
   - Resposta: Métricas consolidadas

4. GET /api/metrics/filtered
   - Descrição: Métricas com filtros aplicados
   - Parâmetros: start_date, end_date, status, priority, level, technician, category
   - Resposta: Métricas filtradas

5. GET /api/technicians
   - Descrição: Lista de técnicos ativos
   - Resposta: Lista de técnicos com informações básicas

6. GET /api/technicians/ranking
   - Descrição: Ranking de técnicos por nível de atendimento
   - Parâmetros: start_date, end_date, level (opcionais)
   - Resposta: Ranking ordenado por performance

7. GET /api/tickets/new
   - Descrição: Tickets novos recentes
   - Parâmetros: limit (opcional, padrão 10)
   - Resposta: Lista de tickets novos

8. GET /api/alerts
   - Descrição: Alertas ativos do sistema
   - Resposta: Lista de alertas

9. GET /api/status
   - Descrição: Status geral do sistema
   - Resposta: Status de todos os componentes

SCHEMAS NECESSÁRIOS:
- DashboardMetrics (métricas do dashboard)
- TechnicianRanking (ranking de técnicos)
- NewTicket (ticket novo)
- Alert (alerta do sistema)
- ApiResponse (resposta padrão)
- ApiError (erro da API)

CONFIGURAÇÕES:
- Servidor: http://localhost:5000
- Versão da API: 1.0.0
- Título: GLPI Dashboard API
- Descrição: API REST para dashboard de métricas GLPI

INCLUIR:
- Exemplos de requisições
- Exemplos de respostas
- Códigos de erro possíveis
- Validações de parâmetros
- Tipos de dados corretos
```

---

### 4. ⚙️ **Organizar Configurações - Consolidar em config/system.yaml**

#### **Prompt:**
```
Analise e consolide todas as configurações do sistema no arquivo config/system.yaml, removendo duplicações e organizando de forma lógica.

CONTEXTO ATUAL:
- Existem configurações espalhadas em múltiplos arquivos
- backend/config/settings.py tem configurações da aplicação
- config/system.yaml deve ser a fonte única de verdade
- Precisa integrar com backend/app.py
- Deve suportar diferentes ambientes (dev, prod, test)

CONFIGURAÇÕES A CONSOLIDAR:

1. **Flask Application**
   - SECRET_KEY
   - DEBUG
   - HOST
   - PORT
   - CORS_ORIGINS

2. **GLPI API**
   - GLPI_URL
   - GLPI_USER_TOKEN
   - GLPI_APP_TOKEN
   - API_TIMEOUT
   - MAX_RETRIES

3. **Cache**
   - CACHE_TYPE
   - REDIS_URL
   - CACHE_DEFAULT_TIMEOUT
   - CACHE_KEY_PREFIX

4. **Logging**
   - LOG_LEVEL
   - LOG_FORMAT
   - LOG_FILE_PATH
   - STRUCTURED_LOGGING

5. **Observabilidade**
   - PROMETHEUS_GATEWAY_URL
   - PROMETHEUS_JOB_NAME
   - ENABLE_METRICS

6. **Alertas**
   - ALERT_RESPONSE_TIME_THRESHOLD
   - ALERT_ERROR_RATE_THRESHOLD
   - ALERT_ZERO_TICKETS_THRESHOLD

7. **Performance**
   - PERFORMANCE_TARGET_P95
   - MAX_CONTENT_LENGTH
   - RATE_LIMIT_PER_MINUTE

ESTRUTURA PROPOSTA:
```yaml
# Configuração principal do sistema
app:
  name: "GLPI Dashboard"
  version: "1.0.0"
  environment: "development"  # development, production, testing

# Configurações Flask
flask:
  secret_key: "${SECRET_KEY}"
  debug: true
  host: "0.0.0.0"
  port: 5000
  cors_origins: ["*"]

# Configurações GLPI
glpi:
  base_url: "${GLPI_URL}"
  user_token: "${GLPI_USER_TOKEN}"
  app_token: "${GLPI_APP_TOKEN}"
  timeout: 30
  max_retries: 3

# Configurações de Cache
cache:
  type: "RedisCache"
  redis_url: "${REDIS_URL}"
  default_timeout: 300
  key_prefix: "glpi_dashboard:"

# Configurações de Logging
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_path: "logs/app.log"
  structured: true

# Configurações de Observabilidade
observability:
  prometheus:
    gateway_url: "${PROMETHEUS_GATEWAY_URL}"
    job_name: "glpi_dashboard"
  metrics:
    enabled: true

# Configurações de Alertas
alerts:
  response_time_threshold: 300
  error_rate_threshold: 0.05
  zero_tickets_threshold: 60

# Configurações de Performance
performance:
  target_p95: 1000
  max_content_length: 16777216
  rate_limit_per_minute: 100
```

ARQUIVOS A ATUALIZAR:
- backend/config/settings.py (usar config/system.yaml)
- backend/app.py (carregar configurações do YAML)
- docker-compose.yml (variáveis de ambiente)
- .env (variáveis de ambiente)

REMOVER:
- Configurações duplicadas
- Valores hardcoded
- Configurações não utilizadas
- Arquivos de configuração obsoletos

MANTER:
- Validação de configurações
- Valores padrão sensatos
- Suporte a variáveis de ambiente
- Configurações por ambiente
```

---

## 🎯 **Instruções de Execução**

### **Ordem Recomendada:**
1. **Primeiro:** Organizar configurações (config/system.yaml)
2. **Segundo:** Refatorar backend/app.py
3. **Terceiro:** Limpar backend/api/routes.py
4. **Quarto:** Atualizar docs/api/openapi.yaml

### **Validação:**
Após cada refatoração, validar que:
- ✅ Aplicação inicia sem erros
- ✅ Endpoints respondem corretamente
- ✅ Frontend consegue consumir a API
- ✅ Logs estão funcionando
- ✅ Métricas estão sendo coletadas

### **Testes:**
- Testar endpoints essenciais
- Validar integração com GLPI
- Verificar performance
- Confirmar compatibilidade com frontend
