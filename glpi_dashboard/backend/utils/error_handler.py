# -*- coding: utf-8 -*-
"""
Sistema robusto de tratamento de erros para o GLPI Dashboard.

Este módulo fornece classes de exceção customizadas e handlers estruturados
para propagar adequadamente os erros para o frontend.
"""

import logging
import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class ErrorSeverity(Enum):
    """Níveis de severidade dos erros."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categorias de erros do sistema."""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    API_CONNECTION = "api_connection"
    DATA_PROCESSING = "data_processing"
    CONFIGURATION = "configuration"
    SYSTEM = "system"
    BUSINESS_LOGIC = "business_logic"


class GLPIError(Exception):
    """Classe base para todas as exceções do GLPI Dashboard."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "GLPI_ERROR",
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.user_message = user_message or self._generate_user_message()
        self.correlation_id = correlation_id
        self.timestamp = datetime.utcnow().isoformat()
        
    def _generate_user_message(self) -> str:
        """Gera uma mensagem amigável para o usuário baseada na categoria."""
        messages = {
            ErrorCategory.VALIDATION: "Dados inválidos fornecidos. Verifique os campos e tente novamente.",
            ErrorCategory.AUTHENTICATION: "Erro de autenticação. Verifique suas credenciais.",
            ErrorCategory.AUTHORIZATION: "Acesso negado. Você não tem permissão para esta operação.",
            ErrorCategory.API_CONNECTION: "Erro de conexão com o servidor GLPI. Tente novamente em alguns instantes.",
            ErrorCategory.DATA_PROCESSING: "Erro no processamento dos dados. Tente novamente.",
            ErrorCategory.CONFIGURATION: "Erro de configuração do sistema. Contate o administrador.",
            ErrorCategory.SYSTEM: "Erro interno do sistema. Contate o suporte técnico.",
            ErrorCategory.BUSINESS_LOGIC: "Operação não permitida pelas regras de negócio."
        }
        return messages.get(self.category, "Erro inesperado. Contate o suporte técnico.")
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o erro para um dicionário serializável."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "user_message": self.user_message,
            "category": self.category.value,
            "severity": self.severity.value,
            "details": self.details,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp
        }


class GLPIValidationError(GLPIError):
    """Erro de validação de dados."""
    
    def __init__(
        self,
        message: str,
        field_errors: Optional[Dict[str, List[str]]] = None,
        **kwargs
    ):
        kwargs.setdefault("error_code", "VALIDATION_ERROR")
        kwargs.setdefault("category", ErrorCategory.VALIDATION)
        kwargs.setdefault("severity", ErrorSeverity.LOW)
        
        details = kwargs.get("details", {})
        if field_errors:
            details["field_errors"] = field_errors
        kwargs["details"] = details
        
        super().__init__(message, **kwargs)


class GLPIAuthenticationError(GLPIError):
    """Erro de autenticação."""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("error_code", "AUTHENTICATION_ERROR")
        kwargs.setdefault("category", ErrorCategory.AUTHENTICATION)
        kwargs.setdefault("severity", ErrorSeverity.HIGH)
        super().__init__(message, **kwargs)


class GLPIAuthorizationError(GLPIError):
    """Erro de autorização."""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("error_code", "AUTHORIZATION_ERROR")
        kwargs.setdefault("category", ErrorCategory.AUTHORIZATION)
        kwargs.setdefault("severity", ErrorSeverity.HIGH)
        super().__init__(message, **kwargs)


class GLPIConnectionError(GLPIError):
    """Erro de conexão com a API GLPI."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, **kwargs):
        kwargs.setdefault("error_code", "CONNECTION_ERROR")
        kwargs.setdefault("category", ErrorCategory.API_CONNECTION)
        kwargs.setdefault("severity", ErrorSeverity.MEDIUM)
        
        details = kwargs.get("details", {})
        if status_code:
            details["status_code"] = status_code
        kwargs["details"] = details
        
        super().__init__(message, **kwargs)


class GLPIDataProcessingError(GLPIError):
    """Erro no processamento de dados."""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("error_code", "DATA_PROCESSING_ERROR")
        kwargs.setdefault("category", ErrorCategory.DATA_PROCESSING)
        kwargs.setdefault("severity", ErrorSeverity.MEDIUM)
        super().__init__(message, **kwargs)


class GLPIConfigurationError(GLPIError):
    """Erro de configuração."""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("error_code", "CONFIGURATION_ERROR")
        kwargs.setdefault("category", ErrorCategory.CONFIGURATION)
        kwargs.setdefault("severity", ErrorSeverity.HIGH)
        super().__init__(message, **kwargs)


class GLPIBusinessLogicError(GLPIError):
    """Erro de regra de negócio."""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("error_code", "BUSINESS_LOGIC_ERROR")
        kwargs.setdefault("category", ErrorCategory.BUSINESS_LOGIC)
        kwargs.setdefault("severity", ErrorSeverity.LOW)
        super().__init__(message, **kwargs)


class ErrorHandler:
    """Handler centralizado para tratamento de erros."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Trata um erro e retorna uma resposta estruturada."""
        
        # Se já é um GLPIError, usar diretamente
        if isinstance(error, GLPIError):
            glpi_error = error
            if correlation_id and not glpi_error.correlation_id:
                glpi_error.correlation_id = correlation_id
        else:
            # Converter exceção genérica para GLPIError
            glpi_error = self._convert_to_glpi_error(error, context, correlation_id)
        
        # Log do erro
        self._log_error(glpi_error, context)
        
        # Retornar resposta estruturada
        return self._create_error_response(glpi_error)
    
    def _convert_to_glpi_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> GLPIError:
        """Converte uma exceção genérica para GLPIError."""
        
        error_type = type(error).__name__
        message = str(error)
        
        # Mapear tipos de exceção conhecidos
        if "connection" in message.lower() or "timeout" in message.lower():
            return GLPIConnectionError(
                message=f"Erro de conexão: {message}",
                details={"original_error": error_type, "context": context},
                correlation_id=correlation_id
            )
        elif "validation" in message.lower() or "invalid" in message.lower():
            return GLPIValidationError(
                message=f"Erro de validação: {message}",
                details={"original_error": error_type, "context": context},
                correlation_id=correlation_id
            )
        elif "auth" in message.lower() or "credential" in message.lower():
            return GLPIAuthenticationError(
                message=f"Erro de autenticação: {message}",
                details={"original_error": error_type, "context": context},
                correlation_id=correlation_id
            )
        else:
            return GLPIError(
                message=f"Erro inesperado: {message}",
                error_code="UNEXPECTED_ERROR",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.HIGH,
                details={"original_error": error_type, "context": context},
                correlation_id=correlation_id
            )
    
    def _log_error(self, error: GLPIError, context: Optional[Dict[str, Any]] = None):
        """Registra o erro no log."""
        
        log_data = {
            "error_code": error.error_code,
            "category": error.category.value,
            "severity": error.severity.value,
            "message": error.message,
            "correlation_id": error.correlation_id,
            "timestamp": error.timestamp,
            "details": error.details
        }
        
        if context:
            log_data["context"] = context
        
        # Escolher nível de log baseado na severidade
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"CRITICAL ERROR: {error.message}", extra=log_data)
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(f"HIGH SEVERITY ERROR: {error.message}", extra=log_data)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"MEDIUM SEVERITY ERROR: {error.message}", extra=log_data)
        else:
            self.logger.info(f"LOW SEVERITY ERROR: {error.message}", extra=log_data)
    
    def _create_error_response(self, error: GLPIError) -> Dict[str, Any]:
        """Cria uma resposta de erro estruturada para o frontend."""
        
        response = {
            "success": False,
            "error": error.to_dict(),
            "data": None
        }
        
        # Adicionar stack trace apenas para erros críticos em desenvolvimento
        if error.severity == ErrorSeverity.CRITICAL:
            response["error"]["stack_trace"] = traceback.format_exc()
        
        return response
    
    def create_success_response(
        self,
        data: Any,
        message: str = "Operação realizada com sucesso",
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Cria uma resposta de sucesso estruturada."""
        
        return {
            "success": True,
            "message": message,
            "data": data,
            "correlation_id": correlation_id,
            "timestamp": datetime.utcnow().isoformat()
        }


# Instância global do handler de erros
error_handler = ErrorHandler()


def handle_glpi_error(func):
    """Decorator para tratamento automático de erros em funções."""
    
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            correlation_id = kwargs.get('correlation_id')
            context = {
                'function': func.__name__,
                'args': str(args)[:200],  # Limitar tamanho
                'kwargs': {k: str(v)[:100] for k, v in kwargs.items()}  # Limitar tamanho
            }
            return error_handler.handle_error(e, context, correlation_id)
    
    return wrapper


def handle_async_glpi_error(func):
    """Decorator para tratamento automático de erros em funções assíncronas."""
    
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            correlation_id = kwargs.get('correlation_id')
            context = {
                'function': func.__name__,
                'args': str(args)[:200],  # Limitar tamanho
                'kwargs': {k: str(v)[:100] for k, v in kwargs.items()}  # Limitar tamanho
            }
            return error_handler.handle_error(e, context, correlation_id)
    
    return wrapper