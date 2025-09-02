# 🚀 Guia de Configuração e Setup - GLPI Metrics Collector

## 🎯 Visão Geral

Este guia fornece instruções **passo a passo** para configurar e executar o `glpi_metrics_collector.py` em qualquer ambiente. Siga este guia para:

- ✅ **Configurar** ambiente de desenvolvimento
- ✅ **Instalar** dependências necessárias
- ✅ **Configurar** variáveis de ambiente
- ✅ **Executar** o script com sucesso
- ✅ **Troubleshoot** problemas comuns

---

## 📋 1. PRÉ-REQUISITOS

### 1.1 Sistema Operacional

- ✅ **Windows 10/11** (testado)
- ✅ **Linux Ubuntu/Debian** (compatível)
- ✅ **macOS** (compatível)

### 1.2 Python

- ✅ **Python 3.8+** (recomendado: Python 3.9+)
- ✅ **pip** (gerenciador de pacotes)

**Verificar versão:**
```bash
python --version
# ou
python3 --version
```

### 1.3 Acesso ao GLPI

- ✅ **URL do GLPI** acessível
- ✅ **App Token** válido
- ✅ **User Token** válido
- ✅ **Permissões** de leitura na API

---

## 🔧 2. INSTALAÇÃO

### 2.1 Clonar/Download do Script

```bash
# Se usando Git
git clone <repository_url>
cd glpi_dashboard_funcional

# Ou baixar o arquivo diretamente
# glpi_metrics_collector.py
```

### 2.2 Instalar Dependências

```bash
# Instalar dependências Python
pip install requests colorama

# Ou usando requirements.txt (se disponível)
pip install -r requirements.txt
```

**Dependências necessárias:**
- `requests` - Para requisições HTTP
- `colorama` - Para cores no terminal (Windows)

### 2.3 Verificar Instalação

```python
# Teste rápido
python -c "import requests, colorama; print('✅ Dependências instaladas!')"
```

---

## ⚙️ 3. CONFIGURAÇÃO

### 3.1 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
# .env
GLPI_BASE_URL=http://cau.ppiratini.intra.rs.gov.br/glpi
GLPI_APP_TOKEN=aY3f9F5aNHJmY8op0vTE4koguiPwpEYANp1JULid
GLPI_USER_TOKEN=TQdSxqg2e56PfF8ZJSX3iEJ1wCpHwhCkQJ2QtRnq
```

### 3.2 Configuração por Sistema

#### Windows (PowerShell)
```powershell
# Configurar variáveis de ambiente
$env:GLPI_BASE_URL="http://cau.ppiratini.intra.rs.gov.br/glpi"
$env:GLPI_APP_TOKEN="aY3f9F5aNHJmY8op0vTE4koguiPwpEYANp1JULid"
$env:GLPI_USER_TOKEN="TQdSxqg2e56PfF8ZJSX3iEJ1wCpHwhCkQJ2QtRnq"

# Verificar configuração
echo $env:GLPI_BASE_URL
```

#### Linux/macOS (Bash)
```bash
# Configurar variáveis de ambiente
export GLPI_BASE_URL="http://cau.ppiratini.intra.rs.gov.br/glpi"
export GLPI_APP_TOKEN="aY3f9F5aNHJmY8op0vTE4koguiPwpEYANp1JULid"
export GLPI_USER_TOKEN="TQdSxqg2e56PfF8ZJSX3iEJ1wCpHwhCkQJ2QtRnq"

# Verificar configuração
echo $GLPI_BASE_URL
```

### 3.3 Configuração Permanente

#### Windows
1. Abrir "Configurações do Sistema"
2. Ir em "Variáveis de Ambiente"
3. Adicionar variáveis do usuário:
   - `GLPI_BASE_URL`
   - `GLPI_APP_TOKEN`
   - `GLPI_USER_TOKEN`

#### Linux/macOS
Adicionar ao arquivo `~/.bashrc` ou `~/.zshrc`:
```bash
# GLPI Configuration
export GLPI_BASE_URL="http://cau.ppiratini.intra.rs.gov.br/glpi"
export GLPI_APP_TOKEN="aY3f9F5aNHJmY8op0vTE4koguiPwpEYANp1JULid"
export GLPI_USER_TOKEN="TQdSxqg2e56PfF8ZJSX3iEJ1wCpHwhCkQJ2QtRnq"
```

---

## 🚀 4. EXECUÇÃO

### 4.1 Execução Básica

```bash
# Navegar para o diretório
cd /caminho/para/glpi_dashboard_funcional

# Executar o script
python glpi_metrics_collector.py
```

### 4.2 Execução com Configuração Inline

#### Windows (PowerShell)
```powershell
$env:GLPI_BASE_URL="http://cau.ppiratini.intra.rs.gov.br/glpi"; $env:GLPI_APP_TOKEN="aY3f9F5aNHJmY8op0vTE4koguiPwpEYANp1JULid"; $env:GLPI_USER_TOKEN="TQdSxqg2e56PfF8ZJSX3iEJ1wCpHwhCkQJ2QtRnq"; python glpi_metrics_collector.py
```

#### Linux/macOS (Bash)
```bash
GLPI_BASE_URL="http://cau.ppiratini.intra.rs.gov.br/glpi" GLPI_APP_TOKEN="aY3f9F5aNHJmY8op0vTE4koguiPwpEYANp1JULid" GLPI_USER_TOKEN="TQdSxqg2e56PfF8ZJSX3iEJ1wCpHwhCkQJ2QtRnq" python glpi_metrics_collector.py
```

### 4.3 Execução com Logs Detalhados

```bash
# Executar com output detalhado
python glpi_metrics_collector.py 2>&1 | tee glpi_output.log
```

---

## 📊 5. VALIDAÇÃO

### 5.1 Teste de Conectividade

```python
# test_connection.py
import requests
import os

def test_glpi_connection():
    base_url = os.getenv('GLPI_BASE_URL')
    app_token = os.getenv('GLPI_APP_TOKEN')
    user_token = os.getenv('GLPI_USER_TOKEN')
    
    if not all([base_url, app_token, user_token]):
        print("❌ Variáveis de ambiente não configuradas")
        return False
    
    # Teste de conectividade
    try:
        response = requests.get(f"{base_url}/apirest.php/initSession", 
                              headers={'App-Token': app_token, 
                                     'Authorization': f'user_token {user_token}'})
        if response.status_code == 200:
            print("✅ Conectividade com GLPI OK")
            return True
        else:
            print(f"❌ Erro de conectividade: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

if __name__ == "__main__":
    test_glpi_connection()
```

### 5.2 Teste de Configuração

```python
# test_config.py
import os

def test_configuration():
    required_vars = ['GLPI_BASE_URL', 'GLPI_APP_TOKEN', 'GLPI_USER_TOKEN']
    
    print("🔍 Verificando configuração...")
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mascarar token para segurança
            if 'TOKEN' in var:
                masked_value = value[:10] + "..." + value[-5:]
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Não configurado")
    
    print("\n🎯 Configuração completa!" if all(os.getenv(var) for var in required_vars) else "⚠️ Configuração incompleta!")

if __name__ == "__main__":
    test_configuration()
```

---

## 🔍 6. TROUBLESHOOTING

### 6.1 Problemas Comuns

#### Erro: "GLPI_BASE_URL não configurado"
```bash
# Solução: Configurar variável de ambiente
export GLPI_BASE_URL="http://cau.ppiratini.intra.rs.gov.br/glpi"
```

#### Erro: "GLPI_APP_TOKEN não configurado"
```bash
# Solução: Configurar token da aplicação
export GLPI_APP_TOKEN="seu_app_token_aqui"
```

#### Erro: "Credenciais não configuradas"
```bash
# Solução: Configurar user token
export GLPI_USER_TOKEN="seu_user_token_aqui"
```

#### Erro: "ModuleNotFoundError: No module named 'requests'"
```bash
# Solução: Instalar dependências
pip install requests colorama
```

#### Erro: "Connection refused" ou "Timeout"
```bash
# Verificar conectividade
ping cau.ppiratini.intra.rs.gov.br

# Verificar se GLPI está acessível
curl -I http://cau.ppiratini.intra.rs.gov.br/glpi
```

### 6.2 Logs de Debug

```python
# Habilitar logs detalhados
import logging
logging.basicConfig(level=logging.DEBUG)

# Ou adicionar prints de debug no script
print(f"[DEBUG] URL: {url}")
print(f"[DEBUG] Headers: {headers}")
print(f"[DEBUG] Response: {response.status_code}")
```

### 6.3 Validação de Tokens

```python
# test_tokens.py
import requests
import os

def validate_tokens():
    base_url = os.getenv('GLPI_BASE_URL')
    app_token = os.getenv('GLPI_APP_TOKEN')
    user_token = os.getenv('GLPI_USER_TOKEN')
    
    # Teste de autenticação
    headers = {
        'Content-Type': 'application/json',
        'App-Token': app_token,
        'Authorization': f'user_token {user_token}'
    }
    
    try:
        response = requests.get(f"{base_url}/apirest.php/initSession", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if 'session_token' in data:
                print("✅ Tokens válidos!")
                print(f"Session Token: {data['session_token'][:20]}...")
                return True
            else:
                print("❌ Resposta inválida - session_token não encontrado")
                return False
        else:
            print(f"❌ Erro de autenticação: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

if __name__ == "__main__":
    validate_tokens()
```

---

## 📁 7. ESTRUTURA DE ARQUIVOS

### 7.1 Arquivos Necessários

```
glpi_dashboard_funcional/
├── glpi_metrics_collector.py          # Script principal
├── GLPI_API_DOCUMENTATION.md          # Documentação completa
├── GLPI_API_EXAMPLES.md               # Exemplos práticos
├── GLPI_SETUP_GUIDE.md                # Este guia
├── .env                               # Variáveis de ambiente (opcional)
├── requirements.txt                   # Dependências Python
└── glpi_metrics_YYYYMMDD_HHMMSS.json # Arquivos de saída
```

### 7.2 Arquivos de Saída

O script gera automaticamente:
- `glpi_metrics_YYYYMMDD_HHMMSS.json` - Métricas coletadas
- Logs no console com cores e emojis

---

## 🎯 8. EXECUÇÃO AUTOMATIZADA

### 8.1 Script de Execução (Windows)

```batch
@echo off
REM run_glpi_metrics.bat

echo Configurando variáveis de ambiente...
set GLPI_BASE_URL=http://cau.ppiratini.intra.rs.gov.br/glpi
set GLPI_APP_TOKEN=aY3f9F5aNHJmY8op0vTE4koguiPwpEYANp1JULid
set GLPI_USER_TOKEN=TQdSxqg2e56PfF8ZJSX3iEJ1wCpHwhCkQJ2QtRnq

echo Executando coleta de métricas...
python glpi_metrics_collector.py

echo Processo concluído!
pause
```

### 8.2 Script de Execução (Linux/macOS)

```bash
#!/bin/bash
# run_glpi_metrics.sh

echo "Configurando variáveis de ambiente..."
export GLPI_BASE_URL="http://cau.ppiratini.intra.rs.gov.br/glpi"
export GLPI_APP_TOKEN="aY3f9F5aNHJmY8op0vTE4koguiPwpEYANp1JULid"
export GLPI_USER_TOKEN="TQdSxqg2e56PfF8ZJSX3iEJ1wCpHwhCkQJ2QtRnq"

echo "Executando coleta de métricas..."
python glpi_metrics_collector.py

echo "Processo concluído!"
```

### 8.3 Agendamento (Cron)

```bash
# Editar crontab
crontab -e

# Executar a cada hora
0 * * * * /caminho/para/run_glpi_metrics.sh

# Executar diariamente às 8h
0 8 * * * /caminho/para/run_glpi_metrics.sh
```

---

## 📊 9. MONITORAMENTO

### 9.1 Verificação de Saúde

```python
# health_check.py
import os
import requests
from datetime import datetime

def health_check():
    """Verificação de saúde do sistema"""
    
    print(f"🔍 Health Check - {datetime.now()}")
    
    # 1. Verificar configuração
    config_ok = all([
        os.getenv('GLPI_BASE_URL'),
        os.getenv('GLPI_APP_TOKEN'),
        os.getenv('GLPI_USER_TOKEN')
    ])
    
    print(f"✅ Configuração: {'OK' if config_ok else 'ERRO'}")
    
    # 2. Verificar conectividade
    try:
        response = requests.get(os.getenv('GLPI_BASE_URL'), timeout=10)
        connectivity_ok = response.status_code < 500
        print(f"✅ Conectividade: {'OK' if connectivity_ok else 'ERRO'}")
    except:
        print("❌ Conectividade: ERRO")
        connectivity_ok = False
    
    # 3. Verificar autenticação
    if config_ok and connectivity_ok:
        try:
            headers = {
                'App-Token': os.getenv('GLPI_APP_TOKEN'),
                'Authorization': f"user_token {os.getenv('GLPI_USER_TOKEN')}"
            }
            response = requests.get(f"{os.getenv('GLPI_BASE_URL')}/apirest.php/initSession", headers=headers)
            auth_ok = response.status_code == 200
            print(f"✅ Autenticação: {'OK' if auth_ok else 'ERRO'}")
        except:
            print("❌ Autenticação: ERRO")
            auth_ok = False
    else:
        auth_ok = False
    
    # Resultado final
    overall_health = config_ok and connectivity_ok and auth_ok
    print(f"\n🎯 Status Geral: {'✅ SAUDÁVEL' if overall_health else '❌ PROBLEMAS DETECTADOS'}")
    
    return overall_health

if __name__ == "__main__":
    health_check()
```

---

## 🎉 10. CONCLUSÃO

Este guia fornece **instruções completas** para configurar e executar o `glpi_metrics_collector.py` em qualquer ambiente. Siga os passos na ordem para garantir uma configuração bem-sucedida.

### 10.1 Próximos Passos

1. ✅ **Configurar** ambiente
2. ✅ **Instalar** dependências
3. ✅ **Configurar** variáveis de ambiente
4. ✅ **Executar** script
5. ✅ **Validar** resultados
6. ✅ **Automatizar** execução (opcional)

### 10.2 Suporte

Em caso de problemas:
1. Verificar logs de erro
2. Executar testes de conectividade
3. Validar configuração
4. Consultar documentação técnica

**Última atualização:** 22 de Janeiro de 2025  
**Versão:** 1.0  
**Status:** ✅ Testado e Validado
