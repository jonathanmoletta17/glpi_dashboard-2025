#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criador de Base de Conhecimento de Exemplo
Cria uma base de conhecimento de exemplo para demonstração
"""

import os
import json
from pathlib import Path
from datetime import datetime


def create_sample_knowledge_base():
    """Cria uma base de conhecimento de exemplo"""
    
    print("🎯 Criando base de conhecimento de exemplo...")
    
    # Criar estrutura de diretórios
    base_path = Path("base_conhecimento_copilot")
    base_path.mkdir(exist_ok=True)
    
    subdirs = [
        "tickets_resolvidos/hardware/impressora",
        "tickets_resolvidos/hardware/computador",
        "tickets_resolvidos/software/aplicativos",
        "tickets_resolvidos/rede/wifi",
        "tickets_resolvidos/sistemas/email",
        "tickets_resolvidos/sistemas/acesso",
        "tickets_resolvidos/sistemas/configuracoes",
        "tickets_resolvidos/geral",
        "solucoes_padrao",
        "metadados"
    ]
    
    for subdir in subdirs:
        (base_path / subdir).mkdir(parents=True, exist_ok=True)
    
    # Criar tickets de exemplo
    sample_tickets = [
        {
            "id": "001",
            "title": "Problema de Impressão - Impressora HP",
            "category": "hardware/impressora",
            "content": """# Problema de Impressão - Impressora HP

## 📋 **PROBLEMA**
**Usuário:** João Silva
**Data:** 2024-12-15
**Prioridade:** Baixa
**Categoria:** Hardware/Impressora
**Ticket ID:** 001

### Descrição:
Usuário relatou que a impressora HP LaserJet não está imprimindo documentos. 
A impressora está ligada e conectada, mas os documentos ficam na fila de impressão.

## 🔧 **SOLUÇÃO**
**Técnico:** Maria Santos
**Data de Resolução:** 2024-12-15
**Tempo de Resolução:** 15 minutos

### Solução Implementada:
1. Verificar se a impressora está online no painel de controle
2. Limpar a fila de impressão (Cancelar todos os documentos)
3. Reiniciar o serviço de spooler de impressão
4. Testar impressão com documento simples

### Comandos/Configurações:
```cmd
net stop spooler
net start spooler
```

## 🏷️ **TAGS**
- ticket_001
- impressora
- hardware
- resolvido
- copilot_knowledge
- hp
- spooler

## 📊 **METADADOS**
- **Complexidade:** Baixa
- **Fonte:** GLPI
- **Data de Extração:** 2025-01-03 10:30:00
- **Copilot Ready:** Sim
- **Categoria GLPI:** Hardware/Impressora
- **Técnico Responsável:** Maria Santos
- **Tempo de Resolução:** 15 minutos

## 🤖 **INSTRUÇÕES PARA COPILOT**
Este ticket contém uma solução para um problema comum de impressão. 
Use as informações da seção "Solução Implementada" para orientar 
usuários com problemas similares. As tags ajudam a identificar 
o tipo de problema e a complexidade da solução.
"""
        },
        {
            "id": "002",
            "title": "Reset de Senha - Active Directory",
            "category": "sistemas/acesso",
            "content": """# Reset de Senha - Active Directory

## 📋 **PROBLEMA**
**Usuário:** Ana Costa
**Data:** 2024-12-14
**Prioridade:** Média
**Categoria:** Sistemas/Acesso
**Ticket ID:** 002

### Descrição:
Usuária esqueceu a senha do Active Directory e não consegue fazer login 
no computador nem acessar o email corporativo.

## 🔧 **SOLUÇÃO**
**Técnico:** Carlos Oliveira
**Data de Resolução:** 2024-12-14
**Tempo de Resolução:** 30 minutos

### Solução Implementada:
1. Verificar identidade do usuário (documento, telefone)
2. Acessar o Active Directory Users and Computers
3. Localizar o usuário no OU correto
4. Clicar com botão direito > Reset Password
5. Gerar nova senha temporária
6. Orientar usuário a alterar senha no primeiro login
7. Testar login com nova senha

### Comandos/Configurações:
```powershell
# Reset via PowerShell (alternativo)
Set-ADAccountPassword -Identity "ana.costa" -Reset
```

## 🏷️ **TAGS**
- ticket_002
- senha
- acesso
- active_directory
- resolvido
- copilot_knowledge
- reset
- login

## 📊 **METADADOS**
- **Complexidade:** Média
- **Fonte:** GLPI
- **Data de Extração:** 2025-01-03 10:30:00
- **Copilot Ready:** Sim
- **Categoria GLPI:** Sistemas/Acesso
- **Técnico Responsável:** Carlos Oliveira
- **Tempo de Resolução:** 30 minutos

## 🤖 **INSTRUÇÕES PARA COPILOT**
Este ticket contém uma solução para reset de senha no Active Directory. 
Use as informações da seção "Solução Implementada" para orientar 
usuários com problemas similares. As tags ajudam a identificar 
o tipo de problema e a complexidade da solução.
"""
        },
        {
            "id": "003",
            "title": "Configuração de Email - Outlook",
            "category": "sistemas/email",
            "content": """# Configuração de Email - Outlook

## 📋 **PROBLEMA**
**Usuário:** Pedro Lima
**Data:** 2024-12-13
**Prioridade:** Baixa
**Categoria:** Sistemas/Email
**Ticket ID:** 003

### Descrição:
Usuário precisa configurar o Outlook para acessar o email corporativo 
em um novo computador. Não sabe quais configurações usar.

## 🔧 **SOLUÇÃO**
**Técnico:** Fernanda Rocha
**Data de Resolução:** 2024-12-13
**Tempo de Resolução:** 20 minutos

### Solução Implementada:
1. Abrir o Outlook
2. Ir em Arquivo > Adicionar Conta
3. Inserir email corporativo: usuario@empresa.com
4. Selecionar "Configuração manual"
5. Configurar servidor IMAP:
   - Servidor de entrada: mail.empresa.com
   - Porta: 993 (SSL)
   - Servidor de saída: mail.empresa.com
   - Porta: 587 (TLS)
6. Testar configuração
7. Sincronizar pastas

### Comandos/Configurações:
```
Servidor IMAP: mail.empresa.com:993
Servidor SMTP: mail.empresa.com:587
Autenticação: Nome de usuário e senha
```

## 🏷️ **TAGS**
- ticket_003
- email
- outlook
- configuracao
- resolvido
- copilot_knowledge
- imap
- smtp

## 📊 **METADADOS**
- **Complexidade:** Baixa
- **Fonte:** GLPI
- **Data de Extração:** 2025-01-03 10:30:00
- **Copilot Ready:** Sim
- **Categoria GLPI:** Sistemas/Email
- **Técnico Responsável:** Fernanda Rocha
- **Tempo de Resolução:** 20 minutos

## 🤖 **INSTRUÇÕES PARA COPILOT**
Este ticket contém uma solução para configuração de email no Outlook. 
Use as informações da seção "Solução Implementada" para orientar 
usuários com problemas similares. As tags ajudam a identificar 
o tipo de problema e a complexidade da solução.
"""
        }
    ]
    
    # Salvar tickets de exemplo
    for ticket in sample_tickets:
        file_path = base_path / "tickets_resolvidos" / ticket["category"] / f"ticket_{ticket['id']}_exemplo.md"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(ticket["content"])
        print(f"✅ Criado: {file_path}")
    
    # Criar soluções padrão
    solucoes_padrao = [
        {
            "filename": "reset_senha.md",
            "content": """# Reset de Senha - Guia Padrão

## 🎯 **PROBLEMA COMUM**
Usuários esquecem a senha do Active Directory e não conseguem fazer login.

## 🔧 **SOLUÇÃO PADRÃO**

### 1. Verificar Identidade
- Confirmar nome completo
- Verificar documento de identidade
- Confirmar telefone de contato

### 2. Reset no Active Directory
1. Abrir "Active Directory Users and Computers"
2. Localizar usuário no OU correto
3. Clicar com botão direito > "Reset Password"
4. Gerar senha temporária forte
5. Anotar senha temporária

### 3. Orientar Usuário
- Informar nova senha temporária
- Orientar a alterar no primeiro login
- Explicar política de senhas da empresa

### 4. Testar Acesso
- Fazer login com nova senha
- Verificar acesso ao email
- Confirmar funcionamento normal

## ⚠️ **IMPORTANTE**
- Sempre verificar identidade antes do reset
- Gerar senhas temporárias seguras
- Orientar sobre política de senhas
- Documentar no ticket

## 🏷️ **TAGS**
- reset_senha
- active_directory
- acesso
- padrao
- copilot_knowledge
"""
        },
        {
            "filename": "problemas_impressora.md",
            "content": """# Problemas de Impressora - Guia Padrão

## 🎯 **PROBLEMAS COMUNS**
- Impressora não imprime
- Documentos na fila de impressão
- Impressora offline
- Erro de driver

## 🔧 **SOLUÇÕES PADRÃO**

### 1. Verificar Status
- Verificar se impressora está ligada
- Confirmar conexão USB/rede
- Verificar papel e tinta

### 2. Limpar Fila de Impressão
1. Abrir "Painel de Controle"
2. Ir em "Dispositivos e Impressoras"
3. Clicar na impressora
4. "Ver o que está na fila de impressão"
5. Cancelar todos os documentos

### 3. Reiniciar Serviço de Spooler
```cmd
net stop spooler
net start spooler
```

### 4. Verificar Driver
- Atualizar driver da impressora
- Reinstalar se necessário
- Verificar compatibilidade

### 5. Testar Impressão
- Imprimir página de teste
- Verificar configurações
- Confirmar funcionamento

## ⚠️ **IMPORTANTE**
- Sempre testar após correções
- Verificar drivers atualizados
- Documentar solução aplicada
- Orientar usuário sobre manutenção

## 🏷️ **TAGS**
- impressora
- hardware
- spooler
- driver
- padrao
- copilot_knowledge
"""
        }
    ]
    
    for solucao in solucoes_padrao:
        file_path = base_path / "solucoes_padrao" / solucao["filename"]
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(solucao["content"])
        print(f"✅ Criado: {file_path}")
    
    # Criar arquivos de metadados
    stats = {
        'total_tickets': len(sample_tickets),
        'processed_tickets': len(sample_tickets),
        'filtered_tickets': len(sample_tickets),
        'categories': {
            'hardware/impressora': 1,
            'sistemas/acesso': 1,
            'sistemas/email': 1
        },
        'technicians': {
            'Maria Santos': 1,
            'Carlos Oliveira': 1,
            'Fernanda Rocha': 1
        },
        'errors': []
    }
    
    # Salvar estatísticas
    stats_file = base_path / "metadados" / "estatisticas.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    # Configuração do Copilot
    copilot_config = {
        "copilot_config": {
            "knowledge_base_name": "GLPI Knowledge Base - Exemplo",
            "version": "1.0.0",
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "total_documents": len(sample_tickets),
            "categories": list(stats['categories'].keys()),
            "filters": {
                "complexity": ["baixa", "media"],
                "status": ["resolvido"],
                "priority": ["baixa", "media"]
            },
            "metadata_fields": [
                "ticket_id",
                "category",
                "complexity",
                "technician",
                "resolution_time"
            ]
        }
    }
    
    config_file = base_path / "copilot_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(copilot_config, f, indent=2, ensure_ascii=False)
    
    # README
    readme_content = f"""# 🤖 Base de Conhecimento GLPI para Copilot - EXEMPLO

## 📊 **ESTATÍSTICAS**
- **Total de Tickets:** {len(sample_tickets)}
- **Tickets Processados:** {len(sample_tickets)}
- **Tickets Filtrados:** {len(sample_tickets)}
- **Data de Criação:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📁 **ESTRUTURA**
- `tickets_resolvidos/` - Tickets processados por categoria
- `solucoes_padrao/` - Soluções padrão para problemas comuns
- `metadados/` - Estatísticas e configurações

## 🏷️ **CATEGORIAS**
- hardware/impressora: 1 tickets
- sistemas/acesso: 1 tickets
- sistemas/email: 1 tickets

## 👥 **TÉCNICOS**
- Maria Santos: 1 tickets
- Carlos Oliveira: 1 tickets
- Fernanda Rocha: 1 tickets

## 🎯 **OBJETIVO**
Esta é uma base de conhecimento de exemplo criada para demonstrar 
a estrutura e funcionamento do sistema de extração de dados do GLPI 
para o Copilot do SharePoint.

## 📝 **COMO USAR**
1. Faça upload desta pasta para o SharePoint
2. Configure o Copilot para usar esta base de conhecimento
3. Teste com perguntas sobre problemas comuns de TI
4. Monitore e ajuste conforme necessário

## 🔄 **ATUALIZAÇÃO**
Execute o script `EXTRATOR_BASE_CONHECIMENTO_GLPI.py` para extrair 
dados reais do GLPI e substituir este exemplo.

## ⚠️ **NOTA**
Esta é uma base de conhecimento de exemplo. Para uso em produção, 
execute o extrator com dados reais do GLPI.
"""
    
    readme_file = base_path / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"\n✅ Base de conhecimento de exemplo criada com sucesso!")
    print(f"📁 Localização: {base_path}")
    print(f"📊 Total de arquivos: {len(sample_tickets) + len(solucoes_padrao) + 3}")
    print(f"\n🎯 Próximos passos:")
    print("1. Revisar os arquivos criados")
    print("2. Testar a estrutura")
    print("3. Fazer upload para o SharePoint")
    print("4. Configurar o Copilot")


if __name__ == "__main__":
    create_sample_knowledge_base()
