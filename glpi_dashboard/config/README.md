# Configuração Centralizada - GLPI Dashboard

Este diretório contém todas as configurações centralizadas do projeto GLPI Dashboard, consolidando arquivos que anteriormente estavam espalhados por diferentes localizações.

## 📁 Estrutura

### Arquivos de Configuração Principal
- `ai_agent_system.yaml` - Configurações do sistema de agentes AI (anteriormente em `/ai_agent_system/config.yaml`)
- `system.yaml` - Configurações gerais do sistema (anteriormente `system_config.yaml` na raiz)
- `sandbox.json` - Configurações do ambiente sandbox para testes de IA
- `settings.py` - Configurações centrais do Flask e API GLPI (mantido em `/glpi_dashboard/backend/`)

### Scripts de Setup (`/setup/`)
- `setup_ai_agents.py` - Configuração dos agentes de IA
- `setup_cache_b_drive.py` - Configuração do cache no drive B
- `setup_gpu_integration.py` - Integração com GPU
- `setup_gpu_minimal.py` - Configuração mínima de GPU
- `setup_monitoring.py` - Configuração do sistema de monitoramento
- `setup_new_architecture.py` - Configuração da nova arquitetura
- `setup_system.py` - Configuração geral do sistema

## 🔧 Uso

### Carregando Configurações
```python
# Para configurações YAML
import yaml
with open('glpi_dashboard/config/ai_agent_system.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Para configurações JSON
import json
with open('glpi_dashboard/config/sandbox.json', 'r') as f:
    config = json.load(f)
```

### Executando Scripts de Setup
```bash
# Executar setup específico
python glpi_dashboard/config/setup/setup_monitoring.py

# Executar setup completo do sistema
python glpi_dashboard/config/setup/setup_system.py
```

## 📋 Histórico de Consolidação

### Arquivos Movidos
- ✅ `ai_agent_system/config.yaml` → `config/ai_agent_system.yaml`
- ✅ `system_config.yaml` → `config/system.yaml`
- ✅ `docs/ai/sandbox/config/sandbox.json` → `config/sandbox.json`
- ✅ Scripts de setup de múltiplos diretórios → `config/setup/`

### Benefícios da Consolidação
- **Organização**: Todas as configurações em um local centralizado
- **Manutenibilidade**: Mais fácil de encontrar e modificar configurações
- **Consistência**: Estrutura padronizada para todos os arquivos de configuração
- **Segurança**: Melhor controle de acesso e versionamento das configurações

## ⚠️ Importante

Após a consolidação, certifique-se de atualizar todas as referências aos arquivos de configuração no código para apontar para os novos caminhos.