# 📚 Documentação Completa das Requisições GLPI API

## 🎯 Visão Geral

Esta documentação serve como **referência definitiva** para todas as requisições implementadas no `glpi_metrics_collector.py`. Ela contém:

- ✅ **Endpoints exatos** utilizados
- ✅ **Parâmetros completos** de cada requisição
- ✅ **Estrutura de resposta** esperada
- ✅ **Tratamento de erros** implementado
- ✅ **Mapeamentos de dados** utilizados
- ✅ **Exemplos práticos** de uso

---

## 🔐 1. AUTENTICAÇÃO

### 1.1 Inicialização de Sessão

**Endpoint:** `POST /apirest.php/initSession`

**Método de Autenticação:** User Token (Recomendado)

```python
# Headers obrigatórios
headers = {
    'Content-Type': 'application/json',
    'App-Token': 'seu_app_token_aqui',
    'Authorization': 'user_token seu_user_token_aqui'
}

# Requisição
url = f"{base_url}/apirest.php/initSession"
response = session.get(url, headers=headers)
```

**Resposta de Sucesso:**
```json
{
    "session_token": "fkegh7v413anh1598a79...",
    "glpi_currenttime": "2025-01-22 22:55:48"
}
```

**Headers para Próximas Requisições:**
```python
session.headers.update({
    'Session-Token': session_token_obtido
})
```

### 1.2 Finalização de Sessão

**Endpoint:** `GET /apirest.php/killSession`

```python
url = f"{base_url}/apirest.php/killSession"
response = session.get(url)
```

---

## 📊 2. MÉTRICAS GERAIS DO SISTEMA

### 2.1 Busca de Todos os Tickets

**Endpoint:** `GET /apirest.php/search/Ticket`

**Parâmetros:**
```python
params = {
    'forcedisplay[0]': 2,    # ID do ticket
    'forcedisplay[1]': 12,   # Status do ticket
    'forcedisplay[2]': 3,    # Prioridade
    'forcedisplay[3]': 15,   # Data de criação
    'range': '0-9999'       # Limite de tickets
}
```

**Estrutura de Resposta:**
```json
{
    "data": [
        {
            "2": "10227",     # ID
            "12": "1",        # Status (1=novo, 2=em_progresso, etc)
            "3": "3",         # Prioridade
            "15": "2025-01-22 10:30:00"  # Data criação
        }
    ]
}
```

**Mapeamento de Status:**
```python
ticket_status = {
    1: 'novo',           # Novo
    2: 'em_progresso',   # Processando (atribuído)
    3: 'planejado',      # Processando (planejado)
    4: 'pendente',       # Pendente
    5: 'solucionado',    # Solucionado
    6: 'fechado'         # Fechado
}
```

---

## 🎫 3. TICKETS NOVOS

### 3.1 Busca de Tickets com Status "Novo"

**Endpoint:** `GET /apirest.php/search/Ticket`

**Parâmetros:**
```python
params = {
    'criteria[0][field]': 12,      # Campo de status
    'criteria[0][searchtype]': 'equals',
    'criteria[0][value]': 1,       # Status "Novo"
    'forcedisplay[0]': 2,          # ID
    'forcedisplay[1]': 1,          # Nome/Título
    'forcedisplay[2]': 12,         # Status
    'forcedisplay[3]': 3,          # Prioridade
    'forcedisplay[4]': 15,         # Data de criação
    'forcedisplay[5]': 5,          # Técnico atribuído
    'order': 'DESC',               # Mais recentes primeiro
    'sort': 15,                    # Ordenar por data de criação
    'range': '0-100'               # Limitar a 100 tickets
}
```

**Estrutura de Resposta:**
```json
{
    "data": [
        {
            "2": "10227",                    # ID
            "1": "Acesso a Sistemas Rede...", # Título
            "12": "1",                       # Status
            "3": "3",                        # Prioridade
            "15": "2025-01-22 10:30:00",     # Data criação
            "5": "1032"                      # Técnico atribuído
        }
    ]
}
```

---

## 🏆 4. RANKING DE TÉCNICOS

### 4.1 Identificação de Técnicos Ativos

**Método:** Lista hardcoded de IDs válidos da entidade CAU

```python
# IDs dos 19 técnicos válidos da entidade CAU
technician_ids = [
    "696", "32", "141", "60", "69", "1032", "252", "721", "926", "1291",
    "185", "1331", "1404", "1088", "1263", "10", "53", "250", "1471"
]
```

### 4.2 Validação de Usuário Ativo

**Endpoint:** `GET /apirest.php/User/{user_id}`

**Filtros Aplicados:**
```python
# Verificar se usuário está ativo e não deletado
is_active = str(user_data.get('is_active', '0')).strip()
is_deleted = str(user_data.get('is_deleted', '0')).strip()

# Critérios de validação
if str(is_active) != '1':  # Deve estar ativo
    return None
    
if str(is_deleted) == '1':  # Não deve estar deletado
    return None
```

**Estrutura de Resposta:**
```json
{
    "id": "1404",
    "name": "gabriel.andrade",
    "firstname": "Gabriel",
    "realname": "Andrade da Conceicao",
    "is_active": "1",
    "is_deleted": "0"
}
```

### 4.3 Determinação de Nível do Técnico

#### 4.3.1 Busca por Grupos GLPI

**Endpoint:** `GET /apirest.php/search/Group_User`

**Parâmetros:**
```python
params = {
    'range': '0-99',
    'criteria[0][field]': '4',  # Campo users_id
    'criteria[0][searchtype]': 'equals',
    'criteria[0][value]': str(user_id),
    'forcedisplay[0]': '3',     # groups_id
    'forcedisplay[1]': '4',     # users_id
}
```

**Mapeamento de Grupos:**
```python
service_levels = {
    'N1': 89,  # CC-SE-SUBADM-DTIC > N1
    'N2': 90,  # CC-SE-SUBADM-DTIC > N2
    'N3': 91,  # CC-SE-SUBADM-DTIC > N3
    'N4': 92,  # CC-SE-SUBADM-DTIC > N4
}
```

#### 4.3.2 Fallback por Nome (Mapeamento Hardcoded)

**Mapeamento Exato dos Técnicos por Nível:**

```python
# N1 - Técnicos Júnior
n1_names = [
    "gabriel andrade da conceicao",
    "nicolas fernando muniz nunez",
]

# N2 - Técnicos Pleno
n2_names = [
    "alessandro carbonera vieira",
    "jonathan nascimento moletta",
    "thales vinicius paz leite",
    "leonardo trojan repiso riela",
    "edson joel dos santos silva",
    "luciano marcelino da silva",
]

# N3 - Técnicos Sênior
n3_names = [
    "anderson da silva morim de oliveira",
    "silvio godinho valim",
    "jorge antonio vicente júnior",
    "pablo hebling guimaraes",
    "miguelangelo ferreira",
]

# N4 - Técnicos Especialista
n4_names = [
    "gabriel silva machado",
    "luciano de araujo silva",
    "wagner mengue",
    "paulo césar pedó nunes",
    "alexandre rovinski almoarqueg",
]
```

**Lógica de Verificação:**
```python
# Construir nome completo
full_name = f"{firstname} {realname}".strip()

# Verificar em ordem decrescente (N4 -> N1)
if full_name in n4_names:
    return "N4"
elif full_name in n3_names:
    return "N3"
elif full_name in n2_names:
    return "N2"
elif full_name in n1_names:
    return "N1"
else:
    return "N1"  # Padrão
```

### 4.4 Cálculo de Métricas do Técnico

**Endpoint:** `GET /apirest.php/search/Ticket`

**Parâmetros:**
```python
params = {
    'criteria[0][field]': 5,       # Campo técnico atribuído
    'criteria[0][searchtype]': 'equals',
    'criteria[0][value]': tecnico_id,
    'forcedisplay[0]': 2,          # ID
    'forcedisplay[1]': 12,         # Status
    'range': '0-1000'
}
```

**Cálculo de Métricas:**
```python
total = len(tickets)
resolvidos = 0
pendentes = 0

for ticket in tickets:
    status_id = int(ticket.get('12', 0))
    
    if status_id in [5, 6]:  # Solucionado ou Fechado
        resolvidos += 1
    elif status_id in [2, 3, 4]:  # Em progresso, Planejado, Pendente
        pendentes += 1

taxa_resolucao = (resolvidos / total * 100) if total > 0 else 0
```

---

## 📈 5. STATUS POR NÍVEL

### 5.1 Busca de Tickets por Grupo

**Endpoint:** `GET /apirest.php/search/Ticket`

**Parâmetros por Nível:**
```python
# Para cada nível (N1, N2, N3, N4)
params = {
    'criteria[0][field]': 8,       # Campo do grupo atribuído (Groups_id)
    'criteria[0][searchtype]': 'equals',
    'criteria[0][value]': group_id,  # 89, 90, 91, 92
    'forcedisplay[0]': 12,         # Status
    'forcedisplay[1]': 2,          # ID do ticket
    'range': '0-9999'              # Aumentar limite
}
```

**Mapeamento de Grupos por Nível:**
```python
service_levels = {
    'N1': 89,  # CC-SE-SUBADM-DTIC > N1
    'N2': 90,  # CC-SE-SUBADM-DTIC > N2
    'N3': 91,  # CC-SE-SUBADM-DTIC > N3
    'N4': 92,  # CC-SE-SUBADM-DTIC > N4
}
```

**Contagem por Status:**
```python
status_map = {
    1: 'novo',
    2: 'em_progresso', 
    3: 'planejado',
    4: 'pendente',
    5: 'solucionado',
    6: 'fechado'
}

# Para cada ticket
status_id = int(ticket.get('12', 0))
status_name = status_map.get(status_id, 'novo')
status_por_nivel[nivel][status_name] += 1
```

---

## 🔧 6. CONFIGURAÇÃO E VARIÁVEIS DE AMBIENTE

### 6.1 Variáveis Obrigatórias

```bash
# URL base do GLPI
GLPI_BASE_URL="http://cau.ppiratini.intra.rs.gov.br/glpi"

# Token da aplicação
GLPI_APP_TOKEN="aY3f9F5aNHJmY8op0vTE4koguiPwpEYANp1JULid"

# Token do usuário
GLPI_USER_TOKEN="TQdSxqg2e56PfF8ZJSX3iEJ1wCpHwhCkQJ2QtRnq"
```

### 6.2 Headers Padrão

```python
session.headers.update({
    'Content-Type': 'application/json',
    'App-Token': self.config.app_token,
    'Session-Token': self.session_token  # Adicionado após login
})
```

---

## 🚨 7. TRATAMENTO DE ERROS

### 7.1 Erros de Autenticação

```python
try:
    response = self.session.get(url, headers=headers)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"❌ Erro na autenticação: {e}")
    return False
except json.JSONDecodeError as e:
    print(f"❌ Erro ao decodificar resposta: {e}")
    return False
```

### 7.2 Erros de Requisição

```python
try:
    response = self.session.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    if not data or 'data' not in data:
        return []
        
except requests.exceptions.RequestException as e:
    print(f"❌ Erro na requisição: {e}")
    return []
except json.JSONDecodeError as e:
    print(f"❌ Erro ao decodificar JSON: {e}")
    return []
```

### 7.3 Validação de Dados

```python
# Verificar se resposta contém dados válidos
if not response.ok:
    print(f"❌ Status HTTP inválido: {response.status_code}")
    return None

data = response.json()
if not isinstance(data, dict) or 'data' not in data:
    print("❌ Estrutura de resposta inválida")
    return None
```

---

## 📋 8. ESTRUTURA DE DADOS DE SAÍDA

### 8.1 Métricas Gerais

```json
{
    "total_tickets": 10000,
    "status_breakdown": {
        "novo": 2,
        "em_progresso": 25,
        "planejado": 14,
        "pendente": 50,
        "solucionado": 3213,
        "fechado": 6696
    },
    "timestamp": "2025-01-22T22:55:48.123456",
    "endpoint_used": "http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php/search/Ticket"
}
```

### 8.2 Tickets Novos

```json
[
    {
        "id": "10227",
        "titulo": "Acesso a Sistemas Rede Piratini...",
        "status": "novo",
        "prioridade": "3",
        "data_criacao": "2025-01-22 10:30:00",
        "tecnico_atribuido": "1032"
    }
]
```

### 8.3 Ranking de Técnicos

```json
{
    "N1": [
        {
            "id": "1404",
            "nome": "Gabriel Andrade da Conceicao",
            "nivel": "N1",
            "grupo_id": 89,
            "posicao": 1,
            "tickets_total": 61,
            "tickets_resolvidos": 59,
            "tickets_pendentes": 2,
            "taxa_resolucao": 96.7
        }
    ],
    "N2": [...],
    "N3": [...],
    "N4": [...]
}
```

### 8.4 Status por Nível

```json
{
    "N1": {
        "novo": 0,
        "em_progresso": 5,
        "planejado": 3,
        "pendente": 2,
        "solucionado": 527,
        "fechado": 934
    },
    "N2": {...},
    "N3": {...},
    "N4": {...}
}
```

---

## 🎯 9. CHECKLIST DE IMPLEMENTAÇÃO

### 9.1 Configuração Inicial

- [ ] Configurar variáveis de ambiente
- [ ] Validar tokens de autenticação
- [ ] Testar conectividade com GLPI

### 9.2 Autenticação

- [ ] Implementar `initSession`
- [ ] Armazenar `session_token`
- [ ] Implementar `killSession`

### 9.3 Coleta de Dados

- [ ] Métricas gerais (todos os tickets)
- [ ] Tickets novos (status = 1)
- [ ] Identificação de técnicos ativos
- [ ] Determinação de níveis
- [ ] Cálculo de métricas por técnico
- [ ] Status por nível de atendimento

### 9.4 Validação

- [ ] Verificar estrutura de respostas
- [ ] Validar mapeamentos de dados
- [ ] Testar tratamento de erros
- [ ] Confirmar contagens de tickets

---

## 🔍 10. DEBUGGING E TROUBLESHOOTING

### 10.1 Problemas Comuns

**Erro: "Session token não recebido"**
- Verificar se `GLPI_APP_TOKEN` está correto
- Verificar se `GLPI_USER_TOKEN` está correto
- Verificar conectividade com GLPI

**Erro: "Nenhum técnico ativo encontrado"**
- Verificar se os IDs dos técnicos estão corretos
- Verificar se `is_active=1` e `is_deleted=0`
- Verificar se usuários existem no GLPI

**Erro: "Nível não determinado"**
- Verificar se técnico está nos grupos 89-92
- Verificar mapeamento de nomes no fallback
- Verificar se nome está sendo construído corretamente

### 10.2 Logs de Debug

```python
# Adicionar logs detalhados
print(f"[DEBUG] Buscando técnico ID: {tech_id}")
print(f"[DEBUG] Resposta GLPI: {response.status_code}")
print(f"[DEBUG] Dados recebidos: {data}")
print(f"[DEBUG] Nível determinado: {nivel}")
```

---

## 📚 11. REFERÊNCIAS

### 11.1 Documentação GLPI

- [GLPI REST API Documentation](https://glpi-developer-documentation.readthedocs.io/en/master/api/rest.html)
- [GLPI API Authentication](https://glpi-developer-documentation.readthedocs.io/en/master/api/rest.html#authentication)

### 11.2 Arquivos de Referência

- `glpi_metrics_collector.py` - Implementação completa
- `glpi_dashboard/backend/services/glpi_service.py` - Backend original
- `glpi_dashboard/backend/api/routes.py` - Endpoints da API

---

## ✅ 12. CONCLUSÃO

Esta documentação serve como **referência definitiva** para implementação de requisições GLPI API. Ela contém todos os detalhes necessários para:

1. **Implementar** novas funcionalidades
2. **Corrigir** problemas existentes
3. **Manter** consistência com o backend
4. **Debuggar** problemas de integração

**Última atualização:** 22 de Janeiro de 2025  
**Versão:** 1.0  
**Status:** ✅ Validado e Funcional
