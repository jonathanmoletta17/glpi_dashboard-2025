#!/bin/bash

# Script para executar o projeto GLPI Dashboard com Docker

echo "🐳 INICIANDO GLPI DASHBOARD COM DOCKER"
echo "======================================"

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker Desktop."
    exit 1
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Remover imagens antigas (opcional)
read -p "🗑️  Remover imagens antigas? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removendo imagens antigas..."
    docker-compose down --rmi all
fi

# Construir e iniciar os containers
echo "🔨 Construindo e iniciando containers..."
docker-compose up --build -d

# Aguardar os serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 10

# Verificar status dos containers
echo "📊 Status dos containers:"
docker-compose ps

# Mostrar logs do backend
echo "📋 Logs do backend:"
docker-compose logs backend

echo ""
echo "🎉 PROJETO INICIADO COM SUCESSO!"
echo "================================"
echo "🌐 Frontend: http://localhost:3001"
echo "🔧 Backend API: http://localhost:5000/api"
echo "🗄️  MySQL: localhost:3307"
echo "📦 Redis: localhost:6379"
echo ""
echo "📋 Comandos úteis:"
echo "  - Ver logs: docker-compose logs -f"
echo "  - Parar: docker-compose down"
echo "  - Reiniciar: docker-compose restart"
echo "  - Status: docker-compose ps"
