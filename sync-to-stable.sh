#!/bin/bash
# sync-to-stable.sh

echo "🔄 Iniciando sincronização para repositório estável..."

# Verificar se estamos no repositório de desenvolvimento
if [ ! -f "glpi_dashboard/package.json" ]; then
    echo "❌ Execute este script no repositório de desenvolvimento"
    exit 1
fi

# Executar testes
echo "🧪 Executando testes..."
cd glpi_dashboard/frontend
npm test || { echo "❌ Testes do frontend falharam"; exit 1; }
cd ../backend
python -m pytest || { echo "❌ Testes do backend falharam"; exit 1; }
cd ../..

# Fazer backup do repositório estável
echo "💾 Fazendo backup do repositório estável..."
cd ../glpi-dashboard-stable
git checkout main
git tag backup-$(date +%Y%m%d-%H%M%S)
cd ../glpi_dashboard_funcional

# Sincronizar código
echo "📦 Sincronizando código..."
git archive --format=tar HEAD | (cd ../glpi-dashboard-stable && tar -xf -)

# Atualizar documentação
echo "📚 Atualizando documentação..."
cd ../glpi-dashboard-stable
cp ../glpi_dashboard_funcional/CHECKPOINT_FUNCIONAL_DOCUMENTATION.md .
cp ../glpi_dashboard_funcional/FRONTEND_ARCHITECTURE_DOCUMENTATION.md .
cp ../glpi_dashboard_funcional/BACKEND_ARCHITECTURE_DOCUMENTATION.md .
cp ../glpi_dashboard_funcional/CONFIGURATION_DOCUMENTATION.md .

# Commit
echo "💾 Fazendo commit..."
git add .
git commit -m "feat: Sincronização automática - $(date +%Y-%m-%d)"
git tag v$(date +%Y.%m.%d)

echo "✅ Sincronização concluída!"
echo "🏷️ Tag criada: v$(date +%Y.%m.%d)"
