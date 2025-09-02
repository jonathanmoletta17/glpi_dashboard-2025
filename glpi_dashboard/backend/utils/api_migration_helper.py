import logging
from typing import Dict, Any, List, Optional
from functools import wraps
from flask import jsonify, g
from .api_response_standardizer import APIResponseStandardizer

logger = logging.getLogger("api_migration_helper")


class APIMigrationHelper:
    """Helper para migração gradual das APIs para o novo padrão de resposta"""
    
    @staticmethod
    def migrate_technicians_response(technicians_data: List[Dict], total_count: int = None, filters: Dict = None) -> Dict[str, Any]:
        """Migra resposta de técnicos para o novo padrão"""
        try:
            return APIResponseStandardizer.standardize_list_response(
                items=technicians_data,
                total_count=total_count,
                filters=filters,
                correlation_id=getattr(g, 'correlation_id', None)
            )
        except Exception as e:
            logger.error(f"Erro ao migrar resposta de técnicos: {e}")
            return APIResponseStandardizer.error_response(
                message="Erro ao processar lista de técnicos",
                errors=[str(e)],
                correlation_id=getattr(g, 'correlation_id', None)
            )
    
    @staticmethod
    def migrate_ranking_response(ranking_data: List[Dict], filters: Dict = None) -> Dict[str, Any]:
        """Migra resposta de ranking para o novo padrão"""
        try:
            return APIResponseStandardizer.standardize_list_response(
                items=ranking_data,
                filters=filters,
                correlation_id=getattr(g, 'correlation_id', None)
            )
        except Exception as e:
            logger.error(f"Erro ao migrar resposta de ranking: {e}")
            return APIResponseStandardizer.error_response(
                message="Erro ao processar ranking de técnicos",
                errors=[str(e)],
                correlation_id=getattr(g, 'correlation_id', None)
            )
    
    @staticmethod
    def migrate_tickets_response(tickets_data: List[Dict], filters: Dict = None) -> Dict[str, Any]:
        """Migra resposta de tickets para o novo padrão"""
        try:
            return APIResponseStandardizer.standardize_list_response(
                items=tickets_data,
                filters=filters,
                correlation_id=getattr(g, 'correlation_id', None)
            )
        except Exception as e:
            logger.error(f"Erro ao migrar resposta de tickets: {e}")
            return APIResponseStandardizer.error_response(
                message="Erro ao processar lista de tickets",
                errors=[str(e)],
                correlation_id=getattr(g, 'correlation_id', None)
            )
    
    @staticmethod
    def migrate_alerts_response(alerts_data: List[Dict]) -> Dict[str, Any]:
        """Migra resposta de alertas para o novo padrão"""
        try:
            return APIResponseStandardizer.standardize_list_response(
                items=alerts_data,
                correlation_id=getattr(g, 'correlation_id', None)
            )
        except Exception as e:
            logger.error(f"Erro ao migrar resposta de alertas: {e}")
            return APIResponseStandardizer.error_response(
                message="Erro ao processar alertas do sistema",
                errors=[str(e)],
                correlation_id=getattr(g, 'correlation_id', None)
            )
    
    @staticmethod
    def migrate_status_response(status_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migra resposta de status para o novo padrão"""
        try:
            return APIResponseStandardizer.standardize_single_item_response(
                item=status_data,
                item_type="system_status",
                correlation_id=getattr(g, 'correlation_id', None)
            )
        except Exception as e:
            logger.error(f"Erro ao migrar resposta de status: {e}")
            return APIResponseStandardizer.error_response(
                message="Erro ao processar status do sistema",
                errors=[str(e)],
                correlation_id=getattr(g, 'correlation_id', None)
            )
    
    @staticmethod
    def migrate_performance_response(performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migra resposta de performance para o novo padrão"""
        try:
            return APIResponseStandardizer.standardize_single_item_response(
                item=performance_data,
                item_type="performance_stats",
                correlation_id=getattr(g, 'correlation_id', None)
            )
        except Exception as e:
            logger.error(f"Erro ao migrar resposta de performance: {e}")
            return APIResponseStandardizer.error_response(
                message="Erro ao processar estatísticas de performance",
                errors=[str(e)],
                correlation_id=getattr(g, 'correlation_id', None)
            )
    
    @staticmethod
    def migrate_config_response(config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migra resposta de configuração para o novo padrão"""
        try:
            return APIResponseStandardizer.standardize_single_item_response(
                item=config_data,
                item_type="system_config",
                correlation_id=getattr(g, 'correlation_id', None)
            )
        except Exception as e:
            logger.error(f"Erro ao migrar resposta de configuração: {e}")
            return APIResponseStandardizer.error_response(
                message="Erro ao processar configuração do sistema",
                errors=[str(e)],
                correlation_id=getattr(g, 'correlation_id', None)
            )


def migrate_api_response(response_type: str):
    """Decorador para migração automática de respostas da API"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                # Se já é uma resposta Flask padronizada, retornar como está
                if hasattr(result, 'status_code'):
                    return result
                
                # Se é um tuple (data, status_code), extrair dados
                if isinstance(result, tuple) and len(result) == 2:
                    data, status_code = result
                    if isinstance(data, dict) and 'success' in data:
                        return jsonify(data), status_code
                
                # Aplicar migração baseada no tipo de resposta
                if isinstance(result, dict):
                    if response_type == "technicians":
                        technicians = result.get('technicians', [])
                        total_count = result.get('total_count')
                        filters = result.get('filters_applied')
                        migrated = APIMigrationHelper.migrate_technicians_response(
                            technicians, total_count, filters
                        )
                        return jsonify(migrated)
                    
                    elif response_type == "ranking":
                        ranking = result.get('ranking', result.get('data', []))
                        filters = result.get('filters_applied')
                        migrated = APIMigrationHelper.migrate_ranking_response(ranking, filters)
                        return jsonify(migrated)
                    
                    elif response_type == "tickets":
                        tickets = result.get('tickets', result.get('data', []))
                        filters = result.get('filters_applied')
                        migrated = APIMigrationHelper.migrate_tickets_response(tickets, filters)
                        return jsonify(migrated)
                    
                    elif response_type == "alerts":
                        alerts = result.get('alerts', result.get('data', []))
                        migrated = APIMigrationHelper.migrate_alerts_response(alerts)
                        return jsonify(migrated)
                    
                    elif response_type == "status":
                        migrated = APIMigrationHelper.migrate_status_response(result)
                        return jsonify(migrated)
                    
                    elif response_type == "performance":
                        migrated = APIMigrationHelper.migrate_performance_response(result)
                        return jsonify(migrated)
                    
                    elif response_type == "config":
                        migrated = APIMigrationHelper.migrate_config_response(result)
                        return jsonify(migrated)
                
                return result
                
            except Exception as e:
                logger.error(f"Erro na migração da API ({response_type}): {e}")
                error_response = APIResponseStandardizer.error_response(
                    message="Erro interno do servidor",
                    errors=[str(e)],
                    correlation_id=getattr(g, 'correlation_id', None)
                )
                return jsonify(error_response), 500
        
        return wrapper
    return decorator


# Mapeamento de compatibilidade para estruturas legadas
LEGACY_COMPATIBILITY_MAP = {
    # Mapeamento de campos antigos para novos
    "rawData": "data",
    "by_level": "by_level",
    "general": "metrics",
    "niveis": "by_level",
    "geral": "metrics",
    
    # Mapeamento de status de tickets
    "Novo": "novos",
    "Pendente": "pendentes", 
    "Processando (atribuído)": "progresso",
    "Processando (planejado)": "progresso",
    "Solucionado": "resolvidos",
    "Fechado": "resolvidos"
}


def apply_legacy_compatibility(data: Dict[str, Any]) -> Dict[str, Any]:
    """Aplica mapeamento de compatibilidade para estruturas legadas"""
    try:
        if not isinstance(data, dict):
            return data
        
        # Criar cópia para não modificar o original
        compatible_data = data.copy()
        
        # Adicionar campos legados se não existirem
        if "data" in compatible_data and "rawData" not in compatible_data:
            compatible_data["rawData"] = compatible_data["data"]
        
        if "by_level" in compatible_data and "niveis" not in compatible_data:
            compatible_data["niveis"] = compatible_data["by_level"]
        
        if "metrics" in compatible_data and "general" not in compatible_data:
            compatible_data["general"] = compatible_data["metrics"]
        
        return compatible_data
        
    except Exception as e:
        logger.error(f"Erro ao aplicar compatibilidade legada: {e}")
        return data