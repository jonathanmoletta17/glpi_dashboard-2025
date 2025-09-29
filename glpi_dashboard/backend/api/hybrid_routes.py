#!/usr/bin/env python3
"""
Rotas específicas para monitoramento da paginação híbrida
"""

import logging
from datetime import datetime
from flask import Blueprint, jsonify

from utils.prometheus_metrics import monitor_api_endpoint
from utils.performance import monitor_performance
from utils.response_formatter import ResponseFormatter

# Blueprint para rotas híbridas
hybrid_bp = Blueprint("hybrid", __name__, url_prefix="/api/hybrid-pagination")

# Logger
logger = logging.getLogger("glpi.api")


@hybrid_bp.route("/stats", methods=["GET"])
@monitor_api_endpoint("hybrid_pagination_stats")
@monitor_performance
def get_hybrid_pagination_stats():
    """Endpoint para monitorar estatísticas da paginação híbrida"""

    try:
        from utils.hybrid_pagination import hybrid_pagination

        stats = hybrid_pagination.get_stats()

        return jsonify({
            "success": True,
            "data": stats,
            "message": "Estatísticas da paginação híbrida",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Erro ao obter stats de paginação híbrida: {e}")
        error_response = ResponseFormatter.format_error_response(
            "Erro interno do servidor", [str(e)]
        )
        return jsonify(error_response), 500


@hybrid_bp.route("/technician/<technician_id>", methods=["GET"])
@monitor_api_endpoint("hybrid_pagination_technician")
@monitor_performance
def get_technician_pagination_info(technician_id):
    """Endpoint para obter informações de paginação de um técnico específico"""

    try:
        from utils.hybrid_pagination import hybrid_pagination

        # Buscar dados do técnico no cache
        tech_data = hybrid_pagination.cache_data["technicians"].get(technician_id)

        if not tech_data:
            return jsonify({
                "success": False,
                "message": f"Técnico {technician_id} não encontrado no cache",
                "data": None
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "technician_id": technician_id,
                "name": tech_data.get("name", "N/A"),
                "last_updated": tech_data.get("last_updated"),
                "last_range": tech_data.get("last_range"),
                "last_count": tech_data.get("last_count"),
                "optimal_range": tech_data.get("optimal_range"),
                "fallback_triggered": tech_data.get("fallback_triggered", False),
                "history": tech_data.get("history", [])[-5:]  # Últimas 5 consultas
            },
            "message": f"Informações de paginação para {tech_data.get('name', technician_id)}",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Erro ao obter info de paginação do técnico {technician_id}: {e}")
        error_response = ResponseFormatter.format_error_response(
            "Erro interno do servidor", [str(e)]
        )
        return jsonify(error_response), 500


@hybrid_bp.route("/cleanup", methods=["POST"])
@monitor_api_endpoint("hybrid_pagination_cleanup")
@monitor_performance
def cleanup_hybrid_pagination():
    """Endpoint para limpar entradas antigas do cache"""

    try:
        from utils.hybrid_pagination import hybrid_pagination

        before_count = len(hybrid_pagination.cache_data["technicians"])
        hybrid_pagination.cleanup_old_entries()
        after_count = len(hybrid_pagination.cache_data["technicians"])

        removed_count = before_count - after_count

        return jsonify({
            "success": True,
            "data": {
                "before_count": before_count,
                "after_count": after_count,
                "removed_count": removed_count
            },
            "message": f"Limpeza concluída: {removed_count} entradas removidas",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Erro na limpeza da paginação híbrida: {e}")
        error_response = ResponseFormatter.format_error_response(
            "Erro interno do servidor", [str(e)]
        )
        return jsonify(error_response), 500
