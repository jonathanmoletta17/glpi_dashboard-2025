# GLPI Dashboard - Versão Estável

## 🎯 Visão Geral

Este é o repositório estável do **GLPI Dashboard**, um sistema de dashboard moderno e responsivo para visualização de métricas e dados do GLPI. Esta versão representa um checkpoint funcional e estável, pronto para produção.

## ✨ Características Principais

- **🎨 Interface Moderna**: Design responsivo com sistema de cores dinâmico
- **🌙 Modo Escuro**: Suporte completo ao tema escuro
- **📊 Dashboard Interativo**: Métricas em tempo real e visualizações dinâmicas
- **👥 Ranking de Técnicos**: Sistema de ranking e métricas por nível
- **🔧 API REST**: Backend robusto com Flask e cache inteligente
- **📱 Responsivo**: Funciona perfeitamente em desktop, tablet e mobile

## 🚀 Início Rápido

### Pré-requisitos

- **Node.js 18+** (para frontend)
- **Python 3.12+** (para backend)
- **GLPI** configurado e acessível

### Instalação Automática

#### Windows
```bash
setup.bat
```

#### Linux/macOS
```bash
chmod +x setup.sh
./setup.sh
```

### Instalação Manual

#### 1. Frontend
```bash
cd glpi_dashboard/frontend
npm install
npm run build
```

#### 2. Backend
```bash
cd glpi_dashboard/backend
pip install -r ../requirements.txt
python app.py
```

#### 3. Configuração
```bash
# Copie o arquivo de exemplo
cp env.example .env

# Configure as variáveis necessárias
# Edite o arquivo .env com suas configurações do GLPI
```

## ⚙️ Configuração

### Variáveis de Ambiente

Configure as seguintes variáveis no arquivo `.env`:

```bash
# GLPI Configuration
GLPI_URL=http://your-glpi-server/glpi
GLPI_USER_TOKEN=your-user-token
GLPI_APP_TOKEN=your-app-token

# API Configuration
VITE_API_URL=http://localhost:8000
```

### Configuração do GLPI

1. Acesse seu GLPI
2. Vá em **Configuração > API**
3. Gere um **User Token** e **App Token**
4. Configure as URLs e tokens no arquivo `.env`

## 🏗️ Arquitetura

### Frontend
- **React 18** com TypeScript
- **Vite** para build e desenvolvimento
- **Tailwind CSS** para estilização
- **Hooks customizados** para gerenciamento de estado

### Backend
- **Flask 2.3.3** com Python
- **Cache inteligente** (SimpleCache/Redis)
- **Logging estruturado** para observabilidade
- **APIs REST** para integração

## 📚 Documentação

- **[Checkpoint Funcional](CHECKPOINT_FUNCIONAL_DOCUMENTATION.md)** - Detalhes do checkpoint estável
- **[Arquitetura Frontend](FRONTEND_ARCHITECTURE_DOCUMENTATION.md)** - Documentação completa do frontend
- **[Arquitetura Backend](BACKEND_ARCHITECTURE_DOCUMENTATION.md)** - Documentação completa do backend
- **[Configuração e Deploy](CONFIGURATION_DOCUMENTATION.md)** - Guias de configuração e deploy

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
cd glpi_dashboard/backend
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 🔧 Desenvolvimento

### Scripts Disponíveis

```bash
# Frontend
npm run dev          # Servidor de desenvolvimento
npm run build        # Build de produção
npm run preview      # Preview do build

# Backend
python app.py        # Servidor de desenvolvimento
pytest              # Executar testes
```

### Estrutura do Projeto

```
glpi-dashboard-stable/
├── glpi_dashboard/
│   ├── frontend/          # Aplicação React
│   ├── backend/           # API Flask
│   └── requirements.txt   # Dependências Python
├── docs/                  # Documentação
├── scripts/               # Scripts de automação
└── README.md             # Este arquivo
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

## 🧪 Testes

```bash
# Frontend
cd glpi_dashboard/frontend
npm run test

# Backend
cd glpi_dashboard/backend
pytest
```

## 📈 Monitoramento

### Health Check
```bash
curl http://localhost:8000/api/health
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
1. Verifique se a porta 8000 está livre
2. Verifique a conexão com GLPI
3. Verifique os logs: `tail -f logs/app.log`

#### Cache não funciona
1. Verifique se Redis está rodando (opcional)
2. O sistema usa SimpleCache como fallback
3. Verifique a configuração de TTL

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
