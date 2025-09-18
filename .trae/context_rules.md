# Context Rules - GLPI Dashboard

## Indexação de Contexto

### Prioridades de Indexação
1. **Alta Prioridade** - Sempre incluir no contexto:
   - `frontend/src/` - Código fonte React/TypeScript
- `backend/` - Código fonte Flask/Python
   - `frontend/package.json` - Dependências frontend
- `requirements.txt` - Dependências backend
   - `docs/BYTEROVER.md` - Documentação principal da arquitetura
   - `.trae/` - Configurações do Trae AI

2. **Média Prioridade** - Incluir quando relevante:
   - `docker-compose.yml` - Configuração de containers
- `frontend/tailwind.config.js` - Configuração do Tailwind
   - `frontend/vite.config.ts` - Configuração do Vite
   - `docs/` - Documentação geral
   - `monitoring/` - Configurações de monitoramento

3. **Baixa Prioridade** - Incluir apenas se especificamente solicitado:
   - `data/` - Dados de exemplo/teste
- `scripts/` - Scripts utilitários
   - Arquivos de log e temporários

### Contexto por Tipo de Tarefa

#### Desenvolvimento Frontend
- **Foco Principal**: `frontend/src/`
- **Arquivos de Configuração**: `package.json`, `tailwind.config.js`, `vite.config.ts`
- **Componentes UI**: Priorizar `src/components/`
- **Tipos TypeScript**: Incluir `src/types/`
- **Estilos**: Considerar classes Tailwind e componentes shadcn/ui

#### Desenvolvimento Backend
- **Foco Principal**: `backend/`
- **APIs**: Priorizar `backend/api/`
- **Serviços**: Incluir `backend/services/`
- **Configuração**: `backend/config/`
- **Schemas**: `backend/schemas/`
- **Testes**: `backend/tests/`

#### Debugging e Troubleshooting
- **Logs**: Incluir saídas de terminal relevantes
- **Configurações**: Docker, ambiente, dependências
- **Testes**: Resultados de testes e coverage
- **Monitoramento**: Métricas e alertas se disponíveis

#### Documentação e Arquitetura
- **Documentação Principal**: `docs/BYTEROVER.md`
- **Documentação Técnica**: `docs/`
- **READMEs**: Arquivos README em subprojetos
- **Configurações**: Arquivos de configuração relevantes

## Regras de Contexto Inteligente

### Detecção Automática de Escopo
1. **Quando mencionar "frontend"** → Incluir automaticamente:
   - `frontend/src/`
   - `package.json`
   - Configurações do Vite/Tailwind

2. **Quando mencionar "backend"** → Incluir automaticamente:
   - `backend/`
   - `requirements.txt`
   - Configurações Flask

3. **Quando mencionar "componente"** → Incluir automaticamente:
   - `src/components/`
   - Tipos TypeScript relacionados
   - Estilos Tailwind relevantes

4. **Quando mencionar "API"** → Incluir automaticamente:
   - `backend/api/`
   - `backend/schemas/`
   - Documentação de API

### Contexto de Dependências
- **React/TypeScript**: Sempre considerar tipos e interfaces
- **Flask/Python**: Incluir schemas e validações
- **Tailwind CSS**: Considerar configurações e classes customizadas
- **shadcn/ui**: Incluir componentes base e customizações

### Contexto de Arquivos Relacionados
- **Ao editar componente React**: Incluir tipos, hooks e estilos relacionados
- **Ao editar API Flask**: Incluir schemas, serviços e testes relacionados
- **Ao editar configuração**: Incluir arquivos de ambiente e documentação

## Otimizações de Performance

### Limitações de Contexto
- **Máximo de arquivos por contexto**: 50
- **Tamanho máximo por arquivo**: 10MB
- **Priorizar arquivos modificados recentemente**
- **Excluir arquivos binários e gerados automaticamente**

### Cache de Contexto
- **Reutilizar contexto para tarefas similares**
- **Atualizar cache quando arquivos são modificados**
- **Limpar cache periodicamente**

## Regras de Segurança

### Informações Sensíveis
- **NUNCA incluir**: Arquivos `.env` com credenciais reais
- **SEMPRE usar**: Arquivos `.env.example` como referência
- **Mascarar**: Chaves de API, senhas, tokens
- **Excluir**: Logs com informações pessoais

### Dados de Produção
- **Não incluir**: Dados reais de usuários
- **Usar apenas**: Dados de exemplo/teste
- **Anonimizar**: Qualquer informação identificável

## Contexto Específico do GLPI

### Terminologia GLPI
- **Tickets**: Chamados/solicitações
- **Técnicos**: Usuários responsáveis por resolver tickets
- **Solicitantes**: Usuários que abrem tickets
- **Categorias**: Classificação de tickets
- **Status**: Estado atual do ticket
- **Prioridade**: Urgência do ticket

### Estrutura de Dados GLPI
- **Tabelas principais**: tickets, users, categories, priorities
- **Relacionamentos**: tickets ↔ users, tickets ↔ categories
- **Campos importantes**: id, name, status, priority, date_creation

### Métricas e KPIs
- **Tempo de resolução**: Tempo médio para resolver tickets
- **Volume de tickets**: Quantidade por período
- **Distribuição por técnico**: Carga de trabalho
- **Satisfação**: Avaliações dos usuários
- **SLA**: Cumprimento de acordos de nível de serviço
