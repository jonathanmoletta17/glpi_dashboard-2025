# Diretório de Scripts Consolidados

Este diretório contém scripts de debug e análise que foram consolidados de diferentes localizações do projeto para melhorar a organização.

## Estrutura

### `/root_debug/`
Scripts que estavam na raiz do projeto (`/debug/`):
- Scripts de debug de usuários ativos
- Scripts de análise de resposta do backend
- Scripts de debug de cache e performance
- Scripts de investigação de dados

### `/scripts/` (original `/debug/scripts/`)
Scripts organizados por categoria:
- **audit/**: Scripts de auditoria do sistema
- **cache/**: Scripts de análise e otimização de cache
- **investigation/**: Scripts de investigação de dados
- **optimization/**: Scripts de otimização de performance

## Uso

Todos os scripts mantêm sua funcionalidade original. Para executar:

```bash
cd glpi_dashboard/backend/scripts/consolidated_debug
python root_debug/[script_name].py
# ou
python scripts/[category]/[script_name].py
```

## Histórico

- **Data**: 30/08/2025
- **Ação**: Consolidação de estruturas duplicadas
- **Origem**: `/debug/` e `/debug/scripts/` da raiz do projeto
- **Destino**: `glpi_dashboard/backend/scripts/consolidated_debug/`