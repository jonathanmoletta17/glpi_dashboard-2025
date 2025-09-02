#!/usr/bin/env python3
"""
Ponto de entrada principal da aplicação Flask GLPI Dashboard
Consolidado e refatorado para melhor organização e manutenibilidade
"""

import logging
import os
import sys
from typing import Dict, Any

import redis
from flask import Flask
from flask_caching import Cache
from flask_cors import CORS

# Adiciona o diretório pai ao path para importar módulos
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from api.routes import api_bp
from config.settings import active_config
from utils.observability_middleware import setup_observability
from utils.structured_logging import system_logger

# Instância global do cache
cache = Cache()


def _load_app_config(config_obj) -> Dict[str, Any]:
    """Carrega e converte configurações para o Flask"""
    return {
        # Configurações básicas do Flask
        'SECRET_KEY': str(config_obj.SECRET_KEY),
        'DEBUG': bool(config_obj.DEBUG),
        'HOST': str(config_obj.HOST),
        'PORT': int(config_obj.PORT),
        'CORS_ORIGINS': list(config_obj.CORS_ORIGINS) if config_obj.CORS_ORIGINS else ["*"],
        'MAX_CONTENT_LENGTH': int(config_obj.MAX_CONTENT_LENGTH),
        
        # Configurações GLPI
        'GLPI_URL': str(config_obj.GLPI_URL),
        'GLPI_USER_TOKEN': str(config_obj.GLPI_USER_TOKEN) if config_obj.GLPI_USER_TOKEN else "",
        'GLPI_APP_TOKEN': str(config_obj.GLPI_APP_TOKEN) if config_obj.GLPI_APP_TOKEN else "",
        'API_TIMEOUT': int(config_obj.API_TIMEOUT),
        
        # Configurações de cache
        'REDIS_URL': str(config_obj.REDIS_URL),
        'CACHE_TYPE': str(config_obj.CACHE_TYPE),
        'CACHE_DEFAULT_TIMEOUT': int(config_obj.CACHE_DEFAULT_TIMEOUT),
        
        # Configurações de logging e observabilidade
        'LOG_LEVEL': str(config_obj.LOG_LEVEL),
        'PROMETHEUS_GATEWAY_URL': str(config_obj.PROMETHEUS_GATEWAY_URL),
        'PROMETHEUS_JOB_NAME': str(config_obj.PROMETHEUS_JOB_NAME),
    }


def _setup_cache(app: Flask) -> Dict[str, Any]:
    """Configura cache com Redis e fallback para SimpleCache"""
    try:
        # Tenta conectar ao Redis
        redis_client = redis.from_url(
            app.config.get("REDIS_URL", "redis://localhost:6379/0")
        )
        redis_client.ping()  # Testa conexão

        cache_config = {
            "CACHE_TYPE": "RedisCache",
            "CACHE_REDIS_URL": app.config.get(
                "CACHE_REDIS_URL", "redis://localhost:6379/0"
            ),
            "CACHE_DEFAULT_TIMEOUT": app.config.get("CACHE_DEFAULT_TIMEOUT", 300),
            "CACHE_KEY_PREFIX": app.config.get("CACHE_KEY_PREFIX", "glpi_dashboard:"),
        }

        system_logger.log_operation_end(
            "redis_connection",
            success=True,
            redis_url=app.config.get("REDIS_URL", "redis://localhost:6379/0"),
        )
        return cache_config

    except Exception as e:
        # Fallback para cache simples em caso de erro no Redis
        cache_config = {
            "CACHE_TYPE": "SimpleCache",
            "CACHE_DEFAULT_TIMEOUT": app.config.get("CACHE_DEFAULT_TIMEOUT", 300),
        }

        system_logger.log_operation_end(
            "redis_connection_failed",
            success=False,
            error=str(e),
            fallback="SimpleCache",
        )
        return cache_config


def _setup_cors(app: Flask) -> None:
    """Configura CORS para a aplicação"""
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:3000",
                    "http://localhost:3001", 
                    "http://localhost:3002",
                ],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
    )


def _setup_logging(app: Flask) -> None:
    """Configura logging da aplicação"""
    if not app.debug:
        logging.basicConfig(level=logging.INFO)


def create_app(config=None) -> Flask:
    """Cria e configura a aplicação Flask com observabilidade completa"""
    app = Flask(__name__)

    # Carrega configurações
    if config is None:
        config_obj = active_config()
        app_config = _load_app_config(config_obj)
        app.config.update(app_config)
    else:
        app.config.from_object(config)

    # Log início da configuração
    system_logger.log_operation_start(
        "app_initialization",
        environment=app.config.get("ENV", "development"),
        debug=app.config.get("DEBUG", False),
    )

    # Configurar observabilidade ANTES de outros componentes
    observability_config = {
        "structured_logging": True,
        "prometheus_gateway_url": app.config.get("PROMETHEUS_GATEWAY_URL"),
    }
    setup_observability(app, observability_config)

    # Configura cache
    cache_config = _setup_cache(app)
    cache.init_app(app, config=cache_config)

    # Configura CORS
    _setup_cors(app)

    # Configura logging
    _setup_logging(app)

    # Registra blueprints
    app.register_blueprint(api_bp, url_prefix="/api")

    # Log configuração completa
    system_logger.log_operation_end(
        "app_initialization_complete",
        success=True,
        cache_type=cache_config["CACHE_TYPE"],
        cors_enabled=True,
        blueprints_registered=["api"],
    )

    return app


def _get_server_config() -> Dict[str, Any]:
    """Obtém configurações do servidor"""
    config_obj = active_config()
    return {
        'host': str(config_obj.HOST),
        'port': int(config_obj.PORT),
        'debug': bool(config_obj.DEBUG)
    }


def run_server() -> None:
    """Inicia o servidor Flask"""
    logger = logging.getLogger("app")
    server_config = _get_server_config()
    
    logger.info(
        f"Iniciando servidor Flask em {server_config['host']}:{server_config['port']} "
        f"(Debug: {server_config['debug']})"
    )
    
    try:
        app.run(
            host=server_config['host'],
            port=server_config['port'],
            debug=server_config['debug']
        )
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor: {e}")
        raise


# Cria a aplicação
app = create_app()

if __name__ == "__main__":
    run_server()
