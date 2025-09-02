"""Utilitário para conversão entre convenções de nomenclatura.

Este módulo fornece funções para converter entre snake_case (backend)
e camelCase (frontend), padronizando a comunicação entre as camadas.
"""

import re
from typing import Any, Dict, List, Union


class NamingConverter:
    """Conversor de convenções de nomenclatura entre backend e frontend."""

    # Mapeamentos específicos para casos especiais
    SNAKE_TO_CAMEL_MAP = {
        'start_date': 'startDate',
        'end_date': 'endDate',
        'filter_type': 'filterType',
        'entity_id': 'entityId',
        'ticket_id': 'ticketId',
        'user_id': 'userId',
        'technician_id': 'technicianId',
        'category_id': 'categoryId',
        'priority_id': 'priorityId',
        'status_id': 'statusId',
        'created_at': 'createdAt',
        'updated_at': 'updatedAt',
        'resolved_at': 'resolvedAt',
        'closed_at': 'closedAt',
        'response_time': 'responseTime',
        'resolution_time': 'resolutionTime',
        'last_update': 'lastUpdate',
        'sistema_ativo': 'sistemaAtivo',
        'ultima_atualizacao': 'ultimaAtualizacao',
        'tickets_resolved': 'ticketsResolved',
        'tickets_in_progress': 'ticketsInProgress',
        'average_resolution_time': 'averageResolutionTime',
        'by_level': 'byLevel',
        'raw_data': 'rawData',
        'date_range': 'dateRange',
        'filtros_aplicados': 'filtrosAplicados',
        'tempo_execucao': 'tempoExecucao',
        'system_status': 'systemStatus',
        'technician_ranking': 'technicianRanking'
    }

    CAMEL_TO_SNAKE_MAP = {v: k for k, v in SNAKE_TO_CAMEL_MAP.items()}

    @classmethod
    def snake_to_camel(cls, snake_str: str) -> str:
        """Converte string de snake_case para camelCase.
        
        Args:
            snake_str: String em snake_case
            
        Returns:
            String em camelCase
        """
        # Verificar mapeamento específico primeiro
        if snake_str in cls.SNAKE_TO_CAMEL_MAP:
            return cls.SNAKE_TO_CAMEL_MAP[snake_str]
        
        # Conversão automática
        components = snake_str.split('_')
        return components[0] + ''.join(word.capitalize() for word in components[1:])

    @classmethod
    def camel_to_snake(cls, camel_str: str) -> str:
        """Converte string de camelCase para snake_case.
        
        Args:
            camel_str: String em camelCase
            
        Returns:
            String em snake_case
        """
        # Verificar mapeamento específico primeiro
        if camel_str in cls.CAMEL_TO_SNAKE_MAP:
            return cls.CAMEL_TO_SNAKE_MAP[camel_str]
        
        # Conversão automática usando regex
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @classmethod
    def convert_dict_keys_to_camel(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Converte todas as chaves de um dicionário para camelCase.
        
        Args:
            data: Dicionário com chaves em snake_case
            
        Returns:
            Dicionário com chaves em camelCase
        """
        if not isinstance(data, dict):
            return data
        
        converted = {}
        for key, value in data.items():
            camel_key = cls.snake_to_camel(key)
            
            # Recursivamente converter dicionários aninhados
            if isinstance(value, dict):
                converted[camel_key] = cls.convert_dict_keys_to_camel(value)
            elif isinstance(value, list):
                converted[camel_key] = [
                    cls.convert_dict_keys_to_camel(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                converted[camel_key] = value
                
        return converted

    @classmethod
    def convert_dict_keys_to_snake(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Converte todas as chaves de um dicionário para snake_case.
        
        Args:
            data: Dicionário com chaves em camelCase
            
        Returns:
            Dicionário com chaves em snake_case
        """
        if not isinstance(data, dict):
            return data
        
        converted = {}
        for key, value in data.items():
            snake_key = cls.camel_to_snake(key)
            
            # Recursivamente converter dicionários aninhados
            if isinstance(value, dict):
                converted[snake_key] = cls.convert_dict_keys_to_snake(value)
            elif isinstance(value, list):
                converted[snake_key] = [
                    cls.convert_dict_keys_to_snake(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                converted[snake_key] = value
                
        return converted

    @classmethod
    def normalize_api_params(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza parâmetros da API convertendo camelCase para snake_case.
        
        Esta função é especialmente útil para converter parâmetros vindos
        do frontend (camelCase) para o formato esperado pelo backend (snake_case).
        
        Args:
            params: Dicionário com parâmetros em camelCase
            
        Returns:
            Dicionário com parâmetros em snake_case
        """
        return cls.convert_dict_keys_to_snake(params)

    @classmethod
    def normalize_api_response(cls, response: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza resposta da API convertendo snake_case para camelCase.
        
        Esta função é especialmente útil para converter respostas do backend
        (snake_case) para o formato esperado pelo frontend (camelCase).
        
        Args:
            response: Dicionário com dados em snake_case
            
        Returns:
            Dicionário com dados em camelCase
        """
        return cls.convert_dict_keys_to_camel(response)


# Funções de conveniência para uso direto
def snake_to_camel(snake_str: str) -> str:
    """Função de conveniência para converter snake_case para camelCase."""
    return NamingConverter.snake_to_camel(snake_str)


def camel_to_snake(camel_str: str) -> str:
    """Função de conveniência para converter camelCase para snake_case."""
    return NamingConverter.camel_to_snake(camel_str)


def normalize_frontend_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza parâmetros vindos do frontend (camelCase → snake_case)."""
    return NamingConverter.normalize_api_params(params)


def normalize_backend_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza resposta do backend (snake_case → camelCase)."""
    return NamingConverter.normalize_api_response(response)