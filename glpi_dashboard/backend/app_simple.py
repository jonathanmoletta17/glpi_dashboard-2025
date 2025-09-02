#!/usr/bin/env python3
"""
Versão simplificada do app.py para debug
"""

import logging
import os
import sys
from datetime import datetime

from flask import Flask, jsonify
from flask_cors import CORS

# Adiciona o diretório pai ao path para importar módulos
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from config.settings import active_config


def create_simple_app():
    """Cria uma aplicação Flask simplificada para debug"""
    app = Flask(__name__)
    
    # Carrega configurações básicas
    app.config.from_object(active_config)
    
    # Configura CORS básico
    CORS(app)
    
    # Rota de health check simples
    @app.route("/api/health")
    def health_check():
        """Endpoint de health check básico"""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "GLPI Dashboard API - Simple Version"
        })
    
    # Rota raiz
    @app.route("/")
    def root():
        """Rota raiz"""
        return jsonify({
            "message": "GLPI Dashboard API - Simple Version",
            "status": "running",
            "timestamp": datetime.now().isoformat()
        })
    
    return app


if __name__ == "__main__":
    # Configuração para execução direta
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("simple_app")
    
    config_obj = active_config()
    port = config_obj.PORT
    host = "127.0.0.1"  # Forçar localhost
    debug = config_obj.DEBUG
    
    logger.info(f"Iniciando servidor Flask simplificado em {host}:{port} (Debug: {debug})")
    
    app = create_simple_app()
    app.run(host=host, port=port, debug=debug, threaded=True)