"""Configurações centralizadas do projeto com validações robustas"""
import logging
import os
import warnings
from typing import Any, Dict, Optional
from pathlib import Path

from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Importação opcional do YAML
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    warnings.warn("PyYAML não está instalado. Usando apenas variáveis de ambiente.")


class ConfigValidationError(Exception):
    """Exceção para erros de validação de configuração"""

    pass


class Config:
    """Configuração base com validações robustas"""

    def __init__(self):
        """Inicializa e valida as configurações"""
        self._load_yaml_config()
        self._validate_required_configs()
        self._validate_config_values()

    def _load_yaml_config(self):
        """Carrega configurações do arquivo YAML"""
        self.yaml_config = {}

        if not YAML_AVAILABLE:
            warnings.warn("PyYAML não disponível. Usando apenas variáveis de ambiente.")
            return

        try:
            # Caminho para o arquivo de configuração
            config_path = Path(__file__).parent.parent.parent / "config" / "system.yaml"

            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as file:
                    self.yaml_config = yaml.safe_load(file)
            else:
                # Fallback para configurações padrão se arquivo não existir
                warnings.warn(f"Arquivo de configuração não encontrado: {config_path}")
        except Exception as e:
            warnings.warn(f"Erro ao carregar config/system.yaml: {e}")
            self.yaml_config = {}

    def _get_config_value(self, path: str, default=None, env_var=None):
        """Obtém valor de configuração do YAML ou variável de ambiente"""
        # Primeiro tenta variável de ambiente
        if env_var and os.environ.get(env_var):
            return os.environ.get(env_var)

        # Depois tenta YAML
        keys = path.split('.')
        value = self.yaml_config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        # Substitui variáveis de ambiente no valor
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_key = value[2:-1]
            return os.environ.get(env_key, default)

        return value if value is not None else default

    # Flask
    @property
    def SECRET_KEY(self) -> str:
        return self._get_config_value("flask.secret_key", "dev-secret-key-change-in-production", "SECRET_KEY")

    @property
    def DEBUG(self) -> bool:
        return self._get_config_value("flask.debug", False) or os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    @property
    def PORT(self) -> int:
        """Porta do servidor com validação"""
        try:
            port = self._get_config_value("flask.port", 5000, "PORT")
            port = int(port)  # Garantir que é inteiro
            if not (1 <= port <= 65535):
                raise ValueError(f"Porta inválida: {port}")
            return port
        except (ValueError, TypeError) as e:
            raise ConfigValidationError(f"Erro na configuração PORT: {e}")

    @property
    def HOST(self) -> str:
        return self._get_config_value("flask.host", "0.0.0.0", "HOST")

    # GLPI API
    @property
    def GLPI_URL(self) -> str:
        return self._get_config_value("glpi.base_url", "http://10.73.0.79/glpi/apirest.php", "GLPI_URL")

    @property
    def GLPI_USER_TOKEN(self) -> str:
        return self._get_config_value("glpi.user_token", None, "GLPI_USER_TOKEN")

    @property
    def GLPI_APP_TOKEN(self) -> str:
        return self._get_config_value("glpi.app_token", None, "GLPI_APP_TOKEN")

    # Backend API
    @property
    def BACKEND_API_URL(self) -> str:
        return self._get_config_value("api.backend_url", "http://localhost:8000", "BACKEND_API_URL")

    @property
    def API_KEY(self) -> str:
        return self._get_config_value("api.key", "", "API_KEY")

    @property
    def API_TIMEOUT(self) -> int:
        """Timeout da API com validação"""
        try:
            timeout = self._get_config_value("glpi.timeout", 30, "API_TIMEOUT")
            timeout = int(timeout)  # Garantir que é inteiro
            if not (1 <= timeout <= 300):
                raise ValueError(f"Timeout deve estar entre 1 e 300 segundos: {timeout}")
            return timeout
        except (ValueError, TypeError) as e:
            raise ConfigValidationError(f"Erro na configuração API_TIMEOUT: {e}")

    # Observabilidade
    @property
    def PROMETHEUS_GATEWAY_URL(self) -> str:
        return self._get_config_value("observability.prometheus.gateway_url", "http://localhost:9091", "PROMETHEUS_GATEWAY_URL")

    @property
    def PROMETHEUS_JOB_NAME(self) -> str:
        return self._get_config_value("observability.prometheus.job_name", "glpi_dashboard", "PROMETHEUS_JOB_NAME")

    @property
    def STRUCTURED_LOGGING(self) -> bool:
        return self._get_config_value("logging.structured", True) or os.environ.get("STRUCTURED_LOGGING", "True").lower() == "true"

    @property
    def LOG_FILE_PATH(self) -> str:
        return self._get_config_value("logging.file_path", "logs/app.log", "LOG_FILE_PATH")

    @property
    def LOG_MAX_BYTES(self) -> int:
        return self._get_config_value("logging.max_bytes", 10485760, "LOG_MAX_BYTES")

    @property
    def LOG_BACKUP_COUNT(self) -> int:
        return self._get_config_value("logging.backup_count", 5, "LOG_BACKUP_COUNT")

    # Alertas
    @property
    def ALERT_RESPONSE_TIME_THRESHOLD(self) -> float:
        return self._get_config_value("alerts.response_time_threshold", 300, "ALERT_RESPONSE_TIME_THRESHOLD")

    @property
    def ALERT_ERROR_RATE_THRESHOLD(self) -> float:
        return self._get_config_value("alerts.error_rate_threshold", 0.05, "ALERT_ERROR_RATE_THRESHOLD")

    @property
    def ALERT_ZERO_TICKETS_THRESHOLD(self) -> int:
        return self._get_config_value("alerts.zero_tickets_threshold", 60, "ALERT_ZERO_TICKETS_THRESHOLD")

    # Logging
    @property
    def LOG_LEVEL(self) -> str:
        return self._get_config_value("logging.level", "INFO", "LOG_LEVEL")

    @property
    def LOG_FORMAT(self) -> str:
        return self._get_config_value("logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # CORS
    @property
    def CORS_ORIGINS(self) -> list:
        return self._get_config_value("flask.cors_origins", ["*"])

    # Redis Cache
    @property
    def REDIS_URL(self) -> str:
        return self._get_config_value("cache.redis_url", "redis://localhost:6379/0", "REDIS_URL")

    @property
    def CACHE_TYPE(self) -> str:
        return self._get_config_value("cache.type", "RedisCache", "CACHE_TYPE")

    @property
    def CACHE_REDIS_URL(self) -> str:
        return self._get_config_value("cache.redis_url", self.REDIS_URL, "CACHE_REDIS_URL")

    @property
    def CACHE_DEFAULT_TIMEOUT(self) -> int:
        """Timeout do cache com validação"""
        try:
            timeout = self._get_config_value("cache.default_timeout", 300, "CACHE_DEFAULT_TIMEOUT")
            timeout = int(timeout)  # Garantir que é inteiro
            if not (10 <= timeout <= 3600):
                raise ValueError(f"Cache timeout deve estar entre 10 e 3600 segundos: {timeout}")
            return timeout
        except (ValueError, TypeError) as e:
            raise ConfigValidationError(f"Erro na configuração CACHE_DEFAULT_TIMEOUT: {e}")

    @property
    def CACHE_KEY_PREFIX(self) -> str:
        return self._get_config_value("cache.key_prefix", "glpi_dashboard:", "CACHE_KEY_PREFIX")

    # Performance Settings
    @property
    def PERFORMANCE_TARGET_P95(self) -> int:
        """Target de performance P95 com validação"""
        try:
            target = self._get_config_value("performance.target_p95", 1000, "PERFORMANCE_TARGET_P95")
            target = int(target)  # Garantir que é inteiro
            if not (50 <= target <= 10000):
                raise ValueError(f"Performance target deve estar entre 50 e 10000ms: {target}")
            return target
        except (ValueError, TypeError) as e:
            raise ConfigValidationError(f"Erro na configuração PERFORMANCE_TARGET_P95: {e}")

    # Configurações de segurança
    @property
    def MAX_CONTENT_LENGTH(self) -> int:
        """Tamanho máximo de conteúdo"""
        return int(self._get_config_value("flask.max_content_length", 16777216, "MAX_CONTENT_LENGTH"))

    @property
    def RATE_LIMIT_PER_MINUTE(self) -> int:
        """Limite de requisições por minuto"""
        return int(self._get_config_value("performance.rate_limit_per_minute", 100, "RATE_LIMIT_PER_MINUTE"))

    def _validate_required_configs(self) -> None:
        """Valida configurações obrigatórias"""
        required_configs = {
            "GLPI_URL": self.GLPI_URL,
            "GLPI_USER_TOKEN": self.GLPI_USER_TOKEN,
            "GLPI_APP_TOKEN": self.GLPI_APP_TOKEN,
        }

        missing_configs = [key for key, value in required_configs.items() if not value]

        if missing_configs:
            raise ConfigValidationError(
                f"Configurações obrigatórias ausentes: {', '.join(missing_configs)}"
            )

    def _validate_config_values(self) -> None:
        """Valida valores das configurações"""
        # Validar URL do GLPI
        if not self.GLPI_URL.startswith(("http://", "https://")):
            raise ConfigValidationError(
                f"GLPI_URL deve começar com http:// ou https://: {self.GLPI_URL}"
            )

        # Validar nível de log
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.LOG_LEVEL.upper() not in valid_log_levels:
            warnings.warn(f"LOG_LEVEL inválido '{self.LOG_LEVEL}', usando 'INFO'")
            self.LOG_LEVEL = "INFO"

        # Validar chave secreta em produção
        if not self.DEBUG and self.SECRET_KEY == "dev-secret-key-change-in-production":
            raise ConfigValidationError(
                "SECRET_KEY deve ser alterada em ambiente de produção"
            )

    @classmethod
    def configure_logging(cls) -> logging.Logger:
        """Configura o sistema de logging de forma robusta"""
        try:
            config_instance = cls()
            numeric_level = getattr(logging, config_instance.LOG_LEVEL.upper(), None)
            if not isinstance(numeric_level, int):
                numeric_level = logging.INFO

            # Configurar logging básico
            logging.basicConfig(
                level=numeric_level,
                format=config_instance.LOG_FORMAT,
                force=True,  # Força reconfiguração
            )

            # Configurar loggers específicos
            logger = logging.getLogger("api")
            logger.setLevel(numeric_level)

            # Reduzir verbosidade de bibliotecas externas
            logging.getLogger("urllib3").setLevel(logging.WARNING)
            logging.getLogger("requests").setLevel(logging.WARNING)

            return logger

        except Exception as e:
            # Fallback para configuração básica
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
            logger = logging.getLogger("api")
            logger.warning(f"Erro na configuração de logging: {e}")
            return logger

    def get_config_summary(self) -> Dict[str, Any]:
        """Retorna um resumo das configurações (sem dados sensíveis)"""
        return {
            "app_name": self._get_config_value("app.name", "GLPI Dashboard"),
            "app_version": self._get_config_value("app.version", "1.0.0"),
            "environment": self._get_config_value("app.environment", "development"),
            "debug": self.DEBUG,
            "port": self.PORT,
            "host": self.HOST,
            "glpi_url": self.GLPI_URL,
            "log_level": self.LOG_LEVEL,
            "cache_type": self.CACHE_TYPE,
            "cache_timeout": self.CACHE_DEFAULT_TIMEOUT,
            "performance_target": self.PERFORMANCE_TARGET_P95,
            "api_timeout": self.API_TIMEOUT,
            "structured_logging": self.STRUCTURED_LOGGING,
            "prometheus_enabled": self._get_config_value("observability.metrics.enabled", True),
        }


# Configuração de desenvolvimento
class DevelopmentConfig(Config):
    """Configuração para ambiente de desenvolvimento"""

    DEBUG = True


# Configuração de produção
class ProductionConfig(Config):
    """Configuração para ambiente de produção"""

    DEBUG = False
    CORS_ORIGINS = ["https://dashboard.example.com"]


# Configuração de teste
class TestingConfig(Config):
    """Configuração para ambiente de teste"""

    DEBUG = True
    TESTING = True


# Dicionário de configurações
config_by_name = {
    "dev": DevelopmentConfig,
    "development": DevelopmentConfig,
    "prod": ProductionConfig,
    "production": ProductionConfig,
    "test": TestingConfig,
}

# Configuração ativa
active_config = config_by_name[os.environ.get("FLASK_ENV", "dev")]


def get_config():
    """Retorna a configuração ativa baseada na variável de ambiente FLASK_ENV"""
    return active_config()
