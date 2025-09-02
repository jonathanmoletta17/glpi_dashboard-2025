# 🤖 Instruções para Trae AI - Refatoração Dashboard GLPI

## 🎯 **Tarefas Organizadas para Execução**

### **📋 Ordem de Execução Recomendada:**
1. **Configurações** → 2. **Aplicação** → 3. **Rotas** → 4. **Documentação**

---

## 1. ⚙️ **TAREFA: Organizar Configurações**

### **Comando para Trae AI:**
```
Analise o arquivo config/system.yaml e consolide todas as configurações do sistema, removendo duplicações e organizando de forma lógica.

ARQUIVOS PARA ANALISAR:
- config/system.yaml (arquivo principal)
- backend/config/settings.py (configurações da aplicação)
- docker-compose.yml (variáveis de ambiente)
- .env (variáveis de ambiente)

OBJETIVO:
Consolidar todas as configurações em config/system.yaml como fonte única de verdade.

ESTRUTURA DESEJADA:
```yaml
app:
  name: "GLPI Dashboard"
  version: "1.0.0"
  environment: "development"

flask:
  secret_key: "${SECRET_KEY}"
  debug: true
  host: "0.0.0.0"
  port: 5000
  cors_origins: ["*"]

glpi:
  base_url: "${GLPI_URL}"
  user_token: "${GLPI_USER_TOKEN}"
  app_token: "${GLPI_APP_TOKEN}"
  timeout: 30
  max_retries: 3

cache:
  type: "RedisCache"
  redis_url: "${REDIS_URL}"
  default_timeout: 300
  key_prefix: "glpi_dashboard:"

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_path: "logs/app.log"
  structured: true

observability:
  prometheus:
    gateway_url: "${PROMETHEUS_GATEWAY_URL}"
    job_name: "glpi_dashboard"
  metrics:
    enabled: true

alerts:
  response_time_threshold: 300
  error_rate_threshold: 0.05
  zero_tickets_threshold: 60

performance:
  target_p95: 1000
  max_content_length: 16777216
  rate_limit_per_minute: 100
```

AÇÃO:
1. Analisar configurações existentes
2. Consolidar em config/system.yaml
3. Remover duplicações
4. Organizar por categorias
5. Manter suporte a variáveis de ambiente
```

---

## 2. 🔧 **TAREFA: Refatorar backend/app.py**

### **Comando para Trae AI:**
```
Analise e refatore o arquivo backend/app.py para consolidar a aplicação principal Flask.

ARQUIVOS PARA ANALISAR:
- backend/app.py (arquivo principal)
- backend/config/settings.py (configurações)
- backend/api/routes.py (rotas)
- backend/services/glpi_service.py (serviço GLPI)
- backend/utils/ (utilitários)
- config/system.yaml (configuração principal)

OBJETIVO:
Consolidar inicialização da aplicação Flask com funcionalidades essenciais.

FUNCIONALIDADES ESSENCIAIS:
1. Inicialização da aplicação Flask
2. Configuração de middleware (CORS, logging, observabilidade)
3. Registro de blueprints da API
4. Tratamento de erros global
5. Inicialização de serviços (GLPI, cache, alertas)
6. Configuração de métricas Prometheus
7. Carregamento de configurações do config/system.yaml

REMOVER:
- Código duplicado
- Configurações desnecessárias
- Middleware não utilizado
- Inicializações complexas desnecessárias

MANTER:
- Compatibilidade com frontend React
- Endpoints essenciais: /api/health, /api/metrics, /api/technicians/ranking
- Logging estruturado
- Observabilidade básica
- Tratamento de erros robusto
- Cache Redis se disponível
- Sistema de alertas

AÇÃO:
1. Analisar código atual
2. Simplificar inicialização
3. Configurar middleware essencial
4. Integrar com config/system.yaml
5. Manter funcionalidades core
```

---

## 3. 🛣️ **TAREFA: Limpar backend/api/routes.py**

### **Comando para Trae AI:**
```
Analise e limpe o arquivo backend/api/routes.py mantendo apenas as rotas essenciais para o dashboard GLPI.

ARQUIVOS PARA ANALISAR:
- backend/api/routes.py (rotas da API)
- backend/services/glpi_service.py (dados GLPI)
- backend/utils/response_formatter.py (formatação)
- backend/utils/date_validator.py (validação)
- backend/utils/performance.py (métricas)
- backend/utils/alerting_system.py (alertas)
- frontend/src/ (consumo da API)

OBJETIVO:
Manter apenas rotas essenciais e remover código desnecessário.

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

AÇÃO:
1. Analisar rotas atuais
2. Identificar rotas essenciais
3. Remover código desnecessário
4. Manter funcionalidades core
5. Preservar integração com frontend
```

---

## 4. 📚 **TAREFA: Atualizar docs/api/openapi.yaml**

### **Comando para Trae AI:**
```
Atualize o arquivo docs/api/openapi.yaml para documentar a API atual do dashboard GLPI após a refatoração.

ARQUIVOS PARA ANALISAR:
- docs/api/openapi.yaml (especificação OpenAPI)
- backend/api/routes.py (endpoints)
- backend/schemas/dashboard.py (schemas)
- frontend/src/ (consumo da API)

OBJETIVO:
Documentar API atual com endpoints essenciais e schemas corretos.

ENDPOINTS A DOCUMENTAR:
1. GET /api/health - Health check da aplicação
2. GET /api/health/glpi - Health check da conexão GLPI
3. GET /api/metrics - Métricas gerais do dashboard
4. GET /api/metrics/filtered - Métricas com filtros aplicados
5. GET /api/technicians - Lista de técnicos ativos
6. GET /api/technicians/ranking - Ranking de técnicos por nível
7. GET /api/tickets/new - Tickets novos recentes
8. GET /api/alerts - Alertas ativos do sistema
9. GET /api/status - Status geral do sistema

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

AÇÃO:
1. Analisar endpoints atuais
2. Atualizar especificação OpenAPI
3. Corrigir schemas
4. Adicionar exemplos
5. Documentar validações
```

---

## 🎯 **Instruções de Execução para Trae AI**

### **Para Cada Tarefa:**

1. **Analisar** o arquivo atual e arquivos relacionados
2. **Identificar** problemas e duplicações
3. **Refatorar** mantendo funcionalidades essenciais
4. **Validar** que não quebrou funcionalidades
5. **Testar** integração com outros componentes

### **Validação Após Cada Tarefa:**

- [ ] Aplicação inicia sem erros
- [ ] Endpoints respondem corretamente
- [ ] Frontend consegue consumir API
- [ ] Logs estão funcionando
- [ ] Métricas estão sendo coletadas
- [ ] Configurações estão carregando
- [ ] Tratamento de erros funciona
- [ ] Cache está operacional
- [ ] Alertas estão ativos

### **Testes de Integração:**

- [ ] Testar endpoints essenciais
- [ ] Validar integração com GLPI
- [ ] Verificar performance
- [ ] Confirmar compatibilidade frontend
- [ ] Testar tratamento de erros
- [ ] Validar cache
- [ ] Verificar alertas
- [ ] Testar métricas

---

## 📋 **Arquivos de Referência**

### **Para Análise:**
- `config/system.yaml` - Configuração principal
- `backend/app.py` - Aplicação principal
- `backend/api/routes.py` - Rotas da API
- `backend/config/settings.py` - Configurações
- `backend/services/glpi_service.py` - Serviço GLPI
- `backend/utils/` - Utilitários
- `docs/api/openapi.yaml` - Documentação API

### **Para Validação:**
- `frontend/src/` - Consumo da API
- `docker-compose.yml` - Configuração Docker
- `.env` - Variáveis de ambiente
- `requirements.txt` - Dependências

---

**Status:** 📋 Pronto para execução pelo Trae AI
**Ordem:** Configurações → Aplicação → Rotas → Documentação
**Validação:** Testar após cada refatoração
