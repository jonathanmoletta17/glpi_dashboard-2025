# 🔍 Processo de Verificação Rigorosa de Dependências

## ⚠️ LIÇÃO APRENDIDA
A remoção precipitada dos componentes `dialog`, `card`, `button` e `badge` causou erros na interface, demonstrando a necessidade de um processo mais rigoroso.

## 📋 Checklist Obrigatório ANTES de Remover Qualquer Arquivo

### 1. 🔎 Verificação de Importações
```bash
# Buscar por importações diretas
grep -r "import.*from.*filename" src/
grep -r "import.*filename" src/

# Buscar por importações dinâmicas
grep -r "import(" src/
grep -r "require(" src/
```

### 2. 🔗 Verificação de Referências
```bash
# Buscar por referências no código
grep -r "filename" src/ --exclude-dir=node_modules
grep -r "ComponentName" src/ --exclude-dir=node_modules

# Verificar em arquivos de configuração
grep -r "filename" *.json *.js *.ts *.tsx
```

### 3. 🧪 Verificação de Testes
```bash
# Verificar se há testes que referenciam o arquivo
grep -r "filename" src/__tests__/
grep -r "filename" src/**/*.test.*
grep -r "filename" src/**/*.spec.*
```

### 4. 📦 Verificação de Build
```bash
# SEMPRE executar build antes de confirmar remoção
npm run build
npm run lint
npm run type-check
```

### 5. 🎯 Verificação de Uso em Componentes UI
Para componentes do design system, verificar:
- `@/components/ui/` - Importações diretas
- `shadcn/ui` - Componentes base
- Arquivos de estilo que podem referenciar classes CSS

## 🚨 Regras de Segurança

### ❌ NUNCA Remover Sem Verificar:
1. Componentes do diretório `ui/`
2. Arquivos de configuração (`.ts`, `.js`, `.json`)
3. Arquivos de setup de testes
4. Arquivos de ambiente/configuração
5. Hooks customizados
6. Utilitários compartilhados

### ✅ Processo Seguro de Remoção:
1. **Identificar** → Listar arquivos candidatos à remoção
2. **Verificar** → Executar todos os checks acima
3. **Testar** → Build + Lint + Testes
4. **Documentar** → Registrar o que foi removido
5. **Validar** → Testar interface funcionando
6. **Commit** → Commit pequeno e específico

## 🛠️ Scripts de Verificação Automatizada

### Script de Verificação de Dependências
```bash
#!/bin/bash
# verify-dependencies.sh

FILE_TO_CHECK=$1
echo "🔍 Verificando dependências para: $FILE_TO_CHECK"

echo "📦 Verificando importações..."
grep -r "import.*$FILE_TO_CHECK" src/ || echo "✅ Nenhuma importação encontrada"

echo "🔗 Verificando referências..."
grep -r "$FILE_TO_CHECK" src/ --exclude="$FILE_TO_CHECK" || echo "✅ Nenhuma referência encontrada"

echo "🧪 Executando build..."
npm run build && echo "✅ Build OK" || echo "❌ Build FALHOU"

echo "🔍 Executando lint..."
npm run lint && echo "✅ Lint OK" || echo "❌ Lint com problemas"
```

## 📊 Relatório de Impacto

### Componentes Restaurados:
- ✅ `badge.tsx` - Usado em: ProfessionalRankingTable, PremiumLevelCard, ProfessionalTicketsList
- ✅ `button.tsx` - Usado em: ProfessionalTicketsList
- ✅ `card.tsx` - Usado em: Múltiplos componentes do dashboard
- ✅ `dialog.tsx` - Componente base para modais

### Lições Aprendidas:
1. **Auditoria automatizada** pode ter falsos positivos
2. **Componentes UI base** são críticos para o sistema
3. **Verificação manual** é essencial antes da remoção
4. **Testes de build** devem ser executados SEMPRE

## 🎯 Próximos Passos Seguros

1. **Implementar script de verificação** antes de qualquer remoção
2. **Criar whitelist** de arquivos que NUNCA devem ser removidos
3. **Estabelecer processo de review** para remoções
4. **Documentar dependências críticas** do sistema

---
**⚠️ IMPORTANTE**: Este processo deve ser seguido RIGOROSAMENTE para evitar quebras no sistema.