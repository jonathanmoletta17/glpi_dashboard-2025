# FRONTEND ARCHITECTURE - GLPI DASHBOARD

## 📋 VISÃO GERAL

O frontend do GLPI Dashboard é uma aplicação React moderna construída com TypeScript, Vite e Tailwind CSS. Este documento detalha a arquitetura, componentes e funcionalidades do sistema.

## 🏗️ ARQUITETURA TÉCNICA

### **Stack Tecnológico**
- **React 18** - Biblioteca principal para UI
- **TypeScript** - Tipagem estática
- **Vite 5.4.19** - Build tool e dev server
- **Tailwind CSS** - Framework de CSS utilitário
- **Lucide React** - Biblioteca de ícones

### **Estrutura de Pastas**
```
src/
├── components/           # Componentes React
│   ├── dashboard/       # Componentes específicos do dashboard
│   ├── ui/             # Componentes de UI reutilizáveis
│   └── ...
├── hooks/              # Hooks customizados
├── services/           # Serviços de API e dados
├── types/              # Definições de tipos TypeScript
├── utils/              # Utilitários e helpers
└── test/               # Testes e mocks
```

## 🧩 COMPONENTES PRINCIPAIS

### **Dashboard Components**

#### **ModernDashboard.tsx**
- **Função:** Componente principal do dashboard
- **Características:**
  - Layout responsivo
  - Integração com hooks de dados
  - Sistema de cores dinâmico
  - Modo escuro

#### **RankingTable.tsx**
- **Função:** Tabela de ranking de técnicos
- **Características:**
  - Ordenação por métricas
  - Filtros de data
  - Paginação
  - Indicadores visuais de performance

#### **LevelMetricsGrid.tsx**
- **Função:** Grid de métricas por nível (N1, N2, N3, N4)
- **Características:**
  - Cards de métricas
  - Indicadores de tendência
  - Cores dinâmicas por nível
  - Responsividade

#### **StatusCard.tsx**
- **Função:** Cards de status e métricas
- **Características:**
  - Indicadores visuais
  - Cores por status
  - Animações suaves
  - Tooltips informativos

### **UI Components**

#### **badge.tsx**
- **Função:** Componente de badge/etiqueta
- **Variantes:**
  - `default` - Estilo padrão
  - `outline` - Apenas borda
  - `secondary` - Estilo secundário
  - `destructive` - Estilo de erro

#### **separator.tsx**
- **Função:** Separador visual
- **Características:**
  - Linha divisória
  - Orientação horizontal/vertical
  - Estilização customizável

## 🎣 HOOKS CUSTOMIZADOS

### **useDashboard.ts**
- **Função:** Gerenciamento de estado do dashboard
- **Características:**
  - Estado centralizado
  - Cache de dados
  - Gerenciamento de loading
  - Tratamento de erros

### **useApi.ts**
- **Função:** Comunicação com APIs
- **Características:**
  - Requests HTTP
  - Cache inteligente
  - Retry automático
  - Interceptors

### **useDebounce.ts**
- **Função:** Debounce para inputs
- **Características:**
  - Delay configurável
  - Otimização de performance
  - Cancelamento de requests

## 🔌 SERVIÇOS

### **api.ts**
- **Função:** Cliente de API principal
- **Características:**
  - Configuração centralizada
  - Interceptors de request/response
  - Tratamento de erros
  - Cache automático

### **httpClient.ts**
- **Função:** Cliente HTTP base
- **Características:**
  - Configuração de timeout
  - Headers padrão
  - Retry logic
  - Logging de requests

### **smartCache.ts**
- **Função:** Sistema de cache inteligente
- **Características:**
  - Cache em memória
  - TTL configurável
  - Invalidação automática
  - Métricas de performance

## 📊 TIPOS E INTERFACES

### **api.ts**
```typescript
export interface MetricsData {
  novos: number;
  pendentes: number;
  progresso: number;
  resolvidos: number;
  total: number;
  niveis: {
    n1: LevelMetrics;
    n2: LevelMetrics;
    n3: LevelMetrics;
    n4: LevelMetrics;
  };
}

export interface LevelMetrics {
  novos: number;
  progresso: number;
  pendentes: number;
  resolvidos: number;
}

export interface TechnicianRanking {
  id: string;
  name: string;
  rank: number;
  total_tickets: number;
  resolved_tickets: number;
  avg_resolution_time: number;
  level: string;
}
```

### **ticket.ts**
```typescript
export interface Ticket {
  id: string;
  title: string;
  status: string;
  priority: string;
  assignee: string;
  created_at: string;
  updated_at: string;
}
```

## 🎨 SISTEMA DE CORES DINÂMICO

### **Implementação**
- **Base:** Tailwind CSS com cores customizadas
- **Modo Escuro:** Suporte completo
- **Cores por Nível:**
  - N1: Verde (sucesso)
  - N2: Azul (informação)
  - N3: Amarelo (atenção)
  - N4: Vermelho (crítico)

### **Configuração Tailwind**
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
        // Cores customizadas para níveis
        level: {
          n1: '#10b981',
          n2: '#3b82f6',
          n3: '#f59e0b',
          n4: '#ef4444',
        }
      }
    }
  }
}
```

## 🧪 SISTEMA DE TESTES

### **Estrutura de Testes**
```
src/test/
├── accessibility/       # Testes de acessibilidade
├── components/         # Testes de componentes
├── e2e/               # Testes end-to-end
├── integration/       # Testes de integração
├── unit/              # Testes unitários
└── visual/            # Testes visuais
```

### **Ferramentas de Teste**
- **Vitest** - Test runner
- **Testing Library** - Utilitários de teste
- **Playwright** - Testes E2E
- **Jest** - Testes unitários

## ⚡ OTIMIZAÇÕES DE PERFORMANCE

### **Code Splitting**
- Lazy loading de componentes
- Chunks otimizados por rota
- Tree shaking automático

### **Cache Inteligente**
- Cache de API responses
- Invalidação seletiva
- Métricas de hit rate

### **Bundle Optimization**
- Minificação automática
- Compressão gzip
- Assets otimizados

## 🔧 CONFIGURAÇÕES

### **Vite Config**
```typescript
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['lucide-react']
        }
      }
    }
  }
})
```

### **TypeScript Config**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

## 🚀 COMANDOS DE DESENVOLVIMENTO

### **Instalação**
```bash
npm install
```

### **Desenvolvimento**
```bash
npm run dev
```

### **Build**
```bash
npm run build
```

### **Preview**
```bash
npm run preview
```

### **Testes**
```bash
npm run test
npm run test:ui
npm run test:e2e
```

## 📈 MÉTRICAS DE QUALIDADE

- **Build Time:** ~6.5s
- **Bundle Size:** ~405KB (gzipped: ~129KB)
- **TypeScript Errors:** 0 (após correções)
- **Test Coverage:** Configurado
- **Lighthouse Score:** Otimizado

## 🔄 INTEGRAÇÃO COM BACKEND

### **Endpoints Principais**
- `GET /api/metrics` - Métricas do dashboard
- `GET /api/technicians/ranking` - Ranking de técnicos
- `GET /api/tickets` - Lista de tickets
- `GET /api/health` - Status do sistema

### **Configuração de API**
```typescript
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

## 🎯 CARACTERÍSTICAS ESPECIAIS

### **Sistema de Cores Dinâmico**
- Cores baseadas em dados
- Transições suaves
- Acessibilidade garantida

### **Responsividade**
- Mobile-first design
- Breakpoints otimizados
- Layout adaptativo

### **Acessibilidade**
- ARIA labels
- Navegação por teclado
- Contraste adequado
- Screen reader support

## ✅ CONCLUSÃO

O frontend do GLPI Dashboard representa uma implementação moderna e robusta com:
- Arquitetura limpa e escalável
- Performance otimizada
- Código bem tipado e testado
- Interface responsiva e acessível
- Sistema de cores dinâmico funcional

**Status:** ✅ PRONTO PARA PRODUÇÃO
