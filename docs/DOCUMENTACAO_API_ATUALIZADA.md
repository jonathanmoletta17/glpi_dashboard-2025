# DOCUMENTAÇÃO DA API - GLPI DASHBOARD

**Data:** 06 de Janeiro de 2025  
**Versão:** 2.0 (Pós-Auditoria)  
**Status:** Documentação baseada na auditoria completa do backend

---

## 🎯 VISÃO GERAL

### Contexto do Projeto:
- **Tipo:** Dashboard simples para métricas GLPI
- **Interface:** Tela única, sem scroll, foco em simplicidade
- **Objetivo:** Exibir métricas essenciais de técnicos e chamados
- **Arquitetura:** Flask API + Frontend React

### Estado Atual (Pré-Correção):
- ⚠️ **13 endpoints** implementados (excesso para projeto simples)
- ⚠️ **3 APIs diferentes** (Flask, FastAPI, Hybrid)
- ⚠️ **Complexidade desnecessária** para escopo real
- ⚠️ **Duplicações** e funcionalidades não utilizadas

---

## 📋 ENDPOINTS ATUAIS (AUDITORIA)

### API Principal - Flask (`routes.py`)
**Base URL:** `http://localhost:8000/api`

#### ✅ ENDPOINTS ESSENCIAIS (Manter)

##### 1. Health Check
```http
GET /health
```
**Descrição:** Verificação básica de saúde da API  
**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-06T10:30:00Z",
  "version": "1.0.0"
}
```
**Status:** ✅ Essencial - Manter

##### 2. Health Check GLPI
```http
GET /health/glpi
```
**Descrição:** Verificação de conectividade com GLPI  
**Resposta:**
```json
{
  "glpi_status": "connected",
  "response_time": "150ms",
  "last_check": "2025-01-06T10:29:45Z"
}
```
**Status:** ✅ Essencial - Manter

##### 3. Métricas Principais
```http
GET /metrics
```
**Descrição:** Métricas principais do dashboard  
**Parâmetros de Query:**
- `start_date` (opcional): Data início (YYYY-MM-DD)
- `end_date` (opcional): Data fim (YYYY-MM-DD)

**Resposta:**
```json
{
  "total_tickets": 1250,
  "open_tickets": 45,
  "closed_tickets": 1205,
  "average_resolution_time": "2.5 days",
  "period": {
    "start": "2025-01-01",
    "end": "2025-01-06"
  }
}
```
**Status:** ✅ Essencial - Manter

##### 4. Lista de Técnicos
```http
GET /technicians
```
**Descrição:** Lista todos os técnicos ativos  
**Resposta:**
```json
{
  "technicians": [
    {
      "id": 1,
      "name": "João Silva",
      "email": "joao@empresa.com",
      "active_tickets": 12,
      "total_resolved": 145
    }
  ],
  "total": 15
}
```
**Status:** ✅ Essencial - Manter

##### 5. Ranking de Técnicos
```http
GET /technicians/ranking
```
**Descrição:** Ranking de performance dos técnicos  
**Parâmetros de Query:**
- `period` (opcional): last_week, last_month, last_quarter
- `metric` (opcional): resolved_count, avg_time, satisfaction

**Resposta:**
```json
{
  "ranking": [
    {
      "position": 1,
      "technician_id": 5,
      "name": "Maria Santos",
      "score": 98.5,
      "tickets_resolved": 67,
      "avg_resolution_time": "1.8 days"
    }
  ],
  "period": "last_month",
  "total_technicians": 15
}
```
**Status:** ✅ Essencial - Manter

#### ⚠️ ENDPOINTS QUESTIONÁVEIS (Avaliar)

##### 6. Status Geral
```http
GET /status
```
**Descrição:** Status geral do sistema  
**Avaliação:** Pode ser útil, mas verificar se não duplica `/health`
**Recomendação:** Consolidar com health checks

##### 7. Novos Chamados
```http
GET /tickets/new
```
**Descrição:** Lista chamados recentes  
**Avaliação:** Verificar se é exibido no dashboard
**Recomendação:** Manter apenas se usado no frontend

##### 8. Detalhes do Chamado
```http
GET /tickets/<int:ticket_id>
```
**Descrição:** Detalhes específicos de um chamado  
**Avaliação:** Complexidade alta para dashboard simples
**Recomendação:** Remover se não há drill-down no frontend

#### ❌ ENDPOINTS DESNECESSÁRIOS (Remover)

##### 9. Sistema de Alertas
```http
GET /alerts
POST /alerts
DELETE /alerts/<alert_id>
```
**Problema:** Sistema de alertas complexo para dashboard simples  
**Recomendação:** ❌ Remover completamente

##### 10. Estatísticas de Cache
```http
GET /cache/stats
POST /cache/invalidate
```
**Problema:** Exposição desnecessária de detalhes internos  
**Recomendação:** ❌ Remover (cache deve ser transparente)

##### 11. Métricas Filtradas
```http
GET /metrics/filtered
```
**Problema:** Duplicação da funcionalidade de `/metrics`  
**Recomendação:** ❌ Remover (consolidar em `/metrics`)

##### 12. Tipos de Filtro
```http
GET /filter-types
```
**Problema:** Over-engineering para interface simples  
**Recomendação:** ❌ Remover (filtros podem ser hardcoded)

---

## 🗑️ APIS REDUNDANTES (Para Remoção)

### API Híbrida (`hybrid_routes.py`)
**Problema:** Paginação complexa para tela sem scroll

#### Endpoints a Remover:
```http
GET /hybrid/stats                    # Estatísticas de paginação
GET /hybrid/technician/<id>          # Info de paginação do técnico
```
**Justificativa:** Dashboard não tem scroll, paginação é desnecessária

### API FastAPI (`simple_metrics_api.py`)
**Problema:** Duplicação da API Flask principal

#### Endpoints a Remover:
```http
GET /simple/health                   # Duplica Flask health
GET /simple/metrics/operational      # Duplica métricas principais
```
**Justificativa:** Duas APIs para mesma funcionalidade

---

## 🎯 API SIMPLIFICADA (Proposta Pós-Correção)

### Estrutura Final Recomendada:
**Base URL:** `http://localhost:8000/api`

#### Endpoints Finais (5 endpoints essenciais):

1. **`GET /health`** - Health check completo (GLPI + API)
2. **`GET /metrics`** - Métricas principais com filtros opcionais
3. **`GET /technicians`** - Lista de técnicos
4. **`GET /technicians/ranking`** - Ranking de performance
5. **`GET /tickets/recent`** - Chamados recentes (se necessário)

### Benefícios da Simplificação:
- 📉 **Redução de 13 para 5 endpoints** (-62%)
- 🗑️ **Eliminação de 2 APIs redundantes**
- 🧹 **Código mais limpo e manutenível**
- 🚀 **Performance melhorada**
- 📚 **Documentação mais simples**

---

## 🔧 PADRÕES E CONVENÇÕES

### Formato de Resposta Padrão:
```json
{
  "data": {}, // Dados principais
  "meta": {   // Metadados
    "timestamp": "2025-01-06T10:30:00Z",
    "version": "2.0",
    "cache_hit": true
  },
  "status": "success"
}
```

### Tratamento de Erros:
```json
{
  "error": {
    "code": "GLPI_CONNECTION_ERROR",
    "message": "Não foi possível conectar ao GLPI",
    "details": "Connection timeout after 30s"
  },
  "status": "error",
  "timestamp": "2025-01-06T10:30:00Z"
}
```

### Códigos de Status HTTP:
- **200** - Sucesso
- **400** - Erro de validação
- **401** - Não autorizado
- **404** - Recurso não encontrado
- **500** - Erro interno do servidor
- **503** - GLPI indisponível

---

## 📊 CACHE E PERFORMANCE

### Estratégia de Cache Atual:
- **Sistema:** `simple_dict_cache.py` (único após limpeza)
- **TTL Padrão:** 5 minutos
- **Tamanho Máximo:** 1000 entradas
- **Limpeza:** A cada 1 minuto

### Endpoints com Cache:
- ✅ `/metrics` - 5 minutos
- ✅ `/technicians` - 10 minutos
- ✅ `/technicians/ranking` - 15 minutos
- ❌ `/health` - Sem cache (sempre atual)

---

## 🔒 SEGURANÇA E AUTENTICAÇÃO

### Estado Atual:
- **Autenticação:** Básica (usuário/senha GLPI)
- **CORS:** Configurado para desenvolvimento
- **Rate Limiting:** Não implementado (desnecessário para uso interno)
- **HTTPS:** Recomendado para produção

### Recomendações:
- ✅ Manter autenticação simples
- ✅ Configurar CORS para produção
- ❌ Não implementar OAuth (over-engineering)
- ❌ Não implementar JWT (complexidade desnecessária)

---

## 🧪 TESTES E VALIDAÇÃO

### Testes Essenciais:
```python
# Testes básicos necessários
def test_health_endpoint():
    # Verificar se API responde
    pass

def test_metrics_endpoint():
    # Verificar estrutura de dados
    pass

def test_glpi_connection():
    # Verificar conectividade GLPI
    pass
```

### Ferramentas de Teste:
- **Unitários:** pytest
- **Integração:** requests + pytest
- **Performance:** Não necessário (uso interno)

---

## 📈 MONITORAMENTO

### Métricas Essenciais:
- ✅ **Uptime da API**
- ✅ **Tempo de resposta**
- ✅ **Status de conexão GLPI**
- ✅ **Taxa de cache hit**
- ❌ Métricas complexas (desnecessárias)

### Logs Importantes:
```python
# Logs essenciais
logger.info("API started successfully")
logger.warning("GLPI connection slow: 5s")
logger.error("Failed to fetch metrics", extra={"error": str(e)})
```

---

## 🚀 ROADMAP DE IMPLEMENTAÇÃO

### Fase 1: Limpeza (Semana 1)
- ❌ Remover APIs redundantes
- ❌ Eliminar endpoints desnecessários
- ✅ Manter apenas funcionalidades essenciais

### Fase 2: Consolidação (Semana 2)
- 🔄 Refatorar endpoints restantes
- 📚 Atualizar documentação
- 🧪 Implementar testes básicos

### Fase 3: Otimização (Semana 3)
- ⚡ Otimizar performance
- 🔧 Ajustar configurações
- 📊 Implementar monitoramento básico

---

## ✅ CRITÉRIOS DE ACEITAÇÃO

### Funcionalidade:
- ✅ Dashboard continua funcionando
- ✅ Todas as métricas são exibidas
- ✅ Performance mantida ou melhorada

### Qualidade:
- ✅ Máximo 5 endpoints essenciais
- ✅ Uma única API (Flask)
- ✅ Documentação clara e concisa
- ✅ Código limpo e manutenível

### Performance:
- ✅ Tempo de resposta < 500ms
- ✅ Cache funcionando adequadamente
- ✅ Logs estruturados e úteis

---

## 📞 CONTATO E SUPORTE

### Responsável Técnico:
- **Desenvolvedor:** IA Assistant
- **Projeto:** GLPI Dashboard Funcional
- **Última Atualização:** 06/01/2025

### Próximos Passos:
1. **Aprovação** desta documentação
2. **Execução** do plano de correções
3. **Validação** das mudanças
4. **Atualização** da documentação final

---

**Nota:** Esta documentação reflete o estado atual (pré-correção) e serve como base para as simplificações propostas no PLANO_CORRECOES_BACKEND.md.