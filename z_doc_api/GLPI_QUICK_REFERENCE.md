# ⚡ Referência Rápida - GLPI API

## 🎯 Visão Geral

Esta é uma **referência rápida** para consulta imediata de endpoints, parâmetros e estruturas de dados do GLPI API implementadas no `glpi_metrics_collector.py`.

---

## 🔐 AUTENTICAÇÃO

### Inicializar Sessão
```http
GET /apirest.php/initSession
Headers:
  App-Token: {app_token}
  Authorization: user_token {user_token}
```

### Finalizar Sessão
```http
GET /apirest.php/killSession
Headers:
  Session-Token: {session_token}
```

---

## 📊 ENDPOINTS PRINCIPAIS

### 1. Métricas Gerais
```http
GET /apirest.php/search/Ticket
Params:
  forcedisplay[0]=2    # ID
  forcedisplay[1]=12   # Status
  forcedisplay[2]=3    # Prioridade
  forcedisplay[3]=15   # Data criação
  range=0-9999
```

### 2. Tickets Novos
```http
GET /apirest.php/search/Ticket
Params:
  criteria[0][field]=12
  criteria[0][searchtype]=equals
  criteria[0][value]=1
  forcedisplay[0]=2    # ID
  forcedisplay[1]=1    # Título
  forcedisplay[2]=12   # Status
  forcedisplay[3]=3    # Prioridade
  forcedisplay[4]=15   # Data criação
  forcedisplay[5]=5    # Técnico
  order=DESC
  sort=15
  range=0-100
```

### 3. Detalhes do Usuário
```http
GET /apirest.php/User/{user_id}
Headers:
  Session-Token: {session_token}
```

### 4. Grupos do Usuário
```http
GET /apirest.php/search/Group_User
Params:
  criteria[0][field]=4
  criteria[0][searchtype]=equals
  criteria[0][value]={user_id}
  forcedisplay[0]=3    # groups_id
  forcedisplay[1]=4    # users_id
  range=0-99
```

### 5. Tickets do Técnico
```http
GET /apirest.php/search/Ticket
Params:
  criteria[0][field]=5
  criteria[0][searchtype]=equals
  criteria[0][value]={tecnico_id}
  forcedisplay[0]=2    # ID
  forcedisplay[1]=12   # Status
  range=0-1000
```

### 6. Tickets por Grupo
```http
GET /apirest.php/search/Ticket
Params:
  criteria[0][field]=8
  criteria[0][searchtype]=equals
  criteria[0][value]={group_id}
  forcedisplay[0]=12   # Status
  forcedisplay[1]=2    # ID
  range=0-9999
```

---

## 🏷️ MAPEAMENTOS

### Status de Tickets
```python
{
    1: 'novo',
    2: 'em_progresso',
    3: 'planejado',
    4: 'pendente',
    5: 'solucionado',
    6: 'fechado'
}
```

### Grupos por Nível
```python
{
    'N1': 89,  # CC-SE-SUBADM-DTIC > N1
    'N2': 90,  # CC-SE-SUBADM-DTIC > N2
    'N3': 91,  # CC-SE-SUBADM-DTIC > N3
    'N4': 92,  # CC-SE-SUBADM-DTIC > N4
}
```

### Técnicos por Nível
```python
# N1
["gabriel andrade da conceicao", "nicolas fernando muniz nunez"]

# N2
["alessandro carbonera vieira", "jonathan nascimento moletta", 
 "thales vinicius paz leite", "leonardo trojan repiso riela",
 "edson joel dos santos silva", "luciano marcelino da silva"]

# N3
["anderson da silva morim de oliveira", "silvio godinho valim",
 "jorge antonio vicente júnior", "pablo hebling guimaraes",
 "miguelangelo ferreira"]

# N4
["gabriel silva machado", "luciano de araujo silva", "wagner mengue",
 "paulo césar pedó nunes", "alexandre rovinski almoarqueg"]
```

### IDs dos Técnicos Ativos
```python
[
    "696", "32", "141", "60", "69", "1032", "252", "721", "926", "1291",
    "185", "1331", "1404", "1088", "1263", "10", "53", "250", "1471"
]
```

---

## 🔧 CONFIGURAÇÃO

### Variáveis de Ambiente
```bash
GLPI_BASE_URL=http://cau.ppiratini.intra.rs.gov.br/glpi
GLPI_APP_TOKEN=aY3f9F5aNHJmY8op0vTE4koguiPwpEYANp1JULid
GLPI_USER_TOKEN=TQdSxqg2e56PfF8ZJSX3iEJ1wCpHwhCkQJ2QtRnq
```

### Headers Padrão
```python
{
    'Content-Type': 'application/json',
    'App-Token': app_token,
    'Session-Token': session_token
}
```

---

## 📋 CAMPOS DE RESPOSTA

### Ticket
- `2`: ID
- `1`: Nome/Título
- `12`: Status
- `3`: Prioridade
- `15`: Data de criação
- `5`: Técnico atribuído
- `8`: Grupo atribuído

### User
- `id`: ID do usuário
- `name`: Login
- `firstname`: Nome
- `realname`: Sobrenome
- `is_active`: Ativo (1/0)
- `is_deleted`: Deletado (1/0)

### Group_User
- `3`: groups_id
- `4`: users_id

---

## 🚨 CÓDIGOS DE ERRO

### HTTP Status
- `200`: Sucesso
- `400`: Requisição inválida
- `401`: Não autorizado
- `403`: Proibido
- `404`: Não encontrado
- `500`: Erro interno do servidor

### Validações
```python
# Usuário ativo
is_active == '1'

# Usuário não deletado
is_deleted == '0'

# Resposta válida
response.ok and 'data' in response.json()
```

---

## ⚡ COMANDOS RÁPIDOS

### Executar Script
```bash
# Windows
$env:GLPI_BASE_URL="..."; $env:GLPI_APP_TOKEN="..."; $env:GLPI_USER_TOKEN="..."; python glpi_metrics_collector.py

# Linux/macOS
GLPI_BASE_URL="..." GLPI_APP_TOKEN="..." GLPI_USER_TOKEN="..." python glpi_metrics_collector.py
```

### Testar Conectividade
```bash
curl -I http://cau.ppiratini.intra.rs.gov.br/glpi
```

### Instalar Dependências
```bash
pip install requests colorama
```

---

## 📊 ESTRUTURAS DE SAÍDA

### Métricas Gerais
```json
{
    "total_tickets": 10000,
    "status_breakdown": {
        "novo": 2,
        "em_progresso": 25,
        "solucionado": 3213,
        "fechado": 6696
    }
}
```

### Ranking de Técnicos
```json
{
    "N1": [{
        "id": "1404",
        "nome": "Gabriel Andrade da Conceicao",
        "nivel": "N1",
        "tickets_total": 61,
        "tickets_resolvidos": 59,
        "taxa_resolucao": 96.7
    }]
}
```

### Status por Nível
```json
{
    "N1": {
        "em_progresso": 5,
        "solucionado": 527,
        "fechado": 934
    }
}
```

---

## 🔍 DEBUGGING

### Logs Úteis
```python
print(f"[DEBUG] URL: {url}")
print(f"[DEBUG] Status: {response.status_code}")
print(f"[DEBUG] Response: {response.text[:200]}")
```

### Validações
```python
# Verificar resposta
if not response.ok:
    print(f"❌ HTTP {response.status_code}")

# Verificar estrutura
data = response.json()
if 'data' not in data:
    print("❌ Campo 'data' não encontrado")
```

---

## 📚 REFERÊNCIAS

- **Documentação Completa:** `GLPI_API_DOCUMENTATION.md`
- **Exemplos Práticos:** `GLPI_API_EXAMPLES.md`
- **Guia de Setup:** `GLPI_SETUP_GUIDE.md`
- **Script Principal:** `glpi_metrics_collector.py`

---

**Última atualização:** 22 de Janeiro de 2025  
**Versão:** 1.0  
**Status:** ✅ Validado e Funcional
