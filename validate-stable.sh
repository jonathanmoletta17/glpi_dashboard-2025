#!/bin/bash
# validate-stable.sh

echo "🔍 Validando repositório estável..."

cd glpi-dashboard-stable

# Verificar estrutura
if [ ! -f "glpi_dashboard/frontend/package.json" ]; then
    echo "❌ Estrutura do frontend inválida"
    exit 1
fi

if [ ! -f "glpi_dashboard/backend/app.py" ]; then
    echo "❌ Estrutura do backend inválida"
    exit 1
fi

# Testar build do frontend
echo "🏗️ Testando build do frontend..."
cd glpi_dashboard/frontend
npm install
npm run build || { echo "❌ Build do frontend falhou"; exit 1; }
cd ../..

# Testar backend
echo "🐍 Testando backend..."
cd glpi_dashboard/backend
python -c "import app; print('✅ Backend OK')" || { echo "❌ Backend inválido"; exit 1; }
cd ../..

echo "✅ Validação concluída com sucesso!"
