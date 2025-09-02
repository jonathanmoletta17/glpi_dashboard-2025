# Protocolo de Validação de Dados - GLPI Dashboard

## Objetivo
Estabelecer procedimentos obrigatórios para validação de dados antes de apresentar informações sobre técnicos, rankings e métricas do sistema GLPI.

## Princípios Fundamentais

### 🚫 NUNCA FAZER:
1. **Inventar ou assumir dados** sem validação
2. **Apresentar informações fictícias** como reais
3. **Usar dados de exemplo** como se fossem dados reais
4. **Fazer suposições** sobre performance ou rankings
5. **Confiar apenas em documentação** sem verificar a API

### ✅ SEMPRE FAZER:
1. **Validar com a API real** antes de apresentar qualquer dado
2. **Documentar a fonte** de cada informação
3. **Incluir timestamps** e correlation IDs quando disponíveis
4. **Verificar múltiplas vezes** dados críticos
5. **Marcar claramente** dados de exemplo vs dados reais

## Procedimentos de Validação

### 1. Validação de Dados de Técnicos

#### Checklist Obrigatório:
- [ ] Fazer requisição à API `/api/technicians/ranking`
- [ ] Verificar se o técnico existe no sistema
- [ ] Confirmar ID, nome e nível corretos
- [ ] Validar métricas de performance (tickets resolvidos, pendentes, tempo médio)
- [ ] Documentar posição real no ranking
- [ ] Registrar correlation ID da consulta

#### Comando de Validação:
```powershell
# Validação completa do ranking
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/technicians/ranking?limit=50" -Method GET -ContentType "application/json"
$data = $response.Content | ConvertFrom-Json

# Buscar técnico específico
$technician = $data.data | Where-Object { $_.id -eq "ID_DO_TECNICO" }
if ($technician) {
    Write-Host "Técnico encontrado: $($technician.name)"
    Write-Host "Posição: $($technician.rank)"
    Write-Host "Nível: $($technician.level)"
    Write-Host "Tickets resolvidos: $($technician.resolved_tickets)"
    Write-Host "Tickets pendentes: $($technician.pending_tickets)"
    Write-Host "Total: $($technician.total_tickets)"
} else {
    Write-Host "Técnico não encontrado!"
}
```

### 2. Validação de Métricas do Dashboard

#### Endpoints a Validar:
- `/api/dashboard/metrics` - Métricas gerais
- `/api/technicians/ranking` - Ranking de técnicos
- `/api/system/status` - Status do sistema

#### Processo:
1. Fazer requisições aos endpoints
2. Verificar códigos de resposta (200 OK)
3. Validar estrutura JSON
4. Confirmar dados com múltiplas consultas se necessário
5. Documentar timestamps e correlation IDs

### 3. Documentação de Validação

#### Template de Registro:
```markdown
## Validação de Dados - [DATA]

**Endpoint:** [URL_DA_API]
**Método:** [GET/POST/etc]
**Timestamp:** [YYYY-MM-DD HH:MM:SS]
**Correlation ID:** [ID_SE_DISPONIVEL]
**Status:** [SUCCESS/FAILED]

### Dados Validados:
- **Campo 1:** [VALOR_REAL]
- **Campo 2:** [VALOR_REAL]
- **Campo N:** [VALOR_REAL]

### Observações:
[NOTAS_ADICIONAIS]
```

## Casos de Uso Específicos

### Análise de Técnico Individual

1. **Identificação:**
   - Confirmar ID do técnico
   - Validar nome completo
   - Verificar se está ativo no sistema

2. **Performance:**
   - Consultar tickets resolvidos vs pendentes
   - Calcular taxa de resolução real
   - Verificar tempo médio de resolução

3. **Ranking:**
   - Confirmar posição atual no ranking
   - Verificar critérios de ordenação
   - Comparar com outros técnicos

### Relatórios de Ranking

1. **Dados Completos:**
   - Obter lista completa de técnicos
   - Verificar ordenação por critérios corretos
   - Confirmar métricas de cada posição

2. **Filtros:**
   - Testar filtros por nível (N1, N2, N3, N4)
   - Validar filtros por período
   - Confirmar filtros por entidade

## Ferramentas de Validação

### Scripts PowerShell
```powershell
# Função para validar técnico
function Validate-Technician {
    param(
        [string]$TechnicianId,
        [string]$BaseUrl = "http://localhost:5000"
    )
    
    try {
        $response = Invoke-WebRequest -Uri "$BaseUrl/api/technicians/ranking" -Method GET
        $data = $response.Content | ConvertFrom-Json
        
        $tech = $data.data | Where-Object { $_.id -eq $TechnicianId }
        
        if ($tech) {
            return @{
                Found = $true
                Data = $tech
                CorrelationId = $data.correlation_id
                Timestamp = Get-Date
            }
        } else {
            return @{
                Found = $false
                Message = "Técnico não encontrado"
                Timestamp = Get-Date
            }
        }
    } catch {
        return @{
            Found = $false
            Error = $_.Exception.Message
            Timestamp = Get-Date
        }
    }
}
```

## Responsabilidades

### Antes de Apresentar Dados:
1. **Executar validação completa**
2. **Documentar processo de validação**
3. **Confirmar dados com fonte primária (API)**
4. **Registrar evidências da validação**

### Em Caso de Inconsistências:
1. **Parar imediatamente** a apresentação de dados incorretos
2. **Investigar causa raiz** da inconsistência
3. **Corrigir dados** com informações validadas
4. **Documentar lições aprendidas**
5. **Atualizar protocolos** se necessário

## Auditoria e Melhoria Contínua

### Revisões Periódicas:
- **Semanal:** Verificar dados críticos
- **Mensal:** Revisar protocolos de validação
- **Trimestral:** Auditoria completa do processo

### Métricas de Qualidade:
- Taxa de dados validados vs não validados
- Número de inconsistências identificadas
- Tempo médio de validação
- Eficácia das correções aplicadas

---

**Versão:** 1.0  
**Data de Criação:** $(Get-Date -Format "yyyy-MM-dd")  
**Próxima Revisão:** $(Get-Date -Format "yyyy-MM-dd" -Date (Get-Date).AddMonths(1))  

**Nota:** Este protocolo deve ser seguido rigorosamente para garantir a integridade e confiabilidade dos dados apresentados.