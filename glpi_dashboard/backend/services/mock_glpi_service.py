#!/usr/bin/env python3
"""
Serviço GLPI Mock para desenvolvimento quando o servidor GLPI não está disponível
"""
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from utils.response_formatter import ResponseFormatter


class MockGLPIService:
    """Serviço mock que simula as respostas do GLPI para desenvolvimento"""

    def __init__(self):
        self.session_token = "mock_session_token"
        self.authenticated = True

    def _ensure_authenticated(self) -> bool:
        """Mock de autenticação - sempre retorna True"""
        return True

    def get_system_status(self) -> Dict[str, Any]:
        """Mock do status do sistema"""
        return {"status": "online", "version": "10.0.0", "response_time": 150}

    def get_ticket_by_id(self, ticket_id: str) -> Dict[str, Any]:
        """Mock para obter detalhes de um ticket específico"""
        # Simula dados de um ticket específico
        return {
            "id": int(ticket_id),
            "name": f"Ticket Mock {ticket_id}",
            "content": f"Descrição detalhada do ticket {ticket_id} - " f"Problema simulado para demonstração",
            "status": random.choice([1, 2, 3, 4, 5]),
            "priority": random.choice([1, 2, 3, 4]),
            "date": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
            "solvedate": (datetime.now() - timedelta(days=random.randint(0, 5))).isoformat()
            if random.choice([True, False])
            else None,
            "itilcategories_id": random.randint(1, 10),
            "category_name": f"Categoria {random.randint(1, 10)}",
            "users_id_requester": random.randint(100, 999),
            "requester_name": f"Usuário {random.randint(1, 100)}",
            "users_id_assign": random.randint(200, 299),
            "technician_name": f"Técnico {random.randint(1, 20)}",
            "entities_id": 1,
            "entity_name": "Entidade Principal",
        }

    def get_dashboard_metrics(self, correlation_id: str = None) -> Dict[str, Any]:
        """Mock das métricas do dashboard"""
        mock_data = {
            "total_tickets": 1250,
            "open_tickets": 85,
            "closed_tickets": 1165,
            "pending_tickets": 42,
            "avg_resolution_time": 2.5,
            "tickets_by_priority": {
                "1": 15,  # Muito alta
                "2": 25,  # Alta
                "3": 35,  # Média
                "4": 10,  # Baixa
            },
            "tickets_by_status": {
                "1": 85,  # Novo
                "2": 42,  # Em andamento
                "3": 15,  # Pendente
                "4": 1165,  # Resolvido
            },
        }
        return ResponseFormatter.format_success_response(
            data=mock_data, message="Métricas obtidas com sucesso", correlation_id=correlation_id
        )

    def get_dashboard_metrics_with_date_filter(self, start_date=None, end_date=None, correlation_id=None) -> Dict[str, Any]:
        """Mock das métricas do dashboard com filtro de data"""
        return self.get_dashboard_metrics(correlation_id=correlation_id)

    def get_dashboard_metrics_with_modification_date_filter(
        self, start_date=None, end_date=None, correlation_id=None
    ) -> Dict[str, Any]:
        """Mock das métricas do dashboard com filtro de data de modificação"""
        return self.get_dashboard_metrics(correlation_id=correlation_id)

    def get_dashboard_metrics_with_filters(
        self,
        start_date=None,
        end_date=None,
        status=None,
        priority=None,
        level=None,
        technician=None,
        category=None,
        correlation_id=None,
    ) -> Dict[str, Any]:
        """Mock das métricas do dashboard com filtros diversos"""
        return self.get_dashboard_metrics(correlation_id=correlation_id)

    def get_new_tickets(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Mock de tickets novos"""
        tickets = []
        for i in range(min(limit, 10)):  # Limita a 10 tickets mock
            ticket_id = 1000 + i
            tickets.append(
                {
                    "id": ticket_id,
                    "name": f"Ticket de Teste #{ticket_id}",
                    "content": f"Descrição do ticket {ticket_id} - Problema simulado para testes",
                    "date": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
                    "users_id": random.randint(100, 200),
                    "priority": random.randint(1, 4),
                    "itilcategories_id": random.randint(1, 10),
                    "status": 1,  # Novo
                    "requester_name": f"Usuário Teste {random.randint(1, 50)}",
                    "category_name": f"Categoria {random.randint(1, 10)}",
                }
            )
        return tickets

    def get_ticket_details(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Mock de detalhes do ticket"""
        return {
            "id": ticket_id,
            "name": f"Ticket Detalhado #{ticket_id}",
            "content": f"Descrição completa do ticket {ticket_id} com mais " f"detalhes para visualização",
            "date": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
            "users_id": random.randint(100, 200),
            "priority": random.randint(1, 4),
            "itilcategories_id": random.randint(1, 10),
            "status": random.randint(1, 4),
            "requester_name": f"Usuário Detalhado {random.randint(1, 50)}",
            "category_name": f"Categoria Detalhada {random.randint(1, 10)}",
            "technician_name": f"Técnico {random.randint(1, 20)}",
            "created_at": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
            "updated_at": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
        }

    def get_technician_ranking(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Mock do ranking de técnicos"""
        technicians = []
        for i in range(min(limit, 15)):  # Limita a 15 técnicos mock
            technicians.append(
                {
                    "id": 200 + i,
                    "name": f"Técnico {i + 1}",
                    "tickets_resolved": random.randint(10, 100),
                    "avg_resolution_time": round(random.uniform(1.0, 5.0), 2),
                    "satisfaction_rate": round(random.uniform(3.5, 5.0), 2),
                    "level": random.randint(1, 3),
                }
            )
        return sorted(technicians, key=lambda x: x["tickets_resolved"], reverse=True)

    def get_technician_ranking_with_filters(self, **kwargs) -> List[Dict[str, Any]]:
        """Mock do ranking de técnicos com filtros"""
        return self.get_technician_ranking(kwargs.get("limit", 100))

    def get_alerts(self) -> List[Dict[str, Any]]:
        """Mock de alertas"""
        return [
            {
                "id": 1,
                "type": "warning",
                "message": "Alto número de tickets pendentes",
                "count": 42,
                "timestamp": datetime.now().isoformat(),
            },
            {
                "id": 2,
                "type": "info",
                "message": "Sistema funcionando normalmente",
                "count": 0,
                "timestamp": datetime.now().isoformat(),
            },
        ]

    def _get_user_name_by_id(self, user_id: int) -> str:
        """Mock para obter nome do usuário"""
        return f"Usuário Mock {user_id}"

    def _get_category_name_by_id(self, category_id: int) -> str:
        """Mock para obter nome da categoria"""
        categories = {
            1: "Hardware",
            2: "Software",
            3: "Rede",
            4: "Impressora",
            5: "Email",
            6: "Sistema",
            7: "Telefonia",
            8: "Acesso",
            9: "Backup",
            10: "Outros",
        }
        return categories.get(category_id, f"Categoria {category_id}")
