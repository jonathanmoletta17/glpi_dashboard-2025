# GLPI Dashboard - Configuração de Ambiente

## Visão Geral

Este projeto utiliza um sistema robusto de configuração de variáveis de ambiente para garantir segurança e flexibilidade entre diferentes ambientes (desenvolvimento, produção).

## Estrutura de Configuração

### Arquivos de Ambiente

- **`docker.env`**: Configurações principais para containers Docker
- **`frontend/.env`**: Configurações específicas do frontend (desenvolvimento)
- **`frontend/.env.example`**: Template das variáveis do frontend
- **`docs/env.example`**: Documentação das variáveis de ambiente

### Frontend (React + Vite)

#### Variáveis Disponíveis

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:5000/api
VITE_API_URL=http://localhost:5000/api

# Development Settings
VITE_LOG_LEVEL=debug
VITE_SHOW_PERFORMANCE=true
VITE_SHOW_API_CALLS=true
VITE_SHOW_CACHE_HITS=true

# API Timeout & Retry
VITE_API_TIMEOUT=30000
VITE_API_RETRY_ATTEMPTS=3
VITE_API_RETRY_DELAY=1000

# Authentication (commented for security)
# VITE_AUTH_CLIENT_ID=your_client_id
# VITE_AUTH_CLIENT_SECRET=your_client_secret
```

#### Implementação

O frontend utiliza:
- **`src/config/environment.ts`**: Configuração centralizada
- **`src/services/httpClient.ts`**: Cliente HTTP com configurações dinâmicas
- **Função `getEnvVar()`**: Carregamento seguro de variáveis

### Backend (Flask + Python)

#### Variáveis Principais

```bash
# GLPI Configuration
GLPI_URL=http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php
GLPI_USER_TOKEN=your_user_token
GLPI_APP_TOKEN=your_app_token

# Database
DATABASE_URL=mysql://user:password@localhost/glpi

# Redis Cache
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your_redis_password

# Flask Settings
FLASK_SECRET_KEY=your_secret_key
FLASK_DEBUG=true
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# API Configuration
API_KEY=your_api_key
API_TIMEOUT=30
BACKEND_API_URL=http://localhost:5000/api

# Security
JWT_SECRET_KEY=your_jwt_secret
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002

# Monitoring
PROMETHEUS_GATEWAY_URL=http://localhost:9091
LOG_LEVEL=INFO
```

#### Implementação

O backend utiliza:
- **`config/settings.py`**: Classe Config com propriedades dinâmicas
- **Função `_get_config_value()`**: Carregamento de YAML ou variáveis de ambiente
- **Validação automática**: Para tipos e valores obrigatórios

## Configuração por Ambiente

### Desenvolvimento

1. **Frontend**: Copie `.env.example` para `.env` e ajuste as URLs
2. **Backend**: Configure `docker.env` com credenciais de desenvolvimento
3. **Execução**:
   ```bash
   # Frontend
   cd frontend
   npm run dev

   # Backend
   cd backend
   python app.py
   ```

### Produção

1. **Docker**: Use `docker.env` com configurações de produção
2. **Build**:
   ```bash
   # Frontend
   cd frontend
   npm run build

   # Docker
   docker-compose up -d
   ```

## Segurança

### Boas Práticas Implementadas

- ✅ Arquivos `.env` no `.gitignore`
- ✅ Templates `.env.example` sem valores sensíveis
- ✅ Validação de variáveis obrigatórias
- ✅ Logs sem exposição de secrets
- ✅ Configuração dinâmica por ambiente

### Variáveis Sensíveis

**NUNCA** commite:
- Tokens de API (GLPI_USER_TOKEN, GLPI_APP_TOKEN)
- Senhas de banco (DATABASE_URL)
- Chaves secretas (JWT_SECRET_KEY, FLASK_SECRET_KEY)
- Credenciais Redis (REDIS_PASSWORD)

## Validação

### Testes Realizados

- ✅ Build do frontend sem erros
- ✅ Carregamento correto das configurações do backend
- ✅ Comunicação frontend-backend funcionando
- ✅ Variáveis de ambiente sendo utilizadas corretamente
- ✅ Aplicação rodando em desenvolvimento (http://localhost:3002/)
- ✅ API backend respondendo (http://localhost:5000/api/health)

### Verificação Manual

```bash
# Verificar configurações do backend
cd backend
python -c "from config.settings import Config; config = Config(); print(f'GLPI_URL: {config.GLPI_URL}'); print(f'DEBUG: {config.DEBUG}')"

# Testar API
Invoke-WebRequest -Uri http://localhost:5000/api/health -Method GET

# Build do frontend
cd frontend
npm run build
```

## Troubleshooting

### Problemas Comuns

1. **Erro de CORS**: Verifique `CORS_ORIGINS` no backend
2. **API não responde**: Confirme `VITE_API_BASE_URL` no frontend
3. **Build falha**: Verifique referências de variáveis no código
4. **Conexão GLPI**: Valide tokens e URL do GLPI

### Logs Úteis

- Frontend: Console do navegador
- Backend: Logs estruturados em JSON
- Docker: `docker-compose logs -f`

## Conclusão

O sistema de configuração está completamente funcional e seguro, permitindo:
- Desenvolvimento local eficiente
- Deploy em produção sem alterações de código
- Manutenção fácil de credenciais
- Monitoramento e debugging adequados

Todas as variáveis de ambiente estão sendo utilizadas corretamente e a aplicação está funcionando conforme esperado.
