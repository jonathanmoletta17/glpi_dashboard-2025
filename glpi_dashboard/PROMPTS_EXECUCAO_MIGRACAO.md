# Cadeia de Prompts Executáveis - Migração CSS para Shadcn UI

## 📋 Visão Geral

Este documento contém uma sequência de prompts executáveis para migrar o dashboard GLPI das classes CSS personalizadas para o padrão Shadcn UI + Tailwind CSS, seguindo o plano de migração incremental estabelecido.

## 🎯 Objetivos

- ✅ Migração segura e incremental
- ✅ Preservação da funcionalidade existente
- ✅ Validação contínua através de testes
- ✅ Rollback seguro em caso de problemas

---

## 🚀 FASE 1: Preparação e Validação Inicial

### Prompt 1.1: Executar Baseline de Testes
```bash
# Execute este comando para estabelecer a baseline de testes
npm test

# Verifique se todos os testes passam antes de continuar
# Se algum teste falhar, corrija antes de prosseguir
```

### Prompt 1.2: Backup do Estado Atual
```bash
# Crie um backup do estado atual
git add .
git commit -m "feat: backup antes da migração CSS para Shadcn UI"
git tag "pre-shadcn-migration-$(date +%Y%m%d-%H%M%S)"
```

---

## 🔄 FASE 2: Migração do Componente LevelsSection

### Prompt 2.1: Migrar LevelsSection para Shadcn Card
```typescript
// Substitua o conteúdo do arquivo src/components/LevelsSection.tsx
// Migre de 'card-base' para componentes Shadcn Card
// Mantenha toda a lógica de cálculo existente
// Use: Card, CardHeader, CardTitle, CardContent do Shadcn UI

// IMPORTANTE: Preserve estas funcionalidades:
// - Cálculo de taxa de resolução
// - Grid responsivo (col-span-3 md:col-span-6 lg:col-span-3)
// - Animações e transições existentes
// - Estrutura de dados (LevelMetrics)
```

### Prompt 2.2: Atualizar Classes de Status
```typescript
// No arquivo migrado, substitua as classes de status:
// status-new → text-blue-600 dark:text-blue-400
// status-progress → text-yellow-600 dark:text-yellow-400  
// status-pending → text-orange-600 dark:text-orange-400
// status-resolved → text-green-600 dark:text-green-400
// bg-status-resolved → bg-green-500
```

### Prompt 2.3: Validar Migração do LevelsSection
```bash
# Execute os testes de regressão visual
npm test visual-regression

# Execute todos os testes
npm test

# Inicie o servidor de desenvolvimento para validação visual
npm run dev

# Acesse http://localhost:3001 e verifique:
# - Layout dos cards de nível mantido
# - Cores dos status preservadas
# - Responsividade funcionando
# - Barras de progresso corretas
```

---

## 🎨 FASE 3: Migração das Classes de Tipografia

### Prompt 3.1: Migrar Classes de Texto
```typescript
// Substitua em todos os arquivos .tsx:
// text-h1 → text-2xl font-bold text-gray-900 dark:text-gray-100
// text-h2 → text-xl font-semibold text-gray-800 dark:text-gray-200
// text-h3 → text-lg font-medium text-gray-700 dark:text-gray-300
// text-body → text-sm text-gray-600 dark:text-gray-400
// text-meta → text-xs text-gray-500 dark:text-gray-500
// text-numeric → text-2xl font-bold

// Use busca e substituição global nos arquivos:
// - src/components/LevelsSection.tsx
// - src/components/MetricCard.tsx
// - src/components/TicketCard.tsx
// - src/components/ProfessionalDashboard.tsx
```

### Prompt 3.2: Migrar Classes de Cor
```typescript
// Substitua as classes de cor:
// text-primary → text-gray-900 dark:text-gray-100
// text-secondary → text-gray-600 dark:text-gray-400
// text-muted → text-gray-500 dark:text-gray-500
```

### Prompt 3.3: Validar Migração de Tipografia
```bash
# Execute validação completa
npm test
npm run type-check
npm run lint

# Teste visual no navegador
npm run dev
```

---

## 📦 FASE 4: Migração das Classes de Layout

### Prompt 4.1: Migrar Grid Container
```typescript
// Substitua em todos os componentes:
// grid-container → w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8

// Mantenha a estrutura de grid interna:
// grid grid-cols-12 gap-4
```

### Prompt 4.2: Migrar Card Base
```typescript
// Substitua card-base por componente Shadcn Card:
// card-base → <Card className="bg-white dark:bg-gray-800 shadow-sm border border-gray-200 dark:border-gray-700">

// Estruture o conteúdo com:
// <CardHeader> para cabeçalhos
// <CardContent> para conteúdo principal
// <CardFooter> se necessário
```

### Prompt 4.3: Validar Layout
```bash
# Validação completa do layout
npm test visual-regression
npm run dev

# Verifique:
# - Espaçamento mantido
# - Responsividade preservada
# - Sombras e bordas corretas
```

---

## 🧹 FASE 5: Limpeza do CSS Legacy

### Prompt 5.1: Remover Classes CSS Não Utilizadas
```css
/* No arquivo src/index.css, remova as seguintes seções:

1. Classes de tipografia personalizadas:
   - .text-h1, .text-h2, .text-h3
   - .text-body, .text-meta, .text-numeric

2. Classes de cor personalizadas:
   - .text-primary, .text-secondary, .text-muted

3. Classes de status personalizadas:
   - .status-new, .status-progress, .status-pending, .status-resolved
   - .bg-status-resolved

4. Classes de layout personalizadas:
   - .grid-container, .card-base

⚠️ IMPORTANTE: Remova APENAS após confirmar que não há mais referências
*/
```

### Prompt 5.2: Verificar Referências Restantes
```bash
# Busque por referências restantes das classes removidas
grep -r "text-h[1-3]" src/
grep -r "text-body\|text-meta\|text-numeric" src/
grep -r "text-primary\|text-secondary\|text-muted" src/
grep -r "status-" src/
grep -r "grid-container\|card-base" src/

# Se encontrar referências, migre-as antes de remover do CSS
```

### Prompt 5.3: Validação Final da Limpeza
```bash
# Teste completo após limpeza
npm test
npm run build
npm run dev

# Verifique se não há:
# - Estilos quebrados
# - Elementos sem estilo
# - Erros de console
```

---

## ✅ FASE 6: Validação Final e Documentação

### Prompt 6.1: Teste de Regressão Completo
```bash
# Execute suite completa de testes
npm run test:ci
npm run type-check
npm run lint
npm run build

# Teste manual:
# 1. Navegue por todas as páginas
# 2. Teste responsividade (mobile, tablet, desktop)
# 3. Teste modo escuro/claro se aplicável
# 4. Verifique performance (sem degradação)
```

### Prompt 6.2: Commit da Migração
```bash
# Commit das mudanças
git add .
git commit -m "feat: migração completa para Shadcn UI + Tailwind CSS

- Migrou LevelsSection para componentes Shadcn Card
- Substituiu classes de tipografia personalizadas por Tailwind
- Removeu classes CSS legacy não utilizadas
- Manteve funcionalidade e responsividade
- Todos os testes passando"

git tag "shadcn-migration-complete-$(date +%Y%m%d-%H%M%S)"
```

### Prompt 6.3: Atualizar Documentação
```markdown
# Atualize o README.md com:
# - Novas convenções de CSS (Shadcn UI + Tailwind)
# - Remoção de referências às classes legacy
# - Instruções para novos componentes
# - Guia de contribuição atualizado
```

---

## 🚨 Plano de Rollback

### Em Caso de Problemas

```bash
# Rollback para o estado anterior
git reset --hard pre-shadcn-migration-[TIMESTAMP]

# Ou rollback seletivo
git revert [COMMIT_HASH]

# Restaurar dependências se necessário
npm install
```

### Checklist de Problemas Comuns

- [ ] **Estilos quebrados**: Verifique se todas as classes foram migradas
- [ ] **Layout desalinhado**: Confirme grid e spacing classes
- [ ] **Cores incorretas**: Valide mapeamento de cores de status
- [ ] **Responsividade**: Teste breakpoints em diferentes dispositivos
- [ ] **Performance**: Monitore bundle size e rendering

---

## 📊 Métricas de Sucesso

### Antes da Migração
- [ ] Todos os testes passando
- [ ] Build sem erros
- [ ] Funcionalidade completa

### Após a Migração
- [ ] Todos os testes continuam passando
- [ ] Build sem erros ou warnings
- [ ] Funcionalidade preservada
- [ ] CSS reduzido (menos classes personalizadas)
- [ ] Melhor consistência visual
- [ ] Facilidade de manutenção aumentada

---

## 🔗 Referências

- [Guia de Padrões de Componentes](./GUIA_PADROES_COMPONENTES.md)
- [Documentação Shadcn UI](https://ui.shadcn.com/)
- [Documentação Tailwind CSS](https://tailwindcss.com/docs)
- [Testes de Regressão Visual](./frontend/src/test/visual-regression.test.tsx)

---

**⚠️ IMPORTANTE**: Execute cada fase completamente antes de prosseguir para a próxima. Sempre valide com testes antes de continuar.