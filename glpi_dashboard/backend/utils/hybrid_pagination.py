#!/usr/bin/env python3
"""
Sistema de Paginação Híbrida Inteligente para GLPI Dashboard
Combina paginação adaptativa com fallback automático para garantir
que nenhum técnico produtivo tenha métricas zeradas.
"""

import json
import os
import time
import logging
from typing import Dict, Any, Tuple, Optional, List
from pathlib import Path

# Configuração de logging
logger = logging.getLogger(__name__)

class HybridPaginationConfig:
    """Configurações para paginação híbrida"""

    # Ranges adaptativos baseados em densidade
    EXPLORATORY_RANGE = "0-100"        # Consulta inicial para análise
    LOW_DENSITY_RANGE = "0-500"        # Técnicos com poucos tickets
    MEDIUM_DENSITY_RANGE = "0-1500"    # Técnicos com volume médio
    HIGH_DENSITY_RANGE = "0-3000"      # Técnicos com alto volume
    MAXIMUM_RANGE = "0-5000"           # Limite absoluto de segurança

    # Thresholds para classificação de densidade
    HIGH_DENSITY_THRESHOLD = 80        # 80+ tickets em 100 = alta densidade
    MEDIUM_DENSITY_THRESHOLD = 40      # 40+ tickets em 100 = média densidade

    # Configurações de completude
    COMPLETENESS_THRESHOLD = 0.8       # 80% do range = potencialmente incompleto (mais agressivo)
    EXTENSION_FACTOR = 2.0             # Fator de extensão para fallback (mais generoso)

    # Configurações de cache
    CACHE_TTL_HOURS = 24               # TTL do cache em horas (mais longo para performance)
    LEARNING_THRESHOLD = 1             # Mínimo de consultas para aprendizado (mais rápido)

    # Configurações de performance
    MAX_CACHE_SIZE = 50                # Máximo de técnicos no cache (reduzido)
    CACHE_CLEANUP_INTERVAL = 7200      # Limpeza a cada 2 horas


class HybridPagination:
    """
    Sistema de paginação híbrida que combina:
    1. Paginação adaptativa baseada em densidade
    2. Fallback automático para ranges insuficientes
    3. Cache inteligente com aprendizado
    """

    def __init__(self, cache_dir: str = "backend/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "hybrid_pagination.json"
        self.config = HybridPaginationConfig()
        self.cache_data = self._load_cache()

        logger.info("Sistema de paginação híbrida inicializado")

    def _load_cache(self) -> Dict[str, Any]:
        """Carrega cache de paginação"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.debug(f"Cache carregado: {len(data.get('technicians', {}))} técnicos")
                    return data
        except Exception as e:
            logger.warning(f"Erro ao carregar cache: {e}")

        return {
            "technicians": {},
            "global_stats": {
                "total_queries": 0,
                "fallback_triggers": 0,
                "cache_hits": 0,
                "last_cleanup": time.time()
            }
        }

    def _save_cache(self):
        """Salva cache de paginação"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, indent=2, ensure_ascii=False)
            logger.debug("Cache salvo com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")

    def get_adaptive_range(self, technician_id: str, technician_name: str = "") -> str:
        """
        Fase 1: Determina range adaptativo baseado em densidade histórica

        Returns:
            str: Range otimizado para o técnico
        """
        # Verificar cache primeiro
        cached_info = self.cache_data["technicians"].get(technician_id)

        if cached_info and self._is_cache_valid(cached_info):
            self.cache_data["global_stats"]["cache_hits"] += 1
            optimal_range = cached_info.get("optimal_range", self.config.HIGH_DENSITY_RANGE)
            logger.debug(f"Cache hit para {technician_name}: {optimal_range}")
            return optimal_range

        # Técnicos conhecidos de alto volume (Anderson, etc.)
        if self._is_known_high_volume(technician_name):
            logger.debug(f"Técnico conhecido de alto volume: {technician_name}")
            return self.config.HIGH_DENSITY_RANGE

        # OTIMIZAÇÃO: Para técnicos novos, usar range máximo para evitar zerados
        # Melhor fazer uma consulta grande do que perder dados
        default_range = self.config.HIGH_DENSITY_RANGE
        logger.debug(f"Range padrão para {technician_name}: {default_range}")
        return default_range

    def _is_cache_valid(self, cached_info: Dict) -> bool:
        """Verifica se cache ainda é válido"""
        last_updated = cached_info.get("last_updated", 0)
        ttl_seconds = self.config.CACHE_TTL_HOURS * 3600
        return (time.time() - last_updated) < ttl_seconds

    def _is_known_high_volume(self, technician_name: str) -> bool:
        """Verifica se é técnico conhecido com alto volume"""
        known_high_volume = ["anderson", "anderson silva", "anderson oliveira"]
        return technician_name.lower() in [name.lower() for name in known_high_volume]

    def is_range_potentially_insufficient(self, tickets: List, range_used: str) -> bool:
        """
        Fase 2: Verifica se o range pode ser insuficiente

        Args:
            tickets: Lista de tickets retornados
            range_used: Range utilizado na consulta

        Returns:
            bool: True se range pode ser insuficiente
        """
        try:
            range_limit = int(range_used.split('-')[1])
            ticket_count = len(tickets) if tickets else 0

            # Lógica mais agressiva para detectar ranges insuficientes
            threshold = range_limit * self.config.COMPLETENESS_THRESHOLD

            # Se encontrou tickets próximo ao limite, pode ter mais
            is_insufficient = ticket_count >= threshold

            # REGRA ESPECIAL: Se tem mais de 1000 tickets, sempre verificar
            # Mas apenas se o range atual for menor que 3000
            if ticket_count >= 1000 and range_limit < 3000:
                is_insufficient = True
                logger.warning(f"Técnico com 1000+ tickets detectado: {ticket_count} - forçando fallback")
            elif ticket_count >= 1000 and range_limit >= 3000:
                # Técnico com 1000+ tickets já tem range adequado
                is_insufficient = False
                logger.debug(f"Técnico com 1000+ tickets já tem range adequado: {ticket_count}/{range_limit}")

            if is_insufficient:
                logger.warning(f"Range potencialmente insuficiente: {ticket_count}/{range_limit} tickets")

            return is_insufficient

        except (ValueError, IndexError) as e:
            logger.error(f"Erro ao analisar range {range_used}: {e}")
            return False

    def calculate_extended_range(self, current_range: str) -> str:
        """
        Calcula range estendido para fallback

        Args:
            current_range: Range atual insuficiente

        Returns:
            str: Range estendido
        """
        try:
            current_limit = int(current_range.split('-')[1])
            extended_limit = int(current_limit * self.config.EXTENSION_FACTOR)

            # Aplicar limite máximo
            max_limit = int(self.config.MAXIMUM_RANGE.split('-')[1])
            extended_limit = min(extended_limit, max_limit)

            extended_range = f"0-{extended_limit}"
            logger.info(f"Range estendido: {current_range} → {extended_range}")
            return extended_range

        except (ValueError, IndexError) as e:
            logger.error(f"Erro ao calcular range estendido: {e}")
            return self.config.HIGH_DENSITY_RANGE

    def update_technician_cache(self, technician_id: str, technician_name: str,
                               range_used: str, ticket_count: int,
                               fallback_triggered: bool = False):
        """
        Atualiza cache com informações da consulta

        Args:
            technician_id: ID do técnico
            technician_name: Nome do técnico
            range_used: Range utilizado na consulta
            ticket_count: Quantidade de tickets encontrados
            fallback_triggered: Se foi necessário fallback
        """
        current_time = time.time()

        # Atualizar dados do técnico
        if technician_id not in self.cache_data["technicians"]:
            self.cache_data["technicians"][technician_id] = {
                "name": technician_name,
                "history": []
            }

        tech_data = self.cache_data["technicians"][technician_id]
        tech_data["name"] = technician_name  # Atualizar nome se mudou
        tech_data["last_updated"] = current_time
        tech_data["last_range"] = range_used
        tech_data["last_count"] = ticket_count
        tech_data["fallback_triggered"] = fallback_triggered

        # Adicionar ao histórico
        tech_data["history"].append({
            "timestamp": current_time,
            "range_used": range_used,
            "ticket_count": ticket_count,
            "fallback_triggered": fallback_triggered
        })

        # Manter apenas últimas 10 entradas no histórico
        tech_data["history"] = tech_data["history"][-10:]

        # Calcular range ótimo baseado no histórico
        tech_data["optimal_range"] = self._calculate_optimal_range(tech_data["history"])

        # Atualizar estatísticas globais
        self.cache_data["global_stats"]["total_queries"] += 1
        if fallback_triggered:
            self.cache_data["global_stats"]["fallback_triggers"] += 1

        # Salvar cache
        self._save_cache()

        logger.debug(f"Cache atualizado para {technician_name}: {ticket_count} tickets, range {range_used}")

    def _calculate_optimal_range(self, history: List[Dict]) -> str:
        """Calcula range ótimo baseado no histórico"""
        if not history or len(history) < 2:
            return self.config.MEDIUM_DENSITY_RANGE

        # Pegar contagens recentes
        recent_counts = [entry["ticket_count"] for entry in history[-3:]]
        max_count = max(recent_counts)
        avg_count = sum(recent_counts) / len(recent_counts)

        # Determinar range ótimo com margem de segurança
        if max_count >= 2500:
            return self.config.HIGH_DENSITY_RANGE
        elif max_count >= 1000:
            return self.config.MEDIUM_DENSITY_RANGE
        else:
            return self.config.LOW_DENSITY_RANGE

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema"""
        global_stats = self.cache_data["global_stats"]
        total_queries = global_stats.get("total_queries", 0)
        fallback_triggers = global_stats.get("fallback_triggers", 0)
        cache_hits = global_stats.get("cache_hits", 0)

        fallback_rate = (fallback_triggers / total_queries * 100) if total_queries > 0 else 0
        cache_hit_rate = (cache_hits / total_queries * 100) if total_queries > 0 else 0

        return {
            "total_technicians": len(self.cache_data["technicians"]),
            "total_queries": total_queries,
            "fallback_triggers": fallback_triggers,
            "fallback_rate_percent": round(fallback_rate, 2),
            "cache_hits": cache_hits,
            "cache_hit_rate_percent": round(cache_hit_rate, 2),
            "config": {
                "low_density_range": self.config.LOW_DENSITY_RANGE,
                "medium_density_range": self.config.MEDIUM_DENSITY_RANGE,
                "high_density_range": self.config.HIGH_DENSITY_RANGE,
                "maximum_range": self.config.MAXIMUM_RANGE
            }
        }

    def cleanup_old_entries(self):
        """Remove entradas antigas do cache"""
        current_time = time.time()
        ttl_seconds = self.config.CACHE_TTL_HOURS * 3600 * 7  # 7 dias para cleanup

        to_remove = []
        for tech_id, tech_data in self.cache_data["technicians"].items():
            last_updated = tech_data.get("last_updated", 0)
            if (current_time - last_updated) > ttl_seconds:
                to_remove.append(tech_id)

        for tech_id in to_remove:
            del self.cache_data["technicians"][tech_id]

        if to_remove:
            logger.info(f"Removidas {len(to_remove)} entradas antigas do cache")
            self._save_cache()


# Instância global para uso em toda aplicação
hybrid_pagination = HybridPagination()


# Funções de compatibilidade com sistema anterior
def get_technician_range(technician_id: str, technician_name: str = "") -> str:
    """Função de compatibilidade - retorna range adaptativo"""
    return hybrid_pagination.get_adaptive_range(technician_id, technician_name)


def update_technician_stats(technician_id: str, technician_name: str, total_tickets: int):
    """Função de compatibilidade - atualiza estatísticas"""
    # Usar range médio como padrão para compatibilidade
    range_used = hybrid_pagination.config.MEDIUM_DENSITY_RANGE
    hybrid_pagination.update_technician_cache(
        technician_id, technician_name, range_used, total_tickets
    )
