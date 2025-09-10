#!/bin/bash

echo "🚀 Configurando GLPI Dashboard..."

# Verificar dependências
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Instale Node.js 18+ primeiro."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python não encontrado. Instale Python 3.12+ primeiro."
    exit 1
fi

# Configurar frontend
echo "📦 Configurando frontend..."
cd glpi_dashboard/frontend
npm install
npm run build
cd ../..

# Configurar backend
echo "🐍 Configurando backend..."
cd glpi_dashboard/backend
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
cd ../..

# Configurar variáveis de ambiente
echo "⚙️ Configurando variáveis de ambiente..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Arquivo .env criado. Configure as variáveis necessárias."
fi

echo "✅ Configuração concluída!"
echo "🔧 Configure as variáveis no arquivo .env"
echo "🚀 Execute: npm run dev (frontend) e python app.py (backend)"
