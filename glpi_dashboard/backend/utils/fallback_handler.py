import logging
import json
import asyncio
from typing import Dict, Any, Optional, List, Callable, TypeVar, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

# Cache unificado
from core.cache import get_unified_cache

logger = logging.getLogger(__name__)

T = TypeVar('T')

class DataPriority(Enum):
    """Prioridade dos dados para fallback."""
    CRITICAL = "critical"  # Dados essenciais para funcionamento
    HIGH = "high"         # Dados importantes mas não críticos
    MEDIUM = "medium"     # Dados úteis mas dispensáveis
    LOW = "low"           # Dados opcionais

@dataclass
class FallbackData:
    """Estrutura para dados de fallback."""
    data: Any
    timestamp: datetime
    priority: DataPriority
    source: str
    ttl_seconds: int = 3600  # TTL padrão de 1 hora
    
    def is_expired(self) -> bool:
        """Verifica se os dados expiraram."""
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl_seconds)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário serializável."""
        return {
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority.value,
            'source': self.source,
            'ttl_seconds': self.ttl_seconds
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FallbackData':
        """Cria instância a partir de dicionário."""
        return cls(
            data=data['data'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            priority=DataPriority(data['priority']),
            source=data['source'],
            ttl_seconds=data.get('ttl_seconds', 3600)
        )

class FallbackHandler:
    """Handler para gerenciar dados de fallback e cache de emergência usando cache unificado."""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self._unified_cache = get_unified_cache()
        self._default_fallbacks = self._initialize_default_fallbacks()
        
    def _initialize_default_fallbacks(self) -> Dict[str, Any]:
        """Inicializa dados de fallback padrão para casos críticos."""
        return {
            'recent_tickets': [],
            'technician_ranking': [],
            'dashboard_metrics': {
                'total_tickets': 0,
                'open_tickets': 0,
                'closed_tickets': 0,
                'pending_tickets': 0,
                'avg_resolution_time': 0
            },
            'hierarchy_metrics': {},
            'technician_hierarchy': {}
        }
    
    def _get_cache_file(self, key: str) -> Path:
        """Obtém caminho do arquivo de cache."""
        safe_key = key.replace('/', '_').replace('\\', '_')
        return self.cache_dir / f"{safe_key}.json"
    
    async def store_fallback_data(self, key: str, data: Any, priority: DataPriority, 
                                 source: str = "unknown", ttl_seconds: int = 3600) -> None:
        """Armazena dados de fallback."""
        try:
            fallback_data = FallbackData(
                data=data,
                timestamp=datetime.now(),
                priority=priority,
                source=source,
                ttl_seconds=ttl_seconds
            )
            
            # Armazenar no cache unificado
            self._unified_cache.set(f"fallback_{key}", fallback_data.to_dict(), ttl=ttl_seconds)
            
            # Armazenar em disco para dados críticos e de alta prioridade
            if priority in [DataPriority.CRITICAL, DataPriority.HIGH]:
                await self._store_to_disk(key, fallback_data)
                
            logger.info(f"Dados de fallback armazenados para '{key}' com prioridade {priority.value}")
            
        except Exception as e:
            logger.error(f"Erro ao armazenar dados de fallback para '{key}': {e}")
    
    async def _store_to_disk(self, key: str, fallback_data: FallbackData) -> None:
        """Armazena dados no disco de forma assíncrona."""
        try:
            cache_file = self._get_cache_file(key)
            data_dict = fallback_data.to_dict()
            
            def write_file():
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(data_dict, f, ensure_ascii=False, indent=2)
            
            # Executar I/O em thread separada
            await asyncio.get_event_loop().run_in_executor(None, write_file)
            
        except Exception as e:
            logger.error(f"Erro ao armazenar dados no disco para '{key}': {e}")
    
    async def get_fallback_data(self, key: str, max_age_seconds: Optional[int] = None) -> Optional[Any]:
        """Obtém dados de fallback, priorizando cache unificado depois disco."""
        try:
            # Tentar cache unificado primeiro
            cached_data = self._unified_cache.get(f"fallback_{key}")
            if cached_data:
                fallback_data = FallbackData.from_dict(cached_data)
                if not fallback_data.is_expired():
                    if max_age_seconds is None or \
                       (datetime.now() - fallback_data.timestamp).total_seconds() <= max_age_seconds:
                        logger.info(f"Dados de fallback obtidos do cache unificado para '{key}'")
                        return fallback_data.data
            
            # Tentar disco
            fallback_data = await self._load_from_disk(key)
            if fallback_data and not fallback_data.is_expired():
                if max_age_seconds is None or \
                   (datetime.now() - fallback_data.timestamp).total_seconds() <= max_age_seconds:
                    # Recarregar no cache unificado
                    self._unified_cache.set(f"fallback_{key}", fallback_data.to_dict(), ttl=fallback_data.ttl_seconds)
                    logger.info(f"Dados de fallback obtidos do disco para '{key}'")
                    return fallback_data.data
            
            # Fallback para dados padrão se disponível
            if key in self._default_fallbacks:
                logger.warning(f"Usando dados padrão de fallback para '{key}'")
                return self._default_fallbacks[key]
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter dados de fallback para '{key}': {e}")
            # Tentar dados padrão como último recurso
            return self._default_fallbacks.get(key)
    
    def get_fallback_data_sync(self, key: str, max_age_seconds: Optional[int] = None) -> Optional[Any]:
        """Versão síncrona para obter dados de fallback - cache unificado e dados padrão."""
        try:
            # Tentar cache unificado primeiro
            cached_data = self._unified_cache.get(f"fallback_{key}")
            if cached_data:
                fallback_data = FallbackData.from_dict(cached_data)
                if not fallback_data.is_expired():
                    if max_age_seconds is None or \
                       (datetime.now() - fallback_data.timestamp).total_seconds() <= max_age_seconds:
                        logger.info(f"Dados de fallback obtidos do cache unificado (sync) para '{key}'")
                        return fallback_data.data
            
            # Tentar disco de forma síncrona (sem async)
            try:
                cache_file = self._get_cache_file(key)
                if cache_file.exists():
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data_dict = json.load(f)
                    fallback_data = FallbackData.from_dict(data_dict)
                    if fallback_data and not fallback_data.is_expired():
                        if max_age_seconds is None or \
                           (datetime.now() - fallback_data.timestamp).total_seconds() <= max_age_seconds:
                            # Recarregar no cache unificado
                            self._unified_cache.set(f"fallback_{key}", fallback_data.to_dict(), ttl=fallback_data.ttl_seconds)
                            logger.info(f"Dados de fallback obtidos do disco (sync) para '{key}'")
                            return fallback_data.data
            except Exception as disk_error:
                logger.warning(f"Erro ao ler disco (sync) para '{key}': {disk_error}")
            
            # Fallback para dados padrão se disponível
            if key in self._default_fallbacks:
                logger.warning(f"Usando dados padrão de fallback (sync) para '{key}'")
                return self._default_fallbacks[key]
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter dados de fallback (sync) para '{key}': {e}")
            # Tentar dados padrão como último recurso
            return self._default_fallbacks.get(key)
    
    async def _load_from_disk(self, key: str) -> Optional[FallbackData]:
        """Carrega dados do disco de forma assíncrona."""
        try:
            cache_file = self._get_cache_file(key)
            if not cache_file.exists():
                return None
            
            def read_file():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Executar I/O em thread separada
            data_dict = await asyncio.get_event_loop().run_in_executor(None, read_file)
            return FallbackData.from_dict(data_dict)
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados do disco para '{key}': {e}")
            return None
    
    async def cleanup_expired_data(self) -> None:
        """Remove dados expirados da memória e disco."""
        try:
            # Limpar memória
            expired_keys = []
            for key, fallback_data in self._memory_cache.items():
                if fallback_data.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._memory_cache[key]
                logger.debug(f"Dados expirados removidos da memória: '{key}'")
            
            # Limpar disco
            def cleanup_disk():
                for cache_file in self.cache_dir.glob("*.json"):
                    try:
                        with open(cache_file, 'r', encoding='utf-8') as f:
                            data_dict = json.load(f)
                        
                        fallback_data = FallbackData.from_dict(data_dict)
                        if fallback_data.is_expired():
                            cache_file.unlink()
                            logger.debug(f"Arquivo de cache expirado removido: {cache_file}")
                    except Exception as e:
                        logger.error(f"Erro ao processar arquivo de cache {cache_file}: {e}")
            
            await asyncio.get_event_loop().run_in_executor(None, cleanup_disk)
            
        except Exception as e:
            logger.error(f"Erro durante limpeza de dados expirados: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do cache."""
        try:
            memory_count = len(self._memory_cache)
            disk_count = len(list(self.cache_dir.glob("*.json")))
            
            priority_counts = {}
            for fallback_data in self._memory_cache.values():
                priority = fallback_data.priority.value
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            return {
                'memory_cache_count': memory_count,
                'disk_cache_count': disk_count,
                'priority_distribution': priority_counts,
                'cache_directory': str(self.cache_dir)
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do cache: {e}")
            return {}

# Instância global do handler de fallback
_fallback_handler = FallbackHandler()

def get_fallback_handler() -> FallbackHandler:
    """Obtém instância global do handler de fallback."""
    return _fallback_handler

# Decorador para fallback automático
def with_fallback(key: str, priority: DataPriority = DataPriority.MEDIUM, 
                 ttl_seconds: int = 3600, store_result: bool = True):
    """Decorador para adicionar fallback automático a funções."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        async def wrapper(*args, **kwargs) -> T:
            handler = get_fallback_handler()
            
            try:
                # Tentar executar função
                result = await func(*args, **kwargs)
                
                # Armazenar resultado para fallback futuro
                if store_result and result is not None:
                    await handler.store_fallback_data(
                        key=key,
                        data=result,
                        priority=priority,
                        source=func.__name__,
                        ttl_seconds=ttl_seconds
                    )
                
                return result
                
            except Exception as e:
                logger.warning(f"Função {func.__name__} falhou, tentando fallback: {e}")
                
                # Tentar obter dados de fallback
                fallback_data = await handler.get_fallback_data(key)
                if fallback_data is not None:
                    logger.info(f"Usando dados de fallback para {func.__name__}")
                    return fallback_data
                
                # Re-raise se não há fallback disponível
                raise
        
        return wrapper
    return decorator