# 🐳 GLPI Dashboard - Docker Setup

## 📋 **PRÉ-REQUISITOS**

- Docker Desktop instalado e rodando
- Docker Compose v2.0+
- Portas disponíveis: 3001, 5000, 3307, 6379

## 🚀 **EXECUÇÃO RÁPIDA**

### **Windows:**
```bash
docker-run.bat
```

### **Linux/Mac:**
```bash
chmod +x docker-run.sh
./docker-run.sh
```

### **Manual:**
```bash
# Construir e iniciar todos os serviços
docker-compose up --build -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

## 🏗️ **ARQUITETURA DOS CONTAINERS**

### **Backend (Flask)**
- **Porta**: 5000
- **URL**: http://localhost:5000/api
- **Dockerfile**: `backend/Dockerfile`
- **Dependências**: MySQL, Redis

### **Frontend (React)**
- **Porta**: 3001
- **URL**: http://localhost:3001
- **Dockerfile**: `frontend/Dockerfile`
- **Dependências**: Backend

### **MySQL Database**
- **Porta**: 3307
- **Database**: glpi_dashboard
- **User**: glpi_user
- **Password**: glpi_password

### **Redis Cache**
- **Porta**: 6379
- **Uso**: Cache de dados da API

## ⚙️ **CONFIGURAÇÃO**

### **Variáveis de Ambiente**
Edite o arquivo `docker.env` para configurar:

```env
# GLPI Configuration
GLPI_URL=http://localhost/glpi
GLPI_USER_TOKEN=your_token_here
GLPI_APP_TOKEN=your_app_token_here

# Database Configuration
DATABASE_URL=mysql+pymysql://glpi_user:glpi_password@mysql:3306/glpi_dashboard

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev_secret_key_change_in_production
```

## 📊 **COMANDOS ÚTEIS**

### **Gerenciamento de Containers**
```bash
# Ver status dos containers
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f backend
docker-compose logs -f frontend

# Reiniciar um serviço
docker-compose restart backend

# Parar todos os serviços
docker-compose down

# Parar e remover volumes
docker-compose down -v
```

### **Desenvolvimento**
```bash
# Entrar no container do backend
docker-compose exec backend bash

# Entrar no container do frontend
docker-compose exec frontend sh

# Executar comandos no backend
docker-compose exec backend python -c "print('Hello from backend')"

# Executar comandos no frontend
docker-compose exec frontend npm run build
```

### **Debugging**
```bash
# Ver logs de erro
docker-compose logs backend | grep ERROR

# Verificar conectividade entre containers
docker-compose exec backend ping mysql
docker-compose exec backend ping redis

# Verificar variáveis de ambiente
docker-compose exec backend env
```

## 🔧 **TROUBLESHOOTING**

### **Problemas Comuns**

#### **1. Porta já em uso**
```bash
# Verificar portas em uso
netstat -tulpn | grep :3001
netstat -tulpn | grep :5000

# Parar serviços que usam as portas
sudo lsof -ti:3001 | xargs kill -9
sudo lsof -ti:5000 | xargs kill -9
```

#### **2. Container não inicia**
```bash
# Ver logs detalhados
docker-compose logs backend

# Reconstruir sem cache
docker-compose build --no-cache backend
```

#### **3. Problemas de conectividade**
```bash
# Verificar rede Docker
docker network ls
docker network inspect glpi_dashboard_glpi_network

# Testar conectividade
docker-compose exec backend curl http://mysql:3306
docker-compose exec backend curl http://redis:6379
```

#### **4. Problemas de permissão**
```bash
# Ajustar permissões (Linux/Mac)
sudo chown -R $USER:$USER .
chmod +x docker-run.sh
```

## 📈 **MONITORAMENTO**

### **Health Checks**
- **Backend**: http://localhost:5000/health
- **Frontend**: http://localhost:3001
- **MySQL**: Porta 3307
- **Redis**: Porta 6379

### **Logs**
```bash
# Logs em tempo real
docker-compose logs -f

# Logs específicos
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mysql
docker-compose logs -f redis
```

## 🎯 **ACESSO AO SISTEMA**

Após iniciar os containers:

1. **Frontend**: http://localhost:3001
2. **Backend API**: http://localhost:5000/api
3. **Health Check**: http://localhost:5000/health

## 🔄 **ATUALIZAÇÕES**

### **Atualizar Código**
```bash
# Parar containers
docker-compose down

# Fazer pull das mudanças
git pull

# Reconstruir e iniciar
docker-compose up --build -d
```

### **Atualizar Dependências**
```bash
# Reconstruir com novas dependências
docker-compose build --no-cache

# Reiniciar serviços
docker-compose up -d
```

## 📝 **NOTAS IMPORTANTES**

1. **Primeira execução**: Pode demorar alguns minutos para baixar as imagens
2. **Desenvolvimento**: Use volumes para hot-reload
3. **Produção**: Configure variáveis de ambiente adequadas
4. **Backup**: Dados do MySQL são persistidos em volumes Docker

---

*Para mais informações, consulte a documentação principal do projeto.*
