#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator de Base de Conhecimento GLPI para Copilot
Extrai tickets relevantes do GLPI e gera base de conhecimento estruturada
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import requests


class GLPIKnowledgeExtractor:
    def __init__(self, glpi_url: str, app_token: str, user_token: str):
        self.glpi_url = glpi_url
        self.app_token = app_token
        self.user_token = user_token
        self.session = requests.Session()
        self.session.headers.update(
            {
                "App-Token": app_token,
                "Authorization": f"user_token {user_token}",
                "Content-Type": "application/json",
            }
        )

        # Estatísticas
        self.stats: Dict[str, any] = {
            "total_tickets": 0,
            "processed_tickets": 0,
            "filtered_tickets": 0,
            "categories": {},
            "technicians": {},
            "errors": [],
        }

    def _init_session(self) -> str:
        """Inicia sessão com o GLPI e retorna o session token"""
        try:
            session_url = f"{self.glpi_url}/initSession"
            headers = {
                "App-Token": self.app_token,
                "Authorization": f"user_token {self.user_token}",
                "Content-Type": "application/json",
            }

            response = self.session.get(session_url, headers=headers, timeout=30)

            if response.status_code == 200:
                session_data = response.json()
                session_token = session_data.get("session_token")
                print(f"✅ Sessão iniciada com sucesso")
                return session_token
            else:
                print(f"❌ Erro ao iniciar sessão: {response.status_code}")
                print(f"   Resposta: {response.text[:200]}")
                return None

        except Exception as e:
            print(f"❌ Erro ao iniciar sessão: {e}")
            return None

    def extract_tickets_for_copilot(self, days_back: int = 365) -> List[Dict]:
        """Extrai tickets relevantes para base de conhecimento"""

        print(f"🔍 Extraindo tickets dos últimos {days_back} dias...")

        # Iniciar sessão primeiro
        session_token = self._init_session()
        if not session_token:
            print("❌ Falha ao iniciar sessão com GLPI")
            return []

        # Critérios de filtro para tickets relevantes
        filters = {
            "criteria": [
                {"field": "12", "searchtype": "equals", "value": "6"}  # Status  # Fechado
            ],
            "forcedisplay": [
                "2",  # ID
                "4",  # Título
                "5",  # Descrição
                "12",  # Status
                "3",  # Prioridade
                "7",  # Categoria
                "15",  # Data de criação
                "16",  # Data de fechamento
                "17",  # Solução
                "19",  # Técnico
                "21",  # Usuário
                "22",  # Tempo de resolução
            ],
            "range": "0-5000",  # Aumentar limite para capturar mais tickets
        }

        try:
            # Adicionar session token aos headers
            headers = {
                "App-Token": self.app_token,
                "Session-Token": session_token,
                "Content-Type": "application/json",
            }

            response = self.session.get(
                f"{self.glpi_url}/search/Ticket",
                params=filters,
                headers=headers,
                timeout=60,
                stream=False,  # Desabilitar streaming para respostas chunked
            )

            if response.status_code in [200, 206]:  # 200 OK ou 206 Partial Content
                try:
                    data = response.json()
                    tickets = data.get("data", [])
                    total_count = data.get("totalcount", len(tickets))
                    print(f"✅ Encontrados {len(tickets)} tickets fechados (Total: {total_count})")

                    # Filtrar tickets relevantes
                    relevant_tickets = self._filter_relevant_tickets(tickets)
                    print(f"✅ {len(relevant_tickets)} tickets relevantes")

                    return relevant_tickets
                except json.JSONDecodeError as e:
                    print(f"❌ Erro ao decodificar JSON: {e}")
                    print(f"   Status: {response.status_code}")
                    print(f"   Headers: {dict(response.headers)}")
                    print(f"   Resposta: {response.text[:500]}")
                    self.stats["errors"].append(f"JSON Decode Error: {e}")
                    return []
            else:
                print(f"❌ Erro na API: {response.status_code}")
                print(f"   Resposta: {response.text[:200]}")
                self.stats["errors"].append(f"API Error: {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            self.stats["errors"].append(f"Request Error: {e}")
            return []

    def _filter_relevant_tickets(self, tickets: List[Dict]) -> List[Dict]:
        """Filtra tickets relevantes para Copilot"""

        relevant_tickets = []

        # Palavras-chave para problemas básicos e recorrentes
        basic_keywords = [
            "senha",
            "password",
            "login",
            "acesso",
            "impressora",
            "printer",
            "print",
            "email",
            "outlook",
            "correio",
            "wifi",
            "rede",
            "network",
            "conexão",
            "software",
            "programa",
            "aplicativo",
            "instalação",
            "instalar",
            "instalar",
            "configuração",
            "configurar",
            "reset",
            "reiniciar",
            "restart",
            "atualização",
            "update",
            "atualizar",
            "licença",
            "license",
            "ativação",
            "backup",
            "cópia",
            "restauração",
            "antivírus",
            "antivirus",
            "segurança",
            "teclado",
            "mouse",
            "monitor",
            "som",
            "áudio",
            "audio",
            "câmera",
            "webcam",
            "microfone",
        ]

        for ticket in tickets:
            # Verificar se tem solução documentada
            solution = ticket.get("17", "").strip()
            if not solution or solution == "":
                continue

            # Verificar se é problema básico
            title = ticket.get("4", "").lower()
            description = ticket.get("5", "").lower()
            category = ticket.get("7", "").lower()

            content = f"{title} {description} {category}"

            # Verificar se contém palavras-chave de problemas básicos
            if any(keyword in content for keyword in basic_keywords):
                # Verificar prioridade (preferir baixa/média)
                priority = ticket.get("3", "")
                # Baixa, Média, Alta (evitar Crítica)
                if priority in ["1", "2", "3"]:
                    relevant_tickets.append(ticket)
                    self.stats["filtered_tickets"] += 1

                    # Contar categorias
                    cat = ticket.get("7", "N/A")
                    self.stats["categories"][cat] = self.stats["categories"].get(cat, 0) + 1

                    # Contar técnicos
                    tech = ticket.get("19", "N/A")
                    self.stats["technicians"][tech] = self.stats["technicians"].get(tech, 0) + 1

        return relevant_tickets

    def generate_knowledge_files(self, tickets: List[Dict]) -> None:
        """Gera arquivos de base de conhecimento"""

        print("📝 Gerando arquivos de base de conhecimento...")

        # Criar estrutura de diretórios
        base_path = Path("base_conhecimento_copilot")
        base_path.mkdir(exist_ok=True)

        # Criar subdiretórios
        subdirs = [
            "tickets_resolvidos/hardware",
            "tickets_resolvidos/software",
            "tickets_resolvidos/rede",
            "tickets_resolvidos/sistemas",
            "tickets_resolvidos/geral",
            "solucoes_padrao",
            "metadados",
        ]

        for subdir in subdirs:
            (base_path / subdir).mkdir(parents=True, exist_ok=True)

        # Processar cada ticket
        for ticket in tickets:
            try:
                category = self._categorize_ticket(ticket)
                filename = self._generate_filename(ticket, category)
                content = self._generate_markdown_content(ticket)

                # Salvar arquivo
                file_path = base_path / "tickets_resolvidos" / category / filename
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.stats["processed_tickets"] += 1
                print(f"✅ Arquivo salvo: {file_path}")

            except Exception as e:
                ticket_id = ticket.get("2", "N/A")
                print(f"❌ Erro ao processar ticket {ticket_id}: {e}")
                self.stats["errors"].append(f"Ticket {ticket_id}: {e}")

        # Gerar arquivos de metadados
        self._generate_metadata_files(base_path)

        processed = self.stats["processed_tickets"]
        print(f"✅ Processamento concluído: {processed} arquivos gerados")

    def _categorize_ticket(self, ticket: Dict) -> str:
        """Categoriza ticket baseado no conteúdo"""

        title = ticket.get("4", "").lower()
        description = ticket.get("5", "").lower()
        solution = ticket.get("17", "").lower()
        category = ticket.get("7", "").lower()

        content = f"{title} {description} {solution} {category}"

        # Hardware
        if any(
            keyword in content
            for keyword in [
                "impressora",
                "printer",
                "print",
                "teclado",
                "mouse",
                "monitor",
                "computador",
                "pc",
                "notebook",
                "desktop",
                "hardware",
            ]
        ):
            if "impressora" in content or "printer" in content:
                return "hardware/impressora"
            else:
                return "hardware/computador"

        # Software
        elif any(
            keyword in content
            for keyword in [
                "software",
                "programa",
                "aplicativo",
                "app",
                "instalação",
                "instalar",
                "licença",
                "license",
                "atualização",
                "update",
            ]
        ):
            return "software/aplicativos"

        # Rede
        elif any(
            keyword in content
            for keyword in [
                "wifi",
                "rede",
                "network",
                "conexão",
                "conectar",
                "internet",
                "vpn",
                "roteador",
                "router",
                "switch",
            ]
        ):
            return "rede/wifi"

        # Sistemas
        elif any(
            keyword in content
            for keyword in [
                "email",
                "outlook",
                "correio",
                "senha",
                "password",
                "login",
                "acesso",
                "sistema",
                "configuração",
                "configurar",
            ]
        ):
            if "email" in content or "outlook" in content:
                return "sistemas/email"
            elif "senha" in content or "password" in content:
                return "sistemas/acesso"
            else:
                return "sistemas/configuracoes"

        # Geral
        else:
            return "geral"

    def _generate_filename(self, ticket: Dict, category: str) -> str:
        """Gera nome do arquivo baseado no ticket"""

        title = ticket.get("4", "ticket_sem_titulo")
        ticket_id = ticket.get("2", "000")

        # Limpar título para nome de arquivo
        clean_title = re.sub(r"[^\w\s-]", "", title)
        clean_title = re.sub(r"[-\s]+", "_", clean_title)
        clean_title = clean_title.strip("_").lower()

        # Limitar tamanho do nome
        if len(clean_title) > 50:
            clean_title = clean_title[:50]

        return f"ticket_{ticket_id}_{clean_title}.md"

    def _generate_markdown_content(self, ticket: Dict) -> str:
        """Gera conteúdo Markdown do ticket"""

        # Extrair dados do ticket
        ticket_id = ticket.get("2", "N/A")
        title = ticket.get("4", "Sem título")
        description = ticket.get("5", "Sem descrição")
        solution = ticket.get("17", "Sem solução")
        priority = ticket.get("3", "N/A")
        category = ticket.get("7", "N/A")
        created_date = ticket.get("15", "N/A")
        closed_date = ticket.get("16", "N/A")
        technician = ticket.get("19", "N/A")
        user = ticket.get("21", "N/A")
        resolution_time = ticket.get("22", "N/A")

        # Mapear prioridade
        priority_map = {
            "1": "Baixa",
            "2": "Média",
            "3": "Alta",
            "4": "Crítica",
            "5": "Muito Crítica",
        }
        priority_text = priority_map.get(priority, priority)

        # Gerar tags baseadas no conteúdo
        tags = self._generate_tags(title, description, solution)

        # Gerar conteúdo Markdown
        content = f"""# {title}

## 📋 **PROBLEMA**
**Usuário:** {user}
**Data:** {created_date}
**Prioridade:** {priority_text}
**Categoria:** {category}
**Ticket ID:** {ticket_id}

### Descrição:
{description}

## 🔧 **SOLUÇÃO**
**Técnico:** {technician}
**Data de Resolução:** {closed_date}
**Tempo de Resolução:** {resolution_time}

### Solução Implementada:
{solution}

## 🏷️ **TAGS**
{chr(10).join(f"- {tag}" for tag in tags)}

## 📊 **METADADOS**
- **Complexidade:** Baixa/Média
- **Fonte:** GLPI
- **Data de Extração:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Copilot Ready:** Sim
- **Categoria GLPI:** {category}
- **Técnico Responsável:** {technician}
- **Tempo de Resolução:** {resolution_time}

## 🤖 **INSTRUÇÕES PARA COPILOT**
Este ticket contém uma solução para um problema comum de TI.
Use as informações da seção "Solução Implementada" para orientar
usuários com problemas similares. As tags ajudam a identificar
o tipo de problema e a complexidade da solução.
"""

        return content

    def _generate_tags(self, title: str, description: str, solution: str) -> List[str]:
        """Gera tags baseadas no conteúdo do ticket"""

        content = f"{title} {description} {solution}".lower()

        tags = ["ticket_resolvido", "copilot_knowledge"]

        # Tags por tipo de problema
        if any(keyword in content for keyword in ["senha", "password", "login"]):
            tags.append("acesso")
        if any(keyword in content for keyword in ["impressora", "printer", "print"]):
            tags.append("impressora")
        if any(keyword in content for keyword in ["email", "outlook", "correio"]):
            tags.append("email")
        if any(keyword in content for keyword in ["wifi", "rede", "network"]):
            tags.append("rede")
        if any(keyword in content for keyword in ["software", "programa", "aplicativo"]):
            tags.append("software")
        if any(keyword in content for keyword in ["instalação", "instalar", "instalar"]):
            tags.append("instalacao")
        if any(keyword in content for keyword in ["configuração", "configurar"]):
            tags.append("configuracao")
        if any(keyword in content for keyword in ["reset", "reiniciar", "restart"]):
            tags.append("reset")

        return tags

    def _generate_metadata_files(self, base_path: Path) -> None:
        """Gera arquivos de metadados"""

        # Estatísticas gerais
        stats_file = base_path / "metadados" / "estatisticas.json"
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)

        # Configuração do Copilot
        copilot_config = {
            "copilot_config": {
                "knowledge_base_name": "GLPI Knowledge Base",
                "version": "1.0.0",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_documents": self.stats["processed_tickets"],
                "categories": list(self.stats["categories"].keys()),
                "filters": {
                    "complexity": ["baixa", "media"],
                    "status": ["resolvido"],
                    "priority": ["baixa", "media"],
                },
                "metadata_fields": [
                    "ticket_id",
                    "category",
                    "complexity",
                    "technician",
                    "resolution_time",
                ],
            }
        }

        config_file = base_path / "copilot_config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(copilot_config, f, indent=2, ensure_ascii=False)

        # README da base de conhecimento
        readme_content = f"""# 🤖 Base de Conhecimento GLPI para Copilot

## 📊 **ESTATÍSTICAS**
- **Total de Tickets:** {self.stats['total_tickets']}
- **Tickets Processados:** {self.stats['processed_tickets']}
- **Tickets Filtrados:** {self.stats['filtered_tickets']}
- **Data de Extração:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📁 **ESTRUTURA**
- `tickets_resolvidos/` - Tickets processados por categoria
- `solucoes_padrao/` - Soluções padrão para problemas comuns
- `metadados/` - Estatísticas e configurações

## 🏷️ **CATEGORIAS**
{chr(10).join(f"- {cat}: {count} tickets" for cat, count in self.stats['categories'].items())}

## 👥 **TÉCNICOS**
{chr(10).join(f"- {tech}: {count} tickets" for tech, count in self.stats['technicians'].items())}

## 🎯 **OBJETIVO**
Esta base de conhecimento foi criada para treinar o Copilot do
SharePoint com soluções de problemas básicos e recorrentes extraídos
do GLPI. O foco está em problemas de baixa/média complexidade que
podem ser resolvidos com orientações automatizadas.

## 📝 **COMO USAR**
1. Faça upload desta pasta para o SharePoint
2. Configure o Copilot para usar esta base de conhecimento
3. Teste com perguntas sobre problemas comuns de TI
4. Monitore e ajuste conforme necessário

## 🔄 **ATUALIZAÇÃO**
Execute o script `extract_glpi_knowledge.py` periodicamente para
manter a base atualizada com novos tickets resolvidos.
"""

        readme_file = base_path / "README.md"
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(readme_content)

        print("✅ Arquivos de metadados gerados")


def main():
    """Função principal"""

    print("🤖 Extrator de Base de Conhecimento GLPI para Copilot")
    print("=" * 60)

    # Configurações do GLPI
    GLPI_URL = input("URL do GLPI (ex: http://glpi.exemplo.com/glpi): ").strip()
    APP_TOKEN = input("App Token do GLPI: ").strip()
    USER_TOKEN = input("User Token do GLPI: ").strip()

    if not all([GLPI_URL, APP_TOKEN, USER_TOKEN]):
        print("❌ Configurações incompletas. Abortando.")
        return

    # Criar extrator
    extractor = GLPIKnowledgeExtractor(GLPI_URL, APP_TOKEN, USER_TOKEN)

    # Extrair tickets relevantes
    print("\n🔍 Extraindo tickets relevantes...")
    tickets = extractor.extract_tickets_for_copilot(days_back=365)

    if not tickets:
        print("❌ Nenhum ticket relevante encontrado.")
        return

    # Gerar arquivos de base de conhecimento
    print("\n📝 Gerando arquivos de base de conhecimento...")
    extractor.generate_knowledge_files(tickets)

    # Resumo final
    print("\n" + "=" * 60)
    print("✅ EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
    processed = extractor.stats["processed_tickets"]
    print(f"📊 Total de tickets processados: {processed}")
    print("📁 Base de conhecimento criada em: base_conhecimento_copilot/")
    print("📋 Estatísticas salvas em: base_conhecimento_copilot/metadados/")
    print("\n🎯 Próximos passos:")
    print("1. Revisar os arquivos gerados")
    print("2. Fazer upload para o SharePoint")
    print("3. Configurar o Copilot")
    print("4. Testar com usuários")


if __name__ == "__main__":
    main()
