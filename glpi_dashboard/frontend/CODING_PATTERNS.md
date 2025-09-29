# Padrões de Código - GLPI Dashboard

## Prevenção de Duplicação de Código

### 1. Biblioteca de Animações

**Localização:** `src/utils/animations.ts`

**Padrões:**
- Use `containerVariants` para animações de containers
- Use `itemVariants` para animações de itens individuais
- Use `createContainerVariants()` para containers customizados
- Evite criar animações inline nos componentes

**Exemplo:**
```tsx
import { containerVariants, itemVariants } from '@/utils/animations';

<motion.div variants={containerVariants}>
  <motion.div variants={itemVariants}>
    Conteúdo
  </motion.div>
</motion.div>
```

### 2. Componentes de Loading

**Localização:** `src/utils/loadingComponents.tsx`

**Padrões:**
- Use `LoadingCard` para cards de loading
- Use `LoadingTable` para tabelas de loading
- Use `LoadingList` para listas de loading
- Evite criar skeletons customizados sem necessidade

**Exemplo:**
```tsx
import { LoadingCard } from '@/utils/loadingComponents';

{isLoading ? <LoadingCard /> : <ActualContent />}
```

### 3. Formatação de Dados

**Localização:** `src/utils/utils.ts`

**Padrões:**
- Use `formatDate()` para datas
- Use `formatCurrency()` para valores monetários
- Use `formatPercentage()` para percentuais
- Use `truncateText()` para textos longos

**Exemplo:**
```tsx
import { formatDate, formatCurrency } from '@/utils/utils';

const formattedDate = formatDate(date);
const formattedPrice = formatCurrency(price);
```

### 4. Hooks Customizados

**Localização:** `src/hooks/`

**Padrões:**
- Use `useFormatters()` para formatações complexas
- Crie hooks para lógica reutilizável
- Evite duplicar lógica de estado entre componentes

### 5. Estilos e Classes CSS

**Padrões:**
- Use classes utilitárias do Tailwind
- Evite estilos inline repetitivos
- Crie componentes base para elementos comuns

### 6. Detecção de Duplicação

**Ferramenta:** jscpd

**Comando:** `npm run audit:duplicates`

**Configuração:** `.jscpd.json`

**Limites:**
- Mínimo de 10 linhas para detecção
- Mínimo de 70 tokens
- Threshold de 50 caracteres

### 7. Diretrizes Gerais

1. **Antes de criar código novo:**
   - Verifique se já existe funcionalidade similar
   - Use a busca no código para encontrar padrões existentes
   - Execute `npm run audit:duplicates` regularmente

2. **Ao refatorar:**
   - Extraia código comum para utilitários
   - Crie hooks para lógica compartilhada
   - Mantenha componentes pequenos e focados

3. **Revisão de código:**
   - Verifique duplicações antes de fazer merge
   - Valide uso correto dos utilitários existentes
   - Execute testes após refatorações

### 8. Estrutura de Arquivos

```
src/
├── components/          # Componentes específicos
├── hooks/              # Hooks customizados
├── utils/              # Utilitários e helpers
│   ├── animations.ts   # Animações reutilizáveis
│   ├── loadingComponents.tsx # Componentes de loading
│   └── utils.ts        # Funções utilitárias
└── types/              # Tipos TypeScript
```

### 9. Comandos Úteis

```bash
# Detectar duplicações
npm run audit:duplicates

# Linting e formatação
npm run lint:fix
npm run format

# Verificação de tipos
npm run type-check

# Build e validação
npm run build
```

### 10. Relatórios

- Relatórios de duplicação: `reports/jscpd/html/index.html`
- Abra o arquivo HTML no navegador para visualização detalhada
- Revise regularmente para manter qualidade do código
