#!/bin/bash

echo "🚀 Deploying GLPI Dashboard..."

# Build frontend
echo "📦 Building frontend..."
cd glpi_dashboard/frontend
npm run build
cd ../..

# Build Docker images
echo "🐳 Building Docker images..."
docker-compose build

# Deploy with Docker Compose
echo "🚀 Deploying with Docker Compose..."
docker-compose up -d

echo "✅ Deploy concluído!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "📊 Health: http://localhost:8000/api/health"
