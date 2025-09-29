#!/usr/bin/env python3
"""
Serviço de API para o GLPI Dashboard
Centraliza operações de API e integração com serviços externos
"""

import logging
from typing import Any, Dict, List, Optional

from config.settings import active_config
from utils.structured_logging import system_logger


class APIService:
    """Serviço centralizado para operações de API"""

    def __init__(self):
        """Inicializa o serviço de API"""
        self.config = active_config()
        self.logger = logging.getLogger("api_service")
        self._setup_service()

    def _setup_service(self):
        """Configura o serviço de API"""
        try:
            self.api_url = self.config.BACKEND_API_URL
            self.api_key = self.config.API_KEY
            self.timeout = self.config.API_TIMEOUT

            system_logger.log_operation_end(
                "api_service_setup",
                success=True,
                api_url=self.api_url,
                timeout=self.timeout
            )

        except Exception as e:
            system_logger.log_operation_end(
                "api_service_setup",
                success=False,
                error=str(e)
            )
            raise

    def get_service_status(self) -> Dict[str, Any]:
        """Retorna o status do serviço de API"""
        return {
            "status": "active",
            "api_url": self.api_url,
            "timeout": self.timeout,
            "timestamp": system_logger._get_timestamp()
        }

    def validate_api_key(self, api_key: str) -> bool:
        """Valida uma chave de API"""
        if not api_key:
            return False

        # Em produção, implementar validação real
        return api_key == self.api_key

    def format_api_response(self, data: Any, success: bool = True, message: str = None) -> Dict[str, Any]:
        """Formata resposta padrão da API"""
        response = {
            "success": success,
            "timestamp": system_logger._get_timestamp(),
            "data": data
        }

        if message:
            response["message"] = message

        return response

    def handle_api_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        """Trata erros de API de forma padronizada"""
        error_message = str(error)

        system_logger.log_operation_end(
            f"api_error_{operation}",
            success=False,
            error=error_message
        )

        return self.format_api_response(
            data=None,
            success=False,
            message=f"Erro na operação {operation}: {error_message}"
        )

    def log_api_request(self, endpoint: str, method: str = "GET", params: Dict = None):
        """Registra requisições de API"""
        system_logger.log_operation_start(
            f"api_request_{endpoint}",
            method=method,
            endpoint=endpoint,
            params=params or {}
        )

    def get_health_status(self) -> Dict[str, Any]:
        """Retorna status de saúde do serviço"""
        try:
            status = self.get_service_status()
            return {
                "healthy": True,
                "service": "APIService",
                "details": status
            }
        except Exception as e:
            return {
                "healthy": False,
                "service": "APIService",
                "error": str(e)
            }
