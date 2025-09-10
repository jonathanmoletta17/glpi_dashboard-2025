# Registro de Componentes - GLPI Dashboard

## Componentes Ativos

### Dashboard Principal
- **ModernDashboard.tsx** - Dashboard principal com métricas e gráficos
- **DashboardLayout.tsx** - Layout base do dashboard
- **DashboardHeader.tsx** - Cabeçalho com navegação

### Tickets
- **ProfessionalTicketsList.tsx** ✅ **ATIVO** - Lista principal de tickets profissionais
- **TicketCard.tsx** - Card individual de ticket
- **TicketFilters.tsx** - Filtros para tickets
- **TicketMetrics.tsx** - Métricas de tickets

### Gráficos e Visualizações
- **TicketChart.tsx** - Gráfico de tickets
- **MetricsGrid.tsx** - Grid de métricas
- **ChartContainer.tsx** - Container para gráficos

### Componentes de UI
- **LoadingSkeleton.tsx** - Skeleton para carregamento
- **ErrorBoundary.tsx** - Tratamento de erros
- **Modal.tsx** - Modal genérico
- **Button.tsx** - Botão customizado

### Lazy Loading
- **LazyComponents.tsx** - Componentes com lazy loading

## Componentes Removidos/Deprecated

### ❌ Removidos em [Data da Remoção]
- **RecentTickets.tsx** - Substituído por ProfessionalTicketsList.tsx
  - **Motivo**: Funcionalidade duplicada
  - **Migração**: Usar ProfessionalTicketsList.tsx
  - **Removido em**: Janeiro 2025

- **NewTicketsList.tsx** - Não utilizado
  - **Motivo**: Código morto, sem referências
  - **Migração**: N/A
  - **Removido em**: Janeiro 2025

## Componentes em Análise

### 🔍 Para Revisão
- **CacheManager.tsx** - Verificar se está sendo utilizado
- **LevelMetricsGrid.tsx** - Analisar duplicação com MetricsGrid.tsx

## Diretrizes para Novos Componentes

### Antes de Criar
1. **Verificar se já existe** componente similar
2. **Consultar este registro** para evitar duplicações
3. **Executar auditoria**: `npm run audit:dead-code`
4. **Discutir com a equipe** se necessário

### Ao Criar
1. **Adicionar ao registro** imediatamente
2. **Documentar propósito** e casos de uso
3. **Definir responsável** pela manutenção
4. **Criar testes** adequados

### Nomenclatura
- **Use nomes específicos**: `ProfessionalTicketsList` vs `TicketsList`
- **Evite sufixos genéricos**: `NewList`, `OldTable`
- **Seja descritivo**: `UserProfileModal` vs `Modal`
- **Mantenha consistência**: `TicketCard`, `TicketList`, `TicketFilters`

## Processo de Deprecação

### 1. Marcação como Deprecated
```typescript
/**
 * @deprecated Use ProfessionalTicketsList instead
 * @see ProfessionalTicketsList.tsx
 */
export const RecentTickets = () => {
  // implementação
};
```

### 2. Atualização do Registro
- Mover para seção "Deprecated"
- Adicionar motivo da deprecação
- Indicar componente substituto
- Definir prazo para remoção

### 3. Comunicação
- Notificar equipe via PR
- Atualizar documentação
- Criar issues para migração

### 4. Remoção
- Aguardar período de transição (mínimo 1 sprint)
- Verificar ausência de referências
- Executar testes completos
- Remover arquivo e atualizar registro

## Responsabilidades

### Desenvolvedores
- **Consultar registro** antes de criar componentes
- **Atualizar registro** ao adicionar/remover componentes
- **Executar auditoria** regularmente
- **Reportar duplicações** encontradas

### Tech Lead
- **Revisar novos componentes** em PRs
- **Aprovar deprecações** e remoções
- **Manter registro atualizado**
- **Definir diretrizes** de arquitetura

### QA
- **Verificar funcionalidade** após remoções
- **Testar componentes novos** adequadamente
- **Reportar problemas** de duplicação

## Métricas de Qualidade

### Indicadores
- **Componentes ativos**: 15+
- **Componentes deprecated**: 0
- **Duplicações detectadas**: 0
- **Cobertura de testes**: 80%+

### Auditoria Mensal
- [ ] Executar `npm run audit:dead-code`
- [ ] Revisar componentes em análise
- [ ] Atualizar registro
- [ ] Reportar métricas

## Ferramentas de Apoio

### Scripts Disponíveis
```bash
# Auditoria completa
npm run audit:dead-code

# Buscar referências de componente
grep -r "ComponentName" src/

# Verificar imports não utilizados
npm run lint
```

### Extensões VS Code Recomendadas
- **TypeScript Importer** - Auto-import de componentes
- **Auto Rename Tag** - Renomear componentes
- **Bracket Pair Colorizer** - Melhor visualização
- **ES7+ React/Redux/React-Native snippets** - Snippets úteis

## Histórico de Mudanças

### Janeiro 2025
- ✅ Removido `RecentTickets.tsx` (duplicado)
- ✅ Removido `NewTicketsList.tsx` (não utilizado)
- ✅ Implementado sistema de auditoria
- ✅ Configurado ESLint para detecção

### Próximas Ações
- [ ] Analisar `CacheManager.tsx`
- [ ] Revisar `LevelMetricsGrid.tsx`
- [ ] Implementar testes automatizados
- [ ] Criar dashboard de métricas

---

**Última atualização**: Janeiro 2025
**Responsável**: Equipe de Desenvolvimento
**Próxima revisão**: Fevereiro 2025
