
# Dataset GLPI Otimizado para Copilot/IA

## Visão Geral
Este dataset foi especialmente formatado e otimizado para consultas por sistemas de IA como GitHub Copilot, ChatGPT, e outros assistentes de código.

## Estrutura dos Arquivos

### Arquivos Principais
- `tickets_copilot_optimized.csv`: Tickets/chamados otimizados
- `users_copilot_optimized.csv`: Usuários consolidados (técnicos + solicitantes)
- `search_index.json`: Índice de busca para consultas rápidas
- `dataset_metadata.json`: Metadados completos do dataset

### Campos Otimizados para IA

#### Tickets
- `search_text`: Texto combinado para busca
- `content_normalized`: Conteúdo normalizado
- `keywords`: Palavras-chave extraídas
- `categoria_automatica`: Categorização automática
- `tempo_resolucao_dias`: Tempo de resolução em dias

#### Usuários
- `search_text`: Texto combinado para busca
- `nome_busca`: Nome normalizado
- `tipo_usuario`: Técnico/Solicitante/Usuário Geral
- `departamento`: Setor/Grupo de trabalho

## Como Usar com Copilot

### Consultas Recomendadas
```python
# Buscar tickets por categoria
tickets_email = df[df['categoria_automatica'] == 'Email/Office']

# Encontrar técnicos por departamento
tecnicos_dtic = df[df['departamento'].str.contains('DTIC', na=False)]

# Analisar tempo de resolução
tickets_rapidos = df[df['tempo_resolucao_dias'] <= 1]
```

### Campos de Busca
- Use `search_text` para buscas textuais amplas
- Use `keywords` para busca por palavras-chave específicas
- Use campos `*_normalized` para comparações exatas

## Estatísticas do Dataset
- Total de Tickets: 10.142
- Total de Usuários: ~1.784 (consolidado)
- Técnicos Ativos: 19
- Solicitantes: 600
- Categorias Automáticas: 6

## Qualidade dos Dados
- ✅ Dados limpos e normalizados
- ✅ Texto formatado para IA
- ✅ Campos de busca otimizados
- ✅ Metadados estruturados
- ✅ Índice de busca disponível
