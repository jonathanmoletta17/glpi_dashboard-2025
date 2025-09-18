# Sistema de Monitoramento - GLPI Dashboard

Este diretório contém a configuração completa do sistema de monitoramento e observabilidade para o GLPI Dashboard.

## 📊 Stack de Monitoramento

### Componentes Principais

- **Prometheus** (`:9090`) - Coleta e armazenamento de métricas
- **Grafana** (`:3000`) - Visualização de dashboards e alertas
- **AlertManager** (`:9093`) - Gerenciamento de alertas
- **Node Exporter** (`:9100`) - Métricas do sistema operacional
- **Blackbox Exporter** (`:9115`) - Monitoramento de endpoints HTTP
- **Loki** (`:3100`) - Agregação de logs
- **Promtail** - Coleta de logs da aplicação

### Componentes Opcionais

- **Redis Exporter** (`:9121`) - Métricas do Redis (se configurado)

## 🚀 Início Rápido

### 1. Pré-requisitos

```bash
# Docker e Docker Compose instalados
docker --version
docker-compose --version
```

### 2. Iniciar Stack de Monitoramento

```bash
# Navegar para o diretório de monitoramento
cd monitoring

# Iniciar todos os serviços
docker-compose up -d

# Verificar status dos containers
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f
```

### 3. Acessar Interfaces

- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093

## 📈 Métricas Monitoradas

### Aplicação (GLPI Dashboard)

- `glpi_api_requests_total` - Total de requisições à API
- `glpi_api_response_time_seconds` - Tempo de resposta das requisições
- `glpi_cache_hit_rate` - Taxa de acerto do cache
- `glpi_connection_status` - Status da conexão com GLPI
- `glpi_tickets_total` - Total de tickets por status

### Sistema

- CPU, Memória, Disco, Rede
- Uptime e disponibilidade
- Processos e conexões

### Endpoints

- Disponibilidade HTTP
- Tempo de resposta
- Status codes

## 🚨 Alertas Configurados

### Críticos

- **ServiceDown**: Serviço indisponível (>30s)
- **GLPIConnectionError**: Falha na conexão GLPI (>1min)
- **HighErrorRate**: Taxa de erro >5% (>1min)
- **DiskSpaceLow**: Espaço em disco >90%

### Warnings

- **HighResponseTime**: Tempo resposta >300ms (>2min)
- **LowCacheHitRate**: Taxa cache <80% (>5min)
- **HighCPUUsage**: CPU >80% (>5min)
- **HighMemoryUsage**: Memória >85% (>3min)

### Informativos

- **NoNewTickets**: Sem tickets novos (>1h)
- **UnusualTrafficPattern**: Tráfego anormal

## 📊 Dashboards Recomendados

### 1. Dashboard Principal - GLPI Overview

- Status geral do sistema
- Métricas de tickets em tempo real
- Performance da API
- Status da conexão GLPI

### 2. Dashboard de Performance

- Tempo de resposta por endpoint
- Taxa de erro e sucesso
- Throughput de requisições
- Utilização de cache

### 3. Dashboard de Infraestrutura

- CPU, Memória, Disco, Rede
- Uptime dos serviços
- Logs de erro
- Alertas ativos

## 🔧 Configuração Avançada

### Personalizar Alertas

Edite `alert_rules.yml` para ajustar:

```yaml
# Exemplo: Alterar threshold de CPU
- alert: HighCPUUsage
  expr: cpu_usage > 90  # Era 80
  for: 10m              # Era 5m
```

### Adicionar Novos Targets

Edite `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'novo-servico'
    static_configs:
      - targets: ['localhost:8080']
```

### Configurar Notificações

Crie `alertmanager.yml`:

```yaml
route:
  group_by: ['alertname']
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK'
        channel: '#alerts'
```

## 📝 Logs

### Localização dos Logs

- **Aplicação**: `../backend/logs/`
- **Prometheus**: Container logs
- **Grafana**: Container logs

### Consultar Logs via Loki

```logql
# Logs de erro da aplicação
{job="glpi-dashboard"} |= "ERROR"

# Logs por correlation ID
{job="glpi-dashboard"} |= "correlation_id=abc-123"

# Logs de performance
{job="glpi-dashboard"} |= "response_time" | json
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Prometheus não coleta métricas

```bash
# Verificar conectividade
curl http://localhost:5000/metrics

# Verificar configuração
docker-compose logs prometheus
```

#### 2. Grafana não conecta ao Prometheus

```bash
# Verificar rede Docker
docker network ls
docker network inspect monitoring_monitoring
```

#### 3. Alertas não disparam

```bash
# Verificar regras
curl http://localhost:9090/api/v1/rules

# Verificar AlertManager
curl http://localhost:9093/api/v1/alerts
```

### Comandos Úteis

```bash
# Recarregar configuração Prometheus
curl -X POST http://localhost:9090/-/reload

# Verificar targets
curl http://localhost:9090/api/v1/targets

# Testar query
curl 'http://localhost:9090/api/v1/query?query=up'

# Parar serviços
docker-compose down

# Limpar volumes (CUIDADO: perde dados)
docker-compose down -v
```

## 📚 Recursos Adicionais

- [Documentação Prometheus](https://prometheus.io/docs/)
- [Documentação Grafana](https://grafana.com/docs/)
- [PromQL Guide](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboard Gallery](https://grafana.com/grafana/dashboards/)

## 🔐 Segurança

### Recomendações

1. **Alterar senhas padrão**
2. **Configurar HTTPS em produção**
3. **Restringir acesso por IP**
4. **Usar autenticação externa (LDAP/OAuth)**
5. **Monitorar logs de acesso**

### Configuração de Produção

```yaml
# docker-compose.prod.yml
services:
  grafana:
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_SERVER_PROTOCOL=https
      - GF_SERVER_CERT_FILE=/etc/ssl/grafana.crt
      - GF_SERVER_CERT_KEY=/etc/ssl/grafana.key
```

---

**Última atualização**: 28/01/2025
**Versão**: 1.0.0
**Maintainer**: GLPI Dashboard Team
