"""Helper methods for GLPI Service to reduce function complexity.

This module contains auxiliary methods extracted from GLPIService
to improve code maintainability and reduce cyclomatic complexity.
"""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple, Union

if TYPE_CHECKING:
    from .glpi_service import GLPIService


class GLPIServiceHelpers:
    """Helper class containing auxiliary methods for GLPI operations."""

    def __init__(self, glpi_service: "GLPIService"):
        """Initialize with reference to main GLPI service.

        Args:
            glpi_service: Instance of GLPIService
        """
        self.glpi_service = glpi_service
        self.logger = glpi_service.logger

    def get_technician_ids_from_tickets(
        self, entity_id: Optional[int] = None, days_back: int = 90
    ) -> Set[str]:
        """Extract technician IDs from tickets assigned in recent days.

        Args:
            entity_id: Entity ID to filter tickets (optional)
            days_back: Number of days to look back for tickets (default: 90)

        Returns:
            Set of technician IDs found in tickets
        """
        print(f"DEBUG: get_technician_ids_from_tickets CHAMADO com entity_id={entity_id}")
        start_date = datetime.now() - timedelta(days=days_back)
        ticket_params = self._build_ticket_search_params(start_date, entity_id)

        print(
            f"DEBUG: GLPIServiceHelpers fazendo requisição para: {self.glpi_service.glpi_url}/search/Ticket"
        )
        print(f"DEBUG: Parâmetros: {ticket_params}")
        response = self.glpi_service._make_authenticated_request(
            "GET",
            f"{self.glpi_service.glpi_url}/search/Ticket",
            params=ticket_params,
        )
        print(f"DEBUG: Resposta recebida: {response}")
        print(f"DEBUG: Tipo da resposta: {type(response)}")

        if not response or not response.ok:
            self.logger.error(
                f"Failed to fetch tickets - Status: {response.status_code if response else 'None'}"
            )
            return set()

        ticket_result = response.json()
        ticket_data = ticket_result.get("data", [])

        return self._extract_technician_ids_from_response(ticket_data)

    def _build_ticket_search_params(
        self, start_date: datetime, entity_id: Optional[int]
    ) -> Dict[str, str]:
        """Build search parameters for ticket query.

        Args:
            start_date: Start date for ticket search
            entity_id: Entity ID filter (optional)

        Returns:
            Dictionary of search parameters
        """
        params = {
            "range": "0-5000",  # CORREÇÃO: Aumentado de 500 para 5000 para capturar mais tickets
            "criteria[0][field]": "15",  # date
            "criteria[0][searchtype]": "morethan",
            "criteria[0][value]": start_date.strftime("%Y-%m-%d"),
            "forcedisplay[0]": "2",  # id
            "forcedisplay[1]": "5",  # users_id_tech
            "forcedisplay[2]": "15",  # date
        }

        if entity_id is not None:
            params.update(
                {
                    "criteria[1][field]": "80",  # entities_id
                    "criteria[1][searchtype]": "equals",
                    "criteria[1][value]": str(entity_id),
                    "criteria[1][link]": "AND",
                }
            )

        return params

    def _extract_technician_ids_from_response(self, ticket_data: List[Dict]) -> Set[str]:
        """Extract unique technician IDs from ticket response data.

        Args:
            ticket_data: List of ticket data from API response

        Returns:
            Set of unique technician IDs
        """
        tech_ids_set = set()

        for ticket in ticket_data:
            if isinstance(ticket, dict) and "5" in ticket:
                tech_id = self.glpi_service._parse_technician_id(ticket["5"])
                if tech_id and tech_id != "0":
                    tech_ids_set.add(tech_id)

        return tech_ids_set

    def parse_technician_id(self, tech_field) -> Optional[str]:
        """Parse technician ID from various field formats.

        The users_id_tech field can come as string, list, or number.
        This method handles all these cases consistently.

        Args:
            tech_field: The technician field value from API response

        Returns:
            Parsed technician ID as string, or None if invalid
        """
        if not tech_field:
            return None

        # Handle list format - get first valid item
        if isinstance(tech_field, list):
            return self._parse_list_technician_id(tech_field)

        # Handle string format - may be JSON or simple string
        if isinstance(tech_field, str):
            return self._parse_string_technician_id(tech_field)

        # Handle numeric format
        if isinstance(tech_field, (int, float)):
            return self._parse_numeric_technician_id(tech_field)

        return None

    def _parse_list_technician_id(self, tech_list: List) -> Optional[str]:
        """Parse technician ID from list format."""
        for item in tech_list:
            if item and str(item) != "0":
                return str(item)
        return None

    def _parse_string_technician_id(self, tech_string: str) -> Optional[str]:
        """Parse technician ID from string format (JSON or simple)."""
        # Try parsing as JSON first
        try:
            import json

            parsed = json.loads(tech_string)

            if isinstance(parsed, list) and parsed:
                return self._parse_list_technician_id(parsed)
            elif parsed and str(parsed) != "0":
                return str(parsed)
        except (json.JSONDecodeError, ValueError, TypeError):
            # Not JSON, treat as simple string
            if tech_string and tech_string != "0":
                return str(tech_string)

        return None

    def _parse_numeric_technician_id(self, tech_number: Union[int, float]) -> Optional[str]:
        """Parse technician ID from numeric format."""
        if tech_number and tech_number != 0:
            return str(int(tech_number))
        return None

    def get_technicians_by_assignments(
        self, days_back: int = 30, min_tickets: int = 3
    ) -> Dict[str, Dict]:
        """Identifica técnicos baseado em atribuições de tickets recentes"""
        self.glpi_service.logger.info(
            f"Identificando técnicos por atribuições (últimos {days_back} dias, "
            f"mín. {min_tickets} tickets)"
        )

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        try:
            # Buscar tickets com atribuições no período
            tickets_data = self._fetch_tickets_with_assignments(start_date)
            if not tickets_data:
                return {}

            # Contar atribuições por técnico
            tech_counts = self._count_assignments_by_technician(tickets_data)

            # Filtrar e obter dados dos técnicos
            technicians = self._build_technicians_data(tech_counts, min_tickets)

            self.glpi_service.logger.info(
                f"Identificados {len(technicians)} técnicos por atribuições"
            )
            return technicians

        except Exception as e:
            self.glpi_service.logger.error(f"Erro ao identificar técnicos por atribuições: {e}")
            return {}

    def _fetch_tickets_with_assignments(self, start_date: datetime) -> Optional[Dict]:
        """Busca tickets com atribuições no período especificado"""
        response = self.glpi_service._make_authenticated_request(
            "GET",
            f"{self.glpi_service.glpi_url}/search/Ticket",
            params={
                "range": "0-5000",  # CORREÇÃO: Aumentado de 500 para 5000 para capturar mais tickets
                "criteria[0][field]": "15",  # date
                "criteria[0][searchtype]": "morethan",
                "criteria[0][value]": start_date.strftime("%Y-%m-%d"),
                "forcedisplay[0]": "2",  # id
                "forcedisplay[1]": "5",  # users_id_tech
                "forcedisplay[2]": "15",  # date
            },
        )

        if not response or not response.ok:
            self.glpi_service.logger.error("Falha ao buscar tickets com atribuições")
            return None

        data = response.json()
        if not data or not data.get("data"):
            self.glpi_service.logger.warning("Nenhum ticket encontrado no período")
            return None

        return data

    def _count_assignments_by_technician(self, tickets_data: Dict) -> Dict[str, int]:
        """Conta atribuições por técnico usando parsing corrigido"""
        tech_counts = {}
        parsing_stats = {"total": 0, "parsed": 0, "errors": 0}

        for ticket in tickets_data["data"]:
            parsing_stats["total"] += 1

            tech_field = ticket.get("5")
            tech_id = self.parse_technician_id(tech_field)

            if tech_id:
                tech_counts[tech_id] = tech_counts.get(tech_id, 0) + 1
                parsing_stats["parsed"] += 1
            else:
                parsing_stats["errors"] += 1

        self.glpi_service.logger.info(
            f"Estatísticas de parsing: {parsing_stats['parsed']}/{parsing_stats['total']} "
            "tickets parseados com sucesso"
        )

        return tech_counts

    def _build_technicians_data(
        self, tech_counts: Dict[str, int], min_tickets: int
    ) -> Dict[str, Dict]:
        """Constrói dados dos técnicos com base na contagem de tickets"""
        technicians = {}

        for tech_id, count in tech_counts.items():
            if count >= min_tickets:
                try:
                    user_response = self.glpi_service._make_authenticated_request(
                        "GET",
                        f"{self.glpi_service.glpi_url}/User/{tech_id}",
                    )

                    if user_response and user_response.ok:
                        user_data = user_response.json()

                        # Determinar nível do técnico baseado na contagem de tickets
                        level = self._determine_technician_level(count)

                        technicians[tech_id] = {
                            "name": user_data.get("name", f"Técnico {tech_id}"),
                            "username": user_data.get("name", ""),
                            "level": level,
                            "ticket_count": count,
                        }

                except Exception as e:
                    self.glpi_service.logger.warning(
                        f"Erro ao obter dados do técnico {tech_id}: {e}"
                    )

        return technicians

    def _determine_technician_level(self, ticket_count: int) -> str:
        """Determina o nível do técnico baseado na contagem de tickets"""
        if ticket_count >= 20:
            return "N4"
        elif ticket_count >= 15:
            return "N3"
        elif ticket_count >= 10:
            return "N2"
        else:
            return "N1"

    def fetch_all_pages_robust(
        self,
        search_params: Dict[str, str],
        tech_ids: List[str],
        tech_field_id: str,
    ) -> Dict[str, int]:
        """Implementa paginação robusta para buscar todos os dados incrementalmente

        Args:
            search_params: Parâmetros de busca base
            tech_ids: Lista de IDs dos técnicos
            tech_field_id: ID do campo de técnico

        Returns:
            Dict com contagem de tickets por técnico
        """
        try:
            ticket_counts = {tech_id: 0 for tech_id in tech_ids}
            page_size = 1000
            start_index = 0
            max_retries = 3
            total_processed = 0

            self.glpi_service.logger.info(
                f"Iniciando paginação robusta para {len(tech_ids)} técnicos"
            )

            while True:
                # Buscar página atual
                page_data, page_items = self._fetch_page_with_retry(
                    search_params, start_index, page_size, max_retries
                )

                if not page_data:
                    break

                # Processar dados da página
                page_counts = self._process_page_data(page_data, tech_ids, tech_field_id)

                # Atualizar contadores
                for tech_id, count in page_counts.items():
                    ticket_counts[tech_id] += count

                total_processed += page_items
                self.glpi_service.logger.debug(
                    f"Processados {page_items} tickets na página {start_index}-{start_index + page_size - 1}. "
                    f"Total: {total_processed}"
                )

                # Verificar se chegamos ao fim
                if page_items < page_size:
                    self.glpi_service.logger.info(
                        f"Última página processada. Total de tickets: {total_processed}"
                    )
                    break

                # Avançar para próxima página
                start_index += page_size

                # Limite de segurança
                if start_index > 100000:
                    self.glpi_service.logger.warning(
                        f"Limite de segurança atingido em {start_index} tickets. "
                        "Finalizando paginação."
                    )
                    break

            self.glpi_service.logger.info(
                f"Paginação robusta concluída: {sum(ticket_counts.values())} tickets "
                f"encontrados para {len(tech_ids)} técnicos"
            )
            return ticket_counts

        except Exception as e:
            self.glpi_service.logger.error(f"Erro na paginação robusta: {e}")
            return {tech_id: 0 for tech_id in tech_ids}

    def _fetch_page_with_retry(
        self,
        search_params: Dict[str, str],
        start_index: int,
        page_size: int,
        max_retries: int,
    ) -> Tuple[Optional[Dict], int]:
        """Busca uma página com retry e backoff exponencial"""
        import time

        end_index = start_index + page_size - 1
        current_params = search_params.copy()
        current_params["range"] = f"{start_index}-{end_index}"

        retry_count = 0

        while retry_count < max_retries:
            try:
                url = f"{self.glpi_service.glpi_url}/search/Ticket"
                response = self.glpi_service._make_authenticated_request(
                    "GET", url, params=current_params
                )

                if not response or not response.ok:
                    raise Exception(
                        f"Falha na requisição: "
                        f"{response.status_code if response else 'No response'}"
                    )

                page_data = response.json()

                # Log informações de paginação
                self._log_pagination_info(response, start_index, end_index)

                # Verificar se há dados
                if not page_data or "data" not in page_data or not page_data["data"]:
                    self.glpi_service.logger.info(
                        f"Página {start_index}-{end_index} vazia ou sem dados. "
                        "Finalizando paginação."
                    )
                    return None, 0

                return page_data, len(page_data["data"])

            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 2**retry_count  # Backoff exponencial
                    self.glpi_service.logger.warning(
                        f"Erro na página {start_index}-{end_index}, tentativa "
                        f"{retry_count}/{max_retries}: {e}. Aguardando {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    self.glpi_service.logger.error(
                        f"Falha após {max_retries} tentativas na página "
                        f"{start_index}-{end_index}: {e}"
                    )
                    raise

        return None, 0

    def _log_pagination_info(self, response: Any, start_index: int, end_index: int) -> None:
        """Log informações de paginação do cabeçalho Content-Range"""
        content_range = response.headers.get("Content-Range", "")
        if content_range:
            try:
                # Remove 'items ' prefix if present
                if content_range.startswith("items "):
                    content_range = content_range[6:]
                range_part, total_str = content_range.split("/")
                total_items = int(total_str)
                start_range, end_range = map(int, range_part.split("-"))

                self.glpi_service.logger.debug(
                    f"Página {start_index}-{end_index}: "
                    f"{end_range - start_range + 1} itens de {total_items} total"
                )
            except (ValueError, IndexError) as e:
                self.glpi_service.logger.warning(
                    f"Erro ao parsear Content-Range '{content_range}': {e}"
                )

    def _process_page_data(
        self,
        page_data: Dict[str, Any],
        tech_ids: List[str],
        tech_field_id: str,
    ) -> Dict[str, int]:
        """Processa dados de uma página e conta tickets por técnico"""
        page_counts = {tech_id: 0 for tech_id in tech_ids}

        for ticket in page_data["data"]:
            tech_id = str(ticket.get(tech_field_id, ""))
            if tech_id in page_counts:
                page_counts[tech_id] += 1

        return page_counts

    def get_technician_details_in_batches(
        self, tech_ids: Set[str], batch_size: int = 50
    ) -> Tuple[List[str], Dict[str, str]]:
        """Fetch technician details in batches to avoid API limits.

        Args:
            tech_ids: Set of technician IDs to fetch
            batch_size: Number of IDs to process per batch

        Returns:
            Tuple of (list of valid IDs, dict of ID->name mappings)
        """
        tech_ids_list = list(tech_ids)
        final_tech_ids = []
        final_tech_names = {}

        for i in range(0, len(tech_ids_list), batch_size):
            batch = tech_ids_list[i : i + batch_size]
            batch_ids, batch_names = self._process_technician_batch(batch)

            final_tech_ids.extend(batch_ids)
            final_tech_names.update(batch_names)

        return final_tech_ids, final_tech_names

    def _process_technician_batch(self, batch_ids: List[str]) -> Tuple[List[str], Dict[str, str]]:
        """Process a single batch of technician IDs.

        Args:
            batch_ids: List of technician IDs in this batch

        Returns:
            Tuple of (valid IDs, ID->name mappings) for this batch
        """
        user_params = self._build_user_search_params(batch_ids)

        response = self.glpi_service._make_authenticated_request(
            "GET",
            f"{self.glpi_service.glpi_url}/search/User",
            params=user_params,
        )

        if not response or not response.ok:
            self.logger.error(
                f"Failed to fetch user batch - Status: {response.status_code if response else 'None'}"
            )
            return [], {}

        user_result = response.json()
        user_data = user_result.get("data", [])

        return self._process_user_response(user_data)

    def _build_user_search_params(self, batch_ids: List[str]) -> Dict[str, str]:
        """Build search parameters for user batch query.

        Args:
            batch_ids: List of user IDs to search for

        Returns:
            Dictionary of search parameters
        """
        params = {
            "range": "0-5000",  # CORREÇÃO: Aumentado de 500 para 5000 para capturar mais usuários
            "forcedisplay[0]": "2",  # ID
            "forcedisplay[1]": "1",  # Username
            "forcedisplay[2]": "9",  # Firstname
            "forcedisplay[3]": "34",  # Realname
            "forcedisplay[4]": "8",  # is_active
            "forcedisplay[5]": "23",  # is_deleted
        }

        # Add OR criteria for each user ID
        for idx, user_id in enumerate(batch_ids):
            params[f"criteria[{idx}][field]"] = "2"  # ID field
            params[f"criteria[{idx}][searchtype]"] = "equals"
            params[f"criteria[{idx}][value]"] = str(user_id)
            if idx > 0:
                params[f"criteria[{idx}][link]"] = "OR"

        return params

    def _process_user_response(
        self, user_data: List[Dict[str, Any]]
    ) -> Tuple[List[str], Dict[str, str]]:
        """Process user response data to extract active technicians.

        Args:
            user_data: List of user data from API response

        Returns:
            Tuple of (valid IDs, ID->name mappings)
        """
        batch_ids = []
        batch_names = {}

        for user in user_data:
            if not isinstance(user, dict):
                continue

            user_info = self._extract_user_info(user)
            if not user_info:
                continue

            user_id, full_name, is_active = user_info

            if self._is_active_user(is_active, user.get("23")):
                batch_ids.append(user_id)
                batch_names[user_id] = full_name

        return batch_ids, batch_names

    def _extract_user_info(self, user: Dict[str, Any]) -> Optional[Tuple[str, str, str]]:
        """Extract user information from user data.

        Args:
            user: User data dictionary

        Returns:
            Tuple of (user_id, full_name, is_active) or None if invalid
        """
        user_id = user.get("2")
        if not user_id:
            return None

        firstname = user.get("9", "").strip()
        realname = user.get("34", "").strip()
        is_active = user.get("8", "0")

        # Build full name
        name_parts = [part for part in [firstname, realname] if part]
        full_name = " ".join(name_parts) if name_parts else f"User {user_id}"

        return str(user_id), full_name, str(is_active)

    def _is_active_user(self, is_active: str, is_deleted: Optional[str]) -> bool:
        """Check if user is active and not deleted.

        Args:
            is_active: User active status
            is_deleted: User deleted status

        Returns:
            True if user is active and not deleted
        """
        return is_active == "1" and (not is_deleted or is_deleted == "0")
