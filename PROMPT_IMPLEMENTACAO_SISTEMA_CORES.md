# 🎨 PROMPT: Implementação do Sistema de Cores Inteligente - GLPI Dashboard

## 📋 CONTEXTO E DOCUMENTAÇÃO DE REFERÊNCIA

**IMPORTANTE**: Antes de iniciar qualquer modificação, consulte obrigatoriamente o documento:
- **ANALISE_PADROES_ERROS_PREVENCAO.md** - Para seguir as estratégias de prevenção estabelecidas
- **SISTEMA_CORES_DASHBOARD_GLPI.md** - Para implementar o sistema de cores científico proposto

## 🎯 OBJETIVO PRINCIPAL

Implementar o **Sistema de Cores Inteligente** conforme especificado no documento `SISTEMA_CORES_DASHBOARD_GLPI.md`, aplicando lógica científica e qualidade visual às cores utilizadas no dashboard GLPI, seguindo rigorosamente o protocolo de prevenção de erros.

## 🛡️ PROTOCOLO DE SEGURANÇA (OBRIGATÓRIO)

### **Pré-Requisitos de Verificação:**
1. **Consultar `src/types/index.ts`** - Verificar interfaces `MetricsData`, `LevelMetrics`
2. **Mapear dependências** - Identificar todos os componentes que usam cores
3. **Verificar uso atual** - Confirmar propriedades (singular vs plural: `novos`, `pendentes`, `progresso`, `resolvidos`)
4. **Analisar imports** - Verificar dependências entre componentes

### **Fluxo de Trabalho Seguro:**
- **Fase 1**: Análise completa das estruturas existentes
- **Fase 2**: Implementação incremental (uma alteração por vez)
- **Fase 3**: Validação total com testes em tempo real

## 🎨 ESPECIFICAÇÕES DE IMPLEMENTAÇÃO

### **1. SISTEMA DE CORES PARA STATUS DE TICKETS**

Implementar as cores baseadas em **estado/resultado** conforme documento:

```css
/* Classes CSS a serem criadas/atualizadas */
.metrics-card-novos {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(147, 197, 253, 0.05) 100%);
  border: 1px solid rgba(59, 130, 246, 0.2);
  color: #1E40AF;
}

.metrics-card-progresso {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(252, 211, 77, 0.05) 100%);
  border: 1px solid rgba(245, 158, 11, 0.2);
  color: #D97706;
}

.metrics-card-pendentes {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, rgba(251, 146, 60, 0.05) 100%);
  border: 1px solid rgba(249, 115, 22, 0.2);
  color: #EA580C;
}

.metrics-card-resolvidos {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(110, 231, 183, 0.05) 100%);
  border: 1px solid rgba(16, 185, 129, 0.2);
  color: #059669;
}
```

### **2. SISTEMA DE CORES PARA NÍVEIS DE TÉCNICOS**

Implementar as cores baseadas em **hierarquia/competência**:

```css
/* Cores para níveis técnicos */
.level-n1 {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(134, 239, 172, 0.05) 100%);
  border: 1px solid rgba(34, 197, 94, 0.2);
  color: #16A34A;
}

.level-n2 {
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(103, 232, 249, 0.05) 100%);
  border: 1px solid rgba(6, 182, 212, 0.2);
  color: #0891B2;
}

.level-n3 {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(196, 181, 253, 0.05) 100%);
  border: 1px solid rgba(139, 92, 246, 0.2);
  color: #7C3AED;
}

.level-n4 {
  background: linear-gradient(135deg, rgba(236, 72, 153, 0.1) 0%, rgba(249, 168, 212, 0.05) 100%);
  border: 1px solid rgba(236, 72, 153, 0.2);
  color: #DB2777;
}
```

### **3. SISTEMA DE CORES PARA RANKING**

Implementar as cores baseadas em **performance/posição**:

```css
/* Cores para ranking */
.ranking-1st {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(252, 211, 77, 0.1) 100%);
  border: 1px solid rgba(245, 158, 11, 0.3);
  color: #D97706;
}

.ranking-2nd {
  background: linear-gradient(135deg, rgba(107, 114, 128, 0.2) 0%, rgba(156, 163, 175, 0.1) 100%);
  border: 1px solid rgba(107, 114, 128, 0.3);
  color: #4B5563;
}

.ranking-3rd {
  background: linear-gradient(135deg, rgba(205, 127, 50, 0.2) 0%, rgba(251, 191, 36, 0.1) 100%);
  border: 1px solid rgba(205, 127, 50, 0.3);
  color: #B45309;
}

.ranking-default {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(147, 197, 253, 0.05) 100%);
  border: 1px solid rgba(59, 130, 246, 0.2);
  color: #1E40AF;
}
```

## 📝 TAREFAS ESPECÍFICAS

### **1. Atualização de Arquivos CSS**
- [ ] Atualizar `src/index.css` com as novas classes de cores
- [ ] Remover classes antigas conflitantes
- [ ] Implementar variáveis CSS para consistência

### **2. Atualização de Componentes**
- [ ] **MetricsGrid.tsx**: Aplicar classes `metrics-card-*` para status gerais
- [ ] **LevelMetricsGrid.tsx**: Aplicar classes `level-*` para níveis técnicos
- [ ] **RankingTable.tsx**: Aplicar classes `ranking-*` para posições
- [ ] **lib/utils.ts**: Atualizar função `getStatusColor` se necessário

### **3. Verificações Críticas**
- [ ] Confirmar que propriedades usam plural: `novos`, `pendentes`, `progresso`, `resolvidos`
- [ ] Verificar que não há conflito entre cores de status e níveis
- [ ] Testar acessibilidade (contraste WCAG 2.1 AA)
- [ ] Validar funcionamento em tempo real

## 🧹 LIMPEZA E REVISÃO FINAL

### **Após Implementação, Executar:**

1. **Auditoria de Código Obsoleto:**
   ```bash
   # Buscar classes antigas não utilizadas
   grep -r "bg-blue-50\|bg-yellow-50\|bg-orange-50\|bg-green-50" src/
   grep -r "text-blue-600\|text-yellow-600\|text-orange-600\|text-green-600" src/
   ```

2. **Verificação de Imports Desnecessários:**
   - Remover imports não utilizados
   - Limpar funções obsoletas
   - Remover comentários antigos

3. **Validação de Consistência:**
   - Verificar se todas as cores seguem o padrão estabelecido
   - Confirmar que não há duplicação de estilos
   - Testar responsividade em diferentes telas

4. **Teste de Regressão:**
   - Verificar se dados continuam sendo exibidos corretamente
   - Confirmar que não há erros no console
   - Testar funcionalidades críticas

## ✅ CHECKLIST DE QUALIDADE FINAL

### **Antes de Concluir:**
- [ ] Todas as cores implementadas seguem o documento `SISTEMA_CORES_DASHBOARD_GLPI.md`?
- [ ] Não há conflitos entre cores de status e níveis?
- [ ] Propriedades usam nomenclatura correta (plural)?
- [ ] Dados em tempo real funcionam corretamente?
- [ ] Código obsoleto foi removido?
- [ ] Acessibilidade foi validada?
- [ ] Performance não foi impactada?
- [ ] Documentação foi atualizada?

## 🎯 RESULTADO ESPERADO

**Ao final da implementação, o dashboard deve ter:**

1. **Sistema de Cores Científico**: Baseado em psicologia das cores e acessibilidade
2. **Separação Semântica Clara**: Status ≠ Níveis ≠ Ranking
3. **Código Limpo**: Sem classes obsoletas ou conflitantes
4. **Funcionalidade Preservada**: Dados em tempo real funcionando perfeitamente
5. **Qualidade Visual**: Interface moderna, profissional e acessível

## ⚠️ LEMBRETES IMPORTANTES

- **SEMPRE** consultar `ANALISE_PADROES_ERROS_PREVENCAO.md` antes de modificar
- **NUNCA** alterar múltiplos arquivos simultaneamente
- **SEMPRE** testar após cada alteração
- **VERIFICAR** interfaces em `src/types/index.ts` antes de modificar propriedades
- **MANTER** consistência com padrões estabelecidos

---

*Este prompt deve ser seguido rigorosamente para garantir implementação segura e de qualidade do sistema de cores inteligente.*