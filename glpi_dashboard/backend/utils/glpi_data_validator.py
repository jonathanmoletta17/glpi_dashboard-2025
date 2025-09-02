# -*- coding: utf-8 -*-
"""
GLPI Data Validator

Este módulo fornece validação robusta para dados recebidos da API GLPI.
Garante que os dados estejam em formato correto antes do processamento.

Autor: Sistema de Auditoria
Data: 15 de Janeiro de 2025
Versão: 1.0
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import re


class GLPIDataValidator:
    """
    Validador robusto para dados da API GLPI.
    
    Fornece métodos para validar diferentes tipos de dados:
    - Tickets
    - Usuários/Técnicos
    - Grupos
    - Entidades
    - Perfis
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Padrões de validação
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.name_pattern = re.compile(r'^[a-zA-ZÀ-ÿ\s\-\.]{2,100}$')
        
    def validate_ticket_data(self, ticket: Dict[str, Any]) -> bool:
        """
        Valida dados de um ticket GLPI.
        
        Args:
            ticket: Dicionário com dados do ticket
            
        Returns:
            bool: True se válido, False caso contrário
        """
        try:
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
            
            # Validar técnico atribuído (se presente)
            if 'users_id_assign' in ticket and ticket['users_id_assign'] is not None:
                if not self._validate_id(ticket['users_id_assign']):
                    self.logger.warning(f"ID de técnico inválido: {ticket.get('users_id_assign')}")
                    return False
            
            # Validar datas (se presentes)
            date_fields = ['date', 'date_mod', 'closedate', 'solvedate']
            for date_field in date_fields:
                if date_field in ticket and ticket[date_field]:
                    if not self._validate_datetime(ticket[date_field]):
                        self.logger.warning(f"Data inválida no campo '{date_field}': {ticket.get(date_field)}")
                        return False
            
            # Validar entidade (se presente)
            if 'entities_id' in ticket and ticket['entities_id'] is not None:
                if not self._validate_id(ticket['entities_id']):
                    self.logger.warning(f"ID de entidade inválido: {ticket.get('entities_id')}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao validar dados do ticket: {e}")
            return False
    
    def validate_user_data(self, user: Dict[str, Any]) -> bool:
        """
        Valida dados de um usuário/técnico GLPI.
        
        Args:
            user: Dicionário com dados do usuário
            
        Returns:
            bool: True se válido, False caso contrário
        """
        try:
            # Campos obrigatórios
            required_fields = ['id', 'realname']
            
            # Verificar campos obrigatórios
            for field in required_fields:
                if field not in user or not user[field]:
                    self.logger.warning(f"Campo obrigatório '{field}' ausente ou vazio no usuário")
                    return False
            
            # Validar ID do usuário
            if not self._validate_id(user['id']):
                self.logger.warning(f"ID de usuário inválido: {user.get('id')}")
                return False
            
            # Validar nome real
            realname = str(user['realname']).strip()
            if len(realname) < 2 or len(realname) > 100:
                self.logger.warning(f"Nome real inválido (tamanho): {realname}")
                return False
            
            if not self.name_pattern.match(realname):
                self.logger.warning(f"Nome real inválido (formato): {realname}")
                return False
            
            # Validar email (se presente)
            if 'email' in user and user['email']:
                if not self.email_pattern.match(user['email']):
                    self.logger.warning(f"Email inválido: {user.get('email')}")
                    return False
            
            # Validar status ativo (se presente)
            if 'is_active' in user:
                if not isinstance(user['is_active'], (int, bool)):
                    self.logger.warning(f"Status ativo inválido: {user.get('is_active')}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao validar dados do usuário: {e}")
            return False
    
    def validate_group_data(self, group: Dict[str, Any]) -> bool:
        """
        Valida dados de um grupo GLPI.
        
        Args:
            group: Dicionário com dados do grupo
            
        Returns:
            bool: True se válido, False caso contrário
        """
        try:
            # Campos obrigatórios
            required_fields = ['id', 'name']
            
            # Verificar campos obrigatórios
            for field in required_fields:
                if field not in group or not group[field]:
                    self.logger.warning(f"Campo obrigatório '{field}' ausente ou vazio no grupo")
                    return False
            
            # Validar ID do grupo
            if not self._validate_id(group['id']):
                self.logger.warning(f"ID de grupo inválido: {group.get('id')}")
                return False
            
            # Validar nome do grupo
            name = str(group['name']).strip()
            if len(name) < 2 or len(name) > 255:
                self.logger.warning(f"Nome de grupo inválido (tamanho): {name}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao validar dados do grupo: {e}")
            return False
    
    def validate_entity_data(self, entity: Dict[str, Any]) -> bool:
        """
        Valida dados de uma entidade GLPI.
        
        Args:
            entity: Dicionário com dados da entidade
            
        Returns:
            bool: True se válido, False caso contrário
        """
        try:
            # Campos obrigatórios
            required_fields = ['id', 'name']
            
            # Verificar campos obrigatórios
            for field in required_fields:
                if field not in entity or not entity[field]:
                    self.logger.warning(f"Campo obrigatório '{field}' ausente ou vazio na entidade")
                    return False
            
            # Validar ID da entidade
            if not self._validate_id(entity['id']):
                self.logger.warning(f"ID de entidade inválido: {entity.get('id')}")
                return False
            
            # Validar nome da entidade
            name = str(entity['name']).strip()
            if len(name) < 1 or len(name) > 255:
                self.logger.warning(f"Nome de entidade inválido (tamanho): {name}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao validar dados da entidade: {e}")
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
    
    def validate_batch_data(self, data_list: List[Dict[str, Any]], 
                          validator_func: callable) -> List[Dict[str, Any]]:
        """
        Valida uma lista de dados usando uma função validadora específica.
        
        Args:
            data_list: Lista de dicionários para validar
            validator_func: Função de validação a ser aplicada
            
        Returns:
            List[Dict[str, Any]]: Lista apenas com dados válidos
        """
        valid_data = []
        invalid_count = 0
        
        for item in data_list:
            if validator_func(item):
                valid_data.append(item)
            else:
                invalid_count += 1
        
        if invalid_count > 0:
            self.logger.warning(f"Encontrados {invalid_count} itens inválidos de {len(data_list)} total")
        
        return valid_data
    
    def _validate_id(self, id_value: Any) -> bool:
        """
        Valida se um ID é válido (número inteiro positivo).
        
        Args:
            id_value: Valor do ID para validar
            
        Returns:
            bool: True se válido, False caso contrário
        """
        try:
            # Converter para int se for string
            if isinstance(id_value, str):
                id_value = int(id_value)
            
            # Verificar se é inteiro positivo
            return isinstance(id_value, int) and id_value > 0
            
        except (ValueError, TypeError):
            return False
    
    def _validate_status(self, status_value: Any) -> bool:
        """
        Valida se um status é válido (1-6).
        
        Args:
            status_value: Valor do status para validar
            
        Returns:
            bool: True se válido, False caso contrário
        """
        try:
            # Converter para int se for string
            if isinstance(status_value, str):
                status_value = int(status_value)
            
            # Verificar se está no range válido (1-6)
            return isinstance(status_value, int) and 1 <= status_value <= 6
            
        except (ValueError, TypeError):
            return False
    
    def _validate_datetime(self, datetime_value: Any) -> bool:
        """
        Valida se uma data/hora está em formato válido.
        
        Args:
            datetime_value: Valor da data/hora para validar
            
        Returns:
            bool: True se válido, False caso contrário
        """
        try:
            if not datetime_value:
                return False
            
            # Formatos aceitos
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%d/%m/%Y %H:%M:%S',
                '%d/%m/%Y'
            ]
            
            datetime_str = str(datetime_value).strip()
            
            for fmt in formats:
                try:
                    datetime.strptime(datetime_str, fmt)
                    return True
                except ValueError:
                    continue
            
            return False
            
        except Exception:
            return False


class ValidationError(Exception):
    """
    Exceção customizada para erros de validação.
    """
    pass


class ValidationResult:
    """
    Resultado de uma validação com detalhes.
    """
    
    def __init__(self, is_valid: bool, errors: List[str] = None, 
                 warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str):
        """Adiciona um erro ao resultado."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Adiciona um aviso ao resultado."""
        self.warnings.append(warning)
    
    def __str__(self):
        return f"ValidationResult(valid={self.is_valid}, errors={len(self.errors)}, warnings={len(self.warnings)})"


# Instância global do validador
glpi_validator = GLPIDataValidator()