#!/usr/bin/env python3
"""
Rotas essenciais da API GLPI Dashboard
Versão limpa e otimizada após refatoração
"""

import logging
import time
from datetime import datetime

from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from schemas.dashboard import DashboardMetrics

from config.settings import active_config

# Removed api_service import - service deleted
from services.glpi_service import GLPIService
from services.simple_dict_cache import cached, simple_cache

# Removed unused import: alerting_system
# Removed date_decorators import - module deleted
from utils.performance import monitor_performance
from utils.response_formatter import ResponseFormatter
from utils.simple_decorators import monitor_api_endpoint
from utils.structured_logging import api_logger

# Importar cache do app principal
try:
    from app import cache
except ImportError:
    cache = None

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Inicializa serviços
glpi_service = GLPIService()

# Obtém logger configurado
logger = logging.getLogger("api")

# Cache para métricas do GLPI (evita chamadas frequentes)
# Cache global removido - usando simple_dict_cache com decorator @cached

# Cache inteligente será inicializado pelo app.py


# ============================================================================
# ROTAS ESSENCIAIS - HEALTH CHECK
# ============================================================================


@api_bp.route("/health")
def health_check():
    """Health check básico da aplicação"""
    try:
        return jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "GLPI Dashboard API",
            }
        )
    except Exception as e:
        logger.error(f"Erro no health check: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e),
                }
            ),
            500,
        )


@api_bp.route("/health/glpi")
def glpi_health_check():
    """Health check da conexão GLPI"""
    try:
        auth_result = glpi_service._authenticate_with_retry()

        if auth_result:
            return jsonify(
                {
                    "glpi_connection": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "message": "Conexão GLPI funcionando corretamente",
                }
            )
        else:
            return (
                jsonify(
                    {
                        "glpi_connection": "unhealthy",
                        "timestamp": datetime.now().isoformat(),
                        "message": "Falha na autenticação GLPI",
                    }
                ),
                503,
            )

    except Exception as e:
        logger.error(f"Erro no health check GLPI: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "glpi_connection": "unhealthy",
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e),
                }
            ),
            503,
        )


# ============================================================================
# ROTAS ESSENCIAIS - MÉTRICAS
# ============================================================================


@api_bp.route("/metrics")
@monitor_api_endpoint("get_metrics")
@monitor_performance
@cached(ttl=300)
def get_metrics(validated_start_date=None, validated_end_date=None, validated_filters=None):
    """Endpoint para obter métricas do dashboard do GLPI"""
    import hashlib
    import json

    correlation_id = api_logger.generate_correlation_id()
    observability_logger = api_logger
    start_time = time.time()

    # Cache é gerenciado pelo decorator @cached

    try:
        start_date = validated_start_date
        end_date = validated_end_date
        filters = validated_filters or {}

        # Obter parâmetros de filtro
        filter_type = filters.get("filter_type", "creation")
        status = filters.get("status")
        priority = filters.get("priority")
        level = filters.get("level")
        technician = filters.get("technician")
        category = filters.get("category")

        # Log início da operação
        observability_logger.log_operation_start(
            correlation_id=correlation_id,
            operation="get_metrics",
            filters=filters,
            endpoint="/api/metrics",
            method="GET",
        )

        logger.info(
            f"[{correlation_id}] Buscando métricas do GLPI com filtros: data={start_date} até {end_date}"
        )

        # Usar método apropriado baseado nos filtros
        if start_date or end_date:
            if filter_type == "modification":
                metrics_data = glpi_service.get_dashboard_metrics_with_modification_date_filter(
                    start_date=start_date,
                    end_date=end_date,
                    correlation_id=correlation_id,
                )
            else:  # filter_type == 'creation' (padrão)
                metrics_data = glpi_service.get_dashboard_metrics_with_date_filter(
                    start_date=start_date,
                    end_date=end_date,
                    correlation_id=correlation_id,
                )
        elif any([status, priority, level, technician, category]):
            metrics_data = glpi_service.get_dashboard_metrics_with_filters(
                start_date=start_date,
                end_date=end_date,
                status=status,
                priority=priority,
                level=level,
                technician=technician,
                category=category,
                correlation_id=correlation_id,
            )
        else:
            metrics_data = glpi_service.get_dashboard_metrics(correlation_id=correlation_id)

        # Verificar se houve erro no serviço
        if isinstance(metrics_data, dict) and metrics_data.get("success") is False:
            return jsonify(metrics_data), 500

        if not metrics_data:
            logger.warning("Não foi possível obter métricas do GLPI, usando dados de fallback.")
            error_response = ResponseFormatter.format_error_response(
                "Não foi possível conectar ou obter dados do GLPI", ["Erro de conexão"]
            )
            return jsonify(error_response), 503

        # Log de performance
        response_time = (time.time() - start_time) * 1000
        observability_logger.log_operation_end(
            "get_metrics",
            success=True,
            result_count=1 if metrics_data else 0,
            duration_ms=response_time,
        )

        logger.info(f"[{correlation_id}] Métricas obtidas com sucesso em {response_time:.2f}ms")

        # Verificar performance
        try:
            config_obj = active_config()
            target_p95 = config_obj.PERFORMANCE_TARGET_P95
        except (AttributeError, ImportError):
            target_p95 = 300
        if response_time > target_p95:
            logger.warning(
                f"[{correlation_id}] Resposta lenta detectada: {response_time:.2f}ms > {target_p95}ms"
            )

        # Validar dados com Pydantic
        try:
            if "data" in metrics_data:
                DashboardMetrics(**metrics_data["data"])
        except ValidationError as ve:
            logger.warning(f"[{correlation_id}] Dados não seguem o schema esperado: {ve}")

        # Adicionar correlation_id à resposta
        if isinstance(metrics_data, dict) and "data" in metrics_data:
            metrics_data["correlation_id"] = correlation_id
            metrics_data["cached"] = False

        # Cache é gerenciado automaticamente pelo decorator @cached

        return jsonify(metrics_data)

    except Exception as e:
        logger.error(f"[{correlation_id}] Erro inesperado ao buscar métricas: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(
            f"Erro interno no servidor: {str(e)}",
            [str(e)],
            correlation_id=correlation_id,
        )
        return jsonify(error_response), 500


# Endpoint /metrics/filtered removido - funcionalidade consolidada em /metrics


# ============================================================================
# ROTAS ESSENCIAIS - TÉCNICOS
# ============================================================================


@api_bp.route("/technicians")
@monitor_api_endpoint("get_technicians")
@monitor_performance
@cached(ttl=300)
def get_technicians():
    """Endpoint para obter lista de técnicos"""
    start_time = time.time()
    obs_logger = api_logger
    correlation_id = obs_logger.generate_correlation_id()

    try:
        # Obter parâmetros de filtro
        entity_id = request.args.get("entity_id")
        limit = request.args.get("limit", 100)

        # Validar limite
        try:
            limit = int(limit)
            limit = max(1, min(limit, 500))
        except (ValueError, TypeError):
            limit = 100

        # Validar entity_id
        if entity_id:
            try:
                entity_id = int(entity_id)
            except (ValueError, TypeError):
                entity_id = None

        # Buscar técnicos
        technician_ids, technician_names = glpi_service._get_all_technician_ids_and_names(
            entity_id=entity_id
        )

        # Converter para formato de lista
        technicians = []
        for tech_id in technician_ids:
            tech_name = technician_names.get(tech_id, f"Técnico {tech_id}")
            technicians.append({"id": tech_id, "name": tech_name})

        # Limitar resultados
        if len(technicians) > limit:
            technicians = technicians[:limit]

        # Formatar resposta
        response_data = {
            "success": True,
            "technicians": technicians,
            "total_count": len(technicians),
            "filters_applied": {"entity_id": entity_id, "limit": limit},
            "response_time_ms": round((time.time() - start_time) * 1000, 2),
            "correlation_id": correlation_id,
            "cached": False,
        }

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Erro ao buscar técnicos: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(
            f"Erro interno do servidor: {str(e)}", [str(e)]
        )
        return jsonify(error_response), 500


@api_bp.route("/technicians/ranking")
@monitor_api_endpoint("get_technician_ranking")
@monitor_performance
@cached(ttl=300)
def get_technician_ranking(
    validated_start_date=None, validated_end_date=None, validated_filters=None
):
    """Endpoint para obter ranking de técnicos por nível"""
    start_time = time.time()
    obs_logger = api_logger
    correlation_id = obs_logger.generate_correlation_id()

    try:
        start_date = validated_start_date
        end_date = validated_end_date
        filters = validated_filters or {}

        # Obter parâmetros de filtro
        level = filters.get("level")
        limit = filters.get("limit", 100)
        entity_id = filters.get("entity_id")

        # Validar limite
        try:
            limit = int(limit)
            limit = max(1, min(limit, 200))
        except (ValueError, TypeError):
            limit = 100

        # Cache é gerenciado pelo decorator @cached

        # Log início do pipeline
        obs_logger.log_operation_start(
            "technician_ranking",
            correlation_id=correlation_id,
            start_date=start_date,
            end_date=end_date,
            level=level,
            limit=limit,
            entity_id=entity_id,
        )

        logger.debug(
            f"[{correlation_id}] Buscando ranking de técnicos: dates={start_date}-{end_date}, level={level}"
        )

        # Buscar ranking com ou sem filtros
        if any([start_date, end_date, level, entity_id]):
            ranking_data = glpi_service.get_technician_ranking_with_filters(
                start_date=start_date,
                end_date=end_date,
                level=level,
                limit=limit,
                correlation_id=correlation_id,
                entity_id=entity_id,
            )
        else:
            ranking_data = glpi_service.get_technician_ranking(limit=limit)

        # Verificar resultado
        if ranking_data is None:
            logger.error("Falha na comunicação com o GLPI")
            error_response = ResponseFormatter.format_error_response(
                "Não foi possível conectar ao GLPI", ["Erro de conexão"]
            )
            return jsonify(error_response), 503

        if not ranking_data:
            logger.info(f"[{correlation_id}] Nenhum técnico encontrado com os filtros aplicados")
            return jsonify(
                {
                    "success": True,
                    "data": [],
                    "message": "Nenhum técnico encontrado com os filtros aplicados",
                    "correlation_id": correlation_id,
                    "filters_applied": {
                        "start_date": start_date,
                        "end_date": end_date,
                        "level": level,
                        "limit": limit,
                        "entity_id": entity_id,
                    },
                }
            )

        # Log de performance
        response_time = (time.time() - start_time) * 1000
        obs_logger.log_operation_end(
            "technician_ranking",
            success=True,
            result_count=len(ranking_data),
            duration_ms=response_time,
        )
        logger.info(
            f"[{correlation_id}] Ranking obtido: {len(ranking_data)} técnicos em {response_time:.2f}ms"
        )

        # Verificar performance
        try:
            config_obj = active_config()
            target_p95 = config_obj.PERFORMANCE_TARGET_P95
        except (AttributeError, ImportError):
            target_p95 = 300
        if response_time > target_p95:
            logger.warning(f"[{correlation_id}] Resposta lenta: {response_time:.2f}ms")

        # Preparar dados de resposta
        response_data = {
            "success": True,
            "data": ranking_data,
            "response_time_ms": round(response_time, 2),
            "correlation_id": correlation_id,
            "cached": False,
            "filters_applied": {
                "start_date": start_date,
                "end_date": end_date,
                "level": level,
                "limit": limit,
                "entity_id": entity_id,
            },
        }

        # Cache é gerenciado automaticamente pelo decorator @cached

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Erro inesperado ao buscar ranking de técnicos: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(
            f"Erro interno do servidor: {str(e)}", [str(e)]
        )
        return jsonify(error_response), 500


# ============================================================================
# ROTAS ESSENCIAIS - TICKETS
# ============================================================================


@api_bp.route("/tickets/recent")
@monitor_api_endpoint("get_new_tickets")
@monitor_performance
@cached(ttl=300)
def get_new_tickets(validated_start_date=None, validated_end_date=None, validated_filters=None):
    """Endpoint para obter tickets recentes"""
    start_time = time.time()

    try:
        start_date = validated_start_date
        end_date = validated_end_date
        filters = validated_filters or {}

        # Obter parâmetros de filtro
        limit = filters.get("limit", 5) or 5
        priority = filters.get("priority")
        category = filters.get("category")
        technician = filters.get("technician")

        # Validar limite
        try:
            limit = int(limit)
            limit = max(1, min(limit, 50))
        except (ValueError, TypeError):
            limit = 5

        logger.debug(f"Buscando {limit} tickets novos com filtros")

        # Buscar tickets novos com ou sem filtros
        if any([priority, category, technician, start_date, end_date]):
            new_tickets = glpi_service.get_new_tickets_with_filters(
                limit=limit,
                priority=priority,
                category=category,
                technician=technician,
                start_date=start_date,
                end_date=end_date,
            )
        else:
            new_tickets = glpi_service.get_new_tickets(limit)

        # Verificar resultado
        if new_tickets is None:
            logger.error("Falha na comunicação com o GLPI")
            error_response = ResponseFormatter.format_error_response(
                "Não foi possível conectar ao GLPI", ["Erro de conexão"]
            )
            return jsonify(error_response), 503

        if not new_tickets:
            logger.info("Nenhum ticket novo encontrado com os filtros aplicados")
            return jsonify(
                {
                    "success": True,
                    "data": [],
                    "message": "Nenhum ticket novo encontrado com os filtros aplicados",
                    "filters_applied": {
                        "limit": limit,
                        "priority": priority,
                        "category": category,
                        "technician": technician,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                }
            )

        # Log de performance
        response_time = (time.time() - start_time) * 1000
        logger.info(f"Tickets novos obtidos: {len(new_tickets)} tickets em {response_time:.2f}ms")

        # Verificar performance
        try:
            config_obj = active_config()
            target_p95 = config_obj.PERFORMANCE_TARGET_P95
        except (AttributeError, ImportError):
            target_p95 = 300

        if response_time > target_p95:
            logger.warning(f"Resposta lenta: {response_time:.2f}ms")

        return jsonify(
            {
                "success": True,
                "data": new_tickets,
                "response_time_ms": round(response_time, 2),
                "filters_applied": {
                    "limit": limit,
                    "priority": priority,
                    "category": category,
                    "technician": technician,
                    "start_date": start_date,
                    "end_date": end_date,
                },
            }
        )

    except Exception as e:
        logger.error(f"Erro inesperado ao buscar tickets novos: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(
            f"Erro interno do servidor: {str(e)}", [str(e)]
        )
        return jsonify(error_response), 500


# Endpoint /tickets/<int:ticket_id> removido - não essencial para funcionalidade básica


# ============================================================================
# ROTAS ESSENCIAIS - ALERTAS E STATUS
# ============================================================================

# Alerts endpoint removed - not essential for core functionality


# Cache management endpoints removed - not essential for core functionality


# Filter types endpoint removed - not essential for core functionality


# Endpoint /status removido - funcionalidade consolidada em /health e /health/glpi
