# GLPI Dashboard API Documentation

## Visão Geral

Esta documentação fornece informações completas sobre a API do GLPI Dashboard, incluindo todos os endpoints disponíveis, schemas de dados, exemplos de uso e guias de integração.

## Documentação Interativa (Swagger UI)

### Acesso Local
Quando o servidor estiver rodando localmente, acesse:
- **Swagger UI**: http://localhost:5000/api/docs
- **Especificação OpenAPI**: http://localhost:5000/api/openapi.yaml

### Acesso em Produção
- **Swagger UI**: https://api.glpi-dashboard.com/api/docs
- **Especificação OpenAPI**: https://api.glpi-dashboard.com/api/openapi.yaml

## Endpoints Principais

### 📊 Métricas
- `GET /api/metrics` - Métricas gerais do dashboard
- `GET /api/metrics/filtered` - Métricas com filtros de data

### 👥 Técnicos
- `GET /api/technicians/ranking` - Ranking de técnicos por performance

### 🎫 Tickets
- `GET /api/tickets/new` - Tickets novos no sistema

### 🚨 Alertas
- `GET /api/alerts` - Alertas do sistema

### 📈 Performance
- `GET /api/performance/stats` - Estatísticas de performance

### 🔧 Sistema
- `GET /api/status` - Status geral do sistema
- `GET /api/health` - Health check da API
- `GET /api/filter-types` - Tipos de filtros disponíveis

## Autenticação

A API utiliza autenticação baseada em tokens GLPI. Configure as seguintes variáveis de ambiente:

```bash
GLPI_URL=https://seu-glpi.com/apirest.php
GLPI_USER_TOKEN=seu_user_token_aqui
GLPI_APP_TOKEN=seu_app_token_aqui
```

### Processo de Autenticação

1. **Inicialização de Sessão**
   ```python
   headers = {
       'Content-Type': 'application/json',
       'App-Token': 'seu_app_token_aqui',
       'Authorization': 'user_token seu_user_token_aqui'
   }

   url = f"{base_url}/apirest.php/initSession"
   response = session.get(url, headers=headers)
   ```

2. **Resposta de Sucesso**
   ```json
   {
       "session_token": "fkegh7v413anh1598a79...",
       "glpi_currenttime": "2025-01-22 22:55:48"
   }
   ```

3. **Headers para Próximas Requisições**
   ```python
   session.headers.update({
       'Session-Token': session_token_obtido
   })
   ```

## Schemas de Dados

### Métricas Response
```json
{
  "tickets_novos": 15,
  "tickets_pendentes": 8,
  "tickets_em_progresso": 12,
  "tickets_resolvidos": 45,
  "metricas_por_nivel": {
    "N1": { "novos": 5, "pendentes": 3, "progresso": 4, "resolvidos": 20 },
    "N2": { "novos": 6, "pendentes": 3, "progresso": 5, "resolvidos": 15 },
    "N3": { "novos": 3, "pendentes": 2, "progresso": 2, "resolvidos": 8 },
    "N4": { "novos": 1, "pendentes": 0, "progresso": 1, "resolvidos": 2 }
  },
  "timestamp": "2025-01-22T22:55:48Z"
}
```

### Ranking de Técnicos Response
```json
{
  "ranking": [
    {
      "tecnico_id": 123,
      "nome": "João Silva",
      "nivel": "N2",
      "tickets_resolvidos": 25,
      "tempo_medio_resolucao": "2.5h",
      "score": 95.5
    }
  ],
  "timestamp": "2025-01-22T22:55:48Z"
}
```

## Rate Limiting

- **100 requests por minuto** por IP
- **1000 requests por hora** por token
- Headers de resposta incluem informações de rate limiting:
  ```
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 95
  X-RateLimit-Reset: 1642896000
  ```

## Cache

- **Métricas**: cache de 5 minutos
- **Rankings**: cache de 15 minutos
- **Status**: sem cache
- **Health checks**: cache de 1 minuto

## Códigos de Status

- `200` - Sucesso
- `400` - Requisição inválida
- `401` - Não autorizado
- `403` - Acesso negado
- `404` - Recurso não encontrado
- `429` - Rate limit excedido
- `500` - Erro interno do servidor
- `503` - Serviço indisponível

## Exemplos de Uso

### Obter Métricas Básicas
```bash
curl -X GET "http://localhost:5000/api/metrics" \
  -H "Authorization: Bearer seu_token_aqui"
```

### Obter Métricas Filtradas
```bash
curl -X GET "http://localhost:5000/api/metrics/filtered?start_date=2025-01-01&end_date=2025-01-31" \
  -H "Authorization: Bearer seu_token_aqui"
```

### Obter Ranking de Técnicos
```bash
curl -X GET "http://localhost:5000/api/technicians/ranking?nivel=N2" \
  -H "Authorization: Bearer seu_token_aqui"
```

## Troubleshooting

### Problemas Comuns

1. **Erro 401 - Token Inválido**
   - Verifique se o token GLPI está correto
   - Confirme se o token não expirou
   - Valide as variáveis de ambiente

2. **Erro 429 - Rate Limit**
   - Implemente backoff exponencial
   - Reduza a frequência de requisições
   - Use cache local quando possível

3. **Erro 503 - GLPI Indisponível**
   - Verifique conectividade com o servidor GLPI
   - Confirme se o serviço GLPI está rodando
   - Valide configurações de rede

### Logs e Debugging

Para habilitar logs detalhados:
```bash
export LOG_LEVEL=DEBUG
export GLPI_DEBUG=true
```

## Documentação Adicional

- **OpenAPI Specification**: Consulte o arquivo `openapi.yaml` para especificação completa
- **Postman Collection**: Disponível em `/docs/postman/`
- **SDK Python**: Documentação em `/docs/sdk/`

## Suporte

Para suporte técnico:
- **Email**: dev@empresa.com
- **Issues**: GitHub Issues
- **Documentação**: Wiki interno

---

**Versão**: 1.0.0
**Última Atualização**: 2025-01-22
**Licença**: MIT
