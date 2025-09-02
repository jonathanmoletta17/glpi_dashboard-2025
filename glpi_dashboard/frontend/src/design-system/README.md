# Design System - Guia de Padrões

Este guia estabelece os padrões unificados para construção de componentes no projeto GLPI Dashboard.

## 🎯 **Princípios Fundamentais**

### 1. **Consistência Visual**
- Todos os componentes devem seguir os mesmos padrões de espaçamento
- Uso consistente de cores, tipografia e bordas
- Comportamento de hover e interações padronizado

### 2. **Reutilização**
- Componentes devem ser modulares e reutilizáveis
- Evitar duplicação de código e estilos
- Usar tokens de design em vez de valores hardcoded

### 3. **Manutenibilidade**
- Código limpo e bem documentado
- Separação clara de responsabilidades
- Fácil de estender e modificar

## 📏 **Sistema de Espaçamento**

### Tokens de Espaçamento
```typescript
import { spacing, componentSpacing, layoutSpacing } from '@/design-system/spacing';

// Uso em componentes
className={`p-${spacing.lg} gap-${componentSpacing.cardGap}`}
```

### Padrões de Espaçamento por Componente
- **Cards**: `p-4` (16px)
- **Listas**: `space-y-2` (8px entre itens)
- **Seções**: `space-y-6` (24px entre seções)
- **Botões**: `px-4 py-2` (16px horizontal, 8px vertical)

## 🧩 **Padrões de Componentes**

### Cards
```typescript
import { createCardClasses } from '@/design-system/component-patterns';

// Uso
<Card className={createCardClasses('custom-class')}>
  {/* conteúdo */}
</Card>
```

### Listas
```typescript
import { createListItemClasses } from '@/design-system/component-patterns';

// Uso
<div className={createListItemClasses()}>
  {/* item da lista */}
</div>
```

### Badges
```typescript
import { createBadgeClasses } from '@/design-system/component-patterns';

// Uso
<Badge className={createBadgeClasses('primary')}>
  {/* conteúdo do badge */}
</Badge>
```

## 🎨 **Sistema de Cores**

### Cores Primárias
- **Primary**: `#3b82f6` (azul)
- **Success**: `#10b981` (verde)
- **Warning**: `#f59e0b` (amarelo)
- **Danger**: `#ef4444` (vermelho)

### Cores de Texto
- **Primary**: `#1e293b` (escuro) / `#f8fafc` (claro)
- **Secondary**: `#64748b` (escuro) / `#94a3b8` (claro)
- **Muted**: `#9ca3af` (escuro) / `#6b7280` (claro)

## 📱 **Responsividade**

### Breakpoints
- **Mobile**: `< 768px`
- **Tablet**: `768px - 1024px`
- **Desktop**: `1024px - 1280px`
- **Large**: `> 1280px`

### Padrões Responsivos
```typescript
// Espaçamento responsivo
className="p-4 md:p-6 lg:p-8"

// Grid responsivo
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
```

## ⚡ **Performance**

### Otimizações
- Use `React.memo` para componentes que não mudam frequentemente
- Lazy loading para componentes pesados
- Animações otimizadas com `framer-motion`
- CSS-in-JS mínimo, prefira classes Tailwind

### Animações
```typescript
// Animações simples e performáticas
const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.2 } },
};
```

## 🔧 **Ferramentas de Desenvolvimento**

### ESLint Rules
```json
{
  "rules": {
    "tailwindcss/classnames-order": "error",
    "tailwindcss/no-custom-classname": "error"
  }
}
```

### Prettier Config
```json
{
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

## 📋 **Checklist de Componentes**

Antes de criar um novo componente, verifique:

- [ ] Usa tokens de espaçamento do design system
- [ ] Segue os padrões de cores definidos
- [ ] É responsivo em todos os breakpoints
- [ ] Tem estados de loading e erro
- [ ] Suporta modo escuro
- [ ] É acessível (ARIA labels, focus states)
- [ ] Tem animações suaves e performáticas
- [ ] Está documentado com exemplos de uso

## 🚀 **Migração de Componentes Existentes**

### Passos para Migração
1. **Identificar** componentes com problemas de formatação
2. **Refatorar** usando os padrões do design system
3. **Testar** em diferentes dispositivos e temas
4. **Documentar** mudanças e novos padrões
5. **Remover** código obsoleto

### Exemplo de Migração
```typescript
// ❌ Antes (inconsistente)
<div className="p-3 m-2 bg-white border rounded-lg shadow-sm hover:shadow-md">

// ✅ Depois (padronizado)
<div className={createCardClasses()}>
```

## 📚 **Recursos Adicionais**

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Framer Motion Guide](https://www.framer.com/motion/)
- [React Best Practices](https://react.dev/learn)
- [Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
