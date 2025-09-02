# 🔍 Análise de Contexto - Arquivos para Refatoração

## 📁 **Arquivos que Precisam ser Analisados e Corrigidos**

### 1. 🔧 **backend/app.py**

#### **Contexto Atual:**
```python
# Arquivo principal da aplicação Flask
# Deve ser analisado para:
- Inicialização da aplicação
- Configuração de middleware
- Registro de blueprints
- Tratamento de erros global
- Inicialização de serviços
```

#### **Problemas Identificados:**
- ❌ Código duplicado
- ❌ Configurações espalhadas
- ❌ Middleware desnecessário
- ❌ Inicializações complexas

#### **Arquivos Relacionados:**
- `backend/config/settings.py` - Configurações
- `backend/api/routes.py` - Rotas da API
- `backend/services/glpi_service.py` - Serviço GLPI
- `backend/utils/` - Utilitários
- `config/system.yaml` - Configuração principal

---

### 2. 🛣️ **backend/api/routes.py**

#### **Contexto Atual:**
```python
# Contém todas as rotas da API REST
# Deve ser analisado para:
- Rotas essenciais vs desnecessárias
- Decoradores utilizados
- Integração com serviços
- Tratamento de erros
- Validação de parâmetros
```

#### **Problemas Identificados:**
- ❌ Rotas de debug e teste
- ❌ Endpoints não utilizados
- ❌ Código duplicado
- ❌ Validações desnecessárias
- ❌ Logs excessivos

#### **Rotas Essenciais a Manter:**
- ✅ GET /api/health
- ✅ GET /api/health/glpi
- ✅ GET /api/metrics
- ✅ GET /api/metrics/filtered
- ✅ GET /api/technicians
- ✅ GET /api/technicians/ranking
- ✅ GET /api/tickets/new
- ✅ GET /api/alerts
- ✅ GET /api/status

#### **Arquivos Relacionados:**
- `backend/services/glpi_service.py` - Dados GLPI
- `backend/utils/response_formatter.py` - Formatação
- `backend/utils/date_validator.py` - Validação
- `backend/utils/performance.py` - Métricas
- `backend/utils/alerting_system.py` - Alertas

---

### 3. 📚 **docs/api/openapi.yaml**

#### **Contexto Atual:**
```yaml
# Especificação OpenAPI da API
# Deve ser analisado para:
- Documentar endpoints atuais
- Incluir schemas corretos
- Exemplos de requisições/respostas
- Códigos de erro
- Validações de parâmetros
```

#### **Problemas Identificados:**
- ❌ Endpoints desatualizados
- ❌ Schemas incorretos
- ❌ Falta de exemplos
- ❌ Documentação incompleta

#### **Schemas Necessários:**
- ✅ DashboardMetrics
- ✅ TechnicianRanking
- ✅ NewTicket
- ✅ Alert
- ✅ ApiResponse
- ✅ ApiError

#### **Arquivos Relacionados:**
- `backend/schemas/dashboard.py` - Schemas de dados
- `backend/api/routes.py` - Endpoints
- `frontend/src/` - Consumo da API

---

### 4. ⚙️ **config/system.yaml**

#### **Contexto Atual:**
```yaml
# Configuração principal do sistema
# Deve ser analisado para:
- Consolidar todas as configurações
- Remover duplicações
- Organizar por categorias
- Suportar diferentes ambientes
```

#### **Problemas Identificados:**
- ❌ Configurações espalhadas
- ❌ Duplicações
- ❌ Valores hardcoded
- ❌ Falta de organização

#### **Configurações a Consolidar:**
- ✅ Flask Application
- ✅ GLPI API
- ✅ Cache
- ✅ Logging
- ✅ Observabilidade
- ✅ Alertas
- ✅ Performance

#### **Arquivos Relacionados:**
- `backend/config/settings.py` - Configurações da aplicação
- `backend/app.py` - Carregamento de configurações
- `docker-compose.yml` - Variáveis de ambiente
- `.env` - Variáveis de ambiente

---

## 🎯 **Estratégia de Refatoração**

### **Fase 1: Configurações**
1. Analisar `config/system.yaml`
2. Consolidar configurações espalhadas
3. Remover duplicações
4. Organizar por categorias

### **Fase 2: Aplicação Principal**
1. Analisar `backend/app.py`
2. Simplificar inicialização
3. Configurar middleware essencial
4. Integrar com configurações

### **Fase 3: Rotas da API**
1. Analisar `backend/api/routes.py`
2. Identificar rotas essenciais
3. Remover código desnecessário
4. Manter funcionalidades core

### **Fase 4: Documentação**
1. Analisar `docs/api/openapi.yaml`
2. Atualizar endpoints
3. Corrigir schemas
4. Adicionar exemplos

---

## 🔍 **Checklist de Validação**

### **Após Cada Refatoração:**
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
- `backend/app.py` - Aplicação principal
- `backend/api/routes.py` - Rotas da API
- `backend/config/settings.py` - Configurações
- `backend/services/glpi_service.py` - Serviço GLPI
- `backend/utils/` - Utilitários
- `config/system.yaml` - Configuração principal
- `docs/api/openapi.yaml` - Documentação API

### **Para Validação:**
- `frontend/src/` - Consumo da API
- `docker-compose.yml` - Configuração Docker
- `.env` - Variáveis de ambiente
- `requirements.txt` - Dependências

---

**Status:** 📋 Pronto para execução das refatorações
**Próximo Passo:** Executar prompts de refatoração em ordem
**Validação:** Testar após cada refatoração
