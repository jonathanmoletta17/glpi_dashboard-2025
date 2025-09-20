import re
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field, validator


class LevelMetrics(BaseModel):
    """Métricas de um nível específico (N1, N2, N3, N4)"""

    novos: int = Field(ge=0, description="Número de tickets novos")
    pendentes: int = Field(ge=0, description="Número de tickets pendentes")
    progresso: int = Field(ge=0, description="Número de tickets em progresso")
    resolvidos: int = Field(ge=0, description="Número de tickets resolvidos")


class NiveisMetrics(BaseModel):
    """Métricas de todos os níveis"""

    n1: LevelMetrics
    n2: LevelMetrics
    n3: LevelMetrics
    n4: LevelMetrics


class TendenciasMetrics(BaseModel):
    """Tendências das métricas (percentuais de variação)"""

    novos: float = Field(default=0.0, description="Variação percentual de tickets novos")
    pendentes: float = Field(default=0.0, description="Variação percentual de tickets pendentes")
    progresso: float = Field(default=0.0, description="Variação percentual de tickets em progresso")
    resolvidos: float = Field(default=0.0, description="Variação percentual de tickets resolvidos")


class FiltersApplied(BaseModel):
    """Filtros aplicados na consulta"""

    start_date: Optional[str] = Field(None, description="Data inicial (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Data final (YYYY-MM-DD)")
    status: Optional[str] = Field(None, description="Status do ticket")
    priority: Optional[str] = Field(None, description="Prioridade do ticket")
    level: Optional[str] = Field(None, description="Nível do ticket (N1, N2, N3, N4)")
    technician: Optional[str] = Field(None, description="ID ou nome do técnico")
    category: Optional[str] = Field(None, description="Categoria do ticket")

    @validator("start_date", "end_date")
    def validate_date_format(cls, v):
        """Valida formato de data YYYY-MM-DD"""
        if v and not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Data deve estar no formato YYYY-MM-DD")
        return v

    @validator("level")
    def validate_level(cls, v):
        """Valida se o nível é válido"""
        if v and v not in ["N1", "N2", "N3", "N4"]:
            raise ValueError("Nível deve ser N1, N2, N3 ou N4")
        return v


class DashboardMetrics(BaseModel):
    """Schema unificado para métricas do dashboard
    Exemplo:
        {
            "novos": 25,
            "pendentes": 150,
            "progresso": 75,
            "resolvidos": 300,
            "total": 550,
            "niveis": {
                "n1": {
                    "novos": 10, "pendentes": 50,
                    "progresso": 25, "resolvidos": 100
                },
                "n2": {
                    "novos": 8, "pendentes": 40,
                    "progresso": 20, "resolvidos": 80
                },
                "n3": {
                    "novos": 5, "pendentes": 35,
                    "progresso": 18, "resolvidos": 70
                },
                "n4": {
                    "novos": 2, "pendentes": 25,
                    "progresso": 12, "resolvidos": 50
                }
            },
            "tendencias": {
                "novos": 12.5,
                "pendentes": -5.2,
                "progresso": 8.1,
                "resolvidos": 15.3
            }
        }
    """

    novos: int = Field(ge=0, description="Total de tickets novos")
    pendentes: int = Field(ge=0, description="Total de tickets pendentes")
    progresso: int = Field(ge=0, description="Total de tickets em progresso")
    resolvidos: int = Field(ge=0, description="Total de tickets resolvidos")
    total: int = Field(ge=0, description="Total geral de tickets")
    niveis: NiveisMetrics
    tendencias: TendenciasMetrics
    filters_applied: Optional[FiltersApplied] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    @validator("total")
    def validate_total_consistency(cls, v, values):
        """Valida se o total é consistente com a soma dos campos"""
        if "novos" in values and "pendentes" in values and "progresso" in values and "resolvidos" in values:
            calculated_total = values["novos"] + values["pendentes"] + values["progresso"] + values["resolvidos"]
            if v != calculated_total:
                raise ValueError(f"Total ({v}) deve ser igual à soma dos campos " f"({calculated_total})")
        return v


class TechnicianRanking(BaseModel):
    """Ranking de técnico
    Exemplo:
        {
            "id": 123,
            "name": "João Silva",
            "ticket_count": 45,
            "level": "N2",
            "performance_score": 8.7
        }
    """

    id: int = Field(description="ID único do técnico")
    name: str = Field(min_length=1, description="Nome do técnico")
    ticket_count: int = Field(ge=0, description="Quantidade de tickets atribuídos")
    level: str = Field(description="Nível do técnico (N1, N2, N3, N4)")
    performance_score: Optional[float] = Field(None, ge=0, le=10, description="Score de performance (0-10)")

    @validator("level")
    def validate_technician_level(cls, v):
        """Valida se o nível do técnico é válido"""
        if v not in ["N1", "N2", "N3", "N4"]:
            raise ValueError("Nível do técnico deve ser N1, N2, N3 ou N4")
        return v


class NewTicket(BaseModel):
    """Ticket novo
    Exemplo:
        {
            "id": "10280",
            "title": "Problema com email",
            "description": "Não consigo acessar minha conta de email",
            "date": "2025-01-06T14:30:00",
            "requester": "Maria Santos",
            "priority": "Média",
            "status": "Novo",
            "category": "Email"
        }
    """

    id: str = Field(min_length=1, description="ID único do ticket")
    title: str = Field(min_length=1, max_length=255, description="Título do ticket")
    description: str = Field(description="Descrição detalhada do problema")
    date: str = Field(description="Data de criação do ticket")
    requester: str = Field(min_length=1, description="Nome do solicitante")
    priority: str = Field(description="Prioridade do ticket")
    category: Optional[str] = Field(None, description="Categoria do ticket")
    status: str = Field(default="Novo", description="Status atual do ticket")
    filters_applied: Optional[FiltersApplied] = None

    @validator("priority")
    def validate_priority(cls, v):
        """Valida se a prioridade é válida"""
        valid_priorities = ["Muito baixa", "Baixa", "Média", "Alta", "Muito alta"]
        if v not in valid_priorities:
            raise ValueError(f'Prioridade deve ser uma de: {", ".join(valid_priorities)}')
        return v


class ApiResponse(BaseModel):
    """Schema padrão para respostas da API

    Exemplo de sucesso:
        {
            "success": true,
            "data": {"novos": 25, "total": 100},
            "message": "Dados obtidos com sucesso",
            "timestamp": "2025-01-06T14:30:00",
            "execution_time_ms": 150.5
        }
    """

    success: bool = Field(default=True, description="Indica se a operação foi bem-sucedida")
    data: Any = Field(description="Dados retornados pela API")
    message: Optional[str] = Field(None, description="Mensagem informativa")
    errors: Optional[List[str]] = Field(None, description="Lista de erros, se houver")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da resposta")
    execution_time_ms: Optional[float] = Field(None, ge=0, description="Tempo de execução em millisegundos")


class ApiError(BaseModel):
    """Schema para erros da API
    Exemplo:
        {
            "success": false,
            "data": null,
            "message": "Erro ao processar solicitação",
            "errors": [
                "Parâmetro obrigatório ausente",
                "Formato de data inválido"
            ],
            "timestamp": "2025-01-06T14:30:00",
            "error_code": "VALIDATION_ERROR"
        }
    """

    success: bool = Field(default=False, description="Sempre false para erros")
    data: None = Field(default=None, description="Sempre null para erros")
    message: str = Field(description="Mensagem principal do erro")
    errors: List[str] = Field(description="Lista detalhada de erros")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp do erro")
    error_code: Optional[str] = Field(None, description="Código específico do erro")
