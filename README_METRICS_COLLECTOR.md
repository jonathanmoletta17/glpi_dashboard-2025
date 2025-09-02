# GLPI Metrics Collector

## Descrição
Script Python consolidado para coleta de métricas do sistema GLPI, incluindo autenticação, métricas gerais, tickets novos, ranking de técnicos por nível e status por nível de serviço.

## Pré-requisitos

### Dependências Python
```bash
pip install requests colorama
```

### Variáveis de Ambiente (PowerShell)
```powershell
$env:GLPI_BASE_URL = "http://cau.ppiratini.intra.rs.gov.br/glpi"
$env:GLPI_APP_TOKEN = "aY3f9F5aNHJmY8op0vTE4koguiPwpEYANp1JULid"
$env:GLPI_USER_TOKEN = "TQdSxqg2e56PfF8ZJSX3iEJ1wCpHwhCkQJ2QtRnq"
```

### Serviços Necessários
- **GLPI API**: Disponível em `http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php`
- **Dashboard Local**: Deve estar rodando em `http://localhost:5000` para dados de técnicos

## Como Usar

### Execução Simples
```bash
python glpi_metrics_collector.py
```

### Saída
O script gera:
1. **Console**: Output colorido com progresso e resumos
2. **Arquivo JSON**: Métricas completas salvas em `glpi_metrics_YYYYMMDD_HHMMSS.json`

## Funcionalidades

### 🔐 Autenticação
- Conecta automaticamente ao GLPI usando tokens
- Gerencia sessão de forma segura
- Finaliza sessão ao terminar

### 📊 Métricas Gerais
- Total de tickets no sistema
- Breakdown por status (Novo, Em Progresso, Pendente, etc.)
- Timestamp da coleta

### 🎫 Tickets Novos
- Lista tickets com status "novo"
- Inclui ID, título, prioridade, data de criação
- Mostra técnico atribuído (se houver)

### 🏆 Ranking de Técnicos
- **Fonte**: API do dashboard local (`localhost:5000`)
- **Organização**: Por nível (N1, N2, N3, N4)
- **Métricas**: Tickets resolvidos, pendentes, total, posição no ranking
- **Visualização**: Cores diferenciadas por nível

### 📈 Status por Nível
- Contagem de tickets por nível de serviço
- Breakdown por status dentro de cada nível

## Estrutura do JSON de Saída

```json
{
  "timestamp": "2025-09-01T21:18:43.557480",
  "success": true,
  "metrics": {
    "status_geral": {
      "total_tickets": 10000,
      "status_breakdown": {
        "novo": 2,
        "em_progresso": 25,
        "pendente": 14,
        "resolvido": 50,
        "fechado": 3213,
        "cancelado": 6696
      }
    },
    "tickets_novos": [...],
    "ranking_tecnicos": {
      "N1": [...],
      "N2": [...],
      "N3": [...],
      "N4": [...]
    },
    "status_por_nivel": {...}
  }
}
```

## Dados Validados

Os seguintes técnicos foram validados com dados reais da API:

- **João Pedro Wilson Dias** (ID: 1471) - N1, Posição 19, 0 tickets resolvidos, 1 pendente
- **Jonathan Nascimento Moletta** (ID: 1032) - N2, Posição 6, 567 tickets resolvidos
- **Silvio Godinho Valim** (ID: 32) - N3, Posição 2, 1777 tickets resolvidos

## Troubleshooting

### Erro: "export não é reconhecido"
**Problema**: Usando comando Linux no PowerShell
**Solução**: Use `$env:VARIAVEL = "valor"` no PowerShell

### Erro: "Nenhum técnico encontrado"
**Problema**: Dashboard local não está rodando
**Solução**: Certifique-se de que `localhost:5000` está acessível

### Erro de Autenticação
**Problema**: Tokens inválidos ou expirados
**Solução**: Verifique se os tokens estão corretos e válidos

## Logs e Monitoramento

- **Performance**: Tempo total de execução exibido ao final
- **Erros**: Mensagens coloridas indicam problemas
- **Progresso**: Cada fase é claramente identificada
- **Validação**: Dados são validados contra APIs reais

## Manutenção

Para atualizações futuras:
1. Sempre validar dados com APIs reais
2. Nunca inventar ou simular dados
3. Documentar mudanças nos endpoints
4. Testar com tokens atualizados

---

**Criado em**: 01/09/2025  
**Última atualização**: 01/09/2025  
**Versão**: 1.0