# Guia de Padrões de Construção de Componentes

## 📋 Índice
1. [Princípios Fundamentais](#princípios-fundamentais)
2. [Sistema de Espaçamento](#sistema-de-espaçamento)
3. [Padrões de Componentes](#padrões-de-componentes)
4. [Nomenclatura e Organização](#nomenclatura-e-organização)
5. [Exemplos Práticos](#exemplos-práticos)
6. [Checklist de Implementação](#checklist-de-implementação)

## 🎯 Princípios Fundamentais

### 1. Consistência Visual
- **Espaçamentos uniformes** baseados em múltiplos de 4px
- **Hierarquia tipográfica** clara e consistente
- **Sistema de cores** unificado
- **Componentes reutilizáveis** com variações controladas

### 2. Manutenibilidade
- **Separação de responsabilidades** (estrutura, estilo, comportamento)
- **Nomenclatura semântica** e previsível
- **Documentação inline** para componentes complexos
- **Testes visuais** para regressões

### 3. Performance
- **CSS otimizado** com Tailwind CSS
- **Componentes lazy** quando apropriado
- **Bundle splitting** por funcionalidade
- **Memoização** de componentes pesados

## 📏 Sistema de Espaçamento

### Escala de Espaçamento Padronizada

```typescript
// Design Tokens - Espaçamento
export const SPACING = {
  // Base scale (múltiplos de 4px)
  xs: '0.25rem',    // 4px
  sm: '0.5rem',     // 8px
  md: '0.75rem',    // 12px
  lg: '1rem',       // 16px
  xl: '1.5rem',     // 24px
  '2xl': '2rem',    // 32px
  '3xl': '3rem',    // 48px
  '4xl': '4rem',    // 64px
} as const;

// Semantic spacing
export const COMPONENT_SPACING = {
  card: {
    padding: SPACING.xl,      // 24px
    gap: SPACING.lg,          // 16px
    margin: SPACING.xl,       // 24px
  },
  section: {
    padding: SPACING['2xl'],  // 32px
    gap: SPACING['2xl'],      // 32px
    margin: SPACING['3xl'],   // 48px
  },
  grid: {
    gap: SPACING.lg,          // 16px
    columnGap: SPACING.lg,    // 16px
    rowGap: SPACING.xl,       // 24px
  },
} as const;
```

### Mapeamento Tailwind CSS

```typescript
// Tailwind Classes Padronizadas
export const TAILWIND_SPACING = {
  // Padding
  cardPadding: 'p-6',        // 24px
  sectionPadding: 'p-8',     // 32px
  buttonPadding: 'px-4 py-2', // 16px horizontal, 8px vertical
  
  // Gaps
  cardGap: 'gap-4',          // 16px
  sectionGap: 'gap-8',       // 32px
  gridGap: 'gap-4',          // 16px
  
  // Margins
  cardMargin: 'mb-6',        // 24px bottom
  sectionMargin: 'mb-12',    // 48px bottom
  elementMargin: 'mb-4',     // 16px bottom
} as const;
```

## 🧩 Padrões de Componentes

### 1. Estrutura Base de Card

```tsx
// ✅ CORRETO - Padrão Unificado
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface BaseCardProps {
  variant?: 'default' | 'elevated' | 'outlined';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  children: React.ReactNode;
}

const BaseCard: React.FC<BaseCardProps> = ({ 
  variant = 'default', 
  size = 'md', 
  className, 
  children 
}) => {
  const variants = {
    default: 'border bg-card text-card-foreground shadow-sm',
    elevated: 'border bg-card text-card-foreground shadow-lg',
    outlined: 'border-2 bg-transparent text-foreground',
  };
  
  const sizes = {
    sm: 'p-4',      // 16px
    md: 'p-6',      // 24px
    lg: 'p-8',      // 32px
  };
  
  return (
    <Card className={cn(
      'rounded-xl transition-all duration-300',
      variants[variant],
      sizes[size],
      className
    )}>
      {children}
    </Card>
  );
};
```

### 2. Metric Card Padronizado

```tsx
// ✅ CORRETO - Metric Card Consistente
interface MetricCardProps {
  title: string;
  value: string | number;
  change?: {
    value: number;
    isPositive: boolean;
    display: string;
  };
  icon?: React.ComponentType<{ className?: string }>;
  variant?: 'default' | 'compact';
}

const MetricCard: React.FC<MetricCardProps> = ({ 
  title, 
  value, 
  change, 
  icon: Icon, 
  variant = 'default' 
}) => {
  return (
    <BaseCard 
      variant="elevated" 
      size={variant === 'compact' ? 'sm' : 'md'}
      className="hover:shadow-xl transition-shadow duration-300"
    >
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="flex items-baseline space-x-2">
          <div className="text-2xl font-bold text-foreground">
            {value}
          </div>
          {change && (
            <div className={cn(
              "text-xs font-medium",
              change.isPositive ? "text-green-600" : "text-red-600"
            )}>
              {change.display}
            </div>
          )}
        </div>
      </CardContent>
    </BaseCard>
  );
};
```

### 3. Grid Layout Padronizado

```tsx
// ✅ CORRETO - Grid Responsivo Consistente
interface DashboardGridProps {
  children: React.ReactNode;
  columns?: 1 | 2 | 3 | 4;
  gap?: 'sm' | 'md' | 'lg';
  className?: string;
}

const DashboardGrid: React.FC<DashboardGridProps> = ({ 
  children, 
  columns = 3, 
  gap = 'md', 
  className 
}) => {
  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
  };
  
  const gaps = {
    sm: 'gap-3',    // 12px
    md: 'gap-4',    // 16px
    lg: 'gap-6',    // 24px
  };
  
  return (
    <div className={cn(
      'grid w-full',
      gridCols[columns],
      gaps[gap],
      className
    )}>
      {children}
    </div>
  );
};
```

## 🏗️ Nomenclatura e Organização

### Estrutura de Diretórios

```
📁 src/components/
├── 📁 ui/                  # Componentes base (Shadcn UI)
│   ├── button.tsx
│   ├── card.tsx
│   ├── input.tsx
│   └── badge.tsx
├── 📁 atoms/               # Componentes atômicos
│   ├── Icon/
│   ├── StatusBadge/
│   └── LoadingSpinner/
├── 📁 molecules/           # Componentes moleculares
│   ├── MetricCard/
│   │   ├── index.tsx
│   │   ├── MetricCard.tsx
│   │   ├── MetricCard.stories.tsx
│   │   └── MetricCard.test.tsx
│   ├── SearchBox/
│   └── StatusIndicator/
├── 📁 organisms/           # Componentes complexos
│   ├── DashboardGrid/
│   ├── TicketsList/
│   └── RankingTable/
└── 📁 templates/           # Layouts e templates
    ├── DashboardLayout/
    └── PageLayout/
```

### Convenções de Nomenclatura

```typescript
// ✅ CORRETO - Nomenclatura Semântica

// Componentes: PascalCase
const MetricCard = () => {};
const DashboardGrid = () => {};

// Props: camelCase com sufixo Props
interface MetricCardProps {
  title: string;
  value: number;
}

// Constantes: UPPER_SNAKE_CASE
const SPACING_SCALE = {};
const COLOR_TOKENS = {};

// Hooks: camelCase com prefixo use
const useMetrics = () => {};
const useDashboard = () => {};

// Utilitários: camelCase
const formatNumber = () => {};
const calculateChange = () => {};
```

## 💡 Exemplos Práticos

### Antes vs Depois - Refatoração

```tsx
// ❌ ANTES - Inconsistente
<div className="figma-level-card p-12 mb-2">
  <h3 className="text-h3 text-primary">Nível {level}</h3>
  <span className="text-meta status-resolved">{rate}%</span>
  <div className="grid grid-cols-2 gap-3 mb-4">
    <div className="text-center">
      <div className="text-numeric status-new">{data.novos}</div>
      <div className="text-body text-secondary">Novos</div>
    </div>
  </div>
</div>

// ✅ DEPOIS - Padronizado
<BaseCard variant="elevated" size="md" className="hover:shadow-xl">
  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
    <CardTitle className="text-lg font-semibold">Nível {level}</CardTitle>
    <Badge variant="success">{rate}% Resolução</Badge>
  </CardHeader>
  
  <CardContent className="pt-0">
    <DashboardGrid columns={2} gap="sm">
      <div className="text-center space-y-1">
        <div className="text-2xl font-bold text-blue-600">{data.novos}</div>
        <div className="text-sm text-muted-foreground">Novos</div>
      </div>
    </DashboardGrid>
  </CardContent>
</BaseCard>
```

### Exemplo de Componente Completo

```tsx
// ✅ EXEMPLO COMPLETO - Level Metrics Card
import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface LevelMetricsCardProps {
  level: string;
  data: {
    novos: number;
    progresso: number;
    pendentes: number;
    resolvidos: number;
  };
  className?: string;
}

export const LevelMetricsCard: React.FC<LevelMetricsCardProps> = ({ 
  level, 
  data, 
  className 
}) => {
  const total = data.novos + data.progresso + data.pendentes + data.resolvidos;
  const resolutionRate = total > 0 ? Math.round((data.resolvidos / total) * 100) : 0;
  
  const metrics = [
    { label: 'Novos', value: data.novos, color: 'text-blue-600' },
    { label: 'Progresso', value: data.progresso, color: 'text-yellow-600' },
    { label: 'Pendentes', value: data.pendentes, color: 'text-orange-600' },
    { label: 'Resolvidos', value: data.resolvidos, color: 'text-green-600' },
  ];
  
  return (
    <Card className={cn(
      'rounded-xl border bg-card text-card-foreground shadow-sm',
      'hover:shadow-lg transition-all duration-300',
      'p-6',
      className
    )}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-lg font-semibold text-foreground">
          Nível {level}
        </CardTitle>
        <Badge 
          variant={resolutionRate >= 80 ? 'default' : 'secondary'}
          className="text-xs"
        >
          {resolutionRate}% Resolução
        </Badge>
      </CardHeader>
      
      <CardContent className="pt-0 space-y-4">
        {/* Metrics Grid */}
        <div className="grid grid-cols-2 gap-4">
          {metrics.map((metric) => (
            <div key={metric.label} className="text-center space-y-1">
              <div className={cn('text-2xl font-bold', metric.color)}>
                {metric.value}
              </div>
              <div className="text-sm text-muted-foreground">
                {metric.label}
              </div>
            </div>
          ))}
        </div>
        
        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Taxa de Resolução</span>
            <span className="font-medium">{resolutionRate}%</span>
          </div>
          <Progress value={resolutionRate} className="h-2" />
        </div>
      </CardContent>
    </Card>
  );
};
```

## ✅ Checklist de Implementação

### Para Novos Componentes

- [ ] **Estrutura**: Usa componentes base do Shadcn UI
- [ ] **Espaçamento**: Segue escala padronizada (múltiplos de 4px)
- [ ] **Nomenclatura**: PascalCase para componentes, camelCase para props
- [ ] **TypeScript**: Interfaces bem definidas com tipos específicos
- [ ] **Responsividade**: Breakpoints consistentes (sm, md, lg, xl)
- [ ] **Acessibilidade**: ARIA labels e navegação por teclado
- [ ] **Performance**: Memoização quando necessário
- [ ] **Testes**: Pelo menos testes de renderização
- [ ] **Documentação**: Props documentadas e exemplos de uso

### Para Refatoração de Componentes Existentes

- [ ] **Auditoria**: Identificar classes CSS não padronizadas
- [ ] **Mapeamento**: Converter para equivalentes Tailwind
- [ ] **Limpeza**: Remover classes não definidas ou duplicadas
- [ ] **Padronização**: Aplicar sistema de espaçamento consistente
- [ ] **Testes**: Verificar regressões visuais
- [ ] **Documentação**: Atualizar guias e exemplos

### Validação de Qualidade

- [ ] **Consistência Visual**: Espaçamentos uniformes
- [ ] **Performance**: Bundle size otimizado
- [ ] **Manutenibilidade**: Código limpo e bem estruturado
- [ ] **Reutilização**: Componentes modulares e flexíveis
- [ ] **Documentação**: Guias atualizados e exemplos funcionais

---

## 🎯 Resumo dos Benefícios

### Imediatos
- ✅ **Consistência visual** em todo o projeto
- ✅ **Redução de CSS duplicado** e conflitante
- ✅ **Facilidade de manutenção** com padrões claros

### Médio Prazo
- ✅ **Produtividade aumentada** com componentes reutilizáveis
- ✅ **Onboarding facilitado** para novos desenvolvedores
- ✅ **Qualidade de código** melhorada

### Longo Prazo
- ✅ **Escalabilidade** do sistema de design
- ✅ **Performance otimizada** com bundle splitting
- ✅ **Experiência do usuário** consistente e profissional

---

*Este guia deve ser seguido para todos os novos componentes e usado como referência para refatoração dos existentes.*