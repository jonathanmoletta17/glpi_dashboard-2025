# -*- coding: utf-8 -*-
import logging
import threading
import time
import traceback
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import requests

from config.settings import active_config
# Removed unused import: alerting_system
from utils.date_validator import DateValidator
from utils.html_cleaner import clean_html_content
# Removed unused import: prometheus_metrics
from utils.response_formatter import ResponseFormatter
from utils.structured_logging import glpi_logger, log_glpi_request

from .glpi_helpers import GLPIServiceHelpers


class GLPIService:
    """Serviço para integração com a API do GLPI com autenticação robusta"""

    def __init__(self):
        try:
            # Validar configurações obrigatórias
            config_obj = active_config()
            if not hasattr(config_obj, "GLPI_URL") or not config_obj.GLPI_URL:
                raise ValueError("GLPI_URL não está configurado")
            if (not hasattr(config_obj, "GLPI_APP_TOKEN") or
                    not config_obj.GLPI_APP_TOKEN):
                raise ValueError("GLPI_APP_TOKEN não está configurado")
            if (not hasattr(config_obj, "GLPI_USER_TOKEN") or
                    not config_obj.GLPI_USER_TOKEN):
                raise ValueError("GLPI_USER_TOKEN não está configurado")

            self.glpi_url = config_obj.GLPI_URL.rstrip("/")  # Remove trailing slash
            self.base_url = self.glpi_url  # Alias para compatibilidade
            self.app_token = config_obj.GLPI_APP_TOKEN
            self.user_token = config_obj.GLPI_USER_TOKEN

            # Validar formato da URL
            if not self.glpi_url.startswith(("http://", "https://")):
                raise ValueError(
                    f"GLPI_URL deve começar com http:// ou https://, "
                    f"recebido: {self.glpi_url}"
                )

            # Usar logger consolidado
            self.structured_logger = glpi_logger

            self.logger = logging.getLogger("glpi_service")
            self.logger.info("GLPIService inicializado com sucesso")
        except Exception as e:
            error_msg = f"Erro na inicialização do GLPIService: {e}"
            logging.error(error_msg)
            raise RuntimeError(error_msg) from e

        # Mapeamento de status dos tickets
        self.status_map = {
            "Novo": 1,
            "Processando (atribuído)": 2,
            "Processando (planejado)": 3,
            "Pendente": 4,
            "Solucionado": 5,
            "Fechado": 6,
        }

        # Níveis de atendimento (grupos técnicos específicos)
        # Cada nível tem seu próprio grupo no GLPI
        self.service_levels = {
            "N1": 89,  # CC-SE-SUBADM-DTIC > N1
            "N2": 90,  # CC-SE-SUBADM-DTIC > N2
            "N3": 91,  # CC-SE-SUBADM-DTIC > N3
            "N4": 92,  # CC-SE-SUBADM-DTIC > N4
        }

        self.field_ids = {}
        self.session = requests.Session()  # Sessão HTTP para reutilização de conexões
        self.session_token = None
        self.token_created_at = None
        self.token_expires_at = None
        self.max_retries = 3
        self.retry_delay_base = 2  # Base para backoff exponencial
        self.session_timeout = 3600  # 1 hora em segundos

        # Lock para thread safety do cache
        self._cache_lock = threading.RLock()

        # Sistema de cache para evitar consultas repetitivas
        self._cache = {
            "technician_ranking": {
                "data": None,
                "timestamp": None,
                "ttl": 300,
            },  # 5 minutos
            "active_technicians": {
                "data": None,
                "timestamp": None,
                "ttl": 600,
            },  # 10 minutos
            "field_ids": {
                "data": None,
                "timestamp": None,
                "ttl": 1800,
            },  # 30 minutos
            "dashboard_metrics": {
                "data": None,
                "timestamp": None,
                "ttl": 180,
            },  # 3 minutos
            "dashboard_metrics_filtered": {},  # Cache dinâmico para filtros de data
            "priority_names": {},  # Cache para nomes de prioridade
        }

    def _is_cache_valid(self, cache_key: str, sub_key: str = None) -> bool:
        """Verifica se o cache é válido com validações robustas"""
        try:
            # Validar parâmetros de entrada
            if not isinstance(cache_key, str) or not cache_key.strip():
                self.logger.warning("cache_key deve ser uma string não vazia")
                return False

            if sub_key is not None and (not isinstance(sub_key, str) or not sub_key.strip()):
                self.logger.warning("sub_key deve ser uma string não vazia ou None")
                return False

            # Verificar se o cache existe
            if not hasattr(self, "_cache") or not isinstance(self._cache, dict):
                self.logger.warning("Cache não inicializado corretamente")
                return False

            if sub_key:
                cache_data = self._cache.get(cache_key, {}).get(sub_key)
            else:
                cache_data = self._cache.get(cache_key)

            if not cache_data or not isinstance(cache_data, dict):
                return False

            timestamp = cache_data.get("timestamp")
            if timestamp is None or not isinstance(timestamp, (int, float)):
                self.logger.warning(f"Timestamp inválido no cache para {cache_key}")
                return False

            current_time = time.time()
            ttl = cache_data.get("ttl", 300)  # Default 5 minutos

            if not isinstance(ttl, (int, float)) or ttl <= 0:
                self.logger.warning(f"TTL inválido no cache para {cache_key}: {ttl}")
                return False

            is_valid = (current_time - timestamp) < ttl
            if not is_valid:
                self.logger.debug(f"Cache expirado para {cache_key}: " f"idade={current_time - timestamp:.1f}s, TTL={ttl}s")

            return is_valid

        except Exception as e:
            self.logger.error(f"Erro ao verificar cache para {cache_key}: {e}")
            return False

    def _get_cache_data(self, cache_key: str, sub_key: str = None):
        """Obtém dados do cache com validações robustas, verificação de TTL e thread safety"""
        with self._cache_lock:
            try:
                # Validar parâmetros de entrada
                if not isinstance(cache_key, str) or not cache_key.strip():
                    self.logger.warning("cache_key deve ser uma string não vazia")
                    return None

                if sub_key is not None and (not isinstance(sub_key, str) or not sub_key.strip()):
                    self.logger.warning("sub_key deve ser uma string não vazia ou None")
                    return None

                # Verificar se o cache existe
                if not hasattr(self, "_cache") or not isinstance(self._cache, dict):
                    self.logger.warning("Cache não inicializado corretamente")
                    return None

                if sub_key:
                    cache_entry = self._cache.get(cache_key, {}).get(sub_key, {})
                else:
                    cache_entry = self._cache.get(cache_key, {})

                if not isinstance(cache_entry, dict):
                    self.logger.warning(f"Entrada de cache inválida para {cache_key}")
                    return None

                # CORREÇÃO CRÍTICA: Verificar se o cache expirou antes de retornar dados
                timestamp = cache_entry.get("timestamp")
                ttl = cache_entry.get("ttl", 300)  # Default 5 minutos

                if timestamp is not None and isinstance(timestamp, (int, float)):
                    current_time = time.time()
                    cache_age = current_time - timestamp

                    if cache_age >= ttl:
                        self.logger.debug(f"Cache expirado para {cache_key}: idade={cache_age:.1f}s, TTL={ttl}s")
                        # Remover entrada expirada do cache
                        if sub_key:
                            if cache_key in self._cache and sub_key in self._cache[cache_key]:
                                del self._cache[cache_key][sub_key]
                        else:
                            if cache_key in self._cache:
                                del self._cache[cache_key]
                        return None
                    else:
                        self.logger.debug(f"Cache válido para {cache_key}: idade={cache_age:.1f}s, TTL={ttl}s")

                return cache_entry.get("data")

            except Exception as e:
                self.logger.error(f"Erro ao obter dados do cache para {cache_key}: {e}")
                return None

    def _set_cache_data(self, cache_key: str, data, ttl: int = 300, sub_key: str = None):
        """Define dados no cache com validações robustas e thread safety"""
        with self._cache_lock:
            try:
                # Validar parâmetros de entrada
                if not isinstance(cache_key, str) or not cache_key.strip():
                    self.logger.warning("cache_key deve ser uma string não vazia")
                    return

                if sub_key is not None and (not isinstance(sub_key, str) or not sub_key.strip()):
                    self.logger.warning("sub_key deve ser uma string não vazia ou None")
                    return

                if not isinstance(ttl, (int, float)) or ttl <= 0:
                    self.logger.warning(f"TTL deve ser um número positivo, recebido: {ttl}")
                    ttl = 300  # Fallback para 5 minutos

                # Verificar se o cache existe
                if not hasattr(self, "_cache"):
                    self._cache = {}
                elif not isinstance(self._cache, dict):
                    self.logger.warning("Cache corrompido, reinicializando")
                    self._cache = {}

                cache_entry = {"data": data, "timestamp": time.time(), "ttl": ttl}

                if sub_key:
                    if cache_key not in self._cache:
                        self._cache[cache_key] = {}
                    elif not isinstance(self._cache[cache_key], dict):
                        self.logger.warning(f"Entrada de cache corrompida para {cache_key}, reinicializando")
                        self._cache[cache_key] = {}

                    self._cache[cache_key][sub_key] = cache_entry
                    self.logger.debug(f"Cache definido para {cache_key}[{sub_key}] com TTL {ttl}s")
                else:
                    self._cache[cache_key] = cache_entry
                    self.logger.debug(f"Cache definido para {cache_key} com TTL {ttl}s")

            except Exception as e:
                self.logger.error(f"Erro ao definir dados do cache para {cache_key}: {e}")

    def _is_token_expired(self) -> bool:
        """Verifica se o token de sessão está expirado com validações robustas"""
        try:
            # Verificar se o timestamp de criação existe e é válido
            if not self.token_created_at or not isinstance(self.token_created_at, (int, float)):
                self.logger.debug("Timestamp de criação do token não existe ou é inválido")
                return True

            # Verificar se o session_timeout é válido
            if (
                not hasattr(self, "session_timeout")
                or not isinstance(self.session_timeout, (int, float))
                or self.session_timeout <= 0
            ):
                self.logger.warning("session_timeout inválido, usando padrão de 3600s")
                self.session_timeout = 3600

            current_time = time.time()

            # Verificar se o timestamp não é futuro (proteção contra clock skew)
            if self.token_created_at > current_time:
                self.logger.warning("Timestamp do token está no futuro, considerando expirado")
                return True

            token_age = current_time - self.token_created_at
            is_expired = token_age >= self.session_timeout

            if is_expired:
                self.logger.debug(f"Token expirado (idade: {token_age:.0f}s, timeout: {self.session_timeout}s)")
            else:
                self.logger.debug(f"Token válido (idade: {token_age:.0f}s, timeout: {self.session_timeout}s)")

            return is_expired

        except Exception as e:
            self.logger.error(f"Erro ao verificar expiração do token: {e}")
            return True  # Em caso de erro, considerar expirado por segurança

    def _ensure_authenticated(self) -> bool:
        """Garante que temos um token válido, re-autenticando se necessário com validações robustas"""
        try:
            # Verificar se o token existe e é válido
            if not self.session_token or not isinstance(self.session_token, str) or not self.session_token.strip():
                self.logger.info("Token de sessão não existe ou é inválido, autenticando...")
                return self._authenticate_with_retry()

            # Verificar se o token está expirado
            if self._is_token_expired():
                self.logger.info("Token expirado, re-autenticando...")
                return self._authenticate_with_retry()

            self.logger.debug("Token válido, não é necessário re-autenticar")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao garantir autenticação: {e}")
            # Limpar token inválido
            self.session_token = None
            self.token_created_at = None
            self.token_expires_at = None
            return False

    def _authenticate_with_retry(self) -> bool:
        """Autentica com retry automático e backoff exponencial com validações robustas"""
        try:
            # Validar configurações de retry
            if not hasattr(self, "max_retries") or not isinstance(self.max_retries, int) or self.max_retries <= 0:
                self.logger.warning("max_retries inválido, usando padrão de 3")
                self.max_retries = 3

            if (
                not hasattr(self, "retry_delay_base")
                or not isinstance(self.retry_delay_base, (int, float))
                or self.retry_delay_base <= 0
            ):
                self.logger.warning("retry_delay_base inválido, usando padrão de 2")
                self.retry_delay_base = 2

            for attempt in range(self.max_retries):
                try:
                    self.logger.info(f"Tentativa de autenticação {attempt + 1}/{self.max_retries}")

                    if self._perform_authentication():
                        self.logger.info(f"Autenticação bem-sucedida na tentativa {attempt + 1}")
                        return True

                    if attempt < self.max_retries - 1:
                        delay = min(self.retry_delay_base**attempt, 30)  # Máximo de 30 segundos
                        self.logger.warning(
                            f"Tentativa {attempt + 1} falhou, aguardando {delay}s antes da próxima tentativa..."
                        )
                        time.sleep(delay)

                except requests.exceptions.Timeout as e:
                    self.logger.error(f"Timeout na tentativa {attempt + 1}: {e}")
                    if attempt < self.max_retries - 1:
                        delay = min(self.retry_delay_base**attempt, 30)
                        time.sleep(delay)

                except requests.exceptions.ConnectionError as e:
                    self.logger.error(f"Erro de conexão na tentativa {attempt + 1}: {e}")
                    if attempt < self.max_retries - 1:
                        delay = min(self.retry_delay_base**attempt, 30)
                        time.sleep(delay)

                except Exception as e:
                    self.logger.error(f"Erro na tentativa {attempt + 1} de autenticação: {e}")
                    if attempt < self.max_retries - 1:
                        delay = min(self.retry_delay_base**attempt, 30)
                        time.sleep(delay)

            self.logger.error(f"Falha na autenticação após {self.max_retries} tentativas")
            return False

        except Exception as e:
            self.logger.error(f"Erro crítico no processo de autenticação com retry: {e}")
            return False

    def _perform_authentication(self) -> bool:
        """Executa o processo de autenticação com validações robustas"""
        try:
            # Validar tokens de autenticação
            if not self.app_token or not isinstance(self.app_token, str) or not self.app_token.strip():
                self.logger.error("GLPI_APP_TOKEN não está configurado ou é inválido")
                return False

            if not self.user_token or not isinstance(self.user_token, str) or not self.user_token.strip():
                self.logger.error("GLPI_USER_TOKEN não está configurado ou é inválido")
                return False

            # Validar URL do GLPI
            if not self.glpi_url or not isinstance(self.glpi_url, str) or not self.glpi_url.strip():
                self.logger.error("GLPI_URL não está configurado ou é inválido")
                return False

            # Validar session_timeout
            if (
                not hasattr(self, "session_timeout")
                or not isinstance(self.session_timeout, (int, float))
                or self.session_timeout <= 0
            ):
                self.logger.warning("session_timeout inválido, usando padrão de 3600s")
                self.session_timeout = 3600

            session_headers = {
                "Content-Type": "application/json",
                "App-Token": self.app_token,
                "Authorization": f"user_token {self.user_token}",
            }

            auth_url = f"{self.glpi_url.rstrip('/')}/initSession"
            self.logger.info(f"Autenticando na API do GLPI: {auth_url}")

            response = requests.get(
                auth_url,
                headers=session_headers,
                timeout=8,  # Timeout mais generoso para autenticação
            )

            # Verificar status code
            if response.status_code != 200:
                self.logger.error(f"Falha na autenticação - Status: {response.status_code}, Resposta: {response.text}")
                return False

            # Validar resposta JSON
            try:
                response_data = response.json()
            except ValueError as e:
                self.logger.error(f"Resposta de autenticação não é JSON válido: {e}")
                return False

            # Validar presença do session_token
            if not response_data or "session_token" not in response_data:
                self.logger.error(f"session_token não encontrado na resposta: {response_data}")
                return False

            session_token = response_data["session_token"]
            if not session_token or not isinstance(session_token, str) or not session_token.strip():
                self.logger.error(f"session_token inválido: {session_token}")
                return False

            # Definir dados da sessão
            self.session_token = session_token
            self.token_created_at = time.time()
            self.token_expires_at = self.token_created_at + self.session_timeout

            self.logger.info(f"Autenticação bem-sucedida! Token expira em {self.session_timeout}s")
            return True

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout na autenticação: {e}")
            return False

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Erro de conexão na autenticação: {e}")
            return False

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro de requisição na autenticação: {e}")
            return False

        except Exception as e:
            self.logger.error(f"Erro inesperado na autenticação: {e}")
            return False

    def authenticate(self) -> bool:
        """Método público para autenticação (mantido para compatibilidade)"""
        return self._authenticate_with_retry()

    def get_api_headers(self) -> Optional[Dict[str, str]]:
        """Retorna os headers necessários para as requisições da API com validações robustas"""
        try:
            # Garantir autenticação
            if not self._ensure_authenticated():
                self.logger.error("Não foi possível obter headers - falha na autenticação")
                return None

            # Validar tokens necessários
            if not self.app_token or not isinstance(self.app_token, str) or not self.app_token.strip():
                self.logger.error("app_token não está disponível ou é inválido")
                return None

            if not self.session_token or not isinstance(self.session_token, str) or not self.session_token.strip():
                self.logger.error("session_token não está disponível ou é inválido")
                return None

            headers = {
                "Session-Token": self.session_token,
                "App-Token": self.app_token,
            }

            self.logger.debug("Headers da API gerados com sucesso")
            return headers

        except Exception as e:
            self.logger.error(f"Erro ao obter headers da API: {e}")
            return None

    def _make_authenticated_request(
        self,
        method: str,
        url: str,
        correlation_id: Optional[str] = None,
        **kwargs,
    ) -> Optional[requests.Response]:
        """Faz uma requisição autenticada com retry automático e validações robustas"""
        start_time = None  # Initialize start_time to avoid UnboundLocalError
        try:
            # Validar parâmetros de entrada
            if (
                not method
                or not isinstance(method, str)
                or method.strip().upper() not in ["GET", "POST", "PUT", "DELETE", "PATCH"]
            ):
                self.logger.error(f"Método HTTP inválido: {method}")
                return None

            if not url or not isinstance(url, str) or not url.strip():
                self.logger.error("URL não pode ser vazia")
                return None

            method = method.strip().upper()
            url = url.strip()

            # Validar configurações de retry
            if not hasattr(self, "max_retries") or not isinstance(self.max_retries, int) or self.max_retries <= 0:
                self.logger.warning("max_retries inválido, usando padrão de 3")
                self.max_retries = 3

            if (
                not hasattr(self, "retry_delay_base")
                or not isinstance(self.retry_delay_base, (int, float))
                or self.retry_delay_base <= 0
            ):
                self.logger.warning("retry_delay_base inválido, usando padrão de 2")
                self.retry_delay_base = 2

            # Usar timeout configurado se não fornecido
            if "timeout" not in kwargs:
                try:
                    # Importar configurações de performance
                    from backend.config.performance import API_CONFIG
                    
                    # Determinar timeout baseado no tipo de operação
                    endpoint_path = url.split("/")[-1] if "/" in url else url
                    
                    # Operações rápidas (status, auth)
                    if any(fast_op in endpoint_path.lower() for fast_op in ["status", "initSession", "killSession"]):
                        kwargs["timeout"] = API_CONFIG.get("FAST_TIMEOUT", 5)
                    # Operações pesadas (search, reports)
                    elif any(heavy_op in endpoint_path.lower() for heavy_op in ["search", "report", "listSearchOptions"]):
                        kwargs["timeout"] = API_CONFIG.get("SLOW_TIMEOUT", 20)
                    else:
                        # Timeout padrão
                        kwargs["timeout"] = API_CONFIG.get("TIMEOUT", 12)
                        
                except (ImportError, AttributeError):
                    # Fallback para configuração do objeto config
                    try:
                        config_obj = active_config()
                        kwargs["timeout"] = config_obj.API_TIMEOUT
                    except (AttributeError, NameError):
                        kwargs["timeout"] = 30  # Fallback final
                        self.logger.warning("API_TIMEOUT não configurado, usando 30s")

            # Validar timeout
            if not isinstance(kwargs["timeout"], (int, float)) or kwargs["timeout"] <= 0:
                kwargs["timeout"] = 30
                self.logger.warning("Timeout inválido, usando 30s")

            for attempt in range(self.max_retries):
                try:
                    headers = self.get_api_headers()
                    if not headers:
                        self.logger.error(f"Falha ao obter headers de autenticação (tentativa {attempt + 1})")
                        if attempt < self.max_retries - 1:
                            delay = min(self.retry_delay_base**attempt, 30)
                            time.sleep(delay)
                            continue
                        return None

                    # Adicionar headers customizados se fornecidos
                    if "headers" in kwargs and isinstance(kwargs["headers"], dict):
                        headers.update(kwargs["headers"])
                    kwargs["headers"] = headers

                    self.logger.debug(f"Fazendo requisição {method} para {url} (tentativa {attempt + 1})")

                    # Log estruturado da chamada de API com correlation_id
                    if self.structured_logger and correlation_id:
                        log_glpi_request(
                            method=method,
                            url=url,
                            correlation_id=correlation_id,
                            attempt=attempt + 1,
                        )

                    # Instrumentação Prometheus para requisições GLPI
                    start_time = time.time()

                    # Log detalhado antes da requisição
            # Debug logs removidos para produção

                    response = requests.request(method, url, **kwargs)
                    response_time = time.time() - start_time

                    # Log detalhado da resposta
            # Debug detalhado removido para produção

                    # Requisição processada com sucesso

                    # Métricas da requisição GLPI removidas (prometheus_metrics não disponível)

                    # Log estruturado da resposta
                    log_glpi_request(
                        endpoint=f"{method} {url}",
                        status_code=response.status_code,
                        duration=response_time,
                        attempt=attempt + 1,
                        correlation_id=correlation_id,
                    )

                    # Log de performance e alertas para requisições lentas (otimizado para 3s)
                    if response_time > 3.0:
                        self.logger.warning(f"Requisição lenta detectada: {response_time:.2f}s para {method} {url}")
                        # Registrar métrica de performance para resposta lenta
                        glpi_logger.log_performance_metric(
                            "glpi_slow_response",
                            response_time,
                            "seconds",
                            method=method,
                            endpoint=url.split("/")[-1] if "/" in url else url,
                        )
                    else:
                        self.logger.debug(f"Requisição completada em {response_time:.2f}s")

                    # Se recebemos 401 ou 403, token pode estar expirado
                    if response.status_code in [401, 403]:
                        self.logger.warning(f"Recebido status {response.status_code}, token pode estar expirado")
                        # Limpar token para forçar re-autenticação
                        self.session_token = None
                        self.token_created_at = None
                        self.token_expires_at = None

                        if attempt < self.max_retries - 1:
                            self.logger.info("Tentando re-autenticar...")
                            delay = min(self.retry_delay_base**attempt, 10)
                            time.sleep(delay)
                            continue

                    # Log de status codes problemáticos
                    if response.status_code >= 500:
                        self.logger.error(f"Erro do servidor GLPI: {response.status_code} - {response.text[:200]}")
                    elif response.status_code >= 400:
                        self.logger.warning(f"Erro na requisição: {response.status_code} - {response.text[:200]}")
                    elif response.status_code >= 200 and response.status_code < 300:
                        self.logger.debug(f"Requisição bem-sucedida: {response.status_code}")

                    return response

                except requests.exceptions.Timeout as e:
                    self.logger.warning(f"Timeout na requisição (tentativa {attempt + 1}): {e}")
                    # Incrementar contador de erros Prometheus
                    # Métrica de timeout removida (prometheus_metrics não disponível)

                    # Log estruturado do erro
                    glpi_logger.log_error_with_context(
                        "glpi_request_timeout",
                        f"Timeout na requisição: {e}",
                        error=str(e),
                        method=method,
                        url=url,
                        attempt=attempt + 1,
                        correlation_id=correlation_id,
                    )

                    if attempt < self.max_retries - 1:
                        delay = min(self.retry_delay_base**attempt, 30)
                        time.sleep(delay)
                        continue

                except requests.exceptions.ConnectionError as e:
                    self.logger.error(f"Erro de conexão (tentativa {attempt + 1}): {e}")
                    # Incrementar contador de erros Prometheus
                    # Métrica de erro de conexão removida (prometheus_metrics não disponível)

                    # Log estruturado do erro
                    glpi_logger.log_error_with_context(
                        "glpi_connection_error",
                        f"Erro de conexão: {e}",
                        error=str(e),
                        method=method,
                        url=url,
                        attempt=attempt + 1,
                        correlation_id=correlation_id,
                    )

                    if attempt < self.max_retries - 1:
                        delay = min(self.retry_delay_base**attempt, 30)
                        time.sleep(delay)
                        continue

                except requests.exceptions.RequestException as e:
                    self.logger.error(f"Erro na requisição (tentativa {attempt + 1}): {e}")
                    if attempt < self.max_retries - 1:
                        delay = min(self.retry_delay_base**attempt, 30)
                        time.sleep(delay)
                        continue

                except Exception as e:
                    self.logger.error(f"Erro inesperado na requisição (tentativa {attempt + 1}): {e}")
                    if attempt < self.max_retries - 1:
                        delay = min(self.retry_delay_base**attempt, 30)
                        time.sleep(delay)
                        continue

            self.logger.error(f"Todas as {self.max_retries} tentativas falharam para {method} {url}")
            return None

        except Exception as e:
            self.logger.error(f"Erro crítico no método _make_authenticated_request: {e}")
            return None

    def discover_field_ids(self) -> bool:
        """Descobre dinamicamente os IDs dos campos do GLPI com validações robustas e cache"""
        try:
            # Verificar cache primeiro
            cached_field_ids = self._get_cache_data("field_ids")
            if cached_field_ids and isinstance(cached_field_ids, dict):
                self.field_ids = cached_field_ids.copy()
                self.logger.debug("Field IDs carregados do cache")
                return True

            # Validar estado da instância
            if not hasattr(self, "field_ids") or not isinstance(self.field_ids, dict):
                self.field_ids = {}
                self.logger.warning("field_ids não inicializado, criando novo dicionário")

            if not hasattr(self, "glpi_url") or not self.glpi_url:
                self.logger.error("glpi_url não configurado")
                self._apply_fallback_field_ids()
                return False

            # Verificar autenticação
            if not self._ensure_authenticated():
                self.logger.error("Falha na autenticação para descobrir field IDs")
                self._apply_fallback_field_ids()
                return False

            try:
                self.logger.debug("Iniciando descoberta de IDs de campos")
                response = self._make_authenticated_request("GET", f"{self.glpi_url}/listSearchOptions/Ticket")

                if not response:
                    self.logger.error("Resposta nula ao descobrir field IDs")
                    self._apply_fallback_field_ids()
                    return True  # Retorna True porque fallbacks foram aplicados

                if not response.ok:
                    self.logger.error(f"Falha ao descobrir field IDs: HTTP {response.status_code}")
                    self._apply_fallback_field_ids()
                    return True

                # Validar resposta JSON
                try:
                    search_options = response.json()
                except ValueError as e:
                    self.logger.error(f"Resposta JSON inválida ao descobrir field IDs: {e}")
                    self._apply_fallback_field_ids()
                    return True

                if not isinstance(search_options, dict):
                    self.logger.error("Formato de resposta inválido para search options")
                    self._apply_fallback_field_ids()
                    return True

                # Mapear nomes de campos para IDs com maior precisão
                tech_group_field_names = [
                    "Grupo técnico",
                    "Technical group",
                    "Grupo tecnico",
                    "Assigned group",
                    "Group",
                    "Grupo",
                    "Grupo atribuído",
                    "Grupo responsável",
                    "Responsible group",
                ]

                status_field_names = [
                    "Status",
                    "Estado",
                    "State",
                    "Situação",
                    "Condition",
                ]

                # Descobrir campo TECH com mais opções
                tech_field_names = [
                    "Técnico",
                    "Technician",
                    "Tecnico",
                    "Assigned technician",
                    "Técnico encarregado",
                    "Assigned to",
                    "Atribuído para",
                    "Técnico responsável",
                    "Responsável",
                    "Assignee",
                    "Atribuído",
                    "Assigned user",
                    "Usuario atribuído",
                ]

                fields_found = {"GROUP": False, "STATUS": False, "TECH": False}

                for field_id, field_info in search_options.items():
                    try:
                        if not isinstance(field_info, dict) or "name" not in field_info:
                            continue

                        field_name = str(field_info["name"]).strip()
                        if not field_name:
                            continue

                        # Buscar campo de grupo técnico
                        if not fields_found["GROUP"] and any(
                            name.lower() in field_name.lower() for name in tech_group_field_names
                        ):
                            self.field_ids["GROUP"] = str(field_id)
                            fields_found["GROUP"] = True
                            self.logger.info(f"Campo GROUP encontrado: ID {field_id} - {field_name}")

                        # Buscar campo de status
                        elif not fields_found["STATUS"] and any(
                            name.lower() in field_name.lower() for name in status_field_names
                        ):
                            self.field_ids["STATUS"] = str(field_id)
                            fields_found["STATUS"] = True
                            self.logger.info(f"Campo STATUS encontrado: ID {field_id} - {field_name}")

                        # Buscar campo de técnico
                        elif not fields_found["TECH"] and any(name.lower() in field_name.lower() for name in tech_field_names):
                            self.field_ids["TECH"] = str(field_id)
                            fields_found["TECH"] = True
                            self.logger.info(f"Campo TECH encontrado: ID {field_id} - {field_name}")

                        # Parar se todos os campos foram encontrados
                        if all(fields_found.values()):
                            break

                    except Exception as e:
                        self.logger.warning(f"Erro ao processar campo {field_id}: {e}")
                        continue

                # Forçar ID 15 para data de criação (padrão GLPI)
                self.field_ids["DATE_CREATION"] = "15"
                self.logger.info("Campo DATE_CREATION definido como ID 15 (padrão GLPI)")

                # Aplicar fallbacks para campos não encontrados
                self._apply_fallback_field_ids()

                # Verificar se todos os campos essenciais estão presentes
                required_fields = ["GROUP", "STATUS", "DATE_CREATION", "TECH"]
                missing_fields = [
                    field for field in required_fields if field not in self.field_ids or not self.field_ids[field]
                ]

                if missing_fields:
                    self.logger.error(f"Campos críticos ainda ausentes: {missing_fields}")
                    return False

                # Salvar no cache para evitar descobertas futuras
                self._set_cache_data("field_ids", self.field_ids.copy(), ttl=1800)  # 30 minutos
                self.logger.info(f"IDs de campos descobertos com sucesso e salvos no cache: {self.field_ids}")
                return True

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Erro de requisição ao descobrir IDs dos campos: {e}")
                self._apply_fallback_field_ids()
                return True

            except Exception as e:
                self.logger.error(f"Erro inesperado ao descobrir IDs dos campos: {e}")
                self._apply_fallback_field_ids()
                return True

        except Exception as e:
            self.logger.error(f"Erro crítico no método discover_field_ids: {e}")
            # Tentar aplicar fallbacks mesmo em caso de erro crítico
            try:
                self._apply_fallback_field_ids()
            except Exception as fallback_error:
                self.logger.error(f"Erro ao aplicar fallbacks: {fallback_error}")
                return False
            return True

    def _apply_fallback_field_ids(self):
        """Aplica IDs de fallback para campos não encontrados com validações robustas"""
        try:
            # Validar se field_ids existe e é um dicionário
            if not hasattr(self, "field_ids"):
                self.field_ids = {}
                self.logger.warning("field_ids não existe, criando novo dicionário")
            elif not isinstance(self.field_ids, dict):
                self.logger.error(f"field_ids tem tipo inválido: {type(self.field_ids)}, recriando")
                self.field_ids = {}

            # Definir fallbacks padrão do GLPI
            fallbacks = {
                "GROUP": "8",  # Campo padrão para grupo técnico
                "STATUS": "12",  # Campo padrão para status
                "TECH": "5",  # Campo padrão para técnico atribuído
                "DATE_CREATION": "15",  # Campo padrão para data de criação
            }

            # Validar e aplicar fallbacks
            for field_name, fallback_id in fallbacks.items():
                try:
                    # Verificar se o campo não existe ou está vazio
                    if (
                        field_name not in self.field_ids
                        or not self.field_ids[field_name]
                        or not str(self.field_ids[field_name]).strip()
                    ):
                        self.field_ids[field_name] = str(fallback_id)
                        self.logger.warning(f"Campo {field_name} não encontrado ou vazio, usando fallback ID {fallback_id}")
                    else:
                        # Validar se o ID existente é válido
                        existing_id = str(self.field_ids[field_name]).strip()
                        if not existing_id.isdigit():
                            self.logger.warning(
                                f"ID inválido para campo {field_name}: '{existing_id}', usando fallback {fallback_id}"
                            )
                            self.field_ids[field_name] = str(fallback_id)
                        else:
                            self.logger.debug(f"Campo {field_name} já configurado com ID {existing_id}")

                except Exception as e:
                    self.logger.error(f"Erro ao processar fallback para campo {field_name}: {e}")
                    # Em caso de erro, aplicar o fallback mesmo assim
                    self.field_ids[field_name] = str(fallback_id)

            # Verificar integridade final
            required_fields = ["GROUP", "STATUS", "TECH", "DATE_CREATION"]
            for field in required_fields:
                if field not in self.field_ids or not self.field_ids[field]:
                    self.logger.error(f"Campo crítico {field} ainda não configurado após fallbacks")
                    if field in fallbacks:
                        self.field_ids[field] = str(fallbacks[field])
                        self.logger.warning(f"Forçando fallback para campo crítico {field}: {fallbacks[field]}")

            self.logger.debug(f"Fallbacks aplicados. field_ids final: {self.field_ids}")

        except Exception as e:
            self.logger.error(f"Erro crítico ao aplicar fallbacks: {e}")
            # Em caso de erro crítico, tentar configuração mínima
            try:
                self.field_ids = {
                    "GROUP": "8",
                    "STATUS": "12",
                    "TECH": "5",
                    "DATE_CREATION": "15",
                }
                self.logger.warning("Aplicada configuração mínima de fallbacks devido a erro crítico")
            except Exception as critical_error:
                self.logger.error(f"Falha crítica ao aplicar configuração mínima: {critical_error}")
                raise

    def _get_technician_name(self, tech_id: str) -> str:
        """Obtém o nome de um técnico com validações robustas e tratamento de erros"""
        try:
            # Validar parâmetros de entrada
            if not tech_id:
                self.logger.warning("tech_id vazio fornecido")
                return "Técnico Desconhecido"

            # Converter para string e limpar
            tech_id = str(tech_id).strip()
            if not tech_id:
                self.logger.warning("tech_id vazio após limpeza")
                return "Técnico Desconhecido"

            # Se não for um ID numérico, retornar o nome baseado no ID
            if not tech_id.isdigit():
                self.logger.debug(f"tech_id não numérico: {tech_id}, retornando nome baseado no ID")
                return f"Técnico {tech_id}"

            # Verificar configurações necessárias
            if not hasattr(self, "glpi_url") or not self.glpi_url:
                self.logger.error("glpi_url não configurado")
                return f"Técnico {tech_id}"

            try:
                self.logger.debug(f"Buscando dados do técnico {tech_id}")
                user_response = self._make_authenticated_request("GET", f"{self.glpi_url}/User/{tech_id}")

                if not user_response:
                    self.logger.warning(f"Resposta nula ao buscar usuário {tech_id}")
                    return f"Técnico {tech_id}"

                if not user_response.ok:
                    self.logger.warning(f"Falha ao obter dados do usuário {tech_id}: HTTP {user_response.status_code}")
                    return f"Técnico {tech_id}"

                # Validar resposta JSON
                try:
                    user_data = user_response.json()
                except ValueError as e:
                    self.logger.error(f"Resposta JSON inválida para usuário {tech_id}: {e}")
                    return f"Técnico {tech_id}"

                if not user_data:
                    self.logger.warning(f"Dados vazios para usuário {tech_id}")
                    return f"Técnico {tech_id}"

                # Verificar se user_data é uma lista ou dicionário
                user_info = None
                if isinstance(user_data, list):
                    if user_data and isinstance(user_data[0], dict):
                        user_info = user_data[0]
                    else:
                        self.logger.warning(f"Lista de dados inválida para usuário {tech_id}")
                        return f"Técnico {tech_id}"
                elif isinstance(user_data, dict):
                    user_info = user_data
                else:
                    self.logger.warning(f"Formato de dados inválido para usuário {tech_id}: {type(user_data)}")
                    return f"Técnico {tech_id}"

                if not user_info or not isinstance(user_info, dict):
                    self.logger.warning(f"user_info inválido para usuário {tech_id}")
                    return f"Técnico {tech_id}"

                # Tentar diferentes campos de nome em ordem de prioridade
                name_fields = [
                    "completename",  # Nome completo (preferido)
                    "realname",  # Nome real
                    "name",  # Nome de usuário
                    "firstname",  # Primeiro nome
                    "lastname",  # Sobrenome
                ]

                for field in name_fields:
                    try:
                        if field in user_info and user_info[field]:
                            name = str(user_info[field]).strip()
                            if name and name.lower() not in [
                                "null",
                                "none",
                                "",
                            ]:
                                self.logger.debug(f"Nome encontrado para técnico {tech_id}: {name} (campo: {field})")
                                return name
                    except Exception as e:
                        self.logger.warning(f"Erro ao processar campo {field} para usuário {tech_id}: {e}")
                        continue

                # Tentar combinar firstname + lastname
                try:
                    firstname = str(user_info.get("firstname", "")).strip()
                    lastname = str(user_info.get("lastname", "")).strip()

                    if firstname and lastname:
                        combined_name = f"{firstname} {lastname}".strip()
                        if combined_name:
                            self.logger.debug(f"Nome combinado para técnico {tech_id}: {combined_name}")
                            return combined_name
                    elif firstname:
                        self.logger.debug(f"Apenas primeiro nome para técnico {tech_id}: {firstname}")
                        return firstname
                    elif lastname:
                        self.logger.debug(f"Apenas sobrenome para técnico {tech_id}: {lastname}")
                        return lastname
                except Exception as e:
                    self.logger.warning(f"Erro ao combinar nomes para usuário {tech_id}: {e}")

                # Fallback final
                self.logger.warning(f"Nenhum nome válido encontrado para técnico {tech_id}")
                return f"Técnico {tech_id}"

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Erro de requisição ao buscar técnico {tech_id}: {e}")
                return f"Técnico {tech_id}"

            except Exception as e:
                self.logger.error(f"Erro inesperado ao buscar técnico {tech_id}: {e}")
                return f"Técnico {tech_id}"

        except Exception as e:
            self.logger.error(f"Erro crítico no método _get_technician_name para {tech_id}: {e}")
            return f'Técnico {tech_id if tech_id else "Desconhecido"}'

    def get_ticket_count_by_hierarchy(
        self,
        level: str,
        status_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Optional[int]:
        """Busca o total de tickets para um nível hierárquico e status específicos usando campo 8"""
        try:
            # Validações de entrada
            if not isinstance(level, str) or not level.strip():
                self.logger.error(f"[{datetime.now(tz=timezone.utc).isoformat()}] level inválido: {level}")
                return 0

            if not isinstance(status_id, (int, str)) or (isinstance(status_id, str) and not status_id.strip()):
                self.logger.error(f"[{datetime.now(tz=timezone.utc).isoformat()}] status_id inválido: {status_id}")
                return 0

            # Converter status_id para int se necessário
            try:
                status_id = int(status_id)
            except (ValueError, TypeError) as e:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao converter status_id para int: {e}"
                )
                return 0

            # Validar datas se fornecidas
            if start_date and not isinstance(start_date, str):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] start_date deve ser string: {type(start_date)}"
                )
                return 0

            if end_date and not isinstance(end_date, str):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] end_date deve ser string: {type(end_date)}"
                )
                return 0

            # Verificar configuração básica
            if not hasattr(self, "glpi_url") or not self.glpi_url:
                self.logger.error(f"[{datetime.now(tz=timezone.utc).isoformat()}] GLPI URL não configurada")
                return 0

            # Garantir autenticação
            if not self._ensure_authenticated():
                self.logger.error(f"[{datetime.now(tz=timezone.utc).isoformat()}] Falha na autenticação")
                return 0

            if not self.field_ids:
                if not self.discover_field_ids():
                    timestamp = datetime.now(tz=timezone.utc).isoformat()
                    self.logger.error(
                        f"[{timestamp}] Falha ao descobrir field_ids - "
                        f"level: {level}, status_id: {status_id}, "
                        f"start_date: {start_date}, end_date: {end_date}"
                    )
                    return 0

            # Verificar se field_ids necessários estão disponíveis
            if not self.field_ids.get("STATUS"):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Field ID STATUS não encontrado: {self.field_ids.get('STATUS')}"
                )
                return 0

            # Usar campo 8 para estrutura hierárquica em vez do campo GROUP (71)
            search_params = {
                "is_deleted": 0,
                "range": "0-0",
                "criteria[0][field]": "8",  # Campo 8 contém a estrutura hierárquica
                "criteria[0][searchtype]": "contains",
                "criteria[0][value]": level,  # Ex: "N1", "N2", "N3", "N4"
                "criteria[1][link]": "AND",
                "criteria[1][field]": self.field_ids["STATUS"],
                "criteria[1][searchtype]": "equals",
                "criteria[1][value]": status_id,
            }

            # Adicionar filtros de data se fornecidos usando função utilitária
            # Para métricas por nível, usar data de modificação (campo 19) em vez de criação
            if start_date or end_date:
                date_criteria = DateValidator.construir_criterios_filtro_data(
                    start_date=start_date,
                    end_date=end_date,
                    field_id="19",  # Campo de data de modificação para métricas por nível
                    criteria_start_index=2,
                )
                search_params.update(date_criteria)

            self.logger.info(
                f"[{datetime.now(tz=timezone.utc).isoformat()}] Buscando tickets por hierarquia - level: {level}, status: {status_id}"
            )

            response = self._make_authenticated_request(
                "GET",
                f"{self.glpi_url}/search/Ticket",
                correlation_id=correlation_id,
                params=search_params,
            )

            if response.status_code in [200, 206]:
                # Tentar extrair contagem do cabeçalho Content-Range
                content_range = response.headers.get("Content-Range")
                if content_range:
                    try:
                        total_count = int(content_range.split("/")[-1])
                        self.logger.info(
                            f"[{datetime.now(tz=timezone.utc).isoformat()}] Contagem extraída do Content-Range: {total_count}"
                        )
                        return total_count
                    except (ValueError, IndexError) as e:
                        self.logger.warning(
                            f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao extrair contagem do Content-Range: {e}"
                        )

                # Tentar extrair do corpo da resposta
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        # Verificar campo 'content-range'
                        if "content-range" in data:
                            try:
                                total_count = int(data["content-range"].split("/")[-1])
                                self.logger.info(
                                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Contagem extraída do content-range no JSON: {total_count}"
                                )
                                return total_count
                            except (ValueError, IndexError) as e:
                                self.logger.warning(
                                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao extrair contagem do content-range JSON: {e}"
                                )

                        # Verificar campo 'totalcount'
                        if "totalcount" in data:
                            total_count = int(data["totalcount"])
                            self.logger.info(
                                f"[{datetime.now(tz=timezone.utc).isoformat()}] Contagem extraída do totalcount: {total_count}"
                            )
                            return total_count

                        # Se data é uma lista, retornar o comprimento
                        if "data" in data and isinstance(data["data"], list):
                            count = len(data["data"])
                            self.logger.info(
                                f"[{datetime.now(tz=timezone.utc).isoformat()}] Contagem baseada no tamanho da lista de dados: {count}"
                            )
                            return count

                    # Se a resposta é uma lista diretamente
                    elif isinstance(data, list):
                        count = len(data)
                        self.logger.info(
                            f"[{datetime.now(tz=timezone.utc).isoformat()}] Contagem baseada no tamanho da lista: {count}"
                        )
                        return count

                except ValueError as e:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao decodificar JSON: {e}"
                    )

                self.logger.warning(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Resposta sem Content-Range ou totalcount válidos"
                )
                return 0
            else:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro na requisição: {response.status_code} - {response.text}"
                )
                return 0

        except requests.exceptions.RequestException as e:
            self.logger.error(f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro de requisição: {e}")
            return 0
        except Exception as e:
            self.logger.error(f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro inesperado: {e}")
            return 0

    def get_ticket_count(
        self,
        group_id: int,
        status_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        correlation_id: Optional[str] = None,
        date_field: str = "15",  # Campo de data padrão (15 = criação, 19 = modificação)
    ) -> Optional[int]:
        """Busca o total de tickets para um grupo e status específicos, com filtro de data opcional"""
        try:
            # Validações de entrada
            if not isinstance(group_id, (int, str)) or (isinstance(group_id, str) and not group_id.strip()):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] group_id inválido: {group_id}"
                )
                return 0

            if not isinstance(status_id, (int, str)) or (isinstance(status_id, str) and not status_id.strip()):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] status_id inválido: {status_id}"
                )
                return 0

            # Converter para int se necessário
            try:
                group_id = int(group_id)
                status_id = int(status_id)
            except (ValueError, TypeError) as e:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao converter IDs para int: {e}"
                )
                return 0

            # Validar datas se fornecidas
            if start_date and not isinstance(start_date, str):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] start_date deve ser string: {type(start_date)}"
                )
                return 0

            if end_date and not isinstance(end_date, str):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] end_date deve ser string: {type(end_date)}"
                )
                return 0

            # Verificar configuração básica
            if not hasattr(self, "glpi_url") or not self.glpi_url:
                self.logger.error(f"[{datetime.now(tz=timezone.utc).isoformat()}] GLPI URL não configurada")
                return 0

            # Garantir autenticação
            if not self._ensure_authenticated():
                self.logger.error(f"[{datetime.now(tz=timezone.utc).isoformat()}] Falha na autenticação")
                return 0

            if not self.field_ids:
                if not self.discover_field_ids():
                    timestamp = datetime.now(tz=timezone.utc).isoformat()
                    self.logger.error(
                        f"[{timestamp}] Falha ao descobrir field_ids - "
                        f"group_id: {group_id}, status_id: {status_id}, "
                        f"start_date: {start_date}, end_date: {end_date}"
                    )
                    return 0

            # Verificar se field_ids necessários estão disponíveis
            if not self.field_ids.get("GROUP") or not self.field_ids.get("STATUS"):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Field IDs críticos não encontrados: GROUP={self.field_ids.get('GROUP')}, STATUS={self.field_ids.get('STATUS')}"
                )
                return 0

            search_params = {
                "is_deleted": 0,
                "range": "0-0",
                "criteria[0][field]": self.field_ids["GROUP"],
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": group_id,
                "criteria[1][link]": "AND",
                "criteria[1][field]": self.field_ids["STATUS"],
                "criteria[1][searchtype]": "equals",
                "criteria[1][value]": status_id,
            }

            # Log de observabilidade: parâmetros GLPI
            timestamp = datetime.now(tz=timezone.utc).isoformat()
            self.logger.info(
                f"[{timestamp}] GLPI Query Parameters - "
                f"group_id: {group_id}, status_id: {status_id}, "
                f"GROUP_field: {self.field_ids['GROUP']}, STATUS_field: {self.field_ids['STATUS']}, "
                f"date_range: {start_date} to {end_date}"
            )

            # Adicionar filtros de data se fornecidos usando função utilitária
            if (start_date and start_date.strip()) or (end_date and end_date.strip()):
                try:
                    date_criteria = DateValidator.construir_criterios_filtro_data(
                        start_date=start_date.strip() if start_date else None,
                        end_date=end_date.strip() if end_date else None,
                        field_id=date_field,  # Usar campo de data configurável
                        criteria_start_index=2,
                    )
                    search_params.update(date_criteria)
                except ValueError as e:
                    self.logger.warning(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao processar filtros de data: {e}"
                    )

            try:
                response = self._make_authenticated_request(
                    "GET",
                    f"{self.glpi_url}/search/Ticket",
                    correlation_id=correlation_id,
                    params=search_params,
                )

                if not response:
                    timestamp = datetime.now(tz=timezone.utc).isoformat()
                    self.logger.error(
                        f"[{timestamp}] Resposta vazia da API GLPI - "
                        f"group_id: {group_id}, status_id: {status_id}, "
                        f"start_date: {start_date}, end_date: {end_date}"
                    )
                    return 0

                # Verificar se o status code é válido (200 OK ou 206 Partial Content)
                if response.status_code not in [200, 206]:
                    timestamp = datetime.now(tz=timezone.utc).isoformat()
                    self.logger.error(
                        f"[{timestamp}] API GLPI retornou status {response.status_code} - "
                        f"group_id: {group_id}, status_id: {status_id}, "
                        f"start_date: {start_date}, end_date: {end_date}"
                    )
                    return 0

                # Verificar se há cabeçalho Content-Range
                if "Content-Range" in response.headers:
                    try:
                        content_range = response.headers["Content-Range"]
                        if not content_range or "/" not in content_range:
                            self.logger.warning(
                                f"[{datetime.now(tz=timezone.utc).isoformat()}] Content-Range inválido: {content_range}"
                            )
                            return 0

                        total_str = content_range.split("/")[-1]
                        if not total_str.isdigit():
                            self.logger.warning(
                                f"[{datetime.now(tz=timezone.utc).isoformat()}] Total não numérico no Content-Range: {total_str}"
                            )
                            return 0

                        total = int(total_str)
                        timestamp = datetime.now(tz=timezone.utc).isoformat()
                        self.logger.info(
                            f"[{timestamp}] GLPI Query Result - "
                            f"group_id: {group_id}, status_id: {status_id}, "
                            f"ticket_count: {total}, source: content-range_header"
                        )
                        return total
                    except (ValueError, IndexError) as e:
                        self.logger.error(
                            f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao processar Content-Range '{response.headers.get('Content-Range', '')}': {e}"
                        )
                        return 0

                # Verificar se há content-range no corpo da resposta JSON
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and "content-range" in response_data:
                        content_range = response_data["content-range"]
                        if content_range and "/" in content_range:
                            total_str = content_range.split("/")[-1]
                            if total_str.isdigit():
                                total = int(total_str)
                                timestamp = datetime.now(tz=timezone.utc).isoformat()
                                self.logger.info(
                                    f"[{timestamp}] GLPI Query Result - "
                                    f"group_id: {group_id}, status_id: {status_id}, "
                                    f"ticket_count: {total}, source: content-range_json"
                                )
                                return total
                            else:
                                self.logger.warning(
                                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Total não numérico no content-range JSON: {total_str}"
                                )
                        else:
                            self.logger.warning(
                                f"[{datetime.now(tz=timezone.utc).isoformat()}] content-range JSON inválido: {content_range}"
                            )

                    # Verificar se há totalcount no JSON (alternativa)
                    if isinstance(response_data, dict) and "totalcount" in response_data:
                        total = response_data["totalcount"]
                        if isinstance(total, int):
                            timestamp = datetime.now(tz=timezone.utc).isoformat()
                            self.logger.info(
                                f"[{timestamp}] GLPI Query Result - "
                                f"group_id: {group_id}, status_id: {status_id}, "
                                f"ticket_count: {total}, source: totalcount"
                            )
                            return total

                except (ValueError, KeyError) as e:
                    self.logger.warning(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao processar JSON da resposta: {e}"
                    )

                # Se chegou até aqui com status 200 mas sem Content-Range, retornar 0
                self.logger.warning(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Resposta sem Content-Range válido - assumindo 0 tickets"
                )
                return 0

            except requests.exceptions.Timeout as e:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Timeout ao buscar contagem de tickets: {e}"
                )
                return 0
            except requests.exceptions.ConnectionError as e:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro de conexão ao buscar contagem de tickets: {e}"
                )
                return 0
            except requests.exceptions.RequestException as e:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro de requisição ao buscar contagem de tickets: {e}"
                )
                return 0
            except Exception as e:
                timestamp = datetime.now(tz=timezone.utc).isoformat()
                self.logger.error(
                    f"[{timestamp}] Exceção inesperada ao buscar contagem de tickets: {str(e)} - "
                    f"group_id: {group_id}, status_id: {status_id}, "
                    f"start_date: {start_date}, end_date: {end_date}"
                )
                return 0

        except Exception as e:
            self.logger.error(
                f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro geral no get_ticket_count: {e}"
            )
            return 0

    def get_metrics_by_level(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Dict[str, int]]:
        """Retorna métricas de tickets agrupadas por nível de atendimento"""
        try:
            # Verificar configuração básica
            if not hasattr(self, "service_levels") or not self.service_levels:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] service_levels não configurado"
                )
                return {}

            if not hasattr(self, "status_map") or not self.status_map:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] status_map não configurado"
                )
                return {}

            if not hasattr(self, "glpi_url") or not self.glpi_url:
                self.logger.error(f"[{datetime.now(tz=timezone.utc).isoformat()}] GLPI URL não configurada")
                return {}

            # Garantir autenticação
            if not self._ensure_authenticated():
                self.logger.error(f"[{datetime.now(tz=timezone.utc).isoformat()}] Falha na autenticação")
                return {}

            # Descobrir field_ids se necessário
            if not self.discover_field_ids():
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Falha ao descobrir field_ids"
                )
                return {}

            return self._get_metrics_by_level_internal_hierarchy(start_date, end_date, correlation_id)

        except Exception as e:
            self.logger.error(
                f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro geral no get_metrics_by_level: {e}"
            )
            return {}

    def _get_metrics_by_level_internal(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Dict[str, int]]:
        """Método interno para obter métricas por nível (sem autenticação/fechamento)"""
        try:
            # Validações de entrada
            if start_date and not isinstance(start_date, str):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] start_date deve ser string: {type(start_date)}"
                )
                return {}

            if end_date and not isinstance(end_date, str):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] end_date deve ser string: {type(end_date)}"
                )
                return {}

            # Validar formato das datas se fornecidas
            if start_date and start_date.strip():
                try:
                    datetime.strptime(start_date.strip(), "%Y-%m-%d")
                except ValueError as e:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Formato de start_date inválido '{start_date}': {e}"
                    )
                    return {}

            if end_date and end_date.strip():
                try:
                    datetime.strptime(end_date.strip(), "%Y-%m-%d")
                except ValueError as e:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Formato de end_date inválido '{end_date}': {e}"
                    )
                    return {}

            # Verificar se as configurações necessárias estão disponíveis
            if not hasattr(self, "service_levels") or not isinstance(self.service_levels, dict):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] service_levels inválido: {getattr(self, 'service_levels', None)}"
                )
                return {}

            if not hasattr(self, "status_map") or not isinstance(self.status_map, dict):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] status_map inválido: {getattr(self, 'status_map', None)}"
                )
                return {}

            if not self.service_levels:
                self.logger.warning(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] service_levels está vazio"
                )
                return {}

            if not self.status_map:
                self.logger.warning(f"[{datetime.now(tz=timezone.utc).isoformat()}] status_map está vazio")
                return {}

            metrics = {}

            for level_name, group_id in self.service_levels.items():
                try:
                    # Validar level_name e group_id
                    if not level_name or not isinstance(level_name, str):
                        self.logger.warning(
                            f"[{datetime.now(tz=timezone.utc).isoformat()}] level_name inválido: {level_name}"
                        )
                        continue

                    if not isinstance(group_id, (int, str)) or (isinstance(group_id, str) and not group_id.strip()):
                        self.logger.warning(
                            f"[{datetime.now(tz=timezone.utc).isoformat()}] group_id inválido para {level_name}: {group_id}"
                        )
                        continue

                    level_metrics = {}

                    for status_name, status_id in self.status_map.items():
                        try:
                            # Validar status_name e status_id
                            if not status_name or not isinstance(status_name, str):
                                self.logger.warning(
                                    f"[{datetime.now(tz=timezone.utc).isoformat()}] status_name inválido: {status_name}"
                                )
                                continue

                            if not isinstance(status_id, (int, str)) or (isinstance(status_id, str) and not status_id.strip()):
                                self.logger.warning(
                                    f"[{datetime.now(tz=timezone.utc).isoformat()}] status_id inválido para {status_name}: {status_id}"
                                )
                                continue

                            count = self.get_ticket_count(
                                group_id,
                                status_id,
                                start_date,
                                end_date,
                                correlation_id,
                                date_field="19",  # Usar data de modificação para métricas por nível
                            )
                            level_metrics[status_name] = count if count is not None else 0

                        except Exception as e:
                            self.logger.error(
                                f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao obter contagem para {level_name}/{status_name}: {e}"
                            )
                            level_metrics[status_name] = 0

                    metrics[level_name] = level_metrics

                except Exception as e:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao processar nível {level_name}: {e}"
                    )
                    metrics[level_name] = {}

            return metrics

        except Exception as e:
            self.logger.error(
                f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro no _get_metrics_by_level_internal: {e}"
            )
            return {}

    def debug_technician_tickets(self, technician_id: str, correlation_id: str = None) -> Dict[str, any]:
        """Debug específico dos tickets de um técnico"""
        try:
            if not self._ensure_authenticated():
                return {"error": "Falha na autenticação"}

            if not self.discover_field_ids():
                return {"error": "Falha ao descobrir IDs dos campos"}

            # Descobrir ID do campo do técnico
            tech_field_id = self._discover_tech_field_id()
            if not tech_field_id:
                return {"error": "Campo do técnico não encontrado"}

            debug_data = {
                "technician_id": technician_id,
                "tech_field_id": tech_field_id,
                "field_ids": self.field_ids,
                "status_map": self.status_map,
                "tickets": [],
            }

            # Buscar tickets do técnico
            search_params = {
                "is_deleted": 0,
                "range": "0-9",  # Primeiros 10 tickets
                "criteria[0][field]": tech_field_id,
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(technician_id),
                "forcedisplay[0]": "2",  # ID
                "forcedisplay[1]": "1",  # Título
                "forcedisplay[2]": "12",  # Status
                "forcedisplay[3]": "19",  # Data modificação
                "forcedisplay[4]": str(tech_field_id),  # Técnico
            }

            response = self._make_authenticated_request("GET", f"{self.glpi_url}/search/Ticket", params=search_params)

            if response and response.status_code in [200, 206]:
                tickets_data = response.json()
                debug_data["api_response"] = {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "data_keys": list(tickets_data.keys()) if isinstance(tickets_data, dict) else "not_dict",
                }

                if isinstance(tickets_data, dict) and "data" in tickets_data:
                    debug_data["tickets"] = tickets_data["data"][:5]  # Primeiros 5
                    debug_data["total_count"] = tickets_data.get("totalcount", 0)
                else:
                    debug_data["tickets"] = tickets_data if isinstance(tickets_data, list) else []
            else:
                debug_data["api_error"] = {
                    "status_code": response.status_code if response else "no_response",
                    "text": response.text if response else "no_response",
                }

            return debug_data

        except Exception as e:
            self.logger.error(f"Erro no debug do técnico {technician_id}: {e}", exc_info=True)
            return {"error": str(e), "technician_id": technician_id}

    def debug_technician_tickets_general(self, limit: int = 5, correlation_id: str = None) -> Dict[str, any]:
        """Debug geral dos tickets dos técnicos"""
        try:
            if not self._ensure_authenticated():
                return {"error": "Falha na autenticação"}

            debug_data = {
                "authentication": "success",
                "field_discovery": False,
                "technicians": [],
                "field_ids": {},
                "tech_field_id": None,
            }

            # Tentar descobrir IDs dos campos
            if self.discover_field_ids():
                debug_data["field_discovery"] = True
                debug_data["field_ids"] = self.field_ids

                # Descobrir ID do campo do técnico
                tech_field_id = self._discover_tech_field_id()
                debug_data["tech_field_id"] = tech_field_id

                if tech_field_id:
                    # Buscar alguns técnicos
                    try:
                        # Buscar usuários com perfil de técnico (ID 6)
                        profile_users_response = self._make_authenticated_request(
                            "GET",
                            f"{self.glpi_url}/Profile_User",
                            params={
                                "range": f"0-{limit - 1}",
                                "criteria[0][field]": "profiles_id",
                                "criteria[0][value]": "6",
                            },
                        )

                        if profile_users_response and profile_users_response.ok:
                            profile_data = profile_users_response.json()
                            debug_data["profile_users_response"] = {
                                "status": "success",
                                "count": len(profile_data) if isinstance(profile_data, list) else 0,
                            }

                            # Para cada técnico, buscar alguns tickets
                            for i, profile_user in enumerate(profile_data[:limit] if isinstance(profile_data, list) else []):
                                user_id = profile_user.get("users_id")
                                if user_id:
                                    tech_debug = self.debug_technician_tickets(str(user_id), correlation_id)
                                    debug_data["technicians"].append(
                                        {
                                            "user_id": user_id,
                                            "debug_data": tech_debug,
                                        }
                                    )
                        else:
                            debug_data["profile_users_response"] = {
                                "status": "error",
                                "status_code": profile_users_response.status_code if profile_users_response else "no_response",
                            }

                    except Exception as e:
                        debug_data["technicians_error"] = str(e)

            return debug_data

        except Exception as e:
            self.logger.error(f"Erro no debug geral dos técnicos: {e}", exc_info=True)
            return {"error": str(e)}

    def get_ticket_by_id(self, ticket_id: int) -> Dict[str, any]:
        """Busca detalhes completos de um ticket específico pelo ID"""
        if not self._ensure_authenticated():
            return None

        try:
            self.logger.debug(f"Buscando detalhes do ticket ID: {ticket_id}")

            # Buscar o ticket pelo ID
            url = f"{self.base_url}/Ticket/{ticket_id}"
            params = {
                "expand_dropdowns": True,
                "get_hateoas": False,
                "with_devices": True,
                "with_disks": True,
                "with_softwares": True,
                "with_connections": True,
                "with_networkequipments": True,
                "with_infocoms": True,
                "with_contracts": True,
                "with_documents": True,
                "with_tickets": True,
                "with_problems": True,
                "with_changes": True,
                "with_notes": True,
                "with_logs": True,
            }

            headers = {
                "App-Token": self.app_token,
                "Session-Token": self.session_token,
                "Content-Type": "application/json"
            }

            response = self.session.get(url, params=params, headers=headers, timeout=30)

            if response.status_code == 200:
                ticket_data = response.json()

                if ticket_data:
                    # Processar e enriquecer os dados do ticket
                    processed_ticket = self._process_ticket_details(ticket_data)
                    self.logger.info(f"Detalhes do ticket {ticket_id} obtidos com sucesso")
                    return processed_ticket
                else:
                    self.logger.warning(f"Ticket {ticket_id} não encontrado")
                    return None
            elif response.status_code == 404:
                self.logger.warning(f"Ticket {ticket_id} não encontrado (404)")
                return None
            else:
                self.logger.error(f"Erro ao buscar ticket {ticket_id}: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            self.logger.error(
                f"Erro ao buscar detalhes do ticket {ticket_id}: {e}",
                exc_info=True,
            )
            return None

    def _process_ticket_details(self, ticket_data: Dict) -> Dict[str, any]:
        """Processa e enriquece os dados do ticket com informações adicionais"""
        try:
            # Extrair dados básicos do ticket
            raw_description = ticket_data.get("content", "")
            clean_description = clean_html_content(raw_description)

            # Processamento da descrição

            # Extrair ramal da descrição original
            phone = self._extract_phone_from_description(raw_description)

            processed = {
                "id": ticket_data.get("id"),
                "title": ticket_data.get("name", ""),
                "description": clean_description,
                "phone": phone,  # Campo separado para o ramal
                "status": self._map_ticket_status(ticket_data.get("status", 1)),
                "priority": self._map_ticket_priority(ticket_data.get("priority", 3)),
                "category": clean_html_content(ticket_data.get("itilcategories_id", "Não categorizado")),
                "type": ticket_data.get("type_name", "Incidente"),
                "urgency": ticket_data.get("urgency_name", "Média"),
                "impact": ticket_data.get("impact_name", "Médio"),
                "source": ticket_data.get("requesttypes_id_name", "Não especificado"),
                "location": ticket_data.get("locations_id_name", ""),
                "entity": ticket_data.get("entities_id_name", ""),
                "created_at": ticket_data.get("date"),
                "updated_at": ticket_data.get("date_mod"),
                "due_date": ticket_data.get("time_to_resolve"),
                "close_date": ticket_data.get("closedate"),
                "solve_date": ticket_data.get("solvedate"),
                "requester": {
                    "id": ticket_data.get("users_id_recipient"),
                    "name": ticket_data.get("users_id_recipient", "Não especificado"),
                    "email": "",
                },
                "technician": {
                    "id": ticket_data.get("users_id_lastupdater"),
                    "name": ticket_data.get("users_id_lastupdater_name", "Não atribuído"),
                    "email": "",
                },
                "group": {
                    "id": ticket_data.get("groups_id_assign"),
                    "name": ticket_data.get("groups_id_assign_name", "Não atribuído"),
                },
                "time_tracking": {
                    "total_duration": ticket_data.get("actiontime", 0),
                    "waiting_duration": ticket_data.get("waiting_duration", 0),
                    "solve_delay_stat": ticket_data.get("solve_delay_stat", 0),
                    "close_delay_stat": ticket_data.get("close_delay_stat", 0),
                },
                "satisfaction": {
                    "rating": ticket_data.get("satisfaction"),
                    "comment": "",
                },
                "validation": {
                    "status": ticket_data.get("global_validation"),
                    "comment": "",
                },
                "comments": [],
                "attachments": [],
                "tags": [],
            }

            return processed

        except Exception as e:
            self.logger.error(f"Erro ao processar dados do ticket: {e}", exc_info=True)
            return ticket_data

    def _extract_phone_from_description(self, description: str) -> str:
        """Extrai o ramal completo da descrição do ticket

        Args:
            description: Descrição original do ticket (pode conter HTML)

        Returns:
            Ramal completo ou string vazia se não encontrado
        """
        try:
            if not description:
                return ""

            # Limpar HTML primeiro
            clean_desc = clean_html_content(description)

            # Padrão simples e eficaz para extrair ramal - captura apenas os dígitos após RAMAL
            # Busca por "RAMAL" seguido de dois pontos opcionais e captura os dígitos
            phone_pattern = r'RAMAL\s*:?\s*:?\s*(\d+)'

            import re
            phone_match = re.search(phone_pattern, clean_desc, re.IGNORECASE)

            if phone_match and phone_match.group(1).strip():
                phone_clean = phone_match.group(1).strip().replace(':', '').strip()
                return phone_clean if phone_clean else ""

            return ""

        except Exception as e:
            self.logger.warning(f"Erro ao extrair ramal da descrição: {e}")
            return ""

    def _map_ticket_priority(self, priority_id: int) -> str:
        """Mapeia ID de prioridade para nome legível"""
        priority_map = {
            1: "muito_baixa",
            2: "baixa",
            3: "normal",
            4: "alta",
            5: "muito_alta",
            6: "critica",
        }
        return priority_map.get(priority_id, "normal")

    def _map_ticket_status(self, status_id: int) -> str:
        """Mapeia ID de status para nome legível"""
        status_map = {
            1: "novo",
            2: "em_andamento",
            3: "planejado",
            4: "pendente",
            5: "resolvido",
            6: "fechado",
        }
        return status_map.get(status_id, "desconhecido")

    def _get_aggregated_ticket_counts(
        self,
        levels: List[str],
        status_ids: List[int],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Dict[str, int]]:
        """Método otimizado para buscar contagens de tickets agregadas em uma única requisição

        Args:
            levels: Lista de níveis hierárquicos (ex: ["N1", "N2", "N3", "N4"])
            status_ids: Lista de IDs de status
            start_date: Data de início (formato YYYY-MM-DD)
            end_date: Data de fim (formato YYYY-MM-DD)
            correlation_id: ID de correlação para logs

        Returns:
            Dict com estrutura: {"N1": {"status_name": count, ...}, ...}
        """
        try:
            # Inicializar resultado
            result = {level: {} for level in levels}

            # Construir critérios de busca agregada
            search_params = {
                "is_deleted": 0,
                "forcedisplay[0]": "8",  # Campo hierarquia
                "forcedisplay[1]": "12",  # Campo status
            }

            # Critério para hierarquia (campo 8) - usar OR para múltiplos níveis
            criteria_index = 0
            for i, level in enumerate(levels):
                if i == 0:
                    search_params[f"criteria[{criteria_index}][field]"] = "8"  # Campo hierarquia
                    search_params[f"criteria[{criteria_index}][searchtype]"] = "contains"
                    search_params[f"criteria[{criteria_index}][value]"] = level.upper()  # N1, N2, N3, N4
                else:
                    criteria_index += 1
                    search_params[f"criteria[{criteria_index}][link]"] = "OR"
                    search_params[f"criteria[{criteria_index}][field]"] = "8"  # Campo hierarquia
                    search_params[f"criteria[{criteria_index}][searchtype]"] = "contains"
                    search_params[f"criteria[{criteria_index}][value]"] = level.upper()  # N1, N2, N3, N4

            # Critério para status - usar OR para múltiplos status
            criteria_index += 1
            search_params[f"criteria[{criteria_index}][link]"] = "AND"
            search_params[f"criteria[{criteria_index}][field]"] = "12"
            search_params[f"criteria[{criteria_index}][searchtype]"] = "equals"
            search_params[f"criteria[{criteria_index}][value]"] = status_ids[0]

            for status_id in status_ids[1:]:
                criteria_index += 1
                search_params[f"criteria[{criteria_index}][link]"] = "OR"
                search_params[f"criteria[{criteria_index}][field]"] = "12"
                search_params[f"criteria[{criteria_index}][searchtype]"] = "equals"
                search_params[f"criteria[{criteria_index}][value]"] = status_id

            # Adicionar filtros de data se fornecidos usando função utilitária
            # Para métricas por nível, usar data de modificação (campo 19) em vez de criação (campo 15)
            if start_date or end_date:
                date_criteria = DateValidator.construir_criterios_filtro_data(
                    start_date=start_date,
                    end_date=end_date,
                    field_id="19",  # Campo de data de modificação para métricas por nível
                    criteria_start_index=criteria_index + 1,
                )
                search_params.update(date_criteria)

            correlation_log = f"[{correlation_id}] " if correlation_id else ""
            self.logger.info(
                f"{correlation_log}[OTIMIZAÇÃO] Buscando contagens agregadas para {len(levels)} níveis e {len(status_ids)} status"
            )

            # Inicializar contadores
            for level in levels:
                for status_name, status_id in self.status_map.items():
                    result[level][status_name] = 0

            # Usar paginação robusta para buscar todos os dados
            try:
                import time

                page_size = 1000
                start_index = 0
                max_retries = 3
                total_processed = 0

                while True:
                    # Configurar range para esta página
                    end_index = start_index + page_size - 1
                    current_params = search_params.copy()
                    current_params["range"] = f"{start_index}-{end_index}"

                    retry_count = 0
                    page_data = None

                    # Tentar buscar esta página com retry
                    while retry_count < max_retries:
                        try:
                            response = self._make_authenticated_request(
                                "GET",
                                f"{self.glpi_url}/search/Ticket",
                                params=current_params,
                                timeout=60,
                            )

                            if not response or not response.ok:
                                raise Exception(f"Falha na requisição: {response.status_code if response else 'No response'}")

                            page_data = response.json()
                            break  # Sucesso, sair do loop de retry

                        except Exception as e:
                            retry_count += 1
                            if retry_count < max_retries:
                                wait_time = 2**retry_count
                                self.logger.warning(
                                    f"{correlation_log}Erro na página {start_index}-{end_index}, tentativa {retry_count}/{max_retries}: {e}. Aguardando {wait_time}s..."
                                )
                                time.sleep(wait_time)
                            else:
                                self.logger.error(
                                    f"{correlation_log}Falha após {max_retries} tentativas na página {start_index}-{end_index}: {e}"
                                )
                                raise

                    # Processar dados da página
                    if not page_data or not isinstance(page_data, dict) or "data" not in page_data or not page_data["data"]:
                        self.logger.info(
                            f"{correlation_log}Página {start_index}-{end_index} vazia ou sem dados. Finalizando paginação."
                        )
                        break

                    page_items = len(page_data["data"])

                    # Contar tickets por nível e status nesta página
                    for ticket in page_data["data"]:
                        try:
                            ticket_hierarchy = str(ticket.get("8", "")).strip()  # Campo hierarquia
                            ticket_status_id = int(ticket.get("12", 0))  # Campo status

                            # Extrair nível da hierarquia textual (ex: "CC-SE-SUBADM-DTIC > N2" -> "N2")
                            ticket_level = None
                            if ticket_hierarchy and ticket_hierarchy != "None":
                                # Procurar por N1, N2, N3, N4 na string de hierarquia
                                for level in ["N1", "N2", "N3", "N4"]:
                                    if level in ticket_hierarchy:
                                        ticket_level = level
                                        break

                            if ticket_level and ticket_level in result:
                                # Encontrar nome do status
                                for (
                                    status_name,
                                    status_id,
                                ) in self.status_map.items():
                                    if int(status_id) == ticket_status_id:
                                        result[ticket_level][status_name] += 1
                                        break
                        except (ValueError, KeyError, TypeError) as e:
                            self.logger.debug(f"{correlation_log}Erro ao processar ticket: {e}")
                            continue

                    total_processed += page_items
                    self.logger.debug(
                        f"{correlation_log}Processados {page_items} tickets na página {start_index}-{end_index}. Total: {total_processed}"
                    )

                    # Verificar se chegamos ao fim
                    if page_items < page_size:
                        self.logger.info(f"{correlation_log}Última página processada. Total de tickets: {total_processed}")
                        break

                    # Avançar para próxima página
                    start_index += page_size

                    # Limite de segurança
                    if start_index > 100000:
                        self.logger.warning(
                            f"{correlation_log}Limite de segurança atingido em {start_index} tickets. Finalizando paginação."
                        )
                        break

                total_tickets = sum(sum(level_data.values()) for level_data in result.values())
                self.logger.info(f"{correlation_log}[OTIMIZAÇÃO] Contagens agregadas obtidas: {total_tickets} tickets total")

                return result

            except Exception as e:
                self.logger.error(f"{correlation_log}Erro na paginação robusta: {e}")
                return self._get_aggregated_ticket_counts_fallback(levels, status_ids, start_date, end_date, correlation_id)

        except Exception as e:
            correlation_log = f"[{correlation_id}] " if correlation_id else ""
            self.logger.error(f"{correlation_log}Erro na busca agregada: {e}")
            return self._get_aggregated_ticket_counts_fallback(levels, status_ids, start_date, end_date, correlation_id)

    def _get_aggregated_ticket_counts_fallback(
        self,
        levels: List[str],
        status_ids: List[int],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Dict[str, int]]:
        """Método fallback que usa requisições individuais quando a busca agregada falha"""
        correlation_log = f"[{correlation_id}] " if correlation_id else ""
        self.logger.info(f"{correlation_log}[FALLBACK] Usando método individual para contagens")
        result = {level: {} for level in levels}

        for level in levels:
            for status_name, status_id in self.status_map.items():
                try:
                    count = self.get_ticket_count_by_hierarchy(level, status_id, start_date, end_date, correlation_id)
                    result[level][status_name] = count if count is not None else 0
                except Exception as e:
                    self.logger.error(f"{correlation_log}Erro ao obter contagem para {level}/{status_name}: {e}")
                    result[level][status_name] = 0

        return result

    def _get_metrics_by_level_internal_hierarchy(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Dict[str, int]]:
        """Método interno otimizado para obter métricas por nível usando estrutura hierárquica (campo 8)"""
        try:
            # Validações de entrada
            if start_date and not isinstance(start_date, str):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] start_date deve ser string: {type(start_date)}"
                )
                return {}

            if end_date and not isinstance(end_date, str):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] end_date deve ser string: {type(end_date)}"
                )
                return {}

            # Validar formato das datas se fornecidas
            if start_date and start_date.strip():
                try:
                    datetime.strptime(start_date.strip(), "%Y-%m-%d")
                except ValueError as e:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Formato de start_date inválido '{start_date}': {e}"
                    )
                    return {}

            if end_date and end_date.strip():
                try:
                    datetime.strptime(end_date.strip(), "%Y-%m-%d")
                except ValueError as e:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Formato de end_date inválido '{end_date}': {e}"
                    )
                    return {}

            # Verificar se as configurações necessárias estão disponíveis
            if not hasattr(self, "status_map") or not isinstance(self.status_map, dict):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] status_map inválido: {getattr(self, 'status_map', None)}"
                )
                return {}

            if not self.status_map:
                self.logger.warning(f"[{datetime.now(tz=timezone.utc).isoformat()}] status_map está vazio")
                return {}

            # OTIMIZAÇÃO: Usar busca agregada em vez de requisições individuais
            hierarchy_levels = ["N1", "N2", "N3", "N4"]
            status_ids = [int(status_id) for status_id in self.status_map.values()]

            correlation_log = f"[{correlation_id}] " if correlation_id else ""
            self.logger.info(
                f"{correlation_log}[OTIMIZAÇÃO] Usando busca agregada para {len(hierarchy_levels)} níveis e {len(status_ids)} status"
            )

            # Tentar busca agregada primeiro
            metrics = self._get_aggregated_ticket_counts(
                hierarchy_levels,
                status_ids,
                start_date,
                end_date,
                correlation_id,
            )

            if not metrics or all(not level_data for level_data in metrics.values()):
                self.logger.warning(f"{correlation_log}Busca agregada retornou dados vazios, usando fallback")
                return self._get_aggregated_ticket_counts_fallback(
                    hierarchy_levels,
                    status_ids,
                    start_date,
                    end_date,
                    correlation_id,
                )

            return metrics

        except Exception as e:
            correlation_log = f"[{correlation_id}] " if correlation_id else ""
            self.logger.error(
                f"[{datetime.now(tz=timezone.utc).isoformat()}] {correlation_log}Erro geral no _get_metrics_by_level_internal_hierarchy: {e}"
            )
            return {}

    def get_general_metrics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, int]:
        """Retorna métricas gerais de todos os tickets (não apenas grupos N1-N4)"""
        try:
            # Verificar configuração básica
            if not hasattr(self, "status_map") or not self.status_map:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] status_map não configurado"
                )
                return {}

            if not hasattr(self, "glpi_url") or not self.glpi_url:
                self.logger.error(f"[{datetime.now(tz=timezone.utc).isoformat()}] GLPI URL não configurada")
                return {}

            # Garantir autenticação
            if not self._ensure_authenticated():
                self.logger.error(f"[{datetime.now(tz=timezone.utc).isoformat()}] Falha na autenticação")
                return {}

            # Descobrir field_ids se necessário
            if not self.discover_field_ids():
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Falha ao descobrir field_ids"
                )
                return {}

            result = self._get_general_metrics_internal(start_date, end_date, correlation_id)
            return result

        except Exception as e:
            self.logger.error(
                f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro geral no get_general_metrics: {e}"
            )
            return {}

    def _get_general_metrics_internal(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, int]:
        """Método interno para obter métricas gerais (sem autenticação/fechamento)"""
        try:
            # Validações de entrada
            if start_date and not isinstance(start_date, str):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] start_date deve ser string: {type(start_date)}"
                )
                return {}

            if end_date and not isinstance(end_date, str):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] end_date deve ser string: {type(end_date)}"
                )
                return {}

            # Validar formato das datas se fornecidas
            if start_date and start_date.strip():
                try:
                    datetime.strptime(start_date.strip(), "%Y-%m-%d")
                except ValueError as e:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Formato de start_date inválido '{start_date}': {e}"
                    )
                    return {}

            if end_date and end_date.strip():
                try:
                    datetime.strptime(end_date.strip(), "%Y-%m-%d")
                except ValueError as e:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Formato de end_date inválido '{end_date}': {e}"
                    )
                    return {}

            # Verificar configurações necessárias
            if not hasattr(self, "status_map") or not isinstance(self.status_map, dict):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] status_map inválido: {getattr(self, 'status_map', None)}"
                )
                return {}

            if not hasattr(self, "field_ids") or not isinstance(self.field_ids, dict):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] field_ids inválido: {getattr(self, 'field_ids', None)}"
                )
                return {}

            if not self.status_map:
                self.logger.warning(f"[{datetime.now(tz=timezone.utc).isoformat()}] status_map está vazio")
                return {}

            if not self.field_ids.get("STATUS"):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Field ID STATUS não encontrado: {self.field_ids}"
                )
                return {}

            if not hasattr(self, "glpi_url") or not self.glpi_url:
                self.logger.error(f"[{datetime.now(tz=timezone.utc).isoformat()}] GLPI URL não configurada")
                return {}

            status_totals = {}

            # Buscar totais por status sem filtro de grupo
            for status_name, status_id in self.status_map.items():
                try:
                    # Validar status_name e status_id
                    if not status_name or not isinstance(status_name, str):
                        self.logger.warning(
                            f"[{datetime.now(tz=timezone.utc).isoformat()}] status_name inválido: {status_name}"
                        )
                        continue

                    if not isinstance(status_id, (int, str)) or (isinstance(status_id, str) and not status_id.strip()):
                        self.logger.warning(
                            f"[{datetime.now(tz=timezone.utc).isoformat()}] status_id inválido para {status_name}: {status_id}"
                        )
                        continue

                    # Converter status_id para int se necessário
                    try:
                        status_id_int = int(status_id)
                    except (ValueError, TypeError) as e:
                        self.logger.error(
                            f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao converter status_id para int '{status_id}': {e}"
                        )
                        status_totals[status_name] = 0
                        continue

                    search_params = {
                        "is_deleted": 0,
                        "range": "0-0",
                        "criteria[0][field]": self.field_ids["STATUS"],
                        "criteria[0][searchtype]": "equals",
                        "criteria[0][value]": status_id_int,
                    }

                    # Adicionar filtros de data se fornecidos usando função utilitária
                    if start_date or end_date:
                        date_criteria = DateValidator.construir_criterios_filtro_data(
                            start_date=start_date,
                            end_date=end_date,
                            field_id="15",
                            criteria_start_index=1,
                        )
                        search_params.update(date_criteria)

                    try:
                        response = self._make_authenticated_request(
                            "GET",
                            f"{self.glpi_url}/search/Ticket",
                            params=search_params,
                            correlation_id=correlation_id,
                        )

                        if not response:
                            self.logger.warning(
                                f"[{datetime.now(tz=timezone.utc).isoformat()}] Resposta vazia para status {status_name}"
                            )
                            status_totals[status_name] = 0
                            continue

                        if response.status_code not in [200, 206]:
                            self.logger.warning(
                                f"[{datetime.now(tz=timezone.utc).isoformat()}] Status code inválido {response.status_code} para status {status_name}"
                            )
                            status_totals[status_name] = 0
                            continue

                        if "Content-Range" in response.headers:
                            try:
                                content_range = response.headers["Content-Range"]
                                if not content_range or "/" not in content_range:
                                    self.logger.warning(
                                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Content-Range inválido para {status_name}: {content_range}"
                                    )
                                    status_totals[status_name] = 0
                                    continue

                                total_str = content_range.split("/")[-1]
                                if not total_str.isdigit():
                                    self.logger.warning(
                                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Total não numérico para {status_name}: {total_str}"
                                    )
                                    status_totals[status_name] = 0
                                    continue

                                count = int(total_str)
                                status_totals[status_name] = count
                                self.logger.debug(
                                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Contagem para {status_name}: {count}"
                                )
                            except (ValueError, IndexError) as e:
                                self.logger.error(
                                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao processar Content-Range para {status_name}: {e}"
                                )
                                status_totals[status_name] = 0
                        else:
                            self.logger.warning(
                                f"[{datetime.now(tz=timezone.utc).isoformat()}] Sem Content-Range para {status_name}"
                            )
                            status_totals[status_name] = 0

                    except requests.exceptions.Timeout as e:
                        self.logger.error(
                            f"[{datetime.now(tz=timezone.utc).isoformat()}] Timeout ao buscar {status_name}: {e}"
                        )
                        status_totals[status_name] = 0
                    except requests.exceptions.ConnectionError as e:
                        self.logger.error(
                            f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro de conexão ao buscar {status_name}: {e}"
                        )
                        status_totals[status_name] = 0
                    except requests.exceptions.RequestException as e:
                        self.logger.error(
                            f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro de requisição ao buscar {status_name}: {e}"
                        )
                        status_totals[status_name] = 0
                    except Exception as e:
                        self.logger.error(
                            f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro inesperado ao buscar contagem geral para {status_name}: {e}"
                        )
                        status_totals[status_name] = 0

                except Exception as e:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao processar status {status_name}: {e}"
                    )
                    status_totals[status_name] = 0

            return status_totals

        except Exception as e:
            self.logger.error(
                f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro geral no _get_general_metrics_internal: {e}"
            )
            return {}

    def get_dashboard_metrics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, any]:
        """Retorna métricas formatadas para o dashboard React usando o sistema unificado.

        Args:
            start_date: Data inicial no formato YYYY-MM-DD (opcional)
            end_date: Data final no formato YYYY-MM-DD (opcional)

        Retorna um dicionário com as métricas formatadas ou erro.
        """
        start_time = time.time()
        try:
            # Validações de entrada
            if start_date and not isinstance(start_date, str):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] start_date deve ser string: {type(start_date)}"
                )
                return ResponseFormatter.format_error_response(
                    "Parâmetro start_date inválido",
                    ["start_date deve ser uma string"],
                    correlation_id=correlation_id,
                )

            if end_date and not isinstance(end_date, str):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] end_date deve ser string: {type(end_date)}"
                )
                return ResponseFormatter.format_error_response(
                    "Parâmetro end_date inválido",
                    ["end_date deve ser uma string"],
                    correlation_id=correlation_id,
                )

            # Validar formato das datas se fornecidas
            if start_date and start_date.strip():
                try:
                    datetime.strptime(start_date.strip(), "%Y-%m-%d")
                except ValueError as e:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Formato de start_date inválido '{start_date}': {e}"
                    )
                    return ResponseFormatter.format_error_response(
                        "Formato de data inválido",
                        [f"start_date deve estar no formato YYYY-MM-DD: {start_date}"],
                        correlation_id=correlation_id,
                    )

            if end_date and end_date.strip():
                try:
                    datetime.strptime(end_date.strip(), "%Y-%m-%d")
                except ValueError as e:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Formato de end_date inválido '{end_date}': {e}"
                    )
                    return ResponseFormatter.format_error_response(
                        "Formato de data inválido",
                        [f"end_date deve estar no formato YYYY-MM-DD: {end_date}"],
                        correlation_id=correlation_id,
                    )

            # Verificar configurações básicas
            if not hasattr(self, "glpi_url") or not self.glpi_url:
                self.logger.error(f"[{datetime.now(tz=timezone.utc).isoformat()}] GLPI URL não configurada")
                return ResponseFormatter.format_error_response(
                    "Configuração inválida",
                    ["GLPI URL não configurada"],
                    correlation_id=correlation_id,
                )

            if not hasattr(self, "status_map") or not self.status_map:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] status_map não configurado"
                )
                return ResponseFormatter.format_error_response(
                    "Configuração inválida",
                    ["Mapeamento de status não configurado"],
                    correlation_id=correlation_id,
                )

            if not hasattr(self, "service_levels") or not self.service_levels:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] service_levels não configurado"
                )
                return ResponseFormatter.format_error_response(
                    "Configuração inválida",
                    ["Níveis de serviço não configurados"],
                    correlation_id=correlation_id,
                )

            # Se parâmetros de data foram fornecidos, usar o método com filtro
            if start_date or end_date:
                try:
                    return self.get_dashboard_metrics_with_date_filter(start_date, end_date, correlation_id)
                except Exception as e:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro no método com filtro de data: {e}"
                    )
                    return ResponseFormatter.format_error_response(
                        "Erro ao obter métricas com filtro",
                        [str(e)],
                        correlation_id=correlation_id,
                    )

            # Verificar cache primeiro
            try:
                if self._is_cache_valid("dashboard_metrics"):
                    cached_data = self._get_cache_data("dashboard_metrics")
                    if cached_data:
                        self.logger.info(
                            f"[{datetime.now(tz=timezone.utc).isoformat()}] Retornando métricas do cache"
                        )
                        return cached_data
            except Exception as e:
                self.logger.warning(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao verificar cache: {e}"
                )

            # Autenticar uma única vez
            if not self._ensure_authenticated():
                self.logger.error(f"[{datetime.now(tz=timezone.utc).isoformat()}] Falha na autenticação")
                return ResponseFormatter.format_error_response(
                    "Falha na autenticação com GLPI",
                    ["Erro de autenticação"],
                    correlation_id=correlation_id,
                )

            if not self.discover_field_ids():
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Falha ao descobrir field_ids"
                )
                return ResponseFormatter.format_error_response(
                    "Falha ao descobrir IDs dos campos",
                    ["Erro ao obter configuração"],
                    correlation_id=correlation_id,
                )

            # Obter totais gerais (todos os grupos) para métricas principais
            try:
                general_totals = self._get_general_metrics_internal()
                if not isinstance(general_totals, dict):
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] general_totals inválido: {type(general_totals)}"
                    )
                    return ResponseFormatter.format_error_response(
                        "Erro ao obter métricas gerais",
                        ["Dados inválidos retornados"],
                        correlation_id=correlation_id,
                    )

                self.logger.info(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Totais gerais obtidos: {general_totals}"
                )
            except Exception as e:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao obter totais gerais: {e}"
                )
                return ResponseFormatter.format_error_response(
                    "Erro ao obter métricas gerais",
                    [str(e)],
                    correlation_id=correlation_id,
                )

            # Obter métricas por nível (grupos N1-N4)
            try:
                raw_metrics = self._get_metrics_by_level_internal_hierarchy()
                if not isinstance(raw_metrics, dict):
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] raw_metrics inválido: {type(raw_metrics)}"
                    )
                    return ResponseFormatter.format_error_response(
                        "Erro ao obter métricas por nível",
                        ["Dados inválidos retornados"],
                        correlation_id=correlation_id,
                    )

                self.logger.debug(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Métricas por nível obtidas: {raw_metrics}"
                )
            except Exception as e:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao obter métricas por nível: {e}"
                )
                return ResponseFormatter.format_error_response(
                    "Erro ao obter métricas por nível",
                    [str(e)],
                    correlation_id=correlation_id,
                )

            # Usar o mesmo formato da função com filtros para consistência
            # Calcular totais gerais com validação
            try:
                general_novos = general_totals.get("Novo", 0) if general_totals else 0
                general_pendentes = general_totals.get("Pendente", 0) if general_totals else 0
                general_progresso = (
                    (general_totals.get("Processando (atribuído)", 0) + general_totals.get("Processando (planejado)", 0))
                    if general_totals
                    else 0
                )
                general_resolvidos = (
                    (general_totals.get("Solucionado", 0) + general_totals.get("Fechado", 0)) if general_totals else 0
                )
                general_total = general_novos + general_pendentes + general_progresso + general_resolvidos

                # Validar se os valores são numéricos
                for name, value in [
                    ("novos", general_novos),
                    ("pendentes", general_pendentes),
                    ("progresso", general_progresso),
                    ("resolvidos", general_resolvidos),
                ]:
                    if not isinstance(value, (int, float)) or value < 0:
                        self.logger.warning(
                            f"[{datetime.now(tz=timezone.utc).isoformat()}] Valor inválido para {name}: {value}"
                        )

            except Exception as e:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao calcular totais gerais: {e}"
                )
                return ResponseFormatter.format_error_response(
                    "Erro ao calcular totais",
                    [str(e)],
                    correlation_id=correlation_id,
                )

            # Métricas por nível com validação
            try:
                level_metrics = {
                    "n1": {
                        "novos": 0,
                        "progresso": 0,
                        "pendentes": 0,
                        "resolvidos": 0,
                    },
                    "n2": {
                        "novos": 0,
                        "progresso": 0,
                        "pendentes": 0,
                        "resolvidos": 0,
                    },
                    "n3": {
                        "novos": 0,
                        "progresso": 0,
                        "pendentes": 0,
                        "resolvidos": 0,
                    },
                    "n4": {
                        "novos": 0,
                        "progresso": 0,
                        "pendentes": 0,
                        "resolvidos": 0,
                    },
                }

                if raw_metrics and isinstance(raw_metrics, dict):
                    for level_name, level_data in raw_metrics.items():
                        try:
                            if not level_name or not isinstance(level_name, str):
                                self.logger.warning(
                                    f"[{datetime.now(tz=timezone.utc).isoformat()}] level_name inválido: {level_name}"
                                )
                                continue

                            if not isinstance(level_data, dict):
                                self.logger.warning(
                                    f"[{datetime.now(tz=timezone.utc).isoformat()}] level_data inválido para {level_name}: {type(level_data)}"
                                )
                                continue

                            level_key = level_name.lower()
                            if level_key in level_metrics:
                                # Validar e extrair valores com fallback para 0
                                novos = level_data.get("Novo", 0)
                                progresso_atribuido = level_data.get("Processando (atribuído)", 0)
                                progresso_planejado = level_data.get("Processando (planejado)", 0)
                                pendentes = level_data.get("Pendente", 0)
                                solucionado = level_data.get("Solucionado", 0)
                                fechado = level_data.get("Fechado", 0)

                                # Validar tipos numéricos
                                for name, value in [
                                    ("novos", novos),
                                    (
                                        "progresso_atribuido",
                                        progresso_atribuido,
                                    ),
                                    (
                                        "progresso_planejado",
                                        progresso_planejado,
                                    ),
                                    ("pendentes", pendentes),
                                    ("solucionado", solucionado),
                                    ("fechado", fechado),
                                ]:
                                    if not isinstance(value, (int, float)):
                                        self.logger.warning(
                                            f"[{datetime.now(tz=timezone.utc).isoformat()}] Valor não numérico para {level_key}.{name}: {value}"
                                        )

                                level_metrics[level_key]["novos"] = max(
                                    0,
                                    int(novos) if isinstance(novos, (int, float)) else 0,
                                )
                                level_metrics[level_key]["progresso"] = max(
                                    0,
                                    (int(progresso_atribuido) if isinstance(progresso_atribuido, (int, float)) else 0)
                                    + (int(progresso_planejado) if isinstance(progresso_planejado, (int, float)) else 0),
                                )
                                level_metrics[level_key]["pendentes"] = max(
                                    0,
                                    int(pendentes) if isinstance(pendentes, (int, float)) else 0,
                                )
                                level_metrics[level_key]["resolvidos"] = max(
                                    0,
                                    (int(solucionado) if isinstance(solucionado, (int, float)) else 0)
                                    + (int(fechado) if isinstance(fechado, (int, float)) else 0),
                                )
                            else:
                                self.logger.warning(
                                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Nível desconhecido: {level_key}"
                                )
                        except Exception as e:
                            self.logger.error(
                                f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao processar nível {level_name}: {e}"
                            )
                            continue

            except Exception as e:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao processar métricas por nível: {e}"
                )
                return ResponseFormatter.format_error_response(
                    "Erro ao processar métricas por nível",
                    [str(e)],
                    correlation_id=correlation_id,
                )

            # Construir resultado final no formato do schema DashboardMetrics
            try:
                result = {
                    "success": True,
                    "data": {
                        # Campos principais do DashboardMetrics
                        "novos": general_novos,
                        "pendentes": general_pendentes,
                        "progresso": general_progresso,
                        "resolvidos": general_resolvidos,
                        "total": general_total,
                        # Estrutura de níveis
                        "niveis": {
                            "n1": level_metrics["n1"],
                            "n2": level_metrics["n2"],
                            "n3": level_metrics["n3"],
                            "n4": level_metrics["n4"],
                        },
                        "tendencias": self._calculate_trends(
                            general_novos,
                            general_pendentes,
                            general_progresso,
                            general_resolvidos,
                        ),
                        "filters_applied": None,
                        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                    },
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "tempo_execucao": (time.time() - start_time) * 1000,
                }

                # Validar resultado final
                if not isinstance(result, dict) or "success" not in result or "data" not in result:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Resultado final inválido: {type(result)}"
                    )
                    return ResponseFormatter.format_error_response(
                        "Erro na construção do resultado",
                        ["Estrutura de dados inválida"],
                        correlation_id=correlation_id,
                    )

                self.logger.info(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Métricas do dashboard construídas com sucesso"
                )

            except Exception as e:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao construir resultado final: {e}"
                )
                return ResponseFormatter.format_error_response(
                    "Erro ao construir resultado",
                    [str(e)],
                    correlation_id=correlation_id,
                )

            # Salvar no cache
            try:
                self._set_cache_data("dashboard_metrics", result, ttl=180)
                self.logger.debug(f"[{datetime.now(tz=timezone.utc).isoformat()}] Resultado salvo no cache")
            except Exception as e:
                self.logger.warning(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao salvar no cache: {e}"
                )

            return result

        except Exception as e:
            self.logger.error(
                f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro geral ao obter métricas do dashboard: {e}"
            )
            return ResponseFormatter.format_error_response(
                f"Erro interno: {str(e)}",
                [str(e)],
                correlation_id=correlation_id,
            )

    def _get_general_totals_internal(self, start_date: str = None, end_date: str = None) -> dict:
        """Método interno para obter totais gerais com filtro de data"""
        # Validações de entrada
        try:
            if start_date and not isinstance(start_date, str):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] start_date deve ser string: {type(start_date)}"
                )
                return {}

            if end_date and not isinstance(end_date, str):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] end_date deve ser string: {type(end_date)}"
                )
                return {}

            # Validar formato das datas
            if start_date and start_date.strip():
                try:
                    datetime.strptime(start_date.strip(), "%Y-%m-%d")
                except ValueError as e:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Formato de start_date inválido '{start_date}': {e}"
                    )
                    return {}

            if end_date and end_date.strip():
                try:
                    datetime.strptime(end_date.strip(), "%Y-%m-%d")
                except ValueError as e:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Formato de end_date inválido '{end_date}': {e}"
                    )
                    return {}

            # Verificar configurações necessárias
            if not hasattr(self, "status_map") or not self.status_map:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] status_map não configurado"
                )
                return {}

            if not isinstance(self.status_map, dict):
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] status_map deve ser dict: {type(self.status_map)}"
                )
                return {}

            if not hasattr(self, "field_ids") or not self.field_ids:
                self.logger.error(f"[{datetime.now(tz=timezone.utc).isoformat()}] field_ids não configurado")
                return {}

            if not isinstance(self.field_ids, dict) or "STATUS" not in self.field_ids:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] field_ids inválido ou STATUS ausente"
                )
                return {}

            self.logger.debug(
                f"[{datetime.now(tz=timezone.utc).isoformat()}] Iniciando busca de totais gerais com filtro de data"
            )

        except Exception as e:
            self.logger.error(
                f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro na validação de entrada: {e}"
            )
            return {}

        status_totals = {}

        # Buscar totais por status sem filtro de grupo (mesma lógica do _get_general_metrics_internal)
        for status_name, status_id in self.status_map.items():
            try:
                # Validar status_name e status_id
                if not status_name or not isinstance(status_name, str):
                    self.logger.warning(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] status_name inválido: {status_name}"
                    )
                    continue

                if not isinstance(status_id, (int, str)) or (isinstance(status_id, str) and not status_id.strip()):
                    self.logger.warning(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] status_id inválido para {status_name}: {status_id}"
                    )
                    continue

                search_params = {
                    "is_deleted": 0,
                    "range": "0-0",
                    "criteria[0][field]": self.field_ids["STATUS"],
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": status_id,
                }

                # Adicionar filtros de data usando a função utilitária
                criterios_data = DateValidator.construir_criterios_filtro_data(start_date, end_date)
                search_params.update(criterios_data)

                try:
                    response = self._make_authenticated_request(
                        "GET",
                        f"{self.glpi_url}/search/Ticket",
                        params=search_params,
                    )

                    if not response:
                        self.logger.warning(
                            f"[{datetime.now(tz=timezone.utc).isoformat()}] Resposta vazia para {status_name}"
                        )
                        status_totals[status_name] = 0
                        continue

                    if response.status_code not in [200, 206]:
                        self.logger.warning(
                            f"[{datetime.now(tz=timezone.utc).isoformat()}] Status HTTP inválido para {status_name}: {response.status_code}"
                        )
                        status_totals[status_name] = 0
                        continue

                    if "Content-Range" in response.headers:
                        try:
                            content_range = response.headers["Content-Range"]
                            if not content_range or "/" not in content_range:
                                self.logger.warning(
                                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Content-Range mal formatado para {status_name}: {content_range}"
                                )
                                status_totals[status_name] = 0
                                continue

                            count = int(content_range.split("/")[-1])
                            status_totals[status_name] = max(0, count)
                            self.logger.debug(
                                f"[{datetime.now(tz=timezone.utc).isoformat()}] Contagem para {status_name}: {count}"
                            )
                        except (ValueError, IndexError) as e:
                            self.logger.error(
                                f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao parsear Content-Range para {status_name}: {e}"
                            )
                            status_totals[status_name] = 0
                    else:
                        self.logger.warning(
                            f"[{datetime.now(tz=timezone.utc).isoformat()}] Content-Range ausente para {status_name}"
                        )
                        status_totals[status_name] = 0

                except requests.exceptions.Timeout as e:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Timeout ao buscar {status_name}: {e}"
                    )
                    status_totals[status_name] = 0
                except requests.exceptions.ConnectionError as e:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro de conexão ao buscar {status_name}: {e}"
                    )
                    status_totals[status_name] = 0
                except requests.exceptions.RequestException as e:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro de requisição ao buscar {status_name}: {e}"
                    )
                    status_totals[status_name] = 0
                except Exception as e:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro inesperado ao buscar {status_name}: {e}"
                    )
                    status_totals[status_name] = 0

            except Exception as e:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao processar status {status_name}: {e}"
                )
                status_totals[status_name] = 0

        self.logger.info(
            f"[{datetime.now(tz=timezone.utc).isoformat()}] Totais gerais obtidos: {status_totals}"
        )
        return status_totals

    def get_dashboard_metrics_with_date_filter(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, any]:
        """Retorna métricas formatadas para o dashboard React com filtro de data.

        Args:
            start_date: Data inicial no formato YYYY-MM-DD (opcional)
            end_date: Data final no formato YYYY-MM-DD (opcional)

        Retorna um dicionário com as métricas ou None em caso de falha.
        """
        start_time = time.time()
        self.logger.info(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando get_dashboard_metrics_with_date_filter com start_date={start_date}, end_date={end_date}"
        )

        try:
            # Validar formato das datas se fornecidas
            if start_date:
                if not isinstance(start_date, str):
                    self.logger.error(f"start_date deve ser string, recebido: {type(start_date)}")
                    return None
                try:
                    datetime.strptime(start_date, "%Y-%m-%d")
                except ValueError as e:
                    self.logger.error(f"Formato inválido para start_date '{start_date}': {e}")
                    return None

            if end_date:
                if not isinstance(end_date, str):
                    self.logger.error(f"end_date deve ser string, recebido: {type(end_date)}")
                    return None
                try:
                    datetime.strptime(end_date, "%Y-%m-%d")
                except ValueError as e:
                    self.logger.error(f"Formato inválido para end_date '{end_date}': {e}")
                    return None

            # Validar configurações essenciais
            if not hasattr(self, "glpi_url") or not self.glpi_url:
                self.logger.error("glpi_url não configurado")
                return None

            if not hasattr(self, "status_map") or not isinstance(self.status_map, dict) or not self.status_map:
                self.logger.error("status_map não configurado ou inválido")
                return None

            # Criar chave de cache baseada nos parâmetros de data
            cache_key = f"{start_date or 'none'}_{end_date or 'none'}"

            # Verificar se existe cache válido para este filtro
            try:
                if self._is_cache_valid("dashboard_metrics_filtered", cache_key):
                    cached_data = self._get_cache_data("dashboard_metrics_filtered", cache_key)
                    if cached_data:
                        self.logger.info(f"Retornando métricas do cache para filtro: {cache_key}")
                        return cached_data
            except Exception as e:
                self.logger.warning(f"Erro ao verificar cache: {e}")

            # Autenticar uma única vez
            try:
                if not self._ensure_authenticated():
                    self.logger.error("Falha na autenticação")
                    return None
            except Exception as e:
                self.logger.error(f"Erro durante autenticação: {e}")
                return None

            try:
                if not self.discover_field_ids():
                    self.logger.error("Falha na descoberta de field_ids")
                    return None
            except Exception as e:
                self.logger.error(f"Erro durante descoberta de field_ids: {e}")
                return None

            # Obter totais gerais (todos os grupos) para métricas principais com filtro de data
            try:
                general_totals = self._get_general_metrics_internal(start_date, end_date)
                if not isinstance(general_totals, dict):
                    self.logger.error(f"general_totals deve ser dict, recebido: {type(general_totals)}")
                    return None
                self.logger.info(f"Totais gerais obtidos com filtro de data: {general_totals}")
            except Exception as e:
                self.logger.error(f"Erro ao obter totais gerais: {e}")
                return None

            # Obter métricas por nível (grupos N1-N4) com filtro de data
            try:
                raw_metrics = self._get_metrics_by_level_internal_hierarchy(start_date, end_date)
                if not isinstance(raw_metrics, dict):
                    self.logger.error(f"raw_metrics deve ser dict, recebido: {type(raw_metrics)}")
                    return None
                self.logger.info(f"Métricas por nível obtidas: {len(raw_metrics)} níveis")
            except Exception as e:
                self.logger.error(f"Erro ao obter métricas por nível: {e}")
                return None

            # Agregação dos totais por status (apenas para níveis)
            try:
                totals = {
                    "novos": 0,
                    "pendentes": 0,
                    "progresso": 0,
                    "resolvidos": 0,
                }

                # Métricas por nível
                level_metrics = {
                    "n1": {
                        "novos": 0,
                        "progresso": 0,
                        "pendentes": 0,
                        "resolvidos": 0,
                    },
                    "n2": {
                        "novos": 0,
                        "progresso": 0,
                        "pendentes": 0,
                        "resolvidos": 0,
                    },
                    "n3": {
                        "novos": 0,
                        "progresso": 0,
                        "pendentes": 0,
                        "resolvidos": 0,
                    },
                    "n4": {
                        "novos": 0,
                        "progresso": 0,
                        "pendentes": 0,
                        "resolvidos": 0,
                    },
                }

                for level_name, level_data in raw_metrics.items():
                    try:
                        if not isinstance(level_data, dict):
                            self.logger.warning(f"level_data para {level_name} não é dict: {type(level_data)}")
                            continue

                        level_key = level_name.lower()
                        if level_key not in level_metrics:
                            self.logger.warning(f"Nível desconhecido: {level_key}")
                            continue

                        # Novo
                        novo_count = level_data.get("Novo", 0)
                        if not isinstance(novo_count, (int, float)):
                            self.logger.warning(f"Valor inválido para 'Novo' em {level_name}: {novo_count}")
                            novo_count = 0
                        level_metrics[level_key]["novos"] = int(novo_count)
                        totals["novos"] += level_metrics[level_key]["novos"]

                        # Progresso (soma de Processando atribuído e planejado)
                        processando_atribuido = level_data.get("Processando (atribuído)", 0)
                        processando_planejado = level_data.get("Processando (planejado)", 0)
                        if not isinstance(processando_atribuido, (int, float)):
                            self.logger.warning(
                                f"Valor inválido para 'Processando (atribuído)' em {level_name}: {processando_atribuido}"
                            )
                            processando_atribuido = 0
                        if not isinstance(processando_planejado, (int, float)):
                            self.logger.warning(
                                f"Valor inválido para 'Processando (planejado)' em {level_name}: {processando_planejado}"
                            )
                            processando_planejado = 0
                        level_metrics[level_key]["progresso"] = int(processando_atribuido) + int(processando_planejado)
                        totals["progresso"] += level_metrics[level_key]["progresso"]

                        # Pendente
                        pendente_count = level_data.get("Pendente", 0)
                        if not isinstance(pendente_count, (int, float)):
                            self.logger.warning(f"Valor inválido para 'Pendente' em {level_name}: {pendente_count}")
                            pendente_count = 0
                        level_metrics[level_key]["pendentes"] = int(pendente_count)
                        totals["pendentes"] += level_metrics[level_key]["pendentes"]

                        # Resolvidos (soma de Solucionado e Fechado)
                        solucionado = level_data.get("Solucionado", 0)
                        fechado = level_data.get("Fechado", 0)
                        if not isinstance(solucionado, (int, float)):
                            self.logger.warning(f"Valor inválido para 'Solucionado' em {level_name}: {solucionado}")
                            solucionado = 0
                        if not isinstance(fechado, (int, float)):
                            self.logger.warning(f"Valor inválido para 'Fechado' em {level_name}: {fechado}")
                            fechado = 0
                        level_metrics[level_key]["resolvidos"] = int(solucionado) + int(fechado)
                        totals["resolvidos"] += level_metrics[level_key]["resolvidos"]

                    except Exception as e:
                        self.logger.error(f"Erro ao processar métricas para nível {level_name}: {e}")
                        continue

                self.logger.info(f"Agregação concluída - totais: {totals}")

            except Exception as e:
                self.logger.error(f"Erro durante agregação de métricas: {e}")
                return None

            # Usar totais gerais para métricas principais
            try:
                general_novos = general_totals.get("Novo", 0)
                general_pendentes = general_totals.get("Pendente", 0)
                general_progresso_atribuido = general_totals.get("Processando (atribuído)", 0)
                general_progresso_planejado = general_totals.get("Processando (planejado)", 0)
                general_solucionado = general_totals.get("Solucionado", 0)
                general_fechado = general_totals.get("Fechado", 0)

                # Validar tipos dos valores
                for name, value in [
                    ("Novo", general_novos),
                    ("Pendente", general_pendentes),
                    ("Processando (atribuído)", general_progresso_atribuido),
                    ("Processando (planejado)", general_progresso_planejado),
                    ("Solucionado", general_solucionado),
                    ("Fechado", general_fechado),
                ]:
                    if not isinstance(value, (int, float)):
                        self.logger.warning(f"Valor inválido para '{name}': {value}, usando 0")
                        if name == "Novo":
                            general_novos = 0
                        elif name == "Pendente":
                            general_pendentes = 0
                        elif name == "Processando (atribuído)":
                            general_progresso_atribuido = 0
                        elif name == "Processando (planejado)":
                            general_progresso_planejado = 0
                        elif name == "Solucionado":
                            general_solucionado = 0
                        elif name == "Fechado":
                            general_fechado = 0

                general_progresso = int(general_progresso_atribuido) + int(general_progresso_planejado)
                general_resolvidos = int(general_solucionado) + int(general_fechado)
                general_total = int(general_novos) + int(general_pendentes) + general_progresso + general_resolvidos

                self.logger.info(
                    f"Métricas gerais calculadas com filtro: novos={general_novos}, pendentes={general_pendentes}, progresso={general_progresso}, resolvidos={general_resolvidos}, total={general_total}"
                )

            except Exception as e:
                self.logger.error(f"Erro ao calcular métricas gerais: {e}")
                return None

            # Construir resultado final
            try:
                # Calcular tendências
                try:
                    tendencias = self._get_trends_with_logging(
                        general_novos,
                        general_pendentes,
                        general_progresso,
                        general_resolvidos,
                        start_date,
                        end_date,
                    )
                    if not isinstance(tendencias, dict):
                        self.logger.warning(f"Tendências inválidas: {type(tendencias)}, usando valores padrão")
                        tendencias = {
                            "novos": 0.0,
                            "pendentes": 0.0,
                            "progresso": 0.0,
                            "resolvidos": 0.0,
                        }
                except Exception as e:
                    self.logger.error(f"Erro ao calcular tendências: {e}")
                    tendencias = {
                        "novos": 0.0,
                        "pendentes": 0.0,
                        "progresso": 0.0,
                        "resolvidos": 0.0,
                    }

                result = {
                    "success": True,
                    "data": {
                        # Campos diretos para compatibilidade com DashboardMetrics
                        "novos": int(general_novos),
                        "pendentes": int(general_pendentes),
                        "progresso": int(general_progresso),
                        "resolvidos": int(general_resolvidos),
                        "total": int(general_total),
                        "niveis": {
                            "geral": {
                                "novos": int(general_novos),
                                "pendentes": int(general_pendentes),
                                "progresso": int(general_progresso),
                                "resolvidos": int(general_resolvidos),
                                "total": int(general_total),
                            },
                            "n1": level_metrics["n1"],
                            "n2": level_metrics["n2"],
                            "n3": level_metrics["n3"],
                            "n4": level_metrics["n4"],
                        },
                        "tendencias": tendencias,
                        "filters_applied": {
                            "data_inicio": start_date,
                            "data_fim": end_date,
                        },
                        "timestamp": datetime.now().isoformat(),
                    },
                    "tempo_execucao": round(time.time() - start_time, 2),
                }

                # Validar resultado final
                if not isinstance(result.get("data"), dict):
                    self.logger.error("Resultado final inválido: data não é dict")
                    return None

                self.logger.info(f"Métricas formatadas com filtro de data: sucesso=True, tempo={result['tempo_execucao']}s")

            except Exception as e:
                self.logger.error(f"Erro ao construir resultado final: {e}")
                return None

            # Salvar no cache com TTL de 3 minutos
            try:
                self._set_cache_data(
                    "dashboard_metrics_filtered",
                    result,
                    ttl=180,
                    sub_key=cache_key,
                )
                self.logger.info(f"Resultado salvo no cache com chave: {cache_key}")
            except Exception as e:
                self.logger.warning(f"Erro ao salvar no cache: {e}")

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Erro geral em get_dashboard_metrics_with_date_filter após {execution_time:.2f}s: {e}"
            )
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
            return None

    def _get_trends_with_logging(
        self,
        general_novos: int,
        general_pendentes: int,
        general_progresso: int,
        general_resolvidos: int,
        start_date: str,
        end_date: str,
    ) -> dict:
        """Função auxiliar para fazer log e chamar _calculate_trends"""
        self.logger.info(f"Chamando _calculate_trends com start_date={start_date}, end_date={end_date}")
        return self._calculate_trends(
            general_novos,
            general_pendentes,
            general_progresso,
            general_resolvidos,
            start_date,
            end_date,
        )

    def _calculate_trends(
        self,
        current_novos: int,
        current_pendentes: int,
        current_progresso: int,
        current_resolvidos: int,
        current_start_date: Optional[str] = None,
        current_end_date: Optional[str] = None,
    ) -> dict:
        """Calcula as tendências comparando dados atuais com período anterior

        Args:
            current_novos: Número atual de tickets novos
            current_pendentes: Número atual de tickets pendentes
            current_progresso: Número atual de tickets em progresso
            current_resolvidos: Número atual de tickets resolvidos
            current_start_date: Data inicial do período atual (opcional)
            current_end_date: Data final do período atual (opcional)
        """
        self.logger.info(
            f"_calculate_trends chamada com: novos={current_novos}, pendentes={current_pendentes}, progresso={current_progresso}, resolvidos={current_resolvidos}, start_date={current_start_date}, end_date={current_end_date}"
        )
        try:
            # Se há filtros de data aplicados, calcular período anterior baseado neles
            if current_start_date and current_end_date:
                # Calcular a duração do período atual
                current_start = datetime.strptime(current_start_date, "%Y-%m-%d")
                current_end = datetime.strptime(current_end_date, "%Y-%m-%d")
                period_duration = (current_end - current_start).days

                # Calcular período anterior com a mesma duração
                end_date_previous = (current_start - timedelta(days=1)).strftime("%Y-%m-%d")
                start_date_previous = (current_start - timedelta(days=period_duration + 1)).strftime("%Y-%m-%d")

                self.logger.info(
                    f"Calculando tendências com filtro: período atual {current_start_date} a {current_end_date}, período anterior {start_date_previous} a {end_date_previous}"
                )
            else:
                # Usar período padrão de 7 dias
                end_date_previous = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                start_date_previous = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")

                self.logger.info(
                    f"Calculando tendências sem filtro: período anterior {start_date_previous} a {end_date_previous}"
                )

            # Obter métricas do período anterior
            previous_general = self._get_general_totals_internal(start_date_previous, end_date_previous)

            # Calcular totais do período anterior
            previous_novos = previous_general.get("Novo", 0)
            previous_pendentes = previous_general.get("Pendente", 0)
            previous_progresso = previous_general.get("Processando (atribuído)", 0) + previous_general.get(
                "Processando (planejado)", 0
            )
            previous_resolvidos = previous_general.get("Solucionado", 0) + previous_general.get("Fechado", 0)

            self.logger.info(
                f"Dados período anterior: novos={previous_novos}, pendentes={previous_pendentes}, progresso={previous_progresso}, resolvidos={previous_resolvidos}"
            )
            self.logger.info(
                f"Dados período atual: novos={current_novos}, pendentes={current_pendentes}, progresso={current_progresso}, resolvidos={current_resolvidos}"
            )

            # Calcular percentuais de variação
            def calculate_percentage_change(current: int, previous: int) -> float:
                if previous == 0:
                    return 100.0 if current > 0 else 0.0

                change = ((current - previous) / previous) * 100
                return round(change, 1)

            trends = {
                "novos": calculate_percentage_change(current_novos, previous_novos),
                "pendentes": calculate_percentage_change(current_pendentes, previous_pendentes),
                "progresso": calculate_percentage_change(current_progresso, previous_progresso),
                "resolvidos": calculate_percentage_change(current_resolvidos, previous_resolvidos),
            }

            self.logger.info(f"Tendências calculadas: {trends}")
            return trends

        except Exception as e:
            self.logger.error(f"Erro ao calcular tendências: {e}")
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
            # Retornar valores padrão em caso de erro
            return {
                "novos": 0.0,
                "pendentes": 0.0,
                "progresso": 0.0,
                "resolvidos": 0.0,
            }

    def get_technician_ranking(self, limit: int = None) -> list:
        """Retorna ranking de técnicos por total de chamados seguindo a base de conhecimento

        Implementação otimizada que:
        1. Usa cache inteligente com TTL de 5 minutos
        2. Busca APENAS técnicos com perfil ID 6 (Técnico)
        3. Usa consulta direta sem iteração por todos os usuários
        4. Segue exatamente a estrutura da base de conhecimento
        """
        start_time = time.time()  # Definir start_time no início para evitar NameError
        try:
            # LIMPAR CACHE INTERNO FORÇADAMENTE - CORREÇÃO CRÍTICA
            # PROBLEMA IDENTIFICADO: Esta linha estava causando métricas zeradas
            # self._cache.clear()  # COMENTADO - Esta linha estava limpando o cache antes de usar
            self.logger.info(
                f"[{datetime.now(tz=timezone.utc).isoformat()}] Cache interno preservado para melhor performance"
            )

            # Validações de entrada
            if limit is not None:
                if not isinstance(limit, int):
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] limit deve ser int: {type(limit)}"
                    )
                    return []
                if limit <= 0:
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] limit deve ser positivo: {limit}"
                    )
                    return []

            # Validar configurações essenciais
            if not hasattr(self, "glpi_url") or not self.glpi_url:
                self.logger.error(f"[{datetime.now(tz=timezone.utc).isoformat()}] glpi_url não configurado")
                return []

            self.logger.info(
                f"[{datetime.now(tz=timezone.utc).isoformat()}] Iniciando get_technician_ranking com limit={limit}"
            )

            # Verificar cache com lógica inteligente
            cache_key = f"technician_ranking_{limit or 'all'}"
            try:
                cached_data = self._get_cache_data(cache_key)
                # Verificar se cache existe E não está vazio
                if cached_data and isinstance(cached_data, list) and len(cached_data) > 0:
                    self.logger.info(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Retornando ranking do cache: {len(cached_data)} técnicos"
                    )
                    return cached_data[:limit] if limit else cached_data
                else:
                    self.logger.info(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Cache vazio ou inválido, processando dados reais"
                    )
            except Exception as e:
                self.logger.warning(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao verificar cache interno: {e}"
                )

            # Verificar autenticação
            try:
                if not self._ensure_authenticated():
                    self.logger.error(f"[{datetime.now(tz=timezone.utc).isoformat()}] Falha na autenticação")
                    return []
            except Exception as e:
                self.logger.error(f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro na autenticação: {e}")
                return []

            # Implementação seguindo a base de conhecimento
            try:
                self.logger.info(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Chamando _get_technician_ranking_knowledge_base"
                )
                ranking = self._get_technician_ranking_knowledge_base()

                if not isinstance(ranking, list):
                    self.logger.error(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] ranking inválido: {type(ranking)}"
                    )
                    return []

                self.logger.info(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Resultado da busca: {len(ranking)} técnicos"
                )
            except Exception as e:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao obter ranking: {e}"
                )
                return []

            # Armazenar no cache com TTL otimizado para 5 minutos
            try:
                if ranking:
                    self._set_cache_data(cache_key, ranking, ttl=300)
                    self.logger.info(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Dados armazenados no cache por 5 minutos"
                    )
            except Exception as e:
                self.logger.warning(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao salvar no cache: {e}"
                )

            # Aplicar limite se especificado
            try:
                if limit and len(ranking) > limit:
                    ranking = ranking[:limit]
                    self.logger.info(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Ranking limitado a {limit} técnicos"
                    )
            except Exception as e:
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao aplicar limite: {e}"
                )
                return []

            execution_time = time.time() - start_time
            self.logger.info(
                f"[{datetime.now(tz=timezone.utc).isoformat()}] Ranking obtido com sucesso em {execution_time:.2f}s: {len(ranking)} técnicos"
            )
            return ranking

        except Exception as e:
            try:
                execution_time = time.time() - start_time
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro geral em get_technician_ranking após {execution_time:.2f}s: {e}"
                )
            except NameError:
                # start_time não foi definido devido a exceção muito cedo
                self.logger.error(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro geral em get_technician_ranking: {e}"
                )
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
            return []

    def _discover_tech_field_id(self) -> Optional[str]:
        """Descobre dinamicamente o field ID do técnico atribuído (com cache)"""
        # Verificar cache primeiro
        if hasattr(self, '_cached_tech_field_id') and self._cached_tech_field_id:
            return self._cached_tech_field_id

        try:
            self.logger.debug("Descobrindo field ID do técnico...")

            # Timeout reduzido para 10 segundos
            response = self._make_authenticated_request("GET", f"{self.glpi_url}/listSearchOptions/Ticket", timeout=10)
            if not response:
                self.logger.debug("Falha ao buscar search options do Ticket")
                # Cache fallback
                self._cached_tech_field_id = "5"
                return "5"

            search_options = response.json()

            # Procurar por campos conhecidos primeiro
            tech_field_mapping = {"5": "Técnico", "95": "Técnico encarregado"}

            for field_id, expected_name in tech_field_mapping.items():
                if field_id in search_options:
                    field_data = search_options[field_id]
                    if isinstance(field_data, dict) and "name" in field_data:
                        field_name = field_data["name"]
                        if field_name == expected_name:
                            self.logger.debug(f"Campo técnico encontrado: {field_name} (ID: {field_id})")
                            # Cache o resultado
                            self._cached_tech_field_id = field_id
                            return field_id

            # Fallback: procurar por nomes alternativos
            tech_field_names = [
                "Técnico",
                "Atribuído",
                "Assigned to",
                "Technician",
                "Técnico encarregado",
            ]

            for field_id, field_data in search_options.items():
                if isinstance(field_data, dict) and "name" in field_data:
                    field_name = field_data["name"]
                    if field_name in tech_field_names:
                        self.logger.debug(f"Campo técnico encontrado (fallback): {field_name} (ID: {field_id})")
                        # Cache o resultado
                        self._cached_tech_field_id = field_id
                        return field_id

            # Fallback final
            self.logger.debug("Campo de técnico não encontrado, usando fallback ID = 5")
            self._cached_tech_field_id = "5"
            return "5"

        except Exception as e:
            self.logger.debug(f"Erro ao descobrir field ID do técnico: {str(e)[:100]}")
            # Cache fallback em caso de erro
            self._cached_tech_field_id = "5"
            return "5"

    def _get_user_details_direct(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Busca direta de usuário por ID (otimizado)"""
        url = f"{self.glpi_url}/User/{user_id}"

        try:
            # Timeout reduzido para 10 segundos
            response = self._make_authenticated_request("GET", url, timeout=10)
            if not response or not response.ok:
                self.logger.debug(f"Usuário {user_id} não encontrado ou inacessível")
                return None

            user_data = response.json()

            # Verificação rápida de status
            is_active = str(user_data.get("is_active", "0")).strip()
            is_deleted = str(user_data.get("is_deleted", "0")).strip()

            if str(is_active) != "1" or str(is_deleted) == "1":
                return None

            # Construção otimizada do nome
            firstname = str(user_data.get("firstname", "")).strip()
            realname = str(user_data.get("realname", "")).strip()
            username = str(user_data.get("name", "")).strip()

            full_name = f"{firstname} {realname}".strip()
            if not full_name:
                full_name = username or f"Usuário {user_id}"

            return {
                "id": user_id,
                "name": full_name,
                "realname": realname,
                "firstname": firstname,
                "username": username,
            }

        except Exception as e:
            self.logger.debug(f"Erro ao buscar usuário {user_id}: {str(e)[:100]}")
            return None

    def _get_technician_level_by_name_fallback(self, user_id: str) -> str:
        """Determina o nível do técnico baseado no nome (fallback do backend)"""
        try:
            # Buscar nome do usuário
            user_url = f"{self.glpi_url}/User/{user_id}"
            response = self._make_authenticated_request("GET", user_url)
            if not response or response.status_code != 200:
                return "N1"  # Nível padrão

            user_data = response.json()
            firstname = user_data.get("firstname", "").lower()
            realname = user_data.get("realname", "").lower()

            # Mapeamento correto dos técnicos por nível (conforme backend real)
            n1_names = [
                "gabriel andrade da conceicao",
                "nicolas fernando muniz nunez",
            ]

            n2_names = [
                "alessandro carbonera vieira",
                "jonathan nascimento moletta",
                "thales vinicius paz leite",
                "leonardo trojan repiso riela",
                "edson joel dos santos silva",
                "luciano marcelino da silva",
                "joao pedro wilson dias",
            ]

            n3_names = [
                "anderson da silva morim de oliveira",
                "silvio godinho valim",
                "jorge antonio vicente júnior",
                "pablo hebling guimaraes",
                "miguelangelo ferreira",
            ]

            n4_names = [
                "gabriel silva machado",
                "luciano de araujo silva",
                "wagner mengue",
                "paulo césar pedó nunes",
                "alexandre rovinski almoarqueg",
            ]

            # Verificar em qual nível o técnico está
            full_name = f"{firstname} {realname}".strip()

            if full_name in n4_names:
                return "N4"
            elif full_name in n3_names:
                return "N3"
            elif full_name in n2_names:
                return "N2"
            elif full_name in n1_names:
                return "N1"
            else:
                # Se não encontrou, usar N1 como padrão
                return "N1"

        except Exception as e:
            self.logger.error(f"Erro ao determinar nível por nome para usuário {user_id}: {e}")
            return "N1"  # Nível padrão em caso de erro

    def _get_technician_metrics_corrected(self, tecnico_id: str) -> Dict[str, Any]:
        """Coleta métricas de performance de um técnico específico (otimizado)"""
        self.logger.debug(f"Coletando métricas do técnico {tecnico_id}")

        url = f"{self.glpi_url}/search/Ticket"

        # CORREÇÃO: Usar range maior para capturar todos os tickets dos técnicos
        # Range aumentado para evitar que técnicos com muitos tickets sejam zerados
        adaptive_range = "0-5000"  # Range aumentado para capturar mais tickets
        self.logger.debug(f"Usando range expandido para técnico {tecnico_id}: {adaptive_range}")

        # CACHE AGRESSIVO: Verificar se já temos dados em cache
        cache_key = f"technician_metrics_{tecnico_id}"
        cached_metrics = self._get_cache_data(cache_key)
        if cached_metrics:
            self.logger.debug(f"Cache hit para técnico {tecnico_id}")
            return cached_metrics

        # Buscar todos os tickets atribuídos ao técnico com timeout reduzido
        params = {
            "criteria[0][field]": 5,  # Campo técnico atribuído (FIXO)
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": tecnico_id,
            "forcedisplay[0]": 2,  # ID
            "forcedisplay[1]": 12,  # Status
            "range": adaptive_range,  # Range híbrido adaptativo
        }

        # Debug específico removido para produção
        if False:  # Debug removido para performance
            pass  # Debug logs removidos

        try:
            # Timeout reduzido para 15 segundos
            response = self._make_authenticated_request("GET", url, params=params, timeout=8)

            if not response or response.status_code != 200:
                self.logger.warning(f"Falha na requisição para técnico {tecnico_id}: {response.status_code if response else 'None'}")
                # Debug específico removido para produção
                if False:  # Debug removido para performance
                    pass  # Debug logs removidos
                return {
                    "total_tickets": 0,
                    "resolved_tickets": 0,
                    "pending_tickets": 0,
                    "avg_resolution_time": 0.0,
                }

            data = response.json()
            tickets = data.get("data", [])
            # initial_count = len(tickets)  # Commented out unused variable

            # FASE 2: Verificação de completude e fallback automático
            # TEMPORARIAMENTE DESABILITADO PARA MELHORAR PERFORMANCE
            # fallback_triggered = False  # Commented out unused variable
            # try:
            #     if hybrid_pagination.is_range_potentially_insufficient(tickets, adaptive_range):
            #         self.logger.warning(f"Range insuficiente detectado para {tech_name}: {initial_count} tickets")
            #
            #         # Calcular range estendido
            #         extended_range = hybrid_pagination.calculate_extended_range(adaptive_range)
            #         self.logger.info(f"Tentando fallback com range estendido: {extended_range}")
            #
            #         # Nova consulta com range estendido
            #         params["range"] = extended_range
            #         extended_response = self._make_authenticated_request("GET", url, params=params, timeout=8)
            #
            #         if extended_response and extended_response.status_code == 200:
            #             extended_data = extended_response.json()
            #             extended_tickets = extended_data.get("data", [])
            #
            #             if len(extended_tickets) > initial_count:
            #                 self.logger.info(f"Fallback bem-sucedido: {initial_count} → {len(extended_tickets)} tickets")
            #                 tickets = extended_tickets
            #                 adaptive_range = extended_range  # Atualizar range usado
            #                 fallback_triggered = True
            #             else:
            #                 self.logger.debug("Fallback não trouxe tickets adicionais")
            #         else:
            #             self.logger.warning("Falha na consulta de fallback")
            # except Exception as e:
            #     self.logger.error(f"Erro no fallback híbrido: {e}")

            total = len(tickets)
            resolvidos = 0
            pendentes = 0

            # Processamento otimizado sem logs excessivos
            for ticket in tickets:
                try:
                    status_id = int(ticket.get("12", 0))
                    if status_id in [5, 6]:  # Solucionado ou Fechado
                        resolvidos += 1
                    elif status_id in [2, 3, 4]:  # Em progresso, Planejado, Pendente
                        pendentes += 1
                except (ValueError, TypeError):
                    continue  # Ignorar tickets com status inválido

            self.logger.debug(f"Técnico {tecnico_id}: {total} tickets ({resolvidos} resolvidos, {pendentes} pendentes)")

            # Atualizar cache do sistema híbrido
            # try:
            #     hybrid_pagination.update_technician_cache(
            #         tecnico_id,
            #         tech_name or f"Técnico {tecnico_id}",
            #         adaptive_range,
            #         total,
            #         fallback_triggered
            #     )
            # except Exception as e:
            #     self.logger.debug(f"Erro ao atualizar stats de paginação: {e}")

            result = {
                "total_tickets": total,
                "resolved_tickets": resolvidos,
                "pending_tickets": pendentes,
                "avg_resolution_time": 0.0,
            }

            # CACHE AGRESSIVO: Salvar resultado em cache por 1 hora
            self._set_cache_data(cache_key, result, ttl=3600)
            self.logger.debug(f"Cache salvo para técnico {tecnico_id}")

            return result

        except Exception as e:
            self.logger.error(f"Erro ao buscar métricas do técnico {tecnico_id}: {e}")
            return {
                "total_tickets": 0,
                "resolved_tickets": 0,
                "pending_tickets": 0,
                "avg_resolution_time": 0.0,
            }

    def _get_technician_ranking_knowledge_base(self) -> list:
        """Implementação otimizada baseada nos scripts que funcionam - busca direta por ID

        Esta implementação usa a mesma abordagem dos scripts com otimizações:
        1. Lista hardcoded de IDs de técnicos conhecidos
        2. Cache do field ID para evitar descoberta repetida
        3. Processamento paralelo das métricas
        4. Validação direta de ativo/não deletado
        """
        try:
            self.logger.info("=== DEBUG BUSCA DE TÉCNICOS OTIMIZADA ===")

            # Validar configurações essenciais
            if not hasattr(self, "glpi_url") or not self.glpi_url:
                self.logger.error("❌ glpi_url não configurado")
                return []

            self.logger.info(f"🔗 GLPI URL: {self.glpi_url}")

            # IDs dos técnicos válidos da entidade CAU (mesmo dos scripts)
            technician_ids = [
                "696", "32", "141", "60", "69", "1032", "252", "721", "926", "1291",
                "185", "1331", "1404", "1088", "1263", "10", "53", "250", "1471",
            ]

            self.logger.info(f"📋 Lista de técnicos para verificar: {len(technician_ids)} IDs")

            # Cache do field ID para evitar descoberta repetida
            if not hasattr(self, '_cached_tech_field_id'):
                self._cached_tech_field_id = self._discover_tech_field_id()
                if not self._cached_tech_field_id:
                    self.logger.error("❌ Não foi possível descobrir o field ID do técnico")
                    return []
                self.logger.info(f"🔍 Field ID do técnico descoberto e cacheado: {self._cached_tech_field_id}")

            # Buscar detalhes de todos os técnicos em paralelo
            technician_candidates = []
            import concurrent.futures

            def get_technician_data(tech_id):
                try:
                    user_details = self._get_user_details_direct(tech_id)
                    if user_details:
                        return {
                            "id": tech_id,
                            "name": user_details["name"],
                            "realname": user_details["realname"],
                            "firstname": user_details["firstname"],
                        }
                except Exception as e:
                    self.logger.error(f"❌ Erro ao processar técnico {tech_id}: {e}")
                return None

            # Processar técnicos em paralelo (otimizado para 5 threads para melhor estabilidade)
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_tech = {executor.submit(get_technician_data, tech_id): tech_id for tech_id in technician_ids}

                for future in concurrent.futures.as_completed(future_to_tech):
                    tech_id = future_to_tech[future]
                    try:
                        result = future.result(timeout=15)  # Timeout otimizado para 15s por técnico
                        if result:
                            technician_candidates.append(result)
                            self.logger.info(f"✅ Técnico encontrado: {result['name']} (ID: {tech_id})")
                        else:
                            self.logger.warning(f"⚠️ Técnico não encontrado ou inativo: {tech_id}")
                    except concurrent.futures.TimeoutError:
                        self.logger.error(f"⏰ Timeout ao processar técnico {tech_id}")
                    except Exception as e:
                        self.logger.error(f"❌ Erro ao processar técnico {tech_id}: {e}")

            self.logger.info(f"📊 Total de técnicos candidatos encontrados: {len(technician_candidates)}")

            if not technician_candidates:
                self.logger.warning("⚠️ Nenhum técnico candidato encontrado")
                return []

            # Construir ranking com processamento otimizado
            def get_technician_metrics_and_level(tech):
                try:
                    tech_id = tech["id"]
                    # Buscar métricas e nível em paralelo
                    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                        # Submeter tarefas em paralelo
                        metrics_future = executor.submit(self._get_technician_metrics_corrected, tech_id)
                        level_future = executor.submit(self._get_technician_level_by_name_fallback, tech_id)

                        # Aguardar resultados
                        metricas = metrics_future.result(timeout=15)
                        tech_level = level_future.result(timeout=15)

                    return {
                        "id": tech_id,
                        "name": tech["name"],
                        "nome": tech["name"],
                        "total_tickets": metricas["total_tickets"],
                        "resolved_tickets": metricas["resolved_tickets"],
                        "pending_tickets": metricas["pending_tickets"],
                        "avg_resolution_time": metricas["avg_resolution_time"],
                        "level": tech_level,
                        "rank": 0,
                    }
                except Exception as e:
                    self.logger.error(f"❌ Erro ao processar métricas do técnico {tech['id']}: {e}")
                    return None

            ranking = []
            # Processar métricas em paralelo (máximo 3 threads para não sobrecarregar)
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                future_to_tech = {executor.submit(get_technician_metrics_and_level, tech): tech for tech in technician_candidates}

                for future in concurrent.futures.as_completed(future_to_tech):
                    tech = future_to_tech[future]
                    try:
                        result = future.result(timeout=30)  # Timeout otimizado para 30s por técnico
                        if result:
                            ranking.append(result)
                            self.logger.info(f"📊 TÉCNICO {result['name']} (ID: {result['id']}): Total={result['total_tickets']}, Nível={result['level']}")
                    except concurrent.futures.TimeoutError:
                        self.logger.error(f"⏰ Timeout ao processar métricas do técnico {tech['id']}")
                    except Exception as e:
                        self.logger.error(f"❌ Erro ao processar métricas do técnico {tech['id']}: {e}")

            # Ordenar por total de tickets
            ranking.sort(key=lambda x: x["total_tickets"], reverse=True)

            # Atribuir ranks
            for i, tech in enumerate(ranking):
                tech["rank"] = i + 1

            self.logger.info(f"🏆 Ranking final construído com {len(ranking)} técnicos")

            return ranking

        except Exception as e:
            self.logger.error(f"❌ Erro geral na busca de técnicos: {e}")
            return []

    def _get_technician_level(
        self,
        user_id: int,
        total_tickets: int = 0,
        all_technicians_data: list = None,
    ) -> str:
        """Atribui nível do técnico baseado nos grupos do GLPI

        Mapeamento correto dos técnicos por grupos:
        - N1 (ID 89): Gabriel Andrade da Conceicao, Nicolas Fernando Muniz Nunez
        - N2 (ID 90): Alessandro Carbonera Vieira, Edson Joel dos Santos Silva, Luciano Marcelino da Silva,
            Jonathan Nascimento Moletta, Leonardo Trojan Repiso Riela, Thales Vinicius Paz Leite, Joao Pedro Wilson Dias
        - N3 (ID 91): Jorge Antonio Vicente Júnior, Anderson da Silva Morim de Oliveira, Miguelangelo Ferreira,
            Silvio Godinho Valim, Pablo Hebling Guimaraes
        - N4 (ID 92): Paulo César Pedó Nunes, Luciano de Araujo Silva, Wagner Mengue,
            Alexandre Rovinski Almoarqueg, Gabriel Silva Machado
        """
        try:
            # Validar configuração
            if not self.glpi_url:
                self.logger.error("URL do GLPI não configurada")
                return "N1"

            # Buscar grupos do usuário com tratamento de erros
            try:
                response = self._make_authenticated_request(
                    "GET",
                    f"{self.glpi_url}/search/Group_User",
                    params={
                        "range": "0-99",
                        "criteria[0][field]": "4",  # Campo users_id
                        "criteria[0][searchtype]": "equals",
                        "criteria[0][value]": str(user_id),
                        "forcedisplay[0]": "3",  # groups_id
                        "forcedisplay[1]": "4",  # users_id
                    },
                    timeout=10,
                )

                if response and response.ok:
                    try:
                        group_data = response.json()

                        if group_data and isinstance(group_data, dict) and group_data.get("data"):
                            for group_entry in group_data["data"]:
                                if isinstance(group_entry, dict) and "3" in group_entry:
                                    try:
                                        group_id = int(group_entry["3"])

                                        # Verificar se o grupo corresponde aos service_levels
                                        for (
                                            level,
                                            level_group_id,
                                        ) in self.service_levels.items():
                                            if group_id == level_group_id:
                                                self.logger.info(
                                                    f"Técnico {user_id} encontrado no grupo {group_id} -> {level}"
                                                )
                                                return level
                                    except (
                                        ValueError,
                                        TypeError,
                                    ) as parse_error:
                                        self.logger.warning(
                                            f"Erro ao processar group_id para usuário {user_id}: {parse_error}"
                                        )
                                        continue
                    except ValueError as json_error:
                        self.logger.error(
                            f"Erro ao decodificar JSON da resposta de grupos para usuário {user_id}: {json_error}"
                        )
                else:
                    self.logger.warning(
                        f"Falha na busca de grupos para usuário {user_id}: {response.status_code if response else 'Sem resposta'}"
                    )
            except requests.exceptions.Timeout:
                self.logger.error(f"Timeout na busca de grupos para usuário {user_id}")
            except requests.exceptions.ConnectionError:
                self.logger.error(f"Erro de conexão na busca de grupos para usuário {user_id}")
            except requests.exceptions.RequestException as req_error:
                self.logger.error(f"Erro na requisição de grupos para usuário {user_id}: {req_error}")
            except Exception as groups_error:
                self.logger.error(f"Erro inesperado na busca de grupos para usuário {user_id}: {groups_error}")

            # Se não encontrou nos grupos configurados, usar fallback baseado no nome do usuário
            # (para casos onde o técnico não está nos grupos mas está na lista fornecida)
            try:
                user_response = self._make_authenticated_request("GET", f"{self.glpi_url}/User/{user_id}", timeout=10)

                if user_response and user_response.ok:
                    try:
                        user_data = user_response.json()

                        if user_data and isinstance(user_data, dict):
                            # Construir nome completo como no método get_technician_ranking
                            display_name = ""
                            if "realname" in user_data and "firstname" in user_data:
                                display_name = f"{user_data['firstname']} {user_data['realname']}"
                            elif "realname" in user_data:
                                display_name = user_data["realname"]
                            elif "name" in user_data:
                                display_name = user_data["name"]
                            elif "1" in user_data:
                                display_name = user_data["1"]

                            if display_name and display_name.strip():
                                user_name = display_name.lower().strip()

                                # Mapeamento manual baseado nos nomes exatos do GLPI
                                n1_names = [
                                    "gabriel andrade da conceicao",
                                    "nicolas fernando muniz nunez",
                                ]
                                n2_names = [
                                    "alessandro carbonera vieira",
                                    "jonathan nascimento moletta",
                                    "thales vinicius paz leite",
                                    "leonardo trojan repiso riela",
                                    "edson joel dos santos silva",
                                    "luciano marcelino da silva",
                                    "joao pedro wilson dias",
                                ]
                                n3_names = [
                                    "anderson da silva morim de oliveira",
                                    "silvio godinho valim",
                                    "jorge antonio vicente júnior",
                                    "pablo hebling guimaraes",
                                    "miguelangelo ferreira",
                                ]
                                n4_names = [
                                    "gabriel silva machado",
                                    "luciano de araujo silva",
                                    "wagner mengue",
                                    "paulo césar pedó nunes",
                                    "alexandre rovinski almoarqueg",
                                ]

                                if user_name in n4_names:
                                    self.logger.info(f"Técnico {user_id} ({user_name}) mapeado para N4 por nome")
                                    return "N4"
                                elif user_name in n3_names:
                                    self.logger.info(f"Técnico {user_id} ({user_name}) mapeado para N3 por nome")
                                    return "N3"
                                elif user_name in n2_names:
                                    self.logger.info(f"Técnico {user_id} ({user_name}) mapeado para N2 por nome")
                                    return "N2"
                                elif user_name in n1_names:
                                    self.logger.info(f"Técnico {user_id} ({user_name}) mapeado para N1 por nome")
                                    return "N1"
                            else:
                                self.logger.warning(f"Nome de usuário vazio ou inválido para usuário {user_id}")
                        else:
                            self.logger.warning(f"Dados de usuário inválidos para usuário {user_id}")
                    except ValueError as json_error:
                        self.logger.error(f"Erro ao decodificar JSON dos dados do usuário {user_id}: {json_error}")
                else:
                    self.logger.warning(
                        f"Falha na busca de dados do usuário {user_id}: {user_response.status_code if user_response else 'Sem resposta'}"
                    )
            except requests.exceptions.Timeout:
                self.logger.error(f"Timeout na busca de dados do usuário {user_id}")
            except requests.exceptions.ConnectionError:
                self.logger.error(f"Erro de conexão na busca de dados do usuário {user_id}")
            except requests.exceptions.RequestException as req_error:
                self.logger.error(f"Erro na requisição de dados do usuário {user_id}: {req_error}")
            except Exception as user_error:
                self.logger.error(f"Erro inesperado na busca de dados do usuário {user_id}: {user_error}")

            # Fallback final
            self.logger.warning(f"Técnico {user_id} não encontrado nos grupos ou mapeamento - usando N1 como padrão")
            return "N1"

        except Exception as e:
            self.logger.error(f"Erro ao determinar nível do técnico {user_id}: {e}")
            return "N1"  # Nível padrão em caso de erro

    def _get_technician_level_by_name(self, tech_name: str) -> str:
        """Determina o nível do técnico baseado apenas no nome (fallback)"""
        try:
            # Mapeamento completo atualizado de técnicos por nível
            # Gerado automaticamente em 2025-08-16 23:27:01
            n1_names = {
                "gabriel andrade da conceicao",
                "nicolas fernando muniz nunez",
                # Mapeamento legado mantido para compatibilidade
                "Jonathan Moletta",
                "Thales Lemos",
                "Leonardo Riela",
                "Luciano Silva",
                "Thales Leite",
                "jonathan-moletta",
                "thales-leite",
                "leonardo-riela",
                "luciano-silva",
            }

            n2_names = {
                "alessandro carbonera vieira",
                "edson joel dos santos silva",
                "jonathan nascimento moletta",
                "leonardo trojan repiso riela",
                "luciano marcelino da silva",
                "thales vinicius paz leite",
                # Mapeamento legado mantido para compatibilidade
                "Gabriel Conceição",
                "Luciano Araújo",
                "Alice Dutra",
                "Luan Medeiros",
                "gabriel-conceicao",
                "luciano-araujo",
                "alice-dutra",
                "luan-medeiros",
            }

            n3_names = {
                "anderson da silva morim de oliveira",
                "jorge antonio vicente júnior",
                "miguelangelo ferreira",
                "pablo hebling guimaraes",
                "silvio godinho valim",
                # Mapeamento legado mantido para compatibilidade
                "Gabriel Machado",
                "Luciano Marcelino",
                "Jorge Swift",
                "Anderson Morim",
                "Davi Freitas",
                "Lucas Sergio",
                "gabriel-machado",
                "luciano-marcelino",
                "jorge-swift",
                "anderson-oliveira",
                "davi-freitas",
                "lucas-sergio-t1",
            }

            n4_names = {
                "alexandre rovinski almoarqueg",
                "gabriel silva machado",
                "luciano de araujo silva",
                "paulo césar pedó nunes",
                "wagner mengue",
                # Mapeamento legado mantido para compatibilidade
                "Anderson Oliveira",
                "Silvio Godinho",
                "Edson Joel",
                "Paulo Pedó",
                "Pablo Hebling",
                "Leonardo Riela",
                "Alessandro Carbonera",
                "Miguel Angelo",
                "José Barros",
                "Nicolas Nunez",
                "Wagner Mengue",
                "Silvio Valim",
                "anderson-oliveira",
                "silvio-godinho",
                "edson-joel",
                "paulo-pedó",
                "pablo-hebling",
                "leonardo-rielaantigo",
                "alessandro-carbonera",
                "miguelangelo-old",
                "jose-barros",
                "nicolas-nunez",
                "wagner-mengue",
                "silvio-valim",
            }

            # Limpar o nome se vier no formato "Técnico nome-id"
            clean_name = tech_name
            if tech_name.startswith("Técnico "):
                clean_name = tech_name.replace("Técnico ", "").strip()

            # Verificar correspondência exata primeiro
            if clean_name in n4_names or tech_name in n4_names:
                self.logger.info(f"Técnico {tech_name} mapeado para N4 por nome")
                return "N4"
            elif clean_name in n3_names or tech_name in n3_names:
                self.logger.info(f"Técnico {tech_name} mapeado para N3 por nome")
                return "N3"
            elif clean_name in n2_names or tech_name in n2_names:
                self.logger.info(f"Técnico {tech_name} mapeado para N2 por nome")
                return "N2"
            elif clean_name in n1_names or tech_name in n1_names:
                self.logger.info(f"Técnico {tech_name} mapeado para N1 por nome")
                return "N1"

            # Fallback para correspondência parcial (case-insensitive)
            tech_name_lower = tech_name.lower()

            for name in n4_names:
                if name.lower() in tech_name_lower or tech_name_lower in name.lower():
                    self.logger.info(f"Técnico {tech_name} mapeado para N4 por correspondência parcial com {name}")
                    return "N4"

            for name in n3_names:
                if name.lower() in tech_name_lower or tech_name_lower in name.lower():
                    self.logger.info(f"Técnico {tech_name} mapeado para N3 por correspondência parcial com {name}")
                    return "N3"

            for name in n2_names:
                if name.lower() in tech_name_lower or tech_name_lower in name.lower():
                    self.logger.info(f"Técnico {tech_name} mapeado para N2 por correspondência parcial com {name}")
                    return "N2"

            for name in n1_names:
                if name.lower() in tech_name_lower or tech_name_lower in name.lower():
                    self.logger.info(f"Técnico {tech_name} mapeado para N1 por correspondência parcial com {name}")
                    return "N1"

            # Fallback final
            self.logger.warning(f"Técnico {tech_name} não encontrado no mapeamento por nome - usando N1 como padrão")
            return "N1"

        except Exception as e:
            self.logger.error(f"Erro ao determinar nível do técnico por nome {tech_name}: {e}")
            return "N1"  # Nível padrão em caso de erro

    def _get_technician_ranking_fallback(self) -> list:
        """Método de fallback usando a implementação original mais robusta"""
        try:
            # Validar configuração
            if not self.glpi_url:
                self.logger.error("URL do GLPI não configurada para fallback")
                return []

            # Usar método original como fallback
            try:
                active_techs = self._list_active_technicians_fallback()
                if not active_techs:
                    self.logger.warning("Nenhum técnico ativo encontrado no fallback")
                    return []
            except Exception as techs_error:
                self.logger.error(f"Erro ao buscar técnicos ativos no fallback: {techs_error}")
                return []

            try:
                tech_field_id = self._discover_tech_field_id()
                if not tech_field_id:
                    self.logger.error("ID do campo de técnico não encontrado no fallback")
                    return []
            except Exception as field_error:
                self.logger.error(f"Erro ao descobrir ID do campo de técnico no fallback: {field_error}")
                return []

            ranking = []
            for tech_id, tech_name in active_techs:
                try:
                    if not tech_name or not tech_name.strip():
                        self.logger.warning(f"Nome de técnico inválido para ID {tech_id}")
                        continue

                    total_tickets = self._count_tickets_by_technician(tech_id, tech_field_id)
                    if total_tickets is not None and isinstance(total_tickets, int) and total_tickets >= 0:
                        ranking.append(
                            {
                                "id": str(tech_id),
                                "nome": tech_name.strip(),
                                "name": tech_name.strip(),
                                "total_tickets": total_tickets,
                                "resolved_tickets": 0,
                                "pending_tickets": 0,
                                "avg_resolution_time": 0.0,
                            }
                        )
                    else:
                        self.logger.warning(
                            f"Contagem de tickets inválida para técnico {tech_name} (ID: {tech_id}): {total_tickets}"
                        )
                except Exception as ticket_error:
                    self.logger.error(f"Erro ao contar tickets para técnico {tech_name} (ID: {tech_id}): {ticket_error}")
                    continue

            if not ranking:
                self.logger.warning("Nenhum técnico válido encontrado no fallback")
                return []

            try:
                # Ordenar e atribuir ranks
                ranking.sort(key=lambda x: x.get("total", 0), reverse=True)
                for idx, item in enumerate(ranking, start=1):
                    item["rank"] = idx
                    # Atribuir nível usando o método existente
                    try:
                        user_id = int(item["id"])
                        level = self._get_technician_level(user_id, item["total"], ranking)
                        item["level"] = level
                    except Exception as level_error:
                        self.logger.error(
                            f"Erro ao atribuir nível para técnico {item.get('name', 'Desconhecido')}: {level_error}"
                        )
                        item["level"] = "N1"
            except Exception as sort_error:
                self.logger.error(f"Erro ao processar ranking final no fallback: {sort_error}")
                return []

            self.logger.info(f"Fallback concluído com {len(ranking)} técnicos")
            return ranking

        except Exception as e:
            self.logger.error(f"Erro crítico no método de fallback: {e}")
            self.logger.error(f"Stack trace do fallback: {traceback.format_exc()}")
            return []

    def _list_active_technicians_fallback(self) -> list:
        """Método de fallback para listar técnicos ativos (implementação original)"""
        # Verificar cache primeiro
        cache_key = "active_technicians"
        try:
            cached_data = self._get_cached_data(cache_key)
            if cached_data is not None:
                self.logger.info("Retornando lista de técnicos ativos do cache")
                return cached_data
        except Exception as cache_error:
            self.logger.warning(f"Erro ao verificar cache de técnicos ativos: {cache_error}")

        try:
            # Validar configuração
            if not self.glpi_url:
                self.logger.error("URL do GLPI não configurada para fallback")
                return []

            # Buscar usuários com perfil de técnico (ID 6) usando paginação robusta
            base_params = {
                "criteria[0][field]": "profiles_id",
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": 6,  # ID do perfil de técnico
            }

            try:
                import time

                profile_users = []
                page_size = 1000
                start_index = 0
                max_retries = 3

                self.logger.info("Iniciando busca paginada de usuários com perfil de técnico")

                while True:
                    # Configurar range para esta página
                    end_index = start_index + page_size - 1
                    current_params = base_params.copy()
                    current_params["range"] = f"{start_index}-{end_index}"

                    retry_count = 0
                    page_data = None

                    # Tentar buscar esta página com retry
                    while retry_count < max_retries:
                        try:
                            response = self._make_authenticated_request(
                                "GET",
                                f"{self.glpi_url}/Profile_User",
                                params=current_params,
                                timeout=30,
                            )

                            if not response or not response.ok:
                                raise Exception(f"Falha na requisição: {response.status_code if response else 'No response'}")

                            page_data = response.json()
                            break  # Sucesso, sair do loop de retry

                        except Exception as e:
                            retry_count += 1
                            if retry_count < max_retries:
                                wait_time = 2**retry_count
                                self.logger.warning(
                                    f"Erro na página {start_index}-{end_index}, tentativa {retry_count}/{max_retries}: {e}. Aguardando {wait_time}s..."
                                )
                                time.sleep(wait_time)
                            else:
                                self.logger.error(
                                    f"Falha após {max_retries} tentativas na página {start_index}-{end_index}: {e}"
                                )
                                raise

                    # Processar dados da página
                    if not page_data or not isinstance(page_data, list) or not page_data:
                        self.logger.info(f"Página {start_index}-{end_index} vazia ou sem dados. Finalizando paginação.")
                        break

                    page_items = len(page_data)
                    profile_users.extend(page_data)

                    self.logger.debug(
                        f"Processados {page_items} Profile_User na página {start_index}-{end_index}. Total: {len(profile_users)}"
                    )

                    # Verificar se chegamos ao fim
                    if page_items < page_size:
                        self.logger.info(f"Última página processada. Total de Profile_User: {len(profile_users)}")
                        break

                    # Avançar para próxima página
                    start_index += page_size

                    # Limite de segurança
                    if start_index > 50000:
                        self.logger.warning(
                            f"Limite de segurança atingido em {start_index} Profile_User. Finalizando paginação."
                        )
                        break

                if not profile_users:
                    self.logger.warning("Nenhum usuário encontrado com perfil de técnico")
                    return []

            except requests.exceptions.Timeout:
                self.logger.error("Timeout na busca de usuários com perfil de técnico")
                return []
            except requests.exceptions.ConnectionError:
                self.logger.error("Erro de conexão na busca de usuários com perfil de técnico")
                return []
            except requests.exceptions.RequestException as req_error:
                self.logger.error(f"Erro na requisição de usuários com perfil de técnico: {req_error}")
                return []

            self.logger.info(f"Encontrados {len(profile_users)} registros de Profile_User com perfil de técnico")

            # Extrair IDs dos usuários com validação
            tech_user_ids = []
            for profile_user in profile_users:
                if isinstance(profile_user, dict) and "users_id" in profile_user:
                    try:
                        user_id = int(profile_user["users_id"])
                        if user_id > 0:
                            tech_user_ids.append(user_id)
                    except (ValueError, TypeError) as parse_error:
                        self.logger.warning(
                            f"ID de usuário inválido em Profile_User: {profile_user.get('users_id', 'N/A')} - {parse_error}"
                        )
                        continue

            if not tech_user_ids:
                self.logger.warning("Nenhum usuário válido encontrado com perfil de técnico")
                return []

            # Buscar dados completos dos usuários em lotes para otimizar
            technicians = []
            batch_size = 10  # Processar em lotes de 10

            for i in range(0, len(tech_user_ids), batch_size):
                batch_ids = tech_user_ids[i : i + batch_size]
                self.logger.info(f"Processando lote {i // batch_size + 1}: IDs {batch_ids}")

                for user_id in batch_ids:
                    try:
                        user_response = self._make_authenticated_request(
                            "GET",
                            f"{self.glpi_url}/User/{user_id}",
                            timeout=10,
                        )

                        if user_response and user_response.ok:
                            try:
                                user_data = user_response.json()

                                if not user_data or not isinstance(user_data, dict):
                                    self.logger.warning(f"Dados de usuário inválidos para ID {user_id}")
                                    continue

                                # Verificar se o usuário está ativo e não deletado
                                try:
                                    is_active = user_data.get("is_active", 0)
                                    is_deleted = user_data.get("is_deleted", 1)

                                    # Validar valores
                                    if isinstance(is_active, str):
                                        is_active = int(is_active) if is_active.isdigit() else 0
                                    if isinstance(is_deleted, str):
                                        is_deleted = int(is_deleted) if is_deleted.isdigit() else 1

                                    if is_active == 1 and is_deleted == 0:
                                        # Construir nome de exibição com validação
                                        display_name = ""
                                        try:
                                            if user_data.get("realname") and user_data.get("firstname"):
                                                display_name = f"{user_data['firstname']} {user_data['realname']}"
                                            elif user_data.get("realname"):
                                                display_name = user_data["realname"]
                                            elif user_data.get("name"):
                                                display_name = user_data["name"]
                                            else:
                                                display_name = f"Usuário {user_id}"

                                            # Validar e limpar nome
                                            if display_name and isinstance(display_name, str):
                                                display_name = display_name.strip()
                                                if display_name:
                                                    technicians.append((user_id, display_name))
                                                    self.logger.info(
                                                        f"Técnico ativo encontrado: {display_name} (ID: {user_id})"
                                                    )
                                                else:
                                                    self.logger.warning(f"Nome de exibição vazio para usuário {user_id}")
                                            else:
                                                self.logger.warning(
                                                    f"Nome de exibição inválido para usuário {user_id}: {display_name}"
                                                )

                                        except Exception as name_error:
                                            self.logger.error(
                                                f"Erro ao construir nome de exibição para usuário {user_id}: {name_error}"
                                            )
                                            continue
                                    else:
                                        self.logger.debug(
                                            f"Usuário {user_id} não está ativo ou foi deletado (ativo: {is_active}, deletado: {is_deleted})"
                                        )

                                except (
                                    ValueError,
                                    TypeError,
                                ) as validation_error:
                                    self.logger.error(f"Erro ao validar status do usuário {user_id}: {validation_error}")
                                    continue

                            except ValueError as json_error:
                                self.logger.error(f"Erro ao decodificar JSON do usuário {user_id}: {json_error}")
                                continue
                        else:
                            self.logger.warning(
                                f"Resposta inválida para usuário {user_id}: {user_response.status_code if user_response else 'Sem resposta'}"
                            )

                    except requests.exceptions.Timeout:
                        self.logger.error(f"Timeout na busca do usuário {user_id}")
                        continue
                    except requests.exceptions.ConnectionError:
                        self.logger.error(f"Erro de conexão na busca do usuário {user_id}")
                        continue
                    except requests.exceptions.RequestException as req_error:
                        self.logger.error(f"Erro na requisição do usuário {user_id}: {req_error}")
                        continue
                    except Exception as user_error:
                        self.logger.error(f"Erro inesperado ao processar usuário {user_id}: {user_error}")
                        continue

            # Armazenar no cache com tratamento de erro
            try:
                self._set_cached_data(cache_key, technicians)
                self.logger.info("Lista de técnicos armazenada no cache com sucesso")
            except Exception as cache_error:
                self.logger.warning(f"Erro ao armazenar técnicos no cache: {cache_error}")

            self.logger.info(f"Total de técnicos ativos válidos encontrados: {len(technicians)}")
            return technicians

        except Exception as e:
            self.logger.error(f"Erro geral ao listar técnicos ativos (fallback): {e}")
            return []

    def _count_tickets_by_technician_optimized(self, tech_id: int, tech_field_id: str) -> Optional[int]:
        """Conta tickets por técnico seguindo a base de conhecimento

        Usa range 0-0 para retornar apenas contagem (otimizado)
        Corrigido para usar campo 4 (users_id_tech) como o método que funciona
        """
        try:
            # Validar parâmetros de entrada
            if not tech_id or not isinstance(tech_id, int) or tech_id <= 0:
                self.logger.error(f"ID de técnico inválido: {tech_id}")
                return None

            if not self.glpi_url:
                self.logger.error("URL do GLPI não configurada para contagem de tickets")
                return None

            # Usar o tech_field_id descoberto dinamicamente
            tech_field = tech_field_id

            # Parâmetros seguindo a base de conhecimento
            params = {
                "is_deleted": 0,
                "criteria[0][field]": tech_field,  # Campo users_id_tech (field 4)
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(tech_id),  # Garantir que seja string
                "range": "0-0",  # Retorna apenas contagem
            }

            self.logger.info(f"Contando tickets para técnico {tech_id} com field {tech_field}")

            try:
                response = self._make_authenticated_request(
                    "GET",
                    f"{self.glpi_url}/search/Ticket",
                    params=params,
                    timeout=30,
                )

                if not response:
                    self.logger.error(f"Falha na requisição para contar tickets do técnico {tech_id}")
                    return None

                if not response.ok:
                    self.logger.error(f"Erro HTTP na contagem de tickets do técnico {tech_id}: {response.status_code}")
                    return None

            except requests.exceptions.Timeout:
                self.logger.error(f"Timeout na contagem de tickets do técnico {tech_id}")
                return None
            except requests.exceptions.ConnectionError:
                self.logger.error(f"Erro de conexão na contagem de tickets do técnico {tech_id}")
                return None
            except requests.exceptions.RequestException as req_error:
                self.logger.error(f"Erro na requisição de contagem de tickets do técnico {tech_id}: {req_error}")
                return None

            # Extrair total do cabeçalho Content-Range com validação
            try:
                if "Content-Range" in response.headers:
                    content_range = response.headers["Content-Range"]

                    if not content_range or not isinstance(content_range, str):
                        self.logger.warning(f"Content-Range inválido para técnico {tech_id}: {content_range}")
                        return 0

                    # Formato esperado: "items 0-0/total" ou "items */total"
                    if "/" in content_range:
                        total_str = content_range.split("/")[-1].strip()
                        if total_str.isdigit():
                            total = int(total_str)
                            if total >= 0:
                                self.logger.info(f"Técnico {tech_id}: {total} tickets encontrados")
                                return total
                            else:
                                self.logger.warning(f"Total de tickets negativo para técnico {tech_id}: {total}")
                                return 0
                        else:
                            self.logger.warning(f"Total de tickets não numérico para técnico {tech_id}: {total_str}")
                            return 0
                    else:
                        self.logger.warning(f"Formato de Content-Range inválido para técnico {tech_id}: {content_range}")
                        return 0
                else:
                    self.logger.warning(f"Content-Range não encontrado para técnico {tech_id}")
                    # Fallback: tentar extrair do JSON
                    try:
                        result = response.json()
                        if isinstance(result, dict) and "totalcount" in result:
                            total = result["totalcount"]
                            self.logger.info(f"Técnico {tech_id}: {total} tickets encontrados (JSON fallback)")
                            return total
                        elif isinstance(result, dict) and "data" in result:
                            total = len(result["data"])
                            self.logger.info(f"Técnico {tech_id}: {total} tickets encontrados (data length)")
                            return total
                    except Exception as json_error:
                        self.logger.warning(f"Erro ao processar resposta JSON: {json_error}")
                    return 0

            except (ValueError, IndexError, AttributeError) as parse_error:
                self.logger.error(f"Erro ao processar Content-Range para técnico {tech_id}: {parse_error}")
                return 0

        except Exception as e:
            self.logger.error(f"Erro geral ao contar tickets do técnico {tech_id}: {e}")
            return None

    def _count_tickets_by_technician(self, tech_id: int, tech_field_id: str) -> Optional[int]:
        """Método mantido para compatibilidade - redireciona para versão otimizada"""
        return self._count_tickets_by_technician_optimized(tech_id, tech_field_id)

    def _get_technician_ticket_details(self, tech_id: int, tech_field_id: str) -> Optional[dict]:
        """Obtém dados detalhados dos tickets de um técnico (versão legacy - usa função otimizada)

        Retorna:
        {
            "total_tickets": int,
            "resolved_tickets": int,
            "pending_tickets": int,
            "avg_resolution_time": float
        }
        """
        try:
            # Usar a versão otimizada para um único técnico
            result = self._get_technician_ticket_details_optimized([tech_id], tech_field_id)
            return result.get(
                str(tech_id),
                {
                    "total_tickets": 0,
                    "resolved_tickets": 0,
                    "pending_tickets": 0,
                    "avg_resolution_time": 0.0,
                },
            )
        except Exception as e:
            self.logger.error(f"Erro ao obter dados detalhados dos tickets do técnico {tech_id}: {e}")
            return None

    def _get_technician_ticket_details_optimized(self, technician_ids: list, tech_field_id: str) -> dict:
        """Obtém dados detalhados dos tickets de múltiplos técnicos com cache otimizado

        Args:
            technician_ids: Lista de IDs dos técnicos
            tech_field_id: ID do campo técnico no GLPI

        Retorna:
            Dict com dados de cada técnico: {
                "tech_id": {
                    "total_tickets": int,
                    "resolved_tickets": int,
                    "pending_tickets": int,
                    "avg_resolution_time": float
                }
            }
        """
        try:
            self.logger.info("=== DEBUG RANKING TÉCNICOS ===")
            self.logger.info(f"Técnicos para processar: {technician_ids}")
            self.logger.info(f"Field ID do técnico: {tech_field_id}")
            self.logger.info(f"Tipo do field ID: {type(tech_field_id)}")

            # Inicializar resultado para todos os técnicos
            result = {}
            for tech_id in technician_ids:
                result[str(tech_id)] = {
                    "total_tickets": 0,
                    "resolved_tickets": 0,
                    "pending_tickets": 0,
                    "avg_resolution_time": 0.0,
                }

            if not technician_ids:
                self.logger.warning("❌ Lista de técnicos vazia")
                return result

            # Verificar se o field ID é válido
            if not tech_field_id or tech_field_id == "None":
                self.logger.error(f"❌ Field ID do técnico é inválido: '{tech_field_id}'")
                return result

            # Testar consulta simples primeiro
            test_params = {
                "is_deleted": 0,
                "range": "0-5",
                "forcedisplay[0]": tech_field_id,
                "forcedisplay[1]": "12",  # Status
            }

            self.logger.info(f"🔍 Testando consulta simples com params: {test_params}")
            test_response = self._make_authenticated_request(
                "GET",
                f"{self.glpi_url}/search/Ticket",
                params=test_params,
                timeout=30,
            )

            if test_response and test_response.status_code == 200:
                test_data = test_response.json()
                self.logger.info(f"✅ Consulta de teste bem-sucedida: {len(test_data.get('data', []))} tickets encontrados")
                if test_data.get("data"):
                    sample_ticket = test_data["data"][0]
                    self.logger.info(f"📋 Ticket de exemplo: {sample_ticket}")
                    self.logger.info(
                        f"🔍 Campo {tech_field_id} no ticket: {sample_ticket.get(tech_field_id, 'NÃO ENCONTRADO')}"
                    )
                    self.logger.info(f"🔍 Status do ticket: {sample_ticket.get('12', 'NÃO ENCONTRADO')}")
                else:
                    self.logger.warning("⚠️ Nenhum ticket encontrado na consulta de teste")
            else:
                self.logger.error(f"❌ Consulta de teste falhou: {test_response.status_code if test_response else 'None'}")
                if test_response:
                    self.logger.error(f"Resposta: {test_response.text[:500]}")

            # Verificar cache primeiro
            cache_key = f"ticket_details_{hash(tuple(sorted(technician_ids)))}"
            try:
                cached_data = self._get_cache_data(cache_key)
                if cached_data is not None:
                    self.logger.info(
                        f"[{datetime.now(tz=timezone.utc).isoformat()}] Retornando dados de tickets do cache para {len(technician_ids)} técnicos"
                    )
                    return cached_data
            except Exception as e:
                self.logger.warning(
                    f"[{datetime.now(tz=timezone.utc).isoformat()}] Erro ao verificar cache de tickets: {e}"
                )

            # Processar técnicos em lotes menores
            batch_size = 10
            batches = [technician_ids[i : i + batch_size] for i in range(0, len(technician_ids), batch_size)]

            self.logger.info(f"📦 Processando {len(technician_ids)} técnicos em {len(batches)} lotes de até {batch_size}")

            for batch_idx, batch in enumerate(batches):
                try:
                    self.logger.info(f"🔄 Processando lote {batch_idx + 1}/{len(batches)} com {len(batch)} técnicos: {batch}")

                    # Buscar tickets para este lote (otimizado com range menor)
                    params = {
                        "is_deleted": 0,
                        "forcedisplay[0]": tech_field_id,
                        "forcedisplay[1]": "12",
                        "range": "0-5000",  # CORREÇÃO: Aumentado de 500 para 5000 para capturar mais tickets
                    }

                    # Adicionar critérios OR para técnicos do lote
                    for i, tech_id in enumerate(batch):
                        params[f"criteria[{i}][field]"] = tech_field_id
                        params[f"criteria[{i}][searchtype]"] = "equals"
                        params[f"criteria[{i}][value]"] = str(tech_id)
                        if i < len(batch) - 1:
                            params[f"criteria[{i}][link]"] = "OR"

                    self.logger.info(f"🔍 Parâmetros da consulta: {params}")

                    # Fazer a requisição
                    response = self._make_authenticated_request(
                        "GET",
                        f"{self.glpi_url}/search/Ticket",
                        params=params,
                        timeout=30,
                    )

                    if response and response.status_code == 200:
                        tickets_json = response.json()
                        self.logger.info(f"✅ Resposta recebida: {len(tickets_json.get('data', []))} tickets")

                        if "data" in tickets_json:
                            # Processar os tickets e agrupar por técnico
                            for ticket in tickets_json["data"]:
                                tech_id_str = str(ticket.get(str(tech_field_id), ""))
                                self.logger.info(
                                    f"🎫 Processando ticket: técnico={tech_id_str}, status={ticket.get('12', 'N/A')}"
                                )

                                if tech_id_str in result:
                                    status = int(ticket.get("12", 0))
                                    result[tech_id_str]["total_tickets"] += 1

                                    # Contar tickets resolvidos (status 5 e 6)
                                    if status in [5, 6]:
                                        result[tech_id_str]["resolved_tickets"] += 1
                                        self.logger.info(f"✅ Ticket resolvido para técnico {tech_id_str}")
                                    # Contar tickets pendentes (status 1, 2, 3, 4)
                                    elif status in [1, 2, 3, 4]:
                                        result[tech_id_str]["pending_tickets"] += 1
                                        self.logger.info(f"⏳ Ticket pendente para técnico {tech_id_str}")
                                    else:
                                        self.logger.info(f"❓ Status desconhecido {status} para técnico {tech_id_str}")
                                else:
                                    self.logger.warning(f"⚠️ Técnico {tech_id_str} não encontrado na lista de resultados")
                        else:
                            self.logger.warning("⚠️ Nenhum dado encontrado na resposta")
                    else:
                        self.logger.error(
                            f"❌ Falha na requisição do lote {batch_idx + 1}: {response.status_code if response else 'None'}"
                        )
                        if response:
                            self.logger.error(f"Resposta: {response.text[:500]}")

                except Exception as batch_error:
                    self.logger.error(f"❌ Erro no lote {batch_idx + 1}: {batch_error}")
                    continue

            # Log do resultado final
            self.logger.info("📊 RESULTADO FINAL:")
            for tech_id, data in result.items():
                self.logger.info(
                    f"  Técnico {tech_id}: total={data['total_tickets']}, resolvidos={data['resolved_tickets']}, pendentes={data['pending_tickets']}"
                )

            # Salvar no cache
            try:
                self._set_cache_data(cache_key, result, ttl=180)  # Cache por 3 minutos
                self.logger.info(f"💾 Dados de tickets salvos no cache com chave: {cache_key}")
            except Exception as cache_error:
                self.logger.warning(f"⚠️ Erro ao salvar no cache: {cache_error}")

            return result

        except Exception as e:
            self.logger.error(f"❌ Erro geral no processamento de tickets: {e}")
            return result

    def close_session(self):
        """Encerra a sessão com a API do GLPI"""
        if self.session_token:
            try:
                response = self._make_authenticated_request("GET", f"{self.glpi_url}/killSession")
                if response:
                    self.logger.info("Sessão encerrada com sucesso")
                else:
                    self.logger.warning("Falha ao encerrar sessão, mas continuando")
            except Exception as e:
                self.logger.error(f"Erro ao encerrar sessão: {e}")
            finally:
                self.session_token = None
                self.token_created_at = None
                self.token_expires_at = None

    def _get_cached_data(self, cache_key: str):
        """Recupera dados do cache se ainda válidos (TTL customizável)"""
        if cache_key not in self._cache:
            return None

        cache_entry = self._cache[cache_key]
        if cache_entry["data"] is None or cache_entry["timestamp"] is None:
            return None

        # Verificar se o cache ainda é válido
        current_time = time.time()
        ttl = cache_entry.get("ttl", 300)  # TTL padrão de 5 minutos
        if current_time - cache_entry["timestamp"] > ttl:
            # Cache expirado
            cache_entry["data"] = None
            cache_entry["timestamp"] = None
            return None

        return cache_entry["data"]

    def _set_cached_data(self, cache_key: str, data, ttl: int = None):
        """Armazena dados no cache com TTL customizável

        Args:
            cache_key: Chave do cache
            data: Dados a serem armazenados
            ttl: Time to live em segundos (usa TTL padrão do cache se None)
        """
        if cache_key in self._cache:
            self._cache[cache_key]["data"] = data
            self._cache[cache_key]["timestamp"] = time.time()
            if ttl is not None:
                self._cache[cache_key]["ttl"] = ttl

    def _get_user_name_by_id(self, user_id: str) -> str:
        """Busca o nome do usuário pelo ID"""
        if not user_id or user_id == "Não informado":
            return "Não informado"

        try:
            # Verificar cache primeiro
            cache_key = f"user_name_{user_id}"
            cached_name = self._get_cache_data("user_names", cache_key)
            if cached_name:
                return cached_name

            # Buscar usuário por ID
            response = self._make_authenticated_request("GET", f"{self.glpi_url}/User/{user_id}")

            if not response or not response.ok:
                self.logger.warning(f"Falha ao buscar usuário {user_id}")
                return f"Usuário {user_id}"

            user_data = response.json()

            # Construir nome de exibição
            display_name = "Usuário desconhecido"
            if isinstance(user_data, dict):
                if user_data.get("realname") and user_data.get("firstname"):
                    display_name = f"{user_data['firstname']} {user_data['realname']}"
                elif user_data.get("realname"):
                    display_name = user_data["realname"]
                elif user_data.get("name"):
                    display_name = user_data["name"]
                elif user_data.get("firstname"):
                    display_name = user_data["firstname"]

            # Armazenar no cache por 1 hora
            self._set_cache_data("user_names", display_name, 3600, cache_key)

            return display_name

        except Exception as e:
            self.logger.error(f"Erro ao buscar nome do usuário {user_id}: {e}")
            return f"Usuário {user_id}"

    def _get_priority_name_by_id(self, priority_id: str) -> str:
        """Converte ID de prioridade do GLPI para nome legível"""
        if not priority_id:
            return "Média"

        try:
            # Verificar cache primeiro
            cache_key = f"priority_name_{priority_id}"
            if self._is_cache_valid("priority_names", cache_key):
                cached_name = self._get_cache_data("priority_names", cache_key)
                if cached_name:
                    return cached_name

            # Mapeamento padrão de prioridades do GLPI
            priority_map = {
                "1": "Muito Baixa",
                "2": "Baixa",
                "3": "Média",
                "4": "Alta",
                "5": "Muito Alta",
                "6": "Crítica",
            }

            priority_name = priority_map.get(str(priority_id), "Média")

            # Armazenar no cache por 1 hora
            self._set_cache_data("priority_names", priority_name, 3600, cache_key)

            return priority_name

        except Exception as e:
            self.logger.error(f"Erro ao converter prioridade {priority_id}: {e}")
            return "Média"

    def _get_category_name_by_id(self, category_id) -> str:
        """Converte ID de categoria do GLPI para nome legível"""
        if not category_id:
            return "Não categorizado"

        # Se category_id for uma lista, pegar o primeiro elemento
        if isinstance(category_id, list):
            if not category_id:
                return "Não categorizado"
            category_id = str(category_id[0])
        else:
            category_id = str(category_id)

        try:
            # Verificar cache primeiro
            cache_key = f"category_name_{category_id}"
            if self._is_cache_valid("category_names", cache_key):
                cached_name = self._get_cache_data("category_names", cache_key)
                if cached_name:
                    return cached_name

            # Buscar categoria na API GLPI
            if not self._ensure_authenticated():
                return "Não categorizado"

            response = self._make_authenticated_request("GET", f"{self.glpi_url}/ITILCategory/{category_id}")

            if response and response.ok:
                category_data = response.json()
                category_name = category_data.get("name", "Não categorizado")

                # Armazenar no cache por 1 hora
                self._set_cache_data("category_names", category_name, 3600, cache_key)

                return category_name
            else:
                self.logger.warning(f"Falha ao buscar categoria {category_id}")
                return "Não categorizado"

        except Exception as e:
            self.logger.error(f"Erro ao converter categoria {category_id}: {e}")
            return "Não categorizado"

    def format_ticket_description(self, raw_description: str) -> str:
        """Formata descrição de ticket de forma inteligente

        Detecta se é uma descrição estruturada (com campos como LOCALIZAÇÃO, RAMAL, etc.)
        e formata de forma legível, ou mantém texto livre com limite apropriado.

        Args:
            raw_description: Descrição bruta do ticket

        Returns:
            Descrição formatada e legível
        """
        try:
            if not raw_description or not raw_description.strip():
                return "Sem descrição"

            # Limpar HTML primeiro
            clean_description = clean_html_content(raw_description)

            # Detectar se é descrição estruturada
            is_structured = (
                "Dados do formulário" in clean_description or
                "Dados Gerais" in clean_description or
                "LOCALIZAÇÃO" in clean_description or
                "RAMAL" in clean_description
            )

            if is_structured:
                return self._format_structured_description(clean_description)
            else:
                # Para texto livre, manter formatação original com limite de 500 caracteres
                if len(clean_description) > 500:
                    return clean_description[:497] + "..."
                return clean_description

        except Exception as e:
            self.logger.warning(f"Erro ao formatar descrição: {e}")
            # Fallback: retornar descrição limpa com limite de 500 caracteres
            clean_fallback = clean_html_content(raw_description) if raw_description else "Sem descrição"
            if len(clean_fallback) > 500:
                return clean_fallback[:497] + "..."
            return clean_fallback

    def _format_structured_description(self, description: str) -> str:
        """Formata descrição estruturada extraindo campos principais

        Args:
            description: Descrição limpa com estrutura de formulário

        Returns:
            Descrição formatada de forma profissional e legível
        """
        try:
            # Extrair campos principais usando regex
            import re

            # Padrões mais robustos para extrair informações
            location_pattern = r'LOCALIZAÇÃO\s*:?\s*([^\n\r]+?)(?=\d+\)|$|RAMAL|DESCR|ARQUIVO)'
            phone_pattern = r'RAMAL\s*:?\s*:?\s*([^\n\r]+?)(?=\d+\)|$|DESCR|ARQUIVO)'
            description_pattern = r'DESCR[IÇ]?[ÃA]?O?\s*DO\s*PEDIDO\s*:?\s*([\s\S]+?)(?=$|\n\n|Dados|\d+\)\s*ARQUIVO|ARQUIVO)'
            file_pattern = r'ARQUIVO\s*:?\s*:?\s*([^\n\r]+?)(?=$|\d+\)|LOCALIZAÇÃO|RAMAL|DESCR)'

            location = re.search(location_pattern, description, re.IGNORECASE)
            phone = re.search(phone_pattern, description, re.IGNORECASE)
            desc_content = re.search(description_pattern, description, re.IGNORECASE)
            file_content = re.search(file_pattern, description, re.IGNORECASE)

            # Construir descrição formatada com estrutura melhorada
            formatted_parts = []

            if location and location.group(1).strip():
                location_clean = location.group(1).strip()
                formatted_parts.append(f"LOCALIZAÇÃO: {location_clean}")

            if phone and phone.group(1).strip():
                phone_clean = phone.group(1).strip().replace(':', '').strip()
                if phone_clean:
                    formatted_parts.append(f"RAMAL: {phone_clean}")

            if desc_content and desc_content.group(1).strip():
                desc_text = desc_content.group(1).strip()
                # Limpar quebras de linha extras e espaços
                desc_text = re.sub(r'\s+', ' ', desc_text)
                # Limitar descrição a 500 caracteres para manter legibilidade
                if len(desc_text) > 500:
                    desc_text = desc_text[:497] + "..."
                formatted_parts.append(f"DESCRIÇÃO: {desc_text}")

            if file_content and file_content.group(1).strip():
                file_clean = file_content.group(1).strip()
                formatted_parts.append(f"ARQUIVO: {file_clean}")

            if formatted_parts:
                # Retornar com quebras de linha para melhor formatação
                return "\n".join(formatted_parts)
            else:
                # Se não conseguiu extrair campos, retornar descrição original limitada
                if len(description) > 500:
                    return description[:497] + "..."
                return description

        except Exception as e:
            self.logger.warning(f"Erro ao formatar descrição estruturada: {e}")
            # Fallback para descrição original limitada
            if len(description) > 300:
                return description[:297] + "..."
            return description

    def get_new_tickets(self, limit: int = 10) -> List[Dict[str, any]]:
        """Busca tickets com status 'novo' com detalhes completos"""
        if not self._ensure_authenticated():
            return []

        if not self.discover_field_ids():
            return []

        try:
            # Buscar ID do status 'novo' (geralmente 1)
            status_id = self.status_map.get("novos", 1)

            # Parâmetros para buscar tickets com status novo
            search_params = {
                "is_deleted": 0,
                "range": f"0-{limit - 1}",  # Limitar resultados
                "criteria[0][field]": self.field_ids["STATUS"],
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": status_id,
                "sort": "19",  # Ordenar por data de criação (campo 19)
                "order": "DESC",  # Mais recentes primeiro
                "forcedisplay[0]": "2",  # ID do ticket
                "forcedisplay[1]": "1",  # Título
                "forcedisplay[2]": "21",  # Descrição
                "forcedisplay[3]": "15",  # Data de abertura
                "forcedisplay[4]": "4",  # Solicitante (users_id_recipient)
                "forcedisplay[5]": "3",  # Prioridade
                "forcedisplay[6]": "5",  # Categoria
                "forcedisplay[7]": "12",  # Status
            }

            response = self._make_authenticated_request("GET", f"{self.glpi_url}/search/Ticket", params=search_params)

            if not response or not response.ok:
                self.logger.error("Falha ao buscar tickets novos")
                return []

            data = response.json()
            tickets = []

            if "data" in data and data["data"]:
                for ticket_data in data["data"]:
                    # Extrair ID do requerente e buscar o nome
                    requester_id = ticket_data.get("4", "")
                    requester_name = self._get_user_name_by_id(str(requester_id)) if requester_id else "Não informado"

                    # Extrair ID da prioridade e converter para nome
                    priority_id = ticket_data.get("3", "3")  # Default para prioridade média (ID 3)
                    priority_name = self._get_priority_name_by_id(str(priority_id))

                    # Extrair ID da categoria e converter para nome
                    category_id = ticket_data.get("5", "")  # Campo 5 = categoria
                    category_name = self._get_category_name_by_id(str(category_id)) if category_id else "Não categorizado"

                    # Extrair e formatar descrição usando nova função inteligente
                    raw_description = ticket_data.get("21", "")
                    formatted_description = self.format_ticket_description(raw_description)

                    # Extrair informações do ticket
                    ticket_info = {
                        "id": str(ticket_data.get("2", "")),  # ID do ticket
                        "title": ticket_data.get("1", "Sem título"),  # Título
                        "description": formatted_description,  # Descrição formatada inteligentemente
                        "date": ticket_data.get("15", ""),  # Data de abertura
                        "requester": requester_name,  # Nome do solicitante
                        "priority": priority_name,  # Nome da prioridade convertido
                        "category": category_name,  # Nome da categoria convertido
                        "status": "Novo",
                    }
                    tickets.append(ticket_info)

            self.logger.info(f"Encontrados {len(tickets)} tickets novos")
            return tickets

        except Exception as e:
            self.logger.error(f"Erro ao buscar tickets novos: {e}")
            return []

    def get_system_status(self) -> Dict[str, any]:
        """Retorna status do sistema GLPI com verificação rápida"""
        try:
            start_time = time.time()

            # Verificação rápida de conectividade sem autenticação completa
            # Se já temos um token válido, usar ele; caso contrário, fazer ping básico
            if self.session_token and not self._is_token_expired():
                # Token válido - verificação rápida
                try:
                    headers = {
                        "Session-Token": self.session_token,
                        "App-Token": self.app_token,
                    }
                    response = requests.get(
                        f"{self.base_url}/getGlpiConfig",
                        headers=headers,
                        timeout=1,  # Timeout muito baixo para status check
                        verify=False,
                    )
                    response_time = time.time() - start_time

                    if response.status_code == 200:
                        return {
                            "status": "online",
                            "message": "GLPI conectado (token válido)",
                            "response_time": response_time,
                            "token_valid": True,
                        }
                    else:
                        return {
                            "status": "warning",
                            "message": f"GLPI respondeu com status {response.status_code}",
                            "response_time": response_time,
                            "token_valid": False,
                        }

                except requests.exceptions.Timeout:
                    response_time = time.time() - start_time
                    return {
                        "status": "warning",
                        "message": "GLPI lento (timeout em 1s)",
                        "response_time": response_time,
                        "token_valid": False,
                    }

            else:
                # Sem token válido - ping básico sem autenticação
                try:
                    response = requests.get(
                        f"{self.base_url}/",
                        timeout=1,  # Timeout muito baixo
                        verify=False,
                    )
                    response_time = time.time() - start_time

                    if response.status_code in [
                        200,
                        401,
                        403,
                    ]:  # 401/403 indicam que o servidor está respondendo
                        return {
                            "status": "online",
                            "message": "GLPI acessível (sem token)",
                            "response_time": response_time,
                            "token_valid": False,
                        }
                    else:
                        return {
                            "status": "warning",
                            "message": f"GLPI respondeu com status {response.status_code}",
                            "response_time": response_time,
                            "token_valid": False,
                        }

                except requests.exceptions.Timeout:
                    response_time = time.time() - start_time
                    return {
                        "status": "warning",
                        "message": "GLPI lento (timeout em 1s)",
                        "response_time": response_time,
                        "token_valid": False,
                    }

        except Exception as e:
            response_time = time.time() - start_time
            return {
                "status": "offline",
                "message": f"Erro de conexão: {str(e)}",
                "response_time": response_time,
                "token_valid": False,
            }

    def get_dashboard_metrics_with_filters(
        self,
        start_date: str = None,
        end_date: str = None,
        status: str = None,
        priority: str = None,
        level: str = None,
        technician: str = None,
        category: str = None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, any]:
        """Obtém métricas do dashboard com filtros avançados usando o sistema unificado"""
        start_time = time.time()

        try:
            if not self._ensure_authenticated():
                return ResponseFormatter.format_error_response(
                    "Falha na autenticação com GLPI",
                    ["Erro de autenticação"],
                    correlation_id=correlation_id,
                )

            if not self.discover_field_ids():
                return ResponseFormatter.format_error_response(
                    "Falha ao descobrir IDs dos campos",
                    ["Erro ao obter configuração"],
                    correlation_id=correlation_id,
                )

            # Combinar métricas por nível e gerais com filtros
            level_metrics = self._get_metrics_by_level_internal_hierarchy(start_date, end_date, correlation_id)
            general_metrics = self._get_general_metrics_internal(start_date, end_date, correlation_id)

            # Aplicar filtros adicionais se especificados
            if status or priority or level or technician or category:
                level_metrics = self._apply_additional_filters(
                    level_metrics,
                    status,
                    priority,
                    level,
                    technician,
                    category,
                )

            # Usar o formatador unificado
            raw_data = {"by_level": level_metrics, "general": general_metrics}
            filters_data = {
                "start_date": start_date,
                "end_date": end_date,
                "status": status,
                "priority": priority,
                "level": level,
                "technician": technician,
                "category": category,
            }
            result = ResponseFormatter.format_dashboard_response(raw_data, filters=filters_data, start_time=start_time)

            return result

        except Exception as e:
            self.logger.error(f"Erro ao obter métricas com filtros: {e}")
            return ResponseFormatter.format_error_response(
                f"Erro interno: {str(e)}",
                [str(e)],
                correlation_id=correlation_id,
            )

    def _get_all_technician_ids_and_names(self, entity_id: int = None) -> tuple[list, dict]:
        """Obtém todos os IDs de técnicos ativos do GLPI e seus nomes

        IMPLEMENTAÇÃO CORRIGIDA: Busca direta de usuários ativos com perfil de técnico
        usando busca por atribuições de tickets recentes como fallback para Profile_User vazio

        Args:
            entity_id: ID da entidade para filtrar técnicos (opcional)

        Returns:
            tuple: (lista de IDs, dicionário ID->nome)
        """
        print(f"DEBUG: INÍCIO _get_all_technician_ids_and_names com entity_id={entity_id}")
        try:
            print(f"DEBUG: _get_all_technician_ids_and_names chamado com entity_id={entity_id}")
            timestamp = datetime.now(tz=timezone.utc).isoformat()
            self.logger.info(f"[{timestamp}] Iniciando busca de técnicos com método alternativo")

            # Criar instância dos helpers
            helpers = GLPIServiceHelpers(self)
            print(f"DEBUG: GLPIServiceHelpers criado: {helpers}")

            # Buscar IDs de técnicos através de tickets atribuídos
            print(f"DEBUG: Chamando get_technician_ids_from_tickets com entity_id={entity_id}")
            tech_ids_set = helpers.get_technician_ids_from_tickets(entity_id)
            print(f"DEBUG: get_technician_ids_from_tickets retornou: {tech_ids_set}")

            if not tech_ids_set:
                self.logger.warning(f"[{timestamp}] Nenhum técnico encontrado nos tickets")
                return [], {}

            # Buscar detalhes dos técnicos em lotes
            tech_ids, tech_names = helpers.get_technician_details_in_batches(tech_ids_set)
            if len(tech_ids) == 0:
                self.logger.warning(f"[{timestamp}] Nenhum técnico ativo encontrado")
                return [], {}

            self.logger.info(
                f"[{timestamp}] Busca concluída: {len(tech_ids)} técnicos ativos " f"identificados via atribuições de tickets"
            )
            return tech_ids, tech_names

        except Exception as e:
            print(f"DEBUG: EXCEÇÃO CAPTURADA em _get_all_technician_ids_and_names: {e}")
            print(f"DEBUG: Tipo da exceção: {type(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            self.logger.error(f"Erro ao obter técnicos: {e}")
            return [], {}

    def _get_all_technician_ids(self) -> list:
        """Obtém todos os IDs de técnicos ativos do GLPI (compatibilidade)"""
        tech_ids, _ = self._get_all_technician_ids_and_names()
        return tech_ids

    def _parse_technician_id(self, tech_field):
        """Parse correto do campo users_id_tech que pode vir como string, lista ou número"""
        helpers = GLPIServiceHelpers(self)
        return helpers.parse_technician_id(tech_field)

    def get_technicians_by_assignments(self, days_back=30, min_tickets=3):
        """Identifica técnicos baseado em atribuições de tickets recentes

        Args:
            days_back: Número de dias para buscar no histórico
            min_tickets: Número mínimo de tickets para considerar como técnico

        Returns:
            dict: Dicionário com técnicos identificados
        """
        helpers = GLPIServiceHelpers(self)
        return helpers.get_technicians_by_assignments(days_back, min_tickets)

    def _get_all_tickets_grouped_by_technician(
        self,
        technician_ids: List[str],
        start_date: str = None,
        end_date: str = None,
    ) -> Dict[str, int]:
        """Busca todos os tickets de uma vez e agrupa por técnico para otimizar performance

        OTIMIZAÇÃO: Usa uma única query para buscar todos os tickets e agrupa por técnico
        ao invés de fazer requisições individuais para cada técnico.
        """
        try:
            if not technician_ids:
                self.logger.warning("Lista de técnicos vazia")
                return {}

            # Descobrir o campo correto para técnico responsável dinamicamente
            tech_field_id = self._discover_tech_field_id()
            if not tech_field_id:
                self.logger.error("Não foi possível descobrir o campo do técnico")
                return {}

            # Inicializar contadores para todos os técnicos
            ticket_counts = {tech_id: 0 for tech_id in technician_ids}

            # OTIMIZAÇÃO: Buscar todos os tickets de uma vez usando uma única query
            self.logger.info(f"[OTIMIZAÇÃO] Iniciando busca otimizada em lote para " f"{len(technician_ids)} técnicos")
            if start_date and end_date:
                # Com filtros de data - usar query otimizada em lote
                self.logger.info(f"[OTIMIZAÇÃO] Usando busca em lote COM filtro de data: " f"{start_date} a {end_date}")
                ticket_counts = self._get_tickets_batch_with_date_filter(technician_ids, start_date, end_date, tech_field_id)
            else:
                # Sem filtros de data - usar query otimizada em lote
                self.logger.info("[OTIMIZAÇÃO] Usando busca em lote SEM filtro de data")
                ticket_counts = self._get_tickets_batch_without_date_filter(technician_ids, tech_field_id)

            self.logger.info(f"[OTIMIZAÇÃO] Busca otimizada concluída: " f"{sum(ticket_counts.values())} tickets total")
            return ticket_counts

        except Exception as e:
            self.logger.error(f"[FALLBACK] Erro ao buscar tickets agrupados por técnico: {e}")
            self.logger.error(f"[FALLBACK] Traceback completo: {traceback.format_exc()}")
            # Fallback para método individual em caso de erro
            self.logger.info("[FALLBACK] Usando fallback para método individual")
            return self._get_all_tickets_grouped_by_technician_fallback(technician_ids, start_date, end_date)

    def _get_tickets_batch_with_date_filter(
        self,
        technician_ids: List[str],
        start_date: str,
        end_date: str,
        tech_field_id: str,
    ) -> Dict[str, int]:
        """Busca todos os tickets com filtros de data usando paginação robusta

        Args:
            technician_ids: Lista de IDs dos técnicos
            start_date: Data de início no formato YYYY-MM-DD
            end_date: Data de fim no formato YYYY-MM-DD

        Returns:
            Dict com contagem de tickets por técnico
        """
        try:
            # Debug: Método _get_tickets_batch_with_date_filter iniciado

            if not technician_ids:
                print("[DEBUG] _get_tickets_batch_with_date_filter: technician_ids vazio")
                # Debug: Problema de technician_ids vazio registrado
                return {}

            self.logger.info(f"_get_tickets_batch_with_date_filter: processando {len(technician_ids)} técnicos")
            self.logger.info(f"Período: {start_date} a {end_date}")
            self.logger.info(f"tech_field_id: {tech_field_id}")

            # Construir parâmetros de busca usando função utilitária centralizada

            search_params = {
                "is_deleted": 0,
                # Campo do técnico descoberto dinamicamente
                "forcedisplay[0]": tech_field_id,
                "forcedisplay[1]": "2",  # id
            }

            # Usar função utilitária para construir critérios de data
            date_criteria = DateValidator.construir_criterios_filtro_data(
                start_date=start_date,
                end_date=end_date,
                field_id="15",  # Campo de data de criação
                criteria_start_index=0,
            )
            search_params.update(date_criteria)

            # Usar lotes otimizados (reduzido para evitar erro 414 - URI Too Long)
            batch_size = 25  # Reduzido para evitar erro 414
            all_ticket_counts = {tech_id: 0 for tech_id in technician_ids}

            # print(f"[DEBUG] Processando {len(technician_ids)} técnicos em lotes " f"otimizados de {batch_size}")

            for i in range(0, len(technician_ids), batch_size):
                batch_tech_ids = technician_ids[i : i + batch_size]
                batch_params = search_params.copy()

                # Adicionar critérios para cada técnico no batch
                # Calcular próximo índice disponível após critérios de data
                date_criteria_count = len(date_criteria) // 3 if date_criteria else 0
                criteria_index = date_criteria_count

                for j, tech_id in enumerate(batch_tech_ids):
                    link_type = "OR" if j > 0 else "AND"
                    batch_params.update(
                        {
                            f"criteria[{criteria_index}][link]": link_type,
                            # Campo do técnico
                            f"criteria[{criteria_index}][field]": tech_field_id,
                            # descoberto dinamicamente
                            f"criteria[{criteria_index}][searchtype]": "equals",
                            f"criteria[{criteria_index}][value]": str(tech_id),
                        }
                    )
                    criteria_index += 1

                # Usar paginação robusta para este batch
                batch_counts = self._fetch_all_pages_robust(batch_params, batch_tech_ids, tech_field_id)

                # Combinar resultados
                for tech_id, count in batch_counts.items():
                    all_ticket_counts[tech_id] += count

            return all_ticket_counts

        except Exception as e:
            self.logger.error(f"Erro na busca em lote com filtro de data: {e}")
            # Retornar contadores zerados em caso de erro
            return {tech_id: 0 for tech_id in technician_ids}

    def _fetch_all_pages_robust(self, search_params: dict, tech_ids: List[str], tech_field_id: str) -> Dict[str, int]:
        """Implementa paginação robusta para buscar todos os dados incrementalmente

        Args:
            search_params: Parâmetros de busca base
            tech_ids: Lista de IDs dos técnicos
            tech_field_id: ID do campo de técnico

        Returns:
            Dict com contagem de tickets por técnico
        """
        helpers = GLPIServiceHelpers(self)
        return helpers.fetch_all_pages_robust(search_params, tech_ids, tech_field_id)

    def _process_ticket_batch(self, search_params: dict, tech_ids: List[str], tech_field_id: str) -> Dict[str, int]:
        """Processa um batch de técnicos e retorna contagem de tickets"""
        import time

        start_time = time.time()
        try:
            ticket_counts = {tech_id: 0 for tech_id in tech_ids}

            url = f"{self.glpi_url}/search/Ticket"

            # print(f"[DEBUG] Processando batch de {len(tech_ids)} técnicos - URL: {url}")
            self.logger.info(f"Processando batch de {len(tech_ids)} técnicos")

            response = self._make_authenticated_request("GET", url, params=search_params)
            if not response or not response.ok:
                self.logger.error(f"Falha na requisição do batch: " f"{response.status_code if response else 'No response'}")
                return ticket_counts

            data = response.json()

            if "data" in data and data["data"]:
                # Contar tickets por técnico
                for ticket in data["data"]:
                    tech_id = str(ticket.get(tech_field_id, ""))  # Campo do técnico descoberto dinamicamente
                    if tech_id in ticket_counts:
                        ticket_counts[tech_id] += 1

            # elapsed_time = time.time() - start_time  # Commented out unused variable
            # print(f"[DEBUG] Batch processado em {elapsed_time:.2f}s: " f"{sum(ticket_counts.values())} tickets encontrados")
            self.logger.info(f"Batch processado: {sum(ticket_counts.values())} tickets encontrados")
            return ticket_counts

        except Exception as e:
            # elapsed_time = time.time() - start_time  # Commented out unused variable
            # print(f"[DEBUG] Erro no batch após {elapsed_time:.2f}s: {e}")
            self.logger.error(f"Erro no processamento do batch: {e}")
            return {tech_id: 0 for tech_id in tech_ids}

    def _get_tickets_batch_without_date_filter(self, technician_ids: List[str], tech_field_id: str) -> Dict[str, int]:
        """Busca todos os tickets sem filtros de data em uma única query otimizada

        Args:
            technician_ids: Lista de IDs dos técnicos

        Returns:
            Dict com contagem de tickets por técnico
        """
        try:
            if not technician_ids:
                return {}

            # Inicializar contadores
            ticket_counts = {tech_id: 0 for tech_id in technician_ids}

            # Construir parâmetros de busca usando a mesma estrutura que funciona
            search_params = {
                "is_deleted": 0,
                # Campo do técnico descoberto dinamicamente
                "forcedisplay[0]": tech_field_id,
                "forcedisplay[1]": "2",  # id
            }

            # Adicionar critérios para cada técnico com OR
            criteria_index = 0
            for i, tech_id in enumerate(technician_ids):
                if i == 0:
                    # Primeiro critério não precisa de link
                    search_params.update(
                        {
                            # Campo do técnico descoberto dinamicamente
                            f"criteria[{criteria_index}][field]": tech_field_id,
                            f"criteria[{criteria_index}][searchtype]": "equals",
                            f"criteria[{criteria_index}][value]": str(tech_id),
                        }
                    )
                else:
                    # Demais critérios usam OR
                    search_params.update(
                        {
                            f"criteria[{criteria_index}][link]": "OR",
                            # Campo do técnico descoberto dinamicamente
                            f"criteria[{criteria_index}][field]": tech_field_id,
                            f"criteria[{criteria_index}][searchtype]": "equals",
                            f"criteria[{criteria_index}][value]": str(tech_id),
                        }
                    )
                criteria_index += 1

            # Usar paginação robusta para buscar todos os dados
            self.logger.info(f"Buscando tickets em lote para {len(technician_ids)} técnicos sem filtro de data")

            ticket_counts = self._fetch_all_pages_robust(search_params, technician_ids, tech_field_id)

            self.logger.info(f"Busca em lote concluída: {sum(ticket_counts.values())} tickets encontrados")
            return ticket_counts

        except Exception as e:
            self.logger.error(f"Erro na busca em lote sem filtro de data: {e}")
            # Retornar contadores zerados em caso de erro
            return {tech_id: 0 for tech_id in technician_ids}

    def _get_technician_batch_optimized(
        self,
        technician_ids: List[str],
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, int]:
        """
        Busca dados de múltiplos técnicos em uma única requisição
        Reduz de N requisições para 1 requisição

        Args:
            technician_ids: Lista de IDs dos técnicos
            start_date: Data de início no formato YYYY-MM-DD (opcional)
            end_date: Data de fim no formato YYYY-MM-DD (opcional)

        Returns:
            Dict com contagem de tickets por técnico
        """
        import time

        start_time = time.time()

        try:
            # Log detalhado de início
            self.logger.info(f"[BATCH_OPTIMIZED] Iniciando processamento em lote para {len(technician_ids)} técnicos")
            self.logger.info(f"[BATCH_OPTIMIZED] Período: {start_date or 'sem filtro'} a {end_date or 'sem filtro'}")

            # Validação de entrada
            if not technician_ids:
                self.logger.warning("[BATCH_OPTIMIZED] Lista de técnicos vazia")
                return {}

            # Descobrir o campo correto para técnico responsável dinamicamente
            tech_field_id = self._discover_tech_field_id()
            if not tech_field_id:
                self.logger.error("[BATCH_OPTIMIZED] Não foi possível descobrir o campo do técnico")
                raise Exception("Campo do técnico não encontrado")

            self.logger.info(f"[BATCH_OPTIMIZED] Campo do técnico descoberto: {tech_field_id}")

            # Usar método otimizado com requisições individuais range 0-0
            ticket_counts = {tech_id: 0 for tech_id in technician_ids}

            # Para cada técnico, usar método otimizado que retorna apenas contagem
            for tech_id in technician_ids:
                try:
                    if start_date and end_date:
                        # Usar método com filtro de data
                        count = self._count_tickets_with_date_filter(tech_id, start_date, end_date)
                    else:
                        # Usar método otimizado sem filtro de data (range 0-0)
                        count = self._count_tickets_by_technician_optimized(int(tech_id), tech_field_id)

                    ticket_counts[tech_id] = count if count is not None else 0
                    self.logger.info(f"[BATCH_OPTIMIZED] Técnico {tech_id}: {ticket_counts[tech_id]} tickets")

                except Exception as e:
                    self.logger.error(f"[BATCH_OPTIMIZED] Erro ao processar técnico {tech_id}: {e}")
                    ticket_counts[tech_id] = 0

            elapsed_time = time.time() - start_time
            total_tickets = sum(ticket_counts.values())
            self.logger.info(f"[BATCH_OPTIMIZED] Processamento concluído em {elapsed_time:.2f}s")
            self.logger.info(f"[BATCH_OPTIMIZED] Total de tickets encontrados: {total_tickets}")
            self.logger.info(f"[BATCH_OPTIMIZED] Distribuição por técnico: {dict(ticket_counts)}")

            return ticket_counts

        except Exception as e:
            elapsed_time = time.time() - start_time
            self.logger.error(f"[BATCH_OPTIMIZED] Erro no batch processing após {elapsed_time:.2f}s: {e}")

            # Fallback para método original
            self.logger.info("[BATCH_OPTIMIZED] Executando fallback para método original")
            try:
                return self._get_all_tickets_grouped_by_technician_fallback(
                    technician_ids, start_date, end_date
                )
            except Exception as fallback_error:
                self.logger.error(f"[BATCH_OPTIMIZED] Erro no fallback: {fallback_error}")
                # Retornar contadores zerados como último recurso
                return {tech_id: 0 for tech_id in technician_ids}

    def _get_all_tickets_grouped_by_technician_fallback(
        self,
        technician_ids: List[str],
        start_date: str = None,
        end_date: str = None,
    ) -> Dict[str, int]:
        """Método fallback que usa requisições individuais (método original)

        Este método é usado apenas quando a busca em lote falha.
        """
        try:
            if not technician_ids:
                self.logger.warning("Lista de técnicos vazia")
                return {}

            # Descobrir o campo correto para técnico responsável dinamicamente
            tech_field_id = self._discover_tech_field_id()
            if not tech_field_id:
                self.logger.error("Não foi possível descobrir o campo do técnico")
                return {}

            # Inicializar contadores para todos os técnicos
            ticket_counts = {tech_id: 0 for tech_id in technician_ids}

            # Para cada técnico, usar o método apropriado
            for tech_id in technician_ids:
                try:
                    if start_date and end_date:
                        # Usar método com filtro de data
                        count = self._count_tickets_with_date_filter(tech_id, start_date, end_date)
                    else:
                        # Usar método otimizado sem filtro de data
                        count = self._count_tickets_by_technician_optimized(int(tech_id), tech_field_id)

                    ticket_counts[tech_id] = count if count is not None else 0
                except Exception as e:
                    self.logger.error(f"Erro ao contar tickets para técnico {tech_id}: {e}")
                    ticket_counts[tech_id] = 0

            return ticket_counts

        except Exception as e:
            self.logger.error(f"Erro no método fallback: {e}")
            return {}

    def get_technician_ranking_with_filters(
        self,
        start_date: str = None,
        end_date: str = None,
        level: str = None,
        limit: int = 10,
        correlation_id: str = None,
        entity_id: str = None,
    ) -> List[Dict[str, any]]:
        """Obtém ranking de técnicos com filtros avançados

        Args:
            start_date: Data de início no formato YYYY-MM-DD
            end_date: Data de fim no formato YYYY-MM-DD
            level: Filtro por nível (N1, N2, N3, N4)
            limit: Número máximo de técnicos no ranking
            correlation_id: ID de correlação para logs
            entity_id: ID da entidade para filtrar técnicos
        """
        # Log simples para confirmar que o método está sendo chamado
        # print(f"[DEBUG] get_technician_ranking_with_filters CHAMADO - start_date: {start_date}, end_date: {end_date}")

        if not correlation_id:
            obs_logger = glpi_logger
            correlation_id = obs_logger.generate_correlation_id()
        else:
            obs_logger = glpi_logger

        auth_result = self._ensure_authenticated()
        print(f"DEBUG: _ensure_authenticated() retornou: {auth_result}")
        if not auth_result:
            obs_logger.emit_warning(
                correlation_id,
                "AUTHENTICATION_FAILURE",
                "Falha na autenticação com GLPI",
            )
            return []

        print(f"DEBUG: Autenticação OK, continuando com o ranking")

        try:
            obs_logger.log_pipeline_step(
                correlation_id,
                "glpi_service_start",
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "level": level,
                    "limit": limit,
                },
            )
            self.logger.info(
                f"[{correlation_id}] Iniciando ranking com filtros - start_date: {start_date}, end_date: {end_date}, level: {level}, limit: {limit}"
            )

            # Descobrir o field ID do técnico dinamicamente
            tech_field_id = self._discover_tech_field_id()
            print(f"DEBUG: tech_field_id descoberto: {tech_field_id}")
            print(f"DEBUG: tech_field_id type: {type(tech_field_id)}")
            print(f"DEBUG: tech_field_id bool: {bool(tech_field_id)}")
            print(f"DEBUG: not tech_field_id: {not tech_field_id}")
            if not tech_field_id:
                obs_logger.emit_warning(
                    correlation_id,
                    "TECH_FIELD_DISCOVERY_FAILURE",
                    "Não foi possível descobrir o field ID do técnico",
                )
                return []
            print(f"DEBUG: Continuando com tech_field_id: {tech_field_id}")

            # print(f"[DEBUG] tech_field_id descoberto: {tech_field_id}")

            # Obter todos os técnicos ativos dinamicamente com nomes otimizados
            # print(f"[DEBUG] [{correlation_id}] Buscando técnicos ativos com entity_id: {entity_id}")
            (
                technician_ids,
                technician_names,
            ) = self._get_all_technician_ids_and_names(entity_id=entity_id)
            # print(f"[DEBUG] [{correlation_id}] Encontrados {len(technician_ids) if technician_ids else 0} técnicos")
            # print(f"[DEBUG] [{correlation_id}] Técnicos encontrados: {technician_ids[:5] if technician_ids else 'Nenhum'}")

            if not technician_ids:
                obs_logger.log_pipeline_step(
                    correlation_id,
                    "technician_extraction_failed",
                    {"message": "Nenhum técnico ativo encontrado"},
                )
                self.logger.warning(f"[{correlation_id}] Nenhum técnico ativo encontrado")
                return []

            obs_logger.log_pipeline_step(
                correlation_id,
                "technician_ids_extracted",
                {
                    "technician_count": len(technician_ids),
                    "sample_ids": technician_ids[:5],  # Primeiros 5 IDs como amostra
                },
            )
            self.logger.info(
                f"[{correlation_id}] Encontrados {len(technician_ids)} técnicos: {technician_ids[:10]}..."
            )  # Limitar log

            ranking = []

            # Buscar todos os tickets de uma vez e agrupar por técnico (otimizado)
            if start_date and end_date:
                self.logger.info(f"[{correlation_id}] Usando método otimizado com filtros de data: {start_date} a {end_date}")
                self.logger.info(f"Chamando _get_tickets_batch_with_date_filter para {len(technician_ids)} técnicos")
                ticket_counts = self._get_tickets_batch_with_date_filter(technician_ids, start_date, end_date, tech_field_id)
                self.logger.info(f"_get_tickets_batch_with_date_filter retornou {len(ticket_counts)} resultados")
                self.logger.info(f"Conteúdo de ticket_counts: {ticket_counts}")
            else:
                self.logger.info(f"[{correlation_id}] Usando método sem filtros de data")
                ticket_counts = self._get_tickets_batch_without_date_filter(technician_ids, tech_field_id)

            # Para cada técnico, usar os dados já obtidos
            for tech_id in technician_ids:
                try:
                    # Obter nome do técnico do cache otimizado
                    tech_name = technician_names.get(tech_id, f"Técnico {tech_id}")

                    # Obter contagem de tickets do cache otimizado
                    ticket_count = ticket_counts.get(tech_id, 0)

                    # Determinar o nível real do técnico
                    # Tentar converter tech_id para int, se falhar usar o método alternativo
                    try:
                        tech_id_int = int(tech_id)
                        tech_level = self._get_technician_level(tech_id_int, ticket_count)
                    except (ValueError, TypeError):
                        # Se tech_id não for numérico, usar nome para determinar nível
                        self.logger.debug(f"tech_id não numérico: {tech_id}, usando nome para determinar nível")
                        self.logger.debug(f"Nome do técnico obtido: {tech_name}")
                        tech_level = self._get_technician_level_by_name(tech_name)
                        self.logger.debug(f"Nível determinado para {tech_name}: {tech_level}")

                    # Se um filtro de nível foi especificado, verificar se o técnico corresponde
                    if level and tech_level != level:
                        self.logger.debug(
                            f"Técnico {tech_name} (nível {tech_level}) filtrado - não corresponde ao filtro {level}"
                        )
                        continue  # Pular este técnico se não corresponder ao filtro de nível

                    ranking.append(
                        {
                            "id": tech_id,
                            "name": tech_name,
                            "total_tickets": ticket_count,
                            "resolved_tickets": 0,
                            "pending_tickets": 0,
                            "avg_resolution_time": 0.0,
                            "level": tech_level,  # Usar o nível real do técnico
                            "rank": 0,  # Será definido após ordenação
                        }
                    )

                except Exception as e:
                    self.logger.error(f"Erro ao processar técnico {tech_id}: {e}")
                    self.logger.error(f"Traceback completo: {traceback.format_exc()}")
                    continue

            # Log antes da ordenação
            obs_logger.log_pipeline_step(
                correlation_id,
                "pre_sorting",
                {
                    "total_technicians_processed": len(ranking),
                    "zero_totals": sum(1 for tech in ranking if tech.get("total_tickets", 0) == 0),
                    "max_total": max([tech.get("total_tickets", 0) for tech in ranking]) if ranking else 0,
                },
            )

            # Ordenar por contagem de tickets (decrescente)
            ranking.sort(key=lambda x: x["total_tickets"], reverse=True)

            # Definir ranks
            for i, tech in enumerate(ranking):
                tech["rank"] = i + 1

            result = ranking[:limit]

            # Log final com estatísticas
            obs_logger.log_pipeline_step(
                correlation_id,
                "ranking_completed",
                {
                    "final_count": len(result),
                    "limit_applied": limit,
                    "top_3_totals": [tech.get("total_tickets", 0) for tech in result[:3]],
                },
            )

            self.logger.info(f"[{correlation_id}] Ranking com filtros concluído: {len(result)} técnicos")

            return result

        except Exception as e:
            self.logger.error(f"Erro ao obter ranking com filtros: {e}")
            return []

    def get_new_tickets_with_filters(
        self,
        limit: int = 10,
        priority: str = None,
        category: str = None,
        technician: str = None,
        start_date: str = None,
        end_date: str = None,
    ) -> List[Dict[str, any]]:
        """Obtém tickets novos com filtros avançados de forma robusta"""
        # Validações de entrada
        try:
            # Validar limite
            if not isinstance(limit, int) or limit < 1:
                limit = 10
            limit = max(1, min(limit, 100))  # Entre 1 e 100

            # Validar formato das datas
            if start_date:
                try:
                    datetime.strptime(start_date, "%Y-%m-%d")
                except ValueError:
                    self.logger.warning(f"Formato de data de início inválido: {start_date}")
                    start_date = None

            if end_date:
                try:
                    datetime.strptime(end_date, "%Y-%m-%d")
                except ValueError:
                    self.logger.warning(f"Formato de data de fim inválido: {end_date}")
                    end_date = None

            # Validar se data de início não é posterior à data de fim
            if start_date and end_date:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                if start_dt > end_dt:
                    self.logger.warning("Data de início posterior à data de fim")
                    start_date, end_date = None, None

        except Exception as e:
            self.logger.error(f"Erro na validação de parâmetros: {e}")
            return []

        if not self._ensure_authenticated():
            self.logger.warning("Falha na autenticação para buscar tickets novos")
            return []

        if not self.discover_field_ids():
            self.logger.warning("Falha ao descobrir field_ids para buscar tickets novos")
            return []

        try:
            # Construir parâmetros de busca de forma mais eficiente
            search_params = {
                "is_deleted": 0,
                "range": f"0-{limit - 1}",
                "sort": "15",  # Ordenar por data de criação
                "order": "DESC",
                "criteria[0][field]": self.field_ids.get("STATUS", "12"),
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": self.status_map.get("Novo", 1),
            }

            criteria_index = 1

            # Adicionar filtros opcionais
            if priority:
                priority_id = self._get_priority_id_by_name(priority)
                if priority_id:
                    search_params.update(
                        {
                            f"criteria[{criteria_index}][link]": "AND",
                            # Campo prioridade
                            f"criteria[{criteria_index}][field]": "3",
                            f"criteria[{criteria_index}][searchtype]": "equals",
                            f"criteria[{criteria_index}][value]": priority_id,
                        }
                    )
                    criteria_index += 1

            if technician:
                tech_field = self.field_ids.get("TECH", "5")
                search_params.update(
                    {
                        f"criteria[{criteria_index}][link]": "AND",
                        f"criteria[{criteria_index}][field]": tech_field,
                        f"criteria[{criteria_index}][searchtype]": "equals",
                        f"criteria[{criteria_index}][value]": technician,
                    }
                )
                criteria_index += 1

            # Usar função utilitária para filtros de data
            date_criteria_dict = DateValidator.construir_criterios_filtro_data(start_date, end_date, criteria_index)

            # Atualizar o índice de critérios com base nos critérios de data adicionados
            if date_criteria_dict:
                # Contar quantos critérios de data foram adicionados
                date_criteria_count = len([k for k in date_criteria_dict.keys() if "criteria[" in k and "][field]" in k])
                criteria_index += date_criteria_count

            # Adicionar critérios de data se existirem
            if date_criteria_dict:
                search_params.update(date_criteria_dict)

            self.logger.debug(
                f"Buscando tickets novos com filtros: priority={priority}, technician={technician}, dates={start_date}-{end_date}"
            )

            response = self._make_authenticated_request(
                "GET",
                f"{self.glpi_url}/search/Ticket",
                params=search_params,
                timeout=active_config().API_TIMEOUT,
            )

            if not response:
                self.logger.error("Falha na comunicação com o GLPI")
                return []

            if not response.ok:
                self.logger.warning(f"Erro na requisição GLPI: {response.status_code} - {response.text[:200]}")
                return []

            try:
                data = response.json()
                if not isinstance(data, dict):
                    self.logger.warning("Resposta da API não é um objeto JSON válido")
                    return []
            except Exception as e:
                self.logger.error(f"Erro ao processar JSON da resposta: {e}")
                return []

            tickets = []

            if isinstance(data, dict) and "data" in data and data["data"]:
                for ticket_data in data["data"]:
                    try:
                        # Processar dados do ticket de forma segura
                        ticket_id = str(ticket_data.get("2", ""))
                        title = ticket_data.get("1", "Sem título")
                        raw_description = ticket_data.get("21", "")

                        # Formatar descrição usando nova função inteligente
                        description = self.format_ticket_description(raw_description)

                        # Obter informações do solicitante
                        requester_id = ticket_data.get("4", "")
                        requester_name = "Não informado"
                        if requester_id:
                            try:
                                requester_name = self._get_user_name_by_id(str(requester_id))
                            except Exception:
                                pass  # Manter fallback

                        # Obter prioridade
                        priority_id = ticket_data.get("3", "3")
                        priority_name = self._get_priority_name_by_id(str(priority_id))

                        ticket_info = {
                            "id": ticket_id,
                            "title": title,
                            "description": description,
                            "date": ticket_data.get("15", ""),
                            "requester": requester_name,
                            "priority": priority_name,
                            "status": "Novo",
                            "filters_applied": {
                                "priority": priority,
                                "category": category,
                                "technician": technician,
                                "start_date": start_date,
                                "end_date": end_date,
                            },
                        }
                        tickets.append(ticket_info)

                    except Exception as e:
                        self.logger.warning(f"Erro ao processar ticket individual: {e}")
                        continue

            self.logger.info(f"Encontrados {len(tickets)} tickets novos com filtros aplicados")
            return tickets  # Manter compatibilidade retornando apenas os tickets

        except requests.exceptions.Timeout:
            self.logger.error("Timeout na requisição para buscar tickets novos")
            return []
        except requests.exceptions.ConnectionError:
            self.logger.error("Erro de conexão ao buscar tickets novos")
            return []
        except Exception as e:
            self.logger.error(f"Erro inesperado ao buscar tickets novos com filtros: {e}")
            return []

    def _apply_additional_filters(
        self,
        metrics: Dict,
        status: str = None,
        priority: str = None,
        level: str = None,
        technician: str = None,
        category: str = None,
    ) -> Dict:
        """Aplica filtros adicionais às métricas"""
        # Por enquanto, retorna as métricas sem modificação
        # Implementação completa requereria consultas adicionais à API
        return metrics

    def _count_tickets_with_date_filter(self, tech_id, start_date: str = None, end_date: str = None) -> Optional[int]:
        """Conta tickets de um técnico com filtro de data de forma robusta"""
        try:
            # Validar e converter tech_id
            if not tech_id:
                self.logger.error(f"ID de técnico vazio: {tech_id}")
                return 0

            # Converter para string se necessário
            tech_id_str = str(tech_id).strip()
            if not tech_id_str or not tech_id_str.isdigit():
                self.logger.error(f"ID de técnico inválido: {tech_id}")
                return 0

            # Descobrir field_ids se não existirem
            if not self.field_ids:
                if not self.discover_field_ids():
                    self.logger.warning("Falha ao descobrir field_ids, usando fallbacks")
                    return 0

            # Descobrir o campo correto para técnico responsável dinamicamente
            tech_field = self._discover_tech_field_id()
            if not tech_field:
                self.logger.error("Não foi possível descobrir o campo do técnico")
                return 0

            self.logger.debug(f"Usando campo {tech_field} para buscar tickets do técnico {tech_id_str}")

            # Verificar configuração da URL do GLPI
            if not self.glpi_url:
                self.logger.error("URL do GLPI não configurada")
                return 0

            # Construir parâmetros de busca
            search_params = {
                "is_deleted": 0,
                "range": "0-0",  # Apenas contagem
                "criteria[0][field]": tech_field,
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": tech_id_str,
            }

            criteria_index = 1

            # Preparar datas com formato completo de data e hora
            start_date_full = None
            end_date_full = None

            if start_date:
                start_date_full = f"{start_date} 00:00:00" if len(start_date) == 10 else start_date

            if end_date:
                end_date_full = f"{end_date} 23:59:59" if len(end_date) == 10 else end_date

            # Usar função utilitária para filtros de data
            date_criteria_dict = DateValidator.construir_criterios_filtro_data(start_date_full, end_date_full, criteria_index)

            # Adicionar critérios de data se existirem
            if date_criteria_dict:
                search_params.update(date_criteria_dict)

            self.logger.debug(f"Contando tickets para técnico {tech_id_str} com filtros: start={start_date}, end={end_date}")

            response = self._make_authenticated_request("GET", f"{self.glpi_url}/search/Ticket", params=search_params)

            if not response or not response.ok:
                self.logger.warning(f"Falha na requisição para contar tickets do técnico {tech_id_str}")
                return 0

            # Extrair total do header Content-Range
            if "Content-Range" in response.headers:
                try:
                    content_range = response.headers["Content-Range"]
                    self.logger.debug(f"Content-Range recebido: {content_range}")
                    # Formato esperado: "0-0/total" ou "0-N/total"
                    total = int(content_range.split("/")[-1])
                    self.logger.debug(f"Técnico {tech_id_str}: {total} tickets encontrados (Content-Range)")
                    return total
                except (ValueError, IndexError) as e:
                    self.logger.error(f"Erro ao parsear Content-Range '{content_range}': {e}")
                    # Tentar fallback para JSON
                    pass

            # Fallback: tentar extrair do JSON
            try:
                result = response.json()
                if isinstance(result, dict) and "totalcount" in result:
                    return result["totalcount"]
                elif isinstance(result, dict) and "data" in result:
                    return len(result["data"])
            except Exception as e:
                self.logger.warning(f"Erro ao processar resposta JSON: {e}")

            return 0

        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout ao contar tickets do técnico {tech_id_str}")
            return 0
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Erro de conexão ao contar tickets do técnico {tech_id_str}")
            return 0
        except Exception as e:
            self.logger.error(f"Erro ao contar tickets do técnico {tech_id_str}: {e}")
            return 0

    def _get_priority_id_by_name(self, priority_name: str) -> Optional[str]:
        """Converte nome de prioridade para ID do GLPI"""
        priority_reverse_map = {
            "Muito Baixa": "1",
            "Baixa": "2",
            "Média": "3",
            "Alta": "4",
            "Muito Alta": "5",
            "Crítica": "6",
        }
        return priority_reverse_map.get(priority_name)

    def get_dashboard_metrics_with_modification_date_filter(
        self,
        start_date: str,
        end_date: str,
        correlation_id: Optional[str] = None,
    ) -> dict:
        """Obtém métricas do dashboard com filtro por data de modificação.

        Args:
            start_date: Data de início (YYYY-MM-DD)
            end_date: Data de fim (YYYY-MM-DD)

        Returns:
            dict: Métricas formatadas para o dashboard
        """
        # Validar parâmetros
        if not start_date or not end_date:
            return self.get_dashboard_metrics(correlation_id=correlation_id)

        # Criar chave de cache específica
        cache_key = f"dashboard_metrics_modification_filter_{start_date}_{end_date}"

        # Verificar cache
        if self._is_cache_valid(cache_key):
            cached_data = self._get_cache_data(cache_key)
            if cached_data:
                timestamp = datetime.now(tz=timezone.utc).isoformat()
                self.logger.info(f"[{timestamp}] Cache hit para métricas com filtro de modificação: {start_date} a {end_date}")
                return cached_data

        try:
            # Garantir autenticação
            if not self._ensure_authenticated():
                raise Exception("Falha na autenticação com GLPI")

            # Descobrir field_ids se necessário
            if not self.discover_field_ids():
                raise Exception("Falha ao descobrir field_ids")

            timestamp = datetime.now(tz=timezone.utc).isoformat()
            self.logger.info(f"[{timestamp}] Obtendo métricas com filtro de modificação: " f"{start_date} a {end_date}")

            # Obter métricas por data de modificação
            metrics_by_level = self._get_metrics_by_level_by_modification_date(start_date, end_date)

            # Agregar totais por status
            total_novos = sum(level_data.get("Novo", 0) for level_data in metrics_by_level.values())
            total_pendentes = sum(level_data.get("Pendente", 0) for level_data in metrics_by_level.values())
            total_progresso = sum(
                level_data.get("Processando (atribuído)", 0) + level_data.get("Processando (planejado)", 0)
                for level_data in metrics_by_level.values()
            )
            total_resolvidos = sum(
                level_data.get("Solucionado", 0) + level_data.get("Fechado", 0) for level_data in metrics_by_level.values()
            )

            # Calcular tendências (simplificado para filtros)
            trends = {
                "novos": 0,
                "pendentes": 0,
                "progresso": 0,
                "resolvidos": 0,
            }

            # Formatar resultado
            result = {
                "totals": {
                    "novos": total_novos,
                    "pendentes": total_pendentes,
                    "progresso": total_progresso,
                    "resolvidos": total_resolvidos,
                },
                "trends": trends,
                "levels": {
                    "N1": {
                        "novos": metrics_by_level.get("N1", {}).get("Novo", 0),
                        "pendentes": metrics_by_level.get("N1", {}).get("Pendente", 0),
                        "progresso": (
                            metrics_by_level.get("N1", {}).get("Processando (atribuído)", 0)
                            + metrics_by_level.get("N1", {}).get("Processando (planejado)", 0)
                        ),
                        "resolvidos": (
                            metrics_by_level.get("N1", {}).get("Solucionado", 0)
                            + metrics_by_level.get("N1", {}).get("Fechado", 0)
                        ),
                    },
                    "N2": {
                        "novos": metrics_by_level.get("N2", {}).get("Novo", 0),
                        "pendentes": metrics_by_level.get("N2", {}).get("Pendente", 0),
                        "progresso": (
                            metrics_by_level.get("N2", {}).get("Processando (atribuído)", 0)
                            + metrics_by_level.get("N2", {}).get("Processando (planejado)", 0)
                        ),
                        "resolvidos": (
                            metrics_by_level.get("N2", {}).get("Solucionado", 0)
                            + metrics_by_level.get("N2", {}).get("Fechado", 0)
                        ),
                    },
                    "N3": {
                        "novos": metrics_by_level.get("N3", {}).get("Novo", 0),
                        "pendentes": metrics_by_level.get("N3", {}).get("Pendente", 0),
                        "progresso": (
                            metrics_by_level.get("N3", {}).get("Processando (atribuído)", 0)
                            + metrics_by_level.get("N3", {}).get("Processando (planejado)", 0)
                        ),
                        "resolvidos": (
                            metrics_by_level.get("N3", {}).get("Solucionado", 0)
                            + metrics_by_level.get("N3", {}).get("Fechado", 0)
                        ),
                    },
                    "N4": {
                        "novos": metrics_by_level.get("N4", {}).get("Novo", 0),
                        "pendentes": metrics_by_level.get("N4", {}).get("Pendente", 0),
                        "progresso": (
                            metrics_by_level.get("N4", {}).get("Processando (atribuído)", 0)
                            + metrics_by_level.get("N4", {}).get("Processando (planejado)", 0)
                        ),
                        "resolvidos": (
                            metrics_by_level.get("N4", {}).get("Solucionado", 0)
                            + metrics_by_level.get("N4", {}).get("Fechado", 0)
                        ),
                    },
                },
                "filter_info": {
                    "type": "modification",
                    "start_date": start_date,
                    "end_date": end_date,
                    "description": ("Tickets modificados no período (inclui mudanças de status)"),
                },
            }

            # Salvar no cache
            self._set_cache_data(cache_key, result, ttl_minutes=3)

            timestamp = datetime.now(tz=timezone.utc).isoformat()
            self.logger.info(
                f"[{timestamp}] Métricas obtidas com sucesso - Filtro modificação, "
                f"Total: {sum(result['totals'].values())}"
            )

            return result

        except Exception as e:
            timestamp = datetime.now(tz=timezone.utc).isoformat()
            self.logger.error(f"[{timestamp}] Erro ao obter métricas com filtro de modificação: {e}")
            # Retornar métricas sem filtro em caso de erro
            return self.get_dashboard_metrics(correlation_id=correlation_id)

    def _get_general_metrics_by_modification_date(self, start_date: str, end_date: str) -> dict:
        """Obtém métricas gerais filtradas por data de modificação."""
        totals = {}

        for status_name, status_id in self.status_map.items():
            search_params = {
                "is_deleted": 0,
                "range": "0-0",
                "criteria[0][field]": "12",  # Status
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(status_id),
                "criteria[1][link]": "AND",
                "criteria[1][field]": "19",  # Data de modificação
                "criteria[1][searchtype]": "morethan",
                "criteria[1][value]": start_date,
                "criteria[2][link]": "AND",
                "criteria[2][field]": "19",
                "criteria[2][searchtype]": "lessthan",
                "criteria[2][value]": end_date,
            }

            response = self._make_authenticated_request("GET", f"{self.glpi_url}/search/Ticket", params=search_params)

            if response and response.status_code in [200, 206]:
                if "Content-Range" in response.headers:
                    count = int(response.headers["Content-Range"].split("/")[-1])
                    totals[status_name] = count
                else:
                    totals[status_name] = 0
            else:
                totals[status_name] = 0

        return totals

    def debug_field_values(self, correlation_id=None) -> Dict[str, Any]:
        """Debug para verificar valores únicos nos campos do GLPI"""
        try:
            correlation_log = f"[{correlation_id}] " if correlation_id else ""
            self.logger.info(f"{correlation_log}Iniciando debug de valores dos campos")

            if not self._ensure_authenticated():
                raise Exception("Falha na autenticação")

            # Buscar alguns tickets para analisar os valores dos campos
            search_params = {
                "range": "0-50",  # Buscar apenas 50 tickets para análise
                "forcedisplay[0]": "8",  # Campo hierarquia
                "forcedisplay[1]": "12",  # Campo status
                "forcedisplay[2]": "71",  # Campo grupo
                "forcedisplay[3]": "5",  # Campo técnico
                "forcedisplay[4]": "4",  # Campo categoria
                "forcedisplay[5]": "7",  # Campo localização
                "forcedisplay[6]": "6",  # Campo solicitante
            }

            response = self._make_authenticated_request("GET", f"{self.glpi_url}/search/Ticket", params=search_params)

            if not response or not response.ok:
                raise Exception(f"Erro na busca: " f"{response.status_code if response else 'Sem resposta'}")

            data = response.json()
            tickets = data.get("data", [])

            # Analisar valores únicos
            field_8_values = set()  # Hierarquia
            field_12_values = set()  # Status
            field_71_values = set()  # Grupo
            field_5_values = set()  # Técnico
            field_4_values = set()  # Categoria
            field_7_values = set()  # Localização
            field_6_values = set()  # Solicitante

            # Analisar todos os campos disponíveis em cada ticket
            all_fields = set()
            for ticket in tickets:
                all_fields.update(ticket.keys())
                if "8" in ticket:
                    field_8_values.add(str(ticket["8"]))
                if "12" in ticket:
                    field_12_values.add(str(ticket["12"]))
                if "71" in ticket:
                    field_71_values.add(str(ticket["71"]))
                if "5" in ticket:
                    field_5_values.add(str(ticket["5"]))
                if "4" in ticket:
                    field_4_values.add(str(ticket["4"]))
                if "7" in ticket:
                    field_7_values.add(str(ticket["7"]))
                if "6" in ticket:
                    field_6_values.add(str(ticket["6"]))

            result = {
                "total_tickets_analyzed": len(tickets),
                "all_available_fields": sorted(list(all_fields)),
                "field_8_hierarchy_values": sorted(list(field_8_values)),
                "field_12_status_values": sorted(list(field_12_values)),
                "field_71_group_values": sorted(list(field_71_values)),
                "field_5_technician_values": sorted(list(field_5_values)),
                "field_4_category_values": sorted(list(field_4_values)),
                "field_7_location_values": sorted(list(field_7_values)),
                "field_6_requester_values": sorted(list(field_6_values)),
                "service_levels_config": self.service_levels,
                "status_map_config": self.status_map,
                "field_ids_config": getattr(self, "field_ids", {}),
            }

            # Verificar se os IDs de grupo configurados existem nos dados
            group_id_analysis = {}
            for ticket in tickets:
                if "71" in ticket:
                    group_id = str(ticket["71"])
                    if group_id not in group_id_analysis:
                        group_id_analysis[group_id] = 0
                    group_id_analysis[group_id] += 1

            result["group_id_analysis"] = group_id_analysis
            result["configured_group_ids_found"] = {}

            # Verificar se os IDs configurados existem nos dados
            for level_name, group_id in self.service_levels.items():
                group_id_str = str(group_id)
                result["configured_group_ids_found"][level_name] = {
                    "configured_id": group_id,
                    "found_in_data": group_id_str in group_id_analysis,
                    "ticket_count": group_id_analysis.get(group_id_str, 0),
                }

            self.logger.info(f"{correlation_log}Debug concluído: {result}")
            return result

        except Exception as e:
            self.logger.error(f"{correlation_log}Erro no debug de campos: {e}")
            raise

    def _get_metrics_by_level_by_modification_date(self, start_date: str, end_date: str) -> dict:
        """Obtém métricas por nível filtradas por data de modificação."""
        metrics = {}

        for level_name, group_id in self.service_levels.items():
            level_metrics = {}

            for status_name, status_id in self.status_map.items():
                search_params = {
                    "is_deleted": 0,
                    "range": "0-0",
                    "criteria[0][field]": self.field_ids["GROUP"],
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": str(group_id),
                    "criteria[1][link]": "AND",
                    "criteria[1][field]": "12",  # Status
                    "criteria[1][searchtype]": "equals",
                    "criteria[1][value]": str(status_id),
                    "criteria[2][link]": "AND",
                    "criteria[2][field]": "19",  # Data de modificação
                    "criteria[2][searchtype]": "morethan",
                    "criteria[2][value]": start_date,
                    "criteria[3][link]": "AND",
                    "criteria[3][field]": "19",
                    "criteria[3][searchtype]": "lessthan",
                    "criteria[3][value]": end_date,
                }

                response = self._make_authenticated_request(
                    "GET",
                    f"{self.glpi_url}/search/Ticket",
                    params=search_params,
                )

                if response and response.status_code in [200, 206]:
                    if "Content-Range" in response.headers:
                        count = int(response.headers["Content-Range"].split("/")[-1])
                        level_metrics[status_name] = count
                    else:
                        level_metrics[status_name] = 0
                else:
                    level_metrics[status_name] = 0

            metrics[level_name] = level_metrics

        return metrics

    def debug_silvio_tickets(self, silvio_id: str = "696") -> Dict[str, Any]:
        """Método específico para debugar tickets do Silvio"""
        # self.logger.info(f"🔍 [DEBUG SILVIO] Iniciando debug específico para Silvio ID: {silvio_id}")

        # Primeiro, verificar se o usuário existe
        user_url = f"{self.glpi_url}/User/{silvio_id}"
        user_response = self._make_authenticated_request("GET", user_url)

        if user_response and user_response.status_code == 200:
            # user_data = user_response.json()  # Commented out unused variable
            # self.logger.info(f"🔍 [DEBUG SILVIO] Usuário encontrado: {user_data.get('name', 'N/A')}")
            # self.logger.info(f"🔍 [DEBUG SILVIO] Firstname: {user_data.get('firstname', 'N/A')}")
            # self.logger.info(f"🔍 [DEBUG SILVIO] Realname: {user_data.get('realname', 'N/A')}")
            pass
        else:
            self.logger.error(f"❌ [DEBUG SILVIO] Usuário {silvio_id} não encontrado")
            return {"error": "Usuário não encontrado"}

        # Testar diferentes campos para buscar tickets
        test_fields = [5, 95, 4, 6]  # Diferentes campos que podem ser usados para técnico

        for field_id in test_fields:
            # self.logger.info(f"🔍 [DEBUG SILVIO] Testando campo {field_id} para técnico {silvio_id}")

            url = f"{self.glpi_url}/search/Ticket"
            params = {
                "criteria[0][field]": field_id,
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": silvio_id,
                "forcedisplay[0]": 2,  # ID
                "forcedisplay[1]": 12,  # Status
                "range": "0-10",  # Apenas 10 tickets para teste
            }

            try:
                response = self._make_authenticated_request("GET", url, params=params, timeout=10)
                if response and response.status_code == 200:
                    data = response.json()
                    tickets = data.get("data", [])
                    # Debug logs removidos para produção
                    if len(tickets) > 0:
                        pass  # Debug removido
                else:
                    self.logger.warning(
                        f"⚠️ [DEBUG SILVIO] Campo {field_id}: Erro {response.status_code if response else 'None'}"
                    )
            except Exception as e:
                self.logger.error(f"❌ [DEBUG SILVIO] Campo {field_id}: Erro {e}")

        return {"debug": "Concluído"}
