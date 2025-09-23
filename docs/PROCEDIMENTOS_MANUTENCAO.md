# PROCEDIMENTOS DE MANUTENÇÃO - GLPI DASHBOARD

**Data:** 06 de Janeiro de 2025  
**Versão:** 2.0 (Pós-Simplificação)  
**Objetivo:** Procedimentos simplificados para manutenção do sistema

---

## 🎯 FILOSOFIA DE MANUTENÇÃO

### Princípios Fundamentais:
- 🎯 **SIMPLICIDADE ACIMA DE TUDO** - Se é complexo, está errado
- 🔧 **MANUTENÇÃO PREVENTIVA** - Evitar problemas antes que aconteçam
- 📊 **MONITORAMENTO ESSENCIAL** - Apenas o que realmente importa
- 🚀 **CORREÇÕES RÁPIDAS** - Problemas devem ser resolvidos em minutos
- 📚 **DOCUMENTAÇÃO VIVA** - Sempre atualizada e útil

### Regra de Ouro:
> **"Se você não consegue explicar em 2 minutos como funciona, está muito complexo!"**

---

## 🏗️ ARQUITETURA SIMPLIFICADA

### Componentes Essenciais:
```
GLPI Dashboard
├── Frontend (React)           # Interface única, sem scroll
├── Backend (Flask)            # API com 5 endpoints essenciais
├── Cache (simple_dict_cache)  # Cache em memória simples
└── GLPI Connection           # Conexão direta com GLPI
```

### Fluxo de Dados:
```
Usuário → Frontend → API Flask → Cache → GLPI → Resposta
```

**Tempo Total:** < 500ms para qualquer operação

---

## 🔍 MONITORAMENTO DIÁRIO

### ✅ CHECKLIST DIÁRIO (5 minutos)

#### 1. Verificação de Saúde
```bash
# Teste rápido da API
curl http://localhost:8000/api/health

# Resposta esperada:
{
  "status": "healthy",
  "glpi_connection": "ok",
  "response_time": "<200ms"
}
```

#### 2. Verificação do Frontend
```bash
# Acesse o dashboard
http://localhost:3000

# Verificar:
✅ Página carrega em < 3 segundos
✅ Métricas são exibidas
✅ Não há erros no console
```

#### 3. Verificação de Logs
```bash
# Verificar logs do backend
tail -n 50 backend/logs/app.log

# Procurar por:
❌ ERROR - Erros críticos
⚠️ WARNING - Avisos importantes
✅ INFO - Funcionamento normal
```

#### 4. Verificação de Performance
```bash
# Teste de tempo de resposta
time curl http://localhost:8000/api/metrics

# Deve ser < 500ms
```

### 📊 Métricas de Saúde:
- ✅ **API Response Time:** < 500ms
- ✅ **Frontend Load Time:** < 3s
- ✅ **GLPI Connection:** < 200ms
- ✅ **Cache Hit Rate:** > 80%
- ✅ **Error Rate:** < 1%

---

## 🚨 RESOLUÇÃO DE PROBLEMAS

### Problema 1: API Não Responde
**Sintomas:** Dashboard não carrega, erro 500

**Diagnóstico:**
```bash
# 1. Verificar se o processo está rodando
ps aux | grep uvicorn

# 2. Verificar logs
tail -n 100 backend/logs/app.log

# 3. Testar conexão GLPI
curl http://localhost:8000/api/health/glpi
```

**Soluções:**
```bash
# Solução 1: Reiniciar API
cd backend
python -m uvicorn asgi:asgi_app --reload --host 0.0.0.0 --port 8000

# Solução 2: Limpar cache
rm -rf __pycache__/
rm -rf .pytest_cache/

# Solução 3: Verificar dependências
pip install -r requirements.txt
```

**Tempo de Resolução:** < 5 minutos

### Problema 2: Dados Não Atualizando
**Sintomas:** Métricas antigas, dados desatualizados

**Diagnóstico:**
```bash
# 1. Verificar cache
curl http://localhost:8000/api/metrics
# Verificar timestamp na resposta

# 2. Testar conexão GLPI direta
# (verificar se GLPI está respondendo)
```

**Soluções:**
```bash
# Solução 1: Limpar cache manualmente
# (reiniciar a API limpa o cache automaticamente)

# Solução 2: Verificar configuração GLPI
# Verificar arquivo config/settings.py

# Solução 3: Testar conectividade
ping [GLPI_SERVER_IP]
telnet [GLPI_SERVER_IP] [GLPI_PORT]
```

**Tempo de Resolução:** < 3 minutos

### Problema 3: Frontend Não Carrega
**Sintomas:** Página em branco, erro no navegador

**Diagnóstico:**
```bash
# 1. Verificar se o processo está rodando
ps aux | grep node

# 2. Verificar logs do frontend
npm run dev
# Observar mensagens de erro

# 3. Verificar console do navegador
# F12 → Console → Procurar erros
```

**Soluções:**
```bash
# Solução 1: Reiniciar frontend
cd frontend
npm run dev

# Solução 2: Limpar cache do npm
npm cache clean --force
rm -rf node_modules/
npm install

# Solução 3: Verificar porta
# Verificar se porta 3000 está livre
netstat -tulpn | grep 3000
```

**Tempo de Resolução:** < 5 minutos

### Problema 4: Performance Lenta
**Sintomas:** Dashboard demora para carregar

**Diagnóstico:**
```bash
# 1. Medir tempo de resposta
time curl http://localhost:8000/api/metrics

# 2. Verificar uso de CPU/Memória
top -p $(pgrep -f uvicorn)

# 3. Verificar logs de performance
grep "slow" backend/logs/app.log
```

**Soluções:**
```bash
# Solução 1: Reiniciar serviços
# (limpa cache e reconecta)

# Solução 2: Verificar conexão GLPI
# (pode estar lenta)

# Solução 3: Otimizar consultas
# (verificar se queries GLPI estão eficientes)
```

**Tempo de Resolução:** < 10 minutos

---

## 🔧 MANUTENÇÃO SEMANAL

### ✅ CHECKLIST SEMANAL (15 minutos)

#### 1. Limpeza de Logs
```bash
# Manter apenas últimos 7 dias
find backend/logs/ -name "*.log" -mtime +7 -delete

# Rotacionar logs grandes
if [ $(stat -f%z backend/logs/app.log) -gt 10485760 ]; then
    mv backend/logs/app.log backend/logs/app.log.old
    touch backend/logs/app.log
fi
```

#### 2. Verificação de Dependências
```bash
# Backend
cd backend
pip list --outdated

# Frontend
cd frontend
npm outdated

# Atualizar apenas se necessário (segurança)
```

#### 3. Backup de Configurações
```bash
# Backup simples
cp config/settings.py config/settings.py.backup.$(date +%Y%m%d)
cp frontend/src/config.js frontend/src/config.js.backup.$(date +%Y%m%d)

# Manter apenas últimos 4 backups
ls -t config/settings.py.backup.* | tail -n +5 | xargs rm -f
```

#### 4. Teste de Funcionalidades
```bash
# Teste automatizado simples
curl -s http://localhost:8000/api/health | jq '.status'
curl -s http://localhost:8000/api/metrics | jq '.total_tickets'
curl -s http://localhost:8000/api/technicians | jq '.total'

# Todos devem retornar dados válidos
```

---

## 🔄 MANUTENÇÃO MENSAL

### ✅ CHECKLIST MENSAL (30 minutos)

#### 1. Análise de Performance
```bash
# Analisar logs do último mês
grep "ERROR" backend/logs/app.log.* | wc -l
grep "WARNING" backend/logs/app.log.* | wc -l

# Meta: < 10 erros por mês
```

#### 2. Otimização de Cache
```bash
# Verificar estatísticas de cache
# (implementar endpoint simples se necessário)
curl http://localhost:8000/api/health | jq '.cache_stats'

# Meta: > 80% hit rate
```

#### 3. Revisão de Configurações
```bash
# Verificar se configurações ainda fazem sentido
cat config/settings.py

# Verificar:
✅ URLs do GLPI corretas
✅ Timeouts adequados
✅ Cache TTL apropriado
```

#### 4. Documentação
```bash
# Verificar se documentação está atualizada
# Atualizar este arquivo se necessário
```

---

## 🚀 PROCEDIMENTOS DE DEPLOY

### Deploy Simples (Desenvolvimento)
```bash
# 1. Parar serviços
killall uvicorn
killall node

# 2. Atualizar código
git pull origin main

# 3. Instalar dependências (se necessário)
cd backend && pip install -r requirements.txt
cd frontend && npm install

# 4. Iniciar serviços
cd backend && python -m uvicorn asgi:asgi_app --reload --host 0.0.0.0 --port 8000 &
cd frontend && npm run dev &

# 5. Verificar funcionamento
sleep 10
curl http://localhost:8000/api/health
```

### Deploy Produção (Se necessário)
```bash
# 1. Backup atual
cp -r . ../backup_$(date +%Y%m%d_%H%M%S)

# 2. Deploy com zero downtime
# (usar PM2 ou similar se necessário)

# 3. Verificação pós-deploy
curl http://[PRODUCTION_URL]/api/health
```

---

## 📋 LOGS E AUDITORIA

### Estrutura de Logs:
```
backend/logs/
├── app.log              # Log principal
├── error.log            # Apenas erros
└── access.log           # Logs de acesso (se necessário)
```

### Formato de Log Padrão:
```json
{
  "timestamp": "2025-01-06T10:30:00Z",
  "level": "INFO",
  "message": "Metrics fetched successfully",
  "module": "routes",
  "function": "get_metrics",
  "duration_ms": 150,
  "cache_hit": true
}
```

### Logs Importantes para Monitorar:
- ✅ **Inicialização da API**
- ✅ **Conexões com GLPI**
- ✅ **Erros de autenticação**
- ✅ **Timeouts de requisição**
- ✅ **Cache hits/misses**
- ❌ Logs desnecessários (debug excessivo)

---

## 🔒 SEGURANÇA E BACKUP

### Backup Essencial:
```bash
# Arquivos críticos para backup
config/settings.py       # Configurações
frontend/src/config.js   # Config frontend
backend/logs/           # Logs (últimos 30 dias)

# Backup automático simples
tar -czf backup_$(date +%Y%m%d).tar.gz config/ frontend/src/config.js backend/logs/
```

### Segurança Básica:
- ✅ **Senhas não commitadas** no git
- ✅ **CORS configurado** adequadamente
- ✅ **Logs sem informações sensíveis**
- ✅ **Acesso restrito** aos logs
- ❌ Não implementar segurança excessiva (over-engineering)

---

## 📞 CONTATOS DE EMERGÊNCIA

### Responsáveis:
- **Desenvolvedor Principal:** IA Assistant
- **Administrador GLPI:** [Definir]
- **Suporte Técnico:** [Definir]

### Escalação de Problemas:
1. **Nível 1:** Problemas simples (< 15 min)
2. **Nível 2:** Problemas complexos (< 1 hora)
3. **Nível 3:** Problemas críticos (imediato)

---

## 📈 MÉTRICAS DE SUCESSO

### KPIs de Manutenção:
- ✅ **Uptime:** > 99%
- ✅ **Tempo de Resolução:** < 15 minutos
- ✅ **Problemas Recorrentes:** 0
- ✅ **Satisfação do Usuário:** Alta
- ✅ **Tempo de Manutenção:** < 1 hora/semana

### Relatório Mensal:
```
Mês: Janeiro 2025
- Uptime: 99.8%
- Problemas: 2 (resolvidos em < 10 min)
- Performance: Excelente
- Melhorias: Nenhuma necessária
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

### Após Qualquer Manutenção:
- [ ] API responde em < 500ms
- [ ] Frontend carrega em < 3s
- [ ] Todas as métricas são exibidas
- [ ] Logs não mostram erros
- [ ] Cache funcionando (> 80% hit rate)
- [ ] Conexão GLPI estável
- [ ] Documentação atualizada

### Critérios de Sucesso:
- ✅ **Simplicidade mantida**
- ✅ **Performance adequada**
- ✅ **Zero complexidade desnecessária**
- ✅ **Manutenção < 1 hora/semana**
- ✅ **Problemas resolvidos rapidamente**

---

## 🎯 CONCLUSÃO

### Filosofia Final:
> **"Manutenção deve ser tão simples quanto o sistema que mantemos."**

### Regras de Ouro:
1. **Se é complexo, simplifique**
2. **Se não é usado, remova**
3. **Se não é monitorado, não é importante**
4. **Se demora para resolver, está mal projetado**
5. **Se precisa de manual extenso, está errado**

### Próximos Passos:
1. **Implementar** os procedimentos
2. **Treinar** a equipe (se houver)
3. **Automatizar** o que for possível
4. **Manter** a simplicidade sempre

---

**Última Atualização:** 06/01/2025  
**Próxima Revisão:** 06/02/2025  
**Status:** Ativo e Simplificado ✅