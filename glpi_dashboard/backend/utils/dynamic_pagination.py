#!/usr/bin/env python3
"""
Sistema de paginação dinâmica para otimizar consultas GLPI
Ajusta automaticamente o range baseado no histórico de cada técnico
"""

import json
from typing import Dict, Optional
from pathlib import Path


class DynamicPagination:
    """Gerencia paginação dinâmica baseada no histórico de tickets por técnico"""

    def __init__(self, cache_file: str = "backend/cache/technician_ranges.json"):
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.ranges_cache = self._load_cache()

        # Técnicos conhecidos com muitos chamados
        self.high_volume_technicians = {
            "anderson": {"min_range": 3000, "reason": "2700+ chamados"},
            # Adicionar outros técnicos conforme necessário
        }

    def _load_cache(self) -> Dict[str, Dict]:
        """Carrega cache de ranges por técnico"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_cache(self) -> None:
        """Salva cache de ranges"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.ranges_cache, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get_optimal_range(self, technician_id: str, technician_name: str = "") -> str:
        """Retorna o range ótimo para um técnico específico"""

        # Verificar se é um técnico de alto volume conhecido
        name_lower = technician_name.lower()
        for known_tech, config in self.high_volume_technicians.items():
            if known_tech in name_lower:
                return f"0-{config['min_range']}"

        # Verificar cache histórico
        if technician_id in self.ranges_cache:
            cached = self.ranges_cache[technician_id]
            last_count = cached.get("last_ticket_count", 0)

            # Se o último count foi alto, usar range maior
            if last_count > 2500:
                return "0-3500"  # Range extra para técnicos com muitos tickets
            elif last_count > 1500:
                return "0-2500"
            elif last_count > 800:
                return "0-1500"
            elif last_count > 300:
                return "0-1000"
            else:
                return "0-500"

        # Default seguro para técnicos novos/desconhecidos
        return "0-1000"

    def update_technician_stats(self, technician_id: str, technician_name: str, ticket_count: int) -> None:
        """Atualiza estatísticas de um técnico"""
        if technician_id not in self.ranges_cache:
            self.ranges_cache[technician_id] = {}

        self.ranges_cache[technician_id].update({
            "name": technician_name,
            "last_ticket_count": ticket_count,
            "last_updated": str(Path(__file__).stat().st_mtime),
            "optimal_range": self.get_optimal_range(technician_id, technician_name)
        })

        self._save_cache()

    def get_batch_ranges(self, technician_ids: list) -> Dict[str, str]:
        """Retorna ranges otimizados para uma lista de técnicos"""
        ranges = {}
        for tech_id in technician_ids:
            cached_info = self.ranges_cache.get(tech_id, {})
            tech_name = cached_info.get("name", "")
            ranges[tech_id] = self.get_optimal_range(tech_id, tech_name)

        return ranges

    def get_stats(self) -> Dict:
        """Retorna estatísticas do sistema de paginação"""
        total_technicians = len(self.ranges_cache)
        high_volume_count = sum(1 for tech in self.ranges_cache.values()
                               if tech.get("last_ticket_count", 0) > 1500)

        return {
            "total_technicians_tracked": total_technicians,
            "high_volume_technicians": high_volume_count,
            "cache_file": str(self.cache_file),
            "known_high_volume": list(self.high_volume_technicians.keys())
        }


# Instância global
dynamic_pagination = DynamicPagination()


def get_technician_range(technician_id: str, technician_name: str = "") -> str:
    """Função helper para obter range otimizado"""
    return dynamic_pagination.get_optimal_range(technician_id, technician_name)


def update_technician_stats(technician_id: str, technician_name: str, ticket_count: int) -> None:
    """Função helper para atualizar estatísticas"""
    dynamic_pagination.update_technician_stats(technician_id, technician_name, ticket_count)


if __name__ == "__main__":
    # Teste do sistema
    dp = DynamicPagination()

    # Simular Anderson
    anderson_range = dp.get_optimal_range("123", "Anderson Silva")
    print(f"Range para Anderson: {anderson_range}")

    # Simular técnico novo
    novo_range = dp.get_optimal_range("456", "João Santos")
    print(f"Range para técnico novo: {novo_range}")

    # Atualizar stats
    dp.update_technician_stats("123", "Anderson Silva", 2700)
    anderson_range_updated = dp.get_optimal_range("123", "Anderson Silva")
    print(f"Range para Anderson após update: {anderson_range_updated}")

    print(f"Stats: {dp.get_stats()}")
