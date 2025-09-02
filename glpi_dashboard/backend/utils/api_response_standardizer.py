import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from flask import g
from .naming_converter import NamingConverter

logger = logging.getLogger("api_response_standardizer")


class APIResponseStandardizer:
    """Classe para padronização unificada de respostas da API"""
    
    @staticmethod
    def _get_correlation_id() -> Optional[str]:
        """Obtém o correlation_id do contexto Flask"""
        return getattr(g, 'correlation_id', None)
    
    @staticmethod
    def _calculate_execution_time(start_time: Optional[float] = None) -> Optional[float]:
        """Calcula tempo de execução em milissegundos"""
        if start_time is None:
            return None
        return round((time.time() - start_time) * 1000, 2)
    
    @staticmethod
    def _create_base_response(
        success: bool = True,
        message: Optional[str] = None,
        correlation_id: Optional[str] = None,
        execution_time_ms: Optional[float] = None
    ) -> Dict[str, Any]:
        """Cria estrutura base da resposta padronizada"""
        return {
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "correlation_id": correlation_id or APIResponseStandardizer._get_correlation_id(),
            "execution_time_ms": execution_time_ms
        }
    
    @staticmethod
    def standardize_metrics_response(
        raw_data: Dict[str, Any],
        filters: Optional[Dict] = None,
        start_time: Optional[float] = None,
        correlation_id: Optional[str] = None,
        data_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """Padroniza resposta de métricas do dashboard"""
        try:
            execution_time = APIResponseStandardizer._calculate_execution_time(start_time)
            
            # Estrutura padronizada para métricas
            standardized_data = {
                "metrics": {
                    "novos": raw_data.get("novos", 0),
                    "pendentes": raw_data.get("pendentes", 0),
                    "progresso": raw_data.get("progresso", 0),
                    "resolvidos": raw_data.get("resolvidos", 0),
                    "total": raw_data.get("total", 0)
                },
                "by_level": raw_data.get("niveis", {}),
                "metadata": {
                    "filters_applied": filters or {},
                    "data_source": data_source or "glpi_api",
                    "timestamp": datetime.now().isoformat(),
                    "has_filters": bool(filters)
                }
            }
            
            response = APIResponseStandardizer._create_base_response(
                success=True,
                correlation_id=correlation_id,
                execution_time_ms=execution_time
            )
            response["data"] = standardized_data
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao padronizar resposta de métricas: {e}")
            return APIResponseStandardizer.error_response(
                message="Erro ao processar métricas do dashboard",
                errors=[str(e)],
                correlation_id=correlation_id
            )
    
    @staticmethod
    def standardize_list_response(
        items: List[Dict],
        total_count: Optional[int] = None,
        filters: Optional[Dict] = None,
        correlation_id: Optional[str] = None,
        start_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """Padroniza resposta de listas"""
        try:
            execution_time = APIResponseStandardizer._calculate_execution_time(start_time)
            
            # Converter chaves para camelCase se necessário
            normalized_items = []
            for item in items:
                if isinstance(item, dict):
                    normalized_items.append(NamingConverter.convert_dict_keys_to_camel(item))
                else:
                    normalized_items.append(item)
            
            standardized_data = {
                "items": normalized_items,
                "count": len(normalized_items),
                "total_count": total_count or len(normalized_items),
                "metadata": {
                    "filters_applied": filters or {},
                    "has_filters": bool(filters),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            response = APIResponseStandardizer._create_base_response(
                success=True,
                correlation_id=correlation_id,
                execution_time_ms=execution_time
            )
            response["data"] = standardized_data
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao padronizar resposta de lista: {e}")
            return APIResponseStandardizer.error_response(
                message="Erro ao processar lista de dados",
                errors=[str(e)],
                correlation_id=correlation_id
            )
    
    @staticmethod
    def standardize_single_item_response(
        item: Dict[str, Any],
        item_type: Optional[str] = None,
        correlation_id: Optional[str] = None,
        start_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """Padroniza resposta de item único"""
        try:
            execution_time = APIResponseStandardizer._calculate_execution_time(start_time)
            
            # Converter chaves para camelCase se necessário
            normalized_item = item
            if isinstance(item, dict):
                normalized_item = NamingConverter.convert_dict_keys_to_camel(item)
            
            standardized_data = {
                "item": normalized_item,
                "item_type": item_type,
                "metadata": {
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            response = APIResponseStandardizer._create_base_response(
                success=True,
                correlation_id=correlation_id,
                execution_time_ms=execution_time
            )
            response["data"] = standardized_data
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao padronizar resposta de item único: {e}")
            return APIResponseStandardizer.error_response(
                message="Erro ao processar item",
                errors=[str(e)],
                correlation_id=correlation_id
            )
    
    @staticmethod
    def error_response(
        message: str,
        errors: Optional[List[str]] = None,
        error_code: Optional[str] = None,
        correlation_id: Optional[str] = None,
        start_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """Cria resposta padronizada de erro"""
        execution_time = APIResponseStandardizer._calculate_execution_time(start_time)
        
        response = APIResponseStandardizer._create_base_response(
            success=False,
            message=message,
            correlation_id=correlation_id,
            execution_time_ms=execution_time
        )
        
        response.update({
            "data": None,
            "errors": errors or [],
            "error_code": error_code
        })
        
        return response
    
    @staticmethod
    def success_response(
        data: Any = None,
        message: Optional[str] = None,
        correlation_id: Optional[str] = None,
        start_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """Cria resposta padronizada de sucesso"""
        execution_time = APIResponseStandardizer._calculate_execution_time(start_time)
        
        response = APIResponseStandardizer._create_base_response(
            success=True,
            message=message,
            correlation_id=correlation_id,
            execution_time_ms=execution_time
        )
        
        response["data"] = data
        
        return response