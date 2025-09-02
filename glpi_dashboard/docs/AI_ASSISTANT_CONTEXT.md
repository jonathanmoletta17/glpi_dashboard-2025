# Contexto e Diretrizes para Assistente de IA - GLPI Dashboard

## 📋 Visão Geral do Projeto

O **GLPI Dashboard** é uma aplicação completa para visualização de métricas do sistema GLPI, composta por:

- **Backend**: Flask (Python) com arquitetura modular
- **Frontend**: React + TypeScript com Vite
- **Integração**: API REST com sistema GLPI
- **Observabilidade**: Logs estruturados, métricas Prometheus, alertas
- **Cache**: Sistema inteligente com Redis/SimpleCache

## 🏗️ Arquitetura do Sistema

### Backend (Flask)
```
backend/
├── api/                    # Endpoints REST
│   └── routes.py          # Rotas principais da API
├── config/                # Configurações centralizadas
│   └── settings.py        # Configurações com validação
├── services/              # Camada de serviços
│   ├── glpi_service.py    # Integração com GLPI
│   └── api_service.py     # Serviços de API
├── utils/                 # Utilitários e middleware
│   ├── observability.py  # Sistema de observabilidade
│   ├── prometheus_metrics.py # Métricas
│   └── structured_logging.py # Logs estruturados
└── schemas/               # Validação de dados
    └── dashboard.py       # Schemas do dashboard
```

### Frontend (React + TypeScript)
```
frontend/src/
├── components/            # Componentes React
│   ├── dashboard/        # Componentes do dashboard
│   └── Header.tsx        # Cabeçalho da aplicação
├── hooks/                # Hooks customizados
│   └── useDashboard.ts   # Hook principal do dashboard
├── services/             # Serviços de API
│   ├── api.ts           # Cliente HTTP principal
│   └── cache.ts         # Sistema de cache
├── types/               # Definições TypeScript
│   └── index.ts         # Tipos principais
└── utils/               # Utilitários
    └── performanceMonitor.ts # Monitor de performance
```

## 🎯 Diretrizes para Interação

### ✅ O QUE FAZER

#### 1. **Análise e Debugging**
- Sempre verificar logs estruturados em `backend/logs/`
- Usar métricas Prometheus para análise de performance
- Verificar status dos serviços via endpoints `/api/status`
- Analisar cache hits/misses para otimização

#### 2. **Desenvolvimento de Features**
- Seguir padrão de arquitetura modular existente
- Implementar validação com Pydantic (backend) e TypeScript (frontend)
- Adicionar logs estruturados para novas funcionalidades
- Implementar cache inteligente para dados frequentes
- Usar hooks customizados para lógica de estado

#### 3. **Configuração e Deploy**
- Sempre usar variáveis de ambiente via `.env`
- Validar configurações em `config/settings.py`
- Testar integração GLPI antes de deploy
- Verificar conectividade Redis/cache

#### 4. **Monitoramento e Observabilidade**
- Implementar métricas para novas funcionalidades
- Usar correlation IDs para rastreamento
- Configurar alertas para cenários críticos
- Monitorar performance de queries GLPI

#### 5. **Testes e Qualidade**
- Executar testes unitários: `npm run test` (frontend), `pytest` (backend)
- Verificar cobertura de código
- Validar tipos TypeScript: `npm run type-check`
- Usar linting: `npm run lint` e `pylint`

### ❌ O QUE NÃO FAZER

#### 1. **Segurança**
- **NUNCA** commitar tokens ou credenciais no código
- **NÃO** expor informações sensíveis em logs
- **NÃO** desabilitar validação de entrada
- **NÃO** usar HTTP em produção (sempre HTTPS)

#### 2. **Performance**
- **NÃO** fazer requisições GLPI sem cache
- **NÃO** implementar loops infinitos de polling
- **NÃO** carregar dados desnecessários
- **NÃO** ignorar timeouts de API

#### 3. **Arquitetura**
- **NÃO** quebrar a separação de responsabilidades
- **NÃO** acessar GLPI diretamente do frontend
- **NÃO** misturar lógica de negócio com apresentação
- **NÃO** criar dependências circulares

#### 4. **Dados**
- **NÃO** modificar dados GLPI sem autorização
- **NÃO** cachear dados sensíveis por muito tempo
- **NÃO** ignorar validação de entrada
- **NÃO** assumir formato de dados sem validação

## 🔧 Comandos Essenciais

### Backend
```bash
# Iniciar servidor de desenvolvimento
cd backend && python app.py

# Executar testes
pytest

# Verificar logs
tail -f logs/app.log

# Monitorar métricas
curl http://localhost:5000/api/metrics
```

### Frontend
```bash
# Iniciar servidor de desenvolvimento
cd frontend && npm run dev

# Executar testes
npm run test

# Build para produção
npm run build

# Verificar tipos
npm run type-check
```

## 🚨 Cenários Críticos

### 1. **GLPI Indisponível**
- Verificar conectividade de rede
- Validar tokens de autenticação
- Implementar fallback com dados em cache
- Alertar usuários sobre indisponibilidade

### 2. **Performance Degradada**
- Analisar métricas de response time
- Verificar utilização de cache
- Otimizar queries GLPI
- Implementar rate limiting se necessário

### 3. **Inconsistência de Dados**
- Executar auditoria de dados: `python audit_dashboard_metrics.py`
- Verificar logs de erro estruturados
- Validar integridade do cache
- Reprocessar dados se necessário

## 📊 Métricas e KPIs

### Performance
- Response time < 300ms (alerta se > 300ms)
- Error rate < 5% (alerta se > 5%)
- Cache hit rate > 80%
- GLPI API calls < 100/min

### Disponibilidade
- Uptime > 99.5%
- GLPI connectivity > 95%
- Zero tickets threshold: 60s

### Qualidade
- Test coverage > 80%
- TypeScript strict mode enabled
- Zero security vulnerabilities
- Linting score > 9.0

## 🔍 Debugging e Troubleshooting

### Logs Estruturados
```json
{
  "timestamp": "2025-01-28T10:30:00Z",
  "level": "ERROR",
  "logger": "glpi.service",
  "message": "Falha na autenticação GLPI",
  "correlation_id": "abc-123",
  "error_details": {...}
}
```

### Endpoints de Debug
- `GET /api/status` - Status geral do sistema
- `GET /api/health` - Health check detalhado
- `GET /api/metrics` - Métricas Prometheus
- `GET /api/cache/stats` - Estatísticas de cache

## 🎯 Próximos Passos Recomendados

1. **Implementar autenticação robusta**
2. **Adicionar testes de integração**
3. **Configurar CI/CD pipeline**
4. **Implementar backup de configurações**
5. **Adicionar documentação de API (OpenAPI/Swagger)**

---

**Última atualização**: 28/01/2025
**Versão do projeto**: Commit 306ca75
**Ambiente**: Desenvolvimento local