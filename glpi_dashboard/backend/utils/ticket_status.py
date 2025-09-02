# -*- coding: utf-8 -*-
"""
Ticket Status Enum

Este módulo define o enum centralizado para status de tickets GLPI.
Padroniza o mapeamento de status em todo o sistema.

Autor: Sistema de Auditoria
Data: 15 de Janeiro de 2025
Versão: 1.0
"""

from enum import Enum, IntEnum
from typing import Dict, Optional, List


class TicketStatus(IntEnum):
    """
    Enum para status de tickets GLPI.
    
    Valores baseados na estrutura padrão do GLPI:
    1 = Novo
    2 = Em andamento (atribuído)
    3 = Planejado
    4 = Pendente
    5 = Solucionado
    6 = Fechado
    """
    
    NEW = 1
    IN_PROGRESS = 2
    PLANNED = 3
    PENDING = 4
    SOLVED = 5
    CLOSED = 6
    
    @classmethod
    def get_display_name(cls, status_id: int) -> str:
        """
        Retorna o nome de exibição para um status.
        
        Args:
            status_id: ID do status
            
        Returns:
            str: Nome de exibição do status
        """
        mapping = {
            cls.NEW.value: "new",
            cls.IN_PROGRESS.value: "in_progress",
            cls.PLANNED.value: "planned",
            cls.PENDING.value: "pending",
            cls.SOLVED.value: "solved",
            cls.CLOSED.value: "closed"
        }
        return mapping.get(status_id, "unknown")
    
    @classmethod
    def get_display_name_pt(cls, status_id: int) -> str:
        """
        Retorna o nome de exibição em português para um status.
        
        Args:
            status_id: ID do status
            
        Returns:
            str: Nome de exibição do status em português
        """
        mapping = {
            cls.NEW.value: "Novo",
            cls.IN_PROGRESS.value: "Em Andamento",
            cls.PLANNED.value: "Planejado",
            cls.PENDING.value: "Pendente",
            cls.SOLVED.value: "Solucionado",
            cls.CLOSED.value: "Fechado"
        }
        return mapping.get(status_id, "Desconhecido")
    
    @classmethod
    def get_color_class(cls, status_id: int) -> str:
        """
        Retorna a classe CSS de cor para um status.
        
        Args:
            status_id: ID do status
            
        Returns:
            str: Classe CSS de cor
        """
        mapping = {
            cls.NEW.value: "text-blue-600",
            cls.IN_PROGRESS.value: "text-yellow-600",
            cls.PLANNED.value: "text-purple-600",
            cls.PENDING.value: "text-orange-600",
            cls.SOLVED.value: "text-green-600",
            cls.CLOSED.value: "text-gray-600"
        }
        return mapping.get(status_id, "text-gray-400")
    
    @classmethod
    def get_background_class(cls, status_id: int) -> str:
        """
        Retorna a classe CSS de fundo para um status.
        
        Args:
            status_id: ID do status
            
        Returns:
            str: Classe CSS de fundo
        """
        mapping = {
            cls.NEW.value: "bg-blue-100",
            cls.IN_PROGRESS.value: "bg-yellow-100",
            cls.PLANNED.value: "bg-purple-100",
            cls.PENDING.value: "bg-orange-100",
            cls.SOLVED.value: "bg-green-100",
            cls.CLOSED.value: "bg-gray-100"
        }
        return mapping.get(status_id, "bg-gray-50")
    
    @classmethod
    def is_valid_status(cls, status_id: int) -> bool:
        """
        Verifica se um status ID é válido.
        
        Args:
            status_id: ID do status para verificar
            
        Returns:
            bool: True se válido, False caso contrário
        """
        try:
            return status_id in [member.value for member in cls]
        except (TypeError, ValueError):
            return False
    
    @classmethod
    def get_active_statuses(cls) -> List[int]:
        """
        Retorna lista de status considerados "ativos" (não fechados).
        
        Returns:
            List[int]: Lista de IDs de status ativos
        """
        return [cls.NEW.value, cls.IN_PROGRESS.value, cls.PLANNED.value, cls.PENDING.value]
    
    @classmethod
    def get_resolved_statuses(cls) -> List[int]:
        """
        Retorna lista de status considerados "resolvidos".
        
        Returns:
            List[int]: Lista de IDs de status resolvidos
        """
        return [cls.SOLVED.value, cls.CLOSED.value]
    
    @classmethod
    def get_pending_statuses(cls) -> List[int]:
        """
        Retorna lista de status considerados "pendentes".
        
        Returns:
            List[int]: Lista de IDs de status pendentes
        """
        return [cls.PENDING.value]
    
    @classmethod
    def get_in_progress_statuses(cls) -> List[int]:
        """
        Retorna lista de status considerados "em andamento".
        
        Returns:
            List[int]: Lista de IDs de status em andamento
        """
        return [cls.IN_PROGRESS.value, cls.PLANNED.value]
    
    @classmethod
    def get_status_category(cls, status_id: int) -> str:
        """
        Retorna a categoria de um status.
        
        Args:
            status_id: ID do status
            
        Returns:
            str: Categoria do status (active, resolved, pending, etc.)
        """
        if status_id in cls.get_resolved_statuses():
            return "resolved"
        elif status_id in cls.get_pending_statuses():
            return "pending"
        elif status_id in cls.get_in_progress_statuses():
            return "in_progress"
        elif status_id == cls.NEW.value:
            return "new"
        else:
            return "unknown"
    
    @classmethod
    def get_all_status_info(cls) -> Dict[int, Dict[str, str]]:
        """
        Retorna informações completas de todos os status.
        
        Returns:
            Dict[int, Dict[str, str]]: Dicionário com informações de cada status
        """
        info = {}
        for status in cls:
            info[status.value] = {
                'id': status.value,
                'name': cls.get_display_name(status.value),
                'name_pt': cls.get_display_name_pt(status.value),
                'color_class': cls.get_color_class(status.value),
                'background_class': cls.get_background_class(status.value),
                'category': cls.get_status_category(status.value)
            }
        return info
    
    @classmethod
    def get_status_name_to_id_map(cls) -> Dict[str, int]:
        """
        Retorna mapeamento de nomes de status em português para IDs GLPI.
        
        Returns:
            Dict[str, int]: Dicionário com mapeamento de nomes para IDs
        """
        return {
            "novo": cls.NEW.value,
            "progresso": cls.IN_PROGRESS.value,
            "cancelado": cls.PLANNED.value,  # Mapeamento para status planejado
            "pendente": cls.PENDING.value,
            "resolvido": cls.SOLVED.value,
            "fechado": cls.CLOSED.value,
        }


class TicketPriority(IntEnum):
    """
    Enum para prioridades de tickets GLPI.
    
    Valores baseados na estrutura padrão do GLPI:
    1 = Muito baixa
    2 = Baixa
    3 = Média
    4 = Alta
    5 = Muito alta
    6 = Crítica
    """
    
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5
    CRITICAL = 6
    
    @classmethod
    def get_display_name(cls, priority_id: int) -> str:
        """
        Retorna o nome de exibição para uma prioridade.
        
        Args:
            priority_id: ID da prioridade
            
        Returns:
            str: Nome de exibição da prioridade
        """
        mapping = {
            cls.VERY_LOW.value: "very_low",
            cls.LOW.value: "low",
            cls.MEDIUM.value: "medium",
            cls.HIGH.value: "high",
            cls.VERY_HIGH.value: "very_high",
            cls.CRITICAL.value: "critical"
        }
        return mapping.get(priority_id, "unknown")
    
    @classmethod
    def get_display_name_pt(cls, priority_id: int) -> str:
        """
        Retorna o nome de exibição em português para uma prioridade.
        
        Args:
            priority_id: ID da prioridade
            
        Returns:
            str: Nome de exibição da prioridade em português
        """
        mapping = {
            cls.VERY_LOW.value: "Muito Baixa",
            cls.LOW.value: "Baixa",
            cls.MEDIUM.value: "Média",
            cls.HIGH.value: "Alta",
            cls.VERY_HIGH.value: "Muito Alta",
            cls.CRITICAL.value: "Crítica"
        }
        return mapping.get(priority_id, "Desconhecida")
    
    @classmethod
    def get_color_class(cls, priority_id: int) -> str:
        """
        Retorna a classe CSS de cor para uma prioridade.
        
        Args:
            priority_id: ID da prioridade
            
        Returns:
            str: Classe CSS de cor
        """
        mapping = {
            cls.VERY_LOW.value: "text-gray-500",
            cls.LOW.value: "text-blue-500",
            cls.MEDIUM.value: "text-yellow-500",
            cls.HIGH.value: "text-orange-500",
            cls.VERY_HIGH.value: "text-red-500",
            cls.CRITICAL.value: "text-red-700"
        }
        return mapping.get(priority_id, "text-gray-400")


class TechnicianLevel(IntEnum):
    """
    Enum para níveis de técnicos.
    
    Valores baseados na hierarquia do sistema:
    1 = N1 (Nível 1)
    2 = N2 (Nível 2)
    3 = N3 (Nível 3)
    4 = N4 (Nível 4)
    """
    
    N1 = 1
    N2 = 2
    N3 = 3
    N4 = 4
    
    @classmethod
    def get_display_name(cls, level_id: int) -> str:
        """
        Retorna o nome de exibição para um nível.
        
        Args:
            level_id: ID do nível
            
        Returns:
            str: Nome de exibição do nível
        """
        mapping = {
            cls.N1.value: "N1",
            cls.N2.value: "N2",
            cls.N3.value: "N3",
            cls.N4.value: "N4"
        }
        return mapping.get(level_id, "Unknown")
    
    @classmethod
    def is_valid_level(cls, level_id: int) -> bool:
        """
        Verifica se um nível ID é válido.
        
        Args:
            level_id: ID do nível para verificar
            
        Returns:
            bool: True se válido, False caso contrário
        """
        try:
            return level_id in [member.value for member in cls]
        except (TypeError, ValueError):
            return False


# Funções de conveniência
def get_status_display_name(status_id: int, language: str = 'en') -> str:
    """
    Função de conveniência para obter nome de exibição do status.
    
    Args:
        status_id: ID do status
        language: Idioma ('en' ou 'pt')
        
    Returns:
        str: Nome de exibição do status
    """
    if language == 'pt':
        return TicketStatus.get_display_name_pt(status_id)
    return TicketStatus.get_display_name(status_id)


def get_priority_display_name(priority_id: int, language: str = 'en') -> str:
    """
    Função de conveniência para obter nome de exibição da prioridade.
    
    Args:
        priority_id: ID da prioridade
        language: Idioma ('en' ou 'pt')
        
    Returns:
        str: Nome de exibição da prioridade
    """
    if language == 'pt':
        return TicketPriority.get_display_name_pt(priority_id)
    return TicketPriority.get_display_name(priority_id)


def validate_status_id(status_id: int) -> bool:
    """
    Função de conveniência para validar status ID.
    
    Args:
        status_id: ID do status para validar
        
    Returns:
        bool: True se válido, False caso contrário
    """
    return TicketStatus.is_valid_status(status_id)


def validate_level_id(level_id: int) -> bool:
    """
    Função de conveniência para validar nível ID.
    
    Args:
        level_id: ID do nível para validar
        
    Returns:
        bool: True se válido, False caso contrário
    """
    return TechnicianLevel.is_valid_level(level_id)