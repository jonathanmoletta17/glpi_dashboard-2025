# Testes Consolidados da Raiz

Este diretório contém testes que foram movidos da raiz do projeto (`/test/`) para centralizar toda a estrutura de testes no backend.

## Conteúdo

Testes consolidados incluem:
- `test_ai_integration.py` - Testes de integração com IA
- `test_api_ranking.py` - Testes de ranking da API
- `test_date_filters.py` - Testes de filtros de data
- `test_glpi_integration.py` - Testes de integração GLPI
- `test_new_technician_implementation.py` - Testes de implementação de técnicos
- `test_optimization_models.py` - Testes de modelos de otimização
- `test_python.py` - Testes gerais Python
- `test_ranking_terminal.py` - Testes de ranking no terminal
- `test_ranking_matrix.py` - Testes de matriz de ranking
- `test_ranking_results.py` - Testes de resultados de ranking
- `test_technician_simple.py` - Testes simples de técnicos
- `test_transformers.py` - Testes de transformadores

## Execução

Para executar os testes:

```bash
cd glpi_dashboard/backend/tests/consolidated_root_tests
python -m pytest [test_file].py
```

Ou execute todos os testes:

```bash
python -m pytest .
```

## Histórico

- **Data**: 30/08/2025
- **Ação**: Consolidação de testes da raiz
- **Origem**: `/test/` da raiz do projeto
- **Destino**: `glpi_dashboard/backend/tests/consolidated_root_tests/`
- **Motivo**: Centralização da estrutura de testes no backend