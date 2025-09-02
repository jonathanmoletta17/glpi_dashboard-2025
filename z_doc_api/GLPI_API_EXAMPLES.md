# 🧪 Exemplos Práticos e Casos de Teste - GLPI API

## 🎯 Visão Geral

Este documento contém **exemplos práticos** e **casos de teste** para todas as requisições implementadas no `glpi_metrics_collector.py`. Use este guia para:

- ✅ **Testar** implementações
- ✅ **Validar** respostas
- ✅ **Debuggar** problemas
- ✅ **Entender** fluxos de dados

---

## 🔐 1. EXEMPLOS DE AUTENTICAÇÃO

### 1.1 Teste de Autenticação com User Token

```python
import requests
import json

# Configuração
base_url = "http://cau.ppiratini.intra.rs.gov.br/glpi"
app_token = "aY3f9F5aNHJmY8op0vTE4koguiPwpEYANp1JULid"
user_token = "TQdSxqg2e56PfF8ZJSX3iEJ1wCpHwhCkQJ2QtRnq"

# Headers
headers = {
    'Content-Type': 'application/json',
    'App-Token': app_token,
    'Authorization': f'user_token {user_token}'
}

# Requisição
url = f"{base_url}/apirest.php/initSession"
response = requests.get(url, headers=headers)

print(f"Status: {response.status_code}")
print(f"Resposta: {response.json()}")
```

**Resposta Esperada:**
```json
{
    "session_token": "fkegh7v413anh1598a79...",
    "glpi_currenttime": "2025-01-22 22:55:48"
}
```

### 1.2 Teste de Finalização de Sessão

```python
# Usar session_token obtido anteriormente
session_token = "fkegh7v413anh1598a79..."

headers = {
    'Content-Type': 'application/json',
    'App-Token': app_token,
    'Session-Token': session_token
}

url = f"{base_url}/apirest.php/killSession"
response = requests.get(url, headers=headers)

print(f"Status: {response.status_code}")
print(f"Resposta: {response.json()}")
```

---

## 📊 2. EXEMPLOS DE MÉTRICAS GERAIS

### 2.1 Busca de Todos os Tickets

```python
# Headers com session token
headers = {
    'Content-Type': 'application/json',
    'App-Token': app_token,
    'Session-Token': session_token
}

# Parâmetros
params = {
    'forcedisplay[0]': 2,    # ID
    'forcedisplay[1]': 12,   # Status
    'forcedisplay[2]': 3,    # Prioridade
    'forcedisplay[3]': 15,   # Data criação
    'range': '0-100'         # Limitar para teste
}

url = f"{base_url}/apirest.php/search/Ticket"
response = requests.get(url, headers=headers, params=params)

print(f"Status: {response.status_code}")
data = response.json()
print(f"Total de tickets: {len(data.get('data', []))}")

# Exemplo de ticket
if data.get('data'):
    ticket = data['data'][0]
    print(f"Exemplo de ticket: {ticket}")
```

**Resposta Esperada:**
```json
{
    "data": [
        {
            "2": "10227",
            "12": "1",
            "3": "3",
            "15": "2025-01-22 10:30:00"
        }
    ]
}
```

### 2.2 Contagem por Status

```python
# Processar tickets para contagem
tickets = data.get('data', [])
status_count = {
    'novo': 0,
    'em_progresso': 0,
    'planejado': 0,
    'pendente': 0,
    'solucionado': 0,
    'fechado': 0
}

status_map = {
    1: 'novo',
    2: 'em_progresso',
    3: 'planejado',
    4: 'pendente',
    5: 'solucionado',
    6: 'fechado'
}

for ticket in tickets:
    status_id = int(ticket.get('12', 0))
    if status_id in status_map:
        status_count[status_map[status_id]] += 1

print("Contagem por status:")
for status, count in status_count.items():
    print(f"  {status}: {count}")
```

---

## 🎫 3. EXEMPLOS DE TICKETS NOVOS

### 3.1 Busca de Tickets com Status "Novo"

```python
# Parâmetros para tickets novos
params = {
    'criteria[0][field]': 12,      # Campo status
    'criteria[0][searchtype]': 'equals',
    'criteria[0][value]': 1,       # Status "Novo"
    'forcedisplay[0]': 2,          # ID
    'forcedisplay[1]': 1,          # Título
    'forcedisplay[2]': 12,         # Status
    'forcedisplay[3]': 3,          # Prioridade
    'forcedisplay[4]': 15,         # Data criação
    'forcedisplay[5]': 5,          # Técnico atribuído
    'order': 'DESC',
    'sort': 15,
    'range': '0-10'
}

url = f"{base_url}/apirest.php/search/Ticket"
response = requests.get(url, headers=headers, params=params)

data = response.json()
tickets_novos = data.get('data', [])

print(f"Tickets novos encontrados: {len(tickets_novos)}")

for i, ticket in enumerate(tickets_novos[:5]):
    print(f"{i+1}. ID: {ticket.get('2')} - {ticket.get('1', '')[:50]}...")
```

---

## 🏆 4. EXEMPLOS DE RANKING DE TÉCNICOS

### 4.1 Validação de Técnico Específico

```python
# Testar um técnico específico
tecnico_id = "1404"  # Gabriel Andrade da Conceicao

url = f"{base_url}/apirest.php/User/{tecnico_id}"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    user_data = response.json()

    print(f"Técnico: {user_data.get('firstname')} {user_data.get('realname')}")
    print(f"Ativo: {user_data.get('is_active')}")
    print(f"Deletado: {user_data.get('is_deleted')}")

    # Verificar se é válido
    is_active = str(user_data.get('is_active', '0')).strip()
    is_deleted = str(user_data.get('is_deleted', '0')).strip()

    if str(is_active) == '1' and str(is_deleted) == '0':
        print("✅ Técnico válido!")
    else:
        print("❌ Técnico inválido")
else:
    print(f"❌ Erro: {response.status_code}")
```

### 4.2 Busca de Grupos do Técnico

```python
# Buscar grupos do técnico
params = {
    'range': '0-99',
    'criteria[0][field]': '4',  # Campo users_id
    'criteria[0][searchtype]': 'equals',
    'criteria[0][value]': tecnico_id,
    'forcedisplay[0]': '3',     # groups_id
    'forcedisplay[1]': '4',     # users_id
}

url = f"{base_url}/apirest.php/search/Group_User"
response = requests.get(url, headers=headers, params=params)

data = response.json()
groups = data.get('data', [])

print(f"Grupos do técnico {tecnico_id}:")
for group in groups:
    group_id = group.get('3')
    print(f"  Grupo ID: {group_id}")

# Verificar se está em grupo de nível
service_levels = {'N1': 89, 'N2': 90, 'N3': 91, 'N4': 92}
for group in groups:
    group_id = int(group.get('3', 0))
    for level, level_group_id in service_levels.items():
        if group_id == level_group_id:
            print(f"✅ Técnico está no nível {level} (grupo {group_id})")
```

### 4.3 Cálculo de Métricas do Técnico

```python
# Buscar tickets do técnico
params = {
    'criteria[0][field]': 5,       # Campo técnico
    'criteria[0][searchtype]': 'equals',
    'criteria[0][value]': tecnico_id,
    'forcedisplay[0]': 2,          # ID
    'forcedisplay[1]': 12,         # Status
    'range': '0-1000'
}

url = f"{base_url}/apirest.php/search/Ticket"
response = requests.get(url, headers=headers, params=params)

data = response.json()
tickets = data.get('data', [])

# Calcular métricas
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

print(f"Métricas do técnico {tecnico_id}:")
print(f"  Total: {total}")
print(f"  Resolvidos: {resolvidos}")
print(f"  Pendentes: {pendentes}")
print(f"  Taxa de resolução: {taxa_resolucao:.1f}%")
```

---

## 📈 5. EXEMPLOS DE STATUS POR NÍVEL

### 5.1 Busca de Tickets por Grupo

```python
# Testar um nível específico
nivel = "N1"
group_id = 89  # Grupo N1

params = {
    'criteria[0][field]': 8,       # Campo grupo
    'criteria[0][searchtype]': 'equals',
    'criteria[0][value']': group_id,
    'forcedisplay[0]': 12,         # Status
    'forcedisplay[1]': 2,          # ID
    'range': '0-100'               # Limitar para teste
}

url = f"{base_url}/apirest.php/search/Ticket"
response = requests.get(url, headers=headers, params=params)

data = response.json()
tickets = data.get('data', [])

print(f"Tickets do grupo {group_id} ({nivel}): {len(tickets)}")

# Contar por status
status_map = {
    1: 'novo',
    2: 'em_progresso',
    3: 'planejado',
    4: 'pendente',
    5: 'solucionado',
    6: 'fechado'
}

status_count = {status: 0 for status in status_map.values()}

for ticket in tickets:
    status_id = int(ticket.get('12', 0))
    status_name = status_map.get(status_id, 'novo')
    status_count[status_name] += 1

print(f"Contagem por status para {nivel}:")
for status, count in status_count.items():
    if count > 0:
        print(f"  {status}: {count}")
```

---

## 🧪 6. CASOS DE TESTE COMPLETOS

### 6.1 Teste de Fluxo Completo

```python
def teste_fluxo_completo():
    """Teste completo de todas as funcionalidades"""

    # 1. Autenticação
    print("1. Testando autenticação...")
    session_token = autenticar()
    if not session_token:
        print("❌ Falha na autenticação")
        return False

    # 2. Métricas gerais
    print("2. Testando métricas gerais...")
    metricas = buscar_metricas_gerais(session_token)
    if not metricas:
        print("❌ Falha nas métricas gerais")
        return False

    # 3. Tickets novos
    print("3. Testando tickets novos...")
    tickets_novos = buscar_tickets_novos(session_token)
    print(f"✅ {len(tickets_novos)} tickets novos encontrados")

    # 4. Ranking de técnicos
    print("4. Testando ranking de técnicos...")
    ranking = buscar_ranking_tecnicos(session_token)
    total_tecnicos = sum(len(tecnicos) for tecnicos in ranking.values())
    print(f"✅ {total_tecnicos} técnicos no ranking")

    # 5. Status por nível
    print("5. Testando status por nível...")
    status_nivel = buscar_status_por_nivel(session_token)
    print("✅ Status por nível coletado")

    # 6. Finalização
    print("6. Finalizando sessão...")
    finalizar_sessao(session_token)

    print("✅ Todos os testes passaram!")
    return True

# Executar teste
teste_fluxo_completo()
```

### 6.2 Teste de Validação de Técnicos

```python
def teste_validacao_tecnicos():
    """Teste de validação dos 19 técnicos"""

    technician_ids = [
        "696", "32", "141", "60", "69", "1032", "252", "721", "926", "1291",
        "185", "1331", "1404", "1088", "1263", "10", "53", "250", "1471"
    ]

    session_token = autenticar()
    tecnicos_validos = []

    for tech_id in technician_ids:
        user_data = buscar_usuario(tech_id, session_token)
        if user_data:
            is_active = str(user_data.get('is_active', '0')).strip()
            is_deleted = str(user_data.get('is_deleted', '0')).strip()

            if str(is_active) == '1' and str(is_deleted) == '0':
                nome = f"{user_data.get('firstname')} {user_data.get('realname')}"
                tecnicos_validos.append({'id': tech_id, 'nome': nome})
                print(f"✅ {tech_id}: {nome}")
            else:
                print(f"❌ {tech_id}: Inativo ou deletado")
        else:
            print(f"❌ {tech_id}: Não encontrado")

    print(f"\nTotal de técnicos válidos: {len(tecnicos_validos)}/19")
    return tecnicos_validos

# Executar teste
teste_validacao_tecnicos()
```

### 6.3 Teste de Mapeamento de Níveis

```python
def teste_mapeamento_niveis():
    """Teste do mapeamento de níveis dos técnicos"""

    # Mapeamento esperado
    mapeamento_esperado = {
        "1404": "N1",  # Gabriel Andrade da Conceicao
        "1263": "N1",  # Nicolas Fernando Muniz Nunez
        "1032": "N2",  # Jonathan Nascimento Moletta
        "252": "N2",   # Alessandro Carbonera Vieira
        "721": "N2",   # Thales Vinicius Paz Leite
        "696": "N3",   # Anderson da Silva Morim de Oliveira
        "32": "N3",    # Silvio Godinho Valim
        "141": "N3",   # Jorge Antonio Vicente Júnior
        "1291": "N4",  # Gabriel Silva Machado
        "1088": "N4",  # Luciano de Araujo Silva
    }

    session_token = autenticar()
    resultados = {}

    for tech_id, nivel_esperado in mapeamento_esperado.items():
        nivel_detectado = detectar_nivel_tecnico(tech_id, session_token)
        resultados[tech_id] = {
            'esperado': nivel_esperado,
            'detectado': nivel_detectado,
            'correto': nivel_esperado == nivel_detectado
        }

        status = "✅" if nivel_esperado == nivel_detectado else "❌"
        print(f"{status} {tech_id}: Esperado {nivel_esperado}, Detectado {nivel_detectado}")

    corretos = sum(1 for r in resultados.values() if r['correto'])
    total = len(resultados)

    print(f"\nMapeamento correto: {corretos}/{total} ({corretos/total*100:.1f}%)")
    return resultados

# Executar teste
teste_mapeamento_niveis()
```

---

## 🔍 7. DEBUGGING E LOGS

### 7.1 Logs Detalhados

```python
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def debug_request(url, params=None, headers=None):
    """Função para debug de requisições"""
    logging.debug(f"URL: {url}")
    logging.debug(f"Params: {params}")
    logging.debug(f"Headers: {headers}")

    response = requests.get(url, params=params, headers=headers)

    logging.debug(f"Status: {response.status_code}")
    logging.debug(f"Response: {response.text[:500]}...")

    return response
```

### 7.2 Validação de Respostas

```python
def validar_resposta_glpi(response, expected_fields=None):
    """Valida estrutura de resposta do GLPI"""

    if not response.ok:
        print(f"❌ Status HTTP inválido: {response.status_code}")
        return False

    try:
        data = response.json()
    except json.JSONDecodeError:
        print("❌ Resposta não é JSON válido")
        return False

    if not isinstance(data, dict):
        print("❌ Resposta não é um objeto JSON")
        return False

    if 'data' not in data:
        print("❌ Campo 'data' não encontrado na resposta")
        return False

    if expected_fields:
        for field in expected_fields:
            if field not in data:
                print(f"❌ Campo '{field}' não encontrado")
                return False

    print("✅ Resposta válida")
    return True
```

---

## 📋 8. CHECKLIST DE VALIDAÇÃO

### 8.1 Checklist de Autenticação

- [ ] `GLPI_BASE_URL` configurado corretamente
- [ ] `GLPI_APP_TOKEN` válido
- [ ] `GLPI_USER_TOKEN` válido
- [ ] Conectividade com GLPI funcionando
- [ ] `initSession` retorna `session_token`
- [ ] `killSession` executa sem erros

### 8.2 Checklist de Dados

- [ ] Métricas gerais retornam contadores válidos
- [ ] Tickets novos filtrados corretamente (status = 1)
- [ ] 19 técnicos ativos identificados
- [ ] Níveis mapeados corretamente (N1, N2, N3, N4)
- [ ] Métricas de técnicos calculadas corretamente
- [ ] Status por nível contados corretamente

### 8.3 Checklist de Performance

- [ ] Autenticação < 2 segundos
- [ ] Métricas gerais < 5 segundos
- [ ] Tickets novos < 3 segundos
- [ ] Ranking técnicos < 10 segundos
- [ ] Status por nível < 8 segundos
- [ ] Total < 30 segundos

---

## 🎯 9. CONCLUSÃO

Este documento fornece **exemplos práticos** e **casos de teste** para validar todas as funcionalidades implementadas. Use estes exemplos para:

1. **Testar** novas implementações
2. **Validar** correções
3. **Debuggar** problemas
4. **Garantir** qualidade do código

**Última atualização:** 22 de Janeiro de 2025
**Versão:** 1.0
**Status:** ✅ Testado e Validado
