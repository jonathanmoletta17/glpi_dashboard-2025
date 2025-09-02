# -*- coding: utf-8 -*-
"""
Utilitários de segurança para o sistema GLPI Dashboard

Este módulo fornece funcionalidades para:
- Mascaramento de dados sensíveis em logs
- Validação de entrada segura
- Sanitização de dados
- Detecção de tentativas de injeção
"""

import re
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote, unquote


class SecurityUtils:
    """Utilitários de segurança para proteção de dados sensíveis"""
    
    # Padrões para identificar dados sensíveis
    SENSITIVE_PATTERNS = {
        'token': re.compile(r'(token|key|secret|password|auth)', re.IGNORECASE),
        'session': re.compile(r'(session|sid|sessionid)', re.IGNORECASE),
        'credential': re.compile(r'(credential|cred|pass|pwd)', re.IGNORECASE),
        'api_key': re.compile(r'(api[_-]?key|apikey)', re.IGNORECASE)
    }
    
    # Padrões de injeção maliciosa
    INJECTION_PATTERNS = {
        'sql': re.compile(r'(union|select|insert|update|delete|drop|create|alter|exec|execute)', re.IGNORECASE),
        'xss': re.compile(r'(<script|javascript:|on\w+\s*=)', re.IGNORECASE),
        'path_traversal': re.compile(r'(\.\./|\.\.\\|%2e%2e%2f|%2e%2e%5c)', re.IGNORECASE),
        'command_injection': re.compile(r'(;|\||&|`|\$\(|\${)', re.IGNORECASE)
    }
    
    @staticmethod
    def mask_sensitive_data(data: Any, mask_char: str = '*', visible_chars: int = 4) -> Any:
        """
        Mascara dados sensíveis em estruturas de dados complexas
        
        Args:
            data: Dados para mascarar (dict, list, str, etc.)
            mask_char: Caractere usado para mascaramento
            visible_chars: Número de caracteres visíveis no início e fim
            
        Returns:
            Dados com informações sensíveis mascaradas
        """
        if isinstance(data, dict):
            return {key: SecurityUtils._mask_dict_value(key, value, mask_char, visible_chars) 
                   for key, value in data.items()}
        elif isinstance(data, list):
            return [SecurityUtils.mask_sensitive_data(item, mask_char, visible_chars) 
                   for item in data]
        elif isinstance(data, str):
            return SecurityUtils._mask_string_if_sensitive(data, mask_char, visible_chars)
        else:
            return data
    
    @staticmethod
    def _mask_dict_value(key: str, value: Any, mask_char: str, visible_chars: int) -> Any:
        """Mascara valor de dicionário se a chave for sensível"""
        if SecurityUtils._is_sensitive_key(key):
            if isinstance(value, str) and len(value) > visible_chars * 2:
                return SecurityUtils._create_masked_string(value, mask_char, visible_chars)
            elif isinstance(value, str):
                return mask_char * len(value)
            else:
                return f"{mask_char * 8}[{type(value).__name__}]"
        else:
            return SecurityUtils.mask_sensitive_data(value, mask_char, visible_chars)
    
    @staticmethod
    def _mask_string_if_sensitive(text: str, mask_char: str, visible_chars: int) -> str:
        """Mascara string se parecer conter dados sensíveis"""
        # Verifica se a string parece ser um token/chave (longa e alfanumérica)
        if len(text) > 20 and re.match(r'^[a-zA-Z0-9+/=_-]+$', text):
            return SecurityUtils._create_masked_string(text, mask_char, visible_chars)
        return text
    
    @staticmethod
    def _is_sensitive_key(key: str) -> bool:
        """Verifica se uma chave contém dados sensíveis"""
        return any(pattern.search(key) for pattern in SecurityUtils.SENSITIVE_PATTERNS.values())
    
    @staticmethod
    def _create_masked_string(text: str, mask_char: str, visible_chars: int) -> str:
        """Cria string mascarada mantendo alguns caracteres visíveis"""
        if len(text) <= visible_chars * 2:
            return mask_char * len(text)
        
        start = text[:visible_chars]
        end = text[-visible_chars:] if visible_chars > 0 else ""
        middle_length = len(text) - (visible_chars * 2)
        middle = mask_char * min(middle_length, 8)  # Limita o tamanho do mascaramento
        
        return f"{start}{middle}{end}"
    
    @staticmethod
    def sanitize_input(data: str, max_length: int = 1000) -> str:
        """
        Sanitiza entrada do usuário removendo caracteres perigosos
        
        Args:
            data: String para sanitizar
            max_length: Comprimento máximo permitido
            
        Returns:
            String sanitizada
            
        Raises:
            ValueError: Se a entrada contém padrões maliciosos
        """
        if not isinstance(data, str):
            raise ValueError("Entrada deve ser uma string")
        
        # Verifica comprimento
        if len(data) > max_length:
            raise ValueError(f"Entrada muito longa (máximo {max_length} caracteres)")
        
        # Detecta padrões de injeção
        SecurityUtils._detect_injection_attempts(data)
        
        # Remove caracteres de controle
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', data)
        
        # Normaliza espaços em branco
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        return sanitized
    
    @staticmethod
    def _detect_injection_attempts(data: str) -> None:
        """Detecta tentativas de injeção maliciosa"""
        for injection_type, pattern in SecurityUtils.INJECTION_PATTERNS.items():
            if pattern.search(data):
                raise ValueError(f"Possível tentativa de {injection_type} detectada")
    
    @staticmethod
    def detect_injection_attempts(data: str) -> bool:
        """Detecta tentativas de injeção maliciosa (versão pública que retorna bool)"""
        try:
            SecurityUtils._detect_injection_attempts(data)
            return False
        except ValueError:
            return True
    
    @staticmethod
    def validate_url_parameter(param: str, allowed_chars: str = r'[a-zA-Z0-9_-]') -> str:
        """
        Valida parâmetro de URL
        
        Args:
            param: Parâmetro para validar
            allowed_chars: Regex de caracteres permitidos
            
        Returns:
            Parâmetro validado
            
        Raises:
            ValueError: Se o parâmetro é inválido
        """
        if not isinstance(param, str):
            raise ValueError("Parâmetro deve ser uma string")
        
        if not re.match(f'^{allowed_chars}+$', param):
            raise ValueError(f"Parâmetro contém caracteres inválidos: {param}")
        
        return param
    
    @staticmethod
    def validate_url_parameters(url: str) -> bool:
        """Valida se a URL contém parâmetros seguros"""
        try:
            # Verificações básicas de segurança na URL
            if any(pattern.search(url) for pattern in SecurityUtils.INJECTION_PATTERNS.values()):
                return False
            return True
        except Exception:
            return False
    
    @staticmethod
    def safe_url_encode(data: str) -> str:
        """Codifica URL de forma segura"""
        return quote(data, safe='')
    
    @staticmethod
    def create_secure_log_entry(message: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Cria entrada de log segura com dados mascarados
        
        Args:
            message: Mensagem do log
            data: Dados adicionais para incluir no log
            
        Returns:
            Dicionário com entrada de log segura
        """
        log_entry = {
            'message': message,
            'timestamp': logging.Formatter().formatTime(logging.LogRecord(
                name='security', level=logging.INFO, pathname='', lineno=0,
                msg='', args=(), exc_info=None
            ))
        }
        
        if data:
            log_entry['data'] = SecurityUtils.mask_sensitive_data(data)
        
        return log_entry


class SecureLogger:
    """Logger que automaticamente mascara dados sensíveis"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def _log_with_masking(self, level: int, message: str, *args, **kwargs):
        """Log com mascaramento automático de dados sensíveis"""
        # Mascara argumentos
        masked_args = tuple(SecurityUtils.mask_sensitive_data(arg) for arg in args)
        
        # Mascara kwargs
        masked_kwargs = {}
        for key, value in kwargs.items():
            if key not in ['exc_info', 'stack_info', 'stacklevel', 'extra']:
                masked_kwargs[key] = SecurityUtils.mask_sensitive_data(value)
            else:
                masked_kwargs[key] = value
        
        self.logger.log(level, message, *masked_args, **masked_kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        self._log_with_masking(logging.DEBUG, message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        self._log_with_masking(logging.INFO, message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        self._log_with_masking(logging.WARNING, message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        self._log_with_masking(logging.ERROR, message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        self._log_with_masking(logging.CRITICAL, message, *args, **kwargs)


def create_secure_logger(logger_name: str) -> SecureLogger:
    """Cria um logger seguro que mascara dados sensíveis automaticamente"""
    return SecureLogger(logging.getLogger(logger_name))