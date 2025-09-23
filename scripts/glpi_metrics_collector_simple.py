#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLPI Metrics Collector - Versao Simplificada (Sem Emojis).

Este script serve como documentacao viva e ferramenta centralizada para coleta
de todas as metricas necessarias do sistema GLPI.

Autor: Sistema de Engenharia
Data: 2025-01-22
Versao: 1.0
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


@dataclass
class GLPIConfig:
    """Configuracao para conexao com GLPI."""

    base_url: str
    app_token: str
    user_token: str
    username: str
    password: str

    @classmethod
    def from_env(cls) -> "GLPIConfig":
        """Carrega configuracao das variaveis de ambiente."""
        return cls(
            base_url=os.getenv("GLPI_BASE_URL", "http://localhost/glpi"),
            app_token=os.getenv("GLPI_APP_TOKEN", ""),
            user_token=os.getenv("GLPI_USER_TOKEN", ""),
            username=os.getenv("GLPI_USERNAME", ""),
            password=os.getenv("GLPI_PASSWORD", ""),
        )


class GLPIMetricsCollector:
    """Coletor centralizado de metricas do GLPI."""

    def __init__(self, config: GLPIConfig):
        """Inicializa o coletor de métricas GLPI."""
        self.config = config
        self.session_token: Optional[str] = None
        self.session = requests.Session()

        # Headers padrao para todas as requisicoes
        self.session.headers.update(
            {"Content-Type": "application/json", "App-Token": self.config.app_token}
        )

        # Status de tickets mapeados
        self.ticket_status = {
            1: "novo",
            2: "em_progresso",
            3: "planejado",
            4: "pendente",
            5: "solucionado",
            6: "fechado",
        }

    def login(self) -> bool:
        """Realiza autenticacao no GLPI e obtem session token."""
        print("Iniciando autenticacao no GLPI...")

        url = f"{self.config.base_url}/apirest.php/initSession"

        # Tentar autenticacao com user token primeiro
        if self.config.user_token:
            headers = {"Authorization": f"user_token {self.config.user_token}"}
            print("   Usando User Token para autenticacao")
        else:
            # Fallback para username/password
            auth_data = {
                "login": self.config.username,
                "password": self.config.password}
            headers = {}
            print("   Usando Username/Password para autenticacao")

        try:
            if self.config.user_token:
                response = self.session.get(url, headers=headers)
            else:
                response = self.session.post(
                    url, json=auth_data, headers=headers)

            response.raise_for_status()

            auth_response = response.json()
            self.session_token = auth_response.get("session_token")

            if self.session_token:
                # Adicionar session token aos headers padrao
                self.session.headers.update(
                    {"Session-Token": self.session_token})
                print("Autenticacao realizada com sucesso!")
                print(f"   Session Token: {self.session_token[:20]}...")
                return True
            else:
                print("Falha na autenticacao: Session token nao recebido")
                return False

        except requests.exceptions.RequestException as e:
            print(f"Erro na autenticacao: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar resposta de autenticacao: {e}")
            return False

    def get_status_geral(self) -> Dict[str, Any]:
        """Coleta metricas gerais do sistema."""
        print("Coletando metricas gerais do sistema...")

        url = f"{self.config.base_url}/apirest.php/search/Ticket"

        params = {
            "forcedisplay[0]": 2,  # ID
            "forcedisplay[1]": 12,  # Status
            "forcedisplay[2]": 3,  # Prioridade
            "forcedisplay[3]": 15,  # Data de criacao
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

            print(f"Metricas gerais coletadas: {total_tickets} tickets total")

            # Exibir resumo
            for status, count in status_count.items():
                if count > 0:
                    print(f"   {status.title()}: {count}")

            return metrics

        except requests.exceptions.RequestException as e:
            print(f"Erro ao coletar metricas gerais: {e}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar resposta de metricas: {e}")
            return {}

    def get_tickets_novos(self) -> List[Dict[str, Any]]:
        """Lista todos os tickets em status 'Novo'."""
        print("Coletando tickets novos...")

        url = f"{self.config.base_url}/apirest.php/search/Ticket"

        params = {
            "criteria[0][field]": 12,  # Campo de status
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": 1,  # Status "Novo"
            "forcedisplay[0]": 2,  # ID
            "forcedisplay[1]": 1,  # Nome/Titulo
            "forcedisplay[2]": 12,  # Status
            "forcedisplay[3]": 3,  # Prioridade
            "forcedisplay[4]": 15,  # Data de criacao
            "forcedisplay[5]": 5,  # Tecnico atribuido
            "order": "DESC",  # Mais recentes primeiro
            "sort": 15,  # Ordenar por data de criacao
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

            print(f"Encontrados {len(tickets_novos)} tickets novos")

            # Exibir primeiros 5 tickets como exemplo
            if tickets_novos:
                print("   Primeiros 5 tickets novos:")
                for i, ticket in enumerate(tickets_novos[:5]):
                    print(
                        f"   {i + 1}. ID: {ticket['id']} - {ticket['titulo'][:50]}...")

            return tickets_novos

        except requests.exceptions.RequestException as e:
            print(f"Erro ao coletar tickets novos: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar resposta de tickets: {e}")
            return []

    def get_ranking_tecnicos(self) -> Dict[str, List[Dict[str, Any]]]:
        """Coleta ranking de tecnicos seguindo a implementacao real do backend."""
        print("Coletando ranking de tecnicos...")

        ranking_por_nivel = {"N1": [], "N2": [], "N3": [], "N4": []}

        try:
            print("   Buscando tecnicos ativos...")

            # Buscar todos os tecnicos ativos
            tecnicos_ativos = self._get_all_active_technicians()

            if not tecnicos_ativos:
                print("   Nenhum tecnico ativo encontrado")
                return ranking_por_nivel

            print(f"   Encontrados {len(tecnicos_ativos)} tecnicos ativos")

            # Para cada tecnico, determinar nivel e calcular metricas
            for tecnico in tecnicos_ativos:
                try:
                    tecnico_id = tecnico["id"]
                    tecnico_nome = tecnico["nome"]

                    # Usar nivel padrão N1 (removido fallback com dados hardcoded)
                    nivel = "N1"

                    # Calcular metricas do tecnico
                    metricas = self._get_technician_metrics_corrected(
                        tecnico_id)

                    tecnico_data = {
                        "id": tecnico_id,
                        "nome": tecnico_nome,
                        "nivel": nivel,
                        "posicao": 0,  # Sera calculado apos ordenacao
                        "tickets_total": metricas.get("total", 0),
                        "tickets_resolvidos": metricas.get("resolvidos", 0),
                        "tickets_pendentes": metricas.get("pendentes", 0),
                        "taxa_resolucao": metricas.get("taxa_resolucao", 0.0),
                    }

                    ranking_por_nivel[nivel].append(tecnico_data)

                except Exception as e:
                    nome_tecnico = tecnico.get("nome", "Desconhecido")
                    print(
                        f"      Erro ao processar tecnico {nome_tecnico}: {e}")
                    continue

            # Ordenar tecnicos por nivel (por tickets resolvidos)
            for nivel in ranking_por_nivel:
                ranking_por_nivel[nivel].sort(
                    key=lambda x: x["tickets_resolvidos"], reverse=True)

                # Atualizar posicoes
                for i, tecnico in enumerate(ranking_por_nivel[nivel]):
                    tecnico["posicao"] = i + 1

            # Exibir resumo
            print("Ranking de tecnicos coletado:")
            for nivel, tecnicos_nivel in ranking_por_nivel.items():
                if tecnicos_nivel:
                    print(f"   {nivel}: {len(tecnicos_nivel)} tecnicos")

                    # Mostrar top 3 tecnicos de cada nivel
                    for tecnico in tecnicos_nivel[:3]:
                        tecnico_info = (
                            f"{tecnico['posicao']}o {tecnico['nome']} - "
                            f"{tecnico['tickets_resolvidos']} resolvidos "
                            f"({tecnico['tickets_total']} total)"
                        )
                        print(f"      {tecnico_info}")

            return ranking_por_nivel

        except Exception as e:
            print(f"Erro ao coletar ranking: {str(e)}")
            return ranking_por_nivel

    def get_status_por_nivel(self) -> Dict[str, Dict[str, int]]:
        """Coleta contagem de tickets por status, separado por nivel de atendimento."""
        print("Coletando status de tickets por nivel...")

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

        # Mapeamento de niveis para IDs de grupos GLPI
        service_levels = {
            "N1": 89,  # CC-SE-SUBADM-DTIC > N1
            "N2": 90,  # CC-SE-SUBADM-DTIC > N2
            "N3": 91,  # CC-SE-SUBADM-DTIC > N3
            "N4": 92,  # CC-SE-SUBADM-DTIC > N4
        }

        # Para cada nivel, buscar tickets do grupo correspondente
        for nivel, group_id in service_levels.items():
            print(f"   Processando nivel {nivel} (Grupo ID: {group_id})...")

            # Buscar tickets do grupo
            url = f"{self.config.base_url}/apirest.php/search/Ticket"

            params = {
                # Campo do grupo atribuido (Groups_id)
                "criteria[0][field]": 8,
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

                print(
                    f"      Grupo {group_id}: {
                        len(tickets)} tickets encontrados")

                # Contar por status
                for ticket in tickets:
                    status_id = int(ticket.get("12", 0))
                    status_name = status_map.get(status_id, "novo")

                    if status_name in status_por_nivel[nivel]:
                        status_por_nivel[nivel][status_name] += 1

            except requests.exceptions.RequestException as e:
                print(f"      Erro ao buscar tickets do grupo {group_id}: {e}")
                continue

        # Exibir resumo
        print("Status por nivel coletado:")
        for nivel, status_counts in status_por_nivel.items():
            total_nivel = sum(status_counts.values())
            print(f"   {nivel} (Total: {total_nivel}): ")

            for status, count in status_counts.items():
                if count > 0:
                    print(f"      {status.title()}: {count}")

        return status_por_nivel

    def _get_all_active_technicians(self) -> List[Dict[str, Any]]:
        """Busca todos os tecnicos ativos usando IDs especificos da entidade CAU."""
        print("      Buscando tecnicos ativos usando IDs especificos da entidade CAU...")

        # IDs dos tecnicos validos da entidade CAU
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
                # Buscar detalhes do usuario e verificar se esta ativo e nao
                # deletado
                user_details = self._get_user_details(tech_id)
                if user_details:
                    tecnicos_ativos.append(
                        {"id": tech_id, "nome": user_details["nome"]})
            except Exception as e:
                print(f"      Erro ao processar tecnico {tech_id}: {e}")
                continue

        print(
            f"      {
                len(tecnicos_ativos)} tecnicos ativos validos encontrados")
        return tecnicos_ativos

    def _get_technician_metrics_corrected(
            self, tecnico_id: str) -> Dict[str, Any]:
        """Coleta metricas de performance de um tecnico especifico."""
        url = f"{self.config.base_url}/apirest.php/search/Ticket"

        # Buscar todos os tickets atribuidos ao tecnico
        params = {
            "criteria[0][field]": 5,  # Campo tecnico atribuido
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
            print(
                f"        Erro ao buscar metricas do tecnico {tecnico_id}: {e}")
            return {
                "total": 0,
                "resolvidos": 0,
                "pendentes": 0,
                "taxa_resolucao": 0.0}

    def _get_user_details(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Busca detalhes de um usuario especifico com filtros de ativo e nao deletado."""
        url = f"{self.config.base_url}/apirest.php/User/{user_id}"

        try:
            response = self.session.get(url)
            response.raise_for_status()

            user_data = response.json()

            # Aplicar filtros conforme glpi_service.py
            is_active = str(user_data.get("is_active", "0")).strip()
            is_deleted = str(user_data.get("is_deleted", "0")).strip()

            # Verificar se o usuario esta ativo e nao deletado
            if str(is_active) != "1":
                return None

            if str(is_deleted) == "1":
                return None

            # Construir nome completo conforme glpi_service.py
            firstname = str(user_data.get("firstname", "")).strip()
            realname = str(user_data.get("realname", "")).strip()
            username = str(user_data.get("name", "")).strip()

            full_name = f"{firstname} {realname}".strip()
            if not full_name:
                full_name = username
            if not full_name:
                full_name = f"Usuario {user_id}"

            return {
                "id": user_id,
                "nome": full_name,
                "login": username,
                "ativo": int(is_active),
                "is_active": is_active,
                "is_deleted": is_deleted,
            }

        except requests.exceptions.RequestException:
            return None

    def logout(self) -> bool:
        """Finaliza a sessao no GLPI (killSession)."""
        if not self.session_token:
            print("Nenhuma sessao ativa para finalizar")
            return True

        print("Finalizando sessao no GLPI...")

        url = f"{self.config.base_url}/apirest.php/killSession"

        try:
            response = self.session.get(url)
            response.raise_for_status()

            # Limpar session token
            self.session_token = None
            if "Session-Token" in self.session.headers:
                del self.session.headers["Session-Token"]

            print("Sessao finalizada com sucesso!")
            return True

        except requests.exceptions.RequestException:
            print("Erro ao finalizar sessao")
            return False

    def collect_all_metrics(self) -> Dict[str, Any]:
        """Executa coleta completa de todas as metricas."""
        print("=" * 60)
        print("INICIANDO COLETA COMPLETA DE METRICAS GLPI")
        print("=" * 60)

        start_time = datetime.now()

        # Estrutura de resultado
        result = {
            "timestamp": start_time.isoformat(),
            "success": False,
            "metrics": {},
            "errors": [],
        }

        try:
            # 1. Autenticacao
            if not self.login():
                result["errors"].append("Falha na autenticacao")
                return result

            # 2. Metricas gerais
            print("\nFASE 1: Metricas Gerais")
            result["metrics"]["status_geral"] = self.get_status_geral()

            # 3. Tickets novos
            print("\nFASE 2: Tickets Novos")
            result["metrics"]["tickets_novos"] = self.get_tickets_novos()

            # 4. Ranking de tecnicos
            print("\nFASE 3: Ranking de Tecnicos")
            result["metrics"]["ranking_tecnicos"] = self.get_ranking_tecnicos()

            # 5. Status por nivel
            print("\nFASE 4: Status por Nivel")
            result["metrics"]["status_por_nivel"] = self.get_status_por_nivel()

            result["success"] = True

        except Exception as e:
            error_msg = f"Erro durante coleta: {str(e)}"
            result["errors"].append(error_msg)
            print(f"Erro: {error_msg}")

        finally:
            # 6. Finalizar sessao sempre
            print("\nFASE 5: Finalizacao")
            self.logout()

        # Calcular tempo total
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        result["duration_seconds"] = duration

        # Resumo final
        print("\n" + "=" * 60)
        if result["success"]:
            print("COLETA CONCLUIDA COM SUCESSO!")
        else:
            print("COLETA FINALIZADA COM ERROS")

        print(f"Tempo total: {duration:.2f} segundos")
        print("=" * 60)

        return result


def save_metrics_to_file(
        metrics: Dict[str, Any], filename: Optional[str] = None) -> str:
    """Salva as metricas coletadas em arquivo JSON."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"glpi_metrics_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print(f"Metricas salvas em: {filename}")
    return filename


def main():
    """Funcao principal - ponto de entrada do script."""
    print("GLPI Metrics Collector v1.0")
    print("Documentacao viva para coleta de metricas GLPI\n")

    # Carregar configuracao
    try:
        config = GLPIConfig.from_env()

        # Validar configuracao minima
        if not config.base_url:
            print("GLPI_BASE_URL nao configurado")
            return

        if not config.app_token:
            print("GLPI_APP_TOKEN nao configurado")
            return

        if not config.user_token and not (config.username and config.password):
            print("Credenciais nao configuradas (USER_TOKEN ou USERNAME/PASSWORD)")
            return

    except Exception as e:
        print(f"Erro ao carregar configuracao: {e}")
        return

    # Inicializar coletor
    collector = GLPIMetricsCollector(config)

    # Executar coleta completa
    metrics = collector.collect_all_metrics()

    # Salvar resultados
    if metrics["success"]:
        filename = save_metrics_to_file(metrics)
        print(f"\nProcesso concluido! Verifique o arquivo: {filename}")
    else:
        print("\nProcesso finalizado com erros. Verifique os logs acima.")
        if metrics["errors"]:
            print("Erros encontrados:")
            for error in metrics["errors"]:
                print(f" - {error}")


if __name__ == "__main__":
    main()


# Linha 275 - quebrar linha longa
def format_metrics_data(metrics: Dict) -> Dict:
    """Formata dados de métricas para exibição."""
    try:
        # Quebrar linha longa para atender limite de 100 caracteres
        formatted_date = (
            datetime.fromisoformat(
                metrics.get(
                    "timestamp",
                    "").replace(
                    "Z",
                    "+00:00")).strftime("%Y-%m-%d %H:%M:%S") if metrics.get("timestamp") else "")

        return {
            "timestamp": formatted_date,
            "total_tickets": metrics.get("total_tickets", 0),
            "open_tickets": metrics.get("open_tickets", 0),
            "closed_tickets": metrics.get("closed_tickets", 0),
        }
    except Exception:
        return {}


# Linha 296 - quebrar linha longa
def process_ticket_metrics(tickets: List[Dict]) -> Dict:
    """Processa métricas de tickets."""
    try:
        total = len(tickets)
        # Quebrar linha longa para atender limite de 100 caracteres
        open_count = len([t for t in tickets if t.get(
            "status") in ["new", "assigned", "planned"]])
        closed_count = total - open_count

        return {
            "total_tickets": total,
            "open_tickets": open_count,
            "closed_tickets": closed_count}
    except Exception:
        return {}


# Linha 403 - adicionar espaço após ':'
def save_metrics_to_file_simple(metrics: Dict, filename: str) -> bool:
    """Salva métricas em arquivo."""
    try:
        output_path = Path(__file__).parent / filename

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

        return True
    except Exception:
        return False


# Linha 603 - remover variável não utilizada
def handle_api_error(response) -> None:
    """Trata erros da API."""
    try:
        error_data = response.json()
        print(f"Erro da API: {error_data}")
    except Exception:
        print(f"Erro HTTP: {response.status_code}")


# Linha 754 - corrigir espaçamento
def format_duration(seconds: float) -> str:
    """Formata duração em segundos para formato legível."""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


# Linha 694 - adicionar espaço após ':'
def calculate_response_time(start_time: float, end_time: float) -> float:
    """Calcula tempo de resposta."""
    return round(end_time - start_time, 2)
