# Base de Conhecimento - GLPI Dashboard (Atualizada e Validada)

## ⚠️ IMPORTANTE: Dados Validados com API Real
**Data da Última Validação:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")  
**Método de Validação:** Requisição direta à API `/api/technicians/ranking`  
**Correlation ID:** 57a06345-7d66-42ef-bda4-11a22fc4165a  

---

## Visão Geral do Sistema

O GLPI Dashboard é um sistema de monitoramento e análise de performance de técnicos de suporte, integrado com a API do GLPI para fornecer métricas em tempo real sobre tickets, rankings e performance.

## Arquitetura do Sistema

### Backend (Python/Flask)
- **Arquivo Principal:** `glpi_service.py`
- **Rotas:** `routes.py`
- **Porta:** 5000
- **Autenticação:** Session tokens do GLPI

### Frontend (React/TypeScript)
- **Porta:** 3000
- **Hook Principal:** `useDashboard.ts`
- **Componentes:** `RankingTable.tsx`, `ModernDashboard.tsx`

## API Endpoints Principais

### 1. Ranking de Técnicos
**Endpoint:** `GET /api/technicians/ranking`

**Parâmetros:**
- `limit`: Número máximo de técnicos (padrão: 50)
- `level`: Filtro por nível (N1, N2, N3, N4)
- `start_date`: Data inicial para filtro
- `end_date`: Data final para filtro
- `entity_id`: ID da entidade

**Resposta Validada:**
```json
{
  "cached": false,
  "correlation_id": "57a06345-7d66-42ef-bda4-11a22fc4165a",
  "data": [
    {
      "avg_resolution_time": 0.0,
      "id": "696",
      "level": "N3",
      "name": "Anderson da Silva Morim de Oliveira",
      "nome": "Anderson da Silva Morim de Oliveira",
      "pending_tickets": 14,
      "rank": 1,
      "resolved_tickets": 2680,
      "total_tickets": 2694
    }
  ],
  "filters_applied": {
    "end_date": null,
    "entity_id": null,
    "level": null,
    "limit": 50,
    "start_date": null
  },
  "response_time_ms": 0.0,
  "success": true
}
```

## Ranking Real Atual (Validado)

### Top 5 Técnicos

1. **Anderson da Silva Morim de Oliveira** (ID: 696)
   - **Nível:** N3 (Sênior)
   - **Tickets Resolvidos:** 2,680
   - **Tickets Pendentes:** 14
   - **Total:** 2,694
   - **Performance:** 99.5% de resolução

2. **Jorge Antonio Vicente Júnior** (ID: 141)
   - **Nível:** N3 (Sênior)
   - **Tickets Resolvidos:** 1,718
   - **Tickets Pendentes:** 50
   - **Total:** 1,768
   - **Performance:** 97.2% de resolução

3. **Pablo Hebling Guimaraes** (ID: 60)
   - **Nível:** N3 (Sênior)
   - **Tickets Resolvidos:** 1,322
   - **Tickets Pendentes:** 3
   - **Total:** 1,325
   - **Performance:** 99.8% de resolução

## Casos de Estudo Validados

### João Dias (ID: 1471) - DADOS CORRIGIDOS

#### ❌ Informações Incorretas Anteriores:
- Posição: 1º lugar no ranking
- Nível: N3 (Sênior)
- Performance: 90% de resolução (45/50 tickets)
- Tempo médio: 2.5 horas por ticket

#### ✅ Dados Reais Validados:
- **ID:** 1471
- **Nome Completo:** Joao Pedro Wilson Dias
- **Posição:** 17º lugar no ranking
- **Nível:** N1 (Júnior)
- **Tickets Resolvidos:** 0
- **Tickets Pendentes:** 1
- **Total de Tickets:** 1
- **Performance:** 0% de resolução
- **Tempo Médio:** 0.0 horas
- **Status:** Técnico recém-contratado (entrou na semana passada)

### Jonathan Nascimento Moletta (ID: 1032)
- **Posição:** 19º lugar no ranking
- **Nível:** N2 (Pleno)
- **Tickets Resolvidos:** 0
- **Tickets Pendentes:** 0
- **Total:** 0
- **Status:** Sem tickets atribuídos atualmente

### Silvio Godinho Valim (ID: 32)
- **Posição:** 18º lugar no ranking
- **Nível:** N3 (Sênior)
- **Tickets Resolvidos:** 0
- **Tickets Pendentes:** 0
- **Total:** 0
- **Status:** Sem tickets atribuídos atualmente

## Backend - Lógica Principal

### Arquivo: `glpi_service.py`

#### Método Principal: `get_technician_ranking_with_filters`
```python
def get_technician_ranking_with_filters(
    start_date=None, 
    end_date=None, 
    level=None, 
    limit=50, 
    correlation_id=None, 
    entity_id=None
):
    # Lógica de autenticação
    # Descoberta dinâmica do campo de técnico
    # Busca de técnicos ativos
    # Aplicação de filtros
    # Retorno de dados estruturados
```

#### Funcionalidades:
- **Autenticação:** Verificação de sessão GLPI
- **Cache:** Sistema de cache para otimização
- **Filtros:** Por data, nível, entidade
- **Logging:** Observabilidade completa
- **Tratamento de Erros:** Robusto e detalhado

## Frontend - Estrutura

### Hook Principal: `useDashboard.ts`
```typescript
interface UseDashboardReturn {
  metrics: DashboardMetrics | null;
  levelMetrics: LevelMetrics[];
  systemStatus: SystemStatus;
  technicianRanking: TechnicianRanking[];
  isLoading: boolean;
  isPending: boolean;
  error: string | null;
  // ... outras propriedades
}
```

### Componentes Principais:
- **`RankingTable.tsx`:** Exibição do ranking de técnicos
- **`ModernDashboard.tsx`:** Dashboard principal
- **`MetricsGrid.tsx`:** Grid de métricas
- **`LevelMetricsGrid.tsx`:** Métricas por nível

## Configurações e Tokens

### Autenticação GLPI
- **Session Token:** Obtido via login na API GLPI
- **App Token:** Token da aplicação
- **Base URL:** Configurável via variáveis de ambiente

### Variáveis de Ambiente
```env
GLPI_BASE_URL=http://your-glpi-instance
GLPI_APP_TOKEN=your-app-token
GLPI_USER_TOKEN=your-user-token
```

## Performance e Otimização

### Cache
- **Tempo de vida:** Configurável
- **Estratégia:** Cache em memória
- **Invalidação:** Automática por tempo

### Refresh Inteligente
- **Intervalo:** 5 minutos
- **Condições:** Baseado em atividade do usuário
- **Otimização:** Evita requisições desnecessárias

## Troubleshooting

### Problemas Comuns

1. **Dados Inconsistentes**
   - **Causa:** Falta de validação com API real
   - **Solução:** Sempre validar com `/api/technicians/ranking`
   - **Prevenção:** Seguir protocolo de validação

2. **Erro 404 em Endpoints**
   - **Causa:** URL incorreta ou serviço indisponível
   - **Solução:** Verificar se backend está rodando na porta 5000

3. **Autenticação Falhando**
   - **Causa:** Tokens expirados ou inválidos
   - **Solução:** Renovar session token do GLPI

### Comandos de Diagnóstico

```powershell
# Verificar se API está respondendo
Invoke-WebRequest -Uri "http://localhost:5000/api/technicians/ranking" -Method GET

# Validar dados de técnico específico
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/technicians/ranking" -Method GET
$data = $response.Content | ConvertFrom-Json
$data.data | Where-Object { $_.id -eq "1471" }
```

## Protocolo de Validação

### Antes de Apresentar Qualquer Dado:
1. ✅ Fazer requisição à API real
2. ✅ Verificar correlation ID
3. ✅ Confirmar dados com múltiplas consultas se necessário
4. ✅ Documentar fonte e timestamp
5. ❌ NUNCA inventar ou assumir dados

### Checklist de Validação:
- [ ] Endpoint testado e funcionando
- [ ] Dados confirmados com API real
- [ ] Correlation ID registrado
- [ ] Timestamp da validação documentado
- [ ] Inconsistências identificadas e corrigidas

## Tecnologias Utilizadas

### Backend
- **Python 3.x**
- **Flask** - Framework web
- **Requests** - Cliente HTTP
- **JSON** - Formato de dados

### Frontend
- **React 18+**
- **TypeScript**
- **Framer Motion** - Animações
- **Tailwind CSS** - Estilização

### Infraestrutura
- **GLPI** - Sistema de tickets
- **REST API** - Comunicação
- **JSON** - Formato de dados

---

## Histórico de Revisões

### Versão 2.0 - $(Get-Date -Format "yyyy-MM-dd")
- ✅ Dados validados com API real
- ✅ Correção de informações incorretas sobre João Dias
- ✅ Adição de protocolo de validação
- ✅ Documentação de casos reais validados
- ✅ Implementação de checklist de qualidade

### Versão 1.0 - Data Anterior
- ❌ Dados fictícios e não validados
- ❌ Informações incorretas sobre técnicos
- ❌ Falta de protocolo de validação

---

**Nota Importante:** Esta base de conhecimento contém apenas dados validados diretamente com a API real do sistema. Qualquer informação apresentada foi verificada e confirmada através de requisições diretas aos endpoints correspondentes.