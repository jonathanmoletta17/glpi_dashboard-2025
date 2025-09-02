
# -*- coding: utf-8 -*-
"""
GLPI Data Validator Enhanced

Versão melhorada que suporta mapeamento de campos numéricos da API GLPI.

Autor: Sistema de Auditoria
Data: 30 de Agosto de 2025
Versão: 2.0
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import re

# Mapeamento de campos GLPI
GLPI_FIELD_MAPPING = {
    "2": "id",
    "1": "name",
    "12": "status",
    "80": "entities_id",
    "15": "date",
    "19": "date_mod",
    "16": "closedate",
    "17": "solvedate",
    "5": "users_id_assign",
    "8": "groups_id_assign",
    "71": "groups_id",
    "7": "itilcategories_id",
    "3": "priority",
    "21": "content",
    "6": "users_id_recipient",
    "22": "users_id_lastupdater",
    "18": "due_date",
    "14": "type",
    "13": "urgency",
    "11": "impact",
    "37": "locations_id",
}

class GLPIDataValidatorEnhanced:
    """
    Validador melhorado para dados da API GLPI com suporte a mapeamento de campos.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.field_mapping = GLPI_FIELD_MAPPING
        
        # Padrões de validação
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.name_pattern = re.compile(r'^[a-zA-ZÀ-ÿ\s\-\.]{2,100}$')
    
    def convert_glpi_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte dados da API GLPI de formato numérico para nomes de campos.
        """
        converted_data = {}
        
        for field_num, value in raw_data.items():
            field_name = self.field_mapping.get(str(field_num), f"field_{field_num}")
            converted_data[field_name] = value
        
        return converted_data
    
    def validate_ticket_data(self, ticket: Dict[str, Any], auto_convert: bool = True) -> bool:
        """
        Valida dados de um ticket GLPI com suporte a conversão automática.
        
        Args:
            ticket: Dicionário com dados do ticket
            auto_convert: Se True, tenta converter campos numéricos automaticamente
            
        Returns:
            bool: True se válido, False caso contrário
        """
        try:
            # Verificar se precisa converter campos numéricos
            if auto_convert and self._has_numeric_fields(ticket):
                ticket = self.convert_glpi_data(ticket)
            
            # Campos obrigatórios
            required_fields = ['id', 'status']
            
            # Verificar campos obrigatórios
            for field in required_fields:
                if field not in ticket or ticket[field] is None:
                    self.logger.warning(f"Campo obrigatório '{field}' ausente ou nulo no ticket")
                    return False
            
            # Validar ID do ticket
            if not self._validate_id(ticket['id']):
                self.logger.warning(f"ID de ticket inválido: {ticket.get('id')}")
                return False
            
            # Validar status
            if not self._validate_status(ticket['status']):
                self.logger.warning(f"Status de ticket inválido: {ticket.get('status')}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao validar dados do ticket: {e}")
            return False
    
    def _has_numeric_fields(self, data: Dict[str, Any]) -> bool:
        """
        Verifica se os dados contêm campos numéricos (formato da API GLPI).
        """
        return any(key.isdigit() for key in data.keys())
    
    def _validate_id(self, value: Any) -> bool:
        """
        Valida se um valor é um ID válido.
        """
        try:
            return isinstance(value, (int, str)) and int(value) > 0
        except (ValueError, TypeError):
            return False
    
    def _validate_status(self, value: Any) -> bool:
        """
        Valida se um valor é um status válido.
        """
        try:
            status_int = int(value)
            return 1 <= status_int <= 6  # Status válidos do GLPI
        except (ValueError, TypeError):
            return False
    
    def validate_api_response(self, response_data: Any) -> bool:
        """
        Valida estrutura básica de resposta da API GLPI.
        
        Args:
            response_data: Dados da resposta da API
            
        Returns:
            bool: True se válido, False caso contrário
        """
        try:
            # Verificar se não é None
            if response_data is None:
                self.logger.warning("Resposta da API é None")
                return False
            
            # Se for lista, verificar se não está vazia
            if isinstance(response_data, list):
                if len(response_data) == 0:
                    self.logger.info("Resposta da API é uma lista vazia (válido)")
                    return True
                
                # Verificar primeiro item da lista
                first_item = response_data[0]
                if not isinstance(first_item, dict):
                    self.logger.warning("Primeiro item da lista não é um dicionário")
                    return False
            
            # Se for dicionário, verificar estrutura básica
            elif isinstance(response_data, dict):
                # Verificar se não é um erro
                if 'ERROR' in response_data or 'error' in response_data:
                    self.logger.warning(f"Resposta da API contém erro: {response_data}")
                    return False
            
            else:
                self.logger.warning(f"Tipo de resposta inesperado: {type(response_data)}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao validar resposta da API: {e}")
            return False
