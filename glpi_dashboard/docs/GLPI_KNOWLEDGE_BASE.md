# Base de Conhecimento - Estrutura GLPI

## Índice
1. [Visão Geral](#visão-geral)
2. [Configuração e Autenticação](#configuração-e-autenticação)
3. [Mapeamento de Campos](#mapeamento-de-campos)
4. [Status de Tickets](#status-de-tickets)
5. [Níveis de Atendimento](#níveis-de-atendimento)
6. [Estrutura de Consultas](#estrutura-de-consultas)
7. [Endpoints Principais](#endpoints-principais)
8. [Sistema de Cache](#sistema-de-cache)
9. [Métricas e Relatórios](#métricas-e-relatórios)
10. [Filtros de Data](#filtros-de-data)

## Visão Geral

O GLPI (Gestionnaire Libre de Parc Informatique) é um sistema de gestão de ativos de TI e helpdesk. Este documento detalha a estrutura de integração utilizada no dashboard funcional.

### Arquitetura da Integração

```
Dashboard Frontend → API Service → GLPI Service → GLPI API
```

## Configuração e Autenticação

### Variáveis de Ambiente Obrigatórias

```bash
GLPI_URL=http://seu-glpi.com/apirest.php
GLPI_APP_TOKEN=seu_app_token
GLPI_USER_TOKEN=seu_user_token
API_TIMEOUT=30
```

### Processo de Autenticação

1. **Inicialização de Sessão**:
   - Endpoint: `{GLPI_URL}/initSession`
   - Headers: `App-Token` e `Authorization: user_token {USER_TOKEN}`
   - Retorna: `session_token` válido por 1 hora

2. **Headers de Requisição**:
   ```json
   {
     "Content-Type": "application/json",
     "App-Token": "seu_app_token",
     "Session-Token": "session_token_obtido"
   }
   ```

3. **Renovação Automática**:
   - Sistema detecta tokens expirados (401/403)
   - Re-autentica automaticamente
   - Retry com backoff exponencial (máx 3 tentativas)

## Mapeamento de Campos

### Descoberta Dinâmica de Field IDs

O sistema descobre automaticamente os IDs dos campos através do endpoint `/listSearchOptions/Ticket`:

```javascript
// Campos principais descobertos dinamicamente
field_ids = {
  "GROUP": "8",    // Grupo técnico
  "STATUS": "12",  // Status do ticket
  "TECH": "5"      // Técnico responsável
}
```

### Nomes de Campos Reconhecidos

**Grupo Técnico**:
- "Grupo técnico", "Technical group", "Grupo tecnico"
- "Assigned group", "Group", "Grupo"
- "Grupo atribuído", "Grupo responsável", "Responsible group"

**Status**:
- "Status", "Estado", "State"
- "Situação", "Condition"

**Técnico**:
- "Técnico", "Technician", "Tecnico"
- "Assigned technician", "Técnico encarregado"
- "Assigned to", "Atribuído para", "Técnico responsável"
- "Responsável", "Assignee", "Atribuído"

### Fallback de Field IDs

Caso a descoberta automática falhe, são utilizados IDs padrão:
```javascript
{
  "GROUP": "8",
  "STATUS": "12", 
  "TECH": "5"
}
```

## Status de Tickets

### Mapeamento de Status

```javascript
status_map = {
  "Novo": 1,
  "Processando (atribuído)": 2,
  "Processando (planejado)": 3,
  "Pendente": 4,
  "Solucionado": 5,
  "Fechado": 6
}
```

### Agrupamento para Dashboard

- **Novos**: Status 1
- **Pendentes**: Status 4
- **Em Progresso**: Status 2 + 3
- **Resolvidos**: Status 5 + 6

## Níveis de Atendimento

### Grupos Técnicos por Nível

```javascript
service_levels = {
  "N1": 89,  // CC-SE-SUBADM-DTIC > N1
  "N2": 90,  // CC-SE-SUBADM-DTIC > N2
  "N3": 91,  // CC-SE-SUBADM-DTIC > N3
  "N4": 92   // CC-SE-SUBADM-DTIC > N4
}
```

### Estrutura Hierárquica

Os níveis são identificados através do campo 8 (estrutura hierárquica) que contém valores como "N1", "N2", "N3", "N4".

## Estrutura de Consultas

### Formato de Critérios de Busca

O GLPI utiliza um sistema de critérios estruturado:

```javascript
// Exemplo: Buscar tickets do N1 com status Novo
search_params = {
  "criteria[0][field]": "8",        // Campo hierarquia
  "criteria[0][searchtype]": "contains",
  "criteria[0][value]": "N1",
  "criteria[1][link]": "AND",
  "criteria[1][field]": "12",       // Campo status
  "criteria[1][searchtype]": "equals",
  "criteria[1][value]": "1",        // Status Novo
  "range": "0-999999",
  "forcedisplay[0]": "2",           // ID do ticket
  "forcedisplay[1]": "12",          // Status
  "forcedisplay[2]": "8"            // Grupo
}
```

### Tipos de Busca Suportados

- `equals`: Igualdade exata
- `contains`: Contém o valor
- `morethan`: Maior que (datas)
- `lessthan`: Menor que (datas)

### Operadores Lógicos

- `AND`: E lógico
- `OR`: OU lógico

## Endpoints Principais

### Autenticação
- `GET /initSession` - Iniciar sessão
- `GET /killSession` - Encerrar sessão

### Consultas de Tickets
- `GET /search/Ticket` - Buscar tickets com critérios
- `GET /listSearchOptions/Ticket` - Listar opções de busca

### Usuários e Técnicos
- `GET /search/User` - Buscar usuários
- `GET /search/Profile_User` - Buscar perfis de usuário

### Grupos
- `GET /search/Group` - Buscar grupos

## Sistema de Cache

### Configuração de Cache

```javascript
cache_config = {
  "technician_ranking": { ttl: 300 },      // 5 minutos
  "active_technicians": { ttl: 600 },      // 10 minutos
  "field_ids": { ttl: 1800 },              // 30 minutos
  "dashboard_metrics": { ttl: 180 },       // 3 minutos
  "dashboard_metrics_filtered": {},        // Cache dinâmico
  "priority_names": {}                     // Cache de prioridades
}
```

### Estratégia de Cache

1. **Cache por TTL**: Dados expiram após tempo definido
2. **Cache Dinâmico**: Para filtros de data específicos
3. **Invalidação**: Automática por expiração ou manual

## Métricas e Relatórios

### Métricas Gerais

Coletadas através do método `get_general_metrics()`:

```javascript
// Estrutura de retorno
{
  "novos": 15,
  "pendentes": 8,
  "progresso": 12,
  "resolvidos": 45,
  "total": 80
}
```

### Métricas por Nível

Coletadas através do método `get_metrics_by_level()`:

```javascript
// Estrutura de retorno
{
  "N1": { "novos": 5, "pendentes": 2, "progresso": 3, "resolvidos": 10 },
  "N2": { "novos": 4, "pendentes": 3, "progresso": 4, "resolvidos": 15 },
  "N3": { "novos": 3, "pendentes": 2, "progresso": 3, "resolvidos": 12 },
  "N4": { "novos": 3, "pendentes": 1, "progresso": 2, "resolvidos": 8 }
}
```

### Ranking de Técnicos

Coletado através do método `get_technicians_by_assignments()`:

```javascript
// Estrutura de retorno
[
  {
    "id": "123",
    "name": "João Silva",
    "total_tickets": 25,
    "solved_tickets": 20,
    "closed_tickets": 18,
    "performance_score": 85.5
  }
]
```

## Filtros de Data

### Implementação de Filtros

Utiliza a classe `DateValidator` para construir critérios:

```javascript
// Exemplo de filtro de data
date_criteria = DateValidator.construir_criterios_filtro_data(
  start_date="2024-01-01",
  end_date="2024-01-31",
  criteria_start_index=2
)

// Resultado:
{
  "criteria[2][link]": "AND",
  "criteria[2][field]": "15",      // Campo de data
  "criteria[2][searchtype]": "morethan",
  "criteria[2][value]": "2024-01-01",
  "criteria[3][link]": "AND",
  "criteria[3][field]": "15",
  "criteria[3][searchtype]": "lessthan",
  "criteria[3][value]": "2024-01-31"
}
```

### Campos de Data Utilizados

- **Campo 15**: Data de criação
- **Campo 19**: Data de modificação
- **Campo 80**: ID da entidade (para filtros adicionais)

### Validação de Datas

- Formato obrigatório: `YYYY-MM-DD`
- Validação automática de formato
- Fallback para períodos padrão em caso de erro

## Monitoramento e Logs

### Métricas Prometheus

- `glpi_request_duration`: Tempo de resposta das requisições
- `glpi_request_total`: Total de requisições por endpoint
- `glpi_error_total`: Total de erros por tipo

### Logs Estruturados

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "correlation_id": "req-123",
  "endpoint": "GET /search/Ticket",
  "status_code": 200,
  "duration": 1.25,
  "attempt": 1
}
```

### Alertas de Performance

- Requisições > 5s geram alertas
- Falhas de autenticação são logadas
- Timeouts são monitorados

## Troubleshooting

### Problemas Comuns

1. **Token Expirado**:
   - Sintoma: HTTP 401/403
   - Solução: Re-autenticação automática

2. **Field IDs Incorretos**:
   - Sintoma: Resultados vazios
   - Solução: Verificar descoberta de campos

3. **Cache Desatualizado**:
   - Sintoma: Dados antigos
   - Solução: Invalidar cache manualmente

4. **Timeout de Requisição**:
   - Sintoma: Requisições lentas
   - Solução: Ajustar API_TIMEOUT

### Debug e Diagnóstico

```bash
# Verificar logs de debug
tail -f debug_ranking.log

# Verificar métricas Prometheus
curl http://localhost:8000/metrics

# Testar conectividade GLPI
curl -H "App-Token: TOKEN" {GLPI_URL}/initSession
```

## Considerações de Segurança

1. **Tokens**: Nunca expor em logs ou código
2. **HTTPS**: Sempre usar conexões seguras
3. **Timeout**: Configurar timeouts apropriados
4. **Rate Limiting**: Respeitar limites da API GLPI
5. **Validação**: Sempre validar dados de entrada

## Versionamento e Compatibilidade

- **GLPI Versão**: 9.5+
- **API REST**: Versão 1.0
- **Compatibilidade**: Testado com GLPI 9.5.x e 10.x

---

*Documento atualizado em: Janeiro 2024*
*Versão: 1.0*