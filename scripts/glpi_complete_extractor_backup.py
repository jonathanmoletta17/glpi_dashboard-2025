#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLPI Complete Data Extractor - Versão Corrigida
Extrai dados completos do GLPI com formatação adequada para IA

Autor: Assistant
Data: 2025-01-06
Versão: 2.0
."""

import csv
import html
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


class GLPICompleteExtractor:
    """Extrator completo de dados GLPI com formatação para IA."""

    def __init__(self):
        self.setup_logging()
        self.load_config()
        self.session = requests.Session()
        self.session_token = None
        self.page_size = 1000
        self.max_retries = 3
        self.retry_delay = 2

        # Estatísticas
        self.stats = {
            "start_time": datetime.now(),
            "total_api_calls": 0,
            "tickets_extracted": 0,
            "users_extracted": 0,
            "technicians_filtered": 0,
            "requesters_filtered": 0,
        }

    def setup_logging(self):
        """Configura o sistema de logging."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("glpi_extractor.log", encoding="utf-8"),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def load_config(self):
        """Carrega configurações do ambiente."""
        self.glpi_url = os.getenv("GLPI_URL", "").rstrip("/")
        self.app_token = os.getenv("GLPI_APP_TOKEN", "")
        self.user_token = os.getenv("GLPI_USER_TOKEN", "")

        if not all([self.glpi_url, self.app_token, self.user_token]):
            raise ValueError("Configurações GLPI incompletas no arquivo .env")

        self.logger.info(f"Configuração carregada - URL: `{self.glpi_url}`")

    def authenticate(self) -> bool:
        """Autentica na API GLPI."""
        try:
            self.logger.info("Iniciando autenticação na API GLPI...")

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"user_token {self.user_token}",
                "App-Token": self.app_token,
            }

            response = self.session.get(f"{self.glpi_url}/initSession", headers=headers)
            response.raise_for_status()

            data = response.json()
            self.session_token = data.get("session_token")

            if self.session_token:
                self.logger.info("Autenticação realizada com sucesso")
                return True
            else:
                self.logger.error("Token de sessão não recebido")
                return False

        except Exception as e:
            self.logger.error(f"Erro na autenticação: {e}")
            return False

    def get_headers(self) -> Dict[str, str]:
        """Retorna headers para requisições autenticadas."""
        return {
            "Content-Type": "application/json",
            "Session-Token": self.session_token,
            "App-Token": self.app_token,
        }

    def clean_text(self, text: str) -> str:
        """Limpa e formata texto para IA."""
        if not isinstance(text, str):
            return str(text) if text is not None else ""

        # Decodificar HTML entities
        text = html.unescape(text)

        # Remover tags HTML
        text = re.sub(r"<[^>]+>", "", text)

        # Limpar caracteres especiais e quebras de linha
        text = re.sub(r"[\r\n\t]+", " ", text)
        text = re.sub(r"\s+", " ", text)

        # Remover caracteres de controle
        text = "".join(char for char in text if ord(char) >= 32 or char in "\n\t")

        return text.strip()

    def format_complex_field(self, value: Any) -> str:
        """Formata campos complexos para CSV."""
        if value is None:
            return ""

        if isinstance(value, (dict, list)):
            try:
                # Converter para JSON e limpar
                json_str = json.dumps(value, ensure_ascii=False)
                return self.clean_text(json_str)
            except:
                return str(value)

        return self.clean_text(str(value))

    def make_api_request(
        self, endpoint: str, params: Optional[Dict] = None
    ) -> Optional[List[Dict]]:
        """Faz requisição à API com retry automático."""
        url = f"{self.glpi_url}/{endpoint}"
        headers = self.get_headers()

        for attempt in range(self.max_retries):
            try:
                self.stats["total_api_calls"] += 1
                response = self.session.get(url, headers=headers, params=params, timeout=60)
                response.raise_for_status()

                data = response.json()

                # Verificar se é uma lista ou um único item
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return [data]
                else:
                    self.logger.warning(f"Formato de resposta inesperado: {type(data)}")
                    return []

            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Tentativa {attempt + 1} falhou para {endpoint}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2**attempt))
                else:
                    self.logger.error(f"Falha após {self.max_retries} tentativas para {endpoint}")
                    return None
            except Exception as e:
                self.logger.error(f"Erro inesperado em {endpoint}: {e}")
                return None

        return None

    def extract_with_pagination(self, endpoint: str, description: str) -> List[Dict]:
        """Extrai dados com paginação automática."""
        all_data = []
        start = 0

        self.logger.info(f"Iniciando extração de {description}...")

        while True:
            params = {
                "range": f"{start}-{start + self.page_size - 1}",
                "expand_dropdowns": "true",
                "get_hateoas": "false",
                "with_devices": "true",
                "with_disks": "true",
                "with_softwares": "true",
                "with_connections": "true",
                "with_networkports": "true",
            }

            self.logger.info(
                f"Extraindo {description} - registros {start} a {start + self.page_size - 1}"
            )

            data = self.make_api_request(endpoint, params)

            if not data:
                self.logger.warning(
                    f"Nenhum dado retornado para {description} no range {start}-{start + self.page_size - 1}"
                )
                break

            all_data.extend(data)

            # Se retornou menos que o tamanho da página, chegamos ao fim
            if len(data) < self.page_size:
                break

            start += self.page_size

            # Pequena pausa para não sobrecarregar a API
            time.sleep(0.1)

        self.logger.info(f"Extração de {description} concluída: {len(all_data)} registros")
        return all_data

    def extract_all_tickets(self) -> List[Dict]:
        """Extrai todos os tickets com todos os campos."""
        tickets = self.extract_with_pagination("Ticket", "tickets")

        # Limpar e formatar dados dos tickets
        cleaned_tickets = []
        for ticket in tickets:
            cleaned_ticket = {}
            for key, value in ticket.items():
                if key in ["content", "name", "comment"]:
                    cleaned_ticket[key] = self.clean_text(value)
                else:
                    cleaned_ticket[key] = self.format_complex_field(value)
            cleaned_tickets.append(cleaned_ticket)

        self.stats["tickets_extracted"] = len(cleaned_tickets)
        return cleaned_tickets

    def extract_all_users(self) -> List[Dict]:
        """Extrai todos os usuários."""
        users = self.extract_with_pagination("User", "usuários")

        # Limpar e formatar dados dos usuários
        cleaned_users = []
        for user in users:
            cleaned_user = {}
            for key, value in user.items():
                # Aplicar limpeza de texto nos campos relevantes para análise
                if key in [
                    "comment",
                    "firstname",
                    "realname",
                    "name",
                    "nickname",
                    "user_dn",
                    "registration_number",
                    "phone",
                    "phone2",
                    "mobile",
                ]:
                    cleaned_user[key] = self.clean_text(value)
                else:
                    cleaned_user[key] = self.format_complex_field(value)
            cleaned_users.append(cleaned_user)

        self.stats["users_extracted"] = len(cleaned_users)
        return cleaned_users

    def extract_user_profiles(self, user_id: str) -> List[Dict]:
        """Extrai perfis de um usuário específico."""
        try:
            profiles = self.make_api_request(f"User/{user_id}/Profile_User")
            return profiles if profiles else []
        except:
            return []

    def filter_technicians(self, users: List[Dict]) -> List[Dict]:
        """Filtra usuários que são técnicos baseado em critérios rigorosos."""
        technicians = []

        # Critérios mais específicos para identificar técnicos reais
        tech_comment_keywords = [
            "cc-se-subadm-dtic",
            "dtic",
            "tecnico de informatica",
            "helpdesk",
            "suporte tecnico",
            "administrador de sistema",
            "analista de sistemas",
        ]

        # Entidades específicas de TI
        tech_entities = ["dtic", "informatica", "tecnologia da informacao"]

        for user in users:
            is_technician = False

            # Verificar se está ativo
            if user.get("is_active") != "1":
                continue

            try:
                # Critério 1: Verificar comentários específicos
                comment = str(user.get("comment", "")).lower()
                if any(keyword in comment for keyword in tech_comment_keywords):
                    is_technician = True

                # Critério 2: Verificar entidade específica
                entities_id = str(user.get("entities_id", "")).lower()
                if any(entity in entities_id for entity in tech_entities):
                    is_technician = True

                # Critério 3: Verificar se tem perfil de super-admin (ID 2)
                if str(user.get("profiles_id", "")) == "2":
                    is_technician = True

                # Critério 4: Verificar grupos específicos
                groups_id = str(user.get("groups_id", "")).lower()
                if "dtic" in groups_id or "ti" in groups_id:
                    is_technician = True

                if is_technician:
                    # Aplicar limpeza de texto nos campos relevantes
                    cleaned_tech = {}
                    for key, value in user.items():
                        try:
                            if key in [
                                "comment",
                                "firstname",
                                "realname",
                                "name",
                                "nickname",
                                "user_dn",
                                "registration_number",
                                "phone",
                                "phone2",
                                "mobile",
                            ]:
                                cleaned_tech[key] = self.clean_text(value)
                            else:
                                cleaned_tech[key] = self.format_complex_field(value)
                        except Exception as e:
                            # Em caso de erro na limpeza, manter valor original
                            cleaned_tech[key] = str(value) if value is not None else ""

                    technicians.append(cleaned_tech)

            except Exception as e:
                self.logger.warning(f"Erro ao processar usuário {user.get('id', 'N/A')}: {str(e)}")
                continue

        self.stats["technicians_filtered"] = len(technicians)
        self.logger.info(f"Identificados {len(technicians)} técnicos")
        return technicians

    def filter_requesters(self, users: List[Dict]) -> List[Dict]:
        """Filtra usuários que são solicitantes (usuários finais)."""
        requesters = []

        for user in users:
            # Verificar se está ativo
            if user.get("is_active") != "1":
                continue

            is_requester = False
            user_id = user.get("id")

            # Verificar se tem email válido (indicativo de usuário final)
            name = str(user.get("name", ""))
            if "@" in name and "." in name:
                is_requester = True

            # Verificar entidades que indicam usuários finais
            entities_id = str(user.get("entities_id", "")).lower()
            requester_entities = [
                "secretaria",
                "gabinete",
                "departamento",
                "divisao",
                "setor",
                "coordenacao",
                "assessoria",
                "diretoria",
                "gerencia",
            ]
            if any(entity in entities_id for entity in requester_entities):
                is_requester = True

            # Verificar se NÃO é técnico baseado em indicadores
            tech_indicators = ["dtic", "ti", "suporte", "admin", "tecnico", "informatica"]
            comment = str(user.get("comment", "")).lower()

            # Se tem indicadores técnicos, não é solicitante
            if any(indicator in comment for indicator in tech_indicators):
                is_requester = False
            if any(indicator in entities_id for indicator in tech_indicators):
                is_requester = False

            # Verificar perfis se disponível
            if user_id and is_requester:
                try:
                    profiles = self.extract_user_profiles(user_id)
                    if profiles:
                        # Se tem perfis administrativos, não é solicitante comum
                        admin_profiles = ["super-admin", "admin", "technician"]
                        for profile in profiles:
                            profile_name = str(profile.get("name", "")).lower()
                            if any(admin_prof in profile_name for admin_prof in admin_profiles):
                                is_requester = False
                                break
                except Exception:
                    # Se não conseguir verificar perfis, manter como solicitante se passou nos outros testes
                    pass

            # Adicionar critério adicional: usuários com firstname e realname preenchidos
            firstname = str(user.get("firstname", "")).strip()
            realname = str(user.get("realname", "")).strip()
            if firstname and realname and len(firstname) > 1 and len(realname) > 1:
                if not any(indicator in comment for indicator in tech_indicators):
                    is_requester = True

            if is_requester:
                # Aplicar limpeza de texto nos campos relevantes
                cleaned_req = {}
                for key, value in user.items():
                    if key in [
                        "comment",
                        "firstname",
                        "realname",
                        "name",
                        "nickname",
                        "user_dn",
                        "registration_number",
                        "phone",
                        "phone2",
                        "mobile",
                    ]:
                        cleaned_req[key] = self.clean_text(value)
                    else:
                        cleaned_req[key] = self.format_complex_field(value)
                requesters.append(cleaned_req)

        self.stats["requesters_filtered"] = len(requesters)
        self.logger.info(f"Identificados {len(requesters)} solicitantes")
        return requesters

    def save_to_csv(self, data: List[Dict], filename: str, description: str):
        """Salva dados em arquivo CSV formatado para IA."""
        if not data:
            self.logger.warning(f"Nenhum dado para salvar em {filename}")
            return

        try:
            # Obter todas as chaves únicas
            all_keys = set()
            for item in data:
                all_keys.update(item.keys())

            # Ordenar chaves para consistência
            fieldnames = sorted(list(all_keys))

            with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
                writer.writeheader()

                for item in data:
                    # Garantir que todos os campos estão presentes
                    row = {}
                    for field in fieldnames:
                        value = item.get(field, "")
                        row[field] = self.format_complex_field(value)

                    writer.writerow(row)

            self.logger.info(f"{description} salvos em {filename}: {len(data)} registros")

        except Exception as e:
            self.logger.error(f"Erro ao salvar {filename}: {e}")

    def cleanup(self):
        """Limpa recursos e encerra sessão."""
        try:
            if self.session_token:
                headers = self.get_headers()
                self.session.get(f"{self.glpi_url}/killSession", headers=headers)
                self.logger.info("Sessão GLPI encerrada")
        except Exception as e:
            self.logger.warning(f"Erro ao encerrar sessão: {e}")
        finally:
            self.session.close()

    def print_statistics(self):
        """Imprime estatísticas da extração."""
        end_time = datetime.now()
        duration = end_time - self.stats["start_time"]

        print("\n" + "=" * 60)
        print("ESTATÍSTICAS DA EXTRAÇÃO GLPI")
        print("=" * 60)
        print(f"Início: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Fim: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duração: {duration}")
        print(f"Total de chamadas à API: {self.stats['total_api_calls']}")
        print("\nDADOS EXTRAÍDOS:")
        print(f"  • Tickets: {self.stats['tickets_extracted']}")
        print(f"  • Usuários: {self.stats['users_extracted']}")
        print(f"  • Técnicos: {self.stats['technicians_filtered']}")
        print(f"  • Solicitantes: {self.stats['requesters_filtered']}")
        print("\nARQUIVOS GERADOS:")
        print("  • tickets.csv")
        print("  • usuarios.csv")
        print("  • tecnicos.csv")
        print("  • solicitantes.csv")
        print("=" * 60)

    def run(self):
        """Executa a extração completa."""
        try:
            self.logger.info("Iniciando extração completa de dados GLPI")

            # Autenticar
            if not self.authenticate():
                raise Exception("Falha na autenticação")

            # Extrair todos os tickets
            self.logger.info("Extraindo todos os tickets...")
            tickets = self.extract_all_tickets()
            self.save_to_csv(tickets, "tickets.csv", "Tickets")

            # Extrair todos os usuários
            self.logger.info("Extraindo todos os usuários...")
            users = self.extract_all_users()
            self.save_to_csv(users, "usuarios.csv", "Usuários")

            # Filtrar e salvar técnicos
            self.logger.info("Filtrando técnicos...")
            technicians = self.filter_technicians(users)
            self.save_to_csv(technicians, "tecnicos.csv", "Técnicos")

            # Filtrar e salvar solicitantes
            self.logger.info("Filtrando solicitantes...")
            requesters = self.filter_requesters(users)
            self.save_to_csv(requesters, "solicitantes.csv", "Solicitantes")

            self.logger.info("Extração completa finalizada com sucesso!")
            self.print_statistics()

        except Exception as e:
            self.logger.error(f"Erro durante a extração: {e}")
            raise
        finally:
            self.cleanup()


def main():
    """Função principal."""
    try:
        extractor = GLPICompleteExtractor()
        extractor.run()
        print("\n✅ Extração concluída com sucesso!")
        print("📁 Verifique os arquivos CSV gerados no diretório atual.")
        print("🤖 Dados formatados e limpos para treinamento de IA.")

    except Exception as e:
        print(f"\n❌ Erro na extração: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
