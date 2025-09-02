#!/usr/bin/env python3
"""Versão minimal do app Flask para debug."""

import logging
import os
import sys
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from flask import Flask, jsonify
from flask_cors import CORS
from config.settings import Config

def create_app():
    """Factory function para criar a aplicação Flask."""
    app = Flask(__name__)
    
    # Configuração básica
    app.config.from_object(Config)
    
    # CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Correlation-ID"]
        }
    })
    
    # Rota de teste simples
    @app.route('/api/test', methods=['GET'])
    def test():
        return jsonify({
            "message": "API Test successful", 
            "status": "ok",
            "version": "minimal"
        })
    
    return app

if __name__ == '__main__':
    # Configurar logging básico
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    app = create_app()
    
    print("Iniciando servidor Flask minimal em 0.0.0.0:5003 (Debug: True)")
    app.run(
        host='0.0.0.0',
        port=5003,
        debug=True,
        use_reloader=False  # Desabilitar reloader para evitar problemas
    )