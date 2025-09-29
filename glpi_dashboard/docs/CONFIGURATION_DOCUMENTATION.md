# CONFIGURAÇÃO E DEPLOY - GLPI DASHBOARD

## 📋 VISÃO GERAL

Este documento detalha todas as configurações, variáveis de ambiente, scripts e processos de deploy necessários para executar o GLPI Dashboard em diferentes ambientes.

## 🔧 VARIÁVEIS DE AMBIENTE

### **Frontend (.env)**
```bash
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=10000

# Environment
VITE_NODE_ENV=development
VITE_DEBUG=true

# Features
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG_TOOLS=true
```

### **Backend (.env)**
```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
DEBUG=false
FLASK_ENV=production

# GLPI Configuration
GLPI_URL=http://your-glpi-server/glpi
GLPI_USER_TOKEN=your-user-token
GLPI_APP_TOKEN=your-app-token

# Cache Configuration
CACHE_TYPE=SimpleCache
CACHE_DEFAULT_TIMEOUT=300
REDIS_URL=redis://localhost:6379/0

# Database (opcional)
DATABASE_URL=postgresql://user:password@localhost:5432/glpi_dashboard

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=structured

# Security
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
RATE_LIMIT=1000
```

## 📁 ESTRUTURA DE CONFIGURAÇÃO

### **Arquivos de Configuração**
```
glpi_dashboard/
├── .env.example              # Exemplo de variáveis de ambiente
├── .env                      # Variáveis de ambiente (não versionado)
├── docker-compose.yml        # Configuração Docker
├── docker.env               # Variáveis para Docker
├── requirements.txt         # Dependências Python
├── package.json             # Dependências Node.js
├── pyproject.toml           # Configuração Python
├── tailwind.config.js       # Configuração Tailwind CSS
├── vite.config.ts           # Configuração Vite
├── tsconfig.json            # Configuração TypeScript
└── nginx.conf               # Configuração Nginx
```

## 🐳 CONFIGURAÇÃO DOCKER

### **docker-compose.yml**
```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=http://backend:8000
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - GLPI_URL=${GLPI_URL}
      - GLPI_USER_TOKEN=${GLPI_USER_TOKEN}
      - GLPI_APP_TOKEN=${GLPI_APP_TOKEN}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend

volumes:
  redis_data:
```

### **Dockerfile Frontend**
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### **Dockerfile Backend**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

## 🚀 SCRIPTS DE AUTOMAÇÃO

### **setup.sh (Linux/macOS)**
```bash
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
cd frontend
npm install
npm run build
cd ..

# Configurar backend
echo "🐍 Configurando backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
cd ..

# Configurar variáveis de ambiente
echo "⚙️ Configurando variáveis de ambiente..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Arquivo .env criado. Configure as variáveis necessárias."
fi

echo "✅ Configuração concluída!"
echo "🔧 Configure as variáveis no arquivo .env"
echo "🚀 Execute: npm run dev (frontend) e python app.py (backend)"
```

### **setup.bat (Windows)**
```batch
@echo off
echo 🚀 Configurando GLPI Dashboard...

REM Verificar dependências
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js não encontrado. Instale Node.js 18+ primeiro.
    exit /b 1
)

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado. Instale Python 3.12+ primeiro.
    exit /b 1
)

REM Configurar frontend
echo 📦 Configurando frontend...
cd frontend
npm install
npm run build
cd ..

REM Configurar backend
echo 🐍 Configurando backend...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r ..\requirements.txt
cd ..

REM Configurar variáveis de ambiente
echo ⚙️ Configurando variáveis de ambiente...
if not exist .env (
    copy .env.example .env
    echo 📝 Arquivo .env criado. Configure as variáveis necessárias.
)

echo ✅ Configuração concluída!
echo 🔧 Configure as variáveis no arquivo .env
echo 🚀 Execute: npm run dev (frontend) e python app.py (backend)
```

### **deploy.sh**
```bash
#!/bin/bash

echo "🚀 Deploying GLPI Dashboard..."

# Build frontend
echo "📦 Building frontend..."
cd frontend
npm run build
cd ..

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
```

## 🔧 CONFIGURAÇÕES ESPECÍFICAS

### **Nginx Configuration**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    server {
        listen 80;
        server_name localhost;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

### **Tailwind CSS Config**
```javascript
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
    "./index.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        level: {
          n1: '#10b981',
          n2: '#3b82f6',
          n3: '#f59e0b',
          n4: '#ef4444',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
  darkMode: 'class',
}
```

### **Vite Config**
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['lucide-react']
        }
      }
    }
  }
})
```

## 🧪 CONFIGURAÇÃO DE TESTES

### **Vitest Config**
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
      ]
    }
  }
})
```

### **Playwright Config**
```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './src/test/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

## 🔒 CONFIGURAÇÃO DE SEGURANÇA

### **CORS Configuration**
```python
from flask_cors import CORS

CORS(app, origins=[
    "http://localhost:3000",
    "http://localhost:5173",
    "https://your-domain.com"
])
```

### **Rate Limiting**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

@app.route('/api/metrics')
@limiter.limit("100 per minute")
def get_metrics():
    pass
```

## 📊 CONFIGURAÇÃO DE MONITORAMENTO

### **Prometheus Metrics**
```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Métricas customizadas
metrics.register_default(
    metrics.counter(
        'http_requests_total',
        'Total HTTP requests',
        labels={'method': lambda r: r.method, 'endpoint': lambda r: r.endpoint}
    )
)
```

### **Health Check**
```python
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'services': {
            'api': 'ok',
            'glpi': check_glpi_connection(),
            'cache': check_cache_status()
        }
    }
```

## 🚀 PROCESSO DE DEPLOY

### **Desenvolvimento**
1. Clone o repositório
2. Execute `./setup.sh` (Linux/macOS) ou `setup.bat` (Windows)
3. Configure as variáveis no `.env`
4. Execute `npm run dev` (frontend) e `python app.py` (backend)

### **Produção com Docker**
1. Configure as variáveis de ambiente
2. Execute `./deploy.sh`
3. Acesse http://localhost:3000

### **Produção Manual**
1. Build do frontend: `npm run build`
2. Configure o servidor web (Nginx/Apache)
3. Execute o backend com Gunicorn
4. Configure proxy reverso

## ✅ CHECKLIST DE CONFIGURAÇÃO

### **Frontend**
- [ ] Node.js 18+ instalado
- [ ] Dependências instaladas (`npm install`)
- [ ] Build funcionando (`npm run build`)
- [ ] Variáveis de ambiente configuradas
- [ ] Proxy para API configurado

### **Backend**
- [ ] Python 3.12+ instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Servidor rodando (`python app.py`)
- [ ] Conexão com GLPI funcionando
- [ ] Cache configurado

### **Docker (opcional)**
- [ ] Docker e Docker Compose instalados
- [ ] Imagens construídas
- [ ] Containers rodando
- [ ] Volumes configurados

### **Produção**
- [ ] Servidor web configurado
- [ ] SSL/TLS configurado
- [ ] Monitoramento ativo
- [ ] Backup configurado
- [ ] Logs centralizados

## 🆘 TROUBLESHOOTING

### **Problemas Comuns**

#### **Frontend não carrega**
- Verificar se o build foi executado
- Verificar configuração do proxy
- Verificar variáveis de ambiente

#### **Backend não responde**
- Verificar se a porta 8000 está livre
- Verificar conexão com GLPI
- Verificar logs de erro

#### **Cache não funciona**
- Verificar se Redis está rodando
- Verificar configuração de fallback
- Verificar TTL das chaves

#### **Docker não inicia**
- Verificar se as portas estão livres
- Verificar configuração do docker-compose
- Verificar logs dos containers

## ✅ CONCLUSÃO

Esta documentação fornece todas as configurações necessárias para executar o GLPI Dashboard em diferentes ambientes. Siga o checklist de configuração e consulte a seção de troubleshooting em caso de problemas.

**Status:** ✅ CONFIGURAÇÃO COMPLETA E DOCUMENTADA
