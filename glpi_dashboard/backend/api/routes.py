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

from config.settings import active_config
from schemas.dashboard import ApiError, DashboardMetrics
from services.api_service import APIService
from services.glpi_service import GLPIService
from utils.alerting_system import alert_manager
from utils.date_decorators import standard_date_validation
from utils.performance import (
    cache_with_filters,
    extract_filter_params,
    monitor_performance,
    performance_monitor,
)
from services.smart_cache import cache_with_smart_ttl, smart_cache
from utils.prometheus_metrics import monitor_api_endpoint, prometheus_metrics
from utils.response_formatter import ResponseFormatter
from utils.structured_logging import api_logger

# Importar cache do app principal
try:
    from app import cache
except ImportError:
    cache = None

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Inicializa serviços
api_service = APIService()
glpi_service = GLPIService()

# Obtém logger configurado
logger = logging.getLogger("api")

# Cache para métricas do GLPI (evita chamadas frequentes)
_metrics_cache = {"data": None, "timestamp": 0, "ttl": 180, "filters_hash": None}
_ranking_cache = {"data": None, "timestamp": 0, "ttl": 60, "filters_hash": None}
_status_cache = {"data": None, "timestamp": 0, "ttl": 30}

# Cache inteligente será inicializado pelo app.py


# ============================================================================
# ROTAS ESSENCIAIS - HEALTH CHECK
# ============================================================================

@api_bp.route("/health")
def health_check():
    """Health check básico da aplicação"""
    try:
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "GLPI Dashboard API",
        })
    except Exception as e:
        logger.error(f"Erro no health check: {e}", exc_info=True)
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }), 500


@api_bp.route("/health/glpi")
def glpi_health_check():
    """Health check da conexão GLPI"""
    try:
        auth_result = glpi_service._authenticate_with_retry()

        if auth_result:
            return jsonify({
                "glpi_connection": "healthy",
                "timestamp": datetime.now().isoformat(),
                "message": "Conexão GLPI funcionando corretamente",
            })
        else:
            return jsonify({
                "glpi_connection": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "message": "Falha na autenticação GLPI",
            }), 503

    except Exception as e:
        logger.error(f"Erro no health check GLPI: {e}", exc_info=True)
        return jsonify({
            "glpi_connection": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }), 503


# ============================================================================
# ROTAS ESSENCIAIS - MÉTRICAS
# ============================================================================

@api_bp.route("/metrics")
@monitor_api_endpoint("get_metrics")
@monitor_performance
@cache_with_smart_ttl(endpoint_pattern="/metrics", invalidation_patterns=["metrics", "tickets"])
@standard_date_validation(support_predefined=True, log_usage=True)
def get_metrics(validated_start_date=None, validated_end_date=None, validated_filters=None):
    """Endpoint para obter métricas do dashboard do GLPI"""
    from utils.structured_logging import api_logger
    import hashlib
    import json

    correlation_id = api_logger.generate_correlation_id()
    observability_logger = api_logger
    start_time = time.time()

    # Verificar cache baseado nos filtros
    filters_str = json.dumps({
        "start_date": validated_start_date.isoformat() if validated_start_date else None,
        "end_date": validated_end_date.isoformat() if validated_end_date else None,
        "filters": validated_filters or {},
    }, sort_keys=True)
    filters_hash = hashlib.md5(filters_str.encode()).hexdigest()

    current_time = time.time()
    if (_metrics_cache["data"] is not None and
        current_time - _metrics_cache["timestamp"] < _metrics_cache["ttl"] and
        _metrics_cache["filters_hash"] == filters_hash):

        cached_data = _metrics_cache["data"].copy()
        if isinstance(cached_data, dict):
            cached_data["cached"] = True
            cached_data["correlation_id"] = correlation_id

        response_time = (time.time() - start_time) * 1000
        logger.info(f"[{correlation_id}] Métricas retornadas do cache em {response_time:.2f}ms")
        return jsonify(cached_data)

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

        logger.info(f"[{correlation_id}] Buscando métricas do GLPI com filtros: data={start_date} até {end_date}")

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
            "get_metrics", success=True, result_count=1 if metrics_data else 0, duration_ms=response_time
        )

        logger.info(f"[{correlation_id}] Métricas obtidas com sucesso em {response_time:.2f}ms")

        # Verificar performance
        try:
            config_obj = active_config()
            target_p95 = config_obj.PERFORMANCE_TARGET_P95
        except:
            target_p95 = 300
        if response_time > target_p95:
            logger.warning(f"[{correlation_id}] Resposta lenta detectada: {response_time:.2f}ms > {target_p95}ms")

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

        # Salvar no cache
        _metrics_cache["data"] = metrics_data.copy() if isinstance(metrics_data, dict) else metrics_data
        _metrics_cache["timestamp"] = current_time
        _metrics_cache["filters_hash"] = filters_hash

        return jsonify(metrics_data)

    except Exception as e:
        logger.error(f"[{correlation_id}] Erro inesperado ao buscar métricas: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(
            f"Erro interno no servidor: {str(e)}",
            [str(e)],
            correlation_id=correlation_id,
        )
        return jsonify(error_response), 500


@api_bp.route("/metrics/filtered")
@monitor_api_endpoint("get_filtered_metrics")
@monitor_performance
@cache_with_smart_ttl(endpoint_pattern="/metrics/filtered", invalidation_patterns=["metrics", "tickets"])
@standard_date_validation(support_predefined=True, log_usage=True)
def get_filtered_metrics(validated_start_date=None, validated_end_date=None, validated_filters=None):
    """Endpoint para obter métricas filtradas do dashboard do GLPI"""
    from utils.structured_logging import api_logger

    correlation_id = api_logger.generate_correlation_id()
    observability_logger = api_logger
    start_time = time.time()

    try:
        start_date = validated_start_date
        end_date = validated_end_date
        filters = validated_filters or {}

        # Obter parâmetros de filtro
        status = filters.get("status")
        priority = filters.get("priority")
        level = filters.get("level")
        technician = filters.get("technician")
        category = filters.get("category")

        # Log início da operação
        observability_logger.log_operation_start(
            correlation_id=correlation_id,
            operation="get_filtered_metrics",
            filters=filters,
            endpoint="/api/metrics/filtered",
            method="GET",
        )

        logger.info(f"[{correlation_id}] Buscando métricas filtradas do GLPI")

        # Usar método com filtros
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

        # Verificar se houve erro no serviço
        if isinstance(metrics_data, dict) and metrics_data.get("success") is False:
            return jsonify(metrics_data), 500

        if not metrics_data:
            logger.warning("Não foi possível obter métricas filtradas do GLPI")
            error_response = ResponseFormatter.format_error_response(
                "Não foi possível conectar ou obter dados do GLPI", ["Erro de conexão"]
            )
            return jsonify(error_response), 503

        # Log de performance
        response_time = (time.time() - start_time) * 1000
        observability_logger.log_operation_end(
            "get_filtered_metrics", success=True, result_count=1 if metrics_data else 0, duration_ms=response_time
        )

        logger.info(f"[{correlation_id}] Métricas filtradas obtidas com sucesso em {response_time:.2f}ms")

        # Verificar performance
        try:
            config_obj = active_config()
            target_p95 = config_obj.PERFORMANCE_TARGET_P95
        except:
            target_p95 = 300
        if response_time > target_p95:
            logger.warning(f"[{correlation_id}] Resposta lenta detectada: {response_time:.2f}ms > {target_p95}ms")

        # Validar dados com Pydantic
        try:
            if "data" in metrics_data:
                DashboardMetrics(**metrics_data["data"])
        except ValidationError as ve:
            logger.warning(f"[{correlation_id}] Dados não seguem o schema esperado: {ve}")

        # Adicionar correlation_id à resposta
        if isinstance(metrics_data, dict) and "data" in metrics_data:
            metrics_data["correlation_id"] = correlation_id

        return jsonify(metrics_data)

    except Exception as e:
        logger.error(f"[{correlation_id}] Erro inesperado ao buscar métricas filtradas: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(
            f"Erro interno no servidor: {str(e)}",
            [str(e)],
            correlation_id=correlation_id,
        )
        return jsonify(error_response), 500


# ============================================================================
# ROTAS ESSENCIAIS - TÉCNICOS
# ============================================================================

@api_bp.route("/technicians")
@monitor_api_endpoint("get_technicians")
@monitor_performance
@cache_with_smart_ttl(endpoint_pattern="/technicians", invalidation_patterns=["technicians"])
def get_technicians():
    """Endpoint para obter lista de técnicos"""
    from utils.structured_logging import api_logger

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
        technician_ids, technician_names = glpi_service._get_all_technician_ids_and_names(entity_id=entity_id)

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
@cache_with_smart_ttl(endpoint_pattern="/technicians/ranking", invalidation_patterns=["technicians", "tickets"])
@standard_date_validation(support_predefined=True, log_usage=True)
def get_technician_ranking(validated_start_date=None, validated_end_date=None, validated_filters=None):
    """Endpoint para obter ranking de técnicos por nível"""
    from utils.structured_logging import api_logger

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

        # Verificar cache
        current_time = time.time()
        filters_hash = hash(
            str(sorted(filters.items())) + str(start_date) + str(end_date) + str(limit) + str(entity_id)
        )

        if (_ranking_cache["data"] is not None and
            current_time - _ranking_cache["timestamp"] < _ranking_cache["ttl"] and
            _ranking_cache["filters_hash"] == filters_hash):

            cached_data = _ranking_cache["data"].copy()
            cached_data["cached"] = True
            cached_data["correlation_id"] = correlation_id
            return jsonify(cached_data)

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

        logger.debug(f"[{correlation_id}] Buscando ranking de técnicos: dates={start_date}-{end_date}, level={level}")

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
            return jsonify({
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
            })

        # Log de performance
        response_time = (time.time() - start_time) * 1000
        obs_logger.log_operation_end("technician_ranking", success=True, result_count=len(ranking_data), duration_ms=response_time)
        logger.info(f"[{correlation_id}] Ranking obtido: {len(ranking_data)} técnicos em {response_time:.2f}ms")

        # Verificar performance
        try:
            config_obj = active_config()
            target_p95 = config_obj.PERFORMANCE_TARGET_P95
        except:
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

        # Salvar no cache
        _ranking_cache["data"] = response_data.copy()
        _ranking_cache["timestamp"] = current_time
        _ranking_cache["filters_hash"] = filters_hash

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

@api_bp.route("/tickets/new")
@monitor_api_endpoint("get_new_tickets")
@monitor_performance
@cache_with_smart_ttl(endpoint_pattern="/tickets/new", invalidation_patterns=["tickets"])
@standard_date_validation(support_predefined=True, log_usage=True)
def get_new_tickets(validated_start_date=None, validated_end_date=None, validated_filters=None):
    """Endpoint para obter tickets novos"""
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
            return jsonify({
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
            })

        # Log de performance
        response_time = (time.time() - start_time) * 1000
        logger.info(f"Tickets novos obtidos: {len(new_tickets)} tickets em {response_time:.2f}ms")

        # Verificar performance
        try:
            config_obj = active_config()
            target_p95 = config_obj.PERFORMANCE_TARGET_P95
        except Exception:
            target_p95 = 300

        if response_time > target_p95:
            logger.warning(f"Resposta lenta: {response_time:.2f}ms")

        return jsonify({
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
        })

    except Exception as e:
        logger.error(f"Erro inesperado ao buscar tickets novos: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(
            f"Erro interno do servidor: {str(e)}", [str(e)]
        )
        return jsonify(error_response), 500


@api_bp.route("/tickets/<int:ticket_id>")
@monitor_api_endpoint("get_ticket_details")
@monitor_performance
@cache_with_smart_ttl(endpoint_pattern="/tickets/<int:ticket_id>", invalidation_patterns=["tickets"])
def get_ticket_details(ticket_id):
    """Endpoint para obter detalhes de um ticket específico por ID"""
    start_time = time.time()

    try:
        # Validar ID do ticket
        if not ticket_id or ticket_id <= 0:
            logger.warning(f"ID de ticket inválido: {ticket_id}")
            error_response = ResponseFormatter.format_error_response(
                "ID de ticket inválido", ["O ID do ticket deve ser um número positivo"]
            )
            return jsonify(error_response), 400

        logger.debug(f"Buscando detalhes do ticket ID: {ticket_id}")

        # Buscar detalhes do ticket no GLPI
        ticket_details = glpi_service.get_ticket_by_id(ticket_id)

        # Verificar se o ticket foi encontrado
        if ticket_details is None:
            logger.warning(f"Ticket não encontrado: ID {ticket_id}")
            error_response = ResponseFormatter.format_error_response(
                "Ticket não encontrado", [f"Nenhum ticket encontrado com o ID {ticket_id}"]
            )
            return jsonify(error_response), 404

        # Verificar erro de comunicação com GLPI
        if isinstance(ticket_details, dict) and ticket_details.get("error"):
            logger.error(f"Erro na comunicação com GLPI para ticket {ticket_id}: {ticket_details.get('error')}")
            error_response = ResponseFormatter.format_error_response(
                "Erro na comunicação com GLPI", [ticket_details.get("error", "Erro desconhecido")]
            )
            return jsonify(error_response), 503

        # Log de performance
        response_time = (time.time() - start_time) * 1000
        logger.info(f"Detalhes do ticket {ticket_id} obtidos em {response_time:.2f}ms")

        # Verificar performance
        try:
            config_obj = active_config()
            target_p95 = config_obj.PERFORMANCE_TARGET_P95
        except Exception:
            target_p95 = 300

        if response_time > target_p95:
            logger.warning(f"Resposta lenta para ticket {ticket_id}: {response_time:.2f}ms")

        return jsonify({
            "success": True,
            "data": ticket_details,
            "response_time_ms": round(response_time, 2),
            "ticket_id": ticket_id
        })

    except ValueError as e:
        logger.error(f"Erro de validação para ticket {ticket_id}: {e}")
        error_response = ResponseFormatter.format_error_response(
            "Dados inválidos", [str(e)]
        )
        return jsonify(error_response), 400

    except Exception as e:
        logger.error(f"Erro inesperado ao buscar detalhes do ticket {ticket_id}: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(
            f"Erro interno do servidor: {str(e)}", [str(e)]
        )
        return jsonify(error_response), 500


# ============================================================================
# ROTAS ESSENCIAIS - ALERTAS E STATUS
# ============================================================================

@api_bp.route("/alerts")
@monitor_performance
def get_alerts():
    """Endpoint para obter alertas do sistema"""
    start_time = time.time()

    try:
        logger.debug("Verificando alertas do sistema")

        alerts_data = []
        current_time = datetime.now().isoformat() + "Z"

        # Verifica status do GLPI para alertas dinâmicos
        try:
            glpi_status = glpi_service.get_system_status()

            if glpi_status and glpi_status.get("status") == "online":
                alerts_data.append({
                    "id": "system_001",
                    "type": "info",
                    "severity": "low",
                    "title": "Sistema Operacional",
                    "message": "Dashboard funcionando normalmente",
                    "timestamp": current_time,
                    "acknowledged": False,
                })
            else:
                message = glpi_status.get("message", "Conexão indisponível") if glpi_status else "Falha na verificação"
                alerts_data.append({
                    "id": "glpi_connection",
                    "type": "error",
                    "severity": "high",
                    "title": "Conexão GLPI",
                    "message": f"Status do GLPI: {message}",
                    "timestamp": current_time,
                    "acknowledged": False,
                })

        except Exception as glpi_error:
            logger.warning(f"Erro ao verificar status do GLPI: {glpi_error}")
            alerts_data.append({
                "id": "glpi_error",
                "type": "warning",
                "severity": "medium",
                "title": "Verificação GLPI",
                "message": "Não foi possível verificar o status do GLPI",
                "timestamp": current_time,
                "acknowledged": False,
            })

        # Verificar performance do sistema
        try:
            stats = performance_monitor.get_stats()
            avg_response_time = stats.get("avg_response_time", 0)

            try:
                config_obj = active_config()
                target_p95 = config_obj.PERFORMANCE_TARGET_P95
            except:
                target_p95 = 300
            if avg_response_time > target_p95:
                alerts_data.append({
                    "id": "performance_warning",
                    "type": "warning",
                    "severity": "medium",
                    "title": "Performance",
                    "message": f"Tempo de resposta médio elevado: {avg_response_time:.2f}ms",
                    "timestamp": current_time,
                    "acknowledged": False,
                })
        except Exception as perf_error:
            logger.debug(f"Erro ao verificar performance: {perf_error}")

        # Log de performance
        response_time = (time.time() - start_time) * 1000
        logger.debug(f"Alertas obtidos: {len(alerts_data)} alertas em {response_time:.2f}ms")

        return jsonify({
            "success": True,
            "data": alerts_data,
            "response_time_ms": round(response_time, 2),
            "total_alerts": len(alerts_data),
        })

    except Exception as e:
        logger.error(f"Erro inesperado ao buscar alertas: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(
            f"Erro interno do servidor: {str(e)}", [str(e)]
        )
        return jsonify(error_response), 500


@api_bp.route("/cache/stats")
@monitor_api_endpoint("get_cache_stats")
def get_cache_stats():
    """Endpoint para estatísticas de cache e performance"""
    try:
        cache_stats = smart_cache.get_stats()
        performance_stats = performance_monitor.get_stats()

        # Limpa entradas expiradas do cache local
        expired_cleaned = smart_cache.clear_expired()
        if expired_cleaned > 0:
            logger.info(f"Limpas {expired_cleaned} entradas expiradas do cache")

        return jsonify({
            "cache": cache_stats,
            "performance": performance_stats,
            "expired_cleaned": expired_cleaned,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de cache: {e}", exc_info=True)
        return jsonify({
            "error": "Erro interno do servidor",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@api_bp.route("/cache/invalidate", methods=["POST"])
@monitor_api_endpoint("invalidate_cache")
def invalidate_cache():
    """Endpoint para invalidação manual de cache"""
    try:
        data = request.get_json() or {}
        pattern = data.get('pattern', '')

        if not pattern:
            return jsonify({
                "error": "Padrão de invalidação é obrigatório",
                "timestamp": datetime.now().isoformat()
            }), 400

        invalidated_count = smart_cache.invalidate_pattern(pattern)

        return jsonify({
            "message": f"Cache invalidado com sucesso",
            "pattern": pattern,
            "invalidated_count": invalidated_count,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Erro ao invalidar cache: {e}", exc_info=True)
        return jsonify({
            "error": "Erro interno do servidor",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@api_bp.route("/filter-types")
@monitor_api_endpoint("get_filter_types")
@monitor_performance
@cache_with_smart_ttl(endpoint_pattern="/filter-types", invalidation_patterns=["filter-types"])
def get_filter_types():
    """Endpoint para obter tipos de filtro disponíveis"""
    from utils.structured_logging import api_logger

    start_time = time.time()
    correlation_id = api_logger.generate_correlation_id()

    try:
        # Tipos de filtro padrão disponíveis no sistema
        filter_types = {
            "date_filters": [
                {"id": "creation", "name": "Data de Criação", "description": "Filtrar por data de criação do ticket"},
                {"id": "modification", "name": "Data de Modificação", "description": "Filtrar por data de última modificação"}
            ],
            "status_filters": [
                {"id": "new", "name": "Novo", "value": 1},
                {"id": "assigned", "name": "Atribuído", "value": 2},
                {"id": "planned", "name": "Planejado", "value": 3},
                {"id": "waiting", "name": "Aguardando", "value": 4},
                {"id": "solved", "name": "Resolvido", "value": 5},
                {"id": "closed", "name": "Fechado", "value": 6}
            ],
            "priority_filters": [
                {"id": "very_low", "name": "Muito Baixa", "value": 1},
                {"id": "low", "name": "Baixa", "value": 2},
                {"id": "medium", "name": "Média", "value": 3},
                {"id": "high", "name": "Alta", "value": 4},
                {"id": "very_high", "name": "Muito Alta", "value": 5},
                {"id": "major", "name": "Crítica", "value": 6}
            ],
            "level_filters": [
                {"id": "1", "name": "Nível 1", "description": "Suporte básico"},
                {"id": "2", "name": "Nível 2", "description": "Suporte intermediário"},
                {"id": "3", "name": "Nível 3", "description": "Suporte avançado"}
            ]
        }

        response_time = (time.time() - start_time) * 1000

        logger.info(f"[{correlation_id}] Tipos de filtro obtidos em {response_time:.2f}ms")

        return jsonify({
            "success": True,
            "data": filter_types,
            "response_time_ms": round(response_time, 2),
            "correlation_id": correlation_id,
            "cached": False
        })

    except Exception as e:
        logger.error(f"Erro ao buscar tipos de filtro: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(
            f"Erro interno do servidor: {str(e)}", [str(e)]
        )
        return jsonify(error_response), 500


@api_bp.route("/status")
def get_status():
    """Endpoint para verificar status do sistema"""
    start_time = time.time()

    try:
        current_time_unix = time.time()

        # Verificar cache completo da resposta primeiro
        response_cache_valid = (
            _status_cache["data"] is not None and
            (current_time_unix - _status_cache["timestamp"]) < _status_cache["ttl"]
        )

        if response_cache_valid:
            cached_response = _status_cache["data"].copy()
            response_time = (time.time() - start_time) * 1000
            cached_response["response_time_ms"] = round(response_time, 2)
            return jsonify(cached_response)

        # Verificação simplificada do GLPI
        try:
            import requests

            glpi_start = time.time()
            response = requests.get(f"{active_config().GLPI_URL}/apirest.php", timeout=1)
            glpi_response_time = (time.time() - glpi_start) * 1000

            if response.status_code == 200:
                glpi_info = {
                    "status": "online",
                    "message": "GLPI acessível",
                    "response_time": round(glpi_response_time, 2),
                }
            else:
                glpi_info = {
                    "status": "error",
                    "message": f"GLPI respondeu com status {response.status_code}",
                    "response_time": round(glpi_response_time, 2),
                }

        except Exception as glpi_error:
            glpi_info = {
                "status": "offline",
                "message": f"GLPI inacessível: {str(glpi_error)}",
                "response_time": 0,
            }

        # Dados do status do sistema
        current_time = datetime.now().isoformat()
        status_data = {
            "api": "online",
            "glpi": glpi_info["status"],
            "glpi_message": glpi_info["message"],
            "glpi_response_time": glpi_info["response_time"],
            "last_update": current_time,
            "version": "1.0.0",
            "uptime": "Sistema operacional",
            "cached": response_cache_valid,
        }

        # Determinar status geral do sistema
        overall_status = "healthy" if glpi_info["status"] == "online" else "degraded"

        response_time = (time.time() - start_time) * 1000

        response_data = {
            "success": True,
            "data": status_data,
            "overall_status": overall_status,
            "response_time_ms": round(response_time, 2),
        }

        # Cache da resposta completa
        _status_cache["data"] = response_data
        _status_cache["timestamp"] = current_time_unix

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Erro inesperado ao verificar status: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(
            f"Erro interno do servidor: {str(e)}", [str(e)]
        )
        return jsonify(error_response), 500
