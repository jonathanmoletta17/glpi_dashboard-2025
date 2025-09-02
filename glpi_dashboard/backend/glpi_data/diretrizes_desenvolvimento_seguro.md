# Diretrizes de Desenvolvimento Seguro - GLPI Dashboard

## Checklist Obrigatório Antes de Qualquer Mudança

### ✅ Pré-Implementação

#### 1. Análise de Impacto
- [ ] **Identificar todos os métodos/funções afetados**
- [ ] **Mapear dependências e integrações**
- [ ] **Avaliar impacto em funcionalidades existentes**
- [ ] **Verificar se mudança é realmente necessária**

#### 2. Compreensão da API
- [ ] **Documentar códigos de status HTTP esperados**
- [ ] **Testar comportamento de paginação (status 206)**
- [ ] **Validar autenticação e tokens**
- [ ] **Verificar limites de rate limiting**

#### 3. Preparação do Ambiente
- [ ] **Criar backup automático dos arquivos afetados**
- [ ] **Configurar ambiente de teste isolado**
- [ ] **Preparar dados de teste representativos**
- [ ] **Definir critérios de sucesso/falha**

### ✅ Durante a Implementação

#### 4. Desenvolvimento Incremental
- [ ] **Implementar uma mudança por vez**
- [ ] **Testar cada mudança isoladamente**
- [ ] **Validar logs e métricas após cada alteração**
- [ ] **Documentar cada modificação realizada**

#### 5. Validação de Código
- [ ] **Revisar tratamento de códigos de status HTTP**
- [ ] **Verificar tratamento de exceções**
- [ ] **Validar logs estruturados**
- [ ] **Confirmar timeouts e retries adequados**

### ✅ Pós-Implementação

#### 6. Testes de Validação
- [ ] **Executar testes de funcionalidade básica**
- [ ] **Testar cenários de paginação**
- [ ] **Validar métricas do dashboard**
- [ ] **Verificar logs de erro/sucesso**

#### 7. Monitoramento
- [ ] **Monitorar métricas por 24h após mudança**
- [ ] **Verificar alertas e notificações**
- [ ] **Validar performance e tempo de resposta**
- [ ] **Confirmar ausência de regressões**

## Padrões de Código Seguros

### 1. Tratamento de Respostas HTTP

#### ❌ Padrões Perigosos (NUNCA usar)
```python
# PERIGOSO: Rejeita status 206 válido
if not response.ok:
    return None

# PERIGOSO: Assume apenas 200 como sucesso
if response.status_code == 200:
    return response.json()

# PERIGOSO: Não documenta códigos aceitos
if response.status_code in [200, 206]:  # Por que 206?
    return response.json()
```

#### ✅ Padrões Seguros (SEMPRE usar)
```python
# SEGURO: Códigos documentados e centralizados
VALID_STATUS_CODES = {
    200: "Success - Resposta completa",
    206: "Partial Content - Resposta paginada (GLPI API)"
}

def is_valid_response(response):
    """Valida se resposta HTTP é aceitável para GLPI API.
    
    Args:
        response: Objeto response do requests
        
    Returns:
        bool: True se status é válido
        
    Note:
        Status 206 é normal para paginação da API GLPI
    """
    return response.status_code in VALID_STATUS_CODES.keys()

def handle_glpi_response(response):
    """Processa resposta da API GLPI com tratamento adequado."""
    if not is_valid_response(response):
        logger.error(f"Status HTTP inválido: {response.status_code}")
        raise GLPIAPIError(f"Status inválido: {response.status_code}")
    
    logger.info(f"Resposta válida: {response.status_code} - {VALID_STATUS_CODES[response.status_code]}")
    return response.json()
```

### 2. Logging Estruturado

#### ✅ Padrão de Log Seguro
```python
import logging
import json
from datetime import datetime

def log_api_call(method, url, status_code, response_time, error=None):
    """Log estruturado para chamadas de API."""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": method,
        "url": url,
        "status_code": status_code,
        "response_time_ms": response_time,
        "success": status_code in VALID_STATUS_CODES,
        "error": error
    }
    
    if log_data["success"]:
        logger.info(f"API_CALL_SUCCESS: {json.dumps(log_data)}")
    else:
        logger.error(f"API_CALL_FAILURE: {json.dumps(log_data)}")
```

### 3. Tratamento de Exceções

#### ✅ Padrão de Exception Handling
```python
class GLPIAPIError(Exception):
    """Exceção específica para erros da API GLPI."""
    def __init__(self, message, status_code=None, response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

def safe_api_call(func):
    """Decorator para chamadas seguras à API."""
    def wrapper(*args, **kwargs):
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
            response_time = (time.time() - start_time) * 1000
            
            log_api_call(
                method=func.__name__,
                url=kwargs.get('url', 'unknown'),
                status_code=200,
                response_time=response_time
            )
            return result
            
        except GLPIAPIError as e:
            log_api_call(
                method=func.__name__,
                url=kwargs.get('url', 'unknown'),
                status_code=e.status_code,
                response_time=0,
                error=str(e)
            )
            raise
        except Exception as e:
            log_api_call(
                method=func.__name__,
                url=kwargs.get('url', 'unknown'),
                status_code=None,
                response_time=0,
                error=f"Unexpected error: {str(e)}"
            )
            raise GLPIAPIError(f"Erro inesperado: {str(e)}")
    
    return wrapper
```

## Configurações de Segurança

### 1. Configuração Centralizada

```python
# config/glpi_config.py
class GLPIConfig:
    """Configuração centralizada para API GLPI."""
    
    # Status HTTP válidos (DOCUMENTADO)
    VALID_STATUS_CODES = {
        200: "Success - Resposta completa",
        206: "Partial Content - Paginação automática da API GLPI"
    }
    
    # Timeouts (em segundos)
    DEFAULT_TIMEOUT = 30
    LONG_OPERATION_TIMEOUT = 60
    
    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # segundos
    
    # Paginação
    DEFAULT_PAGE_SIZE = 50
    MAX_PAGE_SIZE = 1000
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_API_CALLS = True
    LOG_PERFORMANCE = True
    
    @classmethod
    def validate_config(cls):
        """Valida configuração antes do uso."""
        required_env_vars = [
            'GLPI_URL',
            'GLPI_APP_TOKEN', 
            'GLPI_USER_TOKEN'
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ConfigurationError(f"Variáveis obrigatórias não definidas: {missing_vars}")
```

### 2. Monitoramento e Alertas

```python
# monitoring/health_check.py
class GLPIHealthMonitor:
    """Monitor de saúde para API GLPI."""
    
    def __init__(self):
        self.metrics = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'status_206_calls': 0,
            'avg_response_time': 0
        }
    
    def record_api_call(self, status_code, response_time):
        """Registra métricas de chamada da API."""
        self.metrics['total_calls'] += 1
        
        if status_code in GLPIConfig.VALID_STATUS_CODES:
            self.metrics['successful_calls'] += 1
            if status_code == 206:
                self.metrics['status_206_calls'] += 1
        else:
            self.metrics['failed_calls'] += 1
        
        # Atualizar média de tempo de resposta
        current_avg = self.metrics['avg_response_time']
        total_calls = self.metrics['total_calls']
        self.metrics['avg_response_time'] = (
            (current_avg * (total_calls - 1) + response_time) / total_calls
        )
    
    def check_health(self):
        """Verifica saúde do sistema."""
        if self.metrics['total_calls'] == 0:
            return {"status": "unknown", "reason": "Nenhuma chamada registrada"}
        
        success_rate = self.metrics['successful_calls'] / self.metrics['total_calls']
        
        if success_rate < 0.8:  # Menos de 80% de sucesso
            return {
                "status": "unhealthy",
                "reason": f"Taxa de sucesso baixa: {success_rate:.2%}",
                "metrics": self.metrics
            }
        
        if self.metrics['avg_response_time'] > 5000:  # Mais de 5 segundos
            return {
                "status": "degraded",
                "reason": f"Tempo de resposta alto: {self.metrics['avg_response_time']:.0f}ms",
                "metrics": self.metrics
            }
        
        return {
            "status": "healthy",
            "metrics": self.metrics
        }
```

## Testes Obrigatórios

### 1. Testes de Status HTTP

```python
# tests/test_http_status_handling.py
import pytest
from unittest.mock import Mock

def test_status_200_accepted():
    """Testa se status 200 é aceito corretamente."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"data": "test"}
    
    result = handle_glpi_response(response)
    assert result == {"data": "test"}

def test_status_206_accepted():
    """Testa se status 206 (paginação) é aceito corretamente."""
    response = Mock()
    response.status_code = 206
    response.json.return_value = {"data": "paginated"}
    
    result = handle_glpi_response(response)
    assert result == {"data": "paginated"}

def test_invalid_status_rejected():
    """Testa se status inválidos são rejeitados."""
    response = Mock()
    response.status_code = 404
    
    with pytest.raises(GLPIAPIError):
        handle_glpi_response(response)

def test_dashboard_metrics_with_pagination():
    """Testa métricas do dashboard com resposta paginada (206)."""
    # Simular resposta 206 da API GLPI
    mock_response = Mock()
    mock_response.status_code = 206
    mock_response.json.return_value = {
        "totalcount": 10065,
        "count": 50,
        "data": [/* dados de tickets */]
    }
    
    # Testar se dashboard processa corretamente
    with patch('requests.get', return_value=mock_response):
        metrics = get_dashboard_metrics()
        assert metrics['total_tickets'] > 0
        assert metrics['total_tickets'] == 10065
```

### 2. Testes de Integração

```python
# tests/test_glpi_integration.py
def test_real_glpi_api_pagination():
    """Testa paginação real com API GLPI."""
    # Este teste deve ser executado contra API real em ambiente de teste
    service = GLPIService()
    
    # Buscar muitos tickets para forçar paginação
    tickets = service.search_tickets(limit=1000)
    
    # Verificar se dados foram retornados mesmo com status 206
    assert len(tickets) > 0
    assert 'id' in tickets[0]
    
def test_dashboard_metrics_integration():
    """Testa métricas do dashboard com dados reais."""
    metrics = get_dashboard_metrics()
    
    # Verificar se métricas não estão zeradas
    assert metrics['total_tickets'] > 0
    assert metrics['n1_tickets'] >= 0
    assert metrics['n2_tickets'] >= 0
    assert metrics['n3_tickets'] >= 0
    assert metrics['n4_tickets'] >= 0
    
    # Verificar consistência
    total_by_level = (
        metrics['n1_tickets'] + 
        metrics['n2_tickets'] + 
        metrics['n3_tickets'] + 
        metrics['n4_tickets']
    )
    assert total_by_level <= metrics['total_tickets']
```

## Procedimentos de Emergência

### 1. Rollback Rápido

```bash
#!/bin/bash
# scripts/emergency_rollback.sh

echo "=== PROCEDIMENTO DE ROLLBACK DE EMERGÊNCIA ==="
echo "Timestamp: $(date)"

# 1. Parar serviços
echo "Parando serviços..."
sudo systemctl stop glpi-dashboard

# 2. Restaurar backup mais recente
echo "Restaurando backup..."
BACKUP_FILE=$(ls -t backups/glpi_service.py.backup_* | head -1)
echo "Usando backup: $BACKUP_FILE"
cp "$BACKUP_FILE" services/glpi_service.py

# 3. Reiniciar serviços
echo "Reiniciando serviços..."
sudo systemctl start glpi-dashboard

# 4. Verificar saúde
echo "Verificando saúde do sistema..."
sleep 10
curl -f http://localhost:8000/health || echo "ERRO: Sistema não respondeu"

echo "=== ROLLBACK CONCLUÍDO ==="
echo "Verifique logs e métricas manualmente"
```

### 2. Checklist de Recuperação

```markdown
## Checklist de Recuperação de Incidente

### Detecção
- [ ] Identificar sintomas (métricas zeradas, erros, etc.)
- [ ] Verificar logs de erro recentes
- [ ] Identificar timestamp do problema
- [ ] Correlacionar com mudanças recentes

### Contenção
- [ ] Executar rollback se necessário
- [ ] Isolar sistema afetado
- [ ] Notificar stakeholders
- [ ] Documentar ações tomadas

### Investigação
- [ ] Analisar logs detalhadamente
- [ ] Identificar causa raiz
- [ ] Reproduzir problema em ambiente de teste
- [ ] Documentar descobertas

### Resolução
- [ ] Desenvolver correção
- [ ] Testar correção isoladamente
- [ ] Aplicar correção em produção
- [ ] Validar resolução

### Prevenção
- [ ] Atualizar documentação
- [ ] Criar/atualizar testes
- [ ] Revisar processos
- [ ] Implementar monitoramento adicional
```

## Conclusão

Este documento deve ser consultado SEMPRE antes de implementar mudanças no sistema GLPI Dashboard. O objetivo é evitar que vulnerabilidades sejam expostas por "melhorias" mal planejadas.

**Lembre-se**: É melhor ter um sistema funcionando com limitações conhecidas do que um sistema quebrado por uma "melhoria" mal implementada.

---

**Última atualização**: 30/08/2025  
**Próxima revisão**: Trimestral  
**Responsável**: Equipe de Desenvolvimento  
**Status**: Ativo e Obrigatório