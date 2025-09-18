#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLPI Metrics Collector - Script Consolidado para Coleta de Métricas

Este script serve como documentação viva e ferramenta centralizada para coleta
de todas as métricas necessárias do sistema GLPI, incluindo:
- Métricas gerais do sistema
- Tickets novos
- Ranking de técnicos por nível
- Status de tickets por nível de atendimento

Autor: Sistema de Engenharia
Data: 2025-01-22
Versão: 1.0
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from colorama import Fore, Style, init

# Inicializar colorama para cores no terminal
init(autoreset=True)


@dataclass
class GLPIConfig:
    """Configuração para conexão com GLPI"""

    base_url: str
    app_token: str
    user_token: str
    username: str
    password: str

    @classmethod
    def from_env(cls) -> "GLPIConfig":
        """Carrega configuração das variáveis de ambiente"""
        return cls(
            base_url=os.getenv("GLPI_BASE_URL", "http://localhost/glpi"),
            app_token=os.getenv("GLPI_APP_TOKEN", ""),
            user_token=os.getenv("GLPI_USER_TOKEN", ""),
            username=os.getenv("GLPI_USERNAME", ""),
            password=os.getenv("GLPI_PASSWORD", ""),
        )


class GLPIMetricsCollector:
    """
    Coletor centralizado de métricas do GLPI

    Este coletor implementa todas as funcionalidades necessárias para:
    1. Autenticação segura com session tokens
    2. Coleta de métricas gerais
    3. Listagem de tickets novos
    4. Ranking de técnicos por nível
    5. Análise de status por nível de atendimento
    """

    def __init__(self, config: GLPIConfig):
        self.config = config
        self.session_token: Optional[str] = None
        self.session = requests.Session()

        # Headers padrão para todas as requisições
        self.session.headers.update(
            {"Content-Type": "application/json", "App-Token": self.config.app_token}
        )

        # Mapeamento de cores por nível de técnico
        self.level_colors = {
            "N1": Fore.GREEN,  # Verde para N1 (Júnior)
            "N2": Fore.YELLOW,  # Amarelo para N2 (Pleno)
            "N3": Fore.BLUE,  # Azul para N3 (Sênior)
            "N4": Fore.RED,  # Vermelho para N4 (Especialista)
        }

        # Status de tickets mapeados
        self.ticket_status = {
            1: "novo",  # Novo
            2: "em_progresso",  # Processando (atribuído)
            3: "planejado",  # Processando (planejado)
            4: "pendente",  # Pendente
            5: "solucionado",  # Solucionado
            6: "fechado",  # Fechado
        }

    def login(self) -> bool:
        """
        Realiza autenticação no GLPI e obtém session token

        Endpoint: POST /apirest.php/initSession

        Métodos de autenticação suportados:
        1. User Token (recomendado para automação)
        2. Username/Password (para usuários interativos)

        Returns:
            bool: True se autenticação foi bem-sucedida
        """
        print(f"{Fore.CYAN}Iniciando autenticacao no GLPI...{Style.RESET_ALL}")

        url = f"{self.config.base_url}/apirest.php/initSession"

        # Tentar autenticação com user token primeiro
        if self.config.user_token:
            headers = {"Authorization": f"user_token {self.config.user_token}"}
            print(f"{Fore.YELLOW}   Usando User Token para autenticação{Style.RESET_ALL}")
        else:
            # Fallback para username/password
            auth_data = {"login": self.config.username, "password": self.config.password}
            headers = {}
            print(f"{Fore.YELLOW}   Usando Username/Password para autenticação{Style.RESET_ALL}")

        try:
            if self.config.user_token:
                response = self.session.get(url, headers=headers)
            else:
                response = self.session.post(url, json=auth_data, headers=headers)

            response.raise_for_status()

            auth_response = response.json()
            self.session_token = auth_response.get("session_token")

            if self.session_token:
                # Adicionar session token aos headers padrão
                self.session.headers.update({"Session-Token": self.session_token})
                print(f"{Fore.GREEN}Autenticacao realizada com sucesso!{Style.RESET_ALL}")
                print(f"{Fore.CYAN}   Session Token: {self.session_token[:20]}...{Style.RESET_ALL}")
                return True
            else:
                print(
                    f"{Fore.RED}❌ Falha na autenticação: Session token não recebido{Style.RESET_ALL}"
                )
                return False

        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}❌ Erro na autenticação: {e}{Style.RESET_ALL}")
            return False
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}❌ Erro ao decodificar resposta de autenticação: {e}{Style.RESET_ALL}")
            return False

    def get_status_geral(self) -> Dict[str, Any]:
        """
        Coleta métricas gerais do sistema (sem filtro de nível)

        Endpoint: GET /apirest.php/search/Ticket

        Parâmetros utilizados:
        - forcedisplay[0]: ID do ticket
        - forcedisplay[1]: Status do ticket
        - forcedisplay[2]: Prioridade
        - forcedisplay[3]: Data de criação
        - range: 0-9999 (todos os tickets)

        Returns:
            Dict contendo contadores por status
        """
        print(f"{Fore.CYAN}📊 Coletando métricas gerais do sistema...{Style.RESET_ALL}")

        url = f"{self.config.base_url}/apirest.php/search/Ticket"

        params = {
            "forcedisplay[0]": 2,  # ID
            "forcedisplay[1]": 12,  # Status
            "forcedisplay[2]": 3,  # Prioridade
            "forcedisplay[3]": 15,  # Data de criação
            "range": "0-9999",  # Todos os tickets
        }

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            tickets = data.get("data", [])

            # Contar tickets por status
            status_count = {
                "novo": 0,
                "em_progresso": 0,
                "planejado": 0,
                "pendente": 0,
                "solucionado": 0,
                "fechado": 0,
            }
            total_tickets = len(tickets)

            for ticket in tickets:
                status_id = ticket.get("12")  # Campo de status
                if status_id and int(status_id) in self.ticket_status:
                    status_name = self.ticket_status[int(status_id)]
                    status_count[status_name] += 1

            metrics = {
                "total_tickets": total_tickets,
                "status_breakdown": status_count,
                "timestamp": datetime.now().isoformat(),
                "endpoint_used": url,
            }

            print(
                f"{Fore.GREEN}✅ Métricas gerais coletadas: {total_tickets} tickets total{Style.RESET_ALL}"
            )

            # Exibir resumo
            for status, count in status_count.items():
                if count > 0:
                    print(f"   {status.title()}: {count}")

            return metrics

        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}❌ Erro ao coletar métricas gerais: {e}{Style.RESET_ALL}")
            return {}
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}❌ Erro ao decodificar resposta de métricas: {e}{Style.RESET_ALL}")
            return {}

    def get_tickets_novos(self) -> List[Dict[str, Any]]:
        """
        Lista todos os tickets em status "Novo" (status = 1)

        Endpoint: GET /apirest.php/search/Ticket

        Critérios de busca:
        - Status = 1 (Novo)
        - Ordenação por data de criação (mais recentes primeiro)

        Campos retornados:
        - ID do ticket
        - Título/Nome
        - Status
        - Prioridade
        - Data de criação
        - Técnico atribuído (se houver)

        Returns:
            Lista de tickets novos
        """
        print(f"{Fore.CYAN}🎫 Coletando tickets novos...{Style.RESET_ALL}")

        url = f"{self.config.base_url}/apirest.php/search/Ticket"

        params = {
            "criteria[0][field]": 12,  # Campo de status
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": 1,  # Status "Novo"
            "forcedisplay[0]": 2,  # ID
            "forcedisplay[1]": 1,  # Nome/Título
            "forcedisplay[2]": 12,  # Status
            "forcedisplay[3]": 3,  # Prioridade
            "forcedisplay[4]": 15,  # Data de criação
            "forcedisplay[5]": 5,  # Técnico atribuído
            "order": "DESC",  # Mais recentes primeiro
            "sort": 15,  # Ordenar por data de criação
            "range": "0-100",  # Limitar a 100 tickets
        }

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            tickets = data.get("data", [])

            tickets_novos = []
            for ticket in tickets:
                ticket_info = {
                    "id": ticket.get("2"),
                    "titulo": ticket.get("1"),
                    "status": "novo",
                    "prioridade": ticket.get("3"),
                    "data_criacao": ticket.get("15"),
                    "tecnico_atribuido": ticket.get("5"),
                }
                tickets_novos.append(ticket_info)

            print(f"{Fore.GREEN}✅ Encontrados {len(tickets_novos)} tickets novos{Style.RESET_ALL}")

            # Exibir primeiros 5 tickets como exemplo
            if tickets_novos:
                print(f"{Fore.YELLOW}   Primeiros 5 tickets novos:{Style.RESET_ALL}")
                for i, ticket in enumerate(tickets_novos[:5]):
                    print(f"   {i+1}. ID: {ticket['id']} - {ticket['titulo'][:50]}...")

            return tickets_novos

        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}❌ Erro ao coletar tickets novos: {e}{Style.RESET_ALL}")
            return []
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}❌ Erro ao decodificar resposta de tickets: {e}{Style.RESET_ALL}")
            return []

    def get_ranking_tecnicos(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Coleta ranking de técnicos seguindo a implementação real do backend

        Processo baseado no glpi_service.py:
        1. Buscar todos os técnicos ativos com perfil técnico (Profile_User)
        2. Para cada técnico, determinar o nível baseado nos grupos GLPI
        3. Calcular métricas de tickets (total, resolvidos, pendentes)
        4. Organizar ranking por nível
        5. Retornar ranking estruturado

        Returns:
            Dict com ranking por nível: {'N1': [...], 'N2': [...], etc}
        """
        print(
            f"{Fore.CYAN}🏆 Coletando ranking de técnicos (implementação real do backend)...{Style.RESET_ALL}"
        )

        # Mapeamento de níveis para IDs de grupos GLPI (conforme backend)
        service_levels = {
            "N1": 89,  # CC-SE-SUBADM-DTIC > N1
            "N2": 90,  # CC-SE-SUBADM-DTIC > N2
            "N3": 91,  # CC-SE-SUBADM-DTIC > N3
            "N4": 92,  # CC-SE-SUBADM-DTIC > N4
        }

        ranking_por_nivel = {"N1": [], "N2": [], "N3": [], "N4": []}

        try:
            print(f"{Fore.BLUE}   Buscando técnicos ativos com perfil técnico...{Style.RESET_ALL}")

            # 1. Buscar todos os técnicos ativos (método do backend)
            tecnicos_ativos = self._get_all_active_technicians()

            if not tecnicos_ativos:
                print(f"{Fore.YELLOW}   ⚠️  Nenhum técnico ativo encontrado{Style.RESET_ALL}")
                return ranking_por_nivel

            print(
                f"{Fore.GREEN}   ✅ Encontrados {len(tecnicos_ativos)} técnicos ativos{Style.RESET_ALL}"
            )

            # 2. Para cada técnico, determinar nível e calcular métricas
            for tecnico in tecnicos_ativos:
                try:
                    tecnico_id = tecnico["id"]
                    tecnico_nome = tecnico["nome"]

                    # Determinar nível do técnico baseado nos grupos GLPI
                    nivel = self._get_technician_level_from_groups(tecnico_id)

                    if not nivel or nivel not in service_levels:
                        print(
                            f"{Fore.YELLOW}      ⚠️  Técnico {tecnico_nome} não está em grupo de nível válido{Style.RESET_ALL}"
                        )
                        continue

                    # Calcular métricas do técnico
                    metricas = self._get_technician_metrics_corrected(tecnico_id)

                    tecnico_data = {
                        "id": tecnico_id,
                        "nome": tecnico_nome,
                        "nivel": nivel,
                        "grupo_id": service_levels[nivel],
                        "posicao": 0,  # Será calculado após ordenação
                        "tickets_total": metricas.get("total", 0),
                        "tickets_resolvidos": metricas.get("resolvidos", 0),
                        "tickets_pendentes": metricas.get("pendentes", 0),
                        "taxa_resolucao": metricas.get("taxa_resolucao", 0.0),
                    }

                    ranking_por_nivel[nivel].append(tecnico_data)

                except Exception as e:
                    print(
                        f"{Fore.RED}      ❌ Erro ao processar técnico {tecnico.get('nome', 'Desconhecido')}: {e}{Style.RESET_ALL}"
                    )
                    continue

            # 3. Ordenar técnicos por nível (por tickets resolvidos)
            for nivel in ranking_por_nivel:
                ranking_por_nivel[nivel].sort(key=lambda x: x["tickets_resolvidos"], reverse=True)

                # Atualizar posições
                for i, tecnico in enumerate(ranking_por_nivel[nivel]):
                    tecnico["posicao"] = i + 1

            # 4. Exibir resumo colorido
            print(f"{Fore.GREEN}✅ Ranking de técnicos coletado:{Style.RESET_ALL}")
            for nivel, tecnicos_nivel in ranking_por_nivel.items():
                if tecnicos_nivel:
                    color = self.level_colors.get(nivel, Fore.WHITE)
                    print(f"{color}   {nivel}: {len(tecnicos_nivel)} técnicos{Style.RESET_ALL}")

                    # Mostrar top 3 técnicos de cada nível
                    for tecnico in tecnicos_nivel[:3]:
                        print(
                            f"{color}      {tecnico['posicao']}º {tecnico['nome']} - {tecnico['tickets_resolvidos']} resolvidos ({tecnico['tickets_total']} total){Style.RESET_ALL}"
                        )

            return ranking_por_nivel

        except Exception as e:
            print(f"{Fore.RED}❌ Erro ao coletar ranking: {str(e)}{Style.RESET_ALL}")
            return ranking_por_nivel

    def get_status_por_nivel(self) -> Dict[str, Dict[str, int]]:
        """
        Coleta contagem de tickets por status, separado por nível de atendimento

        Implementação baseada no backend real:
        1. Para cada nível (N1, N2, N3, N4):
        2. Buscar tickets atribuídos ao grupo GLPI desse nível
        3. Contar por status usando o mapeamento correto

        Returns:
            Dict aninhado: {nivel: {status: count}}
        """
        print(
            f"{Fore.CYAN}📈 Coletando status de tickets por nível (implementação real do backend)...{Style.RESET_ALL}"
        )

        # Mapeamento de status conforme backend
        status_map = {
            1: "novo",
            2: "em_progresso",
            3: "planejado",
            4: "pendente",
            5: "solucionado",
            6: "fechado",
        }

        status_por_nivel = {
            "N1": {
                "novo": 0,
                "em_progresso": 0,
                "planejado": 0,
                "pendente": 0,
                "solucionado": 0,
                "fechado": 0,
            },
            "N2": {
                "novo": 0,
                "em_progresso": 0,
                "planejado": 0,
                "pendente": 0,
                "solucionado": 0,
                "fechado": 0,
            },
            "N3": {
                "novo": 0,
                "em_progresso": 0,
                "planejado": 0,
                "pendente": 0,
                "solucionado": 0,
                "fechado": 0,
            },
            "N4": {
                "novo": 0,
                "em_progresso": 0,
                "planejado": 0,
                "pendente": 0,
                "solucionado": 0,
                "fechado": 0,
            },
        }

        # Mapeamento de níveis para IDs de grupos GLPI
        service_levels = {
            "N1": 89,  # CC-SE-SUBADM-DTIC > N1
            "N2": 90,  # CC-SE-SUBADM-DTIC > N2
            "N3": 91,  # CC-SE-SUBADM-DTIC > N3
            "N4": 92,  # CC-SE-SUBADM-DTIC > N4
        }

        # Para cada nível, buscar tickets do grupo correspondente
        for nivel, group_id in service_levels.items():
            print(
                f"{Fore.YELLOW}   Processando nível {nivel} (Grupo ID: {group_id})...{Style.RESET_ALL}"
            )

            # Buscar tickets do grupo
            url = f"{self.config.base_url}/apirest.php/search/Ticket"

            params = {
                "criteria[0][field]": 8,  # Campo do grupo atribuído (Groups_id)
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": group_id,
                "forcedisplay[0]": 12,  # Status
                "forcedisplay[1]": 2,  # ID do ticket
                "range": "0-9999",  # Aumentar limite
            }

            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()

                data = response.json()
                tickets = data.get("data", [])

                print(f"      Grupo {group_id}: {len(tickets)} tickets encontrados")

                # Contar por status
                for ticket in tickets:
                    status_id = int(ticket.get("12", 0))
                    status_name = status_map.get(status_id, "novo")

                    if status_name in status_por_nivel[nivel]:
                        status_por_nivel[nivel][status_name] += 1

            except requests.exceptions.RequestException as e:
                print(f"      Erro ao buscar tickets do grupo {group_id}: {e}")
                continue

        # Exibir resumo colorido
        print(f"{Fore.GREEN}✅ Status por nível coletado:{Style.RESET_ALL}")
        for nivel, status_counts in status_por_nivel.items():
            color = self.level_colors.get(nivel, Fore.WHITE)
            total_nivel = sum(status_counts.values())
            print(f"{color}   {nivel} (Total: {total_nivel}): {Style.RESET_ALL}")

            for status, count in status_counts.items():
                if count > 0:
                    print(f"{color}      {status.title()}: {count}{Style.RESET_ALL}")

        return status_por_nivel

    def _get_all_active_technicians(self) -> List[Dict[str, Any]]:
        """
        Busca todos os técnicos ativos seguindo a implementação real do backend

        MÉTODO CORRETO: Usar os IDs específicos dos técnicos válidos da entidade CAU
        que estão ativos (is_active=1) e não deletados (is_deleted=0)

        Returns:
            Lista de técnicos com ID e nome
        """
        print("      Buscando técnicos ativos usando IDs específicos da entidade CAU...")

        # IDs dos técnicos válidos da entidade CAU (conforme fornecido pelo usuário)
        technician_ids = [
            "696",
            "32",
            "141",
            "60",
            "69",
            "1032",
            "252",
            "721",
            "926",
            "1291",
            "185",
            "1331",
            "1404",
            "1088",
            "1263",
            "10",
            "53",
            "250",
            "1471",
        ]

        tecnicos_ativos = []

        for tech_id in technician_ids:
            try:
                # Buscar detalhes do usuário e verificar se está ativo e não deletado
                user_details = self._get_user_details(tech_id)
                if user_details:
                    tecnicos_ativos.append({"id": tech_id, "nome": user_details["nome"]})
            except Exception as e:
                print(f"      Erro ao processar técnico {tech_id}: {e}")
                continue

        print(f"      {len(tecnicos_ativos)} técnicos ativos válidos encontrados")
        return tecnicos_ativos

    def _parse_technician_id(self, tech_field) -> Optional[str]:
        """
        Parse correto do campo users_id_tech que pode vir como string, lista ou número
        Implementação baseada no backend real
        """
        if not tech_field:
            return None

        # Se for lista, pegar o primeiro item válido
        if isinstance(tech_field, list):
            for item in tech_field:
                if item and str(item) != "0":
                    return str(item)
            return None

        # Se for string, verificar se é JSON
        if isinstance(tech_field, str):
            # Tentar fazer parse como JSON
            try:
                import json

                parsed = json.loads(tech_field)
                if isinstance(parsed, list) and parsed:
                    for item in parsed:
                        if item and str(item) != "0":
                            return str(item)
                elif parsed and str(parsed) != "0":
                    return str(parsed)
            except Exception:
                # Se não for JSON, tratar como string simples
                if tech_field and tech_field != "0":
                    return str(tech_field)
            return None

        # Se for número
        if isinstance(tech_field, (int, float)):
            if tech_field and str(tech_field) != "0":
                return str(tech_field)

        return None

    def _get_user_id_by_name(self, user_name: str) -> Optional[str]:
        """
        Busca o ID do usuário pelo nome

        Args:
            user_name: Nome do usuário

        Returns:
            ID do usuário ou None se não encontrado
        """
        try:
            url = f"{self.config.base_url}/apirest.php/search/User"

            params = {
                "criteria[0][field]": 1,  # Campo nome
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": user_name,
                "forcedisplay[0]": 2,  # ID
                "forcedisplay[1]": 1,  # Nome
                "range": "0-10",
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            users = data.get("data", [])

            if users and isinstance(users, list) and len(users) > 0:
                user = users[0]
                if isinstance(user, dict):
                    return user.get("2")  # ID do usuário

            return None

        except requests.exceptions.RequestException as e:
            print(f"      Erro ao buscar ID do usuário {user_name}: {e}")
            return None

    def _get_technician_level_from_groups(self, user_id: str) -> Optional[str]:
        """
        Determina o nível do técnico baseado nos grupos GLPI (implementação real do backend)

        Args:
            user_id: ID do usuário/técnico

        Returns:
            Nível (N1, N2, N3, N4) ou None se não encontrado
        """
        # Mapeamento de níveis para IDs de grupos GLPI
        service_levels = {
            "N1": 89,  # CC-SE-SUBADM-DTIC > N1
            "N2": 90,  # CC-SE-SUBADM-DTIC > N2
            "N3": 91,  # CC-SE-SUBADM-DTIC > N3
            "N4": 92,  # CC-SE-SUBADM-DTIC > N4
        }

        try:
            # Buscar grupos do usuário
            url = f"{self.config.base_url}/apirest.php/search/Group_User"

            params = {
                "range": "0-99",
                "criteria[0][field]": "4",  # Campo users_id
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(user_id),
                "forcedisplay[0]": "3",  # groups_id
                "forcedisplay[1]": "4",  # users_id
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if data and isinstance(data, dict) and data.get("data"):
                for group_entry in data["data"]:
                    if isinstance(group_entry, dict) and "3" in group_entry:
                        try:
                            group_id = int(group_entry["3"])

                            # Verificar se o grupo corresponde aos service_levels
                            for level, level_group_id in service_levels.items():
                                if group_id == level_group_id:
                                    return level
                        except (ValueError, TypeError):
                            continue

            # Se não encontrou nos grupos 89-92, usar fallback por nome
            return self._get_technician_level_by_name_fallback(user_id)

        except requests.exceptions.RequestException as e:
            print(f"      Erro ao buscar grupos do usuário {user_id}: {e}")
            return self._get_technician_level_by_name_fallback(user_id)

    def _get_technician_level_by_name_fallback(self, user_id: str) -> str:
        """
        Determina o nível do técnico baseado no nome (fallback do backend)
        Mapeamento hardcoded dos técnicos por nível conforme backend real
        """
        try:
            # Buscar nome do usuário
            user_url = f"{self.config.base_url}/apirest.php/User/{user_id}"
            response = self.session.get(user_url)
            if response.status_code != 200:
                return "N1"  # Nível padrão

            user_data = response.json()
            firstname = user_data.get("firstname", "").lower()
            realname = user_data.get("realname", "").lower()

            # Mapeamento correto dos técnicos por nível (conforme backend real)
            n1_names = [
                "gabriel andrade da conceicao",
                "nicolas fernando muniz nunez",
            ]

            n2_names = [
                "alessandro carbonera vieira",
                "jonathan nascimento moletta",
                "thales vinicius paz leite",
                "leonardo trojan repiso riela",
                "edson joel dos santos silva",
                "luciano marcelino da silva",
            ]

            n3_names = [
                "anderson da silva morim de oliveira",
                "silvio godinho valim",
                "jorge antonio vicente júnior",
                "pablo hebling guimaraes",
                "miguelangelo ferreira",
            ]

            n4_names = [
                "gabriel silva machado",
                "luciano de araujo silva",
                "wagner mengue",
                "paulo césar pedó nunes",
                "alexandre rovinski almoarqueg",
            ]

            # Verificar em qual nível o técnico está
            full_name = f"{firstname} {realname}".strip()

            if full_name in n4_names:
                return "N4"
            elif full_name in n3_names:
                return "N3"
            elif full_name in n2_names:
                return "N2"
            elif full_name in n1_names:
                return "N1"
            else:
                # Se não encontrou, usar N1 como padrão
                return "N1"

        except Exception as e:
            print(f"      Erro ao determinar nível por nome para usuário {user_id}: {e}")
            return "N1"  # Nível padrão em caso de erro

    def _get_technician_metrics_corrected(self, tecnico_id: str) -> Dict[str, Any]:
        """
        Coleta métricas de performance de um técnico específico (implementação corrigida)

        Args:
            tecnico_id: ID do técnico no GLPI

        Returns:
            Dict com métricas: total, resolvidos, pendentes, taxa_resolucao
        """
        url = f"{self.config.base_url}/apirest.php/search/Ticket"

        # Buscar todos os tickets atribuídos ao técnico
        params = {
            "criteria[0][field]": 5,  # Campo técnico atribuído
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": tecnico_id,
            "forcedisplay[0]": 2,  # ID
            "forcedisplay[1]": 12,  # Status
            "range": "0-1000",
        }

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            tickets = data.get("data", [])

            total = len(tickets)
            resolvidos = 0
            pendentes = 0

            for ticket in tickets:
                status_id = int(ticket.get("12", 0))

                if status_id in [5, 6]:  # Solucionado ou Fechado
                    resolvidos += 1
                elif status_id in [2, 3, 4]:  # Em progresso, Planejado, Pendente
                    pendentes += 1

            taxa_resolucao = (resolvidos / total * 100) if total > 0 else 0

            return {
                "total": total,
                "resolvidos": resolvidos,
                "pendentes": pendentes,
                "taxa_resolucao": round(taxa_resolucao, 1),
            }

        except requests.exceptions.RequestException as e:
            print(f"        Erro ao buscar métricas do técnico {tecnico_id}: {e}")
            return {"total": 0, "resolvidos": 0, "pendentes": 0, "taxa_resolucao": 0.0}

    def _get_user_details(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca detalhes de um usuário específico com filtros de ativo e não deletado

        Args:
            user_id: ID do usuário

        Returns:
            Dados do usuário ou None se não encontrado/inválido
        """
        url = f"{self.config.base_url}/apirest.php/User/{user_id}"

        try:
            response = self.session.get(url)
            response.raise_for_status()

            user_data = response.json()

            # Aplicar filtros conforme glpi_service.py
            is_active = str(user_data.get("is_active", "0")).strip()
            is_deleted = str(user_data.get("is_deleted", "0")).strip()

            # Verificar se o usuário está ativo e não deletado
            if str(is_active) != "1":
                print(f"      Usuário {user_id} inativo (is_active={is_active})")
                return None

            if str(is_deleted) == "1":
                print(f"      Usuário {user_id} deletado (is_deleted={is_deleted})")
                return None

            # Não verificar perfil técnico pois já estamos buscando apenas técnicos ativos

            # Construir nome completo conforme glpi_service.py
            firstname = str(user_data.get("firstname", "")).strip()
            realname = str(user_data.get("realname", "")).strip()
            username = str(user_data.get("name", "")).strip()

            full_name = f"{firstname} {realname}".strip()
            if not full_name:
                full_name = username
            if not full_name:
                full_name = f"Usuário {user_id}"

            return {
                "id": user_id,
                "nome": full_name,
                "login": username,
                "ativo": int(is_active),
                "is_active": is_active,
                "is_deleted": is_deleted,
            }

        except requests.exceptions.RequestException as e:
            print(f"      Erro ao buscar usuário {user_id}: {e}")
            return None

    def logout(self) -> bool:
        """
        Finaliza a sessão no GLPI (killSession)

        Endpoint: GET /apirest.php/killSession

        É importante sempre finalizar a sessão para:
        1. Liberar recursos no servidor GLPI
        2. Invalidar o session token
        3. Manter boas práticas de segurança

        Returns:
            bool: True se logout foi bem-sucedido
        """
        if not self.session_token:
            print(f"{Fore.YELLOW}⚠️  Nenhuma sessão ativa para finalizar{Style.RESET_ALL}")
            return True

        print(f"{Fore.CYAN}🔓 Finalizando sessão no GLPI...{Style.RESET_ALL}")

        url = f"{self.config.base_url}/apirest.php/killSession"

        try:
            response = self.session.get(url)
            response.raise_for_status()

            # Limpar session token
            self.session_token = None
            if "Session-Token" in self.session.headers:
                del self.session.headers["Session-Token"]

            print(f"{Fore.GREEN}✅ Sessão finalizada com sucesso!{Style.RESET_ALL}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}❌ Erro ao finalizar sessão: {e}{Style.RESET_ALL}")
            return False

    def collect_all_metrics(self) -> Dict[str, Any]:
        """
        Executa coleta completa de todas as métricas

        Ordem de execução:
        1. Autenticação
        2. Métricas gerais
        3. Tickets novos
        4. Ranking de técnicos
        5. Status por nível
        6. Finalização da sessão

        Returns:
            Dict consolidado com todas as métricas
        """
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}🚀 INICIANDO COLETA COMPLETA DE MÉTRICAS GLPI{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")

        start_time = datetime.now()

        # Estrutura de resultado
        result = {
            "timestamp": start_time.isoformat(),
            "success": False,
            "metrics": {},
            "errors": [],
        }

        try:
            # 1. Autenticação
            if not self.login():
                result["errors"].append("Falha na autenticação")
                return result

            # 2. Métricas gerais
            print(f"\n{Fore.MAGENTA}📊 FASE 1: Métricas Gerais{Style.RESET_ALL}")
            result["metrics"]["status_geral"] = self.get_status_geral()

            # 3. Tickets novos
            print(f"\n{Fore.MAGENTA}🎫 FASE 2: Tickets Novos{Style.RESET_ALL}")
            result["metrics"]["tickets_novos"] = self.get_tickets_novos()

            # 4. Ranking de técnicos
            print(f"\n{Fore.MAGENTA}🏆 FASE 3: Ranking de Técnicos{Style.RESET_ALL}")
            result["metrics"]["ranking_tecnicos"] = self.get_ranking_tecnicos()

            # 5. Status por nível
            print(f"\n{Fore.MAGENTA}📈 FASE 4: Status por Nível{Style.RESET_ALL}")
            result["metrics"]["status_por_nivel"] = self.get_status_por_nivel()

            result["success"] = True

        except Exception as e:
            error_msg = f"Erro durante coleta: {str(e)}"
            result["errors"].append(error_msg)
            print(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")

        finally:
            # 6. Finalizar sessão sempre
            print(f"\n{Fore.MAGENTA}🔓 FASE 5: Finalização{Style.RESET_ALL}")
            self.logout()

        # Calcular tempo total
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        result["duration_seconds"] = duration

        # Resumo final
        print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        if result["success"]:
            print(f"{Fore.GREEN}✅ COLETA CONCLUÍDA COM SUCESSO!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ COLETA FINALIZADA COM ERROS{Style.RESET_ALL}")

        print(f"{Fore.CYAN}⏱️  Tempo total: {duration:.2f} segundos{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")

        return result


def save_metrics_to_file(metrics: Dict[str, Any], filename: Optional[str] = None) -> str:
    """
    Salva as métricas coletadas em arquivo JSON

    Args:
        metrics: Dados das métricas
        filename: Nome do arquivo (opcional)

    Returns:
        Caminho do arquivo salvo
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"glpi_metrics_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print(f"{Fore.GREEN}💾 Métricas salvas em: {filename}{Style.RESET_ALL}")
    return filename


def main():
    """
    Função principal - ponto de entrada do script

    Execução:
    1. Carrega configuração
    2. Inicializa coletor
    3. Executa coleta completa
    4. Salva resultados
    """
    print(f"{Fore.CYAN}GLPI Metrics Collector v1.0{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Documentacao viva para coleta de metricas GLPI{Style.RESET_ALL}\n")

    # Carregar configuração
    try:
        config = GLPIConfig.from_env()

        # Validar configuração mínima
        if not config.base_url:
            print(f"{Fore.RED}❌ GLPI_BASE_URL não configurado{Style.RESET_ALL}")
            return

        if not config.app_token:
            print(f"{Fore.RED}❌ GLPI_APP_TOKEN não configurado{Style.RESET_ALL}")
            return

        if not config.user_token and not (config.username and config.password):
            error_msg = "❌ Credenciais não configuradas " "(USER_TOKEN ou USERNAME/PASSWORD)"
            print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
            return

    except Exception as e:
        print(f"{Fore.RED}❌ Erro ao carregar configuração: {e}{Style.RESET_ALL}")
        return

    # Inicializar coletor
    collector = GLPIMetricsCollector(config)

    # Executar coleta completa
    metrics = collector.collect_all_metrics()

    # Salvar resultados
    if metrics["success"]:
        filename = save_metrics_to_file(metrics)
        success_msg = "🎉 Processo concluído! " f"Verifique o arquivo: {filename}"
        print(f"\n{Fore.GREEN}{success_msg}{Style.RESET_ALL}")
    else:
        error_msg = "⚠️  Processo finalizado com erros. " "Verifique os logs acima."
        print(f"\n{Fore.RED}{error_msg}{Style.RESET_ALL}")
        if metrics["errors"]:
            print(f"{Fore.RED}Erros encontrados: {Style.RESET_ALL}")
            for error in metrics["errors"]:
                print(f"{Fore.RED} - {error}{Style.RESET_ALL}")


if __name__ == "__main__":
    """
    Execução direta do script

    Configuração via variáveis de ambiente:

    export GLPI_BASE_URL="http://seu-glpi.com/glpi"
    export GLPI_APP_TOKEN="seu_app_token"
    export GLPI_USER_TOKEN="seu_user_token"
    # OU
    export GLPI_USERNAME="seu_usuario"
    export GLPI_PASSWORD="sua_senha"

    python glpi_metrics_collector.py
    """

    # Instalar dependências se necessário
    try:
        pass  # requests já importado no topo
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("💡 Instale as dependências com:")
        print("   pip install requests colorama")
        exit(1)

    main()
