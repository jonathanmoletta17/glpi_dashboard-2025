# GLPI Dashboard - Sistema de Monitoramento e Análise

![Status](https://img.shields.io/badge/status-funcional-brightgreen)
![Versão](https://img.shields.io/badge/versão-1.0.0-blue)
![Checkpoint](https://img.shields.io/badge/checkpoint-14e24c3-orange)

Sistema completo de dashboard para monitoramento e análise de tickets do GLPI, com interface moderna e responsiva.

## 🚀 Características Principais

- **Interface Moderna**: Design responsivo com modo escuro/claro
- **Dashboard Interativo**: Métricas em tempo real com gráficos dinâmicos
- **Ranking de Técnicos**: Sistema de performance e estatísticas
- **API REST**: Backend robusto com cache inteligente
- **Sistema de Cores Dinâmico**: Indicadores visuais por nível de prioridade
- **Responsividade**: Otimizado para desktop, tablet e mobile

## 🏗️ Arquitetura

### Stack Tecnológica

**Frontend**
- React 18 com TypeScript
- Vite para build e desenvolvimento
- Tailwind CSS para estilização
- Hooks customizados para gerenciamento de estado

**Backend**
- Flask 2.3.3 com Python 3.11+
- Cache inteligente (SimpleCache/Redis)
- Logging estruturado para observabilidade
- APIs REST para integração

**DevOps**
- Docker para containerização
- Scripts automatizados de deploy
- GitHub Actions para CI/CD

### Padrão de Arquitetura
- **Microservices + SPA**: Backend API + Frontend separado
- **Cache Híbrido**: Sistema inteligente de cache com fallback
- **Logging Estruturado**: Observabilidade completa do sistema

## 📁 Estrutura do Projeto

```
glpi_dashboard_funcional/
├── glpi_dashboard/           # Aplicação principal
│   ├── backend/              # Backend Flask
│   │   ├── api/              # Endpoints da API
│   │   ├── config/           # Configurações centralizadas
│   │   ├── schemas/          # Schemas de validação
│   │   ├── services/         # Serviços de integração
│   │   └── utils/            # Utilitários
│   ├── frontend/             # Frontend React + TypeScript
│   │   ├── src/              # Código fonte
│   │   │   ├── components/   # Componentes React
│   │   │   ├── hooks/        # Hooks customizados
│   │   │   ├── services/     # Serviços do frontend
│   │   │   ├── types/        # Definições TypeScript
│   │   │   └── utils/        # Utilitários
│   │   ├── package.json      # Dependências Node.js
│   │   └── vite.config.ts    # Configuração Vite
│   ├── docs/                 # Documentação técnica
│   └── scripts/              # Scripts auxiliares
├── docs/                     # Documentação geral
├── scripts/                  # Scripts de automação
└── README.md                 # Este arquivo
```

## ⚡ Início Rápido

### Pré-requisitos
- Python 3.11+
- Node.js 16+
- npm ou yarn
- Acesso ao GLPI com tokens de API

### Instalação Automática

**Windows:**
```bash
.\install.bat
```

**Linux/macOS:**
```bash
./install.sh
```

### Instalação Manual

#### 1. Clone e Configuração Inicial
```bash
git clone <repository-url>
cd glpi_dashboard_funcional
cp .env.example .env
```

#### 2. Backend (Flask)
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows
.\venv\Scripts\Activate.ps1
# Linux/Mac
source venv/bin/activate

# Instalar dependências
cd glpi_dashboard
pip install -r requirements.txt

# Executar backend
python app.py
```

#### 3. Frontend (React)
```bash
# Em novo terminal
cd glpi_dashboard/frontend
npm install
npm run dev
```

## ⚙️ Configuração

### Variáveis de Ambiente

**Arquivo raiz `.env`:**
```bash
# GLPI Configuration
GLPI_URL=http://your-glpi-server/glpi/apirest.php
GLPI_USER_TOKEN=your-user-token
GLPI_APP_TOKEN=your-app-token

# Flask Configuration
FLASK_ENV=dev
SECRET_KEY=your-secret-key
FLASK_DEBUG=true
HOST=0.0.0.0
PORT=5000

# Logging
LOG_LEVEL=INFO
```

**Frontend `.env` (glpi_dashboard/frontend/.env):**
```bash
VITE_API_BASE_URL=http://localhost:5000/api
VITE_LOG_LEVEL=info
```

### Configuração do GLPI

1. Acesse seu GLPI
2. Vá em **Configuração > API**
3. Gere um **User Token** e **App Token**
4. Configure as URLs e tokens no arquivo `.env`

## 🚀 Deploy

### Docker (Recomendado)
```bash
./deploy.sh
```

### Manual
```bash
# Frontend
cd glpi_dashboard/frontend
npm run build

# Backend
cd glpi_dashboard
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🔧 Desenvolvimento

### Scripts Disponíveis

**Frontend:**
```bash
npm run dev          # Servidor de desenvolvimento
npm run build        # Build de produção
npm run preview      # Preview do build
npm run test         # Executar testes
```

**Backend:**
```bash
python app.py        # Servidor de desenvolvimento
pytest              # Executar testes
python run_scripts.py # Scripts auxiliares
```

### Scripts Auxiliares

O projeto inclui scripts organizados para debug, testes e validação:

```bash
# Listar scripts disponíveis
python run_scripts.py

# Scripts de debug
python run_scripts.py debug metrics
python run_scripts.py debug trends

# Scripts de validação
python run_scripts.py validation frontend_trends
python run_scripts.py validation trends_math
```

## 📊 Funcionalidades

### Dashboard Principal
- **Métricas Gerais**: Novos, pendentes, em progresso, resolvidos
- **Métricas por Nível**: N1, N2, N3, N4 com cores dinâmicas
- **Ranking de Técnicos**: Performance e estatísticas
- **Filtros de Data**: Análise temporal dos dados

### Sistema de Cores Dinâmico
- **N1 (Verde)**: Sucesso e alta performance
- **N2 (Azul)**: Informação e status normal
- **N3 (Amarelo)**: Atenção e alertas
- **N4 (Vermelho)**: Crítico e urgente

### Modo Escuro
- **Toggle Automático**: Baseado na preferência do sistema
- **Persistência**: Lembra a preferência do usuário
- **Transições Suaves**: Animações fluidas entre temas

## 🌐 Endpoints da API

### Principais Endpoints

```
GET /api/metrics     # Métricas do dashboard
GET /api/status      # Status do sistema
GET /api/health      # Health check
```

**Acesso à Documentação:**
- **Frontend**: `http://localhost:3001`
- **Backend API**: `http://localhost:5000`
- **API Status**: `http://localhost:5000/api/status`

## 🧪 Testes

```bash
# Frontend
cd glpi_dashboard/frontend
npm run test

# Backend
cd glpi_dashboard
pytest
```

## 📈 Monitoramento

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Métricas
- **Performance**: Tempo de resposta, throughput
- **Cache**: Hit rate, miss rate
- **GLPI**: Conectividade e latência
- **Sistema**: Uso de recursos

## 🔒 Segurança

- **CORS** configurado para domínios específicos
- **Rate Limiting** para proteção contra abuso
- **Validação** de entrada em todas as APIs
- **Logs de auditoria** para rastreabilidade

## 🆘 Troubleshooting

### Problemas Comuns

#### Frontend não carrega
1. Verifique se o build foi executado: `npm run build`
2. Verifique a configuração do proxy no `vite.config.ts`
3. Verifique as variáveis de ambiente

#### Backend não responde
1. Verifique se a porta 5000 está livre
2. Verifique a conexão com GLPI
3. Verifique os logs: `tail -f logs/app.log`

#### Cache não funciona
1. Verifique se Redis está rodando (opcional)
2. O sistema usa SimpleCache como fallback
3. Verifique a configuração de TTL

## 📚 Documentação

- **[Checkpoint Funcional](CHECKPOINT_FUNCIONAL_DOCUMENTATION.md)** - Detalhes do checkpoint estável
- **[Arquitetura Frontend](FRONTEND_ARCHITECTURE_DOCUMENTATION.md)** - Documentação completa do frontend
- **[Arquitetura Backend](BACKEND_ARCHITECTURE_DOCUMENTATION.md)** - Documentação completa do backend
- **[Configuração e Deploy](CONFIGURATION_DOCUMENTATION.md)** - Guias de configuração e deploy
- **[BYTEROVER Handbook](BYTEROVER.md)** - Guia técnico completo

## 🤝 Contribuição

Este é um repositório estável. Para contribuições e desenvolvimento ativo, use o repositório principal.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🏷️ Versão

**Versão Estável**: 1.0.0
**Checkpoint**: `14e24c3`
**Data**: 02/09/2025

## 📞 Suporte

Para suporte e dúvidas:
- Consulte a documentação completa
- Verifique a seção de troubleshooting
- Abra uma issue no repositório principal

---

**Status**: ✅ **FUNCIONAL E PRONTO PARA PRODUÇÃO**

Este repositório representa um checkpoint estável e funcional do GLPI Dashboard, com todas as funcionalidades principais implementadas e testadas.

