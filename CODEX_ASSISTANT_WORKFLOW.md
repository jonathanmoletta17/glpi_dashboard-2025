# Fluxo de Trabalho Colaborativo Codex-Assistant

## Visão Geral
Este documento descreve o fluxo de trabalho colaborativo entre o Codex GPT-5 CLI e o Assistant para análise e implementação de código no projeto GLPI Dashboard.

## Configuração Inicial

### 1. Instalação e Autenticação
```powershell
# Instalar Codex CLI globalmente
npm install -g @openai/codex

# Autenticar com conta ChatGPT
& "C:\Users\jonathan-moletta.PPIRATINI\AppData\Roaming\npm\codex.cmd" auth login
```

### 2. Configuração Personalizada
O arquivo `config.toml` está localizado em: `%USERPROFILE%\.codex\config.toml`

**Principais configurações:**
- Modelo padrão: `gpt-5-codex`
- Fallback: `gpt-4-turbo`
- MCPs configurados: filesystem, git, database
- Modo colaborativo ativado

## Fluxos de Trabalho

### Modo 1: Codex Analisa → Assistant Implementa

**Quando usar:** Para análise detalhada de código existente e planejamento de melhorias.

**Processo:**
1. **Análise com Codex:**
   ```powershell
   & "C:\Users\jonathan-moletta.PPIRATINI\AppData\Roaming\npm\codex.cmd" -C "C:\Users\jonathan-moletta.PPIRATINI\projects\glpi_dashboard_funcional" "Analise [componente/funcionalidade] e identifique oportunidades de melhoria"
   ```

2. **Implementação com Assistant:**
   - Receber recomendações do Codex
   - Criar plano de implementação detalhado
   - Executar mudanças no código
   - Validar resultados

**Exemplo de Comando Codex:**
```powershell
& "C:\Users\jonathan-moletta.PPIRATINI\AppData\Roaming\npm\codex.cmd" -C "C:\Users\jonathan-moletta.PPIRATINI\projects\glpi_dashboard_funcional" "Analise a estrutura do frontend React e identifique oportunidades de melhoria na arquitetura de componentes. Foque em: 1) Organização de pastas, 2) Padrões de componentes, 3) Gerenciamento de estado, 4) Performance"
```

### Modo 2: Assistant Analisa → Codex Implementa

**Quando usar:** Para implementação rápida de funcionalidades específicas com supervisão.

**Processo:**
1. **Análise com Assistant:**
   - Examinar código existente
   - Identificar requisitos
   - Definir especificações técnicas

2. **Implementação com Codex:**
   ```powershell
   & "C:\Users\jonathan-moletta.PPIRATINI\AppData\Roaming\npm\codex.cmd" -C "C:\Users\jonathan-moletta.PPIRATINI\projects\glpi_dashboard_funcional" "Implemente [funcionalidade] seguindo as especificações: [detalhes]"
   ```

### Modo 3: Colaboração Simultânea

**Quando usar:** Para problemas complexos que requerem análise e implementação iterativa.

**Processo:**
1. Codex faz análise inicial
2. Assistant refina e planeja
3. Codex implementa primeira versão
4. Assistant revisa e otimiza
5. Iteração até conclusão

## Comandos Úteis

### Análise de Estrutura
```powershell
# Listar arquivos principais
& "C:\Users\jonathan-moletta.PPIRATINI\AppData\Roaming\npm\codex.cmd" -C "C:\Users\jonathan-moletta.PPIRATINI\projects\glpi_dashboard_funcional" "Liste os arquivos principais do projeto"

# Análise de componente específico
& "C:\Users\jonathan-moletta.PPIRATINI\AppData\Roaming\npm\codex.cmd" -C "C:\Users\jonathan-moletta.PPIRATINI\projects\glpi_dashboard_funcional" "Analise o componente [nome] e sugira melhorias"
```

### Análise de Performance
```powershell
# Identificar gargalos
& "C:\Users\jonathan-moletta.PPIRATINI\AppData\Roaming\npm\codex.cmd" -C "C:\Users\jonathan-moletta.PPIRATINI\projects\glpi_dashboard_funcional" "Identifique gargalos de performance no frontend e sugira otimizações"
```

### Análise de Arquitetura
```powershell
# Revisar padrões de código
& "C:\Users\jonathan-moletta.PPIRATINI\AppData\Roaming\npm\codex.cmd" -C "C:\Users\jonathan-moletta.PPIRATINI\projects\glpi_dashboard_funcional" "Revise os padrões de arquitetura e sugira melhorias na organização do código"
```

## Resultados da Análise Inicial

### Frontend React - Insights do Codex:

**Problemas Identificados:**
1. **Organização de Pastas:** Estrutura atual mistura lógica de negócio com apresentação
2. **Gerenciamento de Estado:** Uso de hooks customizados sem otimização de re-renders
3. **Performance:** 
   - Falta de memoização em componentes pesados
   - Fetchs paralelos sem cache adequado
   - Throttling manual sem cancelamento de promises

**Recomendações Específicas:**
1. **Reestruturação:** Migrar para arquitetura `app/features/shared`
2. **Estado:** Implementar React Query para cache e invalidação declarativa
3. **Performance:** 
   - Implementar `useMemo` em componentes de métricas
   - Usar `AbortController` para cancelar requests
   - Otimizar interceptadores HTTP

## Configurações Avançadas

### MCPs Disponíveis
- **filesystem:** Acesso ao sistema de arquivos do projeto
- **git:** Integração com controle de versão
- **database:** Conexão com banco de dados (se necessário)
- **web_search:** Busca web (desabilitado por padrão)

### Parâmetros de Execução
- `--full-auto`: Execução automática com sandbox
- `--search`: Habilita busca web
- `-C <DIR>`: Define diretório de trabalho
- `-a on-failure`: Aprovação apenas em falhas

## Troubleshooting

### Problemas Comuns
1. **Comando não encontrado:** Use o caminho completo do executável
2. **Erro de configuração:** Verifique campos obrigatórios no `config.toml`
3. **MCP servers falham:** Instale dependências npm necessárias

### Logs e Debugging
- Logs do Codex: Disponíveis durante execução
- Configuração: `%USERPROFILE%\.codex\config.toml`
- Cache: `%USERPROFILE%\.codex\`

## Próximos Passos

1. **Implementar Recomendações:** Seguir insights do Codex para otimização do frontend
2. **Automatizar Workflows:** Criar scripts para análises recorrentes
3. **Integração CI/CD:** Incorporar análises do Codex no pipeline
4. **Monitoramento:** Estabelecer métricas de qualidade de código

---

**Última atualização:** Janeiro 2025
**Versão Codex CLI:** 0.39.0
**Configuração:** Personalizada para projeto GLPI Dashboard