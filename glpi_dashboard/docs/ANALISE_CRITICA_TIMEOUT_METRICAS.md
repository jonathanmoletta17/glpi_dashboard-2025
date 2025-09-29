# Análise Crítica: Problemas de Timeout e Inconsistência de Métricas - GLPI Dashboard

## 📋 Resumo Executivo

Este documento apresenta uma análise completa dos problemas críticos identificados no sistema GLPI Dashboard, especificamente:

1. **Timeout de 5000ms na primeira renderização** do dashboard
2. **Métricas zeradas/inconsistentes no ranking de técnicos**
3. **Diferenças de performance entre app.py e asgi.py**

A análise foi realizada através de auditoria completa do código, configurações e arquitetura do sistema.

---

## 🎯 Objetivo do Documento

Este documento serve como **guia instrutivo completo** para correção dos problemas identificados. Ele deve ser usado por desenvolvedores ou sistemas de IA para:

- Entender exatamente onde estão os problemas
- Implementar as correções necessárias
- Validar que as correções foram aplicadas corretamente
- Garantir que o sistema funcione de forma consistente

---

## 🔍 Problemas Identificados

### 1. **PROBLEMA CRÍTICO: Configurações de Timeout Inconsistentes**

#### Localização dos Problemas:
- **Arquivo**: `glpi_dashboard/backend/config/settings.py` (linha 130-139)
- **Arquivo**: `glpi_dashboard/docker.env` (linha 25)
- **Arquivo**: `glpi_dashboard/backend/services/glpi_service.py` (múltiplas linhas)

#### Descrição Detalhada:
O sistema possui **múltiplas configurações de timeout conflitantes**:

```python
# CONFLITO 1: settings.py define 30s como padrão
API_TIMEOUT = 30

# CONFLITO 2: docker.env define 120s
API_TIMEOUT=120

# CONFLITO 3: Código hardcoded com valores diferentes
timeout=8   # Para métricas de técnicos
timeout=10  # Para descoberta de campos
timeout=30  # Para processamento paralelo
timeout=60  # Para consultas complexas
```

#### Impacto:
- Primeira requisição falha por timeout inconsistente
- Sistema não sabe qual timeout usar
- Comportamento imprevisível entre ambientes

#### Correção Necessária:
```python
# 1. Padronizar timeout em settings.py para 60s
@property
def API_TIMEOUT(self) -> int:
    try:
        timeout = self._get_config_value("glpi.timeout", 60, "API_TIMEOUT")
        timeout = int(timeout)
        if not (10 <= timeout <= 300):
            raise ValueError(f"Timeout deve estar entre 10 e 300 segundos: {timeout}")
        return timeout
    except (ValueError, TypeError) as e:
        raise ConfigValidationError(f"Erro na configuração API_TIMEOUT: {e}")

# 2. Atualizar docker.env
API_TIMEOUT=90

# 3. Remover timeouts hardcoded e usar configuração centralizada
```

---

### 2. **PROBLEMA CRÍTICO: Cache Corrompido no Ranking de Técnicos**

#### Localização do Problema:
- **Arquivo**: `glpi_dashboard/backend/services/glpi_service.py`
- **Método**: `get_technician_ranking()` (linhas 3588-3725)
- **Linha Crítica**: 3603

#### Descrição Detalhada:
O método `get_technician_ranking()` possui uma **lógica de cache defeituosa**:

```python
# PROBLEMA: Limpa cache interno FORÇADAMENTE a cada chamada
self._cache.clear()  # Linha 3603

# PROBLEMA: Depois tenta usar o cache que acabou de limpar
cached_data = self._get_cache_data(cache_key)  # Linha 3630
if cached_data is not None:
    return cached_data  # Retorna cache vazio/antigo
```

#### Impacto:
- Técnicos aparecem com métricas zeradas (valores "-")
- Comportamento aleatório entre recarregamentos
- Cache nunca funciona efetivamente

#### Correção Necessária:
```python
def get_technician_ranking(self, limit: int = None) -> list:
    # REMOVER completamente a linha que limpa o cache
    # self._cache.clear()  # COMENTAR OU REMOVER ESTA LINHA

    # Implementar verificação inteligente de cache
    cache_key = f"technician_ranking_{limit or 'all'}"
    cached_data = self._get_cache_data(cache_key)

    # Verificar se cache existe E não está vazio
    if cached_data and isinstance(cached_data, list) and len(cached_data) > 0:
        self.logger.info(f"Retornando ranking do cache: {len(cached_data)} técnicos")
        return cached_data[:limit] if limit else cached_data

    # ... resto do processamento ...

    # Salvar no cache APÓS processar
    if ranking:
        self._set_cache_data(cache_key, ranking, ttl=300)  # 5 minutos
```

---

### 3. **PROBLEMA DE ARQUITETURA: Flask vs Uvicorn**

#### Localização dos Problemas:
- **Arquivo**: `glpi_dashboard/backend/app.py` (linha 244)
- **Arquivo**: `glpi_dashboard/backend/asgi.py` (linha 15)
- **Arquivo**: `glpi_dashboard/backend/Dockerfile` (linha 45)

#### Descrição Detalhada:
O sistema tem **duas formas de execução** com performance muito diferente:

```python
# MÉTODO 1: Flask (app.py) - Processamento SEQUENCIAL
app.run(host=server_config["host"], port=server_config["port"], debug=server_config["debug"])

# MÉTODO 2: Uvicorn (asgi.py) - Processamento ASSÍNCRONO
uvicorn.run("asgi:asgi_app", host="0.0.0.0", port=8000, reload=True)
```

#### Impacto:
- Flask processa uma requisição por vez (lento)
- Uvicorn processa múltiplas requisições simultaneamente (rápido)
- Docker usa Flask por padrão (problemático)

#### Correção Necessária:
```dockerfile
# Dockerfile - Mudar comando padrão
# ANTES:
CMD ["python", "app.py"]

# DEPOIS:
CMD ["uvicorn", "asgi:asgi_app", "--host", "0.0.0.0", "--port", "5000", "--workers", "4"]
```

---

### 4. **PROBLEMA DE RECURSOS: Limitações Docker**

#### Localização do Problema:
- **Arquivo**: `glpi_dashboard/docker-compose.yml` (linhas 70-77)

#### Descrição Detalhada:
Recursos Docker **insuficientes** para o processamento:

```yaml
# RECURSOS ATUAIS (INSUFICIENTES)
deploy:
  resources:
    limits:
      memory: 512M    # Muito pouco
      cpus: '1.0'     # Muito pouco
    reservations:
      memory: 256M    # Muito pouco
      cpus: '0.5'     # Muito pouco
```

#### Impacto:
- Sistema trava por falta de memória
- Processamento lento por CPU limitada
- Timeouts frequentes

#### Correção Necessária:
```yaml
# RECURSOS OTIMIZADOS
deploy:
  resources:
    limits:
      memory: 1G      # Aumentar para 1GB
      cpus: '2.0'     # Aumentar para 2 cores
    reservations:
      memory: 512M    # Aumentar para 512MB
      cpus: '1.0'     # Aumentar para 1 core
```

---

### 5. **PROBLEMA DE CONCORRÊNCIA: Timeouts Inadequados**

#### Localização do Problema:
- **Arquivo**: `glpi_dashboard/backend/services/glpi_service.py`
- **Método**: `_get_technician_ranking_knowledge_base()` (linhas 4080-4143)

#### Descrição Detalhada:
Processamento paralelo com **timeouts muito baixos**:

```python
# PROBLEMA: Timeout muito baixo para processamento paralelo
result = future.result(timeout=30)  # 30s por técnico - MUITO BAIXO

# PROBLEMA: Timeouts inconsistentes
metricas = metrics_future.result(timeout=30)  # 30s
tech_level = level_future.result(timeout=30)  # 30s
```

#### Impacto:
- Técnicos não processados completamente
- Métricas zeradas por timeout
- Comportamento inconsistente

#### Correção Necessária:
```python
# Aumentar timeouts para processamento paralelo
result = future.result(timeout=60)  # Mudança: 30 -> 60

# Timeouts consistentes
metricas = metrics_future.result(timeout=60)  # Mudança: 30 -> 60
tech_level = level_future.result(timeout=60)  # Mudança: 30 -> 60
```

---

## 🛠️ Plano de Correção Detalhado

### **FASE 1: Correções Críticas (PRIORIDADE MÁXIMA)**

#### 1.1 Corrigir Configurações de Timeout
**Arquivo**: `glpi_dashboard/backend/config/settings.py`
```python
# Localizar linha 130-139 e substituir por:
@property
def API_TIMEOUT(self) -> int:
    """Timeout da API com validação"""
    try:
        timeout = self._get_config_value("glpi.timeout", 60, "API_TIMEOUT")  # Mudança: 30 -> 60
        timeout = int(timeout)
        if not (10 <= timeout <= 300):  # Mudança: 1-300 -> 10-300
            raise ValueError(f"Timeout deve estar entre 10 e 300 segundos: {timeout}")
        return timeout
    except (ValueError, TypeError) as e:
        raise ConfigValidationError(f"Erro na configuração API_TIMEOUT: {e}")
```

**Arquivo**: `glpi_dashboard/docker.env`
```bash
# Localizar linha 25 e alterar para:
API_TIMEOUT=90
```

#### 1.2 Corrigir Cache do Ranking
**Arquivo**: `glpi_dashboard/backend/services/glpi_service.py`
```python
# Localizar método get_technician_ranking() (linha 3588)
# COMENTAR ou REMOVER a linha 3603:
# self._cache.clear()  # REMOVER ESTA LINHA

# Substituir lógica de cache (linhas 3627-3640) por:
cache_key = f"technician_ranking_{limit or 'all'}"
cached_data = self._get_cache_data(cache_key)

if cached_data and isinstance(cached_data, list) and len(cached_data) > 0:
    self.logger.info(f"Retornando ranking do cache: {len(cached_data)} técnicos")
    return cached_data[:limit] if limit else cached_data
```

#### 1.3 Migrar para Uvicorn
**Arquivo**: `glpi_dashboard/backend/Dockerfile`
```dockerfile
# Localizar linha 45 e substituir por:
CMD ["uvicorn", "asgi:asgi_app", "--host", "0.0.0.0", "--port", "5000", "--workers", "4"]
```

### **FASE 2: Otimizações de Performance**

#### 2.1 Aumentar Recursos Docker
**Arquivo**: `glpi_dashboard/docker-compose.yml`
```yaml
# Localizar seção backend (linhas 70-77) e substituir por:
deploy:
  resources:
    limits:
      memory: 1G      # Aumentar de 512M
      cpus: '2.0'     # Aumentar de 1.0
    reservations:
      memory: 512M    # Aumentar de 256M
      cpus: '1.0'     # Aumentar de 0.5
```

#### 2.2 Corrigir Timeouts de Concorrência
**Arquivo**: `glpi_dashboard/backend/services/glpi_service.py`
```python
# Localizar linha 4087 e alterar:
result = future.result(timeout=60)  # Mudança: 30 -> 60

# Localizar linhas 4115-4116 e alterar:
metricas = metrics_future.result(timeout=60)  # Mudança: 30 -> 60
tech_level = level_future.result(timeout=60)  # Mudança: 30 -> 60
```

#### 2.3 Melhorar Healthcheck
**Arquivo**: `glpi_dashboard/backend/Dockerfile`
```dockerfile
# Localizar linha 41-42 e substituir por:
HEALTHCHECK --interval=30s --timeout=60s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:5000/health || exit 1
```

### **FASE 3: Validações e Testes**

#### 3.1 Teste de Timeout
```bash
# Executar teste de timeout
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:5000/api/metrics"
```

#### 3.2 Teste de Ranking
```bash
# Executar teste de ranking
curl "http://localhost:5000/api/technicians/ranking" | jq '.data | length'
```

#### 3.3 Teste de Consistência
```bash
# Executar múltiplas vezes para verificar consistência
for i in {1..5}; do
  echo "Teste $i:"
  curl -s "http://localhost:5000/api/technicians/ranking" | jq '.data[0:3] | .[] | {name: .name, total: .total_tickets, resolved: .resolved_tickets}'
  sleep 2
done
```

---

## ✅ Checklist de Validação

### **Validação de Correções Implementadas**

#### 1. Configurações de Timeout
- [ ] `settings.py` tem timeout padrão de 60s
- [ ] `docker.env` tem timeout de 90s
- [ ] Não há timeouts hardcoded < 30s no código

#### 2. Cache do Ranking
- [ ] Linha `self._cache.clear()` foi removida/comentada
- [ ] Cache verifica se dados existem e não estão vazios
- [ ] Cache é salvo APÓS processamento, não antes

#### 3. Migração para Uvicorn
- [ ] Dockerfile usa comando uvicorn
- [ ] 4 workers configurados
- [ ] Porta 5000 mantida

#### 4. Recursos Docker
- [ ] Memória limitada para 1GB
- [ ] CPU limitada para 2 cores
- [ ] Reservas aumentadas adequadamente

#### 5. Timeouts de Concorrência
- [ ] Processamento paralelo usa timeout de 60s
- [ ] Métricas usam timeout de 60s
- [ ] Níveis usam timeout de 60s

### **Validação de Funcionamento**

#### 1. Teste de Performance
- [ ] Primeira renderização < 2 segundos
- [ ] Ranking carrega em < 3 segundos
- [ ] Zero timeouts de 5000ms

#### 2. Teste de Consistência
- [ ] Métricas de técnicos consistentes entre recarregamentos
- [ ] Zero valores "-" no ranking
- [ ] Cache funciona corretamente

#### 3. Teste de Estresse
- [ ] 10 usuários simultâneos funcionam
- [ ] Sistema não trava
- [ ] Recuperação automática de falhas

---

## 🚨 Pontos de Atenção Críticos

### **1. Ordem de Implementação**
**IMPORTANTE**: Implementar as correções na ordem exata:
1. Primeiro: Configurações de timeout
2. Segundo: Cache do ranking
3. Terceiro: Migração para Uvicorn
4. Quarto: Recursos Docker
5. Quinto: Validações

### **2. Backup Antes das Mudanças**
```bash
# Criar backup antes de qualquer alteração
cp -r glpi_dashboard glpi_dashboard_backup_$(date +%Y%m%d_%H%M%S)
```

### **3. Teste Incremental**
- Testar cada correção individualmente
- Não implementar todas as correções de uma vez
- Validar funcionamento após cada mudança

### **4. Monitoramento Pós-Implementação**
- Verificar logs para erros
- Monitorar uso de memória e CPU
- Validar métricas de performance

---

## 📊 Métricas de Sucesso

### **Antes das Correções (Estado Atual)**
- ❌ Timeout de 5000ms na primeira renderização
- ❌ Métricas zeradas no ranking (valores "-")
- ❌ Comportamento inconsistente entre recarregamentos
- ❌ Performance lenta com Flask

### **Após as Correções (Estado Esperado)**
- ✅ Primeira renderização < 2 segundos
- ✅ 100% das métricas carregadas corretamente
- ✅ Comportamento consistente entre recarregamentos
- ✅ Performance otimizada com Uvicorn

---

## 🔧 Comandos de Validação Rápida

### **Verificar Configurações Atuais**
```bash
# Verificar timeout configurado
grep -r "API_TIMEOUT" glpi_dashboard/backend/config/
grep -r "API_TIMEOUT" glpi_dashboard/docker.env

# Verificar comando Docker
grep "CMD" glpi_dashboard/backend/Dockerfile

# Verificar recursos Docker
grep -A 10 "resources:" glpi_dashboard/docker-compose.yml
```

### **Verificar Cache do Ranking**
```bash
# Verificar se cache.clear() foi removido
grep -n "cache.clear()" glpi_dashboard/backend/services/glpi_service.py

# Verificar lógica de cache
grep -A 5 -B 5 "cached_data" glpi_dashboard/backend/services/glpi_service.py
```

### **Testar Performance**
```bash
# Teste de timeout
time curl -s "http://localhost:5000/api/metrics" > /dev/null

# Teste de ranking
time curl -s "http://localhost:5000/api/technicians/ranking" > /dev/null
```

---

## 📝 Notas Finais

Este documento foi criado com base em análise detalhada do código fonte e configurações do sistema GLPI Dashboard. Todas as correções propostas foram testadas conceitualmente e são baseadas em melhores práticas de desenvolvimento.

**IMPORTANTE**: Este documento deve ser usado como guia completo para correção dos problemas identificados. Cada seção contém informações específicas sobre localização, correção e validação dos problemas.

**RESPONSABILIDADE**: O desenvolvedor ou sistema de IA que implementar estas correções deve validar cada ponto do checklist antes de considerar a implementação completa.

---

**Data de Criação**: $(date)
**Versão**: 1.0
**Status**: Pronto para Implementação
**Prioridade**: CRÍTICA
