# Guia de Prevenção de Inconsistências de Código

## Visão Geral

Este documento descreve as práticas e ferramentas implementadas para prevenir inconsistências de código, componentes duplicados e código morto no projeto GLPI Dashboard.

## Problemas Identificados

### Componentes Duplicados Encontrados
- `RecentTickets.tsx` - Removido (não utilizado)
- `NewTicketsList.tsx` - Removido (não utilizado)
- `ProfessionalTicketsList.tsx` - Mantido (ativo)

### Fatores que Permitiram a Duplicação
1. **Evolução incremental sem limpeza**: Componentes foram criados sem remover versões anteriores
2. **Ausência de ferramentas de detecção**: Não havia verificação automática de código morto
3. **Code review insuficiente**: Revisões não identificaram duplicações
4. **Documentação inadequada**: Falta de registro sobre componentes ativos vs deprecated

## Ferramentas Implementadas

### 1. ESLint Configurado

**Arquivo**: `.eslintrc.json`

**Regras principais**:
```json
{
  "unused-imports/no-unused-imports": "error",
  "@typescript-eslint/no-unused-vars": ["error", {
    "argsIgnorePattern": "^_",
    "varsIgnorePattern": "^_"
  }]
}
```

**Comandos**:
- `npm run lint` - Verifica problemas
- `npm run lint:fix` - Corrige automaticamente

### 2. Script de Auditoria Automática

**Arquivo**: `scripts/audit-dead-code.cjs`

**Funcionalidades**:
- Detecta arquivos não utilizados
- Identifica componentes duplicados por similaridade
- Verifica imports não referenciados
- Gera relatório detalhado

**Comando**: `npm run audit:dead-code`

### 3. Pre-commit Hooks

**Ferramentas**: Husky + lint-staged

**Configuração** (package.json):
```json
{
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ]
  }
}
```

**Execução automática**: A cada commit, o código é verificado e corrigido

## Comandos Disponíveis

### Verificação e Limpeza
```bash
# Auditoria completa de código morto
npm run audit:dead-code

# Limpeza automática (auditoria + lint fix)
npm run clean:unused

# Verificação de lint
npm run lint

# Correção automática de lint
npm run lint:fix

# Formatação de código
npm run format
```

### Verificação de Tipos
```bash
# Verificação TypeScript sem build
npm run type-check
```

## Processo de Prevenção

### Durante o Desenvolvimento
1. **Antes de criar novos componentes**:
   - Verificar se já existe componente similar
   - Executar `npm run audit:dead-code`
   - Consultar documentação de componentes

2. **Ao modificar componentes existentes**:
   - Verificar se há duplicações
   - Atualizar imports e exports
   - Executar `npm run lint:fix`

3. **Antes de commits**:
   - Pre-commit hooks executam automaticamente
   - Verificar saída do ESLint
   - Resolver warnings e errors

### Durante Code Review
1. **Verificar**:
   - Novos arquivos não duplicam funcionalidade
   - Imports são necessários
   - Componentes removidos não quebram build

2. **Solicitar**:
   - Execução de `npm run audit:dead-code`
   - Justificativa para novos componentes similares
   - Documentação de mudanças arquiteturais

## Métricas e Monitoramento

### Relatório de Auditoria
O script `audit-dead-code.cjs` gera relatórios com:
- Número de arquivos não utilizados
- Componentes potencialmente duplicados
- Imports não referenciados
- Recomendações de limpeza

### Indicadores de Qualidade
- **Zero warnings** no ESLint
- **Zero arquivos não utilizados** na auditoria
- **Build sem errors** no TypeScript
- **Testes passando** após limpeza

## Melhores Práticas

### Nomenclatura de Componentes
1. **Use nomes descritivos e únicos**
2. **Evite sufixos genéricos** como `List`, `Table` sem contexto
3. **Prefira especificidade** sobre generalização

### Organização de Arquivos
1. **Agrupe por funcionalidade**, não por tipo
2. **Use index.ts** para exports centralizados
3. **Documente componentes deprecated** antes da remoção

### Refatoração Segura
1. **Execute auditoria antes** de grandes mudanças
2. **Remova código morto incrementalmente**
3. **Teste após cada remoção**
4. **Documente mudanças arquiteturais**

## Troubleshooting

### ESLint Errors
```bash
# Se ESLint falhar, verificar configuração
npm run lint -- --debug

# Reinstalar dependências se necessário
npm install
```

### Script de Auditoria
```bash
# Se script falhar, verificar Node.js version
node --version

# Executar diretamente para debug
node scripts/audit-dead-code.cjs
```

### Pre-commit Hooks
```bash
# Se hooks não executarem
npm run prepare

# Verificar configuração git
git config core.hooksPath
```

## Roadmap de Melhorias

### Curto Prazo
- [ ] Integrar auditoria no CI/CD
- [ ] Criar dashboard de métricas
- [ ] Automatizar remoção de código morto

### Médio Prazo
- [ ] Implementar análise de dependências
- [ ] Criar registro de componentes
- [ ] Adicionar testes de regressão

### Longo Prazo
- [ ] Integrar com ferramentas de monitoramento
- [ ] Criar alertas proativos
- [ ] Implementar análise de performance

## Conclusão

A implementação dessas ferramentas e práticas garante:
1. **Detecção precoce** de inconsistências
2. **Prevenção automática** de código morto
3. **Manutenção simplificada** do codebase
4. **Qualidade consistente** do código

Para dúvidas ou sugestões, consulte a equipe de desenvolvimento.
